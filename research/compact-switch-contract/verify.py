#!/usr/bin/env python3
"""Audit the #4100 compact-switch cancellation contract.

The predecessor display and the cancellation paragraph do not bind the same
second coefficient. This verifier does not import a theorem from that prose.
It checks an independent post-increment identity, a frozen-coefficient
counterexample, and an overlapping-guard counterexample. The published
checker is consulted only as a binding control on one witness.

No new kappa and no multiplication theorem are claimed.
"""

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CRT = ROOT / "research/unconditional-batched-crt/CRT.md"
CHECKER = ROOT / "research/unconditional-batched-crt/check_batched_crt.py"

DISPLAY = (
    "y += sum_i 2 z_i t_i 2^j_i;\n"
    "    t += sum_i y[j_i] B^i;\n"
    "    y += sum_i z_i (1-2t_i) 2^j_i;"
)
PROSE_TOTAL = "total z(1-2b)2^j"


def need(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def load_checker():
    spec = importlib.util.spec_from_file_location("batched_crt_predecessor", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def post_step(y, z, tau):
    """One target at bit 0. Second coefficient is the post-increment digit."""
    y1 = y + 2 * z * tau
    bit = y1 & 1
    tau_post = tau + bit
    y2 = y1 + z * (1 - 2 * tau_post)
    return y1, y2, tau_post, bit


def frozen_step(y, z, tau):
    """Same additions with the original digit reused after the t update."""
    y1 = y + 2 * z * tau
    bit = y1 & 1
    y2 = y1 + z * (1 - 2 * tau)
    return y1, y2, bit


def sharp_windows():
    """Isolated cancellation for every legal window, plus the first overflow."""
    safe_cases = overflow_cases = 0
    for bits in (1, 2, 3, 4):
        base = 1 << bits
        width = 8
        limit = 1 << width
        safe_last = limit - (base - 2) - 1
        for tau in range(base - 1):
            for bit in (0, 1):
                for parity in (0, 1):
                    for window in range(safe_last + 1):
                        y = bit + (window << 1)
                        y1, y2, tau_post, read_bit = post_step(y, parity, tau)
                        need(read_bit == bit, "post-increment keeps the target bit")
                        need(tau_post == tau + bit, "digit increments by the original target")
                        need(tau_post <= base - 1, "updated digit does not carry")
                        final_bit = y2 & 1
                        restored = tau_post - (final_bit ^ parity)
                        need(restored == tau and 0 <= restored < base, "control digit restores")
                        need(0 <= (y1 >> 1) < limit, "step-one window stays inside")
                        need(y2 == y + parity * (1 - 2 * bit), "net addend is z(1-2b)")
                        need(final_bit == (bit ^ parity), "target flips exactly by z")
                        need((y2 >> 1) == window and y2 >= 0, "window and sign restore")
                        safe_cases += 1
        if base == 2:
            continue
        tau = base - 2
        window = limit - (base - 2)
        y = 0 + (window << 1)
        y1, _, _, _ = post_step(y, 1, tau)
        need((y1 >> 1) >= limit, "sharp upper window overflows on step one")
        overflow_cases += 1
    return safe_cases, overflow_cases


def published_is_subset():
    """The printed 2B margin implies the sharp window bound, and is stricter."""
    checked = excluded = 0
    for bits in (2, 3, 4):
        base = 1 << bits
        width = 8
        limit = 1 << width
        for window in range(limit):
            published = 2 * base <= window < limit - 2 * base
            sharp = window <= limit - (base - 2) - 1
            if published:
                need(sharp, "published margin leaves the sharp range")
                checked += 1
            elif sharp:
                excluded += 1
    need(excluded > 0, "published margin is a proper subset")
    return checked, excluded


def good(u, t, y, bits, positions, guard):
    base = 1 << bits
    width = guard - 1
    limit = 1 << width
    for index, pos in enumerate(positions):
        u_digit = (u >> (bits * index)) & (base - 1)
        t_digit = (t >> (bits * index)) & (base - 1)
        window = (y >> (pos + 1)) & (limit - 1)
        if u_digit == base - 1 or t_digit == base - 1:
            return False
        if not 2 * base <= window < limit - 2 * base:
            return False
    return True


def macro(u, t, y, source, bits, positions, ybits, control_bits, frozen=False):
    base = 1 << bits
    control_mask = (1 << control_bits) - 1
    ymask = (1 << ybits) - 1

    def one_f(u0, t0, y0):
        parity = [(u0 >> (bits * i)) & 1 for i in range(len(positions))]
        digits = [(t0 >> (bits * i)) & (base - 1) for i in range(len(positions))]
        y1 = y0 + sum(
            2 * parity[i] * digits[i] * (1 << positions[i]) for i in range(len(positions))
        )
        t1 = t0 + sum(((y1 >> positions[i]) & 1) << (bits * i) for i in range(len(positions)))
        live = digits if frozen else [
            (t1 >> (bits * i)) & (base - 1) for i in range(len(positions))
        ]
        y2 = y1 + sum(
            parity[i] * (1 - 2 * live[i]) * (1 << positions[i]) for i in range(len(positions))
        )
        t2 = t1 - sum(
            (((y2 >> positions[i]) & 1) ^ parity[i]) << (bits * i)
            for i in range(len(positions))
        )
        return u0 & control_mask, t2 & control_mask, y2 & ymask

    u, t, y = one_f(u, t, y)
    loaded = source(y)
    u = (u + sum(loaded[i] << (bits * i) for i in range(len(positions)))) & control_mask
    u, t, y = one_f(u, t, y)
    unloaded = source(y)
    u = (u - sum(unloaded[i] << (bits * i) for i in range(len(positions)))) & control_mask
    return u, t, y


def ideal_y(y, source, positions):
    values = source(y)
    for value, pos in zip(values, positions):
        y ^= value << pos
    return y


def single_target_macro():
    passes = 0
    for control in range(16):
        for other in range(16):
            for y in range(256):
                if not good(control, other, y, 2, (0,), 6):
                    continue
                for value in (0, 1):
                    source = lambda word, value=value: (value,)
                    end = macro(control, other, y, source, 2, (0,), 8, 4)
                    need(end == (control, other, y ^ value), "single-target post-increment macro")
                    passes += 1
    return passes


def disjoint_pair_macro():
    positions = (0, 8)
    passes = 0

    def source(word):
        return (word >> 3) & 1, (word >> 12) & 1

    for control in range(16):
        for other in range(16):
            for y in range(1 << 14):
                if not good(control, other, y, 2, positions, 6):
                    continue
                end = macro(control, other, y, source, 2, positions, 14, 4)
                need(end == (control, other, ideal_y(y, source, positions)),
                     "disjoint post-increment macro")
                passes += 1
    return passes


def controls(predecessor):
    # Good address: B=4, tau=0, b=1, z=1, W=8. Display-frozen reading carries.
    control, other, y = 1, 0, 17
    need(good(control, other, y, 2, (0,), 6), "frozen witness is published-good")
    _, post_field, _, _ = post_step(y, 1, 0)
    _, frozen_field, _ = frozen_step(y, 1, 0)
    need(post_field == 16, "one post-increment step flips bit 0")
    need(frozen_field == 18, "one frozen step carries into the guard")
    post = macro(control, other, y, lambda word: (0,), 2, (0,), 8, 4)
    frozen = macro(control, other, y, lambda word: (0,), 2, (0,), 8, 4, frozen=True)
    need(post == (1, 0, 17), "two post-increment steps with f=0 restore y")
    need(frozen == (1, 0, 19), "two frozen steps with f=0 do not restore y")
    bound = predecessor.primitive_f(1, 0, 17, 2, (0,), 8, 4)
    need(bound == (1, 0, 16), "published primitive_f follows the post-increment digit")
    bound_macro = predecessor.compact(1, 0, 17, lambda word: (0,), bits=2, positions=(0,),
                                      ybits=8, control_bits=4)
    need(bound_macro == (1, 0, 17), "published compact restores a zero source")

    # Targets one bit apart. Each window meets the printed margin; t is not restored.
    overlap_u, overlap_t, overlap_y = 0, 1, 80
    positions = (0, 1)

    def overlap_source(word):
        return (word >> 4) & 1, (word >> 5) & 1

    need(good(overlap_u, overlap_t, overlap_y, 2, positions, 6),
         "overlap witness meets the per-target margin")
    overlap = macro(overlap_u, overlap_t, overlap_y, overlap_source, 2, positions, 10, 4)
    wanted = (0, 1, ideal_y(overlap_y, overlap_source, positions))
    need(overlap == (0, 5, 81) and overlap != wanted,
         "overlapping good targets fail the ideal restoration")

    # A source that reads the target changes between load and unload.
    def reads_target(word):
        return (word & 1,)

    leak = macro(1, 0, 17, reads_target, 2, (0,), 8, 4)
    need(leak != (1, 0, 17 ^ 1), "target-dependent source is not restored")
    return {
        "one_step_post_y": post_field,
        "one_step_frozen_y": frozen_field,
        "zero_source_post": list(post),
        "zero_source_frozen": list(frozen),
        "overlap_witness": [overlap_u, overlap_t, overlap_y, list(overlap), list(wanted)],
        "target_source_end": list(leak),
    }


def main():
    text = CRT.read_text(encoding="utf-8")
    need(DISPLAY in text, "CRT.md display changed")
    need(PROSE_TOTAL in text, "CRT.md cancellation sentence changed")
    predecessor = load_checker()
    safe_cases, overflow_cases = sharp_windows()
    published_cases, excluded_cases = published_is_subset()
    single_passes = single_target_macro()
    disjoint_passes = disjoint_pair_macro()
    rejected = controls(predecessor)
    receipt = {
        "status": "PASS_COMPACT_SWITCH_CONTRACT",
        "safe_window_cases": safe_cases,
        "sharp_overflow_cases": overflow_cases,
        "published_margin_cases": published_cases,
        "sharp_only_windows": excluded_cases,
        "single_target_macros": single_passes,
        "disjoint_pair_macros": disjoint_passes,
        "controls": rejected,
        "new_kappa": False,
        "multiplication_theorem": False,
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
