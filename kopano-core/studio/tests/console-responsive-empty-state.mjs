import './console-status-contract.mjs';
import { validStartupFixtures } from './startup-contracts.mjs';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { createServer } from 'vite';
import { getApiUnavailableMessage } from '../src/consoleStatusCopy.mjs';

const localUnavailable = getApiUnavailableMessage('http://127.0.0.1:8000');
assert.match(localUnavailable, /Local API is unavailable/);
assert.doesNotMatch(localUnavailable, /127\.0\.0\.1/);
assert.match(localUnavailable, /python main\.py serve api/);
assert.match(localUnavailable, /then retry/);

const configuredUnavailable = getApiUnavailableMessage('https://context.example.test');
assert.match(configuredUnavailable, /Configured API is unavailable/);
assert.doesNotMatch(configuredUnavailable, /context\.example\.test/);
assert.match(configuredUnavailable, /Check the configured endpoint and network/);

const localHttpError = getApiUnavailableMessage('http://localhost:8000', 503);
assert.match(localHttpError, /returned HTTP 503/);
assert.match(localHttpError, /Confirm the API is running/);
assert.doesNotMatch(localHttpError, /PASS|FAIL/);

const css = await readFile(new URL('../src/App.css', import.meta.url), 'utf8');

function mediaBlock(maxWidth) {
  const marker = `@media (max-width: ${maxWidth}px)`;
  const start = css.indexOf(marker);
  assert.notEqual(start, -1, `missing ${marker}`);
  let index = css.indexOf('{', start) + 1;
  let depth = 1;
  for (; index < css.length && depth > 0; index += 1) {
    if (css[index] === '{') depth += 1;
    if (css[index] === '}') depth -= 1;
  }
  assert.equal(depth, 0, `unclosed ${marker}`);
  return css.slice(css.indexOf('{', start) + 1, index - 1);
}

const tabletRules = mediaBlock(1320);
assert.match(tabletRules, /\.swarm-right\s*\{[^}]*visibility:\s*hidden/s);
assert.match(tabletRules, /\.swarm-right\.is-open\s*\{[^}]*visibility:\s*visible/s);
assert.match(tabletRules, /\.swarm-proof-toggle\s*\{[^}]*display:\s*inline-flex/s);

const mobileRules = mediaBlock(980);
assert.match(mobileRules, /\.swarm-menu-toggle\s*\{[^}]*display:\s*inline-flex/s);
assert.match(mobileRules, /\.swarm-navigation\s*\{[^}]*visibility:\s*hidden/s);
assert.match(mobileRules, /\.swarm-navigation\.is-open\s*\{[^}]*visibility:\s*visible/s);
assert.match(mobileRules, /\.swarm-drawer-backdrop\s*\{[^}]*display:\s*block/s);

