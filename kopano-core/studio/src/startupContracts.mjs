import { isBoolean, isObject, isString, isStringArray } from './consoleStatusCopy.mjs';

const isOptionalInteger = (value) => value === undefined || Number.isInteger(value);

const hasNamedSummary = (entry) => (
  isObject(entry) && [entry.id, entry.name, entry.summary].every(isString)
);

const isInstallerActionSummary = (action) => (
  isObject(action) && [action.id, action.title, action.provider].every(isString)
);

const isCoworkRoomSummary = (room) => (
  isObject(room)
  && Number.isInteger(room.id)
  && [room.name, room.mission, room.lead, room.status].every(isString)
);

const isCoworkTask = (task) => (
  isObject(task)
  && Number.isInteger(task.id)
  && isOptionalInteger(task.room_id)
  && [task.title, task.description, task.owner, task.status, task.priority, task.lane].every(isString)
);

const isCoworkArtifact = (artifact) => (
  isObject(artifact)
  && Number.isInteger(artifact.id)
  && isOptionalInteger(artifact.room_id)
  && [artifact.artifact_type, artifact.title, artifact.summary, artifact.status].every(isString)
  && (artifact.link === undefined || artifact.link === null || isString(artifact.link))
);

const REQUIRED_COWORK_LANES = ['research', 'build', 'review'];

/**
 * Validate the startup /sessions list payload rendered by Council and Admin.
 * @param {unknown} value
 * @returns {boolean}
 */
export function isSessionList(value) {
  return Array.isArray(value) && value.every((session) => (
    isObject(session)
    && Number.isInteger(session.id)
    && isString(session.topic)
    && isString(session.created_at)
    && isOptionalInteger(session.round_count)
    && isOptionalInteger(session.audit_events)
  ));
}

/**
 * Validate rendered Labs overview metrics and playbook/catalog entries.
 * @param {unknown} value
 * @returns {boolean}
 */
export function isLabsOverview(value) {
  if (!isObject(value) || !isObject(value.metrics)) return false;
  return [value.metrics.interfaces, value.metrics.live_tools].every(Number.isInteger)
    && Array.isArray(value.installer_actions) && value.installer_actions.every(isInstallerActionSummary)
    && Array.isArray(value.kopano_interfaces) && value.kopano_interfaces.every(hasNamedSummary)
    && Array.isArray(value.tools) && value.tools.every(hasNamedSummary);
}

/**
 * Validate rendered Labs, Console, and Admin analytics counters.
 * @param {unknown} value
 * @returns {boolean}
 */
export function isLabsAnalytics(value) {
  return isObject(value)
    && isObject(value.mcp_console)
    && isObject(value.forge)
    && [
      value.mcp_console.requests,
      value.mcp_console.sessions,
      value.forge.rooms,
      value.forge.tasks,
    ].every(Number.isInteger);
}

/**
 * Validate rendered Microsoft readiness flags, counters, subscription name, and string lists.
 * @param {unknown} value
 * @returns {boolean}
 */
export function isMicrosoftReadiness(value) {
  if (
    !isObject(value)
    || !isObject(value.summary)
    || !isObject(value.tooling)
    || !isObject(value.tooling.az)
    || !isObject(value.tooling.azd)
    || !isObject(value.tooling.telemetry)
    || !isObject(value.azure_account)
    || !isObject(value.env)
    || !isObject(value.env.azure_openai)
  ) {
    return false;
  }

  return [value.summary.required_ready, value.summary.required_total].every(Number.isInteger)
    && [
      value.summary.demo_ready,
      value.tooling.az.healthy,
      value.tooling.azd.healthy,
      value.tooling.telemetry.configured,
      value.azure_account.logged_in,
      value.env.azure_openai.configured,
    ].every(isBoolean)
    && (value.azure_account.subscription_name === null || isString(value.azure_account.subscription_name))
    && isStringArray(value.env.azure_openai.missing)
    && isStringArray(value.next_steps);
}

/**
 * Validate the cowork room summary list payload before storing room summaries.
 * @param {unknown} value
 * @returns {boolean}
 */
export function isCoworkRoomsPayload(value) {
  return isObject(value) && Array.isArray(value.rooms) && value.rooms.every(isCoworkRoomSummary);
}

/**
 * Validate a cowork room's full detail payload (tasks, artifacts, lanes, and rendered summaries).
 * @param {unknown} room
 * @returns {boolean}
 */
export function hasCoworkRoomDetail(room) {
  if (!isCoworkRoomSummary(room)) return false;
  if (!Array.isArray(room.tasks) || !room.tasks.every(isCoworkTask)) return false;
  if (!Array.isArray(room.artifacts) || !room.artifacts.every(isCoworkArtifact)) return false;
  if (!isObject(room.lanes)) return false;
  if (!REQUIRED_COWORK_LANES.every((lane) => Array.isArray(room.lanes[lane]))) return false;
  if (!Object.values(room.lanes).every((laneTasks) => Array.isArray(laneTasks) && laneTasks.every(isCoworkTask))) {
    return false;
  }
  if (!isObject(room.dispatch_summary) || !isObject(room.artifact_summary)) return false;

  return [
    room.dispatch_summary.total_tasks,
    room.dispatch_summary.in_progress,
    room.dispatch_summary.completed,
    room.artifact_summary.total_artifacts,
  ].every(Number.isInteger)
    && isOptionalInteger(room.dispatch_summary.queued)
    && (room.dispatch_summary.owners === undefined || isStringArray(room.dispatch_summary.owners))
    && (room.artifact_summary.artifact_types === undefined || isStringArray(room.artifact_summary.artifact_types));
}

/**
 * Validate a cowork room detail envelope against the requested room ID.
 * @param {unknown} value
 * @param {number} expectedRoomId
 * @returns {boolean}
 */
export function isCoworkRoomDetailPayload(value, expectedRoomId) {
  return isObject(value)
    && hasCoworkRoomDetail(value.room)
    && value.room.id === expectedRoomId;
}
