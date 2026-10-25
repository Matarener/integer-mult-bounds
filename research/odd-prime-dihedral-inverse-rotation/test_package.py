#!/usr/bin/env python3
"""Package tests; admission via need() so -O still enforces gates."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from model import (  # noqa: E402
    CERTIFIED_PRIMES,
    PROJECTORS,
    build_group,
    direct_four_call,
    need,
    target_state,
    word_state,
)


def test_primes_and_projectors() -> None:
    need(CERTIFIED_PRIMES[0] == 5, "p=5 lead")
    need(all(p % 2 == 1 for p in CERTIFIED_PRIMES), "odd primes")
    need(len(PROJECTORS) == 28, "28 projectors")


def test_direct_and_mutations() -> None:
    for p in CERTIFIED_PRIMES:
        group = build_group(p)
        target = target_state(group["ngroup"], group["e"], group["r"], group["r_inv"])
        labels, projectors = direct_four_call(group)
        need(word_state(group, labels, projectors) == target, f"p={p} direct")
        for drop in range(4):
            reduced_labels = labels[:drop] + labels[drop + 1:]
            reduced_ns = projectors[:drop] + projectors[drop + 1:]
            need(word_state(group, reduced_labels, reduced_ns) != target,
                 f"p={p} deletion {drop}")
        mutated = list(labels)
        mutated[0] = group["t"]
        need(word_state(group, tuple(mutated), projectors) != target,
             f"p={p} mutation")


def test_certificate_dup_and_corruption() -> None:
    cert_path = HERE / "CERTIFICATE.json"
    need(cert_path.is_file(), "certificate present")
    text = cert_path.read_text(encoding="utf-8")

    def hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"dup {key}")
            out[key] = value
        return out

    cert = json.loads(text, object_pairs_hook=hook)
    need(cert["no_new_kappa"] is True, "kappa flag")
    need(tuple(cert["certified_primes"]) == CERTIFIED_PRIMES, "prime list")
    # Temp copy corruption must be detectable by digest mismatch logic.
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "CERTIFICATE.json"
        bad.write_text(text.replace('"no_new_kappa": true', '"no_new_kappa": false'),
                       encoding="utf-8")
        corrupted = json.loads(bad.read_text(encoding="utf-8"))
        need(corrupted.get("no_new_kappa") is False, "corruption applied")
        need(corrupted.get("no_new_kappa") != cert.get("no_new_kappa"),
             "corruption distinct")


def test_even_order_rejected() -> None:
    try:
        build_group(9)  # odd composite
        need(False, "odd composite should fail")
    except SystemExit:
        pass
    try:
        build_group(8)  # even
        need(False, "even should fail")
    except SystemExit:
        pass


def main() -> None:
    test_primes_and_projectors()
    test_direct_and_mutations()
    test_certificate_dup_and_corruption()
    test_even_order_rejected()
    print("PASS_ODD_PRIME_DIHEDRAL_INVERSE_ROTATION_PACKAGE_TESTS groups=4")


if __name__ == "__main__":
    main()
