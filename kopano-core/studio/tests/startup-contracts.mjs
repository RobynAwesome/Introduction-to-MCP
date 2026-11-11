import assert from 'node:assert/strict';
import {
  hasCoworkRoomDetail,
  isCoworkRoomDetailPayload,
  isCoworkRoomsPayload,
  isLabsAnalytics,
  isLabsOverview,
  isMicrosoftReadiness,
  isSessionList,
} from '../src/startupContracts.mjs';

// 1. /sessions contract
const validSessions = [
  { id: 1, topic: 'KC apprenticeship', created_at: '2026-11-07T00:00:00Z', round_count: 2, audit_events: 4 },
  { id: 2, topic: 'Minimal session', created_at: '2026-11-07T01:00:00Z' },
];
assert.equal(isSessionList(validSessions), true);
assert.equal(isSessionList([]), true);
for (const malformed of [
  null,
  {},
  [null],
  [{ id: '1', topic: 'T', created_at: '2026-11-07' }],
  [{ id: 1, topic: {}, created_at: '2026-11-07' }],
  [{ id: 1, topic: 'T', created_at: {} }],
  [{ id: 1, topic: 'T', created_at: '2026-11-07', round_count: {} }],
  [{ id: 1, topic: 'T', created_at: '2026-11-07', audit_events: '4' }],
]) {
  assert.equal(isSessionList(malformed), false);
}

// 2. /api/labs/overview contract
const validOverview = {
  metrics: { interfaces: 5, live_tools: 2 },
  installer_actions: [{ id: 'azure-demo-playbook', title: 'Azure Demo Day Bootstrap', provider: 'Azure' }],
  kopano_interfaces: [{ id: 'ide-surface', name: 'IDE Workspace', summary: 'Repo-aware coding surface.' }],
  tools: [{ id: 'gig-matcher', name: 'Gig Matcher', summary: 'Ranks nearby providers.' }],
};
assert.equal(isLabsOverview(validOverview), true);
for (const malformed of [
  null,
  {},
  { ...validOverview, metrics: null },
  { ...validOverview, metrics: { interfaces: {}, live_tools: 2 } },
  { ...validOverview, metrics: { interfaces: 5, live_tools: '2' } },
  { ...validOverview, installer_actions: [null] },
  { ...validOverview, installer_actions: [{ id: 'a', title: {}, provider: 'Azure' }] },
  { ...validOverview, kopano_interfaces: [{ id: 'i', name: 'IDE', summary: {} }] },
  { ...validOverview, tools: [{ id: 't', name: 123, summary: 'S' }] },
]) {
  assert.equal(isLabsOverview(malformed), false);
}

// 3. /api/labs/analytics contract
const validAnalytics = {
  mcp_console: { requests: 12, sessions: 3 },
  forge: { rooms: 2, tasks: 7 },
};
assert.equal(isLabsAnalytics(validAnalytics), true);
for (const malformed of [
  null,
  {},
  { mcp_console: { requests: {} }, forge: {} },
  { mcp_console: { requests: 1, sessions: '3' }, forge: { rooms: 2, tasks: 7 } },
  { mcp_console: { requests: 1, sessions: 3 }, forge: { rooms: 2, tasks: null } },
  { mcp_console: [], forge: { rooms: 2, tasks: 7 } },
]) {
  assert.equal(isLabsAnalytics(malformed), false);
}

