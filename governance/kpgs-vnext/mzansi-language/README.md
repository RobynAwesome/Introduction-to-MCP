# Mzansi Language Contracts — Phase 7

Status: **PR1 contract slice merged** (`b994272`); **PR2 Data Engine foundation** under review for `RobynAwesome/Introduction-to-MCP#103`.

This directory defines the first governed boundary for KPGS sociolinguistic inference. It does **not** claim a trained Sepedi model, production TTS quality, or native-speaker validation.

## Contracts

| Contract | Purpose |
| --- | --- |
| `evidence-class.schema.json` | Prevents AI-generated/transformed data from silently becoming human truth. |
| `linguistic-record.schema.json` | Stores meaning-aligned language evidence, code-switch segments, declared context, consent/licensing, and validation state. |
| `inference-request.schema.json` | Captures the requested language/register/code-switch/MXIT/speech transformation and locality/cost constraints. |
| `validation-receipt.schema.json` | Records what happened, measurable confidence, human validation, route/fallback, flags, and POC/FOC status. |

All schemas use JSON Schema Draft 2020-12 and follow the strict KPGS vNext pattern (`additionalProperties: false`, versioned `schema` constants).

## Invariants

1. **Meaning preservation is mandatory.** `meaning_preservation_required` is locked to `true`.
2. **Street language is not random slang injection.** Register, code-switching, MXIT compression, and speech are explicit dimensions.
3. **User context is explicit.** `user_contract.context_source` is locked to `explicit_user_input`; region/register preferences must not be guessed from stereotypes.
4. **Evidence provenance is mandatory.** Every linguistic record carries one canonical evidence class.
5. **Synthetic evidence never self-promotes.** `AI_GENERATED` and `AI_TRANSFORMED` remain distinguishable from `HUMAN_RECORDED` and `HUMAN_VALIDATED`.
6. **Consent/licensing are data-plane fields, not policy prose.** Speaker consent and licensing are required record properties.
7. **Cloud/local routing is visible.** The validation receipt records the inference location, providers, and whether fallback occurred.
8. **HOLD is valid.** A request may produce `hold` when evidence is insufficient rather than hallucinating cultural certainty.
9. **POC is receipted.** `POC_VALIDATED` is a receipt outcome, never a branding claim.

## First Sepedi vertical slice

```text
Formal Sepedi text
  -> meaning-preserving register transform
  -> conversational / street Sepedi
  -> optional controlled Sepedi-English code-switch
  -> optional MXIT compression
  -> speech synthesis
  -> validation receipt
```

The first runtime slice should remain limited to Sepedi (`nso`) until receipts support expansion.

## Example request

```json
{
  "schema": "kpgs.mzansi.inference-request.v1",
  "request_id": "req-000001",
  "input": {
    "text": "REPLACE_WITH_VALIDATED_SEPEDI_SOURCE_TEXT",
    "language_tag": "nso",
    "register": "formal"
  },
  "target": {
    "language_tag": "nso",
    "register": "street",
    "meaning_preservation_required": true,
    "code_switch_ratio": 0.25,
    "mxit_mode": "prefer",
    "speech": {
      "required": true,
      "voice_id": null,
      "high_fidelity": false
    }
  },
  "user_contract": {
    "context_source": "explicit_user_input",
    "preferred_language_tag": "nso",
    "street_formal_ratio": 0.75,
    "code_switch_tolerance": "medium",
    "region": null,
    "accessibility_notes": null
  },
  "execution": {
    "locality": "prefer_local",
    "max_cost_zar": 0,
    "allow_teacher_review": true,
    "allow_human_review": true
  },
  "created_at": "2026-08-24T02:10:00+02:00"
}
```

The placeholder source text is deliberate: this contracts PR must not invent Sepedi examples and then accidentally canonize unvalidated linguistic content.

## PR2 — Data Engine foundation

