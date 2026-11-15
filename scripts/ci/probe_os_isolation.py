#!/usr/bin/env python3
"""Bounded OS isolation probe. Checks real Linux kernel namespace behavior, not claimed flags.

This is a read-only probe of the CI runner. PASS is NOT a production runtime attestation.
No network operations, target processes, privilege escalation or estate mutations.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys

def probe() -> dict:
    result = {"schema":"kpgs_os_isolation_probe_v1","platform":sys.platform,
              "subject":"current disposable runner","production_runtime_verified":False,
              "capability_permission_enforced":False,"verdict":"HOLD",
              "network_namespaces":False,"user_namespaces":False,"reasons":[]}
    if sys.platform != "linux":
        result["reasons"].append("not a Linux runner; Windows isolation needs a native separate test")
        return result
    if shutil.which("unshare") is None:
        result["reasons"].append("unshare unavailable; cannot prove kernel isolation")
        return result
    child='''import json, os
def ns(kind):
    return os.readlink("/proc/self/ns/"+kind)
print(json.dumps({"user":ns("user"),"net":ns("net"),"uid":os.getuid()}))
'''
    try:
        parent=json.loads(subprocess.run([sys.executable,"-c",child],capture_output=True,text=True,check=True,timeout=5).stdout)
        proc=subprocess.run(["unshare","--user","--net","--map-root-user",sys.executable,"-c",child],
                            capture_output=True,text=True,timeout=10,check=False)
        result["command_exit_code"]=proc.returncode
        if proc.returncode!=0:
            result["reasons"].append("kernel unshare refused or failed: "+proc.stderr.strip()[:180])
            return result
        child_ns=json.loads(proc.stdout)
        result["user_namespaces"]=(parent["user"]!=child_ns["user"])
        result["network_namespaces"]=(parent["net"]!=child_ns["net"])
        if result["user_namespaces"] and result["network_namespaces"]:
            result["verdict"]="PASS_RUNNER_ONLY"
            result["reasons"].append("real distinct kernel namespaces witnessed on CI runner; production deployment still unverified")
        else:
            result["reasons"].append("child and parent namespace identities did not diverge")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        result["reasons"].append("probe failed safely: "+type(exc).__name__)
    return result

if __name__=="__main__":
    result=probe()
    print(json.dumps(result,sort_keys=True))
    sys.exit(0 if result["verdict"]=="PASS_RUNNER_ONLY" else 2)
