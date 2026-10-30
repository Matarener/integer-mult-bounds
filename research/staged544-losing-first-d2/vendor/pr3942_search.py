# SPDX-License-Identifier: Apache-2.0
"""Radius-one first ADD, unrestricted second ADD, exact frame-price census.

Chris R / Clear1nsight, with substantial OpenAI assistance. The pinned
PR3886 trace, applier and sign criterion are reused, not independently authored.
The interaction and single-new-gap reductions are proved in PROOF.md.
"""
from bisect import bisect_left
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import types

P = Path(__file__).resolve().parent

def module(name, path):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
    return value

# The entry point authenticates these bytes before loading this module.
R = module('pinned_retiming', P / 'vendor/retiming.py')
PHASES = ('A', 'B', 'restore')
ZERO = (0,) * 10

def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def rows(histogram):
    result = []
    for delta, count in sorted(histogram.items()):
        caps = R.caps(delta)
        prefixes = [sum(caps[:j]) for j in range(1, 9)]
        require(R.all_power_nonnegative(delta), 'uncertified signed profile')
        result.append({'delta': list(delta), 'count': count, 'caps': caps,
                       'prefixes': prefixes})
    return result

def geometry(word, section):
    nodes, where, bill = R.tracing(word)
    gates = word[section]
    for lo, hi in R.segments(word, section):
        occurrences = {}
        for i in range(lo, hi):
            for r in R.touched(gates[i]):
                occurrences.setdefault(r, []).append(i)
        entries, exits, removal = {}, {}, {}
        for r, indices in occurrences.items():
            entries[r] = nodes[r][where[((section, indices[0]), r)]][2]
            exits[r] = nodes[r][where[((section, indices[-1]), r)] + 1][3]
        for i in range(lo, hi):
            if gates[i][0] != 'add':
                continue
            delta = [0] * 10
            for r in R.touched(gates[i]):
                seq = nodes[r]
                pos = where[((section, i), r)]
                _, _, before, frame = seq[pos]
                require(seq[pos + 1][1] != 'map', 'missing map-entry check')
                after = seq[pos + 1][3]
                delta[R.rank(frame) - R.rank(before)] -= 1
                delta[R.rank(after) - R.rank(frame)] -= 1
                delta[R.rank(after) - R.rank(before)] += 1
            removal[i] = delta
        yield lo, hi, occurrences, entries, exits, removal

def candidates(word, section, selected, first=False, window=None):
    """Exact prices in the predecessor's fixed-check relaxation.

    First moves use cuts i-1, i, i+2. Cut i+1 duplicates the original position.
    For second moves all permitted corridor cuts and all frame dimensions occur.
    """
    gates = word[section]
    for lo, hi, occurrences, entries, exits, removal in geometry(word, section):
        for i in selected:
            if not lo <= i < hi or gates[i][0] != 'add':
                continue
            gate = gates[i]
            lower, upper = i, i + 1
            while lower > lo and R.crosses(gate, gates[lower - 1]):
                lower -= 1
            while upper < hi and R.crosses(gate, gates[upper]):
                upper += 1
            if window is not None:
                lower, upper = max(lower, window[0]), min(upper, window[1])
            cuts = [c for c in (i - 1, i, i + 2) if lower <= c <= upper] if first else range(lower, upper + 1)
            reduced = {r: [x for x in occurrences[r] if x != i] for r in R.touched(gate)}
            for cut in cuts:
                if cut == i + 1:
                    continue
                bounds = []
                for r in R.touched(gate):
                    indices = reduced[r]
                    j = bisect_left(indices, cut)
                    before = R.span(tuple(gates[indices[j - 1]][-1])) if j else entries[r]
                    after = R.span(tuple(gates[indices[j]][-1])) if j < len(indices) else exits[r]
                    bounds.append((before, after))
                low = R.join(bounds[0][0], bounds[1][0])
                high = bounds[0][1] & bounds[1][1]
                if not R.contained(low, high):
                    continue
                for dimension in range(R.rank(low), R.rank(high) + 1):
                    delta = removal[i].copy()
                    for before, after in bounds:
                        p, q = R.rank(before), R.rank(after)
                        delta[q - p] -= 1
                        delta[dimension - p] += 1
                        delta[q - dimension] += 1
                    delta[0] = 0
                    require(sum(r * n for r, n in enumerate(delta)) == 0, 'rank mass drift')
                    yield i, cut, dimension, low, high, tuple(delta)

@lru_cache(maxsize=None)
def frames(low, high, dimension):
    """All intermediate subspaces, not one representative per dimension."""
    require(R.contained(low, high), 'empty frame interval')
    require(R.rank(low) <= dimension <= R.rank(high), 'invalid frame dimension')
    require(R.rank(high) - R.rank(low) <= 4, 'first-frame resource bound exceeded')
    current = {low}
    for _ in range(dimension - R.rank(low)):
        expanded = set()
        for frame in current:
            for v in range(1, 512):
                if high >> v & 1 and not frame >> v & 1:
                    expanded.add(R.join(frame, R.span((v,))))
        current = expanded
    return tuple(sorted(current))

