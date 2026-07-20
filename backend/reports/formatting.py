"""Shared human-readable label formatting for report/report-service prose.

Kept in sync with frontend/src/utils/format.js's WORD_OVERRIDES so a
scenario or commodity type reads the same whether it's rendered by the
API or the UI.
"""

from __future__ import annotations

_WORD_OVERRIDES = {
    "ais": "AIS",
    "spr": "SPR",
    "opec": "OPEC+",
    "lng": "LNG",
    "id": "ID",
}


def humanize(value: object) -> str:
    """Turns a SCREAMING_SNAKE_CASE enum value (e.g. `HORMUZ_PARTIAL_CLOSURE`,
    `CRUDE_OIL`) into a human-readable label (`Hormuz Partial Closure`,
    `Crude Oil`) for prose - the raw enum stays untouched everywhere else
    (schemas, ids, audit references)."""
    if value is None:
        return ""
    text = str(value)
    words = [word for word in text.replace("_", " ").split() if word]
    return " ".join(_WORD_OVERRIDES.get(word.lower(), word.capitalize()) for word in words)
