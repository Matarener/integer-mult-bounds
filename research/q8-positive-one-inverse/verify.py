#!/usr/bin/env python3
"""Recompute the one-inverse Q8 receipt. Nick Petalas. Apache-2.0."""

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import model  # noqa: E402
import regular  # noqa: E402


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    root = PACKAGE.parents[1]
    checked = 0
    for row in manifest["files"]:
        if row["usage"] == "input":
            raw = (root / row["path"]).read_bytes()
            model.require(sha256(raw).hexdigest() == row["sha256"], "source changed")
            checked += 1
    for row in manifest["vendored_inputs"]:
        raw = (PACKAGE / row["path"]).read_bytes()
        model.require(
            sha256(raw).hexdigest() == row["sha256"], "retained proof changed"
        )
        checked += 1
    return checked


def check_word(word, targets):
    roles = len(targets)
    matrix = model.evaluate(word, roles)
    model.require(matrix == model.endpoint(targets), "wrong full formal endpoint")
    actual = regular.columns(word, roles)
    expected = regular.formal_columns(model.endpoint(targets), roles)
    model.require(actual == expected, "wrong regular dirty-input endpoint")
    return roles * 8


def fixture_checks():
    prices = (
        (0, 0),
        (0, 3),
        (3, 0),
        (1, 1),
        (2, 5),
        (5, 2),
        (Fraction(1, 3), Fraction(2, 7)),
    )
    lists = cases = columns = omissions = 0
    digest = sha256()
    for width in range(1, 5):
        for targets in product((0, 2, 3, 4, 5), repeat=width):
            if sum(g in (3, 5) for g in targets) > 1:
                continue
            lists += 1
            for alpha, beta in prices:
                word = model.construction(targets, alpha, beta)
                bill = sum(alpha if g == 2 else beta for g, _, _ in word)
                model.require(
                    bill == model.tariff(targets, alpha, beta), "tariff mismatch"
                )
                columns += check_word(word, targets)
                cases += 1
                digest.update(repr((targets, str(alpha), str(beta), word)).encode())
            # Delete an actual paid factor at every position, even at zero price.
            for a in range(len(word)):
                model.require(
                    model.evaluate(word[:a] + word[a + 1 :], width)
                    != model.endpoint(targets),
                    "omission accepted",
                )
                omissions += 1
    return {
        "target_lists": lists,
        "priced_cases": cases,
        "regular_columns": columns,
        "omission_controls": omissions,
        "construction_sha256": digest.hexdigest(),
    }


def mixed_controls():
    checked = columns = 0
    for roles in range(2, 9):
        # Invertible binary mixing sends a=e0 to u=e0+e1; v=e0 stays fixed.
        # Conjugate every factor of an attaining word, then compare both engines.
        targets = (3, 4) + (0,) * (roles - 2)
        original = model.construction(targets, 2, 5)
        mixed = tuple(
            (g, u ^ ((u & 1) << 1), v ^ ((v >> 1) & 1)) for g, u, v in original
        )
        matrix = model.evaluate(mixed, roles)
        model.require(
            regular.columns(mixed, roles) == regular.formal_columns(matrix, roles),
            "mixed noncommuting engines disagree",
        )
        model.require(matrix != model.endpoint(targets), "dirty mixing fault escaped")
        columns += roles * 8
        # Noncommuting paid identity spur touches a spectator when roles>=3.
        last = 1 << (roles - 1)
        first = (2, 1 | last, 1)
        second = (4, last, last)
        spur = (first,) + (second,) * 4 + (first,) * 3
        columns += check_word(spur + original, targets)
        checked += 2
    # The first-order quotient erases the sign. This is a deliberately wrong bill.
    model.require(
        model.evaluate(((2, 1, 1),), 1) != model.endpoint((3,)),
        "positive and negative generator identified",
    )
    return {
        "mixed_words": checked,
        "regular_columns": columns,
        "quotient_only_false_positive_rejected": True,
    }


def compute():
    sources = authenticate()
    for a, b, c in product(range(8), repeat=3):
        model.require(
            model.group_mul(model.group_mul(a, b), c)
            == model.group_mul(a, model.group_mul(b, c)),
            "Q8 associativity",
        )
    for a, b in product(range(8), repeat=2):
        expected = regular.multiply(regular.QUATERNIONS[a], regular.QUATERNIONS[b])
        model.require(
            regular.QUATERNIONS[model.group_mul(a, b)] == expected,
            "Hamilton multiplication mismatch",
        )
        for selected in ((2, 3, 4, 5), (2, 3, 6, 7), (4, 5, 6, 7)):
            model.require(
                (model.group_mul(a, b) in selected)
                == ((a in selected) ^ (b in selected)),
                "character is not additive",
            )
    return {
        "schema_version": 1,
        "status": "PASS_Q8_POSITIVE_ONE_INVERSE",
        "sources": sources,
        "associativity_triples": 512,
        "character_checks": 192,
        "saturation_census": model.exhaustive_saturation(),
        "attainment": fixture_checks(),
        "controls": mixed_controls(),
        "claim": (
            "Exact positive-label tariff for at most one negative generator target"
        ),
        "universal_evidence": (
            "PROOF.md; finite replay corroborates only its stated domain"
        ),
        "new_kappa": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = compute()
    raw = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        with args.write.open("x") as output:
            output.write(raw)
    else:
        # Canonical JSON comparison distinguishes true, 1 and 1.0.
        expected = json.loads((PACKAGE / "RESULT.json").read_text())
        model.require(
            json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "receipt differs",
        )
    print(result["status"])


if __name__ == "__main__":
    main()
