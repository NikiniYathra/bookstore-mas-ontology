from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InventorySnapshot:
    """Lightweight view of a book's inventory state."""

    book_isbn: str
    title: str
    quantity: int
    price: float
    low_threshold: int


__all__ = ["InventorySnapshot"]
