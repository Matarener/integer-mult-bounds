"""Reconstruct the fixed E6 witness by a bounded exact search. Apache-2.0."""

import argparse
import json
from itertools import combinations, product
from math import gcd
from pathlib import Path

from verify import HERE, ROOT, model, read_json, require


def local_coordinates(values):
    rows = []
    for value in values:
        for row in rows:
            value = min(value, value ^ row)
        if value:
            rows = sorted(rows + [value], reverse=True)
    require(len(rows) == 7, "large A2 fiber spans seven bits")
    mapping = {0: 0}
    for j, row in enumerate(rows):
        mapping.update({x ^ row: y ^ (1 << j) for x, y in list(mapping.items())})
    require(len(mapping) == 128, "seven-space coordinate inventory")
    return mapping


def annihilators(codimension):
    require(codimension in (1, 2), "bounded seven-space subspaces")
    for pivots in combinations(range(7), codimension):
        choices = []
        for pivot in pivots:
            free = tuple(i for i in range(pivot) if i not in pivots)
            choices.append(
                tuple(
                    (1 << pivot)
                    | sum(((code >> j) & 1) << i for j, i in enumerate(free))
                    for code in range(1 << len(free))
                )
            )
        yield from product(*choices)


def section(fiber, labels, live, rank, size):
    mapping = local_coordinates([labels[i] for i in fiber])
    for rows in annihilators(7 - rank):
        support = [
            i
            for i in fiber
            if i in live
            and all(not (mapping[labels[i]] & row).bit_count() % 2 for row in rows)
        ]
        if len(support) == size:
            return support
    raise ValueError("fixed-plane search exhausted without required section")


def construct():
    roots, labels, live = model()
    normals = [2, 13]
    evaluations = [
        tuple(sum(x * y for x, y in zip(r, roots[n], strict=True)) for n in normals)
        for r in roots
    ]
    groups = {}
    for i, (x, y) in enumerate(evaluations):
        divisor = gcd(x, y)
        key = (
            max((x // divisor, y // divisor), (-x // divisor, -y // divisor))
            if divisor
            else (0, 0)
        )
        groups.setdefault(key, []).append(i)
    large = sorted((key, fiber) for key, fiber in groups.items() if len(fiber) == 27)
    require(len(large) == 3, "three large A2 fibers")
    pieces = []
    for (column, fiber), rank, size in zip(large, (5, 6, 6), (10, 16, 16), strict=True):
        support = section(fiber, labels, live, rank, size)
        coordinate = 0 if column[0] else 1
        values = [evaluations[i][coordinate] for i in support]
        pieces.append(
            {
                "support_full_indices": support,
                "values": values,
                "coefficient_column": list(column),
            }
        )
    retained = {i for piece in pieces for i in piece["support_full_indices"]}
    union = {i for i in live if any(evaluations[i])}
    return {
        "schema_version": 1,
        "normal_full_indices": normals,
        "cut_full_indices": sorted(union - retained),
        "pieces": pieces,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    witness = construct()
    if args.output is None:
        require(
            witness == read_json(HERE / "WITNESS.json"),
            "deterministic witness reconstruction",
        )
    else:
        require(not args.output.resolve().is_relative_to(ROOT), "external output only")
        args.output.write_text(json.dumps(witness, indent=2, sort_keys=True) + "\n")
    print("PASS_FIXED_PLANE_WITNESS_RECONSTRUCTION")


if __name__ == "__main__":
    main()
