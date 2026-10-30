#!/usr/bin/env python3
"""Failure controls for the one-fiber axis-0 comparison."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load():
    spec = importlib.util.spec_from_file_location("axis0_fiber", HERE / "verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    module = load()
    report = module.receipt()
    if report["map"] != "U" or report["match_count"] != 1 or report["checker_called"]:
        raise SystemExit("FAIL: receipt")
    b2 = module.rebuild_b2()
    needle = module.axis0_u_program(b2, 0, 0)
    word = module.load_encoder(b2)
    start = report["match_offset"]
    if word[start : start + len(needle)] != needle:
        raise SystemExit("FAIL: slice drifted")
    # A column-shifted copy is a different fiber and is not this slice.
    shifted = module.axis0_u_program(b2, 0, 1)
    if module.find_slice(word[start : start + len(needle)], shifted):
        raise SystemExit("FAIL: column 1 program collided with column 0")
    if module.find_slice(word, shifted) == [start]:
        raise SystemExit("FAIL: column 1 occupied the column 0 offset")
    # Dropping the restoring doubles leaves a half-scale tail.
    truncated = needle[:-96]
    realized = module.interpret_axis0(truncated, 0, 0)
    tail = realized[8]
    if tail.get(8) != module.Fraction(1, 2):
        raise SystemExit("FAIL: truncated tail scale")
    print("PASS_P104_AXIS0_ENCODER_FIBER_TESTS " + json.dumps({"groups": 3, "new_kappa": False}))


if __name__ == "__main__":
    main()
