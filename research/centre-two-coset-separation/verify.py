"""Corroborate two-coset separation, without replaying the cited block theorem.

Produced by Nick Petalas. SPDX-License-Identifier: Apache-2.0
"""
import argparse
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from linear import apply, need, rank  # noqa: E402
from reader import plane_certificate  # noqa: E402


def multiply(left, right):
    p, bit = left
    q, other = right
    return tuple(p[q[i]] for i in range(3)), bit ^ other


def fixture():
    identity = (0, 1, 2)
    group = [(p, b) for p in permutations(range(3)) for b in range(2)]
    even = [p for p in permutations(range(3))
            if sum(p[i] > p[j] for i in range(3) for j in range(i + 1, 3)) % 2 == 0]
    subgroup = {(p, 0) for p in even}
    odd = [p for p in permutations(range(3)) if p not in even]
    routes = [(p, 0) for p in odd] + [(identity, 1), (odd[0], 1)]
    cosets = sorted({tuple(sorted(multiply(t, h) for h in subgroup)) for t in group})
    rows = [[1, 1, 0, 0, 0], [1, 0, 1, 0, 0],
            [0, 0, 0, 1, 0], [0, 0, 0, 0, 1]]
    need(len(group) == 12 and len(cosets) == 4, "fixture group")
    need(all(multiply(r, r) == (identity, 0) for r in routes), "route involutions")
    images = [{multiply(h, r) for h in subgroup} for r in routes]
    need(images[0] == images[1] == images[2], "distinguished route class")
    need(len({tuple(sorted(s)) for s in images}) == 3, "two singleton classes")
    generator = multiply(routes[0], routes[1])
    need({(identity, 0), generator, multiply(generator, generator)} == subgroup,
         "triple products generate subgroup")
    for p, q in combinations(range(5), 2):
        need(rank([[row[p], row[q]] for row in rows]) == 2, "nonparallel columns")
    for p in (3, 4):
        need(rank([[row[0], row[1], row[p]] for row in rows]) == 3,
             "singleton outside triple plane")
    return group, routes, cosets, rows


def joint_matrix(group, routes, rows, owners, retained_outputs=None):
    variables = [(g, p) for g in sorted(owners) for p in range(5)]
    old = [[rows[k][p] if g == owner else 0 for g, p in variables]
           for owner in sorted(owners) for k in range(4)]
    outputs = group if retained_outputs is None else retained_outputs
    later = [[rows[k][p] if multiply(g, routes[p]) == output else 0
              for g, p in variables] for output in outputs for k in range(4)]
    return variables, old, later


def check_block(group, routes, cosets, rows, owners):
    variables, old, later = joint_matrix(group, routes, rows, owners)
    complete = [set(c) for c in cosets if set(c) <= owners]
    expected = len(complete)
    actual = len(variables) - rank(old + later)
    need(actual == expected, "complete-coset kernel dimension")
    witnesses = [[(1, -1, -1, 0, 0)[p] if g in c else 0 for g, p in variables]
                 for c in complete]
    need(rank(witnesses) == expected, "independent inherited directions")
    for witness in witnesses:
        need(not any(apply(old + later, witness)), "literal kernel witness")
    return actual


def finite_checks():
    group, routes, cosets, rows = fixture()
    full = []
    collision_types = set()
    for first, second in combinations(cosets, 2):
        owners = set(first) | set(second)
        full.append(check_block(group, routes, cosets, rows, owners))
        for output in group:
            counts = [sum(multiply(output, r) in c for r in routes)
                      for c in (set(first), set(second))]
            if all(counts):
                collision_types.add(tuple(sorted(counts)))
    need(full == [2] * 6, "all two-coset fixtures")
    need(collision_types == {(1, 1), (1, 3)}, "both mixed output-class cases")
    universe = sorted(set(cosets[0]) | set(cosets[1]))
    subset_dimensions = []
    for mask in range(1 << len(universe)):
        owners = {g for i, g in enumerate(universe) if mask >> i & 1}
        subset_dimensions.append(check_block(group, routes, cosets, rows, owners))
    return {"full_two_coset_systems": len(full), "subblocks": len(subset_dimensions),
            "subblock_dimension_histogram": {str(k): subset_dimensions.count(k)
                                            for k in sorted(set(subset_dimensions))},
            "collision_class_sizes": [list(t) for t in sorted(collision_types)]}


def controls():
    group, routes, cosets, rows = fixture()
    owners = set(cosets[0]) | set(cosets[1])
    checks = []
    for column in ([1, 2, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]):
        changed = [list(row) for row in rows]
        for i in range(4):
            changed[i][3] = column[i]
        examples = []
        for left, right in combinations(cosets, 2):
            block = set(left) | set(right)
            variables, old, later = joint_matrix(group, routes, changed, block)
            examples.append(len(variables) - rank(old + later))
        checks.append(max(examples))
    need(checks[0] > 2, "outside-plane premise is necessary")
    need(checks[1] > 2, "nonparallel premise is necessary")
    need(checks[2] > 2, "distinct singleton columns are necessary")
    variables, old, later = joint_matrix(group, routes, rows, owners, owners)
    dropped = len(variables) - rank(old + later)
    need(dropped > 2, "whole-output premise is necessary")
    return {"invalid_column_max_kernel_dimensions": checks,
            "source_only_output_kernel_dimension": dropped}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = {"status": "PASS_CENTRE_TWO_COSET_SEPARATION",
              "claim_type": "scoped proof with finite corroboration",
              "new_reader_plane_check": plane_certificate(HERE.parents[1]),
              "new_implication_fixtures": finite_checks(), "controls": controls(),
              "derived_full_source_consequence": {"owners": 8160, "kernel_dimension": 2,
                                                  "minimum_extra_linear_observations": 848638}}
    files = sorted(path for path in HERE.iterdir() if path.is_file())
    need(len(files) <= 16, "package file limit")
    result["package_sha256"] = {p.name: sha256(p.read_bytes()).hexdigest() for p in files}
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        need(args.receipt.is_absolute() and HERE not in args.receipt.parents,
             "receipt must be outside package")
        with args.receipt.open("x") as stream:
            need(stream.write(encoded) == len(encoded), "complete receipt write")
    print(encoded, end="")


if __name__ == "__main__":
    main()
