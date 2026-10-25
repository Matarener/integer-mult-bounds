#!/usr/bin/env python3
"""Package controls: corruption, duplicate keys, read-only default, -O admission.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_TEST: {message}")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True)


def main():
    groups = 0

    groups += 1
    bad = []

    def hook(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            bad.append(True)
        return dict(items)

    json.loads('{"a":1,"a":2}', object_pairs_hook=hook)
    need(bad, "duplicate key hook fires")

    groups += 1
    bad.clear()
    cert_text = (HERE / "CERTIFICATE.json").read_text()
    json.loads(cert_text, object_pairs_hook=hook)
    need(not bad, "certificate unique keys")
    cert = json.loads(cert_text)
    need(cert["no_new_kappa"] is True, "kappa flag")
    need(cert["boolean_meter_inventory"] is False, "no meters")
    need(cert["n2_census_reprinted"] is False, "no n2 census")
    need(cert["dimension"] == 3, "n=3")

    groups += 1
    before = (HERE / "CERTIFICATE.json").read_bytes()
    proc = run([sys.executable, "-I", "-B", str(HERE / "verify.py")])
    need(proc.returncode == 0, proc.stdout + proc.stderr)
    need("PASS_PRECISION_BLIND_N3_DUAL_SCALE" in proc.stdout, proc.stdout)
    need((HERE / "CERTIFICATE.json").read_bytes() == before, "verify left certificate untouched")

    groups += 1
    proc = run([sys.executable, "-I", "-O", "-Werror", "-B", str(HERE / "verify.py")])
    need(proc.returncode == 0, "-O -Werror verify: " + proc.stdout + proc.stderr)

    groups += 1
    proc = run([sys.executable, "-I", "-B", str(HERE / "independent.py")])
    need(proc.returncode == 0, proc.stdout + proc.stderr)
    need("PASS_INDEPENDENT_PRECISION_BLIND_N3_DUAL_SCALE" in proc.stdout, proc.stdout)

    groups += 1
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pkg = tmp_path / "research" / HERE.name
        shutil.copytree(HERE, pkg)
        corrupt = json.loads((pkg / "CERTIFICATE.json").read_text())
        corrupt["single_factor_exists_count"] = 1
        (pkg / "CERTIFICATE.json").write_text(
            json.dumps(corrupt, indent=2, sort_keys=True) + "\n"
        )
        driver = (
            "import runpy,sys; sys.argv=['verify.py']; "
            f"runpy.run_path({str(pkg / 'verify.py')!r}, run_name='__main__')"
        )
        proc = run([sys.executable, "-I", "-B", "-c", driver], cwd=ROOT)
        need(proc.returncode != 0, "corrupted certificate should fail")

    print(f"PASS_PRECISION_BLIND_N3_DUAL_SCALE_PACKAGE_TESTS groups={groups}")


if __name__ == "__main__":
    main()
