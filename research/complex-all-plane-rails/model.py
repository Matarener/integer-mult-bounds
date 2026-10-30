"""Exact binary frame model for the fixed PR1094 temporal-rail contract.

The event order and barriers follow Cinna Davis's PR1996 search.py.
This module implements the extension independently. Apache-2.0.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import cache


@dataclass(frozen=True)
class Space:
    basis: tuple[int, ...]
    mask: int

    @property
    def dim(self) -> int:
        return len(self.basis)


@cache
def space(vectors: tuple[int, ...]) -> Space:
    pivots: dict[int, int] = {}
    for value in vectors:
        if not 0 <= value < 512:
            raise ValueError("frame vector outside F2^9")
        for bit in sorted(pivots, reverse=True):
            if value >> bit & 1:
                value ^= pivots[bit]
        if value:
            bit = value.bit_length() - 1
            for other in pivots:
                if pivots[other] >> bit & 1:
                    pivots[other] ^= value
            pivots[bit] = value
    basis = tuple(pivots[bit] for bit in sorted(pivots, reverse=True))
    points = [0]
    for value in basis:
        points += [point ^ value for point in points]
    return Space(basis, sum(1 << point for point in points))


@dataclass(frozen=True)
class Event:
    location: tuple[str, int]
    regs: tuple[int, ...]
    frame: Space
    before: tuple[Space, ...]
    fixed: bool


def participants(operation: list) -> tuple[int, ...]:
    return (operation[1], operation[2]) if operation[0] == "add" else (operation[1],)


def event_model(word: dict) -> tuple[list[Event], tuple[int, ...], int]:
    width, helpers = word["report"]["v"], word["report"]["R"]
    count = 2 * width + helpers
    current = [space(()) for _ in range(count)]
    for reg, port in enumerate(word["ports"]):
        current[reg] = space((port,))
    for reg, frame in word.get("start_extra", {}).items():
        current[int(reg)] = space(tuple(frame))
    events: list[Event] = []
    for section in ("A", "B"):
        for index, operation in enumerate(word[section]):
            append_event(events, current, (section, index), participants(operation), operation[-1])
        if section == "A":
            levels = word.get("target_levels", {})
            for reg in range(width):
                append_event(events, current, ("target_level", reg), (width + reg,),
                             levels.get(str(reg), []), True)
            for index, (reg, frame) in enumerate(zip(word["centers"], word["center_frames"], strict=True)):
                append_event(events, current, ("center_frame", index), (reg,), frame, True)
    for index, (operation, frame) in enumerate(word.get("early_cleanup", [])):
        append_event(events, current, ("early_cleanup", index), participants(word["cleanup"][operation]), frame)
    full = tuple(1 << bit for bit in range(9))
    for reg in range(count):
        frame = word.get("helper_final", {}).get(str(reg), full)
        if width <= reg < 2 * width:
            port = word["ports"][reg - width]
            frame = tuple(value for value in range(1, 512) if (value & port).bit_count() % 2 == 0)
        append_event(events, current, ("final", reg), (reg,), frame, True)
    baseline = tuple(int(word["report"]["local_profile"].get(str(rank), 0)) for rank in range(10))
    return events, baseline, count


def append_event(events, current, location, regs, vectors, fixed=False) -> None:
    frame = space(tuple(vectors))
    if len(set(regs)) != len(regs):
        raise ValueError("self-add is outside the rail contract")
    before = tuple(current[reg] for reg in regs)
    if any(old.mask & frame.mask != old.mask for old in before):
        raise ValueError("original frame chain is not monotone")
    events.append(Event(location, regs, frame, before, fixed))
    for reg in regs:
        current[reg] = frame


def seeds_for(events: list[Event], helper_start: int) -> list[int]:
    return [index for index, event in enumerate(events)
            if event.location[0] in ("A", "B") and len(event.regs) == 2
            and all(reg >= helper_start for reg in event.regs)]


def backward_caps(events: list[Event], registers: int) -> list[int]:
    full = (1 << 512) - 1
    safe = [full] * registers
    caps = [0] * len(events)
    for index in range(len(events) - 1, -1, -1):
        event = events[index]
        cap = full
        for reg in event.regs:
            cap &= safe[reg]
        if event.fixed:
            cap &= event.frame.mask
        if cap & event.frame.mask != event.frame.mask:
            raise ValueError("unmodified frame violates backward cap")
        caps[index] = cap
        for reg in event.regs:
            safe[reg] = cap
    return caps


def planes_in(mask: int):
    points = [value for value in range(1, 512) if mask >> value & 1]
    for pos, first in enumerate(points):
        for second in points[pos + 1:]:
            third = first ^ second
            if third > second:
                if not mask >> third & 1:
                    raise ValueError("cap is not a subspace")
                yield (1 << first) | (1 << second) | (1 << third)


def join_dim(frame: Space, plane: int) -> int:
    return frame.dim + 2 - (frame.mask & plane).bit_count().bit_length()


def chain_profile(events: list[Event]) -> Counter:
    return Counter(event.frame.dim - old.dim for event in events for old in event.before
                   if event.frame.dim != old.dim)
