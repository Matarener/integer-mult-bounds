#!/usr/bin/env python3
"""Occupied CRT colors are at most the layout batch cap."""

import hashlib
from fractions import Fraction
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CRT = ROOT / "research/unconditional-batched-crt/CRT.md"
ALLOCATOR = ROOT / "research/pr4100-guard-coloring/vendor/pr4174_allocator.py"
CRT_SHA = "02c3a1e38cbee25aefe2640cc72676da62ba10eb7519fbcb9adb9d48b74eff2b"
ALLOCATOR_SHA = "b764195fc6291e3c8fa8297b1f4ceaefc119d5664d8ff348b49eac8a2e79c688"

COLOR_SENTENCE = (
    "Color targets by current position modulo K, so guard intervals are disjoint.\n"
    "This uses O(K)=O(ell+log p) colors."
)
ONE_COLOR_SENTENCE = (
    "One color uses O(1) ordinary H-bit interchanges plus linear scans and paid\n"
    "repair. It costs O(V H^(1-a)+V). With K colors and H<=L=O(p), one switch\n"
    "layer costs O(V p^(1-a) (ell+log p)), including placement and restoration."
)
SECTION_FIVE = "O(V p^(1-a) ell^2 polylog p)."
FORMULA_LINES = (
    "guard_digit_bits = 64 * (ell + logarithm)",
    '("K", 64 * guard_digit_bits)',
    '("r_max", maximum_batch)',
    "maximum_batch = length // (100 * guard_digit_bits)",
    "active = tuple(islice(axes, layout.r_max))",
)


def fail(message):
    raise SystemExit("FAIL_CRT_OCCUPIED_COLOR_MACROS " + message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ceil_log2(value):
    if value < 1:
        fail("logarithm argument")
    exponent = 0
    power = 1
    while power < value:
        power *= 2
        exponent += 1
    return exponent


def layout(ell, widths):
    """The pinned Layout arithmetic. p = 6L, as in the coloring census."""
    length = sum(widths)
    precision = 6 * length
    logarithm = ceil_log2(precision + 2)
    if ell < logarithm:
        fail("ell below ceil(log2(p+2))")
    guard = 64 * (ell + logarithm)
    batch_cap = length // (100 * guard)
    if batch_cap < 1 or 100 * batch_cap * guard > length:
        fail("layout rejected its own volume bound")
    return {
        "L": length,
        "logarithm": logarithm,
        "G": guard,
        "K": 64 * guard,
        "r_max": batch_cap,
        "H": batch_cap * guard,
    }


def occupied(positions, modulus):
    return len({position % modulus for position in positions})


def check_phrases(crt, allocator):
    if COLOR_SENTENCE not in crt or ONE_COLOR_SENTENCE not in crt:
        fail("CRT.md no longer states the K-color layer charge")
    if SECTION_FIVE not in crt:
        fail("section 5 aggregate is missing")
    if "occupied" in ONE_COLOR_SENTENCE or "r_max" in ONE_COLOR_SENTENCE:
        fail("the written one-color sentence already prices the cap")
    for line in FORMULA_LINES:
        if line not in allocator:
            fail("allocator no longer defines " + line)


def check_color_lemma():
    modulus = 6
    universe = range(12)
    checked = 0
    for size in range(len(universe) + 1):
        for subset in combinations(universe, size):
            count = occupied(subset, modulus)
            if count > min(size, modulus):
                fail("occupied colors exceeded min(r, K)")
            distinct = len({position % modulus for position in subset}) == size
            if (count == size) != distinct:
                fail("equality c = r disagreed with distinct residues")
            checked += 1
    if checked != 2**12:
        fail("subset census changed size")
    if occupied((0, modulus), modulus) != 1:
        fail("targets K apart did not share a color")
    if occupied((0, 1, modulus), modulus) != 2:
        fail("a third residue was lost")
    if occupied(range(modulus), modulus) != modulus:
        fail("a full set of residues was not K colors")
    # A per-target bill on a collision, or a per-residue bill on a singleton, overcharges.
    if not (occupied((0, modulus), modulus) < 2 and occupied((0,), modulus) < modulus):
        fail("control: the overcharging bills were not strict")


def check_production():
    alternating = layout(24, tuple(24 if index % 2 == 0 else 23 for index in range(65536)))
    expect = {"L": 1540096, "logarithm": 24, "G": 3072, "K": 196608, "r_max": 5, "H": 15360}
    if alternating != expect:
        fail("production layout " + str(alternating))
    y_bits = (alternating["L"] - alternating["H"]) - 2 * alternating["H"]
    if y_bits != 1494016:
        fail("production y-bit count")
    if alternating["K"] * 1 <= alternating["r_max"]:
        fail("the cap did not tighten the color factor")
    if Fraction(alternating["K"], alternating["r_max"]) != Fraction(196608, 5):
        fail("production ratio")
    uniform_short = layout(24, tuple(23 for _ in range(65536)))
    if uniform_short["L"] != 1507328 or uniform_short["K"] != 196608 or uniform_short["r_max"] != 4:
        fail("uniform ell-1 layout " + str(uniform_short))
    if uniform_short["K"] // uniform_short["r_max"] != 49152:
        fail("uniform ell-1 ratio")
    # The cap binds collisions as well as singletons.
    for positions, residue_count in (((0, alternating["K"]), 1), ((0, 1), 2)):
        if occupied(positions, alternating["K"]) != residue_count:
            fail("production residue example")
        if residue_count > alternating["r_max"] and len(positions) <= alternating["r_max"]:
            fail("a legal batch exceeded the cap")


def main():
    crt_bytes = CRT.read_bytes()
    allocator_bytes = ALLOCATOR.read_bytes()
    if sha256(CRT) != CRT_SHA or hashlib.sha256(crt_bytes).hexdigest() != CRT_SHA:
        fail("CRT.md hash")
    if sha256(ALLOCATOR) != ALLOCATOR_SHA:
        fail("allocator hash")
    crt = crt_bytes.decode()
    allocator = allocator_bytes.decode()
    check_phrases(crt, allocator)
    check_color_lemma()
    check_production()
    print(
        "PASS_CRT_OCCUPIED_COLOR_MACROS "
        "K=196608 r_max=5 ratio=196608/5 "
        "uniform23_r_max=4 ratio=49152 "
        "same_color_pair_macros=1 "
        "no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
