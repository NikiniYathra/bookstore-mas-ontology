"""Minimal message bus to decouple Mesa agents."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, Optional


@dataclass
class Message:
    """Lightweight container for agent communication payloads."""

    topic: str
    payload: Dict[str, Any]


class MessageBus:
    """In-memory pub/sub queue with FIFO semantics."""

    def __init__(self) -> None:
        self._topics: Dict[str, Deque[Message]] = {}

    def publish(self, topic: str, payload: Dict[str, Any]) -> None:
        queue = self._topics.setdefault(topic, deque())
        queue.append(Message(topic=topic, payload=payload))

    def poll(self, topic: str) -> Optional[Message]:
        queue = self._topics.get(topic)
        if not queue:
            return None
        return queue.popleft()

    def clear(self) -> None:
        self._topics.clear()


__all__ = ["Message", "MessageBus"]
