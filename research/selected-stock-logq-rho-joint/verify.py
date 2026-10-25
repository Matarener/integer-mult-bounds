#!/usr/bin/env python3
"""Join the corrected log_q parent with the layer leaf hypothesis.

#4141 leaves rho unbound and gives the sufficient parent term
T(s) = (43/26)*(1-s)*(1321/40). #3667 concludes S_leaf = 1 and rho = 0 for
the selected complex layer, but publishes the reading-(a) coefficient with the
loose base-2 substitution B = 2642. This verifier proves that those two
hypotheses together make T(s) a sufficient envelope coefficient, and that the
published reading-(a) coefficient is exactly 80*T(s). It does not fill
actual_stock_coefficient and does not rerun the layer proof.
"""
import hashlib
import json
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

PINS = {
    "docs/research/selected-bootstrap-scope-map.md":
        "b9196c339ed06c749780749d30c93f2deba0ebb489368a1eb4505e461a1c3062",
    "research/selected-bootstrap-stock-audit/RESULT.json":
        "f0bd4f2270826de7b935323e9b4d2e034f69b46205be9535488c4429e95f7917",
    "research/selected-coarse-depth-stock/PROOF.md":
        "fe1a29b3757a3fda7124027e7e14228a6f3aa49521e23822909036172807f800",
    "research/selected-stock-logq-parent/README.md":
        "d29c317d27c554931563e6375ec598262eaf6affe5e03367289ee713d6148846",
    "research/selected-stock-logq-parent/verify.py":
        "7931d1bf2149fe3a15e95cd76a45a359d88322f848b515f8c198cdae91f7548c",
    "research/selected-stock-rho-ledger/README.md":
        "979a38cc27cbcb6acac212b9c66e95a5261d822cc7ea9429df00fc6df4e3817d",
    "research/selected-stock-rho-ledger/verify.py":
        "e5eea2b7fe9294b2f16befda4dc48d631a2161c72bc461a1d717e6634f9dfb81",
}

LOOSE_BITS = 2642
PRIME_FLOOR = 80
PARENT_DIGITS = Fraction(LOOSE_BITS, PRIME_FLOOR)  # 1321/40
DEPTH = Fraction(43, 26)


def read(rel):
    with open(os.path.join(ROOT, rel), "rb") as handle:
        return handle.read()


def parent_term(one_minus_s, digits):
    """Sufficient coefficient (43/26)*(1-s)*digits of the w*(1+log2 e) shape."""
    if one_minus_s <= 0:
        raise ValueError("stock gap must be positive")
    return DEPTH * one_minus_s * digits


def shape_slack_coefficients(atom_width):
    """Nonnegative witnesses that log2(e) <= w*(1+log2(e)) for every log2(e) >= 0.

    The difference w*(1+L) - L is w + (w-1)*L. Its constant term is w and its
    slope in L is w-1. Both are nonnegative exactly when w >= 1, so the
    inequality holds for every L >= 0, and it is strict when w >= 1 and L > 0.
    """
    if atom_width < 1:
        raise ValueError("atom width must be at least 1")
    return atom_width, atom_width - 1


def one_digit_leaf_log():
    """log_q(q) = 1. This is not bounded by rho = 0."""
    return Fraction(1)


