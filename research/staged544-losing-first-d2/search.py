# SPDX-License-Identifier: Apache-2.0
"""Losing first ADD at displacement exactly two, unrestricted second ADD.

Chris R / Clear1nsight, with substantial OpenAI assistance. The pinned
PR3886 trace, applier and sign criterion are reused, not independently authored.
Adapted from PR3942 with its retained source. The interaction reduction is reused.
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
R.all_power_nonnegative = lru_cache(maxsize=None)(R.all_power_nonnegative)

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
        require(sum(r*n for r,n in enumerate(delta))==0,'histogram rank mass')
        result.append({'delta': list(delta), 'count': count, 'caps': caps,
                       'prefixes': prefixes, 'certificate': R.all_power_nonnegative(delta)})
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

    First moves use cuts i-2 and i+3, hence final displacement exactly two.
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
            cuts = [c for c in (i - 2, i + 3) if lower <= c <= upper] if first else range(lower, upper + 1)
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

def first_moves(word, auditor=None):
    variable, counts, intervals = [], Counter(), set()
    for section in PHASES:
        gates = word[section]
        for i, cut, dimension, low, high, delta in candidates(word, section, range(len(gates)), first=True):
            require(abs(cut - (cut > i) - i) == 2, 'first displacement is not exactly two')
            intervals.add((low, high, dimension))
            counts['first_price_cells'] += 1
            require(R.all_power_nonnegative(delta), 'unclassified first profile')
            if delta == ZERO:
                counts['neutral_price_cells_excluded'] += 1
                continue
            for frame in frames(low, high, dimension):
                counts['losing_subspace_records'] += 1
                variable.append((section, i, cut, frame, delta, 'displacement_two_losing'))
    return variable, counts, intervals

def variable_census(word, variable, auditor=None, progress=False):
    D = module('dirty_blocks', P/'dirty_blocks.py')
    baseline = R.tracing(word)[2]
    histogram, first_histogram, counts = Counter(), Counter(), Counter()
    states, block_checks, rejected, uncertified_witnesses = [], [], [], {}
    for number, (section, i, cut, frame, first_delta, kind) in enumerate(variable):
        middle = R.apply_move(word, section, i, cut, R.basis(frame))
        try:
            intermediate = R.tracing(middle)[2]
        except ValueError as error:
            require(str(error) in ('source fixed boundary','source frame containment'), 'unexpected first rejection: '+str(error))
            rejected.append([section,i,cut,list(R.basis(frame)),str(error)])
            continue
        require(tuple(intermediate.get(r, 0) - baseline.get(r, 0) if r else 0 for r in range(10)) == first_delta,
                'first actual invoice differs from relaxation')
        if auditor is not None:
            require(auditor.frame_bill(middle)[0] == intermediate, 'retained first-word invoice disagrees')
        require(sum(r*n for r,n in intermediate.items())==sum(r*n for r,n in baseline.items()),'first rank mass differs')
        lo,hi=min(i,cut),max(i+1,cut)
        block_checks.append(D.block_equal(word[section][lo:hi],middle[section][lo:hi]))
        first_histogram[first_delta]+=1
        moved = cut - (cut > i)
        registers = set(R.touched(word[section][i]))
        local=Counter()
        for second_section in PHASES:
            selected = [j for j, g in enumerate(middle[second_section])
                        if g[0] == 'add' and registers.intersection(R.touched(g))
                        and (second_section, j) != (section, moved)]
            for j, target, dimension, low, high, second_delta in candidates(middle, second_section, selected):
                delta = tuple(a + b for a, b in zip(first_delta, second_delta))
                histogram[delta] += 1
                local[delta] += 1
                if delta not in uncertified_witnesses and not R.all_power_nonnegative(delta):
                    # An insufficient sign certificate is retained, never treated as a gain.
                    uncertified_witnesses[delta]={'first':[section,i,cut,list(R.basis(frame)),list(first_delta)],
                      'second':[second_section,j,target,dimension,low,high,list(second_delta)]}
        n=sum(local.values());counts['first_words']+=1;counts['second_cut_dimensions']+=n
        states.append({'first':[section,i,cut,list(R.basis(frame)),list(first_delta)],'profile':intermediate,
                       'second_cut_dimensions':n,'second_histogram_sha256':digest(sorted((list(d),n) for d,n in local.items()))})
        if progress and (number%50==0 or number+1==len(variable)):
            print('FIRST_AND_SECOND',number+1,'of',len(variable),'prices',counts['second_cut_dimensions'],flush=True)
    return {'counts':dict(counts),'first_profiles':rows(first_histogram),'profiles':rows(histogram),
            'states':states,'dirty_block_checks':len(block_checks),'dirty_block_stream_sha256':digest(block_checks),
            'boundary_rejected':rejected,'uncertified_witnesses':list(uncertified_witnesses.values())}

def compute(word, auditor=None, progress=False):
    variable, counts, intervals = first_moves(word, auditor)
    if progress:print('FIRST_DOMAIN',dict(counts),'intervals',len(intervals),flush=True)
    serial = [[s, i, c, list(R.basis(f)), list(d), k] for s, i, c, f, d, k in variable]
    return {'first_counts': dict(sorted(counts.items())), 'first_digest': digest(serial),
            'first_intervals':[[l,h,d] for l,h,d in sorted(intervals)],
            'max_first_quotient_dimension': max(R.rank(h)-R.rank(l) for l,h,_ in intervals),
            'variable_frame': variable_census(word, variable, auditor, progress)}
