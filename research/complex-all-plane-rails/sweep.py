"""Enumerate all admissible two-plane injections without scanning rejected pairs."""
from __future__ import annotations

import heapq
from collections import Counter

from model import Event, backward_caps, join_dim, planes_in, seeds_for


def next_events(events: list[Event], registers: int) -> list[tuple[int, ...]]:
    last = [-1] * registers
    following = [() for _ in events]
    for index in range(len(events) - 1, -1, -1):
        following[index] = tuple(last[reg] for reg in events[index].regs)
        for reg in events[index].regs:
            last[reg] = index
    return following


def closure(events, following, baseline, seed, plane) -> tuple[int, ...]:
    counts = list(baseline)
    active: set[int] = set()
    pending = [seed]
    for _ in range(len(events) + 1):
        if not pending:
            break
        index = heapq.heappop(pending)
        for _duplicate in range(2):
            if pending and pending[0] == index:
                heapq.heappop(pending)
        event = events[index]
        touched = active.intersection(event.regs)
        if index != seed and not touched:
            continue
        dim = join_dim(event.frame, plane)
        if event.fixed and dim != event.frame.dim:
            raise ValueError("plane crosses a fixed interface")
        for reg, before in zip(event.regs, event.before, strict=True):
            old = event.frame.dim - before.dim
            prior = join_dim(before, plane) if reg in touched else before.dim
            new = dim - prior
            if new < 0:
                raise ValueError("negative induced rank")
            if old:
                counts[old] -= 1
            if new:
                counts[new] += 1
        if dim == event.frame.dim:
            active.difference_update(event.regs)
        else:
            active.update(event.regs)
        for reg, successor in zip(event.regs, following[index], strict=True):
            if reg in active and successor >= 0:
                heapq.heappush(pending, successor)
    if active or pending:
        raise ValueError("closure did not finish within its finite event bound")
    if min(counts) < 0:
        raise ValueError("negative paid count")
    if sum(rank * count for rank, count in enumerate(counts)) != sum(
            rank * count for rank, count in enumerate(baseline)):
        raise ValueError("rank mass changed with fixed endpoints")
    return tuple(counts)


def census(events, baseline, registers, helper_start) -> dict:
    caps = backward_caps(events, registers)
    seeds = seeds_for(events, helper_start)
    following = next_events(events, registers)
    profiles: Counter = Counter()
    witnesses = {}
    valid = noop = 0
    cap_dimensions: Counter = Counter()
    for seed in seeds:
        cap = caps[seed]
        cardinality = cap.bit_count()
        if cardinality & (cardinality - 1):
            raise ValueError("cap cardinality is not a power of two")
        cap_dimensions[cardinality.bit_length() - 1] += 1
        enumerated = 0
        for plane in planes_in(cap):
            enumerated += 1
            valid += 1
            if plane & events[seed].frame.mask == plane:
                noop += 1
                continue
            profile = closure(events, following, baseline, seed, plane)
            profiles[profile] += 1
            witnesses.setdefault(profile, (seed, plane))
        if enumerated != (cardinality - 1) * (cardinality - 2) // 6:
            raise ValueError("two-plane enumeration is incomplete")
    return {
        "seeds": len(seeds), "planes": 43435, "domain_pairs": 43435 * len(seeds),
        "legal_pairs": valid, "noop_pairs": noop,
        "changed_legal_pairs": valid - noop,
        "illegal_pairs": 43435 * len(seeds) - valid,
        "cap_dimensions": {str(dim): count for dim, count in sorted(cap_dimensions.items())},
        "profiles": [{"profile": list(profile), "count": count,
                      "witness": list(witnesses[profile])}
                     for profile, count in sorted(profiles.items())],
    }
