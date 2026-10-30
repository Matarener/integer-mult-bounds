"""Recompute the Q8 inverse-label tariff evidence. Standard library only."""

import argparse
import hashlib
import json
import sys
from importlib import import_module
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
m = import_module("model")

ROOT = HERE.parents[1]


def authenticate() -> dict:
    manifest_path = HERE / "SOURCES.json"
    m.require(manifest_path.stat().st_size < 64_000, "oversized source manifest")
    manifest = json.loads(manifest_path.read_bytes())
    m.require(len(manifest["files"]) <= 8, "too many source rows")
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            m.require(path.is_file() and not path.is_symlink(), "missing/linked source")
            m.require(path.stat().st_size <= 4_000_000, "oversized source")
            m.require(
                hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                "changed source",
            )
    return json.loads(
        (ROOT / "research/q8-inverse-label-pair-census/CERTIFICATE.json").read_bytes()
    )


def group_checks() -> int:
    for a, b, c in product(range(8), repeat=3):
        m.require(
            m.group(m.group(a, b), c) == m.group(a, m.group(b, c)),
            "group associativity",
        )
    for a, b in product(range(8), repeat=2):
        for selector in (204, 240, 60):
            lhs = (selector >> m.group(a, b)) & 1
            rhs = ((selector >> a) ^ (selector >> b)) & 1
            m.require(lhs == rhs, "parity homomorphism")
    m.require(m.group(2, 4) != m.group(4, 2), "noncommutative Q8")
    return 512


def attaining_checks(predecessor: dict) -> dict:
    digest = hashlib.sha256()
    cases = 0
    for elements in m.fixtures():
        for alpha, beta in product(range(5), repeat=2):
            word = m.witness(elements, alpha, beta)
            m.check_target(elements, word, alpha, beta)
            digest.update(
                bytes(elements) + bytes((alpha, beta, m.tariff(elements, alpha, beta)))
            )
            cases += 1
    names = ("p1", "m1", "pi", "mi", "pj", "mj", "pk", "mk")
    for a, b in product(range(8), repeat=2):
        old = predecessor["endpoints"][f"diag_{names[a]}_{names[b]}"]["inverse"]
        m.require(old["minimum"] == m.tariff((a, b), 1, 1), "predecessor pair minimum")
    return {
        "target_lists": len(m.fixtures()),
        "price_pairs": 25,
        "attaining_cases": cases,
        "digest": digest.hexdigest(),
        "predecessor_pairs": 64,
    }


def prefix_checks() -> dict:
    factors = tuple(
        (g, u, v) for g in m.LABELS for u, v in product(range(1, 4), repeat=2)
    )
    count = 0
    for word in product(factors, repeat=3):
        m.check_invariants(m.endpoint(2, word), word)
        count += 1
    factor_count = 0
    for roles in range(1, 6):
        for u, v in product(range(1, 1 << roles), repeat=2):
            for label in m.LABELS:
                word = ((label, u, v),)
                m.check_invariants(m.endpoint(roles, word), word)
                factor_count += 1
    return {
        "three_call_words": count,
        "all_rank_one_factors_roles_1_to_5": factor_count,
        "nilpotents_included": True,
    }


def controls() -> dict:
    failures = 0
    for elements in ((1, 6, 3), (7, 1, 5), tuple(range(8))):
        word = m.witness(elements, 1, 2)
        for index in range(len(word)):
            changed = word[:index] + word[index + 1 :]
            m.require(
                m.endpoint(len(elements), changed) != m.target(elements),
                "omission accepted",
            )
            failures += 1
    m.require(
        m.tariff((3,), 1, 1) == 1 and m.group(m.group(2, 2), 2) == 3,
        "positive-only price distinction",
    )
    m.require(m.tariff((1, 6), 1, 1) == 4, "overlapping first-order support")
    m.require(
        m.endpoint(2, ((2, 3, 2),)) != m.target((0, 2)), "dirty spectator ignored"
    )
    m.require(
        m.group(2, 2) == 1 and (1 << 1) != 1,
        "central group element confused with scalar",
    )
    m.require(
        (204 >> 0) & 1 == (204 >> 1) & 1 and (240 >> 0) & 1 == (240 >> 1) & 1,
        "quotient alias missing",
    )
    invalid = (
        (True, ()),
        (9, ()),
        (2, ((6, 1, 1),)),
        (2, ((2, 4, 1),)),
        (2, ((2, True, 1),)),
        (2, ((2, 1, 1),) * 49),
    )
    for roles, word in invalid:
        try:
            m.endpoint(roles, word)
        except ValueError:
            continue
        raise ValueError("invalid domain accepted")
    return {
        "single_omissions": failures,
        "hypothesis_controls": 5,
        "invalid_domains": len(invalid),
    }


def build() -> dict:
    predecessor = authenticate()
    return {
        "status": "PASS_Q8_INVERSE_UNIFORM_TARIFF",
        "group_associativity_triples": group_checks(),
        "attainment": attaining_checks(predecessor),
        "prefixes": prefix_checks(),
        "controls": controls(),
        "new_kappa": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write", type=Path, help="write a new receipt, refusing overwrite"
    )
    args = parser.parse_args()
    result = build()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        m.require((HERE / "RESULT.json").stat().st_size < 100_000, "oversized result")
        expected = json.loads((HERE / "RESULT.json").read_bytes())
        m.require(
            json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "result receipt differs",
        )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
