#!/usr/bin/env python3
"""Check the new guard menu and its logical compact-switch composition.

Standard library only. Normal replay writes nothing. The quantified lower
and upper bounds are proved in PROOF.md; these finite checks corroborate
them and exercise the new conjugated interface, not predecessor receipts.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import hashlib
from itertools import product
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Geometry:
    targets: int
    bits: int
    window_bits: int

    def __post_init__(self) -> None:
        # Bounds belong to this finite checker, not the written theorem.
        need(1 <= self.targets <= 4, "checker target capacity")
        need(2 <= self.bits <= 4, "checker radix capacity")
        need(self.bits <= self.window_bits <= 8, "checker window capacity")
        need(self.phases <= self.base, "not enough distinct digit phases")
        need(self.phases * self.bad_width <= self.window, "overlapping window phases")

    @property
    def base(self) -> int:
        return 1 << self.bits

    @property
    def window(self) -> int:
        return 1 << self.window_bits

    @property
    def bad_width(self) -> int:
        return self.base - 2

    @property
    def phases(self) -> int:
        return 3 * self.targets + 1

    @property
    def periods(self) -> tuple[int, ...]:
        return (self.base, self.base, self.window) * self.targets


def forbidden_masks(g: Geometry, coordinate: int, step: int | None = None) -> tuple[int, ...]:
    """Enumerate every value of one coordinate and its forbidden menu phases."""
    window = coordinate % 3 == 2
    period = g.periods[coordinate]
    stride = (g.bad_width if window else 1) if step is None else step
    first_bad = period - (g.bad_width if window else 1)
    return tuple(
        sum(1 << k for k in range(g.phases) if (value + k * stride) % period >= first_bad)
        for value in range(period)
    )


def phase_histogram(g: Geometry) -> tuple[int, ...]:
    """Exact product enumeration, compressed by equal forbidden-phase masks."""
    size = 1 << g.phases
    counts = [0] * size
    counts[0] = 1
    for coordinate in range(3 * g.targets):
        masks = forbidden_masks(g, coordinate)
        need(all(mask & (mask - 1) == 0 for mask in masks), "one coordinate forbids two phases")
        frequencies = Counter(masks)
        following = [0] * size
        for mask, count in enumerate(counts):
            for other, multiplicity in frequencies.items():
                following[mask | other] += count * multiplicity
        counts = following
    histogram = [0] * (g.phases + 1)
    for mask, count in enumerate(counts):
        histogram[g.phases - mask.bit_count()] += count
    need(histogram[0] == 0, "uncovered guard tuple")
    volume = (g.base * g.base * g.window) ** g.targets
    need(sum(histogram) == volume, "lost guard tuples")
    return tuple(histogram)


def direct_histogram(g: Geometry) -> tuple[int, ...]:
    need(g.targets == 1, "direct-product fixture capacity")
    masks = tuple(forbidden_masks(g, j) for j in range(3))
    histogram = [0] * (g.phases + 1)
    for u, t, window in product(range(g.base), range(g.base), range(g.window)):
        blocked = masks[0][u] | masks[1][t] | masks[2][window]
        histogram[g.phases - blocked.bit_count()] += 1
    return tuple(histogram)


def bad(value: int, coordinate: int, g: Geometry) -> bool:
    period = g.periods[coordinate]
    return value >= period - (g.bad_width if coordinate % 3 == 2 else 1)


def adversary(menu: tuple[tuple[int, ...], ...], g: Geometry) -> tuple[int, ...]:
    """Kill menu row j using coordinate j, for any at most 3r translations."""
    need(1 <= len(menu) <= 3 * g.targets, "lower-bound menu size")
    state = [0] * (3 * g.targets)
    for j, shift in enumerate(menu):
        need(len(shift) == len(state), "translation dimension")
        state[j] = (g.periods[j] - 1 - shift[j]) % g.periods[j]
    for shift in menu:
        need(any(bad((x + delta) % period, j, g)
                 for j, (x, delta, period) in enumerate(zip(state, shift, g.periods))),
             "adversary missed a menu row")
    return tuple(state)


def lower_controls(g: Geometry) -> int:
    count = 0
    for length in range(1, 3 * g.targets + 1):
        for trial in range(32):
            menu = sample_values(g.periods, length, 173 + 32 * length + trial)
            adversary(menu, g)
            count += 1
    return count


def sample_values(periods: tuple[int, ...], count: int, seed: int) -> tuple[tuple[int, ...], ...]:
    """Bounded deterministic fixture generation, with no rejection-sampling loop."""
    need(1 <= count <= 256 and 1 <= len(periods) <= 12, "sample capacity")
    state = seed
    rows = []
    for _ in range(count):
        row = []
        for period in periods:
            need(1 <= period <= 1 << 37, "sample period capacity")
            state = (6364136223846793005 * state + 1442695040888963407) & ((1 << 64) - 1)
            row.append((state >> 17) % period)
        rows.append(tuple(row))
    return tuple(rows)


def translate_control(value: int, phase: int, g: Geometry) -> int:
    out = value
    for i in range(g.targets):
        offset = i * g.bits
        digit = (value >> offset) & (g.base - 1)
        out += (((digit + phase) % g.base) - digit) << offset
    return out


def translate_data(value: int, phase: int, g: Geometry) -> int:
    out = value
    for i in range(g.targets):
        offset = i * (g.window_bits + 1) + 1
        window = (value >> offset) & (g.window - 1)
        out += (((window + phase * g.bad_width) % g.window) - window) << offset
    return out


def translated(state: tuple[int, int, int], phase: int, g: Geometry) -> tuple[int, int, int]:
    u, t, y = state
    return (translate_control(u, phase, g), translate_control(t, phase, g),
            translate_data(y, phase, g))


def guard_tuple(state: tuple[int, int, int], g: Geometry) -> tuple[int, ...]:
    u, t, y = state
    out = []
    for i in range(g.targets):
        out.extend(((u >> (i * g.bits)) & (g.base - 1),
                    (t >> (i * g.bits)) & (g.base - 1),
                    (y >> (i * (g.window_bits + 1) + 1)) & (g.window - 1)))
    return tuple(out)


def select_phase(state: tuple[int, int, int], g: Geometry) -> int:
    coordinates = guard_tuple(state, g)
    blocked = 0
    for j, value in enumerate(coordinates):
        period = g.periods[j]
        stride = g.bad_width if j % 3 == 2 else 1
        for k in range(g.phases):
            if bad((value + k * stride) % period, j, g):
                blocked |= 1 << k
    available = ((1 << g.phases) - 1) ^ blocked
    need(available != 0, "selector found no good translation")
    return (available & -available).bit_length() - 1


def source_values(y: int, kind: int, g: Geometry) -> tuple[int, ...]:
    windows = tuple((y >> (i * (g.window_bits + 1) + 1)) & (g.window - 1)
                    for i in range(g.targets))
    spectator = (y >> (g.targets * (g.window_bits + 1))) & 1
    if kind in (0, 1):
        return (kind,) * g.targets
    if kind == 2:
        return tuple((windows[i] ^ (windows[(i + 1) % g.targets] >> 1) ^ spectator) & 1
                     for i in range(g.targets))
    need(kind == 3, "source family")
    return tuple(int(windows[i] < g.window // 2) ^ spectator
                 for i in range(g.targets))


def one_f(state: tuple[int, int, int], g: Geometry) -> tuple[int, int, int]:
    """Literal simultaneous live-digit shears on a bounded dirty rectangle."""
    u, t, y = state
    positions = tuple(i * (g.window_bits + 1) for i in range(g.targets))
    parity = tuple((u >> (i * g.bits)) & 1 for i in range(g.targets))
    digits = tuple((t >> (i * g.bits)) & (g.base - 1) for i in range(g.targets))
    umod = 1 << (g.targets * g.bits + 1)
    ymod = 1 << (g.targets * (g.window_bits + 1) + 1)
    y = (y + sum((2 * z * digit) << pos
                 for z, digit, pos in zip(parity, digits, positions))) % ymod
    t = (t + sum(((y >> pos) & 1) << (i * g.bits)
                 for i, pos in enumerate(positions))) % umod
    live = tuple((t >> (i * g.bits)) & (g.base - 1) for i in range(g.targets))
    y = (y + sum((z * (1 - 2 * digit)) << pos
                 for z, digit, pos in zip(parity, live, positions))) % ymod
    t = (t - sum((((y >> pos) & 1) ^ parity[i]) << (i * g.bits)
                 for i, pos in enumerate(positions))) % umod
    return u, t, y


def macro(state: tuple[int, int, int], phase: int, kind: int, g: Geometry,
          transport_source: bool = True) -> tuple[int, int, int]:
    u, t, y = one_f(state, g)
    source_y = translate_data(y, -phase, g) if transport_source else y
    values = source_values(source_y, kind, g)
    umod = 1 << (g.targets * g.bits + 1)
    u = (u + sum(bit << (i * g.bits) for i, bit in enumerate(values))) % umod
    u, t, y = one_f((u, t, y), g)
    source_y = translate_data(y, -phase, g) if transport_source else y
    values = source_values(source_y, kind, g)
    u = (u - sum(bit << (i * g.bits) for i, bit in enumerate(values))) % umod
    return u, t, y


def ideal(state: tuple[int, int, int], kind: int, g: Geometry) -> tuple[int, int, int]:
    u, t, y = state
    for i, bit in enumerate(source_values(y, kind, g)):
        y ^= bit << (i * (g.window_bits + 1))
    return u, t, y


def composed(state: tuple[int, int, int], kind: int, g: Geometry,
             transport_source: bool = True) -> tuple[int, int, int]:
    phase = select_phase(state, g)
    image = translated(state, phase, g)
    need(not any(bad(value, j, g) for j, value in enumerate(guard_tuple(image, g))),
         "chosen image violates a guard")
    end = translated(macro(image, phase, kind, g, transport_source), -phase, g)
    return end


def check_endpoint(state: tuple[int, int, int], kind: int, g: Geometry) -> None:
    end = composed(state, kind, g)
    need(end == ideal(state, kind, g), "conjugated endpoint")
    need(select_phase(end, g) == select_phase(state, g), "selector cannot be erased")
    for k in range(g.phases):
        need(translated(translated(state, k, g), -k, g) == state, "translation inverse")


def endpoint_checks(g: Geometry, exhaustive: bool) -> int:
    ulimit = 1 << (g.targets * g.bits + 1)
    ylimit = 1 << (g.targets * (g.window_bits + 1) + 1)
    if exhaustive:
        need(g == Geometry(1, 2, 3), "exhaustive rectangle capacity")
        states = product(range(ulimit), range(ulimit), range(ylimit))
        count = ulimit * ulimit * ylimit
    else:
        states = sample_values((ulimit, ulimit, ylimit), 256, 4198)
        count = len(states)
    for state in states:
        for kind in range(4):
            check_endpoint(state, kind, g)
    return 4 * count


def rejection_controls() -> dict:
    g = Geometry(1, 2, 3)
    weakened = tuple(forbidden_masks(g, j, 1) for j in range(3))
    full = (1 << g.phases) - 1
    uncovered = sum(weakened[0][u] | weakened[1][t] | weakened[2][w] == full
                    for u, t, w in product(range(g.base), range(g.base), range(g.window)))
    need(uncovered > 0, "unit window stride mutant unexpectedly covers")
    source_witness = None
    for state in product(range(8), range(8), range(32)):
        if composed(state, 2, g, False) != ideal(state, 2, g):
            source_witness = state
            break
    need(source_witness is not None, "untransported source mutant survived")
    for args in ((2, 2, 4), (1, 2, 2), (1, 1, 3), (5, 4, 8)):
        try:
            Geometry(*args)
        except ValueError:
            continue
        raise ValueError("invalid geometry accepted")
    shorter = tuple(tuple(k * (g.bad_width if j % 3 == 2 else 1)
                          for j in range(3)) for k in range(3))
    witness = adversary(shorter, g)
    need(all(any(bad((x + delta) % period, j, g)
                 for j, (x, delta, period) in enumerate(zip(witness, shift, g.periods)))
             for shift in shorter), "three-phase deletion mutant survived")
    return {"unit_window_stride_uncovered_tuples": uncovered,
            "untransported_source_witness": source_witness,
            "invalid_geometries": ((2, 2, 4), (1, 2, 2), (1, 1, 3), (5, 4, 8)),
            "three_phase_failure_witness": witness}


def receipt() -> dict:
    geometries = (Geometry(1, 2, 3), Geometry(1, 3, 5), Geometry(2, 3, 6),
                  Geometry(3, 4, 8), Geometry(4, 4, 8))
    rows = []
    for g in geometries:
        histogram = phase_histogram(g)
        if g.targets == 1:
            need(histogram == direct_histogram(g), "compressed/direct enumeration disagreement")
        rows.append({"r": g.targets, "B": g.base, "N": g.window,
                     "menu_size": g.phases, "safe_phase_histogram": histogram,
                     "adversarial_menus": lower_controls(g),
                     "endpoint_cases": endpoint_checks(g, g == geometries[0])})
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    return {"claim_type": "scoped proof with finite corroboration", "fixtures": rows,
            "rejection_controls": rejection_controls(),
            "artifact_sha256": {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
                                for name in names}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="explicit authoring output")
    args = parser.parse_args()
    result = receipt()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_result is not None:
        args.write_result.write_text(encoded, encoding="utf-8")
    else:
        need(json.loads((PACKAGE / "RESULT.json").read_text()) == json.loads(encoded),
             "receipt or artifact hashes differ")
    print("PASS_TRANSLATED_SHARP_GUARD_COVER " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
