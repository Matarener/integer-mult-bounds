"""Exact response spaces at every source cut, modulo ground-helper repair.

Invertible coframed ADD and SCALE events preserve the complete field span.
All other span changes are checked. Ali Romman with Codex assistance.
Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from inputs import need, add, index

def extend(nuisance, mode, witness, basis, channels):
    """Extend a nuisance basis and return a new pure-mode witness, if any."""
    a, v, coefficients = dict(nuisance), list(mode), dict(witness)
    while a:
        pivot = min(a)
        if pivot not in basis:
            factor = a[pivot]
            basis[pivot] = ({i:x/factor for i,x in a.items()},
                            [x/factor for x in v],
                            {i:x/factor for i,x in coefficients.items()})
            return None
        row, values, saved = basis[pivot]
        factor = a[pivot]
        add(a, row, -factor)
        v = [x-factor*y for x,y in zip(v, values)]
        add(coefficients, saved, -factor)
    for pivot, (row, saved) in channels.items():
        factor = v[pivot]
        v = [x-factor*y for x,y in zip(v,row)]
        add(coefficients,saved,-factor)
    if not any(v): return None
    pivot = next(i for i,x in enumerate(v) if x)
    factor = v[pivot]
    v = [x/factor for x in v]
    coefficients = {i:x/factor for i,x in coefficients.items()}
    channels[pivot] = (v, coefficients)
    return v, coefficients


def scan(w, R):
    es = w['programs']['backward']
    n = 633 + w['owned_extra_slots_by_direction']['backward']
    cols = [{i: F(1)} for i in range(632)] + [{} for _ in range(n - 632)]
    idx = index
    cur = w['canonical']['start'][:] + [None] * (n - 632)
    before = {}
    for pos, e in enumerate(es):
        typ = e[0]
        if typ == 'scalar' and e[1][0] == 'clear':
            d = idx(e[1][1])
            before[pos] = (d, cur[d])
            cur[d] = e[2]
        elif typ == 'climb':
            d = e[2]
            before[pos] = (d, cur[d])
            need(cur[d] == e[3], 'Exact reverse frame')
            cur[d] = e[4]
        elif typ == 'warp':
            d = idx(e[1])
            before[pos] = (d, cur[d])
            need(cur[d] == e[3], 'Exact reverse frame')
            cur[d] = e[4]
    pivots = {}
    selected = []
    for i in range(112):
        v = [R[j][i] for j in range(8)]
        for p, b in pivots.items():
            a = v[p]
            v = [x - a * y for x, y in zip(v, b)]
        if any(v):
            p = next((j for j, x in enumerate(v) if x))
            a = v[p]
            pivots[p] = [x / a for x in v]
            selected.append(i)
        if len(selected) == 8:
            break
    A = [[R[j][i] for j in range(8)] + [F(k == l) for l in range(8)] for k, i in enumerate(selected)]
    for k in range(8):
        z = next((j for j in range(k, 8) if A[j][k]))
        A[k], A[z] = (A[z], A[k])
        v = A[k][k]
        A[k] = [x / v for x in A[k]]
        for j in range(8):
            if j != k:
                v = A[j][k]
                A[j] = [x - v * y for x, y in zip(A[j], A[k])]
    I = [row[8:] for row in A]
    project_cache = {}
    done = set()
    records = []
    rank_counts = Counter()
    tested = 0
    temporal = {}
    temporal_responses = []
    temporal_observations = 0

    def project(col):
        key = tuple(sorted(col.items()))
        if key in project_cache:
            return project_cache[key]
        mode = [sum((I[j][k] * col.get(i, F(0)) for k, i in enumerate(selected)), F(0)) for j in range(8)]
        nuisance = {i: v for i, v in col.items() if i < 224 or w['canonical']['start'][i] != 0}
        for j, v in enumerate(mode):
            if v:
                for i, a in enumerate(R[j]):
                    x = nuisance.get(i, F(0)) - v * a
                    if x:
                        nuisance[i] = x
                    else:
                        nuisance.pop(i, None)
        project_cache[key] = (nuisance, mode)
        return (nuisance, mode)

    def inspect(f, pos):
        nonlocal tested, temporal_observations
        fields = [i for i, x in enumerate(cur) if x == f and cols[i]]
        if not fields:
            return
        if len(w['canonical']['frames'][f]) == 9 and pos != len(es):
            return
        key = (f, tuple(((i, tuple(sorted(cols[i].items()))) for i in fields)))
        if key in done:
            return
        done.add(key)
        tested += 1
        vectors = [project(cols[i]) for i in fields]
        historical, historical_modes, seen = temporal.setdefault(f, ({}, {}, set()))
        for owner, (raw, v) in zip(fields, vectors):
            key = tuple(sorted(cols[owner].items()))
            if key in seen: continue
            seen.add(key); temporal_observations += 1
            found = extend(raw, v, {(pos, owner): F(1)}, historical, historical_modes)
            if found is not None:
                values, coefficients = found
                temporal_responses.append(dict(frame=f, rank=len(w['canonical']['frames'][f]),
                    mode=list(map(str, values)), scatter=[[at, field, str(c)] for (at, field), c in sorted(coefficients.items())]))
        if not any(any(v) for _,v in vectors): return
        basis, modes, witnesses = {}, {}, []
        for owner, (raw, v) in zip(fields, vectors):
            found = extend(raw, v, {owner:F(1)}, basis, modes)
            if found is not None: witnesses.append(found)
        if modes:
            rank = len(w['canonical']['frames'][f])
            rank_counts[rank] += 1
            for v, z in witnesses:
                records.append(dict(event=pos, frame=f, rank=rank, mode=list(map(str, v)), scatter=[[i, str(x)] for i, x in sorted(z.items())]))
    for f in sorted(set(cur) - {None}):
        inspect(f, len(es))
    for pos in reversed(range(len(es))):
        e = es[pos]
        typ = e[0]
        changed = []
        if typ == 'scalar':
            a = e[1]
            d = idx(a[1])
            kind = a[0]
            if kind == 'add':
                s = idx(a[2])
                need(d != s and cur[s] == cur[d] == e[2], 'Invertible coframed ADD')
                add(cols[s], cols[d], F(a[3], a[4]))
                changed = []
            elif kind == 'copy':
                s = idx(a[2])
                add(cols[s], cols[d], F(1))
                cols[d] = {}
                changed = [s, d]
            elif kind == 'clear':
                cols[d] = {}
                changed = [d]
            elif kind == 'scale':
                need(a[2] and cur[d] == e[2], 'Invertible coframed SCALE')
                cols[d] = {i: v * F(a[2], a[3]) for i, v in cols[d].items()}
                changed = []
        if pos in before:
            d, old = before[pos]
            frames = {cur[d], old}
            cur[d] = old
        else:
            frames = set()
        frames |= {cur[d] for d in changed}
        for f in sorted(frames - {None}):
            inspect(f, pos)
    return dict(contexts=tested, projected_columns=len(project_cache), mode_contexts_by_rank=dict(rank_counts), responses=records, temporal_observations=temporal_observations, temporal_responses=temporal_responses)
