#!/usr/bin/env python3
"""Package controls: duplicate keys, read-only verify, -O admission, corruption.

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


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL_TEST: {message}")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True)


def main() -> None:
    groups = 0

    groups += 1
    dup = []

    def hook(items):
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            dup.append(True)
        return dict(items)

    json.loads('{"a": 1, "a": 2}', object_pairs_hook=hook)
    need(dup, "duplicate key hook fires")
    dup.clear()
    cert_text = (HERE / "CERTIFICATE.json").read_text(encoding="utf-8")
    json.loads(cert_text, object_pairs_hook=hook)
    need(not dup, "certificate unique keys")
    cert = json.loads(cert_text)
    need(cert["no_new_kappa"] is True, "kappa flag")
    need(cert["boolean_meters"] is False, "no meters")
    need(cert["prime_power_grid_reprinted"] is False, "no grid reprint")
    need(cert["composite_single_factor_witnesses"][0]["single_factor"] is True,
         "CRT witness")

    groups += 1
    before = (HERE / "CERTIFICATE.json").read_bytes()
    proc = run([sys.executable, "-I", "-B", str(HERE / "verify.py")])
    need(proc.returncode == 0, proc.stdout + proc.stderr)
    need("PASS_PRECISION_BLIND_COMPOSITE_RIGIDITY" in proc.stdout, proc.stdout)
    need((HERE / "CERTIFICATE.json").read_bytes() == before, "verify left certificate untouched")

    groups += 1
    proc = run([sys.executable, "-I", "-O", "-Werror", "-B", str(HERE / "verify.py")])
    need(proc.returncode == 0, "-O -Werror: " + proc.stdout + proc.stderr)
    need("PASS_PRECISION_BLIND_COMPOSITE_RIGIDITY" in proc.stdout, proc.stdout)

    groups += 1
    proc = run([sys.executable, "-I", "-B", str(HERE / "independent.py")])
    need(proc.returncode == 0, proc.stdout + proc.stderr)
    need("PASS_INDEPENDENT_PRECISION_BLIND_COMPOSITE_RIGIDITY" in proc.stdout, proc.stdout)

    groups += 1
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "research_package.py").write_text("# marker\n", encoding="utf-8")
        for rel in (
            "certificates/selected-result.json",
            "docs/research/agent-task-catalog.json",
        ):
            dest = tmp_path / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / rel, dest)
        pkg = tmp_path / "research" / HERE.name
        shutil.copytree(HERE, pkg)
        corrupt = json.loads((pkg / "CERTIFICATE.json").read_text(encoding="utf-8"))
        corrupt["composite_single_factor_witnesses"][0]["single_factor"] = False
        (pkg / "CERTIFICATE.json").write_text(json.dumps(corrupt, indent=2) + "\n", encoding="utf-8")
        proc = run([sys.executable, "-I", "-B", str(pkg / "verify.py")])
        need(proc.returncode != 0, "corrupted certificate should fail")
        # Duplicate key inside a temp receipt is rejected by the loader.
        bad = tmp_path / "dup.json"
        bad.write_text('{"no_new_kappa": true, "no_new_kappa": false}\n', encoding="utf-8")
        loader = (
            "import importlib.util, sys\n"
            f"spec = importlib.util.spec_from_file_location('verify', {str(HERE / 'verify.py')!r})\n"
            "mod = importlib.util.module_from_spec(spec)\n"
            "spec.loader.exec_module(mod)\n"
            f"mod.load_json_reject_duplicates(__import__('pathlib').Path({str(bad)!r}))\n"
        )
        proc = run([sys.executable, "-I", "-B", "-c", loader])
        need(proc.returncode != 0, "duplicate key file should fail")

    print(f"PASS_PRECISION_BLIND_COMPOSITE_RIGIDITY_PACKAGE_TESTS groups={groups}")


if __name__ == "__main__":
    main()
