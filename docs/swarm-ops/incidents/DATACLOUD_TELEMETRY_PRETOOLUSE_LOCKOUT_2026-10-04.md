# Datacloud telemetry PreToolUse lockout — root and recurrence plan

**Status:** CONTAINED on the operator machine. Root identified. Upstream host and plugin fixes are not applied from this repo.  
**Date of this record:** 2026-10-04  
**Recorder of the containment:** AG (Antigravity), Seat 10, Lead Developer, stateless renter.  
**This record:** Cursor cloud renter, stateless. `I_AM_STATELESS_RENTER_NOT_LANDLORD`. No RTC seat.  
**GSMB home copy:** pending Robyn (Q4). This file is the cloud record until that copy exists.  
**Base:** `master@3a25d77c`.

```text
I_AM_STATELESS_RENTER_NOT_LANDLORD
```

## Root

Three defects stack. Any one of them, alone, would leave the tool plane up. Together they block every tool.

1. **The installer writes a shell string into `hooks.json`.** The command recorded on this machine is:

```text
node "C:\Users\rkhol\.gemini\config\plugins\googlecloudtools.datacloud_telemetry\telemetry_hook_bundle.js" --agent_name gemini --install_source "Antigravity IDE" ; exit 0
```

The quotes are there so a profile path that contains spaces still reaches Node as one argument. The `; exit 0` is the installer's fail-open. A public report of the same plugin shows the same shape with an unquoted path when the profile path itself contains a space (`C:\Users\TUF A15\...`). The generator is choosing quoting per path, and it is choosing a shell program either way.

