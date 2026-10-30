"""Exact snapshot guard for XOR sweeps with distinct destinations.

An event is (destination, source). Payload entries are arbitrary bit strings.
Copyright 2026 Nick Petalas. Apache-2.0.
"""

from dataclasses import dataclass
from heapq import heappop, heappush

MAX_CELLS = 4096
MAX_PAYLOAD_BITS = 256
Event = tuple[int, int]
Word = tuple[Event, ...]


@dataclass(frozen=True)
class Conflict:
    first: int
    second: int
    basis: int
    output: int


def checked_word(cells: int, events: object) -> Word:
    """Validate the unique-write contract before applying the theorem."""
    if type(cells) is not int or not 1 <= cells <= MAX_CELLS:
        raise ValueError("cell count must be an integer in 1..4096")
    if not isinstance(events, (tuple, list)) or len(events) > cells:
        raise ValueError("events must be a sequence with at most cells entries")
    result = []
    destinations = set()
    for event in events:
        if not isinstance(event, (tuple, list)) or len(event) != 2:
            raise ValueError("an event must contain destination and source")
        target, source = event
        if any(type(x) is not int or not 0 <= x < cells for x in event):
            raise ValueError("event endpoints must be integer cell indices")
        if target == source or target in destinations:
            raise ValueError("self-updates and repeated destinations are excluded")
        destinations.add(target)
        result.append((target, source))
    return tuple(result)


def first_conflict(cells: int, events: object) -> Conflict | None:
    """Return a basis-input discrepancy, or certify snapshot equality."""
    word = checked_word(cells, events)
    written: dict[int, int] = {}
    for second, (target, source) in enumerate(word):
        if source in written:
            first = written[source]
            return Conflict(first, second, word[first][1], target)
        written[target] = second
    return None


def safe_order(cells: int, events: object) -> tuple[int, ...] | None:
    """Return safe event indices, or None exactly for a directed cycle."""
    word = checked_word(cells, events)
    incoming = {target: i for i, (target, _) in enumerate(word)}
    outgoing = [0] * cells
    for _, source in word:
        outgoing[source] += 1
    ready = []
    for target in incoming:
        if outgoing[target] == 0:
            heappush(ready, target)
    order = []
    for _ in range(len(word)):
        if not ready:
            return None
        target = heappop(ready)
        index = incoming[target]
        order.append(index)
        source = word[index][1]
        outgoing[source] -= 1
        if outgoing[source] == 0 and source in incoming:
            heappush(ready, source)
    return tuple(order)


def checked_payload(cells: int, values: object) -> tuple[int, ...]:
    if not isinstance(values, (tuple, list)) or len(values) != cells:
        raise ValueError("payload must have one entry per cell")
    if any(type(x) is not int or not 0 <= x < 1 << MAX_PAYLOAD_BITS for x in values):
        raise ValueError("payload entries must be unsigned bit strings of at most 256 bits")
    return tuple(values)


def execute(cells: int, events: object, values: object, *, snapshot: bool) -> tuple[int, ...]:
    word = checked_word(cells, events)
    entry = checked_payload(cells, values)
    if type(snapshot) is not bool:
        raise ValueError("snapshot must be a Boolean")
    current = list(entry)
    for target, source in word:
        current[target] ^= entry[source] if snapshot else current[source]
    return tuple(current)
