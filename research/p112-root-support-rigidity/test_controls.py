"""Threshold, receipt and actual source-boundary controls. Apache-2.0."""

import copy
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import common


def rejects(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError(message)


def threshold_controls():
    g, roots, _, labels = common.model()
    off = sum(1 << i for i, r in enumerate(roots) if g.dot(r, roots[0]))
    permutation = common.reflect(roots, roots[0], g.dot, g.canonical)
    receipt = common.read_json(common.HERE / "RESULT.json")
    for row in receipt["sections"]:
        mask = int(row["boundary_mask"], 16)
        common.require(
            (mask & off).bit_count() == row["threshold"] - 1,
            "actual sharp boundary size",
        )
        selected = [labels[i] for i in range(120) if mask >> i & 1]
        pivots = [0] * 9
        for value in selected:
            for bit in range(8, -1, -1):
                if value >> bit & 1:
                    if pivots[bit]:
                        value ^= pivots[bit]
                    else:
                        pivots[bit] = value
                        break
        common.require(
            sum(bool(x) for x in pivots) == row["dimension"],
            "boundary has declared binary dimension",
        )
        image = sum(1 << permutation[i] for i in range(120) if mask >> i & 1)
        common.require(image != mask, "boundary violates reflection closure")
        rejects(
            lambda mask=mask, capacity=row["capacity"]: common.section_check(
                mask, off, permutation, capacity
            ),
            "lowered threshold incorrectly accepted",
        )


def receipt_controls(directory):
    original = common.read_json(common.HERE / "RESULT.json")
    mutants = []
    changed = copy.deepcopy(original)
    changed["schema_version"] = True
    mutants.append(changed)
    changed = copy.deepcopy(original)
    changed["sections"][0]["critical_count"] -= 1
    mutants.append(changed)
    changed = copy.deepcopy(original)
    changed["support_budget"]["forced_large_piece_partners"] = 1
    mutants.append(changed)
    changed = copy.deepcopy(original)
    changed["caller"]["full_exclusion"] = True
    mutants.append(changed)
    for index, mutant in enumerate(mutants):
        path = directory / f"receipt-{index}.json"
        path.write_text(json.dumps(mutant) + "\n")
        process = subprocess.run(
            [
                sys.executable,
                "-O",
                "-W",
                "error",
                "-B",
                str(common.HERE / "verify.py"),
                "--receipt",
                str(path),
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        common.require(
            process.returncode != 0 and "exact typed result receipt" in process.stderr,
            "actual verifier must reject mutated receipt",
        )
    duplicate = directory / "duplicate.json"
    duplicate.write_text('{"schema_version":1,"schema_version":1}')
    rejects(lambda: common.read_json(duplicate), "duplicate JSON key accepted")
    return len(mutants)


def source_controls(directory):
    for name in common.PINS:
        target = directory / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((common.ROOT / name).read_bytes())
    common.model(directory)
    geometry = directory / common.GEOMETRY
    raw = geometry.read_bytes()
    geometry.write_bytes(raw + b"\n# altered source\n")
    rejects(lambda: common.model(directory), "altered geometry accepted")
    geometry.unlink()
    geometry.symlink_to(common.ROOT / common.GEOMETRY)
    rejects(lambda: common.model(directory), "linked geometry accepted")


def main():
    threshold_controls()
    with tempfile.TemporaryDirectory(
        prefix="p112-root-controls-", dir=os.environ.get("TMPDIR")
    ) as tmp:
        directory = Path(tmp)
        count = receipt_controls(directory)
        source_controls(directory / "source")
    print(
        f"PASS_P112_ROOT_SUPPORT_CONTROLS threshold_boundaries=2 cli_mutants={count} source_controls=2"
    )


if __name__ == "__main__":
    main()