2. **The host starts that string in a way that leaves the quotes in Node's script argument.** Antigravity's hooks document calls `command` "the shell command to execute" ([Hooks](https://antigravity.google/docs/hooks/)). On this failure, Node's own entry-point loader is what throws. The module name in the error is the plugin directory, a backslash, a quote, then the absolute path again:

```text
C:\Users\rkhol\.gemini\config\plugins\googlecloudtools.datacloud_telemetry\"C:\Users\rkhol\.gemini\config\plugins\googlecloudtools.datacloud_telemetry\telemetry_hook_bundle.js"
```

That is `path.win32.resolve(pluginDir, '"C:\\...\\telemetry_hook_bundle.js"')`. A leading quote makes the string non-absolute, so Node joins it onto the working directory. The working directory is the plugin directory. The bundle never starts. `; exit 0` is still sitting in the argument list, so the fail-open never runs. Exit status is 1.

The exact spawn implementation inside Antigravity was not read here. The observable contract break is enough: a documented shell command reached `Module.executeUserEntryPoint` / `run_main_module` with the quote characters intact. Public reports show the same joined path: [179787](https://discuss.ai.google.dev/t/bug-windows-googlecloudtools-datacloud-telemetry-pretooluse-hook-has-malformed-path-with-escaped-quotes-blocking-all-agent-tool-calls/179787) (2026-08-26), [180830](https://discuss.ai.google.dev/t/antigravity-on-windows-pretooluse-telemetry-hook-repeatedly-breaks-all-tool-execution/180830), and the same plugin with a different quoting failure in [179007](https://discuss.ai.google.dev/t/can-not-write-file-when-space-user-profile-at-plugins-googlecloudtools-datacloud-telemetry/179007) (2026-08-21).

3. **`PreToolUse` plus matcher `*` treats that exit as a block of every tool.** The hooks page defines a JSON `decision` field (`allow`, `deny`, `ask`, and the others). It does not publish an exit-code table. Gemini CLI does, and it is the opposite policy for this exit: exit 0 succeeds, exit 2 blocks, any other exit is a warning and the tool continues ([hooks reference](https://geminicli.com/docs/hooks/reference/)). Antigravity's observed policy is that exit 1 from this hook aborts the tool. The hook name in the host error is `jsonhook__googlecloudtools.datacloud_telemetry_PreToolUse_0_0`. Timeout on the recorded command is 30 seconds, on the critical path of every tool, for a telemetry side effect.

Changing the model cannot route around it. The hook runs before the tool, for every model.

## What containment already proved

| Step | Result | Class |
|---|---|---|
| Rename the plugin folder to `….DISABLED` and leave it under `plugins\` | Host still loads the hook. The error's working directory becomes the renamed folder. | E1, this machine, 2026-10-01 through 2026-10-03 |
| Edit `config.json` to disable it | The plugin was never listed there. The edit itself was blocked because every tool was already dead. | E1 |
| Move the folder out of `plugins\`, then kill the process and start again | Tools returned 2026-10-03 08:56. | E1, this machine |
| `path.win32.resolve` of the quoted script, Node v22.14.0 | `isAbsolute` is false. Resolved path matches the operator error, including the embedded quote. | E2, this VM, 2026-10-04 |
| `node` spawned with the quoted path as argv, no shell | Exit 1. `MODULE_NOT_FOUND`. Joined path is `<cwd>/"<absolute>"`. Stack ends in `executeUserEntryPoint` / `run_main_module`. | E2, this VM, 2026-10-04 |
| Same command run by a shell with `; exit 0` | Exit 0, after Node has already failed to find the file. | E2, this VM, 2026-10-04 |

Operator-reported plugin bytes, not re-hashed here: `hooks.json` 456 bytes, `plugin.json` 52 bytes, `telemetry_hook_bundle.js` 18,097 bytes, at `C:\Users\rkhol\Desktop\googlecloudtools.datacloud_telemetry.DISABLED\` after containment. Reported `hooks.json` SHA-256: `86A621BFADAEC35D468233E538D538C78144BEAAFB95A3D68B7A45DC0DE3ACE9`.

The bundle was not read. What it would transmit on a successful run is **UNKNOWN**. It is invoked with `--agent_name gemini`. Do not put it back in order to find out.

## Why this comes back

The host discovers hooks by scanning subfolders of `plugins\`. The folder name is not an off switch. `config.json` is not the discovery list.

A public report says deleting the folder makes Antigravity download it again ([179787](https://discuss.ai.google.dev/t/bug-windows-googlecloudtools-datacloud-telemetry-pretooluse-hook-has-malformed-path-with-escaped-quotes-blocking-all-agent-tool-calls/179787)). That reinstall was **not** reproduced on this machine. Treat it as reported, and treat "the folder is on the Desktop, so this is over" as unproven across the next IDE launch or update.

The documented in-file switch is `"enabled": false` on the hook object ([Hooks](https://antigravity.google/docs/hooks/)). That switch was not what the blocked edit attempted. Whether this host honors it before spawn is **UNKNOWN** until one launch with the folder present, `enabled` false, and a single tool call. It is not a substitute for keeping the folder outside the scan path while that is unknown.

## Operator procedure

Run this in Windows PowerShell. The IDE cannot run it while the hook is blocking tools. One sequence. Do not rename in place. Do not delete the folder. Do not ask the agent to edit `config.json` until a tool call has already succeeded.

```powershell
function Stop-AntigravityHost {
  Get-Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ProcessName -match '^(?i)(Antigravity|agy)$' } |
    Stop-Process -Force -ErrorAction SilentlyContinue
}

Stop-AntigravityHost
Start-Sleep -Seconds 2

$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$dest = Join-Path $env:USERPROFILE "Desktop\antigravity-hook-quarantine\$stamp"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

$roots = @(
  (Join-Path $env:USERPROFILE '.gemini\config\plugins'),
  (Join-Path $env:USERPROFILE '.gemini\antigravity-ide\plugins'),
  (Join-Path $env:USERPROFILE '.gemini\antigravity-cli\plugins')
)
foreach ($root in $roots) {
  if (-not (Test-Path -LiteralPath $root)) { continue }
  Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like 'googlecloudtools.datacloud_telemetry*' } |
    ForEach-Object {
      Move-Item -LiteralPath $_.FullName -Destination (Join-Path $dest $_.Name)
      Write-Output "QUARANTINED $($_.FullName)"
    }
}

Stop-AntigravityHost
Write-Output "DONE $dest"
```

Then start Antigravity and make one trivial tool call. If the plugin directory is back under a `plugins` root and tools die again, run the same sequence again. That second occurrence is the reinstall, and the follow-up is the logon task below plus the upstream report. It is not another rename experiment.

### If it is recreated on launch

Save the sequence above as `%USERPROFILE%\bin\quarantine-datacloud-telemetry.ps1` and register it once from an ordinary PowerShell window:

```powershell
$script = Join-Path $env:USERPROFILE 'bin\quarantine-datacloud-telemetry.ps1'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$script`""
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -TaskName 'Quarantine-Antigravity-Datacloud-Telemetry' -Action $action -Trigger $trigger
```

This is containment (option A), automated. It does not repair the plugin.

## Check that lives in this repo

`scripts/audit_pretooluse_spawn_contract.py` scans a directory for `hooks.json` and exits 2 when a `PreToolUse` command is in the lockout class:

- a quoted absolute path (`"C:\..."` or `"/..."`)
- a `; exit` sequence, which is the shell fail-open
- an enabled `PreToolUse` hook from `googlecloudtools.datacloud_telemetry`, including a folder renamed `.DISABLED`, and including a later install whose command text no longer has quotes

`"enabled": false` is reported as `LATENT` and does not fail the audit. `--quarantine <dir>` moves the plugin directory out of the scan root and refuses a destination inside that root. `--allow-known-plugin` drops the name match and still flags quoted paths and `; exit`.

```text
python3 scripts/audit_pretooluse_spawn_contract.py %USERPROFILE%\.gemini\config\plugins --quarantine %USERPROFILE%\Desktop\antigravity-hook-quarantine
```

Use that from a terminal that is not the locked IDE session. The PowerShell sequence above is the one that works with no checkout.

## Upstream fix

Do this as a report. Do not patch the quarantined bundle locally (option B) unless Robyn approves it, and only with the folder's move-back tested by one tool call and the move-out command already pasted and ready.

### Plugin / installer

- Emit a command with no quotes and no shell metacharacters, run with the plugin directory as the working directory: `node telemetry_hook_bundle.js --agent_name gemini --install_source antigravity-ide`.
- Fail open inside the process. A top-level catch that ends in `process.exit(0)`. The shell text `; exit 0` is not a fail-open on this host, and on `cmd.exe` `;` is not a separator either.
- Stop registering telemetry on `PreToolUse` with matcher `*`. Telemetry belongs after the tool, or off the tool path. A crash in telemetry must not be able to veto `view_file`.
- If the user moved or disabled the plugin, an update must not write an `enabled: true` copy back into `plugins\`.

### Host

- Run `command` through a shell, matching the documented contract, or take an argv array and stop calling the field a shell command. A quote-preserving split that then calls `spawn` without a shell is the failure mode that produces this module path.
- If a `PreToolUse` process fails to start, times out, or exits without a JSON `decision`, let the tool run. Block on an explicit `deny`, or on exit 2, which is the Gemini CLI rule. Exit 1 is a broken telemetry script, not a safety decision.
- Honor `"enabled": false` before spawn.
- Do not load a directory whose name ends in `.DISABLED` or `.bak`.
- Absence from `config.json` must not mean "scan every subdirectory and enable it."

### This repository's own hook runner

`Schematics/06-Reference/kopano-code-implementation/rust/crates/plugins/src/hooks.rs` already has the policy that prevents this outage. Exit 0 allows. Exit 2 denies. Any other exit, and a failure to start, is a warning and the tool continues (`format_hook_warning` says "allowing tool execution to continue"). Windows execution goes through `cmd /C`. That policy stays. Copying Antigravity's "any non-zero PreToolUse blocks the tool" rule into KPGS would reintroduce the outage even after the quoting bug is fixed.

`; exit 0` is still the wrong fail-open to copy. `cmd.exe` does not treat `;` as a separator. The invariant to keep is the exit-code policy, not the shell suffix.

## Upstream report (paste)

```text
Product: Google Antigravity on Windows
Plugin: googlecloudtools.datacloud_telemetry
Hook: PreToolUse, matcher "*", timeout 30
Command written to hooks.json:
  node "<absolute>\telemetry_hook_bundle.js" --agent_name gemini --install_source "Antigravity IDE" ; exit 0

Observed:
  JSON hook "jsonhook__googlecloudtools.datacloud_telemetry_PreToolUse_0_0" failed: command failed: exit status 1
  Error: Cannot find module '<plugin_dir>\"<plugin_dir>\telemetry_hook_bundle.js"'
  code: MODULE_NOT_FOUND
  Stack reaches Module.executeUserEntryPoint / run_main_module.

Effect: every tool call is blocked until the plugin directory is moved out of the plugins scan root. Renaming it inside plugins\ does not unload it. config.json does not list the plugin.

Mechanism: the documented shell command is reaching Node with the quote characters included in the script path. path.win32.isAbsolute is false for a path that starts with a quote, so Node joins it onto the plugin directory. "; exit 0" is not executed, so the intended fail-open never runs. Exit 1 is then treated as a PreToolUse block. Gemini CLI documents the other policy: only exit 2 blocks; any other exit is a warning.

Ask:
  1. Spawn hook commands with a real shell, or pass an argv array.
  2. Do not block the tool when a PreToolUse command fails to start or exits 1. Block only on decision "deny" or exit 2.
  3. Generate a quote-free relative command, and exit 0 from inside the bundle on telemetry failure.
  4. Do not scan *.DISABLED, and do not reinstall this plugin into plugins\ after the user has moved it out.
```

## Option map

| Option | Action | When |
|---|---|---|
| A | Keep the plugin outside every `plugins` scan root. Automate that with the logon task if a launch puts it back. | Now. This is the applied containment. |
| B | Repair the command in place and restore the folder. | Only after Robyn approves, and only with the move-out command ready before the test call. |
| C | Send the report above to the plugin and host owners. | With A. Independent of B. |

## UNKNOWN

- The contents and network behavior of `telemetry_hook_bundle.js`.
- Whether this host honors `"enabled": false` before spawn.
- Whether this host reinstalls the plugin after the folder leaves `plugins\`. Reported by another Windows user on 2026-08-26. Not reproduced here.
- The host function that builds argv. The joined path and the `run_main_module` stack constrain it. They do not name the function.

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
