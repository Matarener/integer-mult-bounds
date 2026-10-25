#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Optional bounded numerical discovery; the exact verifier needs no solver.

Requires scipy==1.18.1 and numpy==2.5.4. Write only to --output, outside
the package. A timeout supplies no impossibility or optimality certificate.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_matrix
from verify import labels_from_source

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def enumerate_frames(labels):
    neighbours = [sum(1 << j for j in range(112)
                      if i != j and (labels[i] & labels[j]).bit_count() % 2 == 0)
                  for i in range(112)]
    frames = []
    stack = [((), (1 << 112) - 1)]
    # Complete for this fixed authenticated source. The explicit node budget
    # fails closed if the source/model or traversal changes unexpectedly.
    for _ in range(1_000_000):
        if not stack:
            if len(frames) != 4032:
                raise ValueError("frame census changed")
            return frames
        chosen, candidates = stack.pop()
        if len(chosen) == 8:
            frames.append(chosen)
            continue
        for _ in range(candidates.bit_count()):
            bit = candidates & -candidates
            candidates -= bit
            port = bit.bit_length() - 1
            if candidates.bit_count() + len(chosen) + 1 >= 8:
                stack.append(((*chosen, port), candidates & neighbours[port]))
    raise ValueError("enumeration node budget exhausted")


def search(frames):
    rows = np.array([i for frame in frames for i in frame], dtype=np.int32)
    columns = np.repeat(np.arange(len(frames), dtype=np.int32), 8)
    matrix = csc_matrix((np.ones(len(rows)), (rows, columns)), shape=(112, len(frames)))
    result = milp(-np.ones(len(frames)), integrality=np.ones(len(frames)),
                  bounds=Bounds(0, 1), constraints=LinearConstraint(matrix, 0, 1),
                  options={"time_limit": 180, "mip_rel_gap": 0})
    if result.x is None:
        raise ValueError("solver returned no candidate")
    selected = [list(frame) for frame, value in zip(frames, result.x, strict=True) if value > 0.5]
    return {"frames": selected, "solver_message": result.message,
            "warning": "Numerical candidate only; check disjointness and every Gram entry exactly."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    output = arguments.output.resolve()
    if output.is_relative_to(HERE) or output.exists():
        raise ValueError("output must be a new file outside this package")
    source = ROOT / "research/adaptive-kernel-demotion/inputs/DATA-PHASES.json"
    if source.stat().st_size > 4_000_000:
        raise ValueError("source size limit")
    labels = labels_from_source(source.read_bytes())
    result = search(enumerate_frames(labels))
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2) + "\n")
    print("NUMERICAL_FRAME_CANDIDATE count=" + str(len(result["frames"])))


if __name__ == "__main__":
    main()
