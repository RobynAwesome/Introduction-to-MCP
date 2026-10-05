'use strict';

const { spawn } = require('child_process');
const path = require('path');

const bundle = path.join(__dirname, 'telemetry_hook_bundle.js');
const limit = Number(process.env.DATACLOUD_HOOK_FAIL_OPEN_MS || 20000);
let finished = false;
let child = null;

function finish() {
  if (finished) {
    return;
  }
  finished = true;
  if (child) {
    try {
      child.kill();
    } catch {
      // The bundle has already exited.
    }
  }
  process.exit(0);
}

try {
  child = spawn(process.execPath, [bundle].concat(process.argv.slice(2)), {
    cwd: __dirname,
    windowsHide: true,
    stdio: ['pipe', 'inherit', 'inherit'],
  });
  child.on('error', finish);
  child.on('exit', finish);
  process.stdin.on('error', finish);
  if (child.stdin) {
    child.stdin.on('error', finish);
    process.stdin.pipe(child.stdin);
  }
} catch {
  finish();
}

setTimeout(finish, Number.isFinite(limit) && limit >= 0 ? limit : 20000);
