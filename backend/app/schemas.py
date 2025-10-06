"""Pydantic request and response models for the FastAPI backend."""

from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RunStepRequest(BaseModel):
    """Request payload for advancing the simulation."""

    steps: int = Field(..., ge=1, description="Number of simulation steps to execute")
    reasoner_sync_interval: Optional[int] = Field(
        None,
        ge=1,
        description="Optional override for the Pellet sync cadence",
    )
    random_seed: Optional[int] = Field(
        None,
        description="Optional override for the RNG seed applied before stepping",
    )


class RunStepResponse(BaseModel):
    """Response emitted after advancing the simulation."""

    steps_advanced: int = Field(..., ge=0)
    step_count: int = Field(..., ge=0)


class InventoryItem(BaseModel):
    isbn: str
    title: str
    price: float
    quantity: int
    low_threshold: int
    needs_restock: bool


class OrderRecord(BaseModel):
    order_id: str
    customer: str
    book: str
    genre: str
    step: int
    price: float


class CustomerSummary(BaseModel):
    customer_id: str
    purchased_books: List[str]


class RestockRecord(BaseModel):
    step: int
    isbn: str
    amount: int
    employee_id: Optional[str]


class ReportResponse(BaseModel):
    """Aggregated view returned by the /report endpoint."""

    steps_run: int
    reasoner_active: bool
    inventory: List[InventoryItem]
    purchases: Dict[str, List[str]]
    restocks: List[RestockRecord]


class ResetResponse(BaseModel):
    """Response for reset actions."""

    step_count: int
    message: str
