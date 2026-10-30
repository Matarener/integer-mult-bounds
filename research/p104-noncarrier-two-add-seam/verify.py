"""Exact two-ADD seam exclusion. JoyboyBrian with OpenAI Codex, Apache-2.0."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
WORD = 'research/p104-helper470-twin-rung-removal/WORD.json.gz'
CUT = 13637
FIRST = range(CUT, 13652)
SECOND = (13652, 13654, 13655)
PIVOT = 572


def need(ok, message):
    if not ok:
        raise ValueError(message)


def add(a, b, scale=Q(1)):
    result = a.copy()
    for k, v in b.items():
        value = result.get(k, 0) + scale * v
        if value:
            result[k] = value
        else:
            result.pop(k, None)
    return result


def forward(rows, event):
    op, r = event[:2]
    if op == 'ADD':
        rows[r] = add(rows[r], rows[event[2]], Q(event[3]))
    elif op == 'COPY':
        rows[r] = {k: Q(event[3]) * v for k, v in rows[event[2]].items() if Q(event[3]) * v}
    elif op == 'SCALE':
        rows[r] = {k: Q(event[2]) * v for k, v in rows[r].items() if Q(event[2]) * v}
    elif op in ('INIT', 'CLEAR'):
        rows[r] = {}
    else:
        need(op == 'MOVE', 'known scalar opcode')


def initial(word):
    return [{i: Q(1)} for i in range(word['public'])] + [{} for _ in range(word['owned_fields'])]


def boundaries(word):
    n = word['public']
    rows = initial(word)
    charts = word['initial'] + [None] * word['owned_fields']
    prefix, banks, beta = {}, {}, {}
    signal = [{} for _ in rows]
    for i, event in enumerate(word['program']):
        op, r = event[:2]
        if op == 'INIT':
            need(charts[r] is None, 'INIT is dead')
            charts[r] = event[2]
        elif op == 'MOVE':
            need(charts[r] == event[2], 'MOVE source chart')
            charts[r] = event[3]
        elif op == 'CLEAR':
            need(charts[r] == event[2], 'CLEAR chart')
            charts[r] = None
        else:
            need(charts[r] == event[-1], 'target chart')
            if op in ('ADD', 'COPY'):
                need(charts[event[2]] == event[-1], 'source chart')
        forward(rows, event)
        if i == CUT:
            signal[PIVOT] = {0: Q(1)}
        elif i > CUT:
            forward(signal, event)
        if i in FIRST or i in SECOND:
            banks[i] = {c: tuple(r for r, f in enumerate(charts) if f == c) for c in (595, 603)}
            prefix[i] = {r: rows[r].copy() for bank in banks[i].values() for r in bank}
            beta[i] = {r: signal[r].get(0, Q(0)) for bank in banks[i].values() for r in bank}
    need(charts[:n] == word['final'] and all(f is None for f in charts[n:]), 'final charts/lifetimes')
    need(all(not row for row in rows[n:]), 'original owned rows restored')
    baseline = rows
    columns = initial(word)
    suffix = {}
    for i in range(len(word['program']) - 1, -1, -1):
        if i in banks:
            suffix[i] = {r: columns[r].copy() for bank in banks[i].values() for r in bank}
        event = word['program'][i]
        op, r = event[:2]
        if op in ('ADD', 'COPY'):
            s, q = event[2], Q(event[3])
            columns[s] = add(columns[s], columns[r], q)
            if op == 'COPY':
                columns[r] = {}
        elif op == 'SCALE':
            columns[r] = {k: Q(event[2]) * v for k, v in columns[r].items() if Q(event[2]) * v}
        elif op in ('INIT', 'CLEAR'):
            columns[r] = {}
        else:
            need(op == 'MOVE', 'reverse opcode')
    transpose = [{} for _ in columns]
    for out, row in enumerate(baseline[:n]):
        for inp, value in row.items():
            transpose[inp][out] = value
    need(columns == transpose, 'full forward/reverse adjoint equality')
    need(banks[CUT][595] == (127, 572, 581, 582, 731, 778), 'first chart inventory')
    need(word['program'][13652] == ['MOVE', 572, 595, 603, False], 'fixed seam')
    return prefix, suffix, banks, beta, baseline


def transfer(word, i, target, j):
    state = [{} for _ in range(word['public'] + word['owned_fields'])]
    state[target] = {0: Q(1)}
    for event in word['program'][i + 1:j + 1]:
        forward(state, event)
    return state


def coefficients(case, data, word):
    i, u, v, j, s, r = case
    prefix, suffix, banks, beta, baseline = data
    ell = prefix[CUT][PIVOT]
    b1, b2 = beta[i][u], beta[j][s]
    g = transfer(word, i, v, j)[s].get(0, Q(0))
    f = add(prefix[i][u], ell, -b1)
    h = add(prefix[j][s], ell, -b2)
    f[word['public']] = b1
    h[word['public']] = b2
    f = {k: q for k, q in f.items() if q}
    h = {k: q for k, q in h.items() if q}
    e = {k: -q for k, q in ell.items()}
    e[word['public']] = Q(1)
    return suffix[CUT][PIVOT], suffix[i][v], suffix[j][r], e, f, h, g


def equations(parts, outside):
    d, A, B, e, f, h, g = parts
    for out in sorted(outside.intersection(set(d) | set(A) | set(B))):
        for inp in sorted(set(e) | set(f) | set(h)):
            yield (out, inp), [A.get(out, 0) * f.get(inp, 0),
                              B.get(out, 0) * h.get(inp, 0),
                              B.get(out, 0) * g * f.get(inp, 0)], -d.get(out, 0) * e.get(inp, 0)


def contradiction(eqs):
    pivots = {}
    for label, values, rhs in eqs:
        row = {j: q for j, q in enumerate(values) if q}
        weights = {label: Q(1)}
        for j, (pivot, value, origin) in pivots.items():
            if j in row:
                q = row[j]
                row = add(row, pivot, -q)
                rhs -= q * value
                weights = add(weights, origin, -q)
        if not row:
            if rhs:
                return {label: q / rhs for label, q in weights.items() if q}
        else:
            j = min(row)
            q = row[j]
            pivots[j] = ({k: v / q for k, v in row.items()}, rhs / q,
                         {label: v / q for label, v in weights.items()})
    return None


def check_dual(eqs, weights):
    """Direct dot products, independent of the elimination/row-add engine."""
    rows = {label: (values, rhs) for label, values, rhs in eqs}
    need(weights is not None and all(label in rows for label in weights), 'dual labels')
    lhs = [sum((q * rows[label][0][j] for label, q in weights.items()), Q(0)) for j in range(3)]
    rhs = sum((q * rows[label][1] for label, q in weights.items()), Q(0))
    need(lhs == [0, 0, 0] and rhs == 1, 'dual proves zero equals one')


def literal(word, case, a, b):
    """Separate whole-word row interpreter; does not call forward/add."""
    rows = initial(word)
    i, u, v, j, s, r = case
    for k, event in enumerate(word['program']):
        op, target = event[:2]
        if op in ('ADD', 'COPY'):
            source, q = event[2], Q(event[3])
            old = rows[target] if op == 'ADD' else {}
            rows[target] = {c: value
                            for c in old.keys() | rows[source].keys()
                            if (value := old.get(c, Q(0)) + q * rows[source].get(c, Q(0)))}
        elif op == 'SCALE':
            rows[target] = {c: Q(event[2]) * q for c, q in rows[target].items() if Q(event[2]) * q}
        elif op in ('INIT', 'CLEAR'):
            rows[target] = {}
        else:
            need(op == 'MOVE', 'literal opcode')
        if k == CUT:
            rows[PIVOT] = {word['public']: Q(1)}
        for when, source, target, q in ((i, u, v, a), (j, s, r, b)):
            if k == when:
                old = rows[target]
                rows[target] = {c: value
                                for c in old.keys() | rows[source].keys()
                                if (value := old.get(c, Q(0)) + q * rows[source].get(c, Q(0)))}
    return rows


def controls(word, data, outside):
    eqs = [((0, 0), [Q(1), Q(0), Q(0)], Q(0)),
           ((0, 1), [Q(1), Q(0), Q(0)], Q(1))]
    witness = contradiction(eqs)
    check_dual(eqs, witness)
    need(contradiction(eqs[:1]) is None, 'consistent system accepted')
    try:
        check_dual(eqs, {k: 2 * v for k, v in witness.items()})
    except ValueError:
        pass
    else:
        raise ValueError('forged dual accepted')
    # A non-carrier two-ADD repair exists in a synthetic changed boundary.
    positive = ({0: Q(1), 1: Q(1)}, {0: Q(1)}, {0: Q(1)},
                {0: Q(-1), 1: Q(1)}, {0: Q(1)}, {1: Q(1)}, Q(0))
    need(contradiction(equations(positive, {0})) is None, 'changed-boundary positive admitted')
    for _, values, rhs in equations(positive, {0}):
        need(values[0] - values[1] - values[2] == rhs, 'positive a=1,b=-1,c=-1')
    damaged = dict(word)
    damaged['program'] = [event.copy() for event in word['program']]
    damaged['program'][13652][3] = 597
    try:
        boundaries(damaged)
    except ValueError as error:
        need(str(error) == 'source chart', 'wrong seam rejected at an actual consumer')
    else:
        raise ValueError('wrong chart accepted')
    cases = [((13637, 127, 572, 13654, 572, 740), Q(2), Q(-3)),
             ((13639, 572, 778, 13655, 709, 572), Q(1, 2), Q(3, 2)),
             ((13637, 731, 582, 13652, 740, 572), Q(-1), Q(2)),
             ((13651, 127, 572, 13654, 740, 572), Q(1), Q(1))]
    saw_bilinear = False
    for case, a, b in cases:
        d, A, B, e, f, h, g = coefficients(case, data, word)
        predicted = [row.copy() for row in data[4]]
        for out in range(word['public']):
            for vector, scale in ((e, d.get(out, 0)), (f, a * A.get(out, 0)),
                                  (h, b * B.get(out, 0)), (f, a * b * g * B.get(out, 0))):
                predicted[out] = add(predicted[out], vector, scale)
        actual = literal(word, case, a, b)
        need(actual == predicted, 'full all-column literal endpoint polynomial')
        saw_bilinear |= bool(g)
    need(saw_bilinear, 'nonzero bilinear production control')
    # The last literal control is also the z-only false positive.
    z = word['public']
    need(all(actual[o].get(z, 0) == 0 for o in outside), 'z-only false positive clears leak')
    need(any(actual[o] != data[4][o] for o in outside), 'arbitrary-X rejects z-only false positive')
    need(any(row.get(z, 0) for row in actual[:z]), 'false positive retains public z')
    return {'literal_full_column_cases': len(cases), 'z_only_false_positive': True,
            'consistent_system': True, 'forged_dual_rejected': True, 'bilinear_case': saw_bilinear,
            'synthetic_noncarrier_repair': True, 'wrong_seam_rejected': True}


def run(word):
    data = boundaries(word)
    prefix, suffix, banks, beta, baseline = data
    outside = {r for r, chart in enumerate(word['final']) if chart != word['final'][PIVOT]}
    digest = sha256()
    count = 0
    sizes = Counter()
    first = None
    for i in FIRST:
        for u in banks[i][595]:
            for v in banks[i][595]:
                if u == v:
                    continue
                for j in SECOND:
                    for s in banks[j][603]:
                        for r in banks[j][603]:
                            if s == r:
                                continue
                            case = (i, u, v, j, s, r)
                            parts = coefficients(case, data, word)
                            witness = contradiction(equations(parts, outside))
                            need(witness is not None, 'every declared case has an inconsistent linear relaxation')
                            d, A, B, e, f, h, g = parts
                            selected = []
                            for out, inp in witness:
                                need(out in outside and inp in set(e) | set(f) | set(h), 'protected equation label')
                                selected.append(((out, inp), [A.get(out, 0) * f.get(inp, 0),
                                                              B.get(out, 0) * h.get(inp, 0),
                                                              B.get(out, 0) * g * f.get(inp, 0)],
                                                 -d.get(out, 0) * e.get(inp, 0)))
                            check_dual(selected, witness)
                            record = {'case': list(case), 'dual': [[*label, str(q)] for label, q in sorted(witness.items())]}
                            digest.update((json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n').encode())
                            if first is None:
                                first = record
                            count += 1
                            sizes[len(witness)] += 1
    need(count == 4500, 'complete 15*30*(2+2+6) location-pair domain')
    return {'claim': 'Every declared two-ADD seam fails exact outside-V restoration, even with ab independent.',
            'cases': count, 'outside_public_roles': len(outside), 'V_chart': word['final'][PIVOT],
            'dual_size_counts': dict(sorted(sizes.items())), 'dual_sha256': digest.hexdigest(),
            'first_dual': first, 'controls': controls(word, data, outside)}


def main():
    manifest = json.loads((HERE / 'SOURCES.json').read_text())
    pin = next(p for p in manifest['files'] if p['path'] == WORD)
    raw = (HERE.parents[1] / WORD).read_bytes()
    need(sha256(raw).hexdigest() == pin['sha256'], 'authenticated selected word')
    word = json.loads(gzip.decompress(raw))
    result = run(word)
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        (HERE / 'RESULT.json').write_text(encoded)
    else:
        need(json.loads((HERE / 'RESULT.json').read_text()) == json.loads(encoded), 'exact result receipt')
    print(encoded, end='')
    print('PASS_P104_NONCARRIER_TWO_ADD_SEAM')


if __name__ == '__main__':
    main()
