#!/usr/bin/env python3
"""Exact Z/4 dirty-fanout endpoint and complete short-word exclusion."""
import hashlib
import itertools
import json
from pathlib import Path

IDENTITY = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0)
TARGET = (1, 0, 0, 2, 0, 1, 0, 1, 0, 0, 1, 1)
PAIRS = ((1, 0), (2, 1), (0, 2), (0, 3))
GENERATORS = tuple((i, j, c) for i, j in PAIRS for c in (1, 2, 3))
WORD = ((2, 1, 3), (1, 0, 3), (0, 3, 1),
        (1, 0, 1), (0, 3, 1), (2, 1, 1))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def valid_gate(gate):
    require(isinstance(gate, tuple) and len(gate) == 3, 'gate shape')
    require(all(type(x) is int for x in gate), 'integer gate entries')
    i, j, c = gate
    require(0 <= i < 3 and 0 <= j <= 3 and i != j, 'gate roles')
    require(1 <= c <= 3, 'nonzero canonical coefficient')


def gate_price(gate):
    valid_gate(gate)
    return 1 if gate[:2] in PAIRS else 100


def apply_gate(state, gate):
    """Literal three-by-four coefficient matrix, without packed arithmetic."""
    valid_gate(gate)
    require(len(state) == 12 and all(type(x) is int and 0 <= x < 4
                                   for x in state), 'matrix residues')
    i, j, c = gate
    source = state[4*j:4*j+4] if j < 3 else (0, 0, 0, 1)
    row = tuple((state[4*i+k] + c*source[k]) % 4 for k in range(4))
    return state[:4*i] + row + state[4*i+4:]


def execute(word, state=IDENTITY):
    require(isinstance(word, tuple) and len(word) <= 64, 'word capacity')
    for gate in word:
        state = apply_gate(state, gate)
    return state


def ball(start, radius):
    require(type(radius) is int and 0 <= radius <= 3, 'radius capacity')
    seen, frontier = {start}, {start}
    for _ in range(radius):
        next_frontier = {apply_gate(s, g) for s in frontier for g in GENERATORS}
        next_frontier.difference_update(seen)
        seen.update(next_frontier)
        require(len(seen) <= 1000, 'state capacity')
        frontier = next_frontier
    return seen


def digest(states):
    return hashlib.sha256(b''.join(bytes(s) for s in sorted(states))).hexdigest()


def scalar_execution(values, word):
    """Independent evaluation on four actual scalars, including the source."""
    require(len(values) == 4, 'scalar shape')
    out = list(values)
    for i, j, c in word:
        out[i] = (out[i] + c*out[j]) % 4
    return tuple(out)


def expect_rejection(function, argument):
    try:
        function(argument)
    except ValueError:
        return 1
    raise ValueError('invalid input accepted')


def main():
    require(execute(WORD) == TARGET, 'complete endpoint')
    require(sum(map(gate_price, WORD)) == 6, 'complete price')
    require(len(GENERATORS) == 12 and len(set(GENERATORS)) == 12, 'alphabet')
    inverse = tuple((i, j, 4-c) for i, j, c in reversed(WORD))
    require(execute(inverse, TARGET) == IDENTITY, 'inverse endpoint')
    forward, backward = ball(IDENTITY, 2), ball(TARGET, 3)
    require(not forward.intersection(backward), 'word of cost at most five')
    literal_cases = 0
    for inputs in itertools.product(range(4), repeat=4):
        a, b, c, p = inputs
        expected = ((a+2*p) % 4, (b+p) % 4, (c+p) % 4, p)
        output = scalar_execution(inputs, WORD)
        require(output == expected, 'literal dirty endpoint')
        require(scalar_execution(output, inverse) == inputs, 'literal inverse')
        literal_cases += 1
    controls = 0
    for k in range(len(WORD)):
        require(execute(WORD[:k]+WORD[k+1:]) != TARGET, 'deletion survived')
        i, j, c = WORD[k]
        changed = WORD[:k] + ((i, j, 4-c),) + WORD[k+1:]
        require(execute(changed) != TARGET, 'wrong sign survived')
        controls += 2
    for gate in ((0, 0, 1), (0, 3, 0), (0, 3, 4), (False, 3, 1), (3, 0, 1)):
        controls += expect_rejection(gate_price, gate)
    controls += expect_rejection(ball_radius_control, 4)
    controls += expect_rejection(execute, WORD*11)
    for i, j in itertools.permutations(range(3), 2):
        require(gate_price((i, j, 1)) == (1 if (i, j) in PAIRS else 100),
                'directed price')
    for i in range(3):
        require(gate_price((i, 3, 1)) == (1 if i == 0 else 100), 'source price')
    package = Path(__file__).resolve().parent
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(package.iterdir()) if p.is_file()}
    receipt = {'status': 'PASS_Z4_DIRECTED_CYCLE_FANOUT', 'minimum_price': 6,
               'word': WORD, 'ball_sizes': [len(forward), len(backward)],
               'ball_hashes': [digest(forward), digest(backward)],
               'literal_inputs': literal_cases, 'controls': controls,
               'package_sha256': hashes}
    print(json.dumps(receipt, sort_keys=True))


def ball_radius_control(radius):
    return ball(IDENTITY, radius)


if __name__ == '__main__':
    main()
