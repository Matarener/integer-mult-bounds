#!/usr/bin/env python3
"""Evaluate Psi at one half on the bit-motif parking node.

Each recursive call has width e/m, so the child list is s copies of width 1.
The role count is W_b and the modulus is m. This check does not replay the
network.
"""

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BATCH = ROOT / "notes/batched-bit-rows.tex"
SWAP = ROOT / "upstream/build/sections/04-swap.tex"
MOTIFS = ROOT / "upstream/build/sections/03-motifs.tex"
MARKER = "PASS_UNIFORM_PARKING_PSI psi_below_one=false no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_UNIFORM_PARKING_PSI " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def psi_half(child_width, child_count, roles, modulus):
    require(child_width > 0 and roles > 0 and modulus % child_width == 0, "widths")
    unit = modulus // child_width
    root = int(unit ** 0.5)
    require(root * root == unit, "square-root modulus")
    return Fraction(child_count, roles) / root


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
    batch = BATCH.read_text(encoding="utf-8")
    swap = SWAP.read_text(encoding="utf-8")
    motifs = MOTIFS.read_text(encoding="utf-8")
    require(r"\Psi(x)=\frac1W\sum_{i=1}^J(t_i/m)^x" in batch, "the Psi definition moved")
    require("park only the other role streams" in batch, "the batched parking sentence moved")
    require("append the $W-1$ inactive role streams" in swap, "the swap parking sentence moved")
    require("exactly $s$." in swap, "the recursive-call count moved")
    require(r"b=e/m" in swap, "the child field width moved")
    modulus = integer_after(motifs, r"m=h\^3=([0-9]+)")
    block = integer_after(motifs, r"N=v\^3=([0-9]+)")
    rank_sum = integer_after(motifs, r"=([0-9]+)<W_\{\\rm b\}m")
    require(r"\frac{L_{\rm b}}{N}=\frac{100}{539}" in motifs, "the L_b ratio moved")
    require(r"\frac{339}{22587335000000}" in motifs, "the displayed deficit ratio moved")
    require(block * 100 % 539 == 0, "L_b is not an integer")
    level = block * 100 // 539
    deficit = block - 2 * level
    roles_times_modulus = rank_sum + deficit
    require(roles_times_modulus % modulus == 0, "the role count is not an integer")
    roles = roles_times_modulus // modulus
    require(Fraction(deficit, roles_times_modulus) == Fraction(339, 22587335000000), "the deficit ratio moved")
    value = psi_half(1, rank_sum, roles, modulus)
    require(value == Fraction(22587334999661, 22587335000) and value > 1, "Psi at one half moved")
    return {
        "node": "bit-motif power-width parking schedule",
        "modulus": modulus,
        "child_width": 1,
        "child_count": str(rank_sum),
        "role_count": str(roles),
        "psi_half": str(value),
        "psi_half_below_one": False,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
