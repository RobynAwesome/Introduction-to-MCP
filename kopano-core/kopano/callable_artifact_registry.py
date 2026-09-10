"""KPGS callable artifact parser and registry.

Loads declarative `artifact.yml` packages from `governance/kpgs-artifacts/`,
validates the minimum v1alpha1 contract, resolves aliases, preserves versioned
semantic bindings, and emits RTC Evolution runtime envelopes.

This parser does not make epistemic claims true and does not persist to Smart
Ledger by itself. It prepares governed runtime state for the appropriate engines.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any, Iterable, Optional

import yaml


API_VERSION = "kpgs.kopanolabs/v1alpha1"
KIND = "CallableArtifact"


class ArtifactContractError(ValueError):
    """Raised when an artifact violates the minimum callable-artifact contract."""


@dataclass(frozen=True)
class ArtifactRuntimeEnvelope:
    artifact_id: str
    identity_id: str
    seat_id: str
    authority_scope: str
    interface: str
    provider: str
    model: str
    model_version: str
    auto_selected: bool
    selection_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "identity_id": self.identity_id,
            "seat_id": self.seat_id,
            "authority_scope": self.authority_scope,
            "interface": self.interface,
            "provider": self.provider,
            "model": self.model,
            "model_version": self.model_version,
            "auto_selected": self.auto_selected,
            "selection_reason": self.selection_reason,
        }


@dataclass(frozen=True)
class CallableArtifact:
    path: Path
    document: dict[str, Any]

    @property
    def artifact_id(self) -> str:
        return str(self.document["metadata"]["id"])

    @property
    def aliases(self) -> tuple[str, ...]:
        aliases = self.document["spec"].get("invocation", {}).get("aliases", [])
        return tuple(str(alias) for alias in aliases)

    def semantic_binding(self, token: str, namespace: Optional[str] = None) -> Any:
        """Resolve a semantic token without flattening versioned/namespaced meanings."""
        bindings = self.document["spec"].get("semantic_bindings", {})
        entry = bindings.get(token)
        if entry is None:
            raise KeyError(f"No semantic binding for {token}")

        if namespace is None:
            return entry

        options = entry.get("bindings", []) if isinstance(entry, dict) else []
        for option in options:
            if option.get("namespace") == namespace:
                return option
        raise KeyError(f"No namespace {namespace!r} for semantic binding {token!r}")

    def resolve_runtime(self, env: Optional[dict[str, str]] = None) -> ArtifactRuntimeEnvelope:
        """Resolve identity/seat/interface/model with explicit fail-closed model semantics."""
        values = os.environ if env is None else env
        spec = self.document["spec"]
        identity_cfg = spec["identity"]
        model_cfg = spec["model_deliberation"]

        auto_env = model_cfg["interface_auto_env"]
        explicit_env = model_cfg["explicit_model_env"]
        auto_model = values.get(auto_env)
        explicit_model = values.get(explicit_env)

        if auto_model:
            model = auto_model
            auto_selected = True
            selection_reason = f"interface_auto:{auto_env}"
        elif explicit_model:
            model = explicit_model
            auto_selected = False
            selection_reason = f"explicit:{explicit_env}"
        else:
            raise ArtifactContractError(
                f"No concrete model resolved. Set {auto_env} from IDE Auto or {explicit_env} explicitly."
            )

        if model.strip().lower() == "auto":
            raise ArtifactContractError("Literal model 'auto' cannot be passed to an agent runtime.")

        identity_id = values.get(
            identity_cfg["identity_env"], identity_cfg.get("preferred_identity", "UNRESOLVED")
        )
        seat_id = values.get(identity_cfg["seat_env"], "UNRESOLVED")
        interface = values.get(model_cfg["interface_env"], "UNRESOLVED")
        provider = values.get(model_cfg["provider_env"], "UNRESOLVED")

        return ArtifactRuntimeEnvelope(
            artifact_id=self.artifact_id,
            identity_id=identity_id,
            seat_id=seat_id,
            authority_scope=str(identity_cfg.get("authority_rule", "task_scoped")),
            interface=interface,
            provider=provider,
            model=model,
            model_version=values.get("KPGS_MODEL_VERSION", "UNRESOLVED"),
            auto_selected=auto_selected,
            selection_reason=selection_reason,
        )


def _require_dict(document: dict[str, Any], key: str) -> dict[str, Any]:
    value = document.get(key)
    if not isinstance(value, dict):
        raise ArtifactContractError(f"{key} must be an object")
    return value


def validate_artifact_document(document: dict[str, Any]) -> None:
    """Validate the minimum contract without requiring the jsonschema package."""
    if document.get("apiVersion") != API_VERSION:
        raise ArtifactContractError(f"apiVersion must equal {API_VERSION}")
    if document.get("kind") != KIND:
        raise ArtifactContractError(f"kind must equal {KIND}")

    metadata = _require_dict(document, "metadata")
    spec = _require_dict(document, "spec")

    for field in ("id", "name", "group", "version", "status"):
        if not metadata.get(field):
            raise ArtifactContractError(f"metadata.{field} is required")

    for field in (
        "purpose",
        "task_mode",
        "invocation",
        "identity",
        "model_deliberation",
        "workflow",
        "evidence",
        "ledger",
    ):
        if field not in spec:
            raise ArtifactContractError(f"spec.{field} is required")

    identity = _require_dict(spec, "identity")
    model = _require_dict(spec, "model_deliberation")
    for field in ("identity_env", "seat_env"):
        if not identity.get(field):
            raise ArtifactContractError(f"spec.identity.{field} is required")
    for field in (
        "interface_auto_env",
        "explicit_model_env",
        "interface_env",
        "provider_env",
    ):
        if not model.get(field):
            raise ArtifactContractError(f"spec.model_deliberation.{field} is required")

    workflow = spec.get("workflow")
    if not isinstance(workflow, list) or not workflow:
        raise ArtifactContractError("spec.workflow must contain at least one step")


def load_artifact(path: Path | str) -> CallableArtifact:
    artifact_path = Path(path)
    with artifact_path.open("r", encoding="utf-8") as handle:
        document = yaml.safe_load(handle)
    if not isinstance(document, dict):
        raise ArtifactContractError("artifact document must be a mapping")
    validate_artifact_document(document)
    return CallableArtifact(path=artifact_path, document=document)


def discover_artifacts(repo_root: Path | str) -> list[CallableArtifact]:
    """Discover all implemented artifact.yml packages beneath the canonical artifact root."""
    root = Path(repo_root) / "governance" / "kpgs-artifacts"
    if not root.exists():
        return []
    return [load_artifact(path) for path in sorted(root.glob("**/artifact.yml"))]


def resolve_artifact(
    artifacts: Iterable[CallableArtifact],
    query: str,
) -> CallableArtifact:
    """Resolve an artifact by exact id or invocation alias."""
    normalized = query.strip().lower()
    matches: list[CallableArtifact] = []

    for artifact in artifacts:
        identifiers = {artifact.artifact_id.lower(), *(alias.lower() for alias in artifact.aliases)}
        if normalized in identifiers:
            matches.append(artifact)

    if not matches:
        raise KeyError(f"No callable artifact matches {query!r}")
    if len(matches) > 1:
        raise ArtifactContractError(
            f"Ambiguous artifact query {query!r}: {[item.artifact_id for item in matches]}"
        )
    return matches[0]


__all__ = [
    "API_VERSION",
    "KIND",
    "ArtifactContractError",
    "ArtifactRuntimeEnvelope",
    "CallableArtifact",
    "validate_artifact_document",
    "load_artifact",
    "discover_artifacts",
    "resolve_artifact",
]
