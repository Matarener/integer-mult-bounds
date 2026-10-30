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
    CALLS,
    C,
    E,
    EXPECTED_CALLS,
    EXPECTED_IDEM,
    GROUP_INV,
    I2,
    IW,
    ROLES,
    W,
    make_direct_word,
    need,
    target_state,
    word_state,
)


def test_alphabet_sizes() -> None:
    need(len(CALLS) == EXPECTED_CALLS, "480 calls")
    need(len(CALLS) // 4 == EXPECTED_IDEM, "120 idempotents")
    need(ROLES == 4, "four roles")


def test_direct_and_mutations() -> None:
    call_index = {call: i for i, call in enumerate(CALLS)}
    direct = make_direct_word(call_index)
    target = target_state((I2, W, C, E))
    need(word_state(tuple(CALLS[i] for i in direct)) == target, "direct word")
    for drop in range(5):
        reduced = direct[:drop] + direct[drop + 1 :]
        need(
            word_state(tuple(CALLS[i] for i in reduced)) != target,
            f"deletion {drop}",
        )
    mutated = list(direct)
    old = CALLS[mutated[-1]]
    mutated[-1] = call_index[(GROUP_INV[old[0]], old[1], old[2])]
    need(word_state(tuple(CALLS[i] for i in mutated)) != target, "mutation")
    # Touching the dirty role incorrectly must miss.
    dirty_touch = list(direct) + [call_index[(I2, 1 << 3, 1 << 3)]]
    need(
        word_state(tuple(CALLS[i] for i in dirty_touch)) != target,
        "extra dirty toggle must miss",
    )


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
    need(cert["result_minimum"] == 5, "minimum")
    need(cert["dirty_role_lowers_minimum"] is False, "dirty flag")
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "CERTIFICATE.json"
        bad.write_text(
            text.replace('"result_minimum": 5', '"result_minimum": 4'),
            encoding="utf-8",
        )
        corrupted = json.loads(bad.read_text(encoding="utf-8"))
        need(corrupted["result_minimum"] == 4, "corruption applied")
        need(corrupted["result_minimum"] != cert["result_minimum"], "corruption distinct")


def test_positive_two_call() -> None:
    call_index = {call: i for i, call in enumerate(CALLS)}
    positive = target_state((I2, W, E, E))
    word = (call_index[(I2, 1, 1)], call_index[(W, 2, 2)])
    need(word_state(tuple(CALLS[i] for i in word)) == positive, "positive control")


def main() -> None:
    test_alphabet_sizes()
    test_direct_and_mutations()
    test_certificate_dup_and_corruption()
    test_positive_two_call()
    print("PASS_SL2F3_DIRTY_ROLE_FOUR_PACKAGE_TESTS groups=4")


if __name__ == "__main__":
    main()
