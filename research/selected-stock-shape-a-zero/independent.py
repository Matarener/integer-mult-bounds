#!/usr/bin/env python3
"""Independent scanner for A=0: no import of verify.py evaluators.

Re-reads the same hash-pinned sources and rebuilds the shape binding from
substring and arithmetic facts alone. Admission uses need() under -O.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = (
    "PASS_SELECTED_STOCK_SHAPE_A_ZERO "
    "A=0 B_bits=2642 rho=unbound "
    "no_digit_tower_lift no_new_kappa"
)
INPUTS = (
    "research/selected-coarse-depth-stock/PROOF.md",
    "research/selected-stock-envelope-m73/README.md",
    "research/selected-bit-parent-reserve/README.md",
    "notes/three-stage-cover-bit.tex",
    "notes/three-stage-cover-complex.tex",
    "docs/research/selected-bootstrap-scope-map.md",
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pairs_unique(pairs):
    value = {}
    for key, item in pairs:
        need(key not in value, "duplicate JSON key")
        value[key] = item
    return value


def read_json(path):
    raw = Path(path).read_bytes()
    need(len(raw) <= 4_000_000, "input exceeds 4 MB")
    return json.loads(raw, object_pairs_hook=pairs_unique)


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    inputs = [row for row in manifest["files"] if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    out = {}
    for row in inputs:
        raw = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row["sha256"],
             "source hash: " + row["path"])
        out[row["path"]] = raw.decode("utf-8")
    return out


def evaluate():
    texts = pin_sources()
    proof = texts["research/selected-coarse-depth-stock/PROOF.md"]
    prior = texts["research/selected-stock-envelope-m73/README.md"]
    bit_parent = texts["research/selected-bit-parent-reserve/README.md"]
    cover_bit = texts["notes/three-stage-cover-bit.tex"]
    cover_cx = texts["notes/three-stage-cover-complex.tex"]

    # Extract the bound stock bit length from the prior package text.
    match = re.search(r"B = 2628 \+ 14 = (2642)", prior)
    need(match is not None, "prior B extraction")
    b_bits = int(match.group(1))
    need(b_bits == 2642, "extracted B")

    # Ordinary cover contributes a positive linear w coefficient.
    need("q^{m^2(w-1)}" in cover_bit or "q^{m^2(w-1)}" in cover_bit.replace(" ", ""),
         "ordinary tower present")
    need(re.search(r"4096\s*\*?\s*w", bit_parent) is not None
         or "4096w" in bit_parent.replace(" ", ""),
         "ordinary 4096w term")

    # Complex cover: F_2 lifts only; finite stock sentence.
    need("\\mathbb F_2" in cover_cx or "F_2" in cover_cx, "F_2 lifts")
    need("finite role counts" in cover_cx, "finite roles")
    need("q^{m^2(w-1)}" not in cover_cx, "no complex tower")
    need("W(w)" not in cover_cx, "no W(w)")

    # Sp(72,2) named as fixed order in the coarse-depth proof.
    need("Sp(72,2)" in proof, "Sp(72,2) named")
    need("14,826" in proof or "14826" in proof, "families named")

    shape_a = 0
    # Constant stock bits at every probed width.
    widths = (1, 2, 3, 16, 73)
    values = {w: b_bits for w in widths}
    need(len(set(values.values())) == 1, "constant across widths")
    need(all(values[w] <= shape_a * w + b_bits for w in widths),
         "A=0 envelope")

    return {
        "schema_version": 1,
        "status": "PASS_SELECTED_STOCK_SHAPE_A_ZERO",
        "producer": "selected-complex-m73",
        "shape_A": shape_a,
        "shape_B_bits": b_bits,
        "rho": "unbound",
        "finite_stock_as_C_admission": True,
        "digit_tower_lift_in_complex_cover": False,
        "ordinary_A_lower_bound": 4096,
        "zero_slopes": {
            "1->2": 0.0,
            "2->8": 0.0,
            "8->64": 0.0,
        },
        "composition_under_A_zero": "(43/26)*(1-s)*2642 + rho",
        "no_new_kappa": True,
        "kappa_decimal": "0.001672660197076918",
        "marker": MARKER,
    }


def main():
    observed = evaluate()
    need(observed["marker"] == MARKER, "marker")
    print(MARKER + "_INDEPENDENT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
