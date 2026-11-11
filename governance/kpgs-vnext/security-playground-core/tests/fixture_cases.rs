use kpgs_security_playground_core::{Component, Finding, Verdict, evaluate_json};

#[test]
fn fixed_node_candidate_is_never_estate_verification() {
    let result = evaluate_json(include_bytes!("fixtures/node-fixed.json"));
    assert_eq!(result.verdict, Verdict::DrillPass);
    assert_eq!(result.finding, Finding::FixedVersionCandidate);
    assert_eq!(result.component, Some(Component::Node));
    assert!(!result.runtime_verified);
    assert!(!result.production_authority);
}

#[test]
fn affected_node_and_prerequisite_match_is_blocked_in_fixture() {
    let result = evaluate_json(include_bytes!("fixtures/node-affected-prerequisite.json"));
    assert_eq!(result.verdict, Verdict::Block);
    assert_eq!(result.finding, Finding::AffectedVersionPrerequisiteMatched);
    assert!(!result.runtime_verified);
}

#[test]
fn missing_runtime_evidence_holds_even_for_production_label() {
    let result = evaluate_json(include_bytes!("fixtures/node-missing-runtime.json"));
    assert_eq!(result.verdict, Verdict::Hold);
    assert_eq!(result.finding, Finding::MissingRuntimeEvidence);
    assert!(!result.runtime_verified);
}

#[test]
fn stale_deployment_sha_holds() {
    let result = evaluate_json(include_bytes!("fixtures/node-stale-deployment-sha.json"));
    assert_eq!(result.verdict, Verdict::Hold);
    assert_eq!(result.finding, Finding::StaleDeploymentSource);
}

#[test]
fn conflicting_provider_receipt_holds() {
    let result = evaluate_json(include_bytes!("fixtures/node-conflicting-receipt.json"));
    assert_eq!(result.verdict, Verdict::Hold);
    assert_eq!(result.finding, Finding::ConflictingRuntimeEvidence);
}
