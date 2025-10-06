"""Agent definitions for the Mesa-based bookstore simulation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mesa import Agent

from .message_bus import MessageBus
from .policies import DecisionPolicy
from .state import InventorySnapshot

if TYPE_CHECKING:  # pragma: no cover - used for type hints only
    from .model import BookstoreModel


class BookAgent(Agent):
    """Passive agent that exposes the state of an inventory item."""

    def __init__(self, unique_id: str, model: BookstoreModel, snapshot: InventorySnapshot) -> None:
        super().__init__(unique_id, model)
        self.snapshot = snapshot

    def step(self) -> None:  # pragma: no cover - placeholder
        """Books do not actively perform actions yet."""


class CustomerAgent(Agent):
    """Customer who may purchase books based on a decision policy."""

    def __init__(
        self,
        unique_id: str,
        model: BookstoreModel,
        policy: DecisionPolicy,
        budget: float,
    ) -> None:
        super().__init__(unique_id, model)
        self.policy = policy
        self.budget = budget

    def step(self) -> None:
        if self.random.random() > self.model.config.simulation.customer_spawn_chance:
            return
        inventory = list(self.model.collect_inventory_state())
        decision = self.policy.choose_purchase(inventory, self.budget, rng=self.random)
        if decision is None:
            return
        book_id, unit_price = decision
        if self.budget < unit_price:
            return
        self.budget -= unit_price
        self.model.message_bus.publish(
            topic="purchases",
            payload={
                "customer_id": self.unique_id,
                "book_id": book_id,
                "price": unit_price,
            },
        )


class EmployeeAgent(Agent):
    """Employee responsible for reacting to restock notifications."""

    def __init__(self, unique_id: str, model: BookstoreModel, message_bus: MessageBus) -> None:
        super().__init__(unique_id, model)
        self.message_bus = message_bus

    def step(self) -> None:
        while True:
            message = self.message_bus.poll(topic="restock")
            if message is None:
                break
            book_id = message.payload.get("book_id")
            amount = message.payload.get(
                "amount",
                self.model.config.simulation.restock_amount,
            )
            if book_id is None:
                continue
            self.model.restock_inventory(book_id, int(amount), employee_id=self.unique_id)


__all__ = [
    "BookAgent",
    "CustomerAgent",
    "EmployeeAgent",
    "InventorySnapshot",
]
