#!/usr/bin/env python3
"""Show that the bit-motif child list has Psi below one at tau = 1-2^{-50}.

Width-1 children give Psi(tau) = (s/W) m^{-tau}. The displayed deficit and a
harmonic upper bound on ln(10) certify s/W < m^tau. The network is not replayed.
"""

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MOTIFS = ROOT / "upstream/build/sections/03-motifs.tex"
SWAP = ROOT / "upstream/build/sections/04-swap.tex"
BATCH = ROOT / "notes/batched-bit-rows.tex"
MARKER = "PASS_UNIFORM_EXPONENT_BOUND psi_below_one=true no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_UNIFORM_EXPONENT_BOUND " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def ln10_upper():
    """Strict upper bound for ln(10): each unit interval of 1/(1+t) is below 1/(1+k)."""
    return sum(Fraction(1, k) for k in range(1, 10))


def exponent_slack(deficit, rank_sum):
    require(deficit > 0 and rank_sum > 0, "rank data")
    return Fraction(deficit * (1 << 50), rank_sum + deficit)


def psi_below_one(deficit, rank_sum, modulus):
    require(modulus == 10**6, "this logarithm bound is for m = 10^6")
    return exponent_slack(deficit, rank_sum) > 6 * ln10_upper()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "notes/batched-bit-rows.tex",
        "upstream/build/sections/04-swap.tex",
        "upstream/build/sections/03-motifs.tex",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def integer_after(text, pattern):
    match = re.search(pattern, text)
    require(match is not None, "missing " + pattern)
    return int(match.group(1))


def evaluate():
    authenticate()
    motifs = MOTIFS.read_text(encoding="utf-8")
    swap = SWAP.read_text(encoding="utf-8")
    batch = BATCH.read_text(encoding="utf-8")
    require(r"\Psi(x)=\frac1W\sum_{i=1}^J(t_i/m)^x" in batch, "the Psi definition moved")
    require("exactly $s$." in swap and r"b=e/m" in swap, "the width-1 call count moved")
    require(r"1-2^{-50}" in motifs, "the manuscript exponent moved")
    modulus = integer_after(motifs, r"m=h\^3=([0-9]+)")
    block = integer_after(motifs, r"N=v\^3=([0-9]+)")
    rank_sum = integer_after(motifs, r"=([0-9]+)<W_\{\\rm b\}m")
    require(r"\frac{L_{\rm b}}{N}=\frac{100}{539}" in motifs, "the L_b ratio moved")
    require(r"\frac{339}{22587335000000}" in motifs, "the displayed deficit ratio moved")
    require(block * 100 % 539 == 0, "L_b is not an integer")
    deficit = block - 2 * (block * 100 // 539)
    require(Fraction(deficit, rank_sum + deficit) == Fraction(339, 22587335000000), "the deficit ratio moved")
    require((rank_sum + deficit) % modulus == 0, "the role count is not an integer")
    slack = exponent_slack(deficit, rank_sum)
    require(psi_below_one(deficit, rank_sum, modulus), "the exponent slack does not clear ln(m)")
    ratio = Fraction(rank_sum * modulus, rank_sum + deficit)
    require(ratio == modulus * (1 - Fraction(deficit, rank_sum + deficit)), "s/W is not m(1-eta)")
    return {
        "exponent": "1-2^{-50}",
        "modulus": modulus,
        "child_width": 1,
        "eta": "339/22587335000000",
        "slack_exceeds_log_bound": True,
        "psi_below_one": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
