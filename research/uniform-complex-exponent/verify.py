#!/usr/bin/env python3
"""Show that the complex motif ratio lies below m to the manuscript exponent.

The displayed rank sum and the deficit 2(N-L_c) rebuild s_c/W_c. The same
harmonic bound used for the bit motif certifies s_c/W_c < m^{1-2^{-50}}.
For a width-1 list of that length, Psi at this exponent is that ratio
divided by the power. The network is not replayed.
"""

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MOTIFS = ROOT / "upstream/build/sections/03-motifs.tex"
BATCH = ROOT / "notes/batched-bit-rows.tex"
MARKER = "PASS_UNIFORM_COMPLEX_EXPONENT psi_below_one=true no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_UNIFORM_COMPLEX_EXPONENT " + message)


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
    return sum(Fraction(1, k) for k in range(1, 10))


def exponent_slack(deficit, rank_sum):
    require(deficit > 0 and rank_sum > 0, "rank data")
    return Fraction(deficit * (1 << 50), rank_sum + deficit)


def ratio_below_power(deficit, rank_sum, modulus):
    require(modulus == 10**6, "this logarithm bound is for m = 10^6")
    return exponent_slack(deficit, rank_sum) > 6 * ln10_upper()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "notes/batched-bit-rows.tex",
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
    batch = BATCH.read_text(encoding="utf-8")
    require(r"\Psi(x)=\frac1W\sum_{i=1}^J(t_i/m)^x" in batch, "the Psi definition moved")
    require(r"1-2^{-50}" in motifs, "the manuscript exponent moved")
    require(r"\frac{s_{\rm c}}{W_{\rm c}}<m^\sigma" in motifs, "the complex comparison moved")
    require(r"The deficit is $2N-2L_{\rm c}>0$." in motifs, "the complex deficit formula moved")
    require("there are $s_{\\rm c}$ such factors" in motifs, "the factor count moved")
    modulus = integer_after(motifs, r"m=h\^3=([0-9]+)")
    block = integer_after(motifs, r"N=v\^3=([0-9]+)")
    rank_sum = integer_after(motifs, r"=([0-9]+)<W_\{\\rm c\}m")
    require(r"\frac{L_{\rm c}}{N}=\frac{101}{539}" in motifs, "the L_c ratio moved")
    require(r"\frac{73}{19906842167500}" in motifs, "the displayed complex ratio moved")
    require(block * 101 % 539 == 0, "L_c is not an integer")
    level = block * 101 // 539
    deficit = 2 * (block - level)
    require(Fraction(deficit, rank_sum + deficit) == Fraction(73, 19906842167500), "the deficit ratio moved")
    require((rank_sum + deficit) % modulus == 0, "the role count is not an integer")
    require(ratio_below_power(deficit, rank_sum, modulus), "the exponent slack does not clear ln(m)")
    ratio = Fraction(rank_sum * modulus, rank_sum + deficit)
    require(ratio == modulus * (1 - Fraction(deficit, rank_sum + deficit)), "s/W is not m(1-eta)")
    return {
        "exponent": "1-2^{-50}",
        "modulus": modulus,
        "child_width": 1,
        "rank_sum": str(rank_sum),
        "eta": "73/19906842167500",
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
