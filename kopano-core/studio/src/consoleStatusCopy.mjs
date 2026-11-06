/**
 * Describe why Studio cannot show proof status without claiming that checks failed.
 * @param {string} apiBase
 * @param {number | undefined} responseStatus
 */
export function getApiUnavailableMessage(apiBase, responseStatus) {
  let localApi = false;
  try {
    const hostname = new URL(apiBase).hostname;
    localApi = hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1';
  } catch {
    // An invalid configured URL is still a configured endpoint problem.
  }

  const source = localApi ? 'Local API' : 'Configured API';
  if (responseStatus !== undefined) {
    const response = `${source} returned HTTP ${responseStatus}; status could not be loaded.`;
    return localApi
      ? `${response} Confirm the API is running, then retry.`
      : `${response} Check the configured endpoint and network, then retry.`;
  }

  return localApi
    ? `${source} is unavailable. Start it with “python main.py serve api” from the repository root, then retry.`
    : `${source} is unavailable. Check the configured endpoint and network, then retry.`;
}

const isObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);
const isString = (value) => typeof value === 'string';
const isBoolean = (value) => typeof value === 'boolean';
const isStringArray = (value) => Array.isArray(value) && value.every(isString);

/**
 * Confirm the version and the fields Studio renders before using a status response.
 * @param {unknown} value
 * @returns {boolean}
 */
export function isSwarmConsoleStatus(value) {
  if (!isObject(value) || value.schema !== 'kc_swarm_console_status_v1') return false;

  const { git, checks, doctrine, ci, cassy } = value;
  return isString(value.persona_route)
    && (value.composer_hint === undefined || isString(value.composer_hint))
    && isString(value.context_host)
    && isBoolean(value.proof_bar_pass)
    && isStringArray(value.proof_gaps)
    && isStringArray(value.cli)
    && isObject(git)
    && [git.branch, git.head_sha, git.origin_fetch_url].every(isString)
    && (git.upstream === null || isString(git.upstream))
    && [git.ahead, git.behind].every(Number.isInteger)
    && isStringArray(git.warnings)
    && isObject(checks)
    && [checks.jsonl_validate_ok, checks.proof_check_ok, checks.guard_all_ok].every(isBoolean)
    && isObject(doctrine)
    && [doctrine.verified_production, doctrine.public_graduation_bar].every(Number.isInteger)
    && [doctrine.production_bar_met, doctrine.roadmap_gate_met, doctrine.swarm_ack_met].every(isBoolean)
    && isObject(ci)
    && [ci.workflow, ci.actions_url, ci.compare_url, ci.guard_command].every(isString)
    && (cassy === undefined || (
      isObject(cassy)
      && [cassy.id, cassy.display_name, cassy.role, cassy.lead_student, cassy.teacher,
        cassy.brain, cassy.mission, cassy.wit_band, cassy.console_role].every(isString)
      && (cassy.drill_promoted_local === null || Number.isInteger(cassy.drill_promoted_local))
      && isBoolean(cassy.drill_is_not_graduation)
      && isStringArray(cassy.steward_commands)
    ));
}
