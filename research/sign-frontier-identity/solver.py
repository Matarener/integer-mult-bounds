"""Exact complete-endpoint tests for bounded live signs.

Produced by Nick Petalas. Apache-2.0.
"""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Gate:
    kind: str
    dst: int
    src: int | None = None
    coefficient: Fraction = Fraction(1)
    sign: int | None = None


def validate(roles, word, frontier_limit):
    """Check the executable capacity contract before allocating state tables."""
    if type(roles) is not int or not 1 <= roles <= 5:
        raise ValueError("roles must be an integer in 1..5")
    if type(frontier_limit) is not int or not 0 <= frontier_limit <= 8:
        raise ValueError("frontier limit must be an integer in 0..8")
    if not isinstance(word, tuple) or len(word) > 4096:
        raise ValueError("word must be a tuple of at most 4096 gates")
    for gate in word:
        if not isinstance(gate, Gate) or gate.kind not in ("ADD", "QUERY", "APPLY", "SWAP"):
            raise ValueError("invalid gate kind")
        if type(gate.dst) is not int or not 0 <= gate.dst < roles:
            raise ValueError("invalid destination")
        if type(gate.coefficient) is not Fraction:
            raise ValueError("coefficient must be an exact Fraction")
        if max(abs(gate.coefficient.numerator).bit_length(), gate.coefficient.denominator.bit_length()) > 64:
            raise ValueError("coefficient exceeds 64 bits")
        if gate.kind != "APPLY":
            if type(gate.src) is not int or not 0 <= gate.src < roles or gate.src == gate.dst:
                raise ValueError("distinct source and destination required")
        elif gate.src is not None:
            raise ValueError("APPLY has no source")
        if gate.kind in ("QUERY", "APPLY"):
            if type(gate.sign) is not int or not 0 <= gate.sign < 4096:
                raise ValueError("sign label must be an integer in 0..4095")
        elif gate.sign is not None:
            raise ValueError("unsigned gate carries a sign")
        if gate.kind in ("SWAP", "APPLY") and gate.coefficient != 1:
            raise ValueError("SWAP and APPLY have unit coefficient")


def identity(roles):
    return tuple(Fraction(i == j) for i in range(roles) for j in range(roles))


def advance(matrix, gate, roles, sign):
    """Apply a literal elementary row operation to the complete prefix map."""
    result = list(matrix)
    for column in range(roles):
        dst = gate.dst * roles + column
        if gate.kind == "APPLY":
            result[dst] = sign * matrix[dst]
        elif gate.kind == "SWAP":
            src = gate.src * roles + column
            result[dst], result[src] = matrix[src], matrix[dst]
        else:
            scale = gate.coefficient * (sign if gate.kind == "QUERY" else 1)
            result[dst] += scale * matrix[gate.src * roles + column]
    return tuple(result)


def retain(echelon, representatives, matrix, witness):
    """Keep an actual prefix when its homogenization increases the span."""
    row = list(matrix) + [Fraction(1)]
    for pivot, basis in echelon:
        coefficient = row[pivot]
        if coefficient:
            row = [value - coefficient * entry for value, entry in zip(row, basis)]
    pivot = next((i for i, value in enumerate(row) if value), None)
    if pivot is not None:
        scale = row[pivot]
        echelon.append((pivot, tuple(value / scale for value in row)))
        representatives.append((matrix, witness))
        assert len(representatives) <= len(matrix) + 1


def schedule(word):
    first, last = {}, {}
    for index, gate in enumerate(word):
        if gate.sign is not None:
            first.setdefault(gate.sign, index)
            last[gate.sign] = index
    active, width, masks = 0, 0, []
    for index, gate in enumerate(word):
        if gate.sign is not None:
            bit = 1 << gate.sign
            if first[gate.sign] == index:
                active |= bit
            if last[gate.sign] == index:
                active &= ~bit
        masks.append(active)
        width = max(width, active.bit_count())
    assert active == 0
    return first, masks, width


def step(states, gate, roles, introduce, mask):
    buffers = {}
    candidates = 0
    for representatives in states.values():
        for matrix, witness in representatives:
            for negative in ((False, True) if introduce else (False,)):
                changed = witness | (1 << gate.sign) if negative else witness
                sign = -1 if gate.sign is not None and (changed >> gate.sign) & 1 else 1
                updated = advance(matrix, gate, roles, sign)
                echelon, kept = buffers.setdefault(changed & mask, ([], []))
                retain(echelon, kept, updated, changed)
                candidates += 1
    return {key: kept for key, (_, kept) in buffers.items()}, candidates


def decide(roles, word, frontier_limit=8):
    """Return identity status, an actual negative-sign mask if false, and counts."""
    validate(roles, word, frontier_limit)
    first, masks, width = schedule(word)
    if width > frontier_limit:
        raise ValueError("live-sign frontier exceeds the declared limit")
    states = {0: [(identity(roles), 0)]}
    candidates, max_states, max_basis = 0, 1, 1
    for index, gate in enumerate(word):
        introduce = gate.sign is not None and first[gate.sign] == index
        states, count = step(states, gate, roles, introduce, masks[index])
        candidates += count
        max_states = max(max_states, len(states))
        max_basis = max(max_basis, max(map(len, states.values())))
        assert len(states) <= 2 ** width
    expected = identity(roles)
    witness = next((bits for matrix, bits in states[0] if matrix != expected), None)
    return {"identity": witness is None, "witness": witness, "frontier": width,
            "max_states": max_states, "max_basis": max_basis, "candidates": candidates}


def inverse(word):
    return tuple(Gate(g.kind, g.dst, g.src,
                      -g.coefficient if g.kind in ("ADD", "QUERY") else g.coefficient,
                      g.sign) for g in reversed(word))
