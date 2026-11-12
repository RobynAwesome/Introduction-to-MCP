//! Shadow evaluator for the existing Security Playground inventory claim.

use std::collections::HashSet;
use std::fmt;

use serde::de::{self, MapAccess, SeqAccess, Visitor};
use serde::{Deserialize, Deserializer, Serialize};
use serde_json::{Map, Value};

use crate::{MAX_INPUT_BYTES, Mode, Verdict, is_fixture_ref, is_hex};

const SCHEMA: &str = "gsmb_security_playground_inventory_gate_v1";
const MAX_ASSETS: usize = 256;
const ISOLATION_CONTROLS: [&str; 5] = [
    "dedicated_isolation_domain",
    "deny_production_network",
    "production_credentials_absent",
    "production_state_readonly",
    "ephemeral_storage",
];

#[derive(Debug, Serialize)]
pub struct InventoryEvaluation {
    schema: &'static str,
    mode: Option<Mode>,
    pub verdict: Verdict,
    reasons: Vec<String>,
    runtime_verified: bool,
    production_authority: bool,
}

impl InventoryEvaluation {
    fn new(mode: Option<Mode>, verdict: Verdict, reasons: Vec<String>) -> Self {
        Self {
            schema: SCHEMA,
            mode,
            verdict,
            reasons,
            runtime_verified: false,
            production_authority: false,
        }
    }

    pub fn invalid_input(reason: &str) -> Self {
        Self::new(None, Verdict::InvalidInput, vec![reason.to_owned()])
    }
}

/// Classify an inventory claim without reading any referenced evidence.
pub fn evaluate_json(input: &[u8]) -> InventoryEvaluation {
    if input.len() > MAX_INPUT_BYTES {
        return InventoryEvaluation::invalid_input("input exceeds the 64 KiB fixture limit");
    }
    let Ok(UniqueJson(value)) = serde_json::from_slice(input) else {
        return InventoryEvaluation::invalid_input("input is malformed or contains duplicate keys");
    };
    let Some(record) = value.as_object() else {
        return InventoryEvaluation::new(
            None,
            Verdict::Block,
            vec!["input must be a JSON object".to_owned()],
        );
    };
    if record
        .get("assets")
        .and_then(Value::as_array)
        .is_some_and(|assets| assets.len() > MAX_ASSETS)
    {
        return InventoryEvaluation::invalid_input(
            "asset inventory exceeds the 256-record fixture limit",
        );
    }

    let mut blocked = Vec::new();
    let mut held = Vec::new();
    let mode = match record.get("mode").and_then(Value::as_str) {
        Some("fixture") => Some(Mode::Fixture),
        Some("cloud") => Some(Mode::Cloud),
        Some("local") => Some(Mode::Local),
        _ => None,
    };
    let fixture = mode == Some(Mode::Fixture);
    if record.get("schema").and_then(Value::as_str) != Some(SCHEMA) {
        held.push("schema is missing or unsupported".to_owned());
    }
    if mode.is_none() {
        held.push("mode must be fixture, cloud or local".to_owned());
    }
    if !record
        .get("source_revision")
        .and_then(Value::as_str)
        .is_some_and(|revision| is_hex(revision, 40))
    {
        held.push("source_revision must be a 40-character Git SHA".to_owned());
    }
    check_isolation(record.get("isolation"), fixture, &mut blocked, &mut held);
    match record
        .get("protected_state_mutations")
        .and_then(Value::as_u64)
    {
        Some(0) => {}
        Some(_) => blocked.push("attempted protected-state mutation detected".to_owned()),
        None => held.push("protected_state_mutations must be a nonnegative integer".to_owned()),
    }
    check_assets(record.get("assets"), fixture, &mut blocked, &mut held);
    match record.get("receipt_refs").and_then(Value::as_array) {
        Some(refs)
            if !refs.is_empty() && refs.iter().all(|value| nonempty(Some(value)).is_some()) =>
        {
            if fixture && refs.iter().any(|value| !fixture_ref(Some(value))) {
                held.push("fixture receipt_refs must use named fixture:// references".to_owned());
            }
        }
        _ => held.push("receipt_refs must contain at least one nonempty reference".to_owned()),
    }

    if !blocked.is_empty() {
        blocked.extend(held);
        InventoryEvaluation::new(mode, Verdict::Block, blocked)
    } else if !held.is_empty() {
        InventoryEvaluation::new(mode, Verdict::Hold, held)
    } else if fixture {
        InventoryEvaluation::new(
            mode,
            Verdict::DrillPass,
            vec![
                "fixture admission assertions passed; no live isolation or runtime verified"
                    .to_owned(),
            ],
        )
    } else {
        InventoryEvaluation::new(
            mode,
            Verdict::Hold,
            vec![
                "real-environment claims require independent control-plane and runtime review"
                    .to_owned(),
            ],
        )
    }
}

