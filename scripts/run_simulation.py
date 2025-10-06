"""Command-line entry point for running the BMS demo simulation."""

from __future__ import annotations

import json
import logging
import random
from pathlib import Path

from bms.config import load_config
from bms.ontology import BookstoreOntologyBuilder, build_default_rules
from bms.ontology.rules import activate_rules
from bms.simulation import BookstoreModel

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

ROOT = Path(__file__).resolve().parents[1]


def _load_sample_inventory() -> list[dict[str, object]]:
    data_path = ROOT / "bms" / "data" / "sample_inventory.json"
    with data_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    config = load_config()
    if config.simulation.random_seed is not None:
        random.seed(config.simulation.random_seed)

    builder = BookstoreOntologyBuilder(
        ontology_iri=config.ontology.ontology_iri,
        storage_path=config.ontology.storage_path,
    )
    builder.build_schema()
    builder.add_inventory(
        _load_sample_inventory(),
        default_threshold=config.simulation.restock_threshold,
    )
    builder.save()

    rules = build_default_rules(builder.onto)
    activate_rules(rules.values())

    model = BookstoreModel(builder=builder, config=config)
    for _ in range(config.simulation.max_steps):
        model.step()

    report = model.generate_report()
    final_ontology_path = builder.save()
    print("\nSimulation complete.")
    print(f"Ontology saved to: {final_ontology_path}")


if __name__ == "__main__":
    main()
