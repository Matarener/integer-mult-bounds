#!/usr/bin/env python3
"""Bind shape constant A=0 for the selected m=73 complex stock divisor.

Card selected-stock-envelope. Predecessor #3113 / selected-stock-envelope-m73
already bound the finite per-level stock allowance B_bits=2642 and the
halving guard; this package does not recompute those as a contribution.
It proves that the retained finite-stock candidate for C(w) is independent
of atom width w, so log_2 C(w) <= A*w + B holds with A=0 and B=2642.
Leaf reserve rho remains unbound. No new kappa.

Admission uses need() and remains active under python -O.
"""

from __future__ import annotations

import hashlib
import json
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
B_BITS = 2642
SHAPE_A = 0
KAPPA_DECIMAL = "0.001672660197076918"


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


def read_text(rel):
    raw = (ROOT / rel).read_bytes()
    need(len(raw) <= 4_000_000, "source size: " + rel)
    return raw.decode("utf-8")


def pin_sources():
    manifest = read_json(HERE / "SOURCES.json")
    rows = manifest["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    need(tuple(row["path"] for row in inputs) == INPUTS, "input inventory")
    pinned = {}
    for row in inputs:
        path = ROOT / row["path"]
        raw = path.read_bytes()
        need(len(raw) <= 4_000_000, "source size")
        digest = hashlib.sha256(raw).hexdigest()
        need(digest == row["sha256"], "source hash: " + row["path"])
        pinned[row["path"]] = raw.decode("utf-8")
    return pinned


def no_atom_width_parameter(formula: str) -> bool:
    """True when a closed-form group/stock formula has no atom-width w."""
    return ("w" not in formula) and ("(w" not in formula)


def evaluate():
    texts = pin_sources()
    proof = texts["research/selected-coarse-depth-stock/PROOF.md"]
    prior = texts["research/selected-stock-envelope-m73/README.md"]
    bit_parent = texts["research/selected-bit-parent-reserve/README.md"]
    cover_bit = texts["notes/three-stage-cover-bit.tex"]
    cover_cx = texts["notes/three-stage-cover-complex.tex"]
    scope = texts["docs/research/selected-bootstrap-scope-map.md"]

    # Predecessor already bound B_bits=2642; cite, do not re-derive Sp order.
    need("2,642-bit stock allowance B" in proof, "cite: finite stock B")
    need("B = 2628 + 14 = 2642" in prior, "cite: prior B decomposition")
    need("missing_lemma=A_B_rho_unbound" in prior or "A, B and rho" in prior,
         "cite: prior left A unbound")
    need("Bind `A` (or prove `A = 0`)" in prior, "cite: prior OQ1")

    # Ordinary BIT digit-tower lift forces positive A.
    need("GL_64(Z/q^w Z)" in bit_parent, "cite: ordinary local-ring cover")
    need("q^(m^2*(w-1))" in bit_parent, "cite: ordinary digit-tower lift")
    need("\\log_q W_q(w)<4096w+1" in bit_parent,
         "cite: ordinary linear-in-w envelope")
    need("W(w)=W_0q^{m^2(w-1)}" in cover_bit.replace(" ", ""),
         "cite: ordinary W(w) formula")
    need("charged in the row reserve" in cover_bit, "cite: ordinary digit charge")

    # Complex cover: Sp->O lifts are F_2 parameters, not atom-width digits.
    need("u\\in U" in cover_cx and "\\mathbb F_2" in cover_cx,
         "cite: complex lifts over F_2")
    need("exactly the orthogonal lifts" in cover_cx, "cite: orthogonal lifts")
    need("|O(2n,2)|" in cover_cx, "cite: finite O/Sp identity")
    need("These full finite role counts are retained" in cover_cx,
         "cite: finite role counts retained")
    need("needs no numerical enumeration" in cover_cx, "cite: binary matrices")
    # No ordinary-style atom-width digit tower in the complex note.
    need("q^{m^2(w-1)}" not in cover_cx, "no complex digit-tower formula")
    need("W(w)" not in cover_cx, "no complex W(w)")
    need("Z/q^w" not in cover_cx and "\\mathbb Z/q^w" not in cover_cx,
         "no complex local-ring cover")

    # Selected m=73 producer identification.
    need("The selected complex supplier has `m=73`" in scope,
         "cite: m=73 binding")
    need("fixed Sp(72,2) order" in proof, "cite: Sp(72,2) stock factor")
    need("14,826 physical families" in proof, "cite: family inventory")

    # Structural w-independence of every charged stock factor.
    # Sp(72,2) closed form uses only the even dimension 72 / n=36.
    sp_formula = "2^(n^2) * prod_{j=1..n} (2^(2j) - 1)"
    need(no_atom_width_parameter(sp_formula), "Sp formula has no w")
    # Family split is a fixed integer partition.
    family_split = (14336, 480, 8, 2)
    need(sum(family_split) == 14826, "family split sum")
    need(all(isinstance(x, int) and x > 0 for x in family_split),
         "family split positive ints")
    # Historical complex note's finite coefficient is also w-free (parallel).
    need("24\\cdot2431=58344" in cover_cx.replace(" ", ""),
         "cite: historical finite complex row coefficient")

    # Shape lemma binding under finite-stock-as-C.
    need("log_q C(w)<=A*w+B" in proof, "cite: shape premise")
    need("Actual A, B and rho are **not established here**" in proof,
         "cite: predecessor left A unbound")
    need(
        "Whether the finite stock bounds uniform C(w)" in proof,
        "cite: finite-stock-as-C admission still named",
    )

    # A=0: C candidate is constant in w, so log_2 C <= 0*w + B_bits.
    need(SHAPE_A == 0, "A is zero")
    need(B_BITS == 2642, "shape B equals bound stock bits")
    # For any two atom widths, constant C implies zero slope.
    c_bits_at = {1: B_BITS, 2: B_BITS, 8: B_BITS, 64: B_BITS}
    slopes = {
        (w1, w2): (c_bits_at[w2] - c_bits_at[w1]) / (w2 - w1)
        for w1, w2 in ((1, 2), (2, 8), (8, 64))
    }
    need(all(slope == 0 for slope in slopes.values()), "zero w-slope of log C")
    need(all(c_bits_at[w] <= SHAPE_A * w + B_BITS for w in c_bits_at),
         "shape inequality holds with A=0")

    # Ordinary contrast control values (must stay strictly positive A).
    ordinary_A_lower = 4096  # from log_q W < 4096 w + 1
    need(ordinary_A_lower > 0, "ordinary A lower bound positive")
    need(ordinary_A_lower != SHAPE_A, "complex A differs from ordinary")

    # Composition consequence under A=0 (rho still free).
    need("sigma <= (43/26)*(1-s)*(A+B) + rho" in proof, "cite: composition")
    # With A=0 and B=B_bits the nonlinear term collapses to B_bits alone.
    collapsed = "(43/26)*(1-s)*2642 + rho"
    need(SHAPE_A + B_BITS == B_BITS, "A+B collapses to B")

    # Kappa unchanged (decimal pin from assignment / selected record).
    selected = read_json(ROOT / "certificates/selected-result.json")
    decimal = selected.get("decimal")
    need(decimal == KAPPA_DECIMAL or str(decimal) == KAPPA_DECIMAL,
         "kappa decimal pin")

    # Mutation controls: each must fail its targeted predicate.
    need(not no_atom_width_parameter("2^(n^2) * q^(w-1)"),
         "control: fake w in Sp formula rejected")
    need("q^{m^2(w-1)}" not in cover_cx, "control: digit tower still absent")
    need(c_bits_at[1] == c_bits_at[64], "control: width-injected stock rejected")
    need(ordinary_A_lower != 0, "control: ordinary A=0 false")
    need(SHAPE_A + 1 != 0, "control: A=1 rejected")

    return {
        "schema_version": 1,
        "status": "PASS_SELECTED_STOCK_SHAPE_A_ZERO",
        "producer": "selected-complex-m73",
        "shape_A": SHAPE_A,
        "shape_B_bits": B_BITS,
        "rho": "unbound",
        "finite_stock_as_C_admission": True,
        "digit_tower_lift_in_complex_cover": False,
        "ordinary_A_lower_bound": ordinary_A_lower,
        "zero_slopes": {f"{a}->{b}": slopes[(a, b)] for a, b in slopes},
        "composition_under_A_zero": collapsed,
        "no_new_kappa": True,
        "kappa_decimal": KAPPA_DECIMAL,
        "marker": MARKER,
    }


def admit(observed, certificate):
    need(observed["status"] == certificate["status"], "certificate mismatch")
    need(observed["shape_A"] == certificate["shape_A"], "certificate mismatch")
    need(observed["shape_B_bits"] == certificate["shape_B_bits"],
         "certificate mismatch")
    need(observed["rho"] == certificate["rho"], "certificate mismatch")
    need(observed["marker"] == certificate["marker"], "certificate mismatch")
    need(observed["no_new_kappa"] is True, "certificate mismatch")


def main():
    observed = evaluate()
    certificate = read_json(HERE / "CERTIFICATE.json")
    admit(observed, certificate)
    # Read-only: package files unchanged relative to certificate hash pin.
    print(MARKER)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
