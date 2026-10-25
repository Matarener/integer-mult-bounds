#!/usr/bin/env python3
"""Canonical replay of the scoped baseline, native review and extended component.

SPDX-License-Identifier: Apache-2.0
Substantial OpenAI Codex assistance under user direction.
"""
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SCRIPTS=("audit.py","review_native.py","symmetric_extended.py","complete_contract_budget.py")


def main():
    out={"status":"PASS_SCOPED_BASELINE_AND_LOCAL_COMPONENT_REPLAY","runs":[]}
    for script in SCRIPTS:
        p=HERE/script
        r=subprocess.run([sys.executable,"-B",str(p)],cwd=REPO,text=True,capture_output=True)
        (HERE/(script+".log")).write_text(r.stdout+r.stderr)
        if r.returncode:
            print(r.stdout+r.stderr)
            raise RuntimeError(script+" failed")
        out["runs"].append({"script":script,"sha256":sha256(p.read_bytes()).hexdigest(),"exit_code":r.returncode})
        print("PASS",script,flush=True)
    out["scope"]="Exact invoice arithmetic, separately bound native component review, and finite symmetric128-port Gaussian component; no whole-supplier or kappa admission"
    (HERE/"REPLAY.json").write_text(json.dumps(out,indent=2)+"\n")
    print(out["status"],flush=True)


if __name__=="__main__":main()
