'use strict';

const fs = require('fs');

function rewriteDocument(document, command) {
  let changed = 0;
  const walk = (node) => {
    if (Array.isArray(node)) {
      node.forEach(walk);
      return;
    }
    if (!node || typeof node !== 'object') {
      return;
    }
    if (typeof node.command === 'string') {
      if (node.command === command || node.command.includes('telemetry_hook_bundle.js')) {
        if (node.command !== command) {
          node.command = command;
        }
        changed += 1;
      }
    }
    Object.keys(node).forEach((key) => {
      walk(node[key]);
    });
  };
  walk(document);
  return changed;
}

function commandIsSpawnSafe(command) {
  if (command.includes('"') || command.includes("'") || /[;&|<>^]/.test(command)) {
    return false;
  }
  const parts = command.split(' ');
  return parts.length >= 2 && parts[0] === 'node' && parts.every((part) => part.length > 0);
}

function rewriteFile(file, command) {
  if (!commandIsSpawnSafe(command)) {
    return { ok: false, code: 2, message: 'COMMAND_NOT_SPAWN_SAFE' };
  }
  const document = JSON.parse(fs.readFileSync(file, 'utf8'));
  const changed = rewriteDocument(document, command);
  if (changed < 1) {
    return { ok: false, code: 3, message: 'NO_COMMAND_REPLACED' };
  }
  const output = `${JSON.stringify(document, null, 2)}\n`;
  if (output.includes('telemetry_hook_bundle.js') || output.includes('; exit')) {
    return { ok: false, code: 4, message: 'UNSAFE_COMMAND_REMAINS' };
  }
  fs.writeFileSync(file, output);
  return { ok: true, code: 0, message: `REPLACED ${changed}` };
}

function main(argv) {
  const file = argv[2];
  const command = argv[3];
  if (!file || !command) {
    process.stderr.write('usage: rewrite_datacloud_hook_command.js <hooks.json> <command>\n');
    return 1;
  }
  const result = rewriteFile(file, command);
  if (!result.ok) {
    process.stderr.write(`${result.message}\n`);
    return result.code;
  }
  process.stdout.write(`${result.message}\n`);
  return 0;
}

if (require.main === module) {
  process.exit(main(process.argv));
}

module.exports = { rewriteDocument, rewriteFile };