fn check_isolation(
    value: Option<&Value>,
    fixture: bool,
    blocked: &mut Vec<String>,
    held: &mut Vec<String>,
) {
    let Some(isolation) = value.and_then(Value::as_object) else {
        held.push("isolation control assertions are missing".to_owned());
        return;
    };
    for control in ISOLATION_CONTROLS {
        match isolation.get(control).and_then(Value::as_bool) {
            Some(true) => {}
            Some(false) => blocked.push(format!("isolation control explicitly failed: {control}")),
            None => held.push(format!("isolation control unverified: {control}")),
        }
    }
    check_evidence_ref(isolation, "isolation", fixture, held);
}

fn check_assets(
    value: Option<&Value>,
    fixture: bool,
    blocked: &mut Vec<String>,
    held: &mut Vec<String>,
) {
    let Some(assets) = value
        .and_then(Value::as_array)
        .filter(|assets| !assets.is_empty())
    else {
        held.push("asset inventory is empty or missing".to_owned());
        return;
    };
    let mut has_php = false;
    let mut ids = HashSet::new();
    for (index, value) in assets.iter().enumerate() {
        let prefix = format!("asset[{index}]");
        let Some(asset) = value.as_object() else {
            held.push(format!("{prefix} is not an object"));
            continue;
        };
        match nonempty(asset.get("id")) {
            Some(id) if !ids.insert(id) => held.push(format!("{prefix} duplicate id")),
            Some(_) => {}
            None => held.push(format!("{prefix} missing id")),
        }
        match asset.get("kind").and_then(Value::as_str) {
            Some("php_runtime") => has_php = true,
            Some("dependency" | "service" | "container") => {}
            _ => held.push(format!("{prefix} kind unknown")),
        }
        match asset.get("status").and_then(Value::as_str) {
            Some("patched" | "not_present") => {}
            Some("vulnerable") => blocked.push(format!("{prefix} has vulnerable status")),
            Some("unknown") => held.push(format!("{prefix} status unknown")),
            _ => held.push(format!("{prefix} status invalid")),
        }
        check_evidence_ref(asset, &prefix, fixture, held);
    }
    if !has_php {
        held.push(
            "explicit PHP runtime inventory record required, including not_present".to_owned(),
        );
    }
}

fn check_evidence_ref(
    record: &Map<String, Value>,
    label: &str,
    fixture: bool,
    held: &mut Vec<String>,
) {
    match nonempty(record.get("evidence_ref")) {
        None => held.push(format!("{label} evidence_ref missing")),
        Some(value) if fixture && !is_fixture_ref(value) => {
            held.push(format!(
                "{label} evidence_ref must use a named fixture:// reference"
            ));
        }
        Some(_) => {}
    }
}

fn nonempty(value: Option<&Value>) -> Option<&str> {
    value
        .and_then(Value::as_str)
        .filter(|text| !text.trim().is_empty())
}

fn fixture_ref(value: Option<&Value>) -> bool {
    value.and_then(Value::as_str).is_some_and(is_fixture_ref)
}

// Value's normal map decoder accepts duplicate keys. A fixture must never
// turn a contradictory assertion into a pass by keeping only its last value.
struct UniqueJson(Value);

impl<'de> Deserialize<'de> for UniqueJson {
    fn deserialize<D: Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        deserializer.deserialize_any(UniqueJsonVisitor)
    }
}

struct UniqueJsonVisitor;

impl<'de> Visitor<'de> for UniqueJsonVisitor {
    type Value = UniqueJson;

    fn expecting(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        formatter.write_str("JSON without duplicate object keys")
    }

    fn visit_map<A: MapAccess<'de>>(self, mut entries: A) -> Result<Self::Value, A::Error> {
        let mut object = Map::new();
        while let Some((key, UniqueJson(value))) = entries.next_entry::<String, UniqueJson>()? {
            if object.insert(key, value).is_some() {
                return Err(de::Error::custom("duplicate object key"));
            }
        }
        Ok(UniqueJson(Value::Object(object)))
    }

    fn visit_seq<A: SeqAccess<'de>>(self, mut entries: A) -> Result<Self::Value, A::Error> {
        let mut values = Vec::new();
        while let Some(UniqueJson(value)) = entries.next_element()? {
            values.push(value);
        }
        Ok(UniqueJson(Value::Array(values)))
    }

    fn visit_bool<E: de::Error>(self, value: bool) -> Result<Self::Value, E> {
        Ok(UniqueJson(value.into()))
    }

    fn visit_i64<E: de::Error>(self, value: i64) -> Result<Self::Value, E> {
        Ok(UniqueJson(value.into()))
    }

    fn visit_u64<E: de::Error>(self, value: u64) -> Result<Self::Value, E> {
        Ok(UniqueJson(value.into()))
    }

    fn visit_f64<E: de::Error>(self, value: f64) -> Result<Self::Value, E> {
        Ok(UniqueJson(value.into()))
    }

    fn visit_str<E: de::Error>(self, value: &str) -> Result<Self::Value, E> {
        Ok(UniqueJson(value.into()))
    }

    fn visit_unit<E: de::Error>(self) -> Result<Self::Value, E> {
        Ok(UniqueJson(Value::Null))
    }
}
