"""Reusable graph query functions used by risk and recommendation agents (Phase 3, section 3.4)."""

from __future__ import annotations


def get_refineries_exposed_to_chokepoint(chokepoint_id: str) -> list[dict]:
    pass


def get_alternative_suppliers(commodity: str, blocked_supplier_id: str) -> list[dict]:
    pass


def get_routes_for_supplier(supplier_id: str) -> list[dict]:
    pass


def get_scenarios_triggered_by_event(event_id: str) -> list[dict]:
    pass


def get_spr_sites_for_refinery(refinery_id: str) -> list[dict]:
    pass
