"""All-rational hyperplane classification of the eight frozen producer values.

Forward reconstruction and Fraction elimination are independent of the
backward producer extraction used during discovery. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rref(matrix, n=8):
    a = [list(row) for row in matrix]
    pivots = []
    for c in range(n):
        r = len(pivots)
        pivot = next((i for i in range(r, len(a)) if a[i][c]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        q = a[r][c]
        a[r] = [v/q for v in a[r]]
        for i in range(len(a)):
            if i != r and a[i][c]:
                q = a[i][c]
                a[i] = [v-q*w for v, w in zip(a[i], a[r])]
        pivots.append(c)
        if len(pivots) == n:
            break
    kernels = []
    for free in sorted(set(range(n))-set(pivots)):
        v = [Q(0)]*n
        v[free] = Q(1)
        for row, c in enumerate(pivots):
            v[c] = -a[row][free]
        q = next(x for x in v if x)
        kernels.append([x/q for x in v])
    return len(pivots), kernels


def binary_basis(vectors):
    out = []
    for v in vectors:
        for w in out:
            v = min(v, v ^ w)
        if v:
            out.append(v)
            out.sort(reverse=True)
    return out


def classify(word):
    frames, events = word['frames'], word['program']
    need(all(0 < v < 512 for f in frames for v in f), 'ambient binary dimension nine')
    rows = [{i: Q(1)} for i in range(word['public'])]
    first = next(i for i, e in enumerate(events) if e[0] == 'INIT')
    for e in events[:first]:
        if e[0] == 'MOVE':
            continue
        d = e[1]
        if e[0] == 'SCALE':
            rows[d] = {i: Q(e[-2])*v for i, v in rows[d].items()}
        elif e[0] == 'ADD':
            for i, v in rows[e[2]].items():
                q = rows[d].get(i, Q(0))+Q(e[-2])*v
                if q:
                    rows[d][i] = q
                else:
                    rows[d].pop(i, None)
        else:
            raise ValueError('noninvertible public prefix')
    copies = [(i, e) for i, e in enumerate(events) if e[0] == 'COPY']
    need(len(copies) == 8, 'eight frozen producers')
    producers = []
    values = []
    for i, e in copies:
        need(not any(x[0] != 'MOVE' and x[1] == e[2] for x in events[first:i]),
             'source value unchanged between joint boundary and COPY')
        clear = next(x for x in events[i+1:] if x[0] == 'CLEAR' and x[1] == e[1])
        values.append(rows[e[2]])
        producers.append({'owned': e[1], 'source_role': e[2], 'copy_event': i,
                          'copy_frame': e[-1], 'clear_frame': clear[-1],
                          'initial_covector': {str(k): str(v) for k, v in sorted(rows[e[2]].items())}})
    counts, modes = Counter(), []
    for normal in range(1, 512):
        outside = [i for i, f in enumerate(word['initial'])
                   if any((normal & v).bit_count() % 2 for v in frames[f])]
        matrix = [[row.get(i, Q(0)) for row in values] for i in outside]
        rank, kernels = rref(matrix)
        counts[rank] += 1
        for coefficients in kernels:
            combination = {}
            for c, row in zip(coefficients, values):
                for i, v in row.items():
                    combination[i] = combination.get(i, Q(0))+c*v
            combination = {i: v for i, v in combination.items() if v}
            support = binary_basis(v for i in combination for v in frames[word['initial'][i]])
            need(not set(combination).intersection(outside), 'exact nullspace lies inside hyperplane')
            need(len(support) == 8, 'every nonzero proper-support mode has dimension eight')
            modes.append({'normal': normal, 'coefficients': [str(v) for v in coefficients],
                          'entry_support_dimension': len(support), 'entry_support_basis': support,
                          'original_symbols': len(combination),
                          'mixed': sum(bool(v) for v in coefficients) > 1})
    need(counts == {8: 495, 7: 16}, 'complete all-511 rational rank census')
    need(len(modes) == 16 and sum(m['mixed'] for m in modes) == 8, 'eight original and eight mixed lines')
    receipt = {'first_owned_init': first, 'source_roles': [e[2] for _, e in copies],
               'rank_counts': {str(k): v for k, v in sorted(counts.items())}, 'modes': modes,
               'scope': 'Every rational combination of the unchanged eight producer values; original-entry support geometry only.'}
    return receipt, modes, producers
