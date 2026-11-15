import assert from 'node:assert/strict';
import { isSwarmConsoleStatus } from '../src/consoleStatusCopy.mjs';

const cassy = {
  id: 'cassy', display_name: 'Cassy', role: 'student_primary', lead_student: 'cassy',
  teacher: 'cassey', brain: 'kc', mission: '', wit_band: '', console_role: '',
  drill_promoted_local: null, drill_is_not_graduation: true, steward_commands: [],
};
const status = {
  schema: 'kc_swarm_console_status_v1',
  persona_route: 'Cassy → Cassey · KC',
  context_host: 'https://context.example.test',
  proof_bar_pass: false,
  proof_gaps: ['Backend returned a real proof gap'],
  git: {
    branch: 'master', head_sha: 'abc', upstream: null, ahead: 0, behind: 0,
    origin_fetch_url: '', warnings: [],
  },
  checks: { jsonl_validate_ok: true, proof_check_ok: false, guard_all_ok: false },
  doctrine: {
    verified_production: 0, production_bar_met: false, roadmap_gate_met: false,
    swarm_ack_met: false, public_graduation_bar: 10,
  },
  ci: {
    workflow: 'test', actions_url: 'https://github.com/example/repo/actions',
    compare_url: 'https://github.com/example/repo/compare/master', guard_command: 'guard',
  },
  cli: [],
};

assert.equal(isSwarmConsoleStatus(status), true);
assert.equal(isSwarmConsoleStatus({ ...status, cassy, composer_hint: 'A bounded turn' }), true);
for (const malformed of [
  null, [], {}, '<html>wrong app</html>',
  { ...status, schema: 'kc_swarm_console_status_v2' },
  { ...status, proof_bar_pass: 'true' },
  { ...status, checks: null },
  { ...status, proof_gaps: [{}] },
  { ...status, doctrine: { ...status.doctrine, verified_production: '10' } },
  { ...status, git: { ...status.git, warnings: {} } },
  { ...status, ci: { ...status.ci, actions_url: null } },
  { ...status, cassy: { ...cassy, steward_commands: 'not a list' } },
]) {
  assert.equal(isSwarmConsoleStatus(malformed), false);
}

console.log('console status contract tests passed');
