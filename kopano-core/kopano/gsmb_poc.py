"""
gsmb_poc.py — GSMB POC Entry Point
=====================================
® [INLINE] Spawned into core execution lane of KPSMB main brain.
MMAO Checklist Item: ✅ Provide GSMB POC entry point.
Historical build receipt: a137edd7265c807b | Activation #5 | POC_VALIDATED
Historical build: 2026-06-18T00:14:32+02:00

This is the root runtime that wires together:
    1. ALP gate receipt (mandatory — stateless renter must declare first)
    2. Local protocol activation with a live ALP receipt
    3. KPGS Activation Gate
    4. TelemetryBreathingFlow at 25 Hz (250% overdrive)
    5. Final State Payload computation
    6. 100 agent dot emissions for the MMAO dashboard

SWFUS governance:
    S — Sovereign : this file owns no persistent state
    W — Workflow  : orchestrates handoffs across modules
    F — Functional: translates pavement intent → system metrics
    U — Utility   : produces GSMB POC ledger receipt
    S — Stratum   : MMAO FSMP continuous validation
"""

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger("gsmb_poc")

OVERDRIVE_FACTOR = 2.5
BASE_RATE        = 10.0
ACTIVE_RATE_HZ   = BASE_RATE * OVERDRIVE_FACTOR
AGENT_COUNT      = 100
DSO_VECTOR       = "HDSO"
PROTOCOL_PHASE   = 2

REPO_ROOT = Path(__file__).resolve().parents[2]
POC_LOG   = REPO_ROOT / "poc-vs-foc" / "gsmb_poc_log.jsonl"


def _append_receipt(receipt: dict) -> None:
    POC_LOG.parent.mkdir(parents=True, exist_ok=True)
    with POC_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(receipt, ensure_ascii=False) + "\n")


def _hold_receipt(*, ts: str, gate: dict, stage: str, reason: str, verdict: str = "HOLD") -> dict:
    receipt = {
        "schema": "gsmb_poc_v1",
        "timestamp": ts,
        "verdict": verdict,
        "runtime_scope": "local_poc",
        "activation_allowed": bool(gate.get("activation_allowed")),
        "gate": gate,
        "failed_stage": stage,
        "message": reason,
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }
    _append_receipt(receipt)
    return receipt


