#!/usr/bin/env python3
"""Replay retained unit minima and check the new count/price completion."""

import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle
import tariff

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parent
        / "inputs/pr3487/research/q8-workspace-reduction"
    ),
)
import model

PACKAGE = Path(__file__).resolve().parent
PREDECESSOR = PACKAGE / "inputs/pr3487/research/q8-workspace-reduction"


def retained_sources():
    rows = json.loads((PACKAGE / "inputs/RETENTION.json").read_text())
    tariff.require(len(rows) == 18, "retained inventory count")
    wanted = set()
    for row in rows:
        name = row["retained_path"]
        path = PACKAGE / name
        tariff.require(
            name.startswith("inputs/pr3487/") and ".." not in Path(name).parts,
            "retained path",
        )
        tariff.require(
            path.is_file() and not path.is_symlink(), "retained regular file"
        )
        tariff.require(
            hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
            "retained source drift",
        )
        wanted.add(path.relative_to(PACKAGE).as_posix())
    actual = {
        p.relative_to(PACKAGE).as_posix()
        for p in (PACKAGE / "inputs/pr3487").rglob("*")
        if p.is_file()
    }
    tariff.require(wanted == actual, "retained inventory equality")
    return len(rows)


def targets():
    result = set()
    for active in (2, 3):
        for labels in product((2, 3, 4, 5), repeat=active):
            if sum(g in (3, 5) for g in labels) != 2:
                continue
            for roles in (2, 3, 4, 8, 12):
                if roles >= active:
                    for positions in (
                        tuple(range(active)),
                        tuple(range(roles - active, roles)),
                    ):
                        target = [0] * roles
                        for position, label in zip(positions, labels, strict=True):
                            target[position] = label
                        result.add(tuple(target))
    result.update(product((3, 5), repeat=3))
    return tuple(sorted(result))


def check_witness(target, word, count_pair):
    tariff.require(tariff.counts(word) == count_pair, "witness counts")
    tariff.require(
        model.evaluate(word, len(target)) == model.diagonal(target), "formal endpoint"
    )
    tariff.require(
        oracle.columns(word, target) == oracle.expected(target), "all dirty columns"
    )


def oracle_table():
    for a, b in product(range(8), repeat=2):
        tariff.require(
            oracle.multiply(a, b) == model.GROUP[a][b], "independent group table"
        )
    return 64


def attaining():
    endpoints = words = dirty_columns = omissions = prices_checked = 0
    price_list = (
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
        (1, 2),
        (2, 1),
        (1, 100),
        (100, 1),
        (Fraction(1, 13), Fraction(7, 17)),
        (Fraction(7, 17), Fraction(1, 13)),
    )
    for target in targets():
        endpoints += 1
        for a, count_pair in enumerate(tariff.frontier(target)):
            word = tariff.witness(target, a)
            check_witness(target, word, count_pair)
            dirty_columns += 8 * len(target)
            words += 1
            for offset in range(len(word)):
                changed = word[:offset] + word[offset + 1 :]
                tariff.require(
                    oracle.columns(changed, target) != oracle.expected(target),
                    "deleted call accepted",
                )
                omissions += 1
        for alpha, beta in price_list:
            word = tariff.optimal_word(target, alpha, beta)
            ni, nj = tariff.counts(word)
            actual = alpha * ni + beta * nj
            bound = tariff.minimum(target, alpha, beta)
            tariff.require(actual == bound, "optimal producer price")
            tariff.require(
                bound
                == min(alpha * ni + beta * nj for ni, nj in tariff.frontier(target)),
                "frontier price minimum",
            )
            check_witness(target, word, (ni, nj))
            dirty_columns += 8 * len(target)
            prices_checked += 1
    return dict(
        endpoints=endpoints,
        frontier_words=words,
        price_cases=prices_checked,
        dirty_columns=dirty_columns,
        omissions=omissions,
    )


