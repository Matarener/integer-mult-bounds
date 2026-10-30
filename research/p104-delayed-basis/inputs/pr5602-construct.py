"""Construct the fixed helper basis changes and coupled handoffs.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source word and its contributors are recorded in SOURCES.json.
"""
from copy import deepcopy
from fractions import Fraction as Q
import local as L


def row(pairs):
    out = {r: Q(q) for r, q in pairs}
    L.need(len(out) == len(pairs) and all(out.values()), 'Unique nonzero witness row')
    return out


def unit(q):
    n, d = abs(q.numerator), q.denominator
    return n > 0 and n & (n-1) == 0 and d & (d-1) == 0


def main_fields(w):
    return set(w['live']) | {r+112 for r in w['live']}


def prefix(w, cut):
    n = w['public']
    rows = [{i: Q(1)} for i in range(n)] + [{} for _ in range(8)]
    frames = w['initial'][:] + [None]*8
    L.need(0 <= cut < len(w['program']), 'Cut in the literal word')
    for e in w['program'][:cut+1]:
        op, r = e[:2]
        if op == 'MOVE':
            L.need(frames[r] == e[2], 'Prefix transport source')
            frames[r] = e[3]
        elif op in ('INIT', 'CLEAR'):
            rows[r] = {}
            frames[r] = e[2] if op == 'INIT' else None
        else:
            L.need(frames[r] == e[-1], 'Prefix scalar chart')
            if op == 'SCALE':
                rows[r] = {k: Q(e[-2])*v for k, v in rows[r].items()}
            else:
                L.need(frames[e[2]] == e[-1], 'Prefix source chart')
                if op == 'COPY':
                    L.need(not rows[r], 'Source COPY into zero')
                L.add(rows[r], rows[e[2]], Q(e[-2]))
    return rows, frames


