"""Smoke tests for the starter project."""

from bms.config import load_config


def test_load_config_defaults() -> None:
    config = load_config()
    assert config.simulation.max_steps > 0
    assert config.ontology.ontology_iri.startswith("http://")
