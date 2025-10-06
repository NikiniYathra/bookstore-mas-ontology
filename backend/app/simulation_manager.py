"""Stateful controller that wraps the Bookstore simulation for FastAPI."""

from __future__ import annotations

import json
import random
from pathlib import Path
from threading import Lock
from typing import Dict, Iterable, List, Optional

from owlready2.base import OwlReadyOntologyParsingError

from bms.config import AppConfig, load_config
from bms.ontology import BookstoreOntologyBuilder, build_default_rules
from bms.ontology.rules import activate_rules
from bms.simulation import BookstoreModel, InventorySnapshot


class SimulationManager:
    """Facade around the Mesa model providing persistence and projections."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.config: AppConfig = load_config()
        self.builder = BookstoreOntologyBuilder(
            ontology_iri=self.config.ontology.ontology_iri,
            storage_path=self.config.ontology.storage_path,
        )
        self.ontology_path = self.builder.storage_path
        self.customer_seed_data = self._load_sample_customers()
        self._prepare_ontology()
        self.model = self._create_model()

    # ------------------------------------------------------------------ helpers

    def _prepare_ontology(self) -> None:
        """Ensure the ontology is loaded and pre-populated if necessary."""

        if self.ontology_path.exists():
            try:
                self.builder.onto.load(file=str(self.ontology_path))
                self.builder.build_schema()
            except OwlReadyOntologyParsingError:
                self._bootstrap_ontology()
        else:
            self._bootstrap_ontology()
        self._seed_customers_if_missing()
        rules = build_default_rules(self.builder.onto)
        activate_rules(rules.values())

    def _bootstrap_ontology(self) -> None:
        """Create ontology schema and seed it with sample inventory."""

        self.builder.build_schema()
        inventory = self._load_sample_inventory()
        self.builder.add_inventory(
            inventory,
            default_threshold=self.config.simulation.restock_threshold,
        )
        if self.customer_seed_data:
            self.builder.add_customers(self.customer_seed_data)
        self.builder.save()

    def _create_model(self) -> BookstoreModel:
        model = BookstoreModel(builder=self.builder, config=self.config)
        if self.config.simulation.random_seed is not None:
            model.random.seed(self.config.simulation.random_seed)
        return model

    def _load_sample_inventory(self) -> List[Dict[str, object]]:
        data_path = Path("bms") / "data" / "sample_inventory.json"
        with data_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _load_sample_customers(self) -> List[Dict[str, object]]:
        data_path = Path("bms") / "data" / "sample_customers.json"
        if not data_path.exists():
            return []
        with data_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _seed_customers_if_missing(self) -> None:
        if not getattr(self, "customer_seed_data", None):
            return
        if self.builder.add_customers(self.customer_seed_data):
            self.builder.save()

    def _persist(self) -> None:
        self.builder.save()

    # ---------------------------------------------------------------- operations

    def run_steps(
        self,
        steps: int,
        *,
        reasoner_sync_interval: Optional[int] = None,
        random_seed_override: Optional[int] = None,
    ) -> int:
        """Advance the simulation by *steps* and return the updated step count."""

        with self._lock:
            if reasoner_sync_interval is not None:
                self.config.simulation.reasoner_sync_interval = reasoner_sync_interval
                self.model.config.simulation.reasoner_sync_interval = reasoner_sync_interval
            if random_seed_override is not None:
                self.config.simulation.random_seed = random_seed_override
                self.model.config.simulation.random_seed = random_seed_override
                random.seed(random_seed_override)
                self.model.random.seed(random_seed_override)
            for _ in range(steps):
                self.model.step()
            self._persist()
            return self.model.step_count

    def reset(self) -> int:
        """Recreate the simulation from the persisted ontology state."""

        with self._lock:
            if self.ontology_path.exists():
                self.builder.onto.load(file=str(self.ontology_path))
                self.builder.build_schema()
            self._seed_customers_if_missing()
            rules = build_default_rules(self.builder.onto)
            activate_rules(rules.values())
            self.model = self._create_model()
            return self.model.step_count

    # ---------------------------------------------------------------- projections

    def get_inventory(self) -> List[Dict[str, object]]:
        with self._lock:
            items: List[Dict[str, object]] = []
            for snapshot in self.model.collect_inventory_state():
                entity = self.model.inventory_entities.get(snapshot.book_isbn)
                needs_restock = bool(entity and entity.NeedsRestock and entity.NeedsRestock[0])
                items.append(
                    {
                        "isbn": snapshot.book_isbn,
                        "title": snapshot.title,
                        "price": snapshot.price,
                        "quantity": snapshot.quantity,
                        "low_threshold": snapshot.low_threshold,
                        "needs_restock": needs_restock,
                    }
                )
            return items

    def get_orders(self) -> List[Dict[str, object]]:
        with self._lock:
            orders: List[Dict[str, object]] = []
            for record in self.model.purchase_log:
                entry = record.copy()
                entry.setdefault("genre", "Unknown")
                orders.append(entry)
            return orders

    def get_restocks(self) -> List[Dict[str, object]]:
        with self._lock:
            return [
                {
                    "step": event.step,
                    "isbn": event.book_isbn,
                    "amount": event.amount,
                    "employee_id": event.employee_id,
                }
                for event in self.model.restock_log
            ]

    def get_customers(self) -> List[Dict[str, object]]:
        with self._lock:
            summaries: List[Dict[str, object]] = []
            for customer in self.model.ontology.Customer.instances():
                purchases = customer.HasPurchased or customer.Purchases
                summaries.append(
                    {
                        "customer_id": customer.name,
                        "purchased_books": sorted({book.name for book in purchases}),
                    }
                )
            return summaries

    def get_report(self) -> Dict[str, object]:
        with self._lock:
            data = self.model.generate_report()
            data["steps_run"] = self.model.step_count
            return data

    @property
    def step_count(self) -> int:
        return self.model.step_count


simulation_manager = SimulationManager()

