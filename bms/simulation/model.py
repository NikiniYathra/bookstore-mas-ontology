"""Mesa model coordinating agents and ontology data."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set

from mesa import Model
from mesa.time import RandomActivation

from bms.config import AppConfig, load_config
from bms.ontology.builder import BookstoreOntologyBuilder
from .agents import BookAgent, CustomerAgent, EmployeeAgent
from .message_bus import MessageBus
from .policies import DecisionPolicy, RandomPurchasePolicy
from .state import InventorySnapshot

LOGGER = logging.getLogger(__name__)

try:  # Owlready2 bundles Pellet but it might be unavailable at runtime
    from owlready2 import sync_reasoner_pellet
except Exception:  # pragma: no cover - environment dependent
    sync_reasoner_pellet = None  # type: ignore[assignment]


@dataclass
class RestockEvent:
    """Record of a single restock operation."""

    step: int
    book_isbn: str
    amount: int
    employee_id: Optional[str]


class BookstoreModel(Model):
    """Glue component between the ontology data and Mesa agents."""

    def __init__(
        self,
        builder: BookstoreOntologyBuilder,
        config: AppConfig | None = None,
        customer_policy: DecisionPolicy | None = None,
    ) -> None:
        super().__init__()
        self.config = config or load_config()
        if self.config.simulation.random_seed is not None:
            self.random.seed(self.config.simulation.random_seed)
        self.builder = builder
        self.ontology = builder.onto
        self.message_bus = MessageBus()
        self.schedule = RandomActivation(self)
        self.customer_policy = customer_policy or RandomPurchasePolicy()
        self.inventory_snapshots: Dict[str, InventorySnapshot] = {}
        self.inventory_entities: Dict[str, Any] = {}
        self.book_entities: Dict[str, Any] = {}
        self.customer_entities: Dict[str, Any] = {}
        self.employee_entities: Dict[str, Any] = {}
        self.pending_restocks: Set[str] = set()
        self.purchase_log: List[Dict[str, Any]] = []
        self.restock_log: List[RestockEvent] = []
        self.order_counter = 0
        self.step_count = 0
        self._reasoner_available = sync_reasoner_pellet is not None
        self._reasoner_warning_emitted = False
        self._load_inventory_from_ontology()
        self._register_agents()

    # ------------------------------------------------------------------ public

    def step(self) -> None:
        self.step_count += 1
        self.schedule.step()
        self._process_purchase_events()
        self._sync_reasoner_if_needed(force=False)

    def collect_inventory_state(self) -> Iterable[InventorySnapshot]:
        """Expose read-only inventory view for agent consumption."""

        return self.inventory_snapshots.values()

    def restock_inventory(
        self,
        book_id: str,
        amount: int,
        *,
        employee_id: Optional[str] = None,
    ) -> None:
        """Increase on-hand quantity and reset the restock flag."""

        snapshot = self.inventory_snapshots.get(book_id)
        if snapshot is None:
            return
        increment = max(int(amount), 0)
        snapshot.quantity += increment
        self.pending_restocks.discard(book_id)
        self._write_back_inventory_to_ontology(
            snapshot,
            needs_restock=snapshot.quantity < snapshot.low_threshold,
        )
        employee_entity = None
        if employee_id is not None:
            employee_entity = self._ensure_employee_entity(employee_id)
        item = self.inventory_entities.get(book_id)
        if employee_entity is not None and item is not None:
            if item not in employee_entity.WorksAt:
                employee_entity.WorksAt.append(item)
        self.restock_log.append(
            RestockEvent(
                step=self.step_count,
                book_isbn=book_id,
                amount=increment,
                employee_id=employee_id,
            )
        )

    def generate_report(self) -> Dict[str, Any]:
        """Materialise ontology inferences, print a summary, and return raw data."""

        self._sync_reasoner_if_needed(force=True)
        inventory_summary = []
        for isbn, snapshot in self.inventory_snapshots.items():
            inventory_entity = self.inventory_entities.get(isbn)
            if inventory_entity is not None:
                quantity = int(inventory_entity.AvailableQuantity[0]) if inventory_entity.AvailableQuantity else snapshot.quantity
                low_threshold = int(inventory_entity.LowThreshold[0]) if inventory_entity.LowThreshold else snapshot.low_threshold
                needs_restock = bool(inventory_entity.NeedsRestock[0]) if inventory_entity.NeedsRestock else quantity < low_threshold
            else:
                quantity = snapshot.quantity
                low_threshold = snapshot.low_threshold
                needs_restock = quantity < low_threshold
            inventory_summary.append(
                {
                    "isbn": isbn,
                    "title": snapshot.title,
                    "price": snapshot.price,
                    "quantity": quantity,
                    "low_threshold": low_threshold,
                    "needs_restock": needs_restock,
                }
            )

        purchases_by_customer: Dict[str, List[str]] = {}
        for customer in self.ontology.Customer.instances():
            source_books = customer.HasPurchased or customer.Purchases
            purchased_books = sorted({book.name for book in source_books})
            if purchased_books:
                purchases_by_customer[customer.name] = purchased_books

        restock_summary = [
            {
                "step": event.step,
                "isbn": event.book_isbn,
                "amount": event.amount,
                "employee_id": event.employee_id,
            }
            for event in self.restock_log
        ]

        report = {
            "inventory": inventory_summary,
            "purchases": purchases_by_customer,
            "restocks": restock_summary,
            "reasoner_active": self._reasoner_available,
        }

        self._print_report(report)
        return report

    # -------------------------------------------------------------- internals

    def _load_inventory_from_ontology(self) -> None:
        """Translate ontology individuals into in-memory snapshots."""

        for book in self.ontology.Book.instances():
            isbn = book.name
            inventory = self.builder.ensure_inventory_for(book)
            quantity = int(inventory.AvailableQuantity[0]) if inventory.AvailableQuantity else 0
            threshold = (
                int(inventory.LowThreshold[0])
                if inventory.LowThreshold
                else self.config.simulation.restock_threshold
            )
            if not inventory.LowThreshold:
                inventory.LowThreshold = [threshold]
            needs_restock = (
                bool(inventory.NeedsRestock[0])
                if inventory.NeedsRestock
                else quantity < threshold
            )
            if not inventory.NeedsRestock:
                inventory.NeedsRestock = [needs_restock]
            price = float(book.HasPrice[0]) if book.HasPrice else 0.0
            title = book.HasTitle[0] if book.HasTitle else isbn
            snapshot = InventorySnapshot(
                book_isbn=isbn,
                title=title,
                quantity=quantity,
                price=price,
                low_threshold=threshold,
            )
            self.inventory_snapshots[isbn] = snapshot
            self.inventory_entities[isbn] = inventory
            self.book_entities[isbn] = book

    def _write_back_inventory_to_ontology(
        self, snapshot: InventorySnapshot, *, needs_restock: bool | None = None
    ) -> None:
        """Persist inventory updates to the ontology instance."""

        book = self._ensure_book_entity(snapshot.book_isbn)
        inventory = self._ensure_inventory_entity(book)
        inventory.AvailableQuantity = [int(snapshot.quantity)]
        inventory.LowThreshold = [int(snapshot.low_threshold)]
        computed_flag = snapshot.quantity < snapshot.low_threshold
        if needs_restock is None:
            inventory.NeedsRestock = [computed_flag]
        else:
            inventory.NeedsRestock = [bool(needs_restock)]
        self.inventory_entities[snapshot.book_isbn] = inventory
        self.book_entities[snapshot.book_isbn] = book

    def _register_agents(self) -> None:
        """Create book, customer, and employee agents."""

        for snapshot in self.inventory_snapshots.values():
            agent = BookAgent(unique_id=f"book::{snapshot.book_isbn}", model=self, snapshot=snapshot)
            self.schedule.add(agent)

        employee_id = "employee::0"
        self._ensure_employee_entity(employee_id)
        employee = EmployeeAgent(unique_id=employee_id, model=self, message_bus=self.message_bus)
        self.schedule.add(employee)

        for idx in range(2):
            customer_id = f"customer::{idx}"
            self._ensure_customer_entity(customer_id)
            customer = CustomerAgent(
                unique_id=customer_id,
                model=self,
                policy=self.customer_policy,
                budget=50.0,
            )
            self.schedule.add(customer)

    def _process_purchase_events(self) -> None:
        """Drain the purchase queue, update inventory, and record ontology facts."""

        while True:
            message = self.message_bus.poll(topic="purchases")
            if message is None:
                break
            book_id = message.payload.get("book_id")
            customer_id = message.payload.get("customer_id")
            price = float(message.payload.get("price", 0.0))
            if not book_id or customer_id is None:
                continue
            snapshot = self.inventory_snapshots.get(book_id)
            if snapshot is None or snapshot.quantity <= 0:
                continue
            snapshot.quantity = max(snapshot.quantity - 1, 0)
            needs_restock = snapshot.quantity < snapshot.low_threshold
            self._write_back_inventory_to_ontology(
                snapshot, needs_restock=needs_restock
            )
            self._record_purchase(customer_id, book_id, price)

    def _record_purchase(self, customer_id: str, book_id: str, price: float) -> None:
        """Create ontology assertions for the purchase event."""

        customer = self._ensure_customer_entity(customer_id)
        book = self._ensure_book_entity(book_id)
        if book is None:
            return
        if book not in customer.Purchases:
            customer.Purchases.append(book)
        order_name = f"order_{self.order_counter}"
        self.order_counter += 1
        order = self.ontology.Order(order_name)
        order.OrderedBy = [customer]
        order.OrderedBook = [book]
        self.purchase_log.append(
            {
                "order": order_name,
                "customer": customer_id,
                "book": book_id,
                "price": price,
                "step": self.step_count,
            }
        )

    def _ensure_book_entity(self, isbn: str):
        book = self.book_entities.get(isbn)
        if book is not None:
            return book
        for candidate in self.ontology.Book.instances():
            if candidate.name == isbn:
                book = candidate
                break
        if book is None:
            with self.ontology:
                book = self.ontology.Book(isbn)
        self.book_entities[isbn] = book
        return book

    def _ensure_inventory_entity(self, book):
        inventory = self.builder.ensure_inventory_for(book)
        self.inventory_entities[book.name] = inventory
        return inventory

    def _ensure_customer_entity(self, unique_id: str):
        name = self._normalise_identifier(unique_id)
        entity = self.customer_entities.get(name)
        if entity is not None:
            return entity
        with self.ontology:
            entity = self.ontology.Customer(name)
        self.customer_entities[name] = entity
        return entity

    def _ensure_employee_entity(self, unique_id: str):
        name = self._normalise_identifier(unique_id)
        entity = self.employee_entities.get(name)
        if entity is not None:
            return entity
        with self.ontology:
            entity = self.ontology.Employee(name)
        self.employee_entities[name] = entity
        return entity

    def _normalise_identifier(self, unique_id: str) -> str:
        return unique_id.replace("::", "_")

    def _sync_reasoner_if_needed(self, force: bool) -> None:
        """Invoke Pellet to materialise SWRL rule consequences."""

        interval = self.config.simulation.reasoner_sync_interval
        if not force and interval and self.step_count % interval != 0:
            self._enqueue_restock_requests_from_ontology(fallback=not self._reasoner_available)
            return
        if not self._reasoner_available:
            self._log_reasoner_warning()
            self._enqueue_restock_requests_from_ontology(fallback=True)
            return
        try:
            sync_reasoner_pellet(  # type: ignore[misc]
                [self.ontology],
                infer_property_values=True,
                infer_data_property_values=True,
            )
        except Exception as exc:  # pragma: no cover - depends on JVM availability
            self._reasoner_available = False
            LOGGER.warning("Pellet reasoner failed; falling back to procedural restock logic (%s)", exc)
            self._enqueue_restock_requests_from_ontology(fallback=True)
        else:
            self._enqueue_restock_requests_from_ontology(fallback=False)

    def _log_reasoner_warning(self) -> None:
        if not self._reasoner_warning_emitted:
            LOGGER.warning("Pellet reasoner unavailable; using heuristic restock detection.")
            self._reasoner_warning_emitted = True

    def _enqueue_restock_requests_from_ontology(self, *, fallback: bool) -> None:
        """Publish restock requests based on ontology state or heuristics."""

        for isbn, item in self.inventory_entities.items():
            snapshot = self.inventory_snapshots[isbn]
            if fallback:
                needs_restock = snapshot.quantity < snapshot.low_threshold
            else:
                needs_restock = bool(item.NeedsRestock and item.NeedsRestock[0])
            if not needs_restock or isbn in self.pending_restocks:
                continue
            self.message_bus.publish(
                topic="restock",
                payload={
                    "book_id": isbn,
                    "amount": self.config.simulation.restock_amount,
                },
            )
            self.pending_restocks.add(isbn)

    def _print_report(self, report: Dict[str, Any]) -> None:
        """Pretty-print the final simulation summary."""

        print("\n=== Inventory Summary ===")
        for entry in report["inventory"]:
            print(
                f"{entry['isbn']} | {entry['title']} | price={entry['price']:.2f} | "
                f"qty={entry['quantity']} | threshold={entry['low_threshold']}"
            )

        print("\n=== Purchases by Customer ===")
        if not report["purchases"]:
            print("No purchases recorded.")
        else:
            for customer, books in sorted(report["purchases"].items()):
                joined = ", ".join(books)
                print(f"{customer}: {joined}")

        print("\n=== Restocks ===")
        if not report["restocks"]:
            print("No restocks performed.")
        else:
            for entry in report["restocks"]:
                print(
                    f"step={entry['step']} | isbn={entry['isbn']} | amount={entry['amount']} | "
                    f"employee={entry['employee_id']}"
                )

        if not report.get("reasoner_active", True):
            print("[warning] Pellet reasoner unavailable; SWRL low_stock rule did not execute.")


__all__ = ["BookstoreModel"]