def first_moves(word):
    fixed, variable, seen = {}, [], set()
    counts = Counter()
    interval_checks = set()
    for section in PHASES:
        gates = word[section]
        for i, cut, dimension, low, high, delta in candidates(word, section, range(len(gates)), first=True):
            interval_checks.add((low, high, dimension))
            for frame in frames(low, high, dimension):
                if frame == R.span(tuple(gates[i][-1])):
                    if cut == i:
                        continue
                    pair = (section, min(i, cut))
                    if pair in seen:
                        continue
                    seen.add(pair)
                    require(delta == ZERO, 'fixed-frame swap was not neutral')
                    fixed[pair] = (i, cut, frame)
                    counts['fixed_adjacent'] += 1
                else:
                    kind = ('frame_only' if cut == i else 'adjacent') + ('_neutral' if delta == ZERO else '_losing')
                    require(R.all_power_nonnegative(delta), 'first move unexpectedly improves')
                    variable.append((section, i, cut, frame, delta, kind))
                    counts[kind] += 1
    # A separate structural enumeration checks completeness of fixed-frame swaps.
    direct = set()
    for section in PHASES:
        gates = word[section]
        for lo, hi in R.segments(word, section):
            for p in range(lo, hi - 1):
                g, h = gates[p:p + 2]
                if g[0] != 'add' and h[0] != 'add':
                    continue
                a, b = (g, h) if g[0] == 'add' else (h, g)
                if not R.crosses(a, b):
                    continue
                if set(R.touched(g)) & set(R.touched(h)) and R.span(tuple(g[-1])) != R.span(tuple(h[-1])):
                    continue
                direct.add((section, p))
    require(set(fixed) == direct, 'fixed-swap enumerators disagree')
    return fixed, variable, counts, interval_checks

def bridge_census(word, fixed):
    """Only the newly opened gap can have a new price after a fixed-frame swap."""
    histogram, counts = Counter(), Counter()
    nonzero = []
    for section in PHASES:
        gates = word[section]
        touched = [set(R.touched(g)) for g in gates]
        for lo, hi, occurrences, entries, exits, removal in geometry(word, section):
            for p in range(lo, hi - 1):
                if (section, p) not in fixed:
                    continue
                counts['first_pairs'] += 1
                g, h = gates[p:p + 2]
                selected = sorted({j for r in touched[p] for j in occurrences[r]
                                   if gates[j][0] == 'add' and j not in (p, p + 1)
                                   and touched[j] & touched[p + 1]})
                for j in selected:
                    counts['bridge_gates'] += 1
                    crossed = gates[j + 1:p] + [h] if j < p else [g] + gates[p + 2:j]
                    if not all(R.crosses(gates[j], e) for e in crossed):
                        continue
                    counts['scalar_legal'] += 1
                    bounds = []
                    for r in R.touched(gates[j]):
                        indices = occurrences[r]
                        left = bisect_left(indices, p) - 1
                        if left >= 0 and indices[left] == j:
                            left -= 1
                        before = R.span(tuple(gates[indices[left]][-1])) if left >= 0 else entries[r]
                        right = bisect_left(indices, p + 2)
                        if right < len(indices) and indices[right] == j:
                            right += 1
                        after = R.span(tuple(gates[indices[right]][-1])) if right < len(indices) else exits[r]
                        if r in touched[p + 1]:
                            before = R.span(tuple(h[-1]))
                        if r in touched[p]:
                            after = R.span(tuple(g[-1]))
                        bounds.append((before, after))
                    low = R.join(bounds[0][0], bounds[1][0])
                    high = bounds[0][1] & bounds[1][1]
                    if not R.contained(low, high):
                        continue
                    for dimension in range(R.rank(low), R.rank(high) + 1):
                        delta = removal[j].copy()
                        for before, after in bounds:
                            a, b = R.rank(before), R.rank(after)
                            delta[b - a] -= 1
                            delta[dimension - a] += 1
                            delta[b - dimension] += 1
                        delta[0] = 0
                        histogram[tuple(delta)] += 1
                        if any(delta):
                            nonzero.append([section, p, j, dimension, delta])
                        counts['candidate_dimensions'] += 1
    return {'counts': dict(counts), 'profiles': rows(histogram), 'nonzero_cases': nonzero}

def variable_census(word, variable, auditor=None, progress=False):
    baseline = R.tracing(word)[2]
    histogram, by_kind = Counter(), {}
    for number, (section, i, cut, frame, first_delta, kind) in enumerate(variable):
        middle = R.apply_move(word, section, i, cut, R.basis(frame))
        intermediate = R.tracing(middle)[2]
        require(tuple(intermediate.get(r, 0) - baseline.get(r, 0) if r else 0 for r in range(10)) == first_delta,
                'first actual invoice differs from relaxation')
        if auditor is not None:
            require(auditor.frame_bill(middle)[0] == intermediate, 'retained first-word invoice disagrees')
        moved = cut - (cut > i)
        registers = set(R.touched(word[section][i]))
        counts = by_kind.setdefault(kind, Counter())
        counts['first_words'] += 1
        for second_section in PHASES:
            selected = [j for j, g in enumerate(middle[second_section])
                        if g[0] == 'add' and registers.intersection(R.touched(g))
                        and (second_section, j) != (section, moved)]
            for _, _, _, _, _, second_delta in candidates(middle, second_section, selected):
                delta = tuple(a + b for a, b in zip(first_delta, second_delta))
                histogram[delta] += 1
                counts['second_cut_dimensions'] += 1
        if progress and number % 100 == 0:
            print('Checked first word', number, 'of', len(variable), flush=True)
    return {'by_kind': {k: dict(v) for k, v in sorted(by_kind.items())}, 'profiles': rows(histogram)}

def compute(word, auditor=None, progress=False):
    fixed, variable, counts, intervals = first_moves(word)
    serial = [[s, p, i, c, list(R.basis(f))] for (s, p), (i, c, f) in sorted(fixed.items())]
    serial += [[s, i, c, list(R.basis(f)), list(d), k] for s, i, c, f, d, k in variable]
    return {'first_counts': dict(sorted(counts.items())), 'first_digest': digest(serial),
            'max_first_quotient_dimension': max(R.rank(h) - R.rank(l) for l, h, _ in intervals),
            'fixed_frame': bridge_census(word, fixed),
            'variable_frame': variable_census(word, variable, auditor, progress)}
