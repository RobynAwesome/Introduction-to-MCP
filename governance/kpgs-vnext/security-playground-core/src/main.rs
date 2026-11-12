use std::env;
use std::ffi::OsString;
use std::fs::File;
use std::io::{Read, Write, stdin, stdout};
use std::process::ExitCode;

use kpgs_security_playground_core::{
    Evaluation, Finding, MAX_INPUT_BYTES, RESULT_SCHEMA, Verdict, evaluate_json, inventory,
};
use serde::Serialize;

fn main() -> ExitCode {
    let args: Vec<_> = env::args_os().skip(1).collect();
    let (inventory_mode, args) = match args.as_slice() {
        [flag, rest @ ..] if flag == "--inventory" => (true, rest),
        args => (false, args),
    };
    if args.len() == 1 && args[0] == "--help" {
        println!(
            "spp-core [--inventory] (--input <fixture.json> | --stdin)\nFixture-only; never authenticates runtime evidence."
        );
        return ExitCode::SUCCESS;
    }

    let input = read_input(args);
    if inventory_mode {
        let result = match input {
            Ok(bytes) => inventory::evaluate_json(&bytes),
            Err(reason) => inventory::InventoryEvaluation::invalid_input(reason),
        };
        write_result(&result, result.verdict)
    } else {
        let result = match input {
            Ok(bytes) => evaluate_json(&bytes),
            Err(reason) => invalid(reason),
        };
        write_result(&result, result.verdict)
    }
}

fn write_result(result: &impl Serialize, verdict: Verdict) -> ExitCode {
    let mut output = stdout().lock();
    if serde_json::to_writer(&mut output, result).is_err() || writeln!(output).is_err() {
        return ExitCode::from(4);
    }
    match verdict {
        Verdict::DrillPass => ExitCode::SUCCESS,
        Verdict::Hold => ExitCode::from(2),
        Verdict::Block => ExitCode::from(3),
        Verdict::InvalidInput => ExitCode::from(4),
    }
}

fn read_input(args: &[OsString]) -> Result<Vec<u8>, &'static str> {
    let mut bytes = Vec::new();
    let read_result = match args {
        [flag, path] if flag == "--input" => File::open(path).and_then(|file| {
            file.take((MAX_INPUT_BYTES + 1) as u64)
                .read_to_end(&mut bytes)
        }),
        [flag] if flag == "--stdin" => stdin()
            .take((MAX_INPUT_BYTES + 1) as u64)
            .read_to_end(&mut bytes),
        _ => return Err("expected --input <path> or --stdin"),
    };
    read_result
        .map(|_| bytes)
        .map_err(|_| "input could not be read")
}

fn invalid(reason: &str) -> Evaluation {
    Evaluation {
        schema: RESULT_SCHEMA,
        case_id: None,
        component: None,
        environment: None,
        source_revision: None,
        advisory_id: None,
        target_source_sha: None,
        verdict: Verdict::InvalidInput,
        finding: Finding::InvalidInput,
        reason: reason.to_owned(),
        runtime_verified: false,
        production_authority: false,
    }
}
