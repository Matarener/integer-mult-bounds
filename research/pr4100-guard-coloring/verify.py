#!/usr/bin/env python3
"""Guard windows under #4100 CRT.md's position-mod-K coloring, on #4174's descriptors.

Standard library only. Three parts:

1. An exhaustive check of the window lemma on small position sets.
2. The compact gadget from #4100's own check_batched_crt.py on every one of
   the 2^20 two-target addresses with targets exactly K apart: (K-1)-bit
   guards versus literal K-bit guards.
3. A census of every one of #4174's production placement plans (vendored
   allocator, byte-checked): targets in y, same-color pairs for any Beneš
   bit schedule, exact-K spacings, and last-K exceptions.

Finite evidence for the written lemma in README.md. Ryanson Jonathan with
Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "research/unconditional-batched-crt"
ALLOCATOR_SHA256 = "b764195fc6291e3c8fa8297b1f4ceaefc119d5664d8ff348b49eac8a2e79c688"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


PHRASES = [
    "from both ends of each K-bit guard. Its bad density is at most",
    "    r [2/B + 8B/2^K] <= C p 2^-G.",
    "Color targets by current position modulo K, so guard intervals are disjoint.",
]
CODE_PHRASE = "2 * radix <= ((y >> (pos + 1)) & ((1 << (guard - 1)) - 1))"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolve string annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def check_sources():
    pins = {row["path"]: row["sha256"]
            for row in json.loads((HERE / "SOURCES.json").read_text())["files"]}
    for rel in ("research/unconditional-batched-crt/CRT.md",
                "research/unconditional-batched-crt/check_batched_crt.py"):
        need(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == pins[rel], f"pin {rel}")
    text = (SOURCE / "CRT.md").read_text()
    for phrase in PHRASES:
        need(phrase in text, f"CRT.md phrase missing: {phrase}")
    need(CODE_PHRASE in (SOURCE / "check_batched_crt.py").read_text(), "good() uses guard-1 window bits")
    vendored = HERE / "vendor/pr4174_allocator.py"
    need(hashlib.sha256(vendored.read_bytes()).hexdigest() == ALLOCATOR_SHA256,
         "vendored #4174 allocator bytes (head 5fec853f, blob 4b3ad896)")
    return load("pr4100_crt", SOURCE / "check_batched_crt.py"), load("pr4174_allocator", vendored), len(PHRASES) + 2


# --- 1. The window lemma ------------------------------------------------------------

def windows_ok(targets, K, width):
    """Same-color (mod K) targets: are their width-bit windows above them free of active targets
    and pairwise disjoint?"""
    for c in range(K):
        same = sorted(j for j in targets if j % K == c)
        for a, b in itertools.combinations(same, 2):
            if a < b <= a + width:          # b inside a's window [a+1, a+width]
                return False
            if b + 1 <= a + width:          # windows overlap (b's window starts at b+1)
                return False
    return True


def check_lemma():
    cases = 0
    for K in (3, 4, 6):
        span = range(4 * K)
        for size in (2, 3):
            for targets in itertools.combinations(span, size):
                need(windows_ok(targets, K, K - 1), "(K-1)-bit windows are always disjoint and target-free")
                exact_k = any(b - a == K for a, b in itertools.combinations(sorted(targets), 2))
                need(windows_ok(targets, K, K) == (not exact_k),
                     "K-bit windows fail exactly when two same-color targets are K apart")
                cases += 1
    return cases


# --- 2. #4100's gadget with K-bit versus (K-1)-bit guards ---------------------------------

SOURCES_2T = {
    "source_pair": lambda y: ((y >> 3) & 1, (y & ~65).bit_count() & 1),   # #4100's own two-target source
    "mixed_pair": lambda y: (((y >> 1) & 1) ^ ((y >> 11) & 1), ((y >> 5) & 1) & ((y >> 8) & 1)),
}


def check_gadget(crt):
    """Targets at 0 and 6 (K = 6 apart), B = 4; guard g means g-1 window bits in the code."""
    rows = []
    for name, fn in SOURCES_2T.items():
        for guard in (6, 7):
            good_n = disagree = leaves = 0
            example = None
            for u in range(16):
                for t in range(16):
                    for y in range(1 << 12):
                        if not crt.good(u, t, y, bits=2, positions=(0, 6), guard=guard):
                            continue
                        good_n += 1
                        f0, f1 = fn(y)
                        ideal = (u, t, y ^ f0 ^ (f1 << 6))
                        actual = crt.compact(u, t, y, fn, positions=(0, 6), ybits=12, control_bits=4)
                        if actual != ideal:
                            disagree += 1
                            example = example or [[u, t, y], list(actual), list(ideal)]
                        if not crt.good(*ideal, bits=2, positions=(0, 6), guard=guard):
                            leaves += 1
            rows.append(dict(source=name, window_bits=guard - 1, good=good_n,
                             S_differs_from_T_on_good=disagree, T_leaves_good_set=leaves,
                             example=example))
            if guard == 6:
                need(disagree == 0 and leaves == 0, "(K-1)-bit guards: the gadget is the ideal switch")
            else:
                need(disagree > 0 and leaves > 0, "K-bit guards at spacing K: the gadget fails on good addresses")
    return rows


# --- 3. Census of #4174's production plans -------------------------------------------------

def census(alloc, ell, widths):
    d = len(widths)
    length = sum(widths)
    layout = alloc.Layout(6 * length, ell, widths)
    L, H, K = layout.L, layout.H, layout.K
    y_lo, y_hi = 2 * H, L - H
    ylen = y_hi - y_lo
    stats = dict(d=d, ell=ell, L=L, G=layout.G, K=K, r_max=layout.r_max, H=H, y_bits=ylen,
                 plans=0, axis_visits=0, fragments=0, targets_outside_y=0,
                 possible_same_color_pairs=0, possible_exact_K_pairs=0,
                 plans_with_possible_exception_axes=0,
                 aligned_target_visits=0, aligned_max_color_multiplicity=0,
                 aligned_multi_target_colors=0, aligned_exact_K_pairs=0,
                 aligned_exception_layers=0, aligned_max_exceptions_per_layer=0,
                 max_pair_distance=0)
    for plan in alloc.iter_plans(layout):
        stats["plans"] += 1
        frags = []
        for dep in plan.dependencies:
            lo, hi = dep.own_interval
            fr = plan.map_interval(lo, hi)
            for f in fr:
                a, b = f.image_interval
                if not (y_lo <= a and b <= y_hi):
                    stats["targets_outside_y"] += 1
            frags.append((dep.axis, lo, hi, fr))
            stats["axis_visits"] += 1
            stats["fragments"] += len(fr)
        # Schedule-independent: can any bit of one active axis share a color with any bit of another?
        exception_axes = 0
        for _, lo, hi, fr in frags:
            if any(f.image_interval[0] < y_lo + K - 1 for f in fr):
                exception_axes += 1
        stats["plans_with_possible_exception_axes"] += exception_axes > 0
        for (_, _, _, fa), (_, _, _, fb) in itertools.combinations(frags, 2):
            for f, g in itertools.product(fa, fb):
                dmin = g.image_interval[0] - (f.image_interval[1] - 1)
                dmax = (g.image_interval[1] - 1) - f.image_interval[0]
                stats["max_pair_distance"] = max(stats["max_pair_distance"], abs(dmin), abs(dmax))
                lo_m, hi_m = -(-dmin // K), dmax // K   # multiples of K in [dmin, dmax]
                if any(m != 0 for m in range(lo_m, hi_m + 1)):
                    stats["possible_same_color_pairs"] += 1
                if (dmin <= K <= dmax) or (dmin <= -K <= dmax):
                    stats["possible_exact_K_pairs"] += 1
        # Aligned Beneš schedule: at bit m, every active axis wider than m targets its bit m.
        for m in range(ell):
            js = []
            for _, lo, hi, fr in frags:
                if hi - lo <= m:
                    continue
                orig = hi - 1 - m
                for f in fr:
                    if f.original_interval[0] <= orig < f.original_interval[1]:
                        cur = orig + f.delta
                        break
                js.append((y_hi - 1) - cur)
            stats["aligned_target_visits"] += len(js)
            colors = {}
            for j in js:
                colors.setdefault(j % K, []).append(j)
            for same in colors.values():
                stats["aligned_max_color_multiplicity"] = max(stats["aligned_max_color_multiplicity"], len(same))
                if len(same) > 1:
                    stats["aligned_multi_target_colors"] += 1
                    same.sort()
                    gaps = [b - a for a, b in zip(same, same[1:])]
                    # (K-1)-bit windows [j+1, j+K-1]: disjoint and free of the other targets iff every gap >= K.
                    need(all(gap >= K for gap in gaps), "(K-1)-bit windows are target-free on actual descriptors")
                    stats["aligned_exact_K_pairs"] += sum(gap == K for gap in gaps)
            exceptions = sum(j > ylen - K for j in js)
            if exceptions:
                stats["aligned_exception_layers"] += 1
                stats["aligned_max_exceptions_per_layer"] = max(stats["aligned_max_exceptions_per_layer"], exceptions)
    need(stats["targets_outside_y"] == 0, "every active axis lies in y after placement")
    need(stats["aligned_max_color_multiplicity"] <= stats["r_max"], "a color never exceeds the batch")
    return stats


def random_widths(ell, seed, short_fraction):
    """Deterministic pseudo-random ell/ell-1 pattern (64-bit LCG, no external state)."""
    state, out = seed, []
    for _ in range(65536):
        state = (6364136223846793005 * state + 1442695040888963407) % (1 << 64)
        out.append(ell - 1 if (state >> 11) / (1 << 53) < short_fraction else ell)
    return tuple(out)


HALF = 32768
PATTERNS = [
    ("alternating 24/23 (#4174 production)", 24, tuple(24 - (i % 2) for i in range(65536))),
    ("blocked: 24 on axes 0..32767, then 23", 24, (24,) * HALF + (23,) * HALF),
    ("blocked: 23 on axes 0..32767, then 24", 24, (23,) * HALF + (24,) * HALF),
    ("uniform 24", 24, (24,) * 65536),
    ("uniform 23 (all ell-1)", 24, (23,) * 65536),
    ("random, half short, seed 4100", 24, random_widths(24, 4100, 0.5)),
    ("random, half short, seed 4174", 24, random_widths(24, 4174, 0.5)),
    ("random, 1/8 short, seed 4329", 24, random_widths(24, 4329, 0.125)),
    ("alternating 32/31", 32, tuple(32 - (i % 2) for i in range(65536))),
]


def with_short(shorts):
    widths = [24] * 65536
    for i in shorts:
        widths[i] = 23
    return tuple(widths)


# Uniform 24 misses a multiple of K by one bit: at level 14, batch 1638 pairs axes 16383 and
# 24576, which are 8,193 axes = 196,632 = K + 24 bits apart. Shortening axes between them
# lands pairs exactly on K. Both patterns are admitted by #4174's Layout.
ADVERSARIAL = [
    ("uniform 24, one ell-1 axis at 20000", 24, with_short([20000]), "possible"),
    ("uniform 24, ell-1 axes 16384..16407", 24, with_short(range(16384, 16408)), "aligned"),
]


def main():
    crt, alloc, phrases = check_sources()
    lemma_cases = check_lemma()
    gadget = check_gadget(crt)
    production = census(alloc, 24, PATTERNS[0][2])
    need(production["plans"] == 104864 and production["axis_visits"] == 524288,
         "same plan count as #4174's production census")
    patterns = [dict(pattern=PATTERNS[0][0], short_axes=PATTERNS[0][2].count(23), **production)]
    for name, ell, widths in PATTERNS[1:]:
        patterns.append(dict(pattern=name, short_axes=widths.count(ell - 1), **census(alloc, ell, widths)))
    for row in patterns:
        need(row["possible_same_color_pairs"] == 0 and row["aligned_max_color_multiplicity"] == 1,
             f"no same-color pair on the regular pattern {row['pattern']}")
    for name, ell, widths, kind in ADVERSARIAL:
        row = dict(pattern=name, short_axes=widths.count(ell - 1), **census(alloc, ell, widths))
        need(row["possible_exact_K_pairs"] > 0, f"exact-K spacing reachable on {name}")
        if kind == "aligned":
            need(row["aligned_exact_K_pairs"] > 0, f"aligned schedule puts same-color targets exactly K apart on {name}")
        patterns.append(row)
    print(json.dumps({
        "status": "PASS_PR4100_GUARD_COLORING_FINITE",
        "source_bindings": phrases,
        "lemma_cases": lemma_cases,
        "gadget": gadget,
        "production_census": production,
        "pattern_census": [{k: row[k] for k in (
            "pattern", "ell", "short_axes", "L", "K", "r_max", "plans", "targets_outside_y",
            "possible_same_color_pairs", "possible_exact_K_pairs", "aligned_target_visits",
            "aligned_max_color_multiplicity", "aligned_multi_target_colors", "aligned_exact_K_pairs",
            "plans_with_possible_exception_axes", "aligned_max_exceptions_per_layer", "max_pair_distance")}
            for row in patterns],
        "all_size_theorem_claimed": False,
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
