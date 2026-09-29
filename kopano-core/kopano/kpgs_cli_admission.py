"""Shared admission for CLI entrypoints that persist KPGS/Main Brain state."""

from __future__ import annotations

from typing import Any

from .kpgs_activation_gate import require_alp_receipt
from .kpgs_renter_entry import assert_and_log_entry


def admit_cli_renter(
    *,
    renter_id: str,
    renter_class: str,
    hood_ack: str,
    operation: str,
) -> dict[str, Any]:
    """Validate and receipt a CLI renter before obtaining the ALP execution receipt."""
    if not renter_id.strip():
        raise ValueError("[KPGS_HOOD_ENTRY] BLOCK — --renter-id is required")
    entry = assert_and_log_entry(
        renter_id=renter_id,
        renter_class=renter_class,
        hood_ack=hood_ack,
        operation=operation,
    )
    return {"hood_entry": entry, "alp_receipt": require_alp_receipt()}
