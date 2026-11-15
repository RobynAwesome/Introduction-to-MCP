#!/usr/bin/env python3
"""Actual OS container boundary probe on disposable Docker host, not an estate attestation."""
from __future__ import annotations
import json
import shutil
import subprocess
import sys

CHILD = """
import json, os, socket
checks={}
checks["nonroot"] = os.geteuid() != 0
try:
    with open("/kpgs-should-never-write", "w") as f:
        f.write("forbidden")
except OSError:
    checks["rootfs_readonly"] = True
else:
    checks["rootfs_readonly"] = False
try:
    socket.create_connection(("1.1.1.1", 443), timeout=3)
except OSError:
    checks["network_denied"] = True
else:
    checks["network_denied"] = False
checks["no_prod_token_injected"] = "GITHUB_TOKEN" not in os.environ
print(json.dumps(checks))
"""
def main():
    report={"schema":"kpgs_disposable_docker_boundary_v1","target":"GitHub hosted Docker runner",
            "verdict":"HOLD","production_runtime_verified":False}
    if not shutil.which("docker"):
        report["reason"]="docker command unavailable"
        print(json.dumps(report))
        return 2
    argv=["docker","run","--rm","--network","none","--read-only","--cap-drop","ALL",
          "--security-opt","no-new-privileges","--pids-limit","64","--memory","128m",
          "--cpus","0.5","--user","65534:65534","python:3.12-alpine",
          "python","-c",CHILD]
    try:
        result=subprocess.run(argv,capture_output=True,text=True,timeout=120,check=False)
        report["process_exit"]=result.returncode
        if result.returncode:
            report["reason"]="docker run denied/failed: "+result.stderr.strip()[-250:]
        else:
            checks=json.loads(result.stdout.strip())
            report["checks"]=checks
            if checks and all(v is True for v in checks.values()):
                report["verdict"]="PASS_RUNNER_ONLY"
            else:
                report["reason"]="one or more real container boundary tests failed"
    except (OSError,subprocess.SubprocessError,ValueError) as exc:
        report["reason"]="probe error: "+type(exc).__name__
    print(json.dumps(report,sort_keys=True))
    return 0 if report["verdict"]=="PASS_RUNNER_ONLY" else 2
if __name__=="__main__":
    raise SystemExit(main())