def suffix_columns(w, cut):
    cols = [{i: Q(1)} for i in range(w['public'])] + [{} for _ in range(8)]
    for e in reversed(w['program'][cut+1:]):
        op, r = e[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR'):
            cols[r] = {}
        elif op == 'SCALE':
            cols[r] = {k: Q(e[-2])*v for k, v in cols[r].items()}
        else:
            L.add(cols[e[2]], cols[r], Q(e[-2]))
            if op == 'COPY':
                cols[r] = {}
    return cols


def transpose(w):
    program = []
    for e in reversed(w['program']):
        op, r = e[:2]
        if op == 'MOVE':
            z = ['MOVE', r, e[3], e[2], e[4]]
        elif op in ('ADD', 'COPY'):
            z = ['ADD', e[2], r, e[3], e[4]]
        elif op == 'SCALE':
            z = e[:]
        else:
            L.need(op in ('INIT', 'CLEAR'), 'Transpose opcode')
            z = ['CLEAR' if op == 'INIT' else 'INIT', r, e[2]]
        program.append(z)
    return dict(w, initial=w['final'][:], final=w['initial'][:], program=program)


def boundary_basis(w, c):
    w = transpose(w) if c['reverse'] else deepcopy(w)
    h, cut, frame = c['helper'], c['cut'], c['frame']
    output, cancel = row(c['output']), row(c['cancel'])
    helpers = set(range(w['public'])) - main_fields(w)
    L.need(h in helpers and unit(output.get(h, Q(0))), 'Helper unit boundary pivot')
    source = w['initial'][h]
    L.need(set(output) <= {r for r in helpers if w['initial'][r] == source},
           'Boundary basis uses one helper input chart')
    rows, frames = prefix(w, cut)
    L.need(frames[h] == frame and h not in cancel and
           all(frames[r] == frame for r in cancel), 'Available boundary cancellation')
    value = rows[h].copy()
    for r, q in cancel.items():
        L.add(value, rows[r], -q)
    L.need(value == output, 'Exact boundary helper relation')
    tail = w['program'][cut+1:]
    L.need(not any(e[0] in ('ADD', 'COPY') and e[2] == h for e in tail),
           'Retired helper has no later source read')
    coefficient = output[h]
    before = [['ADD', h, r, str(-q/coefficient), source]
              for r, q in sorted(output.items()) if r != h]
    middle = [['ADD', h, r, str(-q), frame] for r, q in sorted(cancel.items())]
    if coefficient != 1:
        middle.append(['SCALE', h, str(1/coefficient), frame])
    w['program'] = before + w['program'][:cut+1] + middle + [e for e in tail if e[1] != h]
    w['final'][h] = frame
    return transpose(w) if c['reverse'] else w


def inverse(ops):
    out = []
    for e in reversed(ops):
        z = e[:]
        z[-2] = str(1/Q(e[-2]) if e[0] == 'SCALE' else -Q(e[-2]))
        out.append(z)
    return out


def basis(a, b, p, frame):
    """Return a matrix R with a R = e_p^T and R e_p = b."""
    L.need(sum(a.get(h, 0)*q for h, q in b.items()) == 1, 'Dual basis pairing')
    q = next((h for h in sorted(a) if unit(a[h])), None)
    L.need(q is not None, 'Dyadic basis pivot')
    ops = [] if p == q else [
        ['ADD', p, q, '1', frame], ['ADD', q, p, '-1', frame],
        ['ADD', p, q, '1', frame], ['SCALE', q, '-1', frame]]
    ops += [['ADD', j, q, str(c), frame] for j, c in sorted(b.items()) if j != q]
    if a[q] != 1:
        ops.append(['SCALE', q, str(1/a[q]), frame])
    ops += [['ADD', q, j, str(-c/a[q]), frame] for j, c in sorted(a.items()) if j != q]
    return ops


def relabel(e, mapping):
    z = e[:]
    z[1] = mapping(z[1])
    if z[0] in ('ADD', 'COPY'):
        z[2] = mapping(z[2])
    return z


def handoff(w, c):
    n, cut, frame, p = w['public'], c['cut'], c['frame'], c['pivot']
    source, target = c['group']
    group = {h for h in range(n) if h not in main_fields(w) and
             (w['initial'][h], w['final'][h]) == (source, target)}
    v, u = row(c['v']), row(c['u'])
    pairing = sum(v.get(h, 0)*q for h, q in u.items())
    L.need(unit(pairing), 'Nonzero dyadic handoff pairing')
    v = {h: q/pairing for h, q in v.items()}
    rows, frames = prefix(w, cut)
    L.need(all(f is None for f in frames[n:]), 'No owned field at handoff cut')
    L.need(p in group and frames[p] == frame and
           all(0 <= h < n and frames[h] == frame for h in v.keys() | u.keys()),
           'Public handoff fields share the cut chart')
    L.need(L.span(w['frames'][source]) < L.span(w['frames'][frame]) <
           L.span(w['frames'][target]), 'Strict nested handoff boundaries')
    cols, a, b = suffix_columns(w, cut), {}, {}
    for r, q in v.items():
        L.add(a, rows[r], q)
    for r, q in u.items():
        L.add(b, cols[r], q)
    L.need(a == row(c['source_functional']) and b == row(c['output_direction']),
           'Exact prefix and suffix handoff witnesses')
    L.need(set(a) <= group and set(b) <= group, 'Handoff has only helper boundary support')
    input_ops, cut_basis = basis(a, b, p, source), basis(v, u, p, frame)
    output_ops = inverse(input_ops)
    for e in output_ops:
        e[-1] = target
    old = lambda r: r+1 if r >= n else r
    tail = lambda r: n if r == p else old(r)
    out = deepcopy(w)
    out['public'] = n+1
    out['initial'].append(frame)
    out['final'][p] = frame
    out['final'].append(target)
    out['program'] = input_ops + [relabel(e, old) for e in w['program'][:cut+1]]
    out['program'] += inverse(cut_basis) + [relabel(e, tail) for e in cut_basis]
    out['program'] += [relabel(e, tail) for e in w['program'][cut+1:]]
    out['program'] += [relabel(e, tail) for e in output_ops]
    return out


def restore_copy_opcodes(w):
    fresh, copies = set(), 0
    for e in w['program']:
        op, r = e[:2]
        if op == 'INIT':
            fresh.add(r)
        elif r in fresh and op != 'MOVE':
            L.need(op == 'ADD', 'First owned write is the retained copy')
            e[0] = 'COPY'
            fresh.remove(r)
            copies += 1
    L.need(not fresh and copies == 8, 'All eight owned copy paths remain')


def construct(base, witness):
    L.need(witness['schema'] == 'p104-coupled-helper-bases/1', 'Witness schema')
    L.need([s['kind'] for s in witness['steps']] ==
           ['boundary_basis']*6 + ['coupled_handoff']*9, 'Fixed fifteen changes')
    word, evidence = deepcopy(base), []
    for step in witness['steps']:
        word = boundary_basis(word, step) if step['kind'] == 'boundary_basis' else handoff(word, step)
        check = L.replay(word)
        evidence.append(dict(kind=step['kind'], public=word['public'],
                             events=len(word['program']), paid=check['paid'], helpers=check['helpers']))
    restore_copy_opcodes(word)
    L.replay(word)
    return word, evidence
