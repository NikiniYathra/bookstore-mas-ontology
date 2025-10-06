"""Default SWRL rule definitions for the bookstore ontology."""

from __future__ import annotations

import logging
from typing import Dict, Iterable

from owlready2 import Imp, Ontology, Thing

LOGGER = logging.getLogger(__name__)

RuleMap = Dict[str, Imp]

_CONFIRM_PURCHASE_RULE = (
    "Customer(?c) ^ Purchases(?c, ?b) -> HasPurchased(?c, ?b)"
)

_LOW_STOCK_RULE = (
    "Inventory(?i) ^ AvailableQuantity(?i, ?q) ^ LowThreshold(?i, ?t) ^ "
    "swrlb:lessThan(?q, ?t) -> NeedsRestock(?i, true)"
)

_CLEAR_LOW_STOCK_RULE = (
    "Inventory(?i) ^ AvailableQuantity(?i, ?q) ^ LowThreshold(?i, ?t) ^ "
    "swrlb:greaterThanOrEqual(?q, ?t) -> NeedsRestock(?i, false)"
)

_SWRLB_IRI = "http://www.w3.org/2003/11/swrlb#"
_SWRL_BUILTINS = ("lessThan", "greaterThanOrEqual")


def _ensure_swrlb_stub(ontology: Ontology) -> bool:
    """Ensure the swrlb namespace exposes the builtins we rely on."""

    world = ontology.world
    swrlb = world.get_ontology(_SWRLB_IRI).load()
    with swrlb:
        if getattr(swrlb, "lessThan", None) is None:
            class lessThan(Thing):  # type: ignore[valid-type]
                pass
        if getattr(swrlb, "greaterThanOrEqual", None) is None:
            class greaterThanOrEqual(Thing):  # type: ignore[valid-type]
                pass
    missing = [name for name in _SWRL_BUILTINS if getattr(swrlb, name, None) is None]
    return not missing


def build_default_rules(ontology: Ontology) -> RuleMap:
    """Register core SWRL rules on *ontology* and return them."""

    builtins_ready = _ensure_swrlb_stub(ontology)

    rule_specs = {
        "confirm_purchase": ("ConfirmPurchase", _CONFIRM_PURCHASE_RULE),
        "low_stock": ("LowStockFlag", _LOW_STOCK_RULE),
        "clear_low_stock": ("ClearLowStockFlag", _CLEAR_LOW_STOCK_RULE),
    }

    rules: RuleMap = {}
    with ontology:
        for key, (name, source) in rule_specs.items():
            rule = Imp()
            rule.name = name
            register_source = source
            for builtin in _SWRL_BUILTINS:
                register_source = register_source.replace(f"swrlb:{builtin}", builtin)
            try:
                rule.set_as_rule(register_source)
            except ValueError as exc:
                LOGGER.warning("Failed to register SWRL rule '%s': %s", name, exc)
                continue
            rules[key] = rule
    if not builtins_ready and ("low_stock" in rules or "clear_low_stock" in rules):
        LOGGER.warning(
            "SWRL built-ins could not be fully initialised; low-stock rules will rely on procedural checks as backup.")
    return rules


def activate_rules(rules: Iterable[Imp]) -> None:
    """Ensure the supplied rules are marked as active."""

    for rule in rules:
        try:
            rule.set_active(True)
        except AttributeError:  # pragma: no cover - depends on Owlready internals
            LOGGER.debug("SWRL rule '%s' does not expose set_active", rule.name)


__all__ = ["build_default_rules", "activate_rules", "RuleMap"]