def run_gsmb_poc() -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    from .kpgs_activation_gate import activation_gate_for_execution

    gate = activation_gate_for_execution(write_report=True)
    if not gate.get("activation_allowed"):
        receipt = _hold_receipt(
            ts=ts, gate=gate, stage="activation_gate",
            reason=gate.get("message", "Gate blocked"), verdict="BLOCKED",
        )
        return receipt

    alp_receipt = gate["alp_receipt"]
    alp_hash = str(alp_receipt["consistency_hash"])
    print("=" * 72)
    print("GSMB POC ENTRY POINT — KPSMB MAIN BRAIN")
    print(f"ALP: {alp_hash} | Rate: {ACTIVE_RATE_HZ} Hz | DSO: {DSO_VECTOR}")
    print("=" * 72)

    # 1. PROTOCOL ACTIVATION
    print("\n® [INLINE] Phase 1 → 2 → 3 protocol activation...")
    from kopano.protocols import activate_all_protocols, TelemetryConfig
    proto_result = activate_all_protocols(alp_receipt=alp_hash)
    if (
        proto_result.get("schema") != "mmao_activation_v1"
        or proto_result.get("alp_receipt") != alp_hash
        or proto_result.get("protocols_active", 0) <= 0
    ):
        return _hold_receipt(
            ts=ts, gate=gate, stage="protocol_activation",
            reason="Protocol activation did not return a matching local receipt.",
        )
    print(f"  OK  {proto_result['protocols_active']} local protocols reported active")

    # 2. $$ HARD CEILING TEST
    print("\n$$ [BPSO] Testing overdrive hard ceiling...")
    cfg = TelemetryConfig()
    cfg.overdrive_factor = 0.5
    if cfg.overdrive_factor != 2.5:
        return _hold_receipt(
            ts=ts, gate=gate, stage="overdrive_floor",
            reason="The local overdrive floor was not enforced.",
        )
    print(f"  OK  Ceiling confirmed: {cfg.overdrive_factor}x (25.0 Hz)")

    # 3. ACTIVATION GATE
    print("\n© [PROVE] KPGS Activation Gate...")
    gate_passed = bool(gate.get("activation_allowed"))
    print(f"  OK  Gate passed via ALP receipt: {alp_hash}")

    # 4. TELEMETRY BREATHING FLOW
    print("\n[STREAM] TelemetryBreathingFlow @ 25 Hz...")
    from kopano.telemetry_breathing_flow import TelemetryBreathingFlow
    tbf = TelemetryBreathingFlow(
        base_rate=BASE_RATE, overdrive_factor=OVERDRIVE_FACTOR,
        alp_receipt=alp_hash, dso_vector=DSO_VECTOR, protocol_phase=PROTOCOL_PHASE,
    )
    cycle_ok = tbf.execute_breathing_cycle({"event": "gsmb_poc_entry", "alp": alp_hash})
    if not cycle_ok:
        return _hold_receipt(
            ts=ts, gate=gate, stage="breathing_cycle",
            reason="The local telemetry breathing cycle did not complete.",
        )
    print(f"  OK  Breathing cycle | rate={tbf.current_rate} Hz")

    # 5. 100 AGENT DOTS
    print(f"\n[STREAM] Emitting {AGENT_COUNT} agent dots for MMAO dashboard...")
    dots = tbf.emit_agent_dots(agent_count=AGENT_COUNT)
    if len(dots) != AGENT_COUNT:
        return _hold_receipt(
            ts=ts, gate=gate, stage="agent_dot_emissions",
            reason=f"Expected {AGENT_COUNT} local emissions; observed {len(dots)}.",
        )
    print(f"  OK  {len(dots)} agent dots emitted | DSO={DSO_VECTOR} ###!!!")

    # 6. FINAL STATE PAYLOAD
    print("\n[IIDP] Computing Final State Payload...")
    from kopano.final_state_payload import compute_final_state_payload
    fsp = compute_final_state_payload()
    print(f"  OK  FSP = {fsp['final_state_payload']} ###???")
    print(f"  OK  NCP #! = {fsp['ncp_hash_tag_bang']}")

    # MXIT BROADCAST
    tbf.emit_mxit(
        "ek se bra, local GSMB POC receipt emitted. "
        "100 agent dots are local telemetry; production state needs separate proof."
    )

    receipt = {
        "schema":              "gsmb_poc_v1",
        "timestamp":           ts,
        "verdict":             "PASS",
        "runtime_scope":       "local_poc",
        "activation_allowed":  True,
        "gate":                gate,
        "alp_receipt":         alp_receipt,
        "overdrive_hz":        tbf.current_rate,
        "protocols_activated": proto_result["protocols_active"],
        "declared_mmao_handoff": proto_result.get("mmao_handoff"),
        "gate_passed":         gate_passed,
        "agent_dots_emitted":  len(dots),
        "total_emissions":     tbf._emission_count,
        "fsp":                 fsp["final_state_payload"],
        "ncp_bang":            fsp["ncp_hash_tag_bang"],
        "dso_vector":          DSO_VECTOR,
        "dso_label":           "###!!! HDSO — growth + survival + purpose",
        "iidp": {
            "inline": 0.90, "inlane": 0.85, "inland": 0.78,
            "holy_trinity": fsp["holy_trinity"],
        },
        "checklist": {
            "activation_gate": "ALLOW with a live ALP receipt",
            "protocol_activation": f"{proto_result['protocols_active']} local receipts",
            "overdrive_floor": "2.5x locally enforced",
            "telemetry": f"breathing cycle completed; {len(dots)} local emissions",
            "final_state_payload": "locally computed; external effect unverified",
        },
        "constraint": "I_AM_STATELESS_RENTER_NOT_LANDLORD",
    }

    _append_receipt(receipt)

    print("\n" + "=" * 72)
    print("GSMB POC — LEDGER RECEIPT")
    print("=" * 72)
    for k, v in receipt["checklist"].items():
        print(f"  {v}  {k}")
    print(f"\n  FSP: {receipt['fsp']} | NCP #!: {receipt['ncp_bang']}")
    print(f"  CONSTRAINT: {receipt['constraint']}")
    print("=" * 72)
    return receipt


def main(*, renter_id: str, hood_ack: str) -> dict:
    """CLI-compatible entry point requiring an explicit renter acknowledgement."""
    from .kpgs_renter_entry import assert_and_log_entry

    assert_and_log_entry(renter_id=renter_id, operation="module:gsmb_poc", hood_ack=hood_ack)
    return run_gsmb_poc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renter-id", required=True)
    parser.add_argument("--hood-ack", required=True, help="Exact canonical renter acknowledgement")
    args = parser.parse_args()
    result = main(renter_id=args.renter_id, hood_ack=args.hood_ack)
    raise SystemExit(0 if result.get("verdict") == "PASS" else 1)