def count_completion():
    checked = 0
    for target in targets():
        si, sj, negative = tariff.parameters(target)
        for a, b in product(range(17), repeat=2):
            if a + b >= negative:
                pair = si + 2 * a, sj + 2 * b
                selected = tariff.dominated(target, pair)
                tariff.require(
                    selected in tariff.frontier(target)
                    and selected[0] <= pair[0]
                    and selected[1] <= pair[1],
                    "count completion",
                )
                checked += 1
    return {
        "bounded_excess_pairs": checked,
        "maximum_excess_per_class": 32,
        "scope": "integer corroboration of the written unbounded domination proof",
    }


def first_order():
    checked = 0
    for roles, word in model.short_words():
        matrix = model.evaluate(word, roles)
        for label, support in ((2, (2, 3, 6, 7)), (4, (4, 5, 6, 7))):
            expected = [0] * (roles * roles)
            for u, v, g in word:
                if g == label:
                    for a, b in product(range(roles), repeat=2):
                        expected[a * roles + b] ^= u >> a & v >> b & 1
            actual = [sum(value >> h & 1 for h in support) % 2 for value in matrix]
            tariff.require(actual == expected, "first-order label equation")
            trace = sum(actual[a * roles + a] for a in range(roles)) % 2
            tariff.require(
                trace == sum(g == label for _, _, g in word) % 2, "label trace"
            )
        checked += 1
    return {"words": checked, "label_equations": 2 * checked}


def generic_dirty():
    words = columns = 0
    for roles, word in model.short_words():
        if roles < 2:
            continue
        matrix = model.evaluate(word, roles)
        expected = []
        for source, h in product(range(roles), range(8)):
            state = 0
            for destination, g in product(range(roles), range(8)):
                if matrix[destination * roles + source] >> g & 1:
                    state ^= 1 << (8 * destination + model.GROUP[g][h])
            expected.append(state)
        tariff.require(
            oracle.columns(word, (0,) * roles) == tuple(expected),
            "generic faithful action",
        )
        words += 1
        columns += 8 * roles
    return {"words": words, "dirty_columns": columns}


def predecessor():
    command = [
        sys.executable,
        "-I",
        "-O",
        "-Werror",
        "-B",
        str(PREDECESSOR / "verify.py"),
    ]
    done = subprocess.run(
        command, check=True, capture_output=True, text=True, timeout=480
    )
    tariff.require(
        "PASS_Q8_WORKSPACE_REDUCTION" in done.stdout, "predecessor replay marker"
    )
    receipt = json.loads((PREDECESSOR / "RESULT.json").read_text())
    finite = receipt["finite"]
    tariff.require(
        [r["tag"] for r in finite["search"]] == ["r4-two", "r4-pair"], "unit source"
    )
    original = json.loads((PREDECESSOR / "inputs/pr3471-RESULT.json").read_text())
    three = [r for r in original["search"] if r["tag"] == "r3-three"]
    tariff.require(
        len(three) == 1 and three[0]["hits"] == [0, 0], "three-role exclusion"
    )
    return {
        "stdout": done.stdout,
        "finite": finite,
        "three_negative_three_roles": three[0],
    }


def source_hashes():
    names = (
        "tariff.py",
        "oracle.py",
        "verify.py",
        "test_package.py",
        "PROOF.md",
        "inputs/RETENTION.json",
    )
    return {
        name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
        for name in names
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    if args.write_result is not None:
        tariff.require(not args.write_result.exists(), "refuse receipt overwrite")
    result = {
        "retained_files": retained_sources(),
        "group_products": oracle_table(),
        "first_order": first_order(),
        "generic_dirty": generic_dirty(),
        "attaining": attaining(),
        "count_completion": count_completion(),
        "predecessor": predecessor(),
        "science_sources": source_hashes(),
        "no_new_kappa": True,
    }
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write_result is None:
        tariff.require(
            encoded == (PACKAGE / "RESULT.json").read_text(), "exact receipt mismatch"
        )
    else:
        with args.write_result.open("x", encoding="utf-8") as output:
            output.write(encoded)
    print(
        "PASS_Q8_COUNT_FRONTIERS two_negative_any_finite_dirt three_negative_exactly_three_roles"
    )


if __name__ == "__main__":
    main()
