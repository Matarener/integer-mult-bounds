#!/usr/bin/env python3
"""Verify the constructive reduction and its retained finite dependencies."""

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from finite import replay
from model import diagonal, diagonal_target, direct_word, evaluate, require, short_words
from reduction import check_intertwining, compress

PACKAGE = Path(__file__).resolve().parent


def fixtures():
    result = [("central-tight", (0,) * 9 + (1, 0, 0), ())]
    for route in ("image", "quotient"):
        target = (0,) * 9 + (3, 5, 0)
        extra = []
        for a in (1, 4, 7):
            u, v = 1 << 9, (1 << 9) | (1 << a)
            if route == "quotient":
                u, v = v, u
            extra.extend([(u, v, 2)] * 4)
        result.append((route + "-discarded-dirt", target, tuple(extra)))
    result.append(("mixed-noncommuting", (6, 7, 0, 1, 0, 2), ()))
    result.append(("identity-empty", (0,) * 12, ()))
    return [
        (name, target, direct_word(target) + extra) for name, target, extra in result
    ]


def constructive_checks():
    receipts = []
    for name, target, word in fixtures():
        result = compress(word, target)
        check_intertwining(word, target, result)
        for route in ("image", "quotient"):
            forced = compress(word, target, route)
            check_intertwining(word, target, forced)
        receipts.append(
            {
                "name": name,
                "roles": len(target),
                "calls": len(word),
                "reduced_roles": len(result["target"]),
                "route": result["route"],
                "image_rank": result["image_rank"],
                "row_rank": result["row_rank"],
                "odd": result["odd"],
                "representatives": result["representatives"],
                "reduced_word": result["word"],
            }
        )
    words = successful = 0
    routes = {"image": 0, "quotient": 0}
    for r, word in short_words():
        words += 1
        target = diagonal_target(evaluate(word, r), r)
        if target is not None:
            result = compress(word, target)
            check_intertwining(word, target, result)
            successful += 1
            routes[result["route"]] += 1
    return {
        "fixtures": receipts,
        "words": words,
        "diagonal_words": successful,
        "auto_routes": routes,
    }


def corollaries():
    cases = []
    for active, bill in ((2, 6), (3, 7)):
        horizon = bill - 2
        roles = (horizon + active) // 2
        require(roles <= 4 and horizon % 2 == active % 2, "finite lifting boundary")
        cases.append(
            {
                "active_roles": active,
                "odd_targets": active,
                "direct_calls": bill,
                "shorter_parity_horizon": horizon,
                "compressed_roles_at_most": roles,
                "finite_certificate_roles": 4,
            }
        )
    return cases


def attainment():
    endpoints = omissions = 0
    for r in (2, 3, 4, 8, 12):
        for active in (2, 3):
            if active > r:
                continue
            for labels in product((2, 3, 4, 5), repeat=active):
                if sum(g in (3, 5) for g in labels) != 2:
                    continue
                target = (0,) * (r - active) + labels
                word = direct_word(target)
                require(evaluate(word, r) == diagonal(target), "direct attainment")
                for a in range(len(word)):
                    require(
                        evaluate(word[:a] + word[a + 1 :], r) != diagonal(target),
                        "omitted positive sign call accepted",
                    )
                    omissions += 1
                endpoints += 1
    return {"endpoints": endpoints, "omissions": omissions, "roles": [2, 3, 4, 8, 12]}


def science_sources():
    names = (
        "model.py",
        "reduction.py",
        "finite.py",
        "verify.py",
        "inputs/pr3471-search.cpp",
        "inputs/pr3471-RESULT.json",
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
        require(not args.write_result.exists(), "refuse receipt overwrite")
    with tempfile.TemporaryDirectory(prefix="q8-workspace-") as temporary:
        result = {
            "scope": "two-sided role reduction; unit-price pair/triple corollaries",
            "constructive": constructive_checks(),
            "corollaries": corollaries(),
            "attainment": attainment(),
            "finite": replay(Path(temporary)),
            "science_sources": science_sources(),
            "no_new_kappa": True,
        }
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.write_result is not None:
        with args.write_result.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
    else:
        require(
            encoded == (PACKAGE / "RESULT.json").read_text(), "exact receipt mismatch"
        )
    print(
        "PASS_Q8_WORKSPACE_REDUCTION pairs=6 two_negative_triples=7 "
        "arbitrary_dirty_roles no_new_kappa"
    )


if __name__ == "__main__":
    main()
