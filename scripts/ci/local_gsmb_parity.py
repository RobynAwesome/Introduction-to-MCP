#!/usr/bin/env python3
"""Read-only, minimal Local↔Cloud Schematics parity probe.

Run *on the owner's trusted Windows machine*, never in a GitHub runner as
proof of the Windows estate. Emits hashes and file presence, not contents.
This is a bounded critical-file comparison, not whole-estate parity.
"""
from __future__ import annotations
import argparse, hashlib, json, subprocess, sys
from pathlib import Path
from datetime import datetime, timezone

REQUIRED=(
    "00-Home/00-Home - Index.md",
    "21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/Legacy.md",
    "21-KOPANO-PHU GOVERNACE SYSTEMS/MAIN-BRAIN/STATELESS_RENTER_ENTRYWAY.md",
    "index.md",
)
def digest(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(local:Path,cloud:Path)->dict:
    result={"schema":"gsmb_local_parity_probe_v1",
            "observed_utc":datetime.now(timezone.utc).isoformat(),
            "files":[],"scope":"Four critical Schematics files only",
            "verdict":"HOLD","local_source_verified":False,
            "cloud_head":None}
    try:
        result["cloud_head"]=subprocess.run(
            ["git","rev-parse","HEAD"],cwd=cloud,
            capture_output=True,text=True,timeout=10,check=True
        ).stdout.strip()
    except (OSError,subprocess.SubprocessError):
        result["cloud_head"]=None
    for rel in REQUIRED:
        a=local/rel
        b=cloud/"Schematics"/rel
        row={"relative":rel,"local_present":a.is_file(),"cloud_present":b.is_file(),
             "local_sha256":digest(a) if a.is_file() else None,
             "cloud_sha256":digest(b) if b.is_file() else None}
        row["match"]=row["local_sha256"] is not None and row["local_sha256"]==row["cloud_sha256"]
        result["files"].append(row)
    result["local_source_verified"]=local.is_dir() and any(x["local_present"] for x in result["files"])
    if result["local_source_verified"] and result["cloud_head"] and all(x["match"] for x in result["files"]):
        result["verdict"]="MATCHED_BOUNDED_SAMPLE"
    else:
        result["verdict"]="HOLD_PARITY_NOT_PROVEN"
    return result

def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--local-schematics",type=Path,required=True)
    p.add_argument("--cloud-repo",type=Path,required=True)
    p.add_argument("--output",type=Path,default=None)
    a=p.parse_args()
    r=audit(a.local_schematics,a.cloud_repo)
    s=json.dumps(r,indent=2,sort_keys=True)+"\n"
    if a.output:
        a.output.write_text(s,encoding="utf-8")
    print(s)
    return 0 if r["verdict"]=="MATCHED_BOUNDED_SAMPLE" else 2

if __name__=="__main__":
    raise SystemExit(main())
