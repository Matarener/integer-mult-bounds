#!/usr/bin/env python3
"""Package controls for PR2298 §3 opcounts. Wentao Li + AI, Apache-2.0."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PY = sys.executable


def need(ok, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL: {message}")


def run(args, env=None, check=True):
    completed = subprocess.run(
        args,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        raise SystemExit(
            f"FAIL: command {args} rc={completed.returncode}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def load_reject_dup(path: Path):
    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate {key}")
            out[key] = value
        return out

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_hook)


def test_duplicate_json_keys():
    for name in ("CERTIFICATE.json", "SOURCES.json", "TASK.json", "VERIFY.json"):
        load_reject_dup(HERE / name)
    # Inject a duplicate key and require rejection.
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad.json"
        bad.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")
        try:
            load_reject_dup(bad)
            raise SystemExit("FAIL: duplicate key accepted")
        except ValueError:
            pass


def test_need_under_O():
    env = os.environ.copy()
    env["PYTHONOPTIMIZE"] = "1"
    # Corrupting CERTIFICATE must fail even under -O.
    cert = HERE / "CERTIFICATE.json"
    original = cert.read_bytes()
    try:
        data = json.loads(original)
        data["pattern_count"] = -1
        cert.write_bytes(json.dumps(data).encode())
        completed = run([PY, "-I", "-O", "-Werror", "-B", str(HERE / "verify.py")], env=env, check=False)
        need(completed.returncode != 0, "corrupt cert must fail under -O")
        need("FAIL" in completed.stderr or "FAIL" in completed.stdout, "FAIL marker")
    finally:
        cert.write_bytes(original)


def test_read_only_default():
    before = (HERE / "CERTIFICATE.json").read_bytes()
    run([PY, "-I", "-B", str(HERE / "verify.py")])
    after = (HERE / "CERTIFICATE.json").read_bytes()
    need(before == after, "default verify must not rewrite certificate")


def test_bound_mutants():
    sys.path.insert(0, str(HERE))
    from schedule import reversal_schedule, tensor_map_schedule

    rev = reversal_schedule([4, 3, 4, 3])
    need(rev["exchanges"] == 2, "d=4 reversal exchanges")
    # Mutant: claiming adjacent non-endpoint reversal uses more than floor(d/2).
    need(rev["exchanges"] <= rev["bound_exchanges"], "bound")
    ten = tensor_map_schedule([4, 3, 4])
    need(ten["exchanges"] == 4, "d=3 tensor exchanges")
    # Mutant schedule with an extra restore would exceed 2(d-1).
    need(ten["exchanges"] == ten["bound_exchanges"], "tensor sharp on d>1")


def test_nonadjacent_width_reject():
    sys.path.insert(0, str(HERE))
    from schedule import exchange_ops

    try:
        exchange_ops([3, 5], 0, 1)
        raise SystemExit("FAIL: non-adjacent widths accepted")
    except RuntimeError:
        pass


def main():
    groups = [
        ("duplicate_json_keys", test_duplicate_json_keys),
        ("read_only_default", test_read_only_default),
        ("need_under_O", test_need_under_O),
        ("bound_mutants", test_bound_mutants),
        ("nonadjacent_width_reject", test_nonadjacent_width_reject),
    ]
    for name, fn in groups:
        fn()
        print(f"PASS_GROUP {name}")
    print(f"PASS_PR2298_SECTION3_OPCOUNTS_PACKAGE_TESTS groups={len(groups)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
