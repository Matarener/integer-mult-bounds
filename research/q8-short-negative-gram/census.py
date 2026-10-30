"""Complete length-three/five Gram census, without a solver. Apache-2.0."""

import hashlib
import json
from pathlib import Path

from algebra import (combinations, endpoint, first_order, grams, labels, rank,
                     require, target)


def census(n):
    require(n in (3, 5), "only exact lengths three and five are registered")
    shapes = ((3, 0), (2, 1))
    masks = {shape: labels(n, *shape) for shape in shapes}
    rows = {str(shape): {"label_lists": len(masks[shape]), "first_order": 0,
                         "accepted": 0} for shape in shapes}
    streams = {shape: hashlib.sha256() for shape in shapes}
    matrices = spectral = 0
    for a in grams(n):
        matrices += 1
        sums = combinations(a)
        square = tuple(sums[row] for row in a)
        if tuple(sums[row] for row in square) != square or rank(square) != 3:
            continue
        spectral += 1
        for shape in shapes:
            rec = rows[str(shape)]
            for mask in masks[shape]:
                projections = first_order(a, mask, *shape, table=sums)
                if projections is None:
                    continue
                rec["first_order"] += 1
                actual = endpoint(a, mask)
                wanted = target(a, *projections)
                accepted = actual == wanted
                rec["accepted"] += int(accepted)
                packet = [list(a), mask, [list(part) for part in actual], accepted]
                streams[shape].update(json.dumps(packet, separators=(",", ":")).encode() + b"\n")
    require(matrices == 1 << (n * (n - 1)), "incomplete Gram enumeration")
    for shape in shapes:
        rows[str(shape)]["stream_sha256"] = streams[shape].hexdigest()
    return {"calls": n, "diagonal_one_matrices": matrices,
            "rank_three_spectral_matrices": spectral, "shapes": rows}


def source_hashes():
    root = Path(__file__).resolve().parent
    names = ("algebra.py", "census.py", "oracle.py", "controls.py", "verify.py", "test_package.py",
             "PROOF.md", "inputs/pr3517-PROOF.md", "inputs/RETENTION.json")
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
