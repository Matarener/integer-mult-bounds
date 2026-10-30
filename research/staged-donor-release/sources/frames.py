# SPDX-License-Identifier: Apache-2.0
"""Necessary monotone scalar-frame constraints, with optional free warp interfaces.

Graph layout follows Nick Petalas's rank7-joint-frame-optimum/graph.py.
This implementation uses canonical binary bases and retains conflict paths.
"""
from functools import lru_cache

FULL = tuple(1 << i for i in reversed(range(9)))
ZERO = ()


def basis(vectors):
    pivots = {}
    for vector in vectors:
        while vector:
            bit = vector.bit_length() - 1
            if bit in pivots:
                vector ^= pivots[bit]
            else:
                pivots[bit] = vector
                break
    for bit in sorted(pivots):
        for higher in pivots:
            if higher > bit and (pivots[higher] >> bit) & 1:
                pivots[higher] ^= pivots[bit]
    return tuple(pivots[k] for k in sorted(pivots, reverse=True))


@lru_cache(maxsize=32768)
def join(left, right):
    return basis(left + right)


@lru_cache(maxsize=32768)
def contains(frame, vector):
    for pivot in frame:
        if vector.bit_length() == pivot.bit_length():
            vector ^= pivot
    return vector == 0


@lru_cache(maxsize=8192)
def points(frame):
    result = [0]
    for v in frame:
        result += [x ^ v for x in result]
    return tuple(result)


@lru_cache(maxsize=32768)
def meet(left, right):
    if len(left) > len(right):
        left, right = right, left
    return basis(v for v in points(left) if contains(right, v))


def inside(left, right):
    return all(contains(right, v) for v in left)


def operands(gate):
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def build(word, free_warps=False):
    start = [(p,) for p in word['ports']] + [ZERO] * 592
    end = [FULL] * 112 + [basis(v for v in range(1, 512)
           if (v & p).bit_count() % 2 == 0) for p in word['ports']] + [FULL] * 480
    for r, frame in word['start_extra'].items():
        start[int(r)] = basis(frame)
    for r, frame in word['helper_final'].items():
        end[int(r)] = basis(frame)
    labels, incoming, outgoing = [], [], []
    current = [(-1, f, ('start', r)) for r, f in enumerate(start)]
    def anchor(r, before, after, label):
        previous, _, _ = current[r]
        if previous >= 0:
            outgoing[previous].append((-1, basis(before), label, r))
        current[r] = (-1, basis(after), label)
    def scalar(section, position, gate):
        index = len(labels)
        labels.append((section, position))
        incoming.append([])
        outgoing.append([])
        for r in operands(gate):
            previous, frame, label = current[r]
            incoming[index].append((previous, frame, label, r))
            if previous >= 0:
                outgoing[previous].append((index, ZERO, None, r))
            current[r] = (index, ZERO, None)
    for i, gate in enumerate(word['A']):
        if gate[0] == 'warp':
            before, after = (FULL, ZERO) if free_warps else (gate[3], gate[4])
            anchor(gate[1], before, after, ('A_warp', i))
        else:
            scalar('A', i, gate)
    for r, frame in zip(word['centers'], word['center_frames']):
        anchor(r, frame, frame, ('centre', r))
    by_position = {}
    for i, record in enumerate(word['warps']):
        by_position.setdefault(record[0], []).append((i, record))
    for i in range(len(word['B']) + 1):
        for j, rec in by_position.get(i, []):
            before, after = (FULL, ZERO) if free_warps else (rec[3], rec[4])
            anchor(rec[1], before, after, ('B_warp', j))
        if i < len(word['B']):
            scalar('B', i, word['B'][i])
    for i, gate in enumerate(word['restore']):
        scalar('restore', i, gate)
    for r in range(704):
        if r not in word['removed']:
            anchor(r, end[r], end[r], ('end', r))
    return dict(labels=labels, incoming=incoming, outgoing=outgoing)


def bounds(graph):
    lower = []
    upper = [FULL] * len(graph['labels'])
    for incoming in graph['incoming']:
        frame = ZERO
        for previous, anchor, _, _ in incoming:
            frame = join(frame, lower[previous] if previous >= 0 else anchor)
        lower.append(frame)
    for i in reversed(range(len(lower))):
        for following, anchor, _, _ in graph['outgoing'][i]:
            upper[i] = meet(upper[i], upper[following] if following >= 0 else anchor)
    bad = [i for i in range(len(lower)) if not inside(lower[i], upper[i])]
    return lower, upper, bad


def witness(graph, lower, upper, bad):
    """One explicit fixed-anchor -> scalar chain -> fixed-anchor contradiction."""
    pivot = bad[-1]
    required = upper[pivot]
    chain = [pivot]
    current = pivot
    while True:
        edge = next(e for e in graph['incoming'][current]
                    if not inside(lower[e[0]] if e[0] >= 0 else e[1], required))
        previous, frame, label, _ = edge
        if previous < 0:
            vector = next(v for v in frame if not contains(required, v))
            origin = dict(label=label, frame=frame)
            break
        chain.append(previous)
        current = previous
    chain.reverse()
    current = pivot
    while True:
        edge = next(e for e in graph['outgoing'][current]
                    if not contains(upper[e[0]] if e[0] >= 0 else e[1], vector))
        following, frame, label, _ = edge
        if following < 0:
            destination = dict(label=label, frame=frame)
            break
        chain.append(following)
        current = following
    result = dict(vector=vector, origin=origin, destination=destination,
                  scalar_path=[graph['labels'][i] for i in chain])
    validate_witness(graph, result)
    return result


def validate_witness(graph, result):
    """Check the certificate from literal edges alone; no lower/upper computation."""
    vector, origin, destination = result['vector'], result['origin'], result['destination']
    lookup = {label: index for index, label in enumerate(graph['labels'])}
    chain = [lookup[tuple(label)] for label in result['scalar_path']]
    if not chain:
        raise ValueError('empty scalar path')
    first_edges = graph['incoming'][chain[0]]
    if not any(e[0] < 0 and e[2] == origin['label'] and contains(e[1], vector)
               for e in first_edges):
        raise ValueError('unbound origin')
    for first, second in zip(chain, chain[1:]):
        if not any(e[0] == second for e in graph['outgoing'][first]):
            raise ValueError('broken scalar frame path')
    if not any(e[0] < 0 and e[2] == destination['label'] and not contains(e[1], vector)
               for e in graph['outgoing'][chain[-1]]):
        raise ValueError('unbound forbidden destination')
    return True
