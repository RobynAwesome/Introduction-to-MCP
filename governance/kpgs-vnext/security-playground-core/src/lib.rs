//! Fixture-only Security Playground evaluator.
//!
//! This crate classifies synthetic evidence. It does not collect evidence,
//! authenticate receipts, enforce runtime isolation, or grant execution or
//! production authority. A passing fixture is never a runtime attestation.

use serde::{Deserialize, Serialize};

pub mod inventory;

pub const REQUEST_SCHEMA: &str = "kpgs.spp.core.fixture.v1";
pub const RESULT_SCHEMA: &str = "kpgs.spp.core.result.v1";
pub const MAX_INPUT_BYTES: usize = 64 * 1024;

#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Mode {
    Fixture,
    Cloud,
    Local,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
pub enum Component {
    #[serde(rename = "node")]
    Node,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum Environment {
    Production,
    Preview,
    Local,
    BuildCi,
    Tooling,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum EvidenceState {
    Observed,
    Missing,
    Stale,
    Conflicting,
}

#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum PrerequisiteState {
    Satisfied,
    NotSatisfied,
    Unknown,
    NotRequired,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct AdvisoryRange {
    pub id: String,
    pub affected_from: String,
    pub fixed_at: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct RuntimeEvidence {
    pub state: EvidenceState,
    pub exact_version: Option<String>,
    pub deployment_identity: Option<String>,
    pub deployment_source_sha: Option<String>,
    pub artifact_digest_sha256: Option<String>,
    pub observed_at_utc: Option<String>,
    pub evidence_ref: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct PrerequisiteEvidence {
    pub name: String,
    pub state: PrerequisiteState,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct EvaluationRequest {
    pub schema: String,
    pub mode: Mode,
    pub source_revision: String,
    pub case_id: String,
    pub component: Component,
    pub environment: Environment,
    pub target_source_sha: String,
    pub advisory: AdvisoryRange,
    pub runtime: RuntimeEvidence,
    pub prerequisite: PrerequisiteEvidence,
}

#[derive(Debug, Clone, Copy, Serialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Verdict {
    DrillPass,
    Hold,
    Block,
    InvalidInput,
}

#[derive(Debug, Clone, Copy, Serialize, PartialEq, Eq)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Finding {
    FixedVersionCandidate,
    OutsideDeclaredAffectedRange,
    AffectedVersionPrerequisiteMatched,
    AffectedVersionPrerequisiteNotMet,
    MissingRuntimeEvidence,
    StaleRuntimeEvidence,
    ConflictingRuntimeEvidence,
    NonFixtureEvidence,
    IncompleteRuntimeIdentity,
    StaleDeploymentSource,
    UnknownPrerequisite,
    UnsupportedSchema,
    InvalidEvidence,
    InvalidInput,
}

#[derive(Debug, Clone, Serialize, PartialEq, Eq)]
pub struct Evaluation {
    pub schema: &'static str,
    pub case_id: Option<String>,
    pub component: Option<Component>,
    pub environment: Option<Environment>,
    pub source_revision: Option<String>,
    pub advisory_id: Option<String>,
    pub target_source_sha: Option<String>,
    pub verdict: Verdict,
    pub finding: Finding,
    pub reason: String,
    /// Always false: this crate never authenticates runtime evidence.
    pub runtime_verified: bool,
    /// Always false: this crate has no authority to promote or execute.
    pub production_authority: bool,
}

impl Evaluation {
    fn bare(verdict: Verdict, finding: Finding, reason: impl Into<String>) -> Self {
        Self {
            schema: RESULT_SCHEMA,
            case_id: None,
            component: None,
            environment: None,
            source_revision: None,
            advisory_id: None,
            target_source_sha: None,
            verdict,
            finding,
            reason: reason.into(),
            runtime_verified: false,
            production_authority: false,
        }
    }

    fn for_request(
        request: &EvaluationRequest,
        verdict: Verdict,
        finding: Finding,
        reason: impl Into<String>,
    ) -> Self {
        Self {
            schema: RESULT_SCHEMA,
            case_id: Some(request.case_id.clone()),
            component: Some(request.component),
            environment: Some(request.environment),
            source_revision: Some(request.source_revision.clone()),
            advisory_id: Some(request.advisory.id.clone()),
            target_source_sha: Some(request.target_source_sha.clone()),
            verdict,
            finding,
            reason: reason.into(),
            runtime_verified: false,
            production_authority: false,
        }
    }
}

/// Parse one bounded request and evaluate it without performing external I/O.
pub fn evaluate_json(input: &[u8]) -> Evaluation {
    if input.len() > MAX_INPUT_BYTES {
        return Evaluation::bare(
            Verdict::InvalidInput,
            Finding::InvalidInput,
            "input exceeds the 64 KiB fixture limit",
        );
    }

    match serde_json::from_slice::<EvaluationRequest>(input) {
        Ok(request) => evaluate(request),
        Err(_) => Evaluation::bare(
            Verdict::InvalidInput,
            Finding::InvalidInput,
            "request is malformed or contains unsupported fields",
        ),
    }
}

/// Classify a synthetic fixture. Cloud and Local records remain HOLD because
/// there is no independent runtime verifier in this crate.
pub fn evaluate(request: EvaluationRequest) -> Evaluation {
    if request.schema != REQUEST_SCHEMA {
        return Evaluation::for_request(
            &request,
            Verdict::Hold,
            Finding::UnsupportedSchema,
            "unsupported request schema; no evidence was promoted",
        );
    }
    if request.mode != Mode::Fixture {
        return Evaluation::for_request(
            &request,
            Verdict::Hold,
            Finding::NonFixtureEvidence,
            "Cloud and Local evidence require an independent verifier; this crate is fixture-only",
        );
    }
    if !is_hex(&request.source_revision, 40)
        || !is_hex(&request.target_source_sha, 40)
        || request.case_id.trim().is_empty()
        || request.advisory.id.trim().is_empty()
        || request.prerequisite.name.trim().is_empty()
    {
        return Evaluation::for_request(
            &request,
            Verdict::InvalidInput,
            Finding::InvalidInput,
            "source identifiers, case id, advisory id, and prerequisite name are required",
        );
    }
    if !is_fixture_ref(&request.runtime.evidence_ref) {
        return Evaluation::for_request(
            &request,
            Verdict::Hold,
            Finding::NonFixtureEvidence,
            "only fixture:// references are accepted; real receipts are not authenticated here",
        );
    }

    match request.runtime.state {
        EvidenceState::Missing => {
            return Evaluation::for_request(
                &request,
                Verdict::Hold,
                Finding::MissingRuntimeEvidence,
                "exact runtime evidence is missing",
            );
        }
        EvidenceState::Stale => {
            return Evaluation::for_request(
                &request,
                Verdict::Hold,
                Finding::StaleRuntimeEvidence,
                "runtime evidence is marked stale",
            );
        }
        EvidenceState::Conflicting => {
            return Evaluation::for_request(
                &request,
                Verdict::Hold,
                Finding::ConflictingRuntimeEvidence,
                "runtime evidence conflicts; no side is selected",
            );
        }
        EvidenceState::Observed => {}
    }

    let (
        Some(version_text),
        Some(deployment_identity),
        Some(deployment_sha),
        Some(digest),
        Some(observed_at),
    ) = (
        request.runtime.exact_version.as_deref(),
        request.runtime.deployment_identity.as_deref(),
        request.runtime.deployment_source_sha.as_deref(),
        request.runtime.artifact_digest_sha256.as_deref(),
        request.runtime.observed_at_utc.as_deref(),
    )
    else {
        return Evaluation::for_request(
            &request,
            Verdict::Hold,
            Finding::IncompleteRuntimeIdentity,
            "version, deployment identity, source SHA, artifact digest, or observation time is missing",
        );
    };

    if deployment_identity.trim().is_empty()
        || !is_hex(deployment_sha, 40)
        || !is_hex(digest, 64)
        || !is_utc_timestamp(observed_at)
    {
        return Evaluation::for_request(
            &request,
            Verdict::Hold,
            Finding::InvalidEvidence,
            "runtime identity must include a Git SHA, SHA-256 digest, and UTC observation time",
        );
    }
    if deployment_sha != request.target_source_sha {
        return Evaluation::for_request(
            &request,
            Verdict::Hold,
            Finding::StaleDeploymentSource,
            "observed deployment source does not match the requested source SHA",
        );
    }

    let Some(version) = Version::parse(version_text) else {
        return Evaluation::for_request(
            &request,
            Verdict::Hold,
            Finding::InvalidEvidence,
            "runtime version must be an exact three-part numeric version",
        );
    };
    let (Some(affected_from), Some(fixed_at)) = (
        Version::parse(&request.advisory.affected_from),
        Version::parse(&request.advisory.fixed_at),
    ) else {
        return Evaluation::for_request(
            &request,
            Verdict::InvalidInput,
            Finding::InvalidInput,
            "advisory range must use exact three-part numeric versions",
        );
    };
    if fixed_at <= affected_from {
        return Evaluation::for_request(
            &request,
            Verdict::InvalidInput,
            Finding::InvalidInput,
            "fixed_at must be greater than affected_from",
        );
    }

    if version < affected_from {
        return Evaluation::for_request(
            &request,
            Verdict::DrillPass,
            Finding::OutsideDeclaredAffectedRange,
            "synthetic version falls below the supplied affected range; this is not an estate safety claim",
        );
    }
    if version >= fixed_at {
        return Evaluation::for_request(
            &request,
            Verdict::DrillPass,
            Finding::FixedVersionCandidate,
            "synthetic version meets the supplied fixed-version boundary; estate fix verification is not performed",
        );
    }

    match request.prerequisite.state {
        PrerequisiteState::Satisfied | PrerequisiteState::NotRequired => Evaluation::for_request(
            &request,
            Verdict::Block,
            Finding::AffectedVersionPrerequisiteMatched,
            "synthetic affected version and prerequisite match; this is not proof of live exposure",
        ),
        PrerequisiteState::NotSatisfied => Evaluation::for_request(
            &request,
            Verdict::Hold,
            Finding::AffectedVersionPrerequisiteNotMet,
            "synthetic version is in the supplied affected range but the prerequisite is not met",
        ),
        PrerequisiteState::Unknown => Evaluation::for_request(
            &request,
            Verdict::Hold,
            Finding::UnknownPrerequisite,
            "prerequisite state is unknown",
        ),
    }
}

fn is_hex(value: &str, expected_len: usize) -> bool {
    value.len() == expected_len && value.bytes().all(|byte| byte.is_ascii_hexdigit())
}

fn is_fixture_ref(value: &str) -> bool {
    value
        .strip_prefix("fixture://")
        .is_some_and(|name| !name.trim().is_empty())
}

fn is_utc_timestamp(value: &str) -> bool {
    let bytes = value.as_bytes();
    if bytes.len() != 20
        || bytes[4] != b'-'
        || bytes[7] != b'-'
        || bytes[10] != b'T'
        || bytes[13] != b':'
        || bytes[16] != b':'
        || bytes[19] != b'Z'
    {
        return false;
    }
    for range in [0..4, 5..7, 8..10, 11..13, 14..16, 17..19] {
        if !bytes[range].iter().all(u8::is_ascii_digit) {
            return false;
        }
    }

    let year = value[0..4].parse::<u32>().ok();
    let month = value[5..7].parse::<u32>().ok();
    let day = value[8..10].parse::<u32>().ok();
    let hour = value[11..13].parse::<u32>().ok();
    let minute = value[14..16].parse::<u32>().ok();
    let second = value[17..19].parse::<u32>().ok();
    let (Some(year), Some(month), Some(day), Some(hour), Some(minute), Some(second)) =
        (year, month, day, hour, minute, second)
    else {
        return false;
    };
    let days_in_month = match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 if year % 400 == 0 || (year % 4 == 0 && year % 100 != 0) => 29,
        2 => 28,
        _ => return false,
    };
    year > 0 && day > 0 && day <= days_in_month && hour <= 23 && minute <= 59 && second <= 59
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
struct Version(u32, u32, u32);

impl Version {
    fn parse(value: &str) -> Option<Self> {
        let mut parts = value.split('.');
        let major = parse_part(parts.next()?)?;
        let minor = parse_part(parts.next()?)?;
        let patch = parse_part(parts.next()?)?;
        if parts.next().is_some() {
            return None;
        }
        Some(Self(major, minor, patch))
    }
}

fn parse_part(value: &str) -> Option<u32> {
    if value.is_empty()
        || (value.len() > 1 && value.starts_with('0'))
        || !value.bytes().all(|byte| byte.is_ascii_digit())
    {
        return None;
    }
    value.parse().ok()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn request(version: &str, prerequisite: PrerequisiteState) -> EvaluationRequest {
        serde_json::from_value(serde_json::json!({
            "schema": REQUEST_SCHEMA,
            "mode": "fixture",
            "source_revision": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "case_id": "synthetic-node-case",
            "component": "node",
            "environment": "preview",
            "target_source_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
            "advisory": {
                "id": "FIXTURE-NODE-ADVISORY-A",
                "affected_from": "20.0.0",
                "fixed_at": "20.10.0"
            },
            "runtime": {
                "state": "observed",
                "exact_version": version,
                "deployment_identity": "fixture://preview/deployment-1",
                "deployment_source_sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                "artifact_digest_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
                "observed_at_utc": "2026-11-05T12:00:00Z",
                "evidence_ref": "fixture://runtime/node"
            },
            "prerequisite": {
                "name": "synthetic-feature-precondition",
                "state": serde_json::to_value(prerequisite).unwrap()
            }
        })).unwrap()
    }

    #[test]
    fn node_fixed_boundary_is_only_a_fixture_candidate() {
        let result = evaluate(request("20.10.0", PrerequisiteState::Unknown));
        assert_eq!(result.verdict, Verdict::DrillPass);
        assert_eq!(result.finding, Finding::FixedVersionCandidate);
        assert_eq!(result.component, Some(Component::Node));
        assert!(!result.runtime_verified);
        assert!(!result.production_authority);
    }

    #[test]
    fn node_affected_version_with_prerequisite_match_blocks_fixture() {
        let result = evaluate(request("20.9.9", PrerequisiteState::Satisfied));
        assert_eq!(result.verdict, Verdict::Block);
        assert_eq!(result.finding, Finding::AffectedVersionPrerequisiteMatched);
        assert!(result.reason.contains("not proof of live exposure"));
        assert!(!result.runtime_verified);
    }

    #[test]
    fn affected_version_without_prerequisite_evidence_holds() {
        let result = evaluate(request("20.9.9", PrerequisiteState::Unknown));
        assert_eq!(result.verdict, Verdict::Hold);
        assert_eq!(result.finding, Finding::UnknownPrerequisite);
    }

    #[test]
    fn affected_version_with_unmet_prerequisite_stays_held() {
        let result = evaluate(request("20.9.9", PrerequisiteState::NotSatisfied));
        assert_eq!(result.verdict, Verdict::Hold);
        assert_eq!(result.finding, Finding::AffectedVersionPrerequisiteNotMet);
    }

    #[test]
    fn cloud_and_local_records_never_promote() {
        for mode in [Mode::Cloud, Mode::Local] {
            let mut sample = request("20.10.0", PrerequisiteState::Unknown);
            sample.mode = mode;
            let result = evaluate(sample);
            assert_eq!(result.verdict, Verdict::Hold);
            assert_eq!(result.finding, Finding::NonFixtureEvidence);
            assert!(!result.runtime_verified);
            assert!(!result.production_authority);
        }
    }

    #[test]
    fn unknown_and_conflicting_runtime_evidence_hold() {
        let mut missing = request("20.10.0", PrerequisiteState::Unknown);
        missing.runtime.state = EvidenceState::Missing;
        let missing_result = evaluate(missing);
        assert_eq!(missing_result.verdict, Verdict::Hold);
        assert_eq!(missing_result.finding, Finding::MissingRuntimeEvidence);

        let mut conflict = request("20.10.0", PrerequisiteState::Unknown);
        conflict.runtime.state = EvidenceState::Conflicting;
        let conflict_result = evaluate(conflict);
        assert_eq!(conflict_result.verdict, Verdict::Hold);
        assert_eq!(conflict_result.finding, Finding::ConflictingRuntimeEvidence);
    }

    #[test]
    fn stale_deployment_sha_holds() {
        let mut sample = request("20.10.0", PrerequisiteState::Unknown);
        sample.runtime.deployment_source_sha =
            Some("dddddddddddddddddddddddddddddddddddddddd".to_owned());
        let result = evaluate(sample);
        assert_eq!(result.verdict, Verdict::Hold);
        assert_eq!(result.finding, Finding::StaleDeploymentSource);
    }

    #[test]
    fn a_bare_fixture_prefix_does_not_admit_runtime_evidence() {
        let mut sample = request("20.10.0", PrerequisiteState::Unknown);
        sample.runtime.evidence_ref = "fixture://".to_owned();
        let result = evaluate(sample);
        assert_eq!(result.verdict, Verdict::Hold);
        assert_eq!(result.finding, Finding::NonFixtureEvidence);
    }

    #[test]
    fn unsupported_fields_and_semver_are_rejected_or_held() {
        let invalid_schema =
            evaluate_json(br#"{"schema":"kpgs.spp.core.fixture.v1","unknown":true}"#);
        assert_eq!(invalid_schema.verdict, Verdict::InvalidInput);

        let mut sample = request("20.10.0-rc.1", PrerequisiteState::Unknown);
        sample.runtime.exact_version = Some("20.10.0-rc.1".to_owned());
        let result = evaluate(sample);
        assert_eq!(result.verdict, Verdict::Hold);
        assert_eq!(result.finding, Finding::InvalidEvidence);
    }

    #[test]
    fn malformed_utc_observation_time_holds() {
        let mut sample = request("20.10.0", PrerequisiteState::Unknown);
        sample.runtime.observed_at_utc = Some("not-a-timestampZ".to_owned());
        let result = evaluate(sample);
        assert_eq!(result.verdict, Verdict::Hold);
        assert_eq!(result.finding, Finding::InvalidEvidence);
    }

    #[test]
    fn oversized_input_is_rejected_without_parsing() {
        let input = vec![b' '; MAX_INPUT_BYTES + 1];
        let result = evaluate_json(&input);
        assert_eq!(result.verdict, Verdict::InvalidInput);
        assert!(!result.runtime_verified);
    }
}
