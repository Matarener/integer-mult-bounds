#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent closed-form check for PR2753 route_cube fibre invoice.

Does not import verify.py or model.py. Re-derives the partition/write formulas
from the authenticated routes.py loop shape and recomputes fixture arithmetic.

Prepared by Wentao Li with substantial AI assistance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERT_PATH = HERE / "CERTIFICATE.json"
ROUTES = ROOT / "research/selected-bit-recursive-caller/predecessor/vendor/routes.py"
PASS = "PASS_INDEPENDENT_PR2753_ROUTE_CUBE_OWV_FIBRE"


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def load_json_reject_duplicates(path: Path):
    text = path.read_text(encoding="utf-8")

    def _hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(f"duplicate JSON key {key!r}")
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=_hook)


def predict(q, w, dimension, fibre_bits):
    modulus = q**w
    bits = modulus.bit_length() + 1
    cap = modulus // q
    highs = cap ** (dimension * dimension)
    volume = highs * fibre_bits
    if cap > 1:
        partitions = dimension * dimension * bits
        writes = (2 * dimension * dimension * bits + 2) * volume
    else:
        partitions = 0
        writes = 2 * volume
    return bits, cap, highs, volume, partitions, writes


def check_routes_structure():
    text = ROUTES.read_text(encoding="utf-8")
    digest = hashlib.sha256(ROUTES.read_bytes()).hexdigest()
    if digest != "ed7dc3679451696ab1dd841146b215c9515a3eec5e4ff3763f33c315f1696ada":
        fail("routes.py digest drift")
    # Structural markers of the charged loops.
    for needle in (
        "def route_cube(",
        "def partition(",
        "for coordinate in reversed(range(context.dimension*context.dimension)):",
        "cursor = arena.copy(context.ring.one)",
        "following = partition(current, coordinate, cursor, context, fibre, factory)",
        "cursor.msb()",
        "shifted = context.raw.shift_add_bit(cursor, ZERO)",
        "copy_bits(source, decorated, fibre)",
        "copy_bits(current, output, fibre)",
        "copy_bits(source, buckets[bit], fibre)",
        "copy_bits(bucket, output, fibre)",
    ):
        if needle not in text:
            fail(f"missing structural marker: {needle}")


def main():
    check_routes_structure()
    cert = load_json_reject_duplicates(CERT_PATH)
    claim = cert["claim"]
    if claim["formula_cap_gt_1"] != "(2*d*d*L + 2)*V":
        fail("formula text")
    if claim["selected_decimal"] != "0.001672660197076918":
        fail("selected decimal")
    if claim["no_new_kappa"] is not True or claim["no_supplier_admission"] is not True:
        fail("kappa/supplier flags")
    if claim["matches_stated_OwV_charge"] is not True:
        fail("OwV match flag")

    for row in cert["fixtures"]:
        bits, cap, highs, volume, partitions, writes = predict(
            row["q"], row["w"], row["dimension"], row["fibre_bits"]
        )
        if (bits, cap, highs, volume, partitions, writes) != (
            row["arena_bits"],
            row["cap"],
            row["highs"],
            row["volume"],
            row["partition_count"],
            row["fibre_copy_writes"],
        ):
            fail(f"closed form drift for {row}")
        if row["measured_partitions"] != partitions:
            fail("measured partitions")
        if row["measured_fibre_copy_writes"] != writes:
            fail("measured writes")
        if row["w"] >= 2 and writes < 2 * row["w"] * volume:
            fail("OwV numerical lower bound")

    for bits, passes in cert["cursor_pass_lemma"].items():
        if int(bits) != passes:
            fail(f"cursor lemma {bits}")

    print(f"{PASS} fixtures={len(cert['fixtures'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
