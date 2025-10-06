"""Ontology construction helpers using Owlready2."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping, Optional

from owlready2 import DataProperty, ObjectProperty, Thing, get_ontology


class BookstoreOntologyBuilder:
    """Build and populate the core bookstore ontology schema."""

    def __init__(self, ontology_iri: str, storage_path: str) -> None:
        self.ontology_iri = ontology_iri
        self.storage_path = Path(storage_path).resolve()
        self.onto = get_ontology(ontology_iri)

    def build_schema(self) -> None:
        """Declare base classes and properties used across the system."""

        with self.onto:
            class Book(Thing):
                pass

            class Customer(Thing):
                pass

            class Employee(Thing):
                pass

            class Inventory(Thing):
                pass

            class InventoryItem(Inventory):  # type: ignore[misc]
                """Legacy alias retained for backward compatibility."""

                pass

            class Order(Thing):
                pass

            class HasTitle(DataProperty):
                domain = [Book]
                range = [str]

            class HasAuthor(DataProperty):
                domain = [Book]
                range = [str]

            class HasGenre(DataProperty):
                domain = [Book]
                range = [str]

            class HasPrice(DataProperty):
                domain = [Book]
                range = [float]

            class HasInventory(ObjectProperty):
                domain = [Book]
                range = [Inventory]

            class AvailableQuantity(DataProperty):
                domain = [Inventory]
                range = [int]

            class NeedsRestock(DataProperty):
                domain = [Inventory]
                range = [bool]

            class LowThreshold(DataProperty):
                domain = [Inventory]
                range = [int]

            class TracksBook(ObjectProperty):
                domain = [Inventory]
                range = [Book]

            class Purchases(ObjectProperty):
                domain = [Customer]
                range = [Book]

            class HasPurchased(ObjectProperty):
                domain = [Customer]
                range = [Book]

            class HasBudget(DataProperty):
                domain = [Customer]
                range = [float]

            class OrderedBy(ObjectProperty):
                domain = [Order]
                range = [Customer]

            class OrderedBook(ObjectProperty):
                domain = [Order]
                range = [Book]

            class WorksAt(ObjectProperty):
                domain = [Employee]
                range = [Inventory]

    def add_inventory(self, items: Iterable[Mapping[str, object]], default_threshold: int) -> None:
        """Create book and inventory individuals for the supplied records."""

        with self.onto:
            for record in items:
                isbn = str(record["isbn"])
                book = self.onto.Book(isbn)
                book.HasTitle = [record.get("title", "")]
                book.HasAuthor = [record.get("author", "")]
                book.HasGenre = [record.get("genre", "")]
                book.HasPrice = [record.get("price", 0.0)]
                threshold = int(record.get("low_threshold", default_threshold))
                inventory = self.ensure_inventory_for(book)
                quantity = int(record.get("quantity", 0))
                inventory.AvailableQuantity = [quantity]
                inventory.LowThreshold = [threshold]
                inventory.NeedsRestock = [quantity < threshold]
                if hasattr(inventory, "TracksBook") and not getattr(inventory, "TracksBook", []):
                    inventory.TracksBook = [book]

    def add_customers(self, customers: Iterable[Mapping[str, object]], default_budget: float = 50.0) -> bool:
        """Create customer individuals for the supplied profiles."""

        updated = False
        with self.onto:
            for record in customers:
                identifier = str(record.get("id") or record.get("customer_id") or record.get("name") or "").strip()
                if not identifier:
                    continue
                name = identifier.replace("::", "_")
                customer = self.onto.Customer(name)
                try:
                    budget_value = float(record.get("budget", default_budget))
                except (TypeError, ValueError):
                    budget_value = float(default_budget)
                existing = list(getattr(customer, "HasBudget", []))
                if not existing:
                    customer.HasBudget = [budget_value]
                    updated = True
                elif float(existing[0]) != budget_value:
                    customer.HasBudget = [budget_value]
                    updated = True
        return updated

    def ensure_inventory_for(self, book: "Thing") -> "Thing":
        """Return the inventory individual linked to *book*, creating one if missing."""

        inventory = next(iter(book.HasInventory), None)
        if inventory is not None:
            return inventory

        legacy_inventory = self._find_inventory_tracking_book(book)
        if legacy_inventory is not None:
            if legacy_inventory not in book.HasInventory:
                book.HasInventory.append(legacy_inventory)
            return legacy_inventory

        inventory_name = f"inv_{book.name}"
        inventory = self.onto.Inventory(inventory_name)
        if inventory not in book.HasInventory:
            book.HasInventory.append(inventory)
        return inventory

    def get_inventory_for_isbn(self, isbn: str) -> Optional["Thing"]:
        """Fetch the inventory individual associated with *isbn* if one exists."""

        book = self._find_book_by_isbn(isbn)
        if book is None:
            return None
        if book.HasInventory:
            return book.HasInventory[0]

        inventory = self._find_inventory_tracking_book(book)
        if inventory is not None and inventory not in book.HasInventory:
            book.HasInventory.append(inventory)
        return inventory

    def save(self) -> Path:
        """Persist the ontology to disk and return the file path."""

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.onto.save(file=str(self.storage_path))
        return self.storage_path

    # -------------------------------------------------------------- internals

    def _find_book_by_isbn(self, isbn: str) -> Optional["Thing"]:
        for book in self.onto.Book.instances():
            if book.name == isbn:
                return book
        return None

    def _find_inventory_tracking_book(self, book: "Thing") -> Optional["Thing"]:
        inventory_class = getattr(self.onto, "Inventory", None)
        if inventory_class is None:
            return None
        for candidate in inventory_class.instances():
            tracks = getattr(candidate, "TracksBook", [])
            if tracks and book in tracks:
                return candidate
        return None


__all__ = ["BookstoreOntologyBuilder"]
