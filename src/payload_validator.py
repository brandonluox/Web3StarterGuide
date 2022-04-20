from __future__ import annotations

from typing import Any, Dict

REQUIRED_FIELDS = ["id", "timestamp", "network", "op_type", "target", "amount"]


def validate_payload(payload: Dict[str, Any]) -> None:
    """Ensure payload shape meets AuroraLedger expectations."""
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise ValueError(f"Missing payload keys: {', '.join(missing)}")
    if not isinstance(payload["amount"], (int, float)):
        raise TypeError("Payload amount must be numeric.")
    if payload["amount"] < 0:
        raise ValueError("Payload amount cannot be negative.")
