#!/usr/bin/env python3
"""Read-only verifier for composite-modulus antidiagonal rigidity."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from algebra import (  # noqa: E402
    KAPPA_DECIMAL,
    KAPPA_FRACTION,
    bank_formulas_match,
    exhaustive_goods,
    nontrivial_from_split,
    prove_pm1,
    prove_supports,
    split_from_nontrivial,
    weight_list,
    need,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"
PIN = "bb4bccbf42844d2801487450727c2f63e10d1d0f"


def repo_root() -> Path:
    for candidate in [HERE, *HERE.parents]:
        if (candidate / "scripts" / "research_package.py").is_file():
            return candidate
    raise SystemExit("FAIL: repo root")


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise SystemExit(f"FAIL: duplicate JSON key {key!r} in {path}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=hook)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_source_pins(root: Path) -> None:
    sources = load_json_reject_duplicates(SOURCES_PATH)
    need(sources["base_commit"] == PIN, "base_commit pin")
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        live = root / rec["path"]
        need(live.is_file(), f"missing input {rec['path']}")
        need(sha256_file(live) == rec["sha256"], f"source bytes mismatch: {rec['path']}")


def check_kappa(root: Path) -> None:
    selected = load_json_reject_duplicates(root / "certificates" / "selected-result.json")
    need(selected["decimal"] == KAPPA_DECIMAL, "selected decimal kappa")
    need(selected["kappa"] == KAPPA_FRACTION, "selected rational kappa")


def prime_power_control(p: int, k: int) -> dict:
    modulus = p**k
    kinds = {prove_pm1(p, k, x) for x in range(modulus) if (x * x - 1) % modulus == 0}
    need(kinds == {"+1", "-1"}, f"p^k={modulus} solutions {kinds}")
    # Precision-blind prime-power end is not ±1, so single-factor stays blocked.
    a0 = (1 + p ** (k - 1)) % modulus
    middles = tuple(1 for _ in range(3))
    proved = prove_supports(weight_list(a0, middles, modulus), modulus)
    need(proved["single_factor"] is False, f"{p}^{k} single-factor")
    bank_formulas_match(weight_list(a0, middles, modulus), modulus)
    return {
        "p": p,
        "k": k,
        "modulus": modulus,
        "square_one_kinds": sorted(kinds),
        "a0": a0,
        "single_factor": False,
        "good_supports": proved["good_supports"],
    }


def composite_witness(part1: int, part2: int, n: int, middles: tuple[int, ...], brute: bool) -> dict:
    modulus, a0 = nontrivial_from_split(part1, part2)
    need(n == len(middles) + 2, "middle length")
    weights = weight_list(a0, middles, modulus)
    proved = prove_supports(weights, modulus)
    need(proved["single_factor"] is True, "CRT a0 is a single-factor")
    split = split_from_nontrivial(modulus, a0)
    need(split == (part1, part2), f"split recovered {split} != {(part1, part2)}")
    bank_formulas_match(weights, modulus)
    if brute:
        need(exhaustive_goods(weights, modulus) == [(0, n - 1), (n - 1, 0)],
             "brute control")
    return {
        "part1": part1,
        "part2": part2,
        "modulus": modulus,
        "n": n,
        "a0": a0,
        "middles": [m % modulus for m in middles],
        "single_factor": True,
        "good_supports": proved["good_supports"],
        "recovered_split": list(split),
    }


def defect_witness(modulus: int, a0: int, middles: tuple[int, ...], brute: bool) -> dict:
    """Unit a0 with a0²≢1 still has exactly the two ends and no single factor."""
    weights = weight_list(a0, middles, modulus)
    proved = prove_supports(weights, modulus)
    need(proved["single_factor"] is False, "non-square defect")
    need((a0 * a0) % modulus != 1, "a0^2")
    n = proved["n"]
    bank_formulas_match(weights, modulus)
    if brute:
        need(exhaustive_goods(weights, modulus) == [(0, n - 1), (n - 1, 0)],
             "brute defect control")
    return {
        "modulus": modulus,
        "n": n,
        "a0": proved["a0"],
        "a0_square": proved["a0_square"],
        "middles": [m % modulus for m in middles],
        "single_factor": False,
        "good_supports": proved["good_supports"],
    }


def illegal_witness(modulus: int, a0: int, middles: tuple[int, ...], brute: bool) -> dict:
    weights = weight_list(a0, middles, modulus)
    proved = prove_supports(weights, modulus)
    need(proved["good_supports"] == [], "illegal zero")
    n = len(weights)
    if brute:
        need(exhaustive_goods(weights, modulus) == [], "brute illegal")
    return {
        "modulus": modulus,
        "n": n,
        "a0": a0 % modulus,
        "middles": [m % modulus for m in middles],
        "good_supports": [],
    }


def build_certificate() -> dict:
    prime_powers = [
        prime_power_control(3, 2),
        prime_power_control(3, 3),
        prime_power_control(5, 2),
        prime_power_control(7, 2),
        prime_power_control(11, 2),
    ]
    composites = [
        composite_witness(3, 5, 5, (1, 1, 1), True),
        composite_witness(3, 7, 5, (1, -1, 1), True),
        composite_witness(9, 5, 5, (1, 1, 1), True),
        composite_witness(3, 5, 3, (1,), True),
        composite_witness(5, 7, 3, (-1,), True),
        composite_witness(3, 35, 7, (1, 1, 1, 1, 1), True),
        composite_witness(15, 7, 9, (1, -1, 1, -1, 1, -1, 1), False),
    ]
    defects = [
        defect_witness(15, 2, (1, -1, 1), True),
        defect_witness(21, 2, (1, 1, 1), True),
        defect_witness(35, 3, (1,), True),
        defect_witness(45, 2, (1, 1, 1), False),
    ]
    illegals = [
        illegal_witness(15, 4, (1, 1, -1), True),
        illegal_witness(21, 8, (1, 1, -1), True),
        illegal_witness(9, 4, (-1, 1, 1), True),
    ]
    return {
        "schema_version": 1,
        "claim": (
            "On every odd modulus, precision-blind dual scales are exactly "
            "the two antidiagonal ends when middles are reciprocal, and a "
            "shared single-factor scale exists iff a0^2=1, which is possible "
            "outside ±1 iff the modulus is not a prime power."
        ),
        "prime_power_controls": prime_powers,
        "composite_single_factor_witnesses": composites,
        "non_square_defect_witnesses": defects,
        "illegal_middle_witnesses": illegals,
        "prime_power_grid_reprinted": False,
        "boolean_meters": False,
        "n2_census_reprinted": False,
        "kappa_unchanged": KAPPA_DECIMAL,
        "no_new_kappa": True,
    }


def compare_certificate(fresh: dict, committed: dict) -> None:
    need(fresh == committed, "committed certificate drifted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true",
                        help="regenerate CERTIFICATE.json (explicit write only)")
    args = parser.parse_args()
    root = repo_root()
    check_source_pins(root)
    check_kappa(root)
    fresh = build_certificate()
    if args.write:
        CERT_PATH.write_text(json.dumps(fresh, indent=2) + "\n", encoding="utf-8")
        print("WROTE_CERTIFICATE", CERT_PATH)
    need(CERT_PATH.is_file(), "missing CERTIFICATE.json")
    committed = load_json_reject_duplicates(CERT_PATH)
    compare_certificate(fresh, committed)
    print(
        "PASS_PRECISION_BLIND_COMPOSITE_RIGIDITY",
        f"composites={len(fresh['composite_single_factor_witnesses'])}",
        f"defects={len(fresh['non_square_defect_witnesses'])}",
        f"illegals={len(fresh['illegal_middle_witnesses'])}",
        f"prime_powers={len(fresh['prime_power_controls'])}",
        "single_factor_iff_square=true",
        "prime_power_only_pm1=true",
        "boolean_meters=false",
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
