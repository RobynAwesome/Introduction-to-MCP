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
} finally {
  await vite.close();
}

console.log('console responsive and unavailable-state tests passed');