const vite = await createServer({
  configFile: fileURLToPath(new URL('../vite.config.ts', import.meta.url)),
  server: { middlewareMode: true },
  appType: 'custom',
  logLevel: 'error',
});
try {
  const { BackendUnavailableState } = await vite.ssrLoadModule('/src/pages/ConsolePage.tsx');
  const proofMarkup = renderToStaticMarkup(React.createElement(BackendUnavailableState, {
    surface: 'Proof',
    message: localUnavailable,
    loading: false,
    onRetry: () => {},
  }));
  assert.match(proofMarkup, /API unavailable/);
  assert.match(proofMarkup, /Proof status unavailable/);
  assert.match(proofMarkup, /Local API is unavailable/);
  assert.match(proofMarkup, /No PASS or FAIL result is inferred/);
  assert.match(proofMarkup, /Retry status/);

  const checkingMarkup = renderToStaticMarkup(React.createElement(BackendUnavailableState, {
    surface: 'Proof',
    message: localUnavailable,
    loading: true,
    onRetry: () => {},
  }));
  assert.match(checkingMarkup, /Checking API/);
  assert.match(checkingMarkup, /Waiting for the configured backend status response/);
  assert.doesNotMatch(checkingMarkup, /API unavailable|PASS or FAIL/);

  const ciMarkup = renderToStaticMarkup(React.createElement(BackendUnavailableState, {
    surface: 'CI',
    message: configuredUnavailable,
    loading: false,
    onRetry: () => {},
  }));
  assert.match(ciMarkup, /CI status unavailable/);
  assert.match(ciMarkup, /Configured API is unavailable/);
  assert.match(ciMarkup, /No CI result is inferred/);
  assert.match(ciMarkup, /Retry status/);

  const noop = () => {};
  const { AdminPage } = await vite.ssrLoadModule('/src/pages/AdminPage.tsx');
  const { LabsPage } = await vite.ssrLoadModule('/src/pages/LabsPage.tsx');
  const { ForgePage } = await vite.ssrLoadModule('/src/pages/ForgePage.tsx');

  const baseAdminProps = {
    isAdminLoggedIn: true,
    adminUser: {
      id: 1,
      email: 'admin@kopano.local',
      role: 'admin',
      god_mode: false,
      is_active: true,
      created_at: '2026-11-07T00:00:00Z',
    },
    adminEmail: 'admin@kopano.local',
    adminPassword: '',
    adminError: null,
    adminLoading: false,
    selectedSession: null,
    adminFeedPreview: [],
    onAdminEmailChange: noop,
    onAdminPasswordChange: noop,
    onLogin: noop,
    onLogout: noop,
    onLoadSession: noop,
    onOverrideScore: noop,
  };

  const adminValidMarkup = renderToStaticMarkup(React.createElement(AdminPage, {
    ...baseAdminProps,
    sessions: validStartupFixtures.sessions,
    labsAnalytics: validStartupFixtures.analytics,
    microsoftReadiness: validStartupFixtures.readiness,
  }));
  assert.match(adminValidMarkup, /KC apprenticeship/);
  assert.match(adminValidMarkup, /4\/6/);

  const adminFallbackMarkup = renderToStaticMarkup(React.createElement(AdminPage, {
    ...baseAdminProps,
    sessions: [],
    labsAnalytics: null,
    microsoftReadiness: null,
  }));
  assert.match(adminFallbackMarkup, /Forensic sessions/);

  const labsValidMarkup = renderToStaticMarkup(React.createElement(LabsPage, {
    labsOverview: validStartupFixtures.overview,
    labsAnalytics: validStartupFixtures.analytics,
    microsoftReadiness: validStartupFixtures.readiness,
    connectorResult: '',
    isAdminLoggedIn: false,
    onNavigate: noop,
    onRunConnectorAction: noop,
  }));
  assert.match(labsValidMarkup, /Azure Demo Day Bootstrap/);
  assert.match(labsValidMarkup, /Demo Subscription/);
  assert.match(labsValidMarkup, /IDE Workspace/);
  assert.match(labsValidMarkup, /Gig Matcher/);

  const labsFallbackMarkup = renderToStaticMarkup(React.createElement(LabsPage, {
    labsOverview: null,
    labsAnalytics: null,
    microsoftReadiness: null,
    connectorResult: '',
    isAdminLoggedIn: false,
    onNavigate: noop,
    onRunConnectorAction: noop,
  }));
  assert.match(labsFallbackMarkup, /0\/6/);

  const baseForgeProps = {
    roomName: '',
    roomMission: '',
    taskTitle: '',
    taskDescription: '',
    taskOwner: 'DEV_1',
    taskPriority: 'high',
    artifactTitle: '',
    artifactSummary: '',
    artifactType: 'api',
    editingTaskId: null,
    editingArtifactId: null,
    laneOrder: ['research', 'build', 'review'],
    ownerOptions: ['Lead', 'DEV_1'],
    onRoomNameChange: noop,
    onRoomMissionChange: noop,
    onTaskTitleChange: noop,
    onTaskDescriptionChange: noop,
    onTaskOwnerChange: noop,
    onTaskPriorityChange: noop,
    onArtifactTitleChange: noop,
    onArtifactSummaryChange: noop,
    onArtifactTypeChange: noop,
    onCreateRoom: noop,
    onSelectRoom: noop,
    onCreateOrUpdateTask: noop,
    onCreateArtifact: noop,
    onUpdateTaskStatus: noop,
    onUpdateTaskOwner: noop,
    onMoveTaskToLane: noop,
    onEditTask: noop,
    onEditArtifact: noop,
  };

  const forgeValidMarkup = renderToStaticMarkup(React.createElement(ForgePage, {
    ...baseForgeProps,
    coworkRooms: [validStartupFixtures.roomDetail],
    activeRoom: validStartupFixtures.roomDetail,
  }));
  assert.match(forgeValidMarkup, /Kopano Context Premiere/);
  assert.match(forgeValidMarkup, /Connector Pack/);

  const forgeSummaryOnlyMarkup = renderToStaticMarkup(React.createElement(ForgePage, {
    ...baseForgeProps,
    coworkRooms: [validStartupFixtures.roomSummary],
    activeRoom: null,
  }));
  assert.match(forgeSummaryOnlyMarkup, /Kopano Context Premiere/);
} finally {
  await vite.close();
}

console.log('console responsive and unavailable-state tests passed');