def evaluate():
    failures = []

    def require(cond, label):
        if not cond:
            failures.append(label)

    texts = {}
    for rel, digest in PINS.items():
        raw = read(rel)
        require(hashlib.sha256(raw).hexdigest() == digest, "pin:" + rel)
        texts[rel] = raw.decode("utf-8")

    coarse = texts["research/selected-coarse-depth-stock/PROOF.md"]
    logq = texts["research/selected-stock-logq-parent/README.md"]
    logq_code = texts["research/selected-stock-logq-parent/verify.py"]
    rho = texts["research/selected-stock-rho-ledger/README.md"]
    rho_code = texts["research/selected-stock-rho-ledger/verify.py"]
    scope = texts["docs/research/selected-bootstrap-scope-map.md"]
    receipt = json.loads(texts["research/selected-bootstrap-stock-audit/RESULT.json"])

    require("one may take S_leaf=1" in coarse, "coarse-depth admits S_leaf=1")
    require("log_q C(w)<=A*w+B" in coarse, "coarse-depth log_q divisor shape")
    require("log_q S_leaf(e,w)<=rho*w*(1+log2 e)" in coarse, "coarse-depth leaf shape")
    require("sigma <= (43/26)*(1-s)*(A+B) + rho." in coarse, "coarse-depth coefficient")
    require("(43/26)*(1-s)*log2(e)*log_q C(w) + log_q S_leaf(e,w)." in coarse,
            "coarse-depth parent expansion")
    require("q>2^80" in scope, "prime floor q>2^80")
    require("T(s) = (43/26)*(1-s)*(1321/40)" in logq, "log_q parent term T(s)")
    require("It does not prove `S_leaf = 1` or bind `rho`." in logq,
            "log_q note leaves the leaf hypothesis open")
    require("return Fraction(43, 26) * one_minus_s * Fraction(bit_length, log2_floor)" in logq_code,
            "log_q verifier uses bit_length/log2_floor")
    require("so `S_leaf = 1` and `rho = 0`." in rho, "rho-ledger states S_leaf=1 and rho=0")
    require("`sigma <= (43/26)(1-s)·2642 ≈ 4362.14`" in rho,
            "rho-ledger publishes the loose stage-1 coefficient")
    require("No selected step bootstraps the m=73 complex layer." in rho,
            "rho-ledger: the selected bootstrap does not call this layer")
    require("base = F(43, 26) * (1 - s) * b_bits  # complex part with A = 0" in rho_code,
            "rho-ledger code multiplies the base-2 bit length")

    require(PARENT_DIGITS == Fraction(1321, 40), "1321/40 is 2642/80")
    require(LOOSE_BITS == PRIME_FLOOR * PARENT_DIGITS, "loose bits are exactly 80 times the digit bound")

    # Shape embedding used by the coarse-depth coefficient, specialized to A = 0.
    for width in range(1, 65):
        constant, slope = shape_slack_coefficients(width)
        require(constant >= 1 and slope >= 0, "shape slack at width %s" % width)
    require(shape_slack_coefficients(1) == (1, 0), "width-1 slack is the constant 1")

    # rho = 0 bounds log_q(1) = 0 and does not bound a one-digit leaf.
    require(Fraction(0) <= 0, "log_q(1) = 0 is inside rho = 0")
    require(not (one_digit_leaf_log() <= 0), "a one-digit leaf is outside rho = 0")

    terms = {}
    for name, branch in receipt["branches"].items():
        saving = Fraction(branch["common_saving"])
        require(0 < saving < 1, name + " saving in (0,1)")
        gap = 1 - saving
        gaps = {stage["gaps"]["stock"] for stage in branch["stages"]}
        require(gaps == {str(gap)}, name + " stock gap is 1-s")
        require(all(stage["actual_stock_coefficient"] is None for stage in branch["stages"]),
                name + " actual coefficient still null")
        stage1 = next(stage for stage in branch["stages"] if stage["stage"] == 1)
        require(stage1["stock_headroom_log2"] == 6562783, name + " stage-1 headroom")
        joint = parent_term(gap, PARENT_DIGITS)
        loose = parent_term(gap, LOOSE_BITS)
        require(loose == 80 * joint, name + " loose coefficient is exactly 80*T(s)")
        require(joint < 64, name + " joint coefficient is below 64")
        require(joint < loose, name + " joint coefficient is stricter than the published one")
        # Reading (a) in the rho-ledger is this loose value. Its displayed
        # two-decimal upper bound is checked only for the native stage-1 saving.
        if name == "bootstrap":
            displayed = float(loose)
            require(4362.13 < displayed < 4362.15, "native loose coefficient displays as 4362.14")
        guard_argument = 8 * joint
        require(guard_argument < 2 ** 9, name + " ceil(log2(8*T(s))) <= 9")
        require(guard_argument < 2 ** stage1["stock_headroom_log2"],
                name + " headroom still dominates the joint guard argument")
        terms[name] = joint

    if failures:
        raise SystemExit("FAIL " + "; ".join(failures))
    boot = terms["bootstrap"]
    cons = terms["conservative_bootstrap"]
    print(
        "PASS_SELECTED_STOCK_LOGQ_RHO_JOINT"
        f" digits=1321/40 factor=80"
        f" bootstrap_T={boot.numerator}/{boot.denominator}"
        f" conservative_T={cons.numerator}/{cons.denominator}"
        " rho=0 S_leaf=1 coefficient=null layer_not_bootstrapped"
        " headroom_not_adoption no_new_kappa"
    )
    return boot, cons


if __name__ == "__main__":
    evaluate()
