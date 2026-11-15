use std::fs;
use std::process::Command;
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::Value;

fn fixture_path(name: &str) -> std::path::PathBuf {
    std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("tests")
        .join("fixtures")
        .join(name)
}

fn run_fixture(name: &str) -> (i32, Value) {
    let output = Command::new(env!("CARGO_BIN_EXE_spp-core"))
        .args(["--input", fixture_path(name).to_str().unwrap()])
        .output()
        .unwrap();
    let code = output.status.code().unwrap();
    let result: Value = serde_json::from_slice(&output.stdout).unwrap();
    (code, result)
}

#[test]
fn cli_exit_codes_and_json_outputs_are_bounded() {
    let (fixed_code, fixed) = run_fixture("node-fixed.json");
    assert_eq!(fixed_code, 0);
    assert_eq!(fixed["verdict"], "DRILL_PASS");
    assert_eq!(fixed["runtime_verified"], false);
    assert_eq!(fixed["production_authority"], false);

    let (missing_code, missing) = run_fixture("node-missing-runtime.json");
    assert_eq!(missing_code, 2);
    assert_eq!(missing["finding"], "MISSING_RUNTIME_EVIDENCE");
    assert_eq!(missing["runtime_verified"], false);
}

#[test]
fn cli_rejects_malformed_input_with_structured_result() {
    let nonce = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let path = std::env::temp_dir().join(format!("spp-core-invalid-{nonce}.json"));
    fs::write(&path, b"{invalid json").unwrap();

    let output = Command::new(env!("CARGO_BIN_EXE_spp-core"))
        .args(["--input", path.to_str().unwrap()])
        .output()
        .unwrap();
    let _ = fs::remove_file(path);
    assert_eq!(output.status.code(), Some(4));
    let result: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(result["verdict"], "INVALID_INPUT");
    assert_eq!(result["runtime_verified"], false);
    assert!(output.stderr.is_empty());
}

#[test]
fn cli_help_has_no_evaluation_side_effect() {
    let output = Command::new(env!("CARGO_BIN_EXE_spp-core"))
        .arg("--help")
        .output()
        .unwrap();
    assert!(output.status.success());
    assert!(String::from_utf8_lossy(&output.stdout).contains("Fixture-only"));
}
