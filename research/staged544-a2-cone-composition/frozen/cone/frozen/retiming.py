# SPDX-License-Identifier: Apache-2.0
"""Exact, fixed-neighbour single-ADD retiming relaxation.

Chris R / Clear1nsight, with substantial OpenAI assistance. The BORROW-WORD
frame contract and scalar-retiming mechanism are credited in README.md.
This module does not import the retained auditor or a numerical optimiser.
"""
from bisect import bisect_left
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache


def need(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(maxsize=None)
def span(vectors):
    points = {0}
    for v in vectors:
        need(type(v) is int and 0 <= v < 512, 'invalid frame vector')
        points |= {x ^ v for x in tuple(points)}
    return sum(1 << x for x in points)


@lru_cache(maxsize=None)
def basis(mask):
    answer = []
    have = 1
    for v in range(1, 512):
        if (mask >> v) & 1 and not (have >> v) & 1:
            answer.append(v)
            have = span(tuple(answer))
    need(have == mask, 'not a binary subspace')
    return tuple(answer)


@lru_cache(maxsize=None)
def join(a, b):
    return span(basis(a) + basis(b))


@lru_cache(maxsize=None)
def rank(mask):
    n = mask.bit_count()
    need(n > 0 and n & (n - 1) == 0, 'invalid subspace cardinality')
    return n.bit_length() - 1


def contained(a, b):
    return not a & ~b


def touched(gate):
    return gate[1:3] if gate[0] == 'add' else gate[1:2]


def tracing(word):
    """Own chronological trace; centre descent is NOT persistent state.

    A check node is a fixed boundary, not a charged instruction. The census
    relaxes it to a virtual climb. Every legal witness has zero such charge.
    """
    full = (1 << 512) - 1
    live = set(range(704)) - set(word['removed'])
    start, end = {}, {}
    for r in live:
        if r < 112:
            start[r], end[r] = span((word['ports'][r],)), full
        elif r < 224:
            p = word['ports'][r - 112]
            start[r] = 1
            end[r] = sum(1 << x for x in range(512) if (x & p).bit_count() % 2 == 0)
        else:
            start[r], end[r] = 1, full
    for r, fr in word['start_extra'].items():
        start[int(r)] = span(tuple(fr))
    for r, fr in word['helper_final'].items():
        end[int(r)] = span(tuple(fr))
    current = dict(start)
    nodes = {r: [] for r in live}
    where = {}
    bill = Counter()

    def event(r, frame, address, kind='climb'):
        before = current[r]
        if kind != 'map':
            need(contained(before, frame), 'source frame containment')
            d = rank(frame) - rank(before)
            if kind == 'check':
                need(d == 0, 'source fixed boundary')
            elif d:
                bill[d] += 1
        if kind == 'climb':
            where[(address, r)] = len(nodes[r])
        nodes[r].append((address, kind, before, frame))
        current[r] = frame

    for i, gate in enumerate(word['A']):
        if gate[0] == 'warp':
            event(gate[1], span(tuple(gate[3])), ('check-A', i), 'check')
            event(gate[1], span(tuple(gate[4])), ('map-A', i), 'map')
        else:
            for r in touched(gate):
                event(r, span(tuple(gate[-1])), ('A', i))
    levels = {112 + int(r): span(tuple(fr)) for r, fr in word['target_levels'].items()}
    for r in range(112, 224):
        event(r, levels.get(r, 1), ('target-cut', r), 'check')
    for r, fr in zip(word['centers'], word['center_frames']):
        u = span(tuple(fr))
        event(r, u, ('centre-cut', r), 'check')
        served = {levels.get(g[1], 1) for g in word['cut'] if g[2] == r}
        for v in sorted(served, key=lambda x: -rank(x)):
            need(contained(v, u), 'centre nesting')
            if rank(u) > rank(v):
                bill[rank(u) - rank(v)] += 1
            u = v
        # The main forward register remains at its declared centre entry.
    warps = {}
    for j, rec in enumerate(word['warps']):
        warps.setdefault(rec[0], []).append((j, rec))
    for i in range(len(word['B']) + 1):
        for j, rec in warps.get(i, []):
            event(rec[1], span(tuple(rec[3])), ('check-B', j), 'check')
            event(rec[1], span(tuple(rec[4])), ('map-B', j), 'map')
        if i < len(word['B']):
            gate = word['B'][i]
            for r in touched(gate):
                event(r, span(tuple(gate[-1])), ('B', i))
    for i, gate in enumerate(word['restore']):
        for r in touched(gate):
            event(r, span(tuple(gate[-1])), ('restore', i))
    for r in live:
        event(r, end[r], ('end',))
    return nodes, where, dict(sorted(bill.items()))


def crosses(g, h):
    """Sufficient exact scalar normal form, not all algebraic commutations."""
    if h[0] == 'add':
        return g[1] != h[2] and h[1] != g[2]
    return h[0] == 'scale' and h[2] != 0


def segments(word, section):
    if section == 'A':
        cuts = [word['prelude_events'], len(word['A'])]
    elif section == 'B':
        cuts = sorted({0, len(word['B'])} | {rec[0] for rec in word['warps']})
    else:
        cuts = [0, len(word[section])]
    return list(zip(cuts, cuts[1:]))


def caps(delta):
    return [sum(n * min(r, k) for r, n in enumerate(delta)) for k in range(1, 10)]


def all_power_nonnegative(delta):
    """Sufficient exact certificate using decreasing positive curvatures."""
    values = caps(delta)
    prefix = 0
    for value in values[:-1]:
        prefix += value
        if prefix < 0:
            return False
    return values[-1] == 0


def census(word):
    nodes, where, bill = tracing(word)
    deltas = Counter()
    counts = {}
    for section in ('A', 'B', 'restore'):
        gates = word[section]
        count = 0
        for lo, hi in segments(word, section):
            occurrences = {}
            for i in range(lo, hi):
                need(gates[i][0] in ('add', 'scale'), 'unexpected scalar segment')
                for r in touched(gates[i]):
                    occurrences.setdefault(r, []).append(i)
            for i in range(lo, hi):
                g = gates[i]
                if g[0] != 'add':
                    continue
                lower = i
                while lower > lo and crosses(g, gates[lower - 1]):
                    lower -= 1
                upper = i + 1
                while upper < hi and crosses(g, gates[upper]):
                    upper += 1
                removal = [0] * 10
                reduced, entries, exits = {}, {}, {}
                for r in touched(g):
                    seq = nodes[r]
                    pos = where[((section, i), r)]
                    _, _, p, u = seq[pos]
                    need(pos + 1 < len(seq) and seq[pos + 1][1] != 'map', 'missing successor')
                    q = seq[pos + 1][3]
                    removal[rank(u) - rank(p)] -= 1
                    removal[rank(q) - rank(u)] -= 1
                    removal[rank(q) - rank(p)] += 1
                    indices = occurrences[r]
                    reduced[r] = [x for x in indices if x != i]
                    entries[r] = seq[where[((section, indices[0]), r)]][2]
                    last = where[((section, indices[-1]), r)]
                    need(seq[last + 1][1] != 'map', 'missing exit check')
                    exits[r] = seq[last + 1][3]
                for cut in range(lower, upper + 1):
                    if cut == i + 1:  # Same placement as cut i, counted once.
                        continue
                    boundaries = []
                    for r in touched(g):
                        indices = reduced[r]
                        j = bisect_left(indices, cut)
                        p = span(tuple(gates[indices[j - 1]][-1])) if j else entries[r]
                        q = span(tuple(gates[indices[j]][-1])) if j < len(indices) else exits[r]
                        boundaries.append((p, q))
                    lower_frame = join(boundaries[0][0], boundaries[1][0])
                    upper_frame = boundaries[0][1] & boundaries[1][1]
                    if not contained(lower_frame, upper_frame):
                        continue
                    dims = [(rank(p), rank(q)) for p, q in boundaries]
                    for d in range(rank(lower_frame), rank(upper_frame) + 1):
                        delta = removal.copy()
                        for p, q in dims:
                            delta[q - p] -= 1
                            delta[d - p] += 1
                            delta[q - d] += 1
                        delta[0] = 0
                        need(sum(r * n for r, n in enumerate(delta)) == 0, 'rank mass drift')
                        deltas[tuple(delta)] += 1
                        count += 1
        counts[section] = count
    return {'per_section': counts, 'candidates': sum(counts.values()),
            'source_profile': bill,
            'deltas': [{'delta': {r: n for r, n in enumerate(d) if n}, 'count': n,
                        'caps': caps(d), 'certificate': all_power_nonnegative(d)}
                       for d, n in sorted(deltas.items())]}


def apply_move(word, section, index, cut, frame):
    """Apply one exact scalar retiming. Caller must rederive cleanup and audit."""
    need(section in ('A', 'B', 'restore'), 'unknown section')
    gates = word[section]
    need(type(index) is int and 0 <= index < len(gates), 'bad source index')
    need(type(cut) is int and 0 <= cut <= len(gates), 'bad insertion cut')
    need(any(lo <= index < hi and lo <= cut <= hi for lo, hi in segments(word, section)),
         'crosses prelude or native warp boundary')
    g = deepcopy(gates[index])
    need(g[0] == 'add', 'only ADD moves are covered')
    crossed = gates[index + 1:cut] if cut > index else gates[cut:index]
    need(all(crosses(g, h) for h in crossed), 'noncommuting scalar barrier')
    coefficient = Fraction(g[3], g[4])
    for h in crossed:
        if h[0] == 'scale' and h[1] in touched(g):
            power = (1 if h[1] == g[1] else -1) * (1 if cut > index else -1)
            coefficient *= Fraction(h[2], h[3]) ** power
    g[3:5] = [coefficient.numerator, coefficient.denominator]
    g[-1] = list(basis(span(tuple(frame))))
    result = deepcopy(word)
    result[section].pop(index)
    result[section].insert(cut - (cut > index), g)
    # Segment length and all warp cuts are unchanged. No warp is crossed.
    return result
