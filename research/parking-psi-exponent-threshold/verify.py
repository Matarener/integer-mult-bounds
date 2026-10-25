#!/usr/bin/env python3
"""Sharp exponent threshold for the two motif parking recurrences.

The pinned note defines, for a child list t_1..t_J in [1, m-1] and a role
count W,

    Psi(x) = (1/W) sum_{i=1}^J (t_i/m)^x,

and proves that Psi(tau) < 1 for some 0 < tau < 1 gives F(e) = O(e^tau).
The manuscript then displays the two relative rank deficits eta_b and eta_c
and claims Psi(1-2^-50) < 1 through the sufficient comparison
eta > 20*2^-50 and log m < 20.

For a node whose child list has every t_i = 1 (the manuscript's schedule
makes s = sum_i t_i rank-one calls), Psi(tau) = (1-eta) m^(1-tau), so the
strict hypothesis is decided exactly, not only by the displayed comparison.
This program computes rigorous rational brackets for the threshold

    tau*(eta) = 1 - ln(1/(1-eta))/ln m

and for Psi(1-2^-50) on both displayed nodes, then re-checks the
manuscript's own displayed inequality.

Run with --emit to rewrite RESULT.json from the computation.
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

MARKER = "PASS_PARKING_PSI_EXPONENT_THRESHOLD"
DIGITS = 40


def fail(message):
    raise SystemExit("FAIL_PARKING_PSI_EXPONENT_THRESHOLD " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# ---------------------------------------------------------------- exact bounds

def ln_bounds(z, terms=260):
    """Rigorous rational bounds on ln z for rational z > 1.

    Write z = 2^e * s with s in [1,2).  Then ln z = e ln 2 + ln s, and both
    logarithms come from ln u = 2 atanh(y), y = (u-1)/(u+1), whose series
    has only positive terms and a geometric majorant for the tail:

        sum_{k>K} y^(2k+1)/(2k+1) <= y^(2K+3)/(2K+3) * 1/(1-y^2).
    """
    require(z > 1, "ln_bounds needs z > 1")
    exponent = 0
    scaled = Fraction(z)
    while scaled >= 2:
        scaled /= 2
        exponent += 1

    def series(u):
        y = (u - 1) / (u + 1)
        total = Fraction(0)
        for k in range(terms + 1):
            total += y ** (2 * k + 1) / (2 * k + 1)
        tail = y ** (2 * terms + 3) / (2 * terms + 3) / (1 - y * y)
        return 2 * total, 2 * (total + tail)

    ln2_lo, ln2_hi = series(Fraction(2))
    s_lo, s_hi = series(scaled)
    return exponent * ln2_lo + s_lo, exponent * ln2_hi + s_hi


def neg_ln_1m_bounds(eta):
    """Bounds on L = -ln(1-eta) = sum_{k>=1} eta^k/k for 0 < eta < 1.

    The first term is a lower bound (the rest are positive) and the
    geometric majorant of the remainder is an upper bound:

        sum_{k>=2} eta^k/k <= eta^2/2 * 1/(1-eta).
    """
    require(0 < eta < 1, "neg_ln_1m_bounds needs 0 < eta < 1")
    return eta, eta + eta * eta / (2 * (1 - eta))


def exp_bounds(u):
    """For 0 <= u <= 1: 1+u <= e^u <= 1+u+u^2/(2(1-u))."""
    require(0 <= u <= 1, "exp_bounds needs 0 <= u <= 1")
    return 1 + u, 1 + u + u * u / (2 * (1 - u))


# ------------------------------------------------------------------- source IO

def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(
        set(pinned) == {
            "notes/batched-bit-rows.tex",
            "upstream/build/sections/04-swap.tex",
            "upstream/build/sections/03-motifs.tex",
        },
        "input inventory changed",
    )
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    return sources


def parse_fraction(text, name):
    match = re.search(r"\\eta_\{\\rm " + name + r"\}(.*?)=\\frac\{(\d+)\}\{(\d+)\}", text, re.S)
    require(match is not None, "missing eta_" + name)
    return Fraction(int(match.group(2)), int(match.group(3)))


def parse_params():
    batch = NOTE.read_text(encoding="utf-8")
    swap = SWAP.read_text(encoding="utf-8")
    motifs = MOTIFS.read_text(encoding="utf-8")

    require(r"\Psi(x)=\frac1W\sum_{i=1}^J(t_i/m)^x" in batch, "the Psi definition moved")
    require(r"If $\Psi(\tau)<1$ for some $0<\tau<1$" in batch, "the strict hypothesis moved")
    require("integers in $[1,m-1]$" in batch, "the child-width range moved")
    require(r"$\tau=1-2^{-50}$" in swap, "the manuscript exponent moved in 04-swap")
    require(r"\tau=\sigma=1-2^{-50}" in motifs, "the manuscript exponent moved in 03-motifs")
    require(r"$20\cdot2^{-50}$" in motifs, "the displayed comparison constant moved")
    require(r"$m<2^{20}$" in motifs, "the modulus bound moved")

    m = int(re.search(r"m=h\^3=(\d+)", motifs).group(1))
    sb = int(re.search(r"=\s*(\d+)<W_\{\\rm b\}m", motifs).group(1))
    sc = int(re.search(r"=\s*(\d+)<W_\{\\rm c\}m", motifs).group(1))
    eta_b = parse_fraction(motifs, "b")
    eta_c = parse_fraction(motifs, "c")

    # W m = s / (1 - eta) must be an integer on each node.
    wb_m = Fraction(sb) / (1 - eta_b)
    wc_m = Fraction(sc) / (1 - eta_c)
    require(wb_m.denominator == 1, "the bit role count is not an integer")
    require(wc_m.denominator == 1, "the complex role count is not an integer")
    require(int(wb_m) % m == 0 and int(wc_m) % m == 0, "role counts are not multiples of m")
    require(m < 2 ** 20, "the manuscript modulus bound is false")

    exponent = Fraction(1) - Fraction(1, 2 ** 50)
    require(0 < exponent < 1, "the manuscript exponent is outside (0,1)")
    require(1 - exponent == Fraction(1, 2 ** 50), "the exponent step moved")

    return {
        "m": m,
        "exponent": exponent,
        "nodes": {
            "bit": {"eta": eta_b, "s": sb, "w_m": int(wb_m), "w": int(wb_m) // m},
            "complex": {"eta": eta_c, "s": sc, "w_m": int(wc_m), "w": int(wc_m) // m},
        },
    }


# ------------------------------------------------------------------ the result

def compute(params, manuscript=True):
    m = params["m"]
    exponent = params["exponent"]
    ln_m_lo, ln_m_hi = ln_bounds(Fraction(m))

    # The exponent step, bounded above through ln m; m^(1-tau) = exp(step ln m).
    step = 1 - exponent
    require(0 < step <= 1, "the exponent step is outside (0,1]")
    u_hi = step * ln_m_hi
    m_pow_lo, m_pow_hi = exp_bounds(u_hi)

    thresholds = {}
    result = {
        "schema_version": 1,
        "modulus": m,
        "exponent": "1-2^-50",
        "two_to_50": str(2 ** 50),
        "ln_m_decimal_lower": fmt_down(ln_m_lo),
        "ln_m_decimal_upper": fmt_up(ln_m_hi),
        "m_to_step_decimal_lower": fmt_down(m_pow_lo),
        "m_to_step_decimal_upper": fmt_up(m_pow_hi),
        "nodes": {},
        "manuscript": {},
    }

    for name, node in params["nodes"].items():
        eta = node["eta"]
        require(0 < eta < 1, "eta outside (0,1)")
        require((eta * node["w_m"]).denominator == 1, "the deficit is not an integer")
        require(
            node["s"] == node["w_m"] - int(eta * node["w_m"]),
            "s does not match the deficit",
        )

        # Psi(tau) = (1-eta) m^(1-tau) for an all-width-one node.
        psi_lo = (1 - eta) * m_pow_lo
        psi_hi = (1 - eta) * m_pow_hi
        require(psi_hi < 1, "Psi at the manuscript exponent is not below 1 on " + name)

        l_lo, l_hi = neg_ln_1m_bounds(eta)
        tau_lo = 1 - l_hi / ln_m_lo
        tau_hi = 1 - l_lo / ln_m_hi
        require(tau_hi < exponent, "the manuscript exponent is below the threshold on " + name)

        thresholds[name] = (tau_lo, tau_hi)
        deficit_lo = 1 - tau_hi
        deficit_hi = 1 - tau_lo
        margin = 1 - psi_hi
        require(margin > 0, "empty margin on " + name)

        result["nodes"][name] = {
            "eta": [eta.numerator, eta.denominator],
            "child_count": str(node["s"]),
            "role_count": str(node["w"]),
            "role_times_modulus": str(node["w_m"]),
            "deficit": str(int(eta * node["w_m"])),
            "psi_decimal_upper": fmt_up(psi_hi),
            "psi_margin_decimal_lower": fmt_down(margin),
            "tau_star_decimal_lower": fmt_down(tau_lo),
            "tau_star_decimal_upper": fmt_up(tau_hi),
            "tau_star_deficit_decimal_lower": fmt_down(deficit_lo),
            "tau_star_deficit_decimal_upper": fmt_up(deficit_hi),
            "deficit_over_manuscript_constant_decimal": fmt_down(eta / (20 * step)),
        }

    # A single exponent serves both recurrences, so it must clear the larger
    # of the two thresholds.
    tau_lo = max(lo for lo, _ in thresholds.values())
    tau_hi = max(hi for _, hi in thresholds.values())
    require(tau_hi < exponent, "the manuscript exponent is below the joint threshold")
    result["joint"] = {
        "binding_node": max(thresholds, key=lambda name: thresholds[name][1]),
        "tau_star_decimal_lower": fmt_down(tau_lo),
        "tau_star_decimal_upper": fmt_up(tau_hi),
        "tau_star_deficit_decimal_lower": fmt_down(1 - tau_hi),
        "tau_star_deficit_decimal_upper": fmt_up(1 - tau_lo),
        "step_over_threshold_deficit_decimal": fmt_down(step / (1 - tau_hi)),
    }

    if manuscript:
        # The manuscript's displayed criterion: eta > 20*2^-50 and log m < 20.
        for name, node in params["nodes"].items():
            eta = node["eta"]
            require(eta > 20 * step, "the displayed deficit comparison fails on " + name)
            require(ln_m_hi < 20, "log m < 20 fails")
            result["manuscript"][name] = {
                "deficit_above_constant": True,
                "log_m_below_20": True,
            }

        # The sharp sufficient comparison replaces 20 by ln m on both nodes.
        for name, node in params["nodes"].items():
            require(ln_m_hi < node["eta"] / step, "the sharp constant does not cover " + name)

    return result


def fmt_down(value, digits=DIGITS):
    """Truncated decimal expansion of a positive rational (a lower bound)."""
    require(value > 0, "fmt_down needs a positive rational")
    scale = 10 ** digits
    scaled = value.numerator * scale // value.denominator
    text = str(scaled).rjust(digits + 1, "0")
    return text[:-digits] + "." + text[-digits:]


def fmt_up(value, digits=DIGITS):
    """Truncated expansion plus one unit in the last place (an upper bound)."""
    require(value > 0, "fmt_up needs a positive rational")
    scale = 10 ** digits
    scaled = (value.numerator * scale + value.denominator - 1) // value.denominator
    text = str(scaled).rjust(digits + 1, "0")
    return text[:-digits] + "." + text[-digits:]


def main(argv):
    authenticate()
    params = parse_params()
    observed = compute(params)
    stored_path = PACKAGE / "RESULT.json"
    if "--emit" in argv:
        stored_path.write_text(json.dumps(observed, indent=2) + "\n", encoding="utf-8")
        print("WROTE " + str(stored_path))
        return
    stored = json.loads(stored_path.read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main(sys.argv[1:])
