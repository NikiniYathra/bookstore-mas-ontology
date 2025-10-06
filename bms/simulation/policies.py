"""Decision policies that drive agent behaviour."""

from __future__ import annotations

from abc import ABC, abstractmethod
from random import Random
from typing import Iterable, Optional, Tuple

from .state import InventorySnapshot

InventoryDecision = Optional[Tuple[str, float]]


class DecisionPolicy(ABC):
    """Strategy object that selects which book a customer buys."""

    @abstractmethod
    def choose_purchase(
        self,
        inventory: Iterable[InventorySnapshot],
        budget: float,
        rng: Random | None = None,
    ) -> InventoryDecision:
        raise NotImplementedError


class GreedyPurchasePolicy(DecisionPolicy):
    """Pick the cheapest in-stock book within the given budget."""

    def choose_purchase(
        self,
        inventory: Iterable[InventorySnapshot],
        budget: float,
        rng: Random | None = None,
    ) -> InventoryDecision:
        affordable_books = [item for item in inventory if item.price <= budget and item.quantity > 0]
        if not affordable_books:
            return None
        choice = min(affordable_books, key=lambda item: item.price)
        return choice.book_isbn, choice.price


class RandomPurchasePolicy(DecisionPolicy):
    """Pick a random affordable book to simulate browsing behaviour."""

    def choose_purchase(
        self,
        inventory: Iterable[InventorySnapshot],
        budget: float,
        rng: Random | None = None,
    ) -> InventoryDecision:
        affordable_books = [item for item in inventory if item.price <= budget and item.quantity > 0]
        if not affordable_books:
            return None
        generator = rng or Random()
        choice = generator.choice(affordable_books)
        return choice.book_isbn, choice.price


__all__ = [
    "DecisionPolicy",
    "GreedyPurchasePolicy",
    "RandomPurchasePolicy",
    "InventoryDecision",
]
