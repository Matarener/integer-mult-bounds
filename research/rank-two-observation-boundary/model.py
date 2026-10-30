"""Exact coefficient semantics. @CubeJerry with OpenAI Codex. Apache-2.0.

Model: commdata2338 PR2020; open question: Nick Petalas PR5968.
"""
from itertools import combinations_with_replacement, product

ADAPTERS = ((2, 3), (3, 2), (0, 2), (0, 3), (1, 2), (1, 3))
CHILDREN = ((0, 1, 0), (0, 0, 0), (0, 0, 0), (1, 0, 1))
PARTIAL_MASKS = (3, 2, 3, 3)
FULL_MASKS = (3, 3, 3, 3)
PARTIAL_WORD = ((), (), ((2, 3),), ((3, 2),), ())
FULL_WORD = (((2, 3),), ((3, 2),), (), ((0, 3),), ())
EAGER_WORD = ((), ((2, 3),), ((2, 3),), ((2, 3),), ((3, 2),))
IDENTITY = (1, 2, 4, 8)
FINAL = (9, 6, 4, 8)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(children, schedule):
    require(len(children) == 4, "four compulsory children")
    require(all(len(c) == 3 and all(type(v) is int and v in (0, 1)
                for v in c) for c in children), "child alphabet")
    require(len(schedule) == 5, "five adapter gaps")
    require(sum(map(len, schedule)) <= 4, "bounded certificate word")
    require(all(g in ADAPTERS for gap in schedule for g in gap),
            "six-adapter alphabet; no output feedback")


def reference(children=CHILDREN):
    state = list(IDENTITY)
    rows = []
    for output, source, _target in children:
        state[output] ^= 1 << (2 + source)
        rows.append(tuple(state))
    return tuple(rows)


def coefficient_trace(schedule, children=CHILDREN):
    validate(children, schedule)
    state = list(IDENTITY)
    for destination, source in schedule[0]:
        state[destination] ^= state[source]
    trace = []
    for i, (output, source, target) in enumerate(children):
        state[output] ^= state[2 + source]
        state[2 + target] ^= state[3 - target]
        for destination, source in schedule[i + 1]:
            state[destination] ^= state[source]
        trace.append(tuple(state))
    return tuple(trace)


def accepts(trace, masks, children=CHILDREN):
    require(len(trace) == len(masks) == 4 and masks[-1] == 3,
            "four observations with both final outputs")
    require(all(type(m) is int and m in (1, 2, 3) for m in masks),
            "nonempty observation masks")
    wanted = reference(children)
    return trace[-1] == wanted[-1] and all(
        not (mask & (1 << out)) or row[out] == goal[out]
        for row, goal, mask in zip(trace, wanted, masks, strict=True)
        for out in (0, 1))


def schedules(count):
    require(type(count) is int and 0 <= count <= 3, "enumeration count 0..3")
    for gaps in combinations_with_replacement(range(5), count):
        for gates in product(ADAPTERS, repeat=count):
            word = [[] for _ in range(5)]
            for gap, gate in zip(gaps, gates, strict=True):
                word[gap].append(gate)
            yield tuple(tuple(gap) for gap in word)


def update_rank(children=CHILDREN):
    rows = reference(children)[-1]
    a, b = (rows[0] ^ 1) >> 2, (rows[1] ^ 2) >> 2
    return 0 if not (a or b) else 1 + int(bool(a and b and a != b))