// 4. /api/labs/microsoft-readiness contract
const validReadiness = {
  summary: { required_ready: 4, required_total: 6, demo_ready: false },
  tooling: {
    az: { healthy: true },
    azd: { healthy: true },
    telemetry: { configured: false },
  },
  azure_account: { logged_in: true, subscription_name: 'Demo Subscription' },
  env: { azure_openai: { configured: false, missing: ['AZURE_OPENAI_ENDPOINT'] } },
  next_steps: ['Add Azure OpenAI configuration.'],
};
assert.equal(isMicrosoftReadiness(validReadiness), true);
assert.equal(
  isMicrosoftReadiness({
    ...validReadiness,
    azure_account: { logged_in: false, subscription_name: null },
  }),
  true,
);
for (const malformed of [
  null,
  {},
  { ...validReadiness, summary: { required_ready: '4', required_total: 6, demo_ready: false } },
  { ...validReadiness, summary: { required_ready: 4, required_total: 6, demo_ready: 'true' } },
  { ...validReadiness, tooling: { ...validReadiness.tooling, az: { healthy: 1 } } },
  { ...validReadiness, tooling: { ...validReadiness.tooling, azd: { healthy: 'yes' } } },
  { ...validReadiness, tooling: { ...validReadiness.tooling, telemetry: { configured: {} } } },
  { ...validReadiness, azure_account: { logged_in: 'true', subscription_name: null } },
  { ...validReadiness, azure_account: { logged_in: true, subscription_name: {} } },
  { ...validReadiness, azure_account: { logged_in: false } },
  { ...validReadiness, env: { azure_openai: { configured: 1, missing: [] } } },
  { ...validReadiness, env: { azure_openai: { configured: false, missing: [{}] } } },
  { ...validReadiness, next_steps: [{}] },
]) {
  assert.equal(isMicrosoftReadiness(malformed), false);
}

// 5. /api/labs/cowork/rooms contract
const validRoomSummary = {
  id: 1,
  name: 'Kopano Context Premiere',
  mission: 'Launch cowork flow',
  lead: 'Lead',
  status: 'active',
};
assert.equal(isCoworkRoomsPayload({ rooms: [validRoomSummary] }), true);
assert.equal(isCoworkRoomsPayload({ rooms: [] }), true);
for (const malformed of [
  null,
  {},
  { rooms: [null] },
  { rooms: [{ id: 1, name: {} }] },
  { rooms: [{ ...validRoomSummary, status: {} }] },
  { rooms: [{ ...validRoomSummary, id: '1' }] },
]) {
  assert.equal(isCoworkRoomsPayload(malformed), false);
}

// 6. /api/labs/cowork/rooms/:id contract and hasCoworkRoomDetail
const validTask = {
  id: 10,
  room_id: 1,
  title: 'Implement cards',
  description: 'Ship cards',
  owner: 'DEV_1',
  status: 'in_progress',
  priority: 'high',
  lane: 'build',
};
const validArtifact = {
  id: 20,
  room_id: 1,
  artifact_type: 'api',
  title: 'Connector Pack',
  summary: 'Notes',
  status: 'draft',
  link: null,
};
const validRoomDetail = {
  ...validRoomSummary,
  tasks: [validTask],
  artifacts: [validArtifact],
  lanes: { research: [], build: [validTask], review: [] },
  dispatch_summary: { total_tasks: 1, queued: 0, in_progress: 1, completed: 0, owners: ['DEV_1'] },
  artifact_summary: { total_artifacts: 1, artifact_types: ['api'] },
};
assert.equal(hasCoworkRoomDetail(validRoomDetail), true);
assert.equal(isCoworkRoomDetailPayload({ room: validRoomDetail }, 1), true);
assert.equal(isCoworkRoomDetailPayload({ room: validRoomDetail }, 2), false);
for (const malformedRoom of [
  null,
  validRoomSummary,
  {
    ...validRoomSummary,
    tasks: [],
    artifacts: {},
    lanes: {},
    dispatch_summary: {},
    artifact_summary: {},
  },
  { ...validRoomDetail, name: {} },
  { ...validRoomDetail, tasks: [null] },
  { ...validRoomDetail, artifacts: [{ ...validArtifact, title: {} }] },
  { ...validRoomDetail, artifacts: [{ ...validArtifact, link: {} }] },
  { ...validRoomDetail, lanes: { research: [], build: {} } },
  { ...validRoomDetail, lanes: { research: [], build: [null], review: [] } },
  { ...validRoomDetail, dispatch_summary: { ...validRoomDetail.dispatch_summary, total_tasks: '1' } },
  { ...validRoomDetail, artifact_summary: { total_artifacts: {} } },
]) {
  assert.equal(hasCoworkRoomDetail(malformedRoom), false);
  assert.equal(isCoworkRoomDetailPayload({ room: malformedRoom }, 1), false);
}

export const validStartupFixtures = {
  sessions: validSessions,
  overview: validOverview,
  analytics: validAnalytics,
  readiness: validReadiness,
  roomSummary: validRoomSummary,
  roomDetail: validRoomDetail,
};

console.log('startup contracts tests passed');
