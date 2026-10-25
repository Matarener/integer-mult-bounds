#!/usr/bin/env python3
"""Integer-only route to Psi(1-2^-50) < 1 on both motif parking nodes.

This program shares no series, no logarithm and no code with verify.py.  It
re-derives the same conclusion from the manuscript's own two displayed facts
(the deficit comparison and m < 2^20) plus two elementary inequalities:

    e^x <= 1/(1-x)        for 0 <= x < 1,
    -ln(1-eta) >= eta     for 0 < eta < 1.

Both are proved here from their definitions where the proof is short, and the
numeric comparisons are exact integer cross-multiplications.
"""

import hashlib
import json
import re
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
NOTE = ROOT / "notes/batched-bit-rows.tex"
SWAP = ROOT / "upstream/build/sections/04-swap.tex"
MOTIFS = ROOT / "upstream/build/sections/03-motifs.tex"

MARKER = "PASS_PARKING_PSI_EXPONENT_THRESHOLD_INDEPENDENT"
TWO50 = 2 ** 50


def fail(message):
    raise SystemExit("FAIL_PARKING_PSI_EXPONENT_THRESHOLD_INDEPENDENT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        require(sha256(ROOT / row["path"]) == row["sha256"], "input drift " + row["path"])


def parse():
    motifs = MOTIFS.read_text(encoding="utf-8")
    swap = SWAP.read_text(encoding="utf-8")
    batch = NOTE.read_text(encoding="utf-8")

    require(r"\Psi(x)=\frac1W\sum_{i=1}^J(t_i/m)^x" in batch, "Psi definition moved")
    require(r"$\tau=1-2^{-50}$" in swap, "exponent moved")
    require(r"$20\cdot2^{-50}$" in motifs, "constant moved")
    require(r"$m<2^{20}$" in motifs, "modulus bound moved")

    m = int(re.search(r"m=h\^3=(\d+)", motifs).group(1))
    block = {}
    for name in ("b", "c"):
        body = re.search(
            r"\\eta_\{\\rm " + name + r"\}.*?=\\frac\{(\d+)\}\{(\d+)\}",
            motifs,
            re.S,
        )
        require(body is not None, "eta_" + name + " moved")
        block[name] = Fraction(int(body.group(1)), int(body.group(2)))
    sb = int(re.search(r"=(\d+)<W_\{\\rm b\}m", motifs).group(1))
    sc = int(re.search(r"=(\d+)<W_\{\\rm c\}m", motifs).group(1))
    return {"m": m, "eta": block, "s": {"b": sb, "c": sc}}


def e_bounds():
    """Prove 2 < e < 2.72 with the partial sum and a geometric tail."""
    partial = sum(Fraction(1, _factorial(k)) for k in range(9))
    tail = Fraction(1, _factorial(9)) * Fraction(10, 9)
    upper = partial + tail
    require(partial + tail < Fraction(272, 100), "e < 2.72 not established")
    require(2 < partial, "e > 2 not established")
    return partial, upper


def _factorial(k):
    out = 1
    for j in range(2, k + 1):
        out *= j
    return out


def main():
    authenticate()
    data = parse()
    m = data["m"]
    require(m >= 2, "modulus below 2")
    require(m < 2 ** 20, "the manuscript's m < 2^20 fails")

    e_lo, e_hi = e_bounds()
    # ln m < 20: m < 2^20 and ln 2 < 1, which follows from 2 < e.
    require(2 < e_lo, "ln 2 < 1 not established")
    # ln m > 13: 10^6 > e^13 and e < 2.72.
    require(e_hi < Fraction(272, 100), "e < 2.72")
    require(Fraction(272, 100) ** 13 < m, "e^13 < m not established")

    step = Fraction(1, TWO50)
    summary = {}
    for name in ("b", "c"):
        eta = data["eta"][name]
        s = data["s"][name]
        require(0 < eta < 1, "eta outside (0,1)")
        w_m = Fraction(s) / (1 - eta)
        require(w_m.denominator == 1 and int(w_m) % m == 0, "role count is not integral")

        # The manuscript's displayed comparison, as an integer product.
        require(eta.numerator * TWO50 > 20 * eta.denominator,
                "20*2^-50 < eta fails on " + name)

        # ln m < 20 and eta > 20*2^-50 give 2^-50 ln m < eta.
        # Since e^x <= 1/(1-x), Psi = (1-eta) e^(2^-50 ln m) < 1.
        require(20 * step < eta, "strict margin fails on " + name)

        # Coarse threshold bracket from ln m in (13, 20) and
        # L = -ln(1-eta) in [eta, eta/(1-eta)].
        tau_lower = 1 - (eta / (1 - eta)) / 13
        tau_upper = 1 - eta / 20
        require(tau_upper < 1 - step, "the manuscript exponent is below the coarse threshold")
        require(13 * (1 - eta) > 0, "bracket sign")

        summary[name] = {
            "role_times_modulus": str(int(w_m)),
            "deficit_over_20_step": "%.6f" % float(eta / (20 * step)),
            "tau_star_bracket": [str(float(tau_lower)), str(float(tau_upper))],
        }

    print(MARKER)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
