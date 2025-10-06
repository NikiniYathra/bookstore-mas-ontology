"""FastAPI application exposing the Bookstore simulation endpoints."""

from __future__ import annotations

import logging
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import schemas
from .simulation_manager import simulation_manager

LOGGER = logging.getLogger(__name__)

app = FastAPI(title="Bookstore MAS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/run-step", response_model=schemas.RunStepResponse)
def run_step(payload: schemas.RunStepRequest) -> schemas.RunStepResponse:
    if payload.steps <= 0:
        raise HTTPException(status_code=422, detail="steps must be positive")
    steps_advanced = payload.steps
    step_count = simulation_manager.run_steps(
        steps=payload.steps,
        reasoner_sync_interval=payload.reasoner_sync_interval,
        random_seed_override=payload.random_seed,
    )
    return schemas.RunStepResponse(steps_advanced=steps_advanced, step_count=step_count)


@app.get("/inventory", response_model=List[schemas.InventoryItem])
def get_inventory() -> List[schemas.InventoryItem]:
    items = simulation_manager.get_inventory()
    return [schemas.InventoryItem(**item) for item in items]


@app.get("/orders", response_model=List[schemas.OrderRecord])
def get_orders() -> List[schemas.OrderRecord]:
    orders = simulation_manager.get_orders()
    return [
        schemas.OrderRecord(
            order_id=entry.get("order"),
            customer=entry.get("customer"),
            book=entry.get("book"),
            genre=entry.get("genre", "Unknown"),
            step=entry.get("step", 0),
            price=float(entry.get("price", 0.0)),
        )
        for entry in orders
    ]


@app.get("/customers", response_model=List[schemas.CustomerSummary])
def get_customers() -> List[schemas.CustomerSummary]:
    customers = simulation_manager.get_customers()
    return [
        schemas.CustomerSummary(
            customer_id=entry["customer_id"],
            purchased_books=list(entry["purchased_books"]),
        )
        for entry in customers
    ]


@app.get("/restocks", response_model=List[schemas.RestockRecord])
def get_restocks() -> List[schemas.RestockRecord]:
    events = simulation_manager.get_restocks()
    return [schemas.RestockRecord(**event) for event in events]


@app.get("/report", response_model=schemas.ReportResponse)
def get_report() -> schemas.ReportResponse:
    report = simulation_manager.get_report()
    inventory_items = [schemas.InventoryItem(**item) for item in report.get("inventory", [])]
    restocks = [schemas.RestockRecord(**event) for event in report.get("restocks", [])]
    purchases = {key: list(value) for key, value in report.get("purchases", {}).items()}
    return schemas.ReportResponse(
        steps_run=report.get("steps_run", simulation_manager.step_count),
        reasoner_active=report.get("reasoner_active", True),
        inventory=inventory_items,
        purchases=purchases,
        restocks=restocks,
    )


@app.post("/reset", response_model=schemas.ResetResponse)
def reset_simulation() -> schemas.ResetResponse:
    step_count = simulation_manager.reset()
    return schemas.ResetResponse(step_count=step_count, message="Simulation reset")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
