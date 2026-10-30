#!/usr/bin/env python3
"""Odd-prime D_{2p} inverse-rotation four-call floor; read-only default."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from model import (  # noqa: E402
    CERTIFIED_PRIMES,
    EXPECTED_COUNTS,
    PROJECTORS,
    TOTAL_CANDIDATES,
    build_group,
    direct_four_call,
    need,
    target_state,
    word_state,
)

CERT_PATH = HERE / "CERTIFICATE.json"
SOURCES_PATH = HERE / "SOURCES.json"


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r} in {path}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=_hook)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_source_pins() -> None:
    sources = load_json_reject_duplicates(SOURCES_PATH)
    need(sources["base_commit"] == "bb4bccbf42844d2801487450727c2f63e10d1d0f",
         "base_commit pin")
    for rec in sources["files"]:
        if rec["usage"] != "input":
            continue
        live = ROOT / rec["path"]
        need(live.is_file(), f"missing input {rec['path']}")
        need(sha256_file(live) == rec["sha256"], f"source bytes mismatch: {rec['path']}")


def search_prime(p: int) -> dict:
    group = build_group(p)
    target = target_state(group["ngroup"], group["e"], group["r"], group["r_inv"])
    counts = {k: 0 for k in range(4)}
    hits = {k: 0 for k in range(4)}
    digests = {k: hashlib.sha256() for k in range(4)}
    for k in range(4):
        for labels in product((group["s"], group["t"]), repeat=k):
            for projectors in product(PROJECTORS, repeat=k):
                counts[k] += 1
                state = word_state(group, labels, projectors)
                record = bytes(labels)
                record += b"".join(n.to_bytes(2, "little") for n in projectors)
                record += b"".join(c.to_bytes(2, "little") for c in state)
                digests[k].update(record)
                if state == target:
                    hits[k] += 1
    need(counts == EXPECTED_COUNTS, f"p={p}: candidate counts {counts}")
    need(hits == {0: 0, 1: 0, 2: 0, 3: 0}, f"p={p}: unexpected hits {hits}")
    labels, projectors = direct_four_call(group)
    need(word_state(group, labels, projectors) == target, f"p={p}: direct word fails")
    # One-factor deletions and one label mutation fail.
    for drop in range(4):
        reduced_labels = labels[:drop] + labels[drop + 1:]
        reduced_ns = projectors[:drop] + projectors[drop + 1:]
        need(word_state(group, reduced_labels, reduced_ns) != target,
             f"p={p}: deletion {drop} still hits")
    mutated = list(labels)
    mutated[1] = group["s"]
    need(word_state(group, tuple(mutated), projectors) != target,
         f"p={p}: label mutation hits")
    return {
        "p": p,
        "group_order": 2 * p,
        "candidate_counts": {str(k): counts[k] for k in range(4)},
        "exact_endpoint_hits": {str(k): hits[k] for k in range(4)},
        "primary_state_sha256": {str(k): digests[k].hexdigest() for k in range(4)},
        "direct_exact": True,
    }


def build_certificate() -> dict:
    primes = []
    for p in CERTIFIED_PRIMES:
        primes.append(search_prime(p))
    return {
        "schema_version": 1,
        "model": {
            "groups": "D_{2p} for odd primes p in CERTIFIED_PRIMES",
            "presentation": "<s,t | s^2=t^2=e,(st)^p=e>",
            "encoding_primary": "r^k s^epsilon as index 2*k+epsilon, r=st",
            "coefficient_field": "F2",
            "registers": 3,
            "paid_labels": ["s", "t"],
            "scalar_factors": "D_N(g)=I+([g]+[e])N; N=xy^T, y^T x=1",
            "projectors": 28,
        },
        "target": "diag([st],[ts],[e])",
        "certified_primes": list(CERTIFIED_PRIMES),
        "search": {
            "lengths": [0, 1, 2, 3],
            "candidate_counts_per_prime": {
                str(k): EXPECTED_COUNTS[k] for k in range(4)
            },
            "total_candidates_per_prime": TOTAL_CANDIDATES,
            "total_candidates_all_primes": TOTAL_CANDIDATES * len(CERTIFIED_PRIMES),
        },
        "primes": primes,
        "attaining_word": {
            "labels": ["s", "t", "t", "s"],
            "projectors": ["E00", "E00", "E11", "E11"],
            "paid_calls": 4,
            "exact_endpoint": True,
        },
        "conclusion": (
            "Exact minimum 4 for every certified odd prime p; zero hits through "
            "length 3 on each D_{2p}."
        ),
        "kappa_unchanged": "0.001672660197076918",
        "no_new_kappa": True,
    }


def compare_certificate(fresh: dict, committed: dict) -> None:
    need(fresh["certified_primes"] == committed["certified_primes"], "prime list")
    need(fresh["target"] == committed["target"], "target")
    need(len(fresh["primes"]) == len(committed["primes"]), "prime row count")
    for a, b in zip(fresh["primes"], committed["primes"]):
        need(a["p"] == b["p"], "prime order")
        need(a["exact_endpoint_hits"] == b["exact_endpoint_hits"], f"p={a['p']} hits")
        need(a["primary_state_sha256"] == b["primary_state_sha256"],
             f"p={a['p']} digests")
        need(a["direct_exact"] is True and b["direct_exact"] is True,
             f"p={a['p']} direct")
    need(fresh["search"]["total_candidates_all_primes"]
         == committed["search"]["total_candidates_all_primes"],
         "total candidates")
    need(committed.get("no_new_kappa") is True, "kappa flag")


def crosscheck_d10(fresh: dict) -> None:
    """p=5 primary digests must match the pinned D10 certificate exactly."""
    d10 = load_json_reject_duplicates(
        ROOT / "research/d10-reflection-sharing-seeda3def8/CERTIFICATE.json"
    )
    need(d10["target"] == "diag([st],[ts],[e])", "D10 target")
    need(d10["search"]["exact_endpoint_hits"]
         == {"0": 0, "1": 0, "2": 0, "3": 0}, "D10 hits")
    row5 = next(r for r in fresh["primes"] if r["p"] == 5)
    need(row5["primary_state_sha256"] == d10["search"]["primary_state_sha256"],
         "p=5 primary digests must equal D10 certificate")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true",
                        help="regenerate CERTIFICATE.json (explicit write only)")
    args = parser.parse_args()
    check_source_pins()
    need(CERTIFIED_PRIMES[0] == 5, "p=5 cross-check must lead")
    fresh = build_certificate()
    crosscheck_d10(fresh)
    if args.write:
        CERT_PATH.write_text(json.dumps(fresh, indent=2) + "\n", encoding="utf-8")
        print("WROTE_CERTIFICATE", CERT_PATH)
    need(CERT_PATH.is_file(), "missing CERTIFICATE.json")
    committed = load_json_reject_duplicates(CERT_PATH)
    compare_certificate(fresh, committed)
    print(
        "PASS_ODD_PRIME_DIHEDRAL_INVERSE_ROTATION",
        f"primes={list(CERTIFIED_PRIMES)}",
        "min_calls=4",
        f"words_le3_per_prime={TOTAL_CANDIDATES}",
        f"total_words={TOTAL_CANDIDATES * len(CERTIFIED_PRIMES)}",
        "hits=0",
        "p5_crosscheck=true",
        "no_new_kappa",
    )


if __name__ == "__main__":
    main()
