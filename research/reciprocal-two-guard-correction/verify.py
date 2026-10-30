"""Bounded exact checks of the new construction, not predecessor replays."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform

from reciprocal import MAX_TARGET, Result, evaluate, floor_grid

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArithmeticError(message)


def authenticate() -> dict[str, str]:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    hashes = {}
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "source digest: " + row["path"])
            hashes[row["path"]] = digest
    return hashes


def integer_oracle(c: Fraction, target: int) -> tuple[Fraction, list[Fraction]]:
    """Separate dyadic-significand traversal and division-based final oracle."""
    numerator, denominator = c.numerator, c.denominator
    x, stored = 5, 3
    values = []
    steps = (target - 2).bit_length() if target >= 2 else 0
    for index in range(steps + 1):
        bits = 6 if index == 0 else min((1 << index) + 1, target) + 2
        prefix = (numerator << bits) // denominator
        u = prefix * x // (1 << stored)
        x = x * ((2 << bits) - u) // (1 << stored)
        stored = bits
        values.append(Fraction(x, 1 << stored))
    scale = 1 << (target + 2)
    prefix = numerator * scale // denominator
    quotient, remainder = divmod(scale * scale, prefix)
    nearest = quotient + int(2 * remainder > prefix)
    return Fraction(nearest, scale), values


def check_result(c: Fraction, target: int, result: Result) -> None:
    oracle, stages = integer_oracle(c, target)
    require(result.value == oracle, "nearest-prefix inverse disagreement")
    require([r[2] for r in result.stages] == stages, "integer trace disagreement")
    require(1 <= result.candidates <= 13, "candidate count")
    require(abs(result.selected - result.center) <= 6, "correction radius")
    require(result.value == Fraction(result.selected, 1 << (target + 2)),
            "selected grid coordinate")
    scale = 1 << (target + 2)
    require(result.center == (result.stages[-1][2] * scale).__floor__(),
            "correction center")
    eligible = [j for j in range(result.center - 6, result.center + 7)
                if scale // 2 <= j <= scale]
    require(result.candidates == len(eligible), "enumerated candidate count")
    require(result.selected in eligible, "eligible selected coordinate")
    incoming, m = Fraction(5, 8), 2
    for index, (stage, bits, outgoing) in enumerate(result.stages):
        if index:
            m = min(2 * m - 1, target)
        require(stage == m and bits == (m + 2 if index else 6), "schedule")
        scale = 1 << bits
        prefix = Fraction(c.numerator * scale // c.denominator, scale)
        u = Fraction((prefix * incoming * scale).__floor__(), scale)
        raw = incoming * (2 - u)
        require(0 <= raw - outgoing < Fraction(1, scale), "output floor")
        require(0 <= prefix * incoming - u < Fraction(1, scale), "product floor")
        require(abs(1 - c * outgoing) < Fraction(1, 1 << m), "stage invariant")
        incoming = outgoing
    require(abs(1 - c * result.value) < Fraction(1, 1 << (target + 1)),
            "target residual")


def prefix_cells() -> dict[str, object]:
    counts = Counter()
    offsets = Counter()
    for target in range(1, 13):
        bits = max(6, target + 2)
        scale = 1 << bits
        bound = Fraction(1, 1 << (target + 1))
        for cell in range(scale, 2 * scale):
            low = Fraction(cell, scale)
            high = Fraction(cell + 1, scale)
            result = evaluate(low, target)
            check_result(low, target, result)
            # Prefixes are constant on [low,high); the residual is affine.
            require(abs(1 - high * result.value) <= bound, "open cell endpoint")
            counts[target] += 1
            offsets[result.selected - result.center] += 1
    return {"cells_by_target": dict(counts), "cells": sum(counts.values()),
            "selected_offsets": dict(sorted(offsets.items()))}


def large_cases() -> int:
    count = 0
    for target in (13, 15, 16, 17, 31, 32, 33, 63, 64, 65, 127, 128,
                   129, 255, 256, 257, 511, 512, 4096):
        for c in (Fraction(1), Fraction(3, 2), Fraction(127379, 65536),
                  2 - Fraction(1, 1 << (target + 4)),
                  1 + Fraction(1, 1 << (target + 4))):
            check_result(c, target, evaluate(c, target))
            count += 1
    return count


def rejection_controls() -> int:
    count = 0
    for c, target in ((Fraction(0), 3), (Fraction(2), 3), (Fraction(1), 0),
                      (Fraction(1), MAX_TARGET + 1), (Fraction(1), True),
                      (Fraction((1 << 16385) + 1, 1 << 16385), 3)):
        try:
            evaluate(c, target)
        except ValueError:
            count += 1
        else:
            raise ArithmeticError("accepted invalid input")
    for bits in (-1, MAX_TARGET + 3):
        try:
            floor_grid(Fraction(1), bits)
        except ValueError:
            count += 1
        else:
            raise ArithmeticError("accepted invalid grid")
    c, target = Fraction(127379, 65536), 15
    result = evaluate(c, target)
    mutants = (
        Result(result.value + Fraction(1, 2), result.stages, result.center,
               result.selected, result.candidates),
        Result(result.value, result.stages[:-1], result.center,
               result.selected, result.candidates),
        Result(result.value, result.stages, result.center + 20,
               result.selected, result.candidates),
        Result(result.value, result.stages, result.center, result.selected, 14),
    )
    for mutant in mutants:
        try:
            check_result(c, target, mutant)
        except ArithmeticError:
            count += 1
        else:
            raise ArithmeticError("accepted corrupt result")
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    sources = authenticate()
    cells = prefix_cells()
    large = large_cases()
    controls = rejection_controls()
    witness = evaluate(Fraction(127379, 65536), 15)
    residual = 1 - Fraction(127379, 65536) * witness.value
    result = {"status": "PASS_TWO_GUARD_RECIPROCAL", "python": platform.python_version(),
              **cells, "large_cases": large, "rejections": controls,
              "witness_output": str(witness.value), "witness_residual": str(residual),
              "sources": sources, "package_sha256": {
                  p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(PACKAGE.iterdir()) if p.is_file()}}
    if args.receipt:
        with args.receipt.open("x") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
