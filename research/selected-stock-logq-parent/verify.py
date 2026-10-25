#!/usr/bin/env python3
"""Correct the log base of the m=73 parent stock term. No new kappa.

The finite-stock candidate C has bit length 2642, so log2(C) < 2642.
research/selected-stock-shape-a-zero substitutes that 2642 into the log_q
composition of research/selected-coarse-depth-stock. For every prime q > 2^80
the same hypothesis gives the stricter uniform digit bound log_q(C) < 2642/80.
"""
import hashlib
import json
import os
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

PINS = {
    "research/selected-stock-shape-a-zero/PROOF.md":
        "e2ce357464afc8f40fde33416f567c110750cced23b09856dbb9a8252b7f7bf9",
    "research/selected-coarse-depth-stock/PROOF.md":
        "fe1a29b3757a3fda7124027e7e14228a6f3aa49521e23822909036172807f800",
    "research/selected-bootstrap-stock-audit/RESULT.json":
        "f0bd4f2270826de7b935323e9b4d2e034f69b46205be9535488c4429e95f7917",
    "docs/research/selected-bootstrap-scope-map.md":
        "b9196c339ed06c749780749d30c93f2deba0ebb489368a1eb4505e461a1c3062",
}


def read(rel):
    with open(os.path.join(ROOT, rel), "rb") as handle:
        return handle.read()


def sp_order(n):
    """|Sp(2n, 2)| = 2^(n^2) * prod_{j=1..n} (2^(2j) - 1)."""
    value = 2 ** (n * n)
    for j in range(1, n + 1):
        value *= 2 ** (2 * j) - 1
    return value


def parent_term(one_minus_s, bit_length, log2_floor):
    """Uniform parent contribution (43/26)*(1-s)*bit_length/log2_floor.

    This is the sufficient log_q coefficient of w*(1+log2 e) coming from a
    constant divisor whose base-2 logarithm is strictly below bit_length,
    on primes whose base-2 logarithm is strictly above log2_floor.
    """
    if log2_floor <= 0:
        raise ValueError("prime floor must be positive")
    return Fraction(43, 26) * one_minus_s * Fraction(bit_length, log2_floor)


def one_digit_leaf_beats_rho_zero(sample_q=3):
    """log_q(q) = 1 is not <= rho * w * (1+log2 e) when rho = 0."""
    if sample_q <= 1:
        raise ValueError("q > 1")
    leaf_log = Fraction(1)  # log_q(q)
    return leaf_log > 0


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

    shape = texts["research/selected-stock-shape-a-zero/PROOF.md"]
    coarse = texts["research/selected-coarse-depth-stock/PROOF.md"]
    scope = texts["docs/research/selected-bootstrap-scope-map.md"]
    receipt = json.loads(texts["research/selected-bootstrap-stock-audit/RESULT.json"])

    require("sigma <= (43/26) * (1 - s) * 2642 + rho." in shape,
            "shape proof displays the log2 constant inside the log_q composition")
    require("`log_q C(w)<=A*w+B`" in coarse,
            "coarse proof states the log_q shape hypothesis")
    require("q>2^80" in scope,
            "scope map states the admissible prime floor q>2^80")

    order = sp_order(36)
    families = 14336 + 480 + 8 + 2
    stock = order * families
    require(families == 14826, "family split 14826")
    require(order.bit_length() == 2628, "Sp(72,2) bit length 2628")
    require(stock.bit_length() == 2642, "finite stock bit length 2642")
    require(2 ** 2641 <= stock < 2 ** 2642, "log2(stock) is strictly below 2642")

    terms = {}
    for name, branch in receipt["branches"].items():
        saving = Fraction(branch["common_saving"])
        require(0 < saving < 1, name + " saving in (0,1)")
        gaps = {stage["gaps"]["stock"] for stage in branch["stages"]}
        require(gaps == {str(1 - saving)}, name + " stock gap is 1 - saving at every stage")
        require(all(stage["actual_stock_coefficient"] is None for stage in branch["stages"]),
                name + " actual coefficient still null")
        stage1 = next(stage for stage in branch["stages"] if stage["stage"] == 1)
        require(stage1["stock_headroom_log2"] == 6562783, name + " stage-1 headroom")
        tight = parent_term(1 - saving, 2642, 80)
        loose = parent_term(1 - saving, 2642, 1)
        require(loose == 80 * tight, name + " loose parent term is exactly 80 times the q>2^80 term")
        require(tight < 2 ** 6, name + " corrected parent term is below 2^6")
        require(tight < 2 ** stage1["stock_headroom_log2"],
                name + " headroom comparison")
        # The headroom comparison is not adoption: the receipt coefficient stays null.
        terms[name] = tight

    # rho = 0 forces S_leaf = 1. A one-digit leaf has log_q(q) = 1, which is
    # not bounded by 0 * w * (1 + log2 e).
    require(one_digit_leaf_beats_rho_zero(3), "one-digit leaf is outside rho = 0")
    require(not (1 <= 0), "log_q(q) is not <= 0")

    # A prime floor of 2^1 does not justify the factor 80.
    sample = Fraction(39932981492927675859083000107018507072324140917,
                      40000000000000000000000000000000000000000000000)
    require(parent_term(sample, 2642, 1) != parent_term(sample, 2642, 80),
            "dropping the prime floor changes the parent term")
    require(parent_term(sample, 2643, 80) != parent_term(sample, 2642, 80),
            "a longer stock changes the parent term")

    if failures:
        raise SystemExit("FAIL " + "; ".join(failures))
    boot = terms["bootstrap"]
    cons = terms["conservative_bootstrap"]
    print(
        "PASS_SELECTED_STOCK_LOGQ_PARENT"
        f" bits=2642 q_floor=80 factor=80"
        f" bootstrap_parent={boot.numerator}/{boot.denominator}"
        f" conservative_parent={cons.numerator}/{cons.denominator}"
        " rho=unbound coefficient=null headroom_not_adoption no_new_kappa"
    )
    return boot, cons


if __name__ == "__main__":
    evaluate()
