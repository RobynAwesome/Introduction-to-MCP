"""Google ADK-style adapter for FEP Artifact 001: Depiction of Nature and Society.

The artifact YAML owns orchestration metadata. This adapter deliberately resolves a
concrete model before constructing the ADK Agent; it never passes the literal value
"auto" to ADK.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml
from google.adk.agents import Agent


ARTIFACT_PATH = Path(__file__).with_name("artifact.yml")


def load_artifact() -> dict[str, Any]:
    """Load the declarative callable-artifact contract."""
    with ARTIFACT_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data.get("kind") != "CallableArtifact":
        raise ValueError("artifact.yml is not a KPGS CallableArtifact")
    return data


def resolve_runtime(contract: dict[str, Any]) -> dict[str, Any]:
    """Resolve identity, seat, interface, and a concrete model with fail-closed semantics."""
    spec = contract["spec"]
    identity_cfg = spec["identity"]
    model_cfg = spec["model_deliberation"]

    auto_env = model_cfg["interface_auto_env"]
    explicit_env = model_cfg["explicit_model_env"]

    auto_model = os.getenv(auto_env)
    explicit_model = os.getenv(explicit_env)

    if auto_model:
        model = auto_model
        auto_selected = True
        selection_reason = f"resolved by interface Auto via {auto_env}"
    elif explicit_model:
        model = explicit_model
        auto_selected = False
        selection_reason = f"explicit model via {explicit_env}"
    else:
        raise RuntimeError(
            "No model resolved. If the IDE has Auto mode, export its concrete selection "
            f"as {auto_env}. Otherwise choose a model and export {explicit_env}."
        )

    if model.strip().lower() == "auto":
        raise RuntimeError("Literal model='auto' is forbidden; export the concrete selected model.")

    identity = os.getenv(
        identity_cfg["identity_env"], identity_cfg.get("preferred_identity", "UNRESOLVED")
    )
    seat = os.getenv(identity_cfg["seat_env"], "UNRESOLVED")
    interface = os.getenv(model_cfg["interface_env"], "UNRESOLVED")
    provider = os.getenv(model_cfg["provider_env"], "UNRESOLVED")

    return {
        "artifact_id": contract["metadata"]["id"],
        "identity_id": identity,
        "seat_id": seat,
        "authority_scope": "task_scoped",
        "interface": interface,
        "provider": provider,
        "model": model,
        "model_version": os.getenv("KPGS_MODEL_VERSION", "UNRESOLVED"),
        "auto_selected": auto_selected,
        "selection_reason": selection_reason,
    }


def runtime_envelope() -> str:
    """Return the current identity/seat/interface/model provenance as JSON."""
    contract = load_artifact()
    return json.dumps(resolve_runtime(contract), indent=2, sort_keys=True)


def classify_evidence(claim: str, evidence_class: str, source: str) -> dict[str, Any]:
    """Validate an FEP E1-E4 evidence classification without upgrading its authority."""
    allowed = {
        "E1": "Direct user testimony",
        "E2": "Repository or physical artifact evidence",
        "E3": "Working inference",
        "E4": "Unknown; forensic audit required",
    }
    code = evidence_class.upper().strip()
    if code not in allowed:
        return {"accepted": False, "error": "evidence_class must be E1, E2, E3, or E4"}
    return {
        "accepted": True,
        "claim": claim,
        "evidence_class": code,
        "meaning": allowed[code],
        "source": source,
        "canonical_empirical_authority": code == "E2",
    }


def can_promote_empirical_claim(evidence_classes: list[str]) -> dict[str, Any]:
    """Apply the Artifact 001 minimum empirical-promotion gate."""
    normalized = {item.upper().strip() for item in evidence_classes}
    has_e2 = "E2" in normalized
    return {
        "verdict": "ELIGIBLE_FOR_VALIDATION" if has_e2 else "HOLD",
        "reason": (
            "E2 artifact evidence is present; continue through PKA/POC validation."
            if has_e2
            else "No E2 evidence. Preserve as testimony/inference/unknown; do not promote."
        ),
        "evidence_classes": sorted(normalized),
    }


def prepare_receipt_payload(
    question: str,
    subject: str,
    evidence_refs: list[str],
    epistemic_states: list[str],
    unknowns: list[str],
    pka_verdict: str,
    poc_foc_verdict: str,
) -> dict[str, Any]:
    """Prepare, but do not persist, a Smart Ledger-compatible invocation payload."""
    contract = load_artifact()
    runtime = resolve_runtime(contract)
    return {
        **runtime,
        "question": question,
        "subject": subject,
        "evidence_refs": evidence_refs,
        "epistemic_states": epistemic_states,
        "unknowns": unknowns,
        "pka_verdict": pka_verdict,
        "poc_foc_verdict": poc_foc_verdict,
        "ledger_target": contract["spec"]["ledger"]["engine"],
        "write_policy": "PREPARE_ONLY_UNTIL_ADMISSION_GATE",
    }


def build_instruction(contract: dict[str, Any], runtime: dict[str, Any]) -> str:
    """Compile the artifact contract into a compact ADK system instruction."""
    workflow = "\n".join(
        f"{step['step']}. {step['id']}: {step['action']}"
        for step in contract["spec"]["workflow"]
    )
    guardrails = "\n".join(f"- {item}" for item in contract["spec"]["guardrails"])

    return f"""
You are executing KPGS callable artifact: {contract['metadata']['name']}.

RUNTIME PROVENANCE
{json.dumps(runtime, indent=2, sort_keys=True)}

PURPOSE
{contract['spec']['purpose']}

FORENSIC LANES
Keep [NATURE], [SOCIETY], [INTERACTION], and [UNKNOWN] isolated before synthesis.
Use E1-E4 evidence classes. Preserve partial knowledge under PKA.
CDP may hold multiple explanations. CCP may select a candidate for validation.
Selection, consensus, confidence, and CRUD mutation are never automatic proof.

WORKFLOW
{workflow}

GUARDRAILS
{guardrails}

OUTPUT REQUIREMENT
Return a structured depiction, evidence matrix, relationship map, causal candidate set,
governance learning/HOLD state, and a Smart Ledger receipt payload. Never fabricate a
seat, source, model provenance field, causal mechanism, or missing evidence.
""".strip()


def create_root_agent() -> Agent:
    """Create the ADK Agent after KPGS has resolved the runtime model and identity envelope."""
    contract = load_artifact()
    runtime = resolve_runtime(contract)
    return Agent(
        name="fep_depiction_of_nature_and_society",
        model=runtime["model"],
        instruction=build_instruction(contract, runtime),
        tools=[
            runtime_envelope,
            classify_evidence,
            can_promote_empirical_claim,
            prepare_receipt_payload,
        ],
    )


# ADK discovery can use root_agent when the launching interface has already resolved a model.
# Keeping this conditional makes repository imports/test discovery safe without fabricating
# a default model choice.
if os.getenv("KPGS_INTERFACE_SELECTED_MODEL") or os.getenv("KPGS_EXPLICIT_MODEL"):
    root_agent = create_root_agent()
else:
    root_agent = None


__all__ = [
    "create_root_agent",
    "root_agent",
    "runtime_envelope",
    "classify_evidence",
    "can_promote_empirical_claim",
    "prepare_receipt_payload",
]
