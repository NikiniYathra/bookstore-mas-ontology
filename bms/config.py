"""Application wide configuration models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SimulationSettings(BaseModel):
    """Tunable parameters for the Mesa simulation."""

    max_steps: int = Field(100, description="Number of ticks before the run halts")
    customer_spawn_chance: float = Field(
        0.4,
        ge=0.0,
        le=1.0,
        description="Probability that a customer enters the store each tick",
    )
    restock_threshold: int = Field(
        5,
        ge=0,
        description="Default LowThreshold value when sample data omits it",
    )
    reasoner_sync_interval: int = Field(
        3,
        ge=1,
        description="Frequency (in steps) to sync the Pellet reasoner",
    )
    restock_amount: int = Field(
        10,
        ge=1,
        description="Number of copies procured when inventory is replenished",
    )
    random_seed: Optional[int] = Field(
        12345,
        description="Seed for reproducible Mesa agent behaviour",
    )


class OntologySettings(BaseModel):
    """File-system settings for ontology persistence."""

    ontology_iri: str = Field(
        "http://example.org/bookstore",
        description="Base IRI for the ontology individuals and schema",
    )
    storage_path: str = Field(
        "bms/data/bookstore_ontology.owl",
        description="Relative path where the ontology is saved",
    )


class AppConfig(BaseModel):
    """Top-level configuration container."""

    simulation: SimulationSettings = SimulationSettings()
    ontology: OntologySettings = OntologySettings()


def load_config() -> AppConfig:
    """Return an instance of :class:`AppConfig` using default values."""

    return AppConfig()


__all__ = ["AppConfig", "SimulationSettings", "OntologySettings", "load_config"]
