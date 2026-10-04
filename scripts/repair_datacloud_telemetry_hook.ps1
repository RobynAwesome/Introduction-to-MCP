# Repair googlecloudtools.datacloud_telemetry so its PreToolUse hook cannot lock every tool.
# Run in Windows PowerShell (the PS C:\WINDOWS\system32 window), not as an Antigravity tool.
$ErrorActionPreference = 'Stop'

function Write-Utf8NoBom([string]$Path, [string]$Content) {
  $utf8 = New-Object System.Text.UTF8Encoding $false
  [System.IO.File]::WriteAllText($Path, $Content, $utf8)
}

function Stop-AntigravityHost {
  Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -match '^(?i)(Antigravity|agy)$' } |
    Stop-Process -Force -ErrorAction SilentlyContinue
}

$pluginName = 'googlecloudtools.datacloud_telemetry'
$destParent = Join-Path $env:USERPROFILE '.gemini\config\plugins'
$dest = Join-Path $destParent $pluginName
$wrapperName = 'telemetry_hook_failopen.js'
$bundleName = 'telemetry_hook_bundle.js'

if ($dest -match '[\s"]') {
  Write-Output "REFUSED path contains a space or quote: $dest"
  exit 2
}

if (Test-Path -LiteralPath $dest) {
  $existingHooks = Join-Path $dest 'hooks.json'
  $existingWrapper = Join-Path $dest $wrapperName
  $hooksText = ''
  if (Test-Path -LiteralPath $existingHooks) {
    $hooksText = [System.IO.File]::ReadAllText($existingHooks)
  }
  if ((Test-Path -LiteralPath $existingWrapper) -and ($hooksText -like '*telemetry_hook_failopen.js*') -and ($hooksText -notlike '*telemetry_hook_bundle.js*')) {
    Write-Output "ALREADY_REPAIRED $dest"
    exit 0
  }
  Write-Output "REFUSED destination already exists and is not the repaired hook: $dest"
  exit 2
}

$candidates = New-Object System.Collections.Generic.List[string]
foreach ($candidate in @(
  (Join-Path $env:USERPROFILE "Desktop\$pluginName.DISABLED"),
  (Join-Path $env:USERPROFILE "Desktop\$pluginName")
)) {
  if (Test-Path -LiteralPath $candidate) {
    $candidates.Add($candidate)
  }
}
$quarantine = Join-Path $env:USERPROFILE 'Desktop\antigravity-hook-quarantine'
if (Test-Path -LiteralPath $quarantine) {
  Get-ChildItem -LiteralPath $quarantine -Recurse -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "$pluginName*" } |
    ForEach-Object { $candidates.Add($_.FullName) }
}
$sources = @($candidates | Select-Object -Unique)
if ($sources.Count -ne 1) {
  Write-Output "REFUSED expected one plugin copy, found $($sources.Count)"
  $sources | ForEach-Object { Write-Output "SOURCE $_" }
  exit 2
}
$src = $sources[0]
$bundle = Join-Path $src $bundleName
$hooks = Join-Path $src 'hooks.json'
if (-not (Test-Path -LiteralPath $bundle)) {
  Write-Output "REFUSED missing $bundle"
  exit 2
}
if (-not (Test-Path -LiteralPath $hooks)) {
  Write-Output "REFUSED missing $hooks"
  exit 2
}

$wrapperPath = Join-Path $dest $wrapperName
$command = "node $wrapperPath --agent_name gemini --install_source antigravity-ide"
$work = Join-Path $env:TEMP 'datacloud-hook-repair'
New-Item -ItemType Directory -Force -Path $work | Out-Null
$rewriter = Join-Path $work 'rewrite_datacloud_hook_command.js'
# REWRITER_JS_BEGIN
$rewriterJs = @'
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
'@
# REWRITER_JS_END
Write-Utf8NoBom $rewriter $rewriterJs

$backup = Join-Path $src 'hooks.json.before-repair'
if (-not (Test-Path -LiteralPath $backup)) {
  Copy-Item -LiteralPath $hooks -Destination $backup
}
& node $rewriter $hooks $command
if ($LASTEXITCODE -ne 0) {
  Copy-Item -LiteralPath $backup -Destination $hooks -Force
  Write-Output "REFUSED rewrite failed; hooks.json restored"
  exit 1
}

# WRAPPER_JS_BEGIN
$wrapperJs = @'
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
'@
# WRAPPER_JS_END
Write-Utf8NoBom (Join-Path $src $wrapperName) $wrapperJs

Stop-AntigravityHost
Start-Sleep -Seconds 2
New-Item -ItemType Directory -Force -Path $destParent | Out-Null
Move-Item -LiteralPath $src -Destination $dest

foreach ($required in @(
  (Join-Path $dest 'hooks.json'),
  (Join-Path $dest $wrapperName),
  (Join-Path $dest $bundleName),
  (Join-Path $dest 'hooks.json.before-repair')
)) {
  if (-not (Test-Path -LiteralPath $required)) {
    Write-Output "REPAIR_INCOMPLETE $required"
    exit 1
  }
}

Write-Output "REPAIRED $dest"
Write-Output "COMMAND $command"
Write-Output "ROLLBACK Move-Item -LiteralPath '$dest' -Destination '$env:USERPROFILE\Desktop\$pluginName.DISABLED'"
Write-Output "NEXT start Antigravity and run: echo AG tool call OK"
