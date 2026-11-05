"""Reference companion records cannot claim a durable ledger or external action."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "kopano-core"))

from kopano.assert_engine import KopanoAssert, KopanoAssertStore


def make_assertion():
    return KopanoAssert.create("synthetic-session", "GUEST_SEEKER", "FIXTURE", "Synthetic claim")


def test_generated_records_do_not_self_promote_or_invent_residency():
    record = make_assertion()
    assert record.status == "RECORDED_IN_MEMORY"
    assert record.residency == "UNKNOWN"
    assert len(record.proof_hash) == 64


def test_memory_store_cannot_launder_a_verified_label_or_mutate_by_reference():
    store = KopanoAssertStore()
    record = make_assertion()
    record.status = "VERIFIED_ON_LEDGER"
    emitted = store.emit(record)
    assert emitted.status == "RECORDED_IN_MEMORY"
    record.claim = "Changed caller object"
    emitted.claim = "Changed returned object"
    read = store.get(record.assert_id)
    assert read.claim == "Synthetic claim"
    read.status = "VERIFIED_ON_LEDGER"
    assert store.get(record.assert_id).status == "RECORDED_IN_MEMORY"
    listed = store.list_all()
    listed[0].claim = "Changed list object"
    assert store.get(record.assert_id).claim == "Synthetic claim"


def test_new_store_does_not_claim_restart_persistence():
    store = KopanoAssertStore()
    record = store.emit(make_assertion())
    assert store.get(record.assert_id) is not None
    assert KopanoAssertStore().get(record.assert_id) is None
    assert store.list_all(limit=0) == []
    assert store.list_all(limit=-1) == []


def test_reference_chat_does_not_report_external_execution(monkeypatch, tmp_path):
    monkeypatch.setenv("LITELLM_LOCAL_MODEL_COST_MAP", "True")
    from kopano import database
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "synthetic-api.db")
    from kopano import api
    from fastapi.testclient import TestClient

    monkeypatch.setattr(api, "assert_store", KopanoAssertStore())
    client = TestClient(api.app)  # No lifespan/admin bootstrap or provider calls.
    cases = [
        ("find work", "KASILINK_WORK"), ("book football", "FIVES_PITCH"),
        ("car hardware", "CARS4MARS_HARDWARE"), ("learn python", "SOVEREIGN_LEARNING"),
        ("hello", "EVERYDAY_ORCHESTRATION"), ("career", "KASILINK_WORK"),
        ("developer", "EVERYDAY_ORCHESTRATION"),
    ]
    for message, domain in cases:
        response = client.post("/api/kc/chat", json={"message": message})
        assert response.status_code == 200
        result = response.json()
        assert result["response_kind"] == "REFERENCE_GUIDANCE"
        assert result["actions_executed"] is False
        assert result["receipt_storage"] == "PROCESS_MEMORY"
        record = result["assert_receipt"]
        assert record["status"] == "RECORDED_IN_MEMORY"
        assert record["residency"] == "UNKNOWN"
        assert record["intent_domain"] == domain
        readback = client.get(f"/api/kc/assert/{record['assert_id']}")
        assert readback.status_code == 200
        assert readback.json()["status"] == "FOUND_IN_MEMORY"
    listing = client.get("/api/kc/asserts").json()
    assert listing["storage_scope"] == "PROCESS_MEMORY"
    assert listing["residency_region"] == "UNKNOWN"
    assert listing["total_asserts"] == len(cases)
    assert client.get("/api/kc/assert/AST-MISSING-SYNTHETIC").status_code == 404
    client.close()