Admitted scope (owner comment on #103, 2026-08-24, restated 2026-09-07): *record persistence + provenance/consent/validation state and fixtures*. Not in scope: multi-language expansion, production TTS, any dataset, speech, model, or runtime claim.

| File | Role |
| --- | --- |
| `data_engine.py` | Standard-library-only runtime: schema-driven record validation, hash-linked append-only JSONL ledger, rule-table lifecycle transitions, admissible-set computation. |
| `fixtures/linguistic-records.synthetic.json` | Six placeholder records (`synthetic: true`, `FIXTURE_PLACEHOLDER_*` text, `fixture://` provenance) covering every evidence class. **Non-canonical. Contains no Sepedi.** |
| `fixtures/linguistic-records.invalid.json` | Nine records that must be refused, each with the error substring the validator must report. |
| `validate.py` | Gate script. Prints `KPGS-MZANSI-DATA-ENGINE PASS` or `FAIL` and exits non-zero on failure. |
| `../../../tests/test_mzansi_data_engine.py` | Unit tests for admission, transitions, consent, admissibility, persistence and tamper detection. |

### What the engine does

- **Validates** every record against `linguistic-record.schema.json` with a small Draft 2020-12 subset evaluator that reads the schema file itself. An unsupported keyword in the schema is a load-time error, so the evaluator cannot silently skip a constraint.
- **Persists** one entry per governed event to a JSONL ledger. Each entry carries `prev_hash` and `entry_hash` (`sha256(prev_hash + canonical_json(entry))`), so the file is tamper-evident; reload re-verifies the chain and refuses a broken one.
- **Replays** idempotently: re-admitting an identical record appends nothing; re-admitting a changed record with the same `record_id` appends a `record_conflict` entry and leaves the head untouched.
- **Computes admissibility** from data-plane fields only: class `HUMAN_VALIDATED`, status `validated`, `speaker_consent: true`, non-null `license`, and `synthetic: false` unless the caller explicitly asks for synthetic records.

### Lifecycle rule tables

Validation status:

| From | Allowed to | Gate |
| --- | --- | --- |
| `pending` | `validated`, `rejected`, `disputed` | `validated` needs ≥1 `validator_id` and `speaker_consent: true`; `rejected`/`disputed` need `notes` |
| `disputed` | `validated`, `rejected` | same gates |
| `validated` | `disputed` | `notes` required |
| `rejected` | — | terminal |

Evidence class (no edge leads back into `AI_*` or `UNVERIFIED`):

| From | To | Gate |
| --- | --- | --- |
| `UNVERIFIED` | `HUMAN_RECORDED` | `provenance_uri` present and `speaker_consent: true` |
| `HUMAN_RECORDED`, `AI_GENERATED`, `AI_TRANSFORMED` | `HUMAN_VALIDATED` | status already `validated`, ≥1 validator, consent `true` |
| any non-terminal class | `REJECTED` | `reason` required; status becomes `rejected` |

Consent withdrawal is one-way (`true → false`); a `validated` record becomes `disputed` on withdrawal. The `synthetic` flag never changes across any transition, so a synthetic record that reaches `HUMAN_VALIDATED` remains excluded from the default admissible set.

### Running the gate

```bash
python governance/kpgs-vnext/mzansi-language/validate.py
python -m unittest discover -s tests -p 'test_mzansi_data_engine.py' -v
```

Both run in `.github/workflows/kpgs-vnext-phase0-gate.yml`.

### What PR2 does not claim

- No linguistic data: fixtures are placeholders and are marked `non_canonical`.
- No model, TTS, translation, routing, or native-speaker validation.
- No claim that the promotion gate below is met. The engine is the place where the gate's evidence can be recorded; it does not satisfy the gate.

## Promotion gate

Before the Data Engine can claim POC on real evidence:

- collect meaning-aligned examples with provenance;
- record speaker consent/licensing;
- identify which records are human vs synthetic;
- obtain native-speaker validation for candidate transformations;
- define acceptance thresholds for meaning preservation, naturalness, pronunciation, and code-switch appropriateness;
- preserve failures/disagreements instead of deleting them from the evidence trail.

Canonical truth lock: `RobynAwesome/Introduction-to-MCP#103`.
