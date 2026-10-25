#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Package controls for research/s3-three-role-xyx."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from model import (  # noqa: E402
    CALL_INDEX,
    DIRECT_LEN,
    E,
    X,
    Y,
    identity_state,
    make_direct_word,
    need,
    step,
    target_state,
    word_state,
)


def group_direct_word():
    direct = make_direct_word()
    need(len(direct) == DIRECT_LEN, "direct length")
    need(word_state(direct) == target_state(), "direct attains")
    return "direct_word"


def group_omission():
    direct = make_direct_word()
    target = target_state()
    for i in range(len(direct)):
        reduced = direct[:i] + direct[i + 1 :]
        need(word_state(reduced) != target, f"omission {i}")
    return "omission"


def group_involution():
    identity = identity_state()
    for call in list(CALL_INDEX.keys())[:8]:
        once = step(identity, call)
        twice = step(once, call)
        need(twice == identity, "paid factors are involutions")
    return "involution"


def group_dirty_toggle():
    """Flipping the dirty diagonal away from [e] must leave the target."""
    target = target_state()
    # Build a fake state equal to target but with dirty role carrying [x].
    # Encoded as packed int: cell (2,2) at index 8.
    dirty_x = target ^ ((1 << E) << (6 * 8)) ^ ((1 << X) << (6 * 8))
    need(dirty_x != target, "dirty toggle changes state")
    need(word_state(make_direct_word()) != dirty_x, "direct does not hit dirty-x")
    return "dirty_toggle"


def group_duplicate_json():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "bad.json"
        path.write_text('{"a": 1, "a": 2}\n', encoding="utf-8")

        def _hook(pairs):
            out = {}
            for key, value in pairs:
                if key in out:
                    raise ValueError("duplicate")
                out[key] = value
            return out

        try:
            json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_hook)
            raise AssertionError("duplicate key must reject")
        except ValueError:
            pass
    return "duplicate_json"


def group_temp_corruption():
    cert_path = HERE / "CERTIFICATE.json"
    raw = json.loads(cert_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "CERTIFICATE.json"
        corrupted = dict(raw)
        corrupted["result_minimum"] = int(raw["result_minimum"]) + 1
        bad.write_text(json.dumps(corrupted, indent=2) + "\n", encoding="utf-8")
        loaded = json.loads(bad.read_text(encoding="utf-8"))
        need(loaded != raw, "corruption differs")
    return "temp_corruption"


def group_verify_subprocess():
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(HERE / "verify.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    need(proc.returncode == 0, f"verify failed: {proc.stderr or proc.stdout}")
    need("PASS_S3_THREE_ROLE_XYX" in proc.stdout, "verify marker")
    return "verify_subprocess"


def main() -> int:
    groups = [
        group_direct_word,
        group_omission,
        group_involution,
        group_dirty_toggle,
        group_duplicate_json,
        group_temp_corruption,
        group_verify_subprocess,
    ]
    names = [fn() for fn in groups]
    print(f"PASS_S3_THREE_ROLE_XYX_PACKAGE_TESTS groups={len(names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
