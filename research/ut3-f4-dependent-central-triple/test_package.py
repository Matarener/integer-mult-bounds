#!/usr/bin/env python3
"""Package controls for the UT3(F4) dependent central triple."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def run(argv):
    completed = subprocess.run(
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def main():
    code, out, err = run([sys.executable, "-I", "-B", str(PACKAGE / "verify.py")])
    need(code == 0, err or out)
    need("PASS_UT3_F4_DEPENDENT_TRIPLE " in out, out)
    code, out, err = run([sys.executable, "-I", "-O", "-Werror", "-B", str(PACKAGE / "verify.py")])
    need(code == 0, err or out)
    need("minimum=12" in out, out)
    code, out, err = run([sys.executable, "-I", "-B", str(PACKAGE / "independent.py")])
    need(code == 0, err or out)
    need("PASS_UT3_F4_DEPENDENT_TRIPLE_INDEPENDENT " in out, out)
    certificate = json.loads((PACKAGE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    need(certificate["minimum_calls"] == 12, "certificate")
    need(certificate["no_new_kappa"] is True, "kappa flag")
    text = (PACKAGE / "CERTIFICATE.json").read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad.json"
        bad.write_text(text.replace('"n_X"', '"n_X": 1, "n_X"', 1), encoding="utf-8")
        probe = (
            "import json,sys\n"
            "def hook(pairs):\n"
            "    keys=[k for k,_ in pairs]\n"
            "    \n"
            "    if len(keys)!=len(set(keys)): raise SystemExit('dup')\n"
            "    return dict(pairs)\n"
            "json.loads(open(sys.argv[1],encoding='utf-8').read(), object_pairs_hook=hook)\n"
            "raise SystemExit('accepted')\n"
        )
        code, out, err = run([sys.executable, "-I", "-B", "-c", probe, str(bad)])
        need(code != 0 and "dup" in (out + err), "duplicate key control")
    print("PASS_UT3_F4_DEPENDENT_TRIPLE_PACKAGE_TESTS groups=3")


if __name__ == "__main__":
    main()
