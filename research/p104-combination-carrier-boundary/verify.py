#!/usr/bin/env python3
"""Exact retained-information test for PR6045's unit overwrite. Apache-2.0.

New certificate by apoursh with OpenAI Codex assistance. The imported class
census is Nick Petalas's unmodified PR6040 code, as retained by JosieElliston
in PR6045. The prefix/suffix interpreter and information test below are new.
"""
from collections import defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/p104-helper470-twin-rung-removal/WORD.json.gz'
WORD_SHA = '7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f'
CENSUS_SHA = '11e8ef691b28fb4f401a8c2e97b6d462e7a004f0e215a28579d6a654b4ca3304'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def authenticated(path, expected):
    data = path.read_bytes()
    need(sha256(data).hexdigest() == expected, 'source hash: ' + str(path))
    return data


def census_module():
    path = HERE / 'inputs/shapesplit.py'
    data = authenticated(path, CENSUS_SHA)
    module = types.ModuleType('pinned_pr6040_census')
    module.__file__ = str(path)
    # Execute authenticated source, never an unauthenticated pre-existing pyc.
    exec(compile(data, str(path), 'exec'), module.__dict__)
    return module


def add(dst, src, scale):
    for k, value in src.items():
        new = dst.get(k, 0) + scale * value
        if new:
            dst[k] = new
        else:
            dst.pop(k, None)


class State:
    """Sparse rows plus their transpose; mutations preserve both representations."""
    def __init__(self, word):
        self.n = word['public']
        self.rows = [{r: Q(1)} for r in range(self.n)]
        self.rows += [{} for _ in range(word['owned_fields'])]
        self.columns = [{r: Q(1)} for r in range(self.n)]
        self.chart = list(word['initial']) + [None] * word['owned_fields']

    def replace(self, r, row):
        for k in self.rows[r]:
            self.columns[k].pop(r)
        self.rows[r] = {k: value for k, value in row.items() if value}
        for k, value in self.rows[r].items():
            self.columns[k][r] = value

    def event(self, e):
        op, r = e[:2]
        need(0 <= r < len(self.rows), 'field index')
        if op == 'MOVE':
            need(self.chart[r] == e[2], 'MOVE chart')
            self.chart[r] = e[3]
        elif op == 'INIT':
            need(r >= self.n and self.chart[r] is None, 'INIT owned lifetime')
            self.replace(r, {})
            self.chart[r] = e[2]
        elif op == 'CLEAR':
            need(r >= self.n and self.chart[r] == e[2], 'CLEAR owned lifetime')
            self.replace(r, {})
            self.chart[r] = None
        elif op == 'SCALE':
            need(self.chart[r] == e[-1] and Q(e[-2]) != 0, 'SCALE chart/unit')
            self.replace(r, {k: Q(e[-2]) * a for k, a in self.rows[r].items()})
        elif op in ('COPY', 'ADD'):
            source = e[2]
            need(self.chart[r] is not None and self.chart[r] == self.chart[source] == e[-1], 'scalar chart')
            if op == 'COPY':
                need(r >= self.n and not self.rows[r], 'COPY into zero owned field')
                row = {}
            else:
                row = dict(self.rows[r])
            add(row, dict(self.rows[source]), Q(e[-2]))
            self.replace(r, row)
        else:
            raise ValueError('unknown scalar opcode: ' + op)

    def multiply(self, vector):
        result = {}
        for k, value in vector.items():
            add(result, self.columns[k], value)
        return result


def endpoint(word):
    state = State(word)
    for event in word['program']:
        state.event(event)
    need(state.chart[:state.n] == word['final'], 'final charts')
    expected = [{r: Q(1)} for r in range(state.n)]
    for x in word['live']:
        expected[x + 112][x] = Q(1)
    need(state.rows[:state.n] == expected, 'exact public shear endpoint')
    need(all(not r for r in state.rows[state.n:]), 'owned endpoint zero')
    need(all(c is None for c in state.chart[state.n:]), 'owned lifetimes closed')
    # M = I+H with disjoint X,Y banks, so H^2=0 and M^-1=I-H.
    need(not (set(word['live']) & {x + 112 for x in word['live']}), 'disjoint shear banks')
    return expected


def inverse_endpoint(word, vector):
    out = dict(vector)
    for x in word['live']:
        if x in vector:
            add(out, {x + 112: Q(1)}, -vector[x])
    return out


def reverse_event(columns, e):
    op, r = e[:2]
    if op in ('INIT', 'CLEAR'):
        columns[r] = {}
    elif op == 'COPY':
        add(columns[e[2]], columns[r], Q(e[-2]))
        columns[r] = {}
    elif op == 'ADD':
        add(columns[e[2]], dict(columns[r]), Q(e[-2]))
    elif op == 'SCALE':
        columns[r] = {k: Q(e[-2]) * a for k, a in columns[r].items()}
    else:
        need(op == 'MOVE', 'known reverse opcode')


def suffix_columns(word, classes):
    at = defaultdict(list)
    for c in classes:
        at[c['cut_after']].append(c)
    n = word['public']
    columns = [{r: Q(1)} for r in range(n)] + [{} for _ in range(word['owned_fields'])]
    out = {}
    for i in range(len(word['program']) - 1, -1, -1):
        for c in at.get(i, ()):
            p = c['pivot']
            d = dict(columns[p])
            outside = {r: value for r, value in d.items() if word['final'][r] != word['final'][p]}
            need(len(outside) == c['leak'] and bool(outside), 'independent suffix leak check')
            out[(i, p, c['frame'])] = d
        reverse_event(columns, word['program'][i])
    return out


def encoded(vector):
    return [[k, str(a)] for k, a in sorted(vector.items())]


def information_certificate(word, classes, suffix):
    at = defaultdict(list)
    for c in classes:
        at[c['cut_after']].append(c)
    state = State(word)
    certified, residual, transcript = [], [], []
    for i, event in enumerate(word['program']):
        state.event(event)
        for c in at.get(i, ()):
            p = c['pivot']
            key = (i, p, c['frame'])
            need(state.chart[p] == c['frame'], 'cut chart')
            d = suffix[key]
            v = inverse_endpoint(word, d)
            delta = state.multiply(v)
            add(delta, {p: Q(1)}, -1)
            transcript.append([list(key), encoded(v), encoded(delta)])
            if delta:
                residual.append({'key': list(key), 'residual': encoded(delta)})
            else:
                certified.append(list(key))
    return {
        'certified_information_loss': len(certified),
        'residual_cases': residual,
        'transcript_sha256': sha256(json.dumps(transcript, separators=(',', ':')).encode()).hexdigest(),
    }


def left_relations(rows, roles):
    """Complete left kernel: each dependency has a distinct new free role."""
    pivots, relations = {}, []
    for r in sorted(roles):
        row, coeff = dict(rows[r]), {r: Q(1)}
        while row:
            p = min(row)
            if p not in pivots:
                scale = row[p]
                pivots[p] = ({k: v / scale for k, v in row.items()},
                             {k: v / scale for k, v in coeff.items()})
                break
            basis, basis_coeff = pivots[p]
            scale = row[p]
            add(row, basis, -scale)
            add(coeff, basis_coeff, -scale)
        if not row:
            relations.append(coeff)
    return relations


def propagate(vector, event):
    op, r = event[:2]
    value = vector.get(r, 0)
    if op in ('INIT', 'CLEAR'):
        value = 0
    elif op == 'COPY':
        value = Q(event[-2]) * vector.get(event[2], 0)
    elif op == 'SCALE':
        value *= Q(event[-2])
    elif op == 'ADD':
        value += Q(event[-2]) * vector.get(event[2], 0)
    else:
        need(op == 'MOVE', 'known vector opcode')
    if value:
        vector[r] = value
    else:
        vector.pop(r, None)


def local_carriers(word, residual_cases):
    """All event charts until each residual vanishes, or a first witness exists."""
    starts = defaultdict(list)
    for case in residual_cases:
        key = tuple(case['key'])
        starts[key[0]].append((key, {r: Q(a) for r, a in case['residual']}))
    state = State(word)
    banks = defaultdict(set)
    for r, chart in enumerate(state.chart):
        if chart is not None:
            banks[chart].add(r)
    active, cache, found, vanished = {}, {}, [], []
    tests = kernel_computations = 0
    for t, event in enumerate(word['program']):
        r = event[1]
        old_chart = state.chart[r]
        state.event(event)
        chart = state.chart[r]
        touched = {old_chart, chart} - {None}
        if old_chart is not None:
            banks[old_chart].discard(r)
        if chart is not None:
            banks[chart].add(r)
        for f in touched:
            cache.pop(f, None)
        for key, delta in list(active.items()):
            propagate(delta, event)
            if not delta:
                vanished.append({'key': list(key), 'event': t})
                del active[key]
        for key, delta in starts.get(t, ()):
            active[key] = dict(delta)
        for key, delta in list(active.items()):
            need(all(state.chart[f] is not None for f in delta), 'no inactive residual field')
            charts = {state.chart[f] for f in delta}
            if key[0] != t:
                charts &= touched
            hit = False
            for f in sorted(charts):
                tests += 1
                if f not in cache:
                    cache[f] = left_relations(state.rows, banks[f])
                    kernel_computations += 1
                for coeff in cache[f]:
                    pairing = sum(a * delta[k] for k, a in coeff.items() if k in delta)
                    if not pairing:
                        continue
                    row = {}
                    for k, a in coeff.items():
                        add(row, state.rows[k], a)
                    need(not row, 'literal original combination vanishes')
                    need(all(state.chart[k] == f for k in coeff), 'carrier sources colocated')
                    found.append({'key': list(key), 'event': t, 'chart': f,
                                  'combination': encoded(coeff),
                                  'beta_coefficient': str(-pairing)})
                    del active[key]
                    hit = True
                    break
                if hit:
                    break
    need(not active, 'every residual classified before program end')
    need(len(found) + len(vanished) == len(residual_cases), 'complete residual partition')
    return {'carrier_classes': sorted(found, key=lambda c: c['key']),
            'no_carrier_residual_classes': sorted(vanished, key=lambda c: c['key']),
            'chart_checks': tests, 'kernel_computations': kernel_computations}


def dynamic_repair_obstruction(word, found):
    """Finite invariant certificate for arbitrary finite carrier-only programs.

    The allowed extra operation is the atomic chart-local update
    beta <- beta + q e_r (a beta), where a R_t = 0. It preserves the
    unmodified prefix rows R_t; it does not cover other inserted operations.
    """
    need([c['key'] for c in found] == [[13637, 572, 595], [13639, 572, 595]],
         'dynamic certificate applies to the two carrier classes')
    first, last, chart, temporary = 13637, 13656, 595, 778
    chosen = [127, 572, 581, 582, 731]
    outside_rows = [127, 120, 116, 176, 134]
    need(all(word['final'][r] != word['final'][572] for r in outside_rows),
         'dynamic minor rows lie outside the pivot final chart')
    state, snapshots = State(word), {}
    unit = {temporary: Q(1)}
    for t, event in enumerate(word['program']):
        state.event(event)
        if first <= t <= last:
            roles = [r for r, f in enumerate(state.chart) if f == chart]
            relations = left_relations(state.rows, roles)
            if t < 13652:
                need(roles == chosen + [temporary], 'complete dynamic carrier bank')
                need(relations == [{temporary: Q(1), 572: Q(-1)}],
                     'unique retained-copy relation in every active window')
            elif t < last:
                need(temporary in roles and not relations,
                     'no carrier after pivot departure and before CLEAR')
            else:
                need(state.chart[temporary] is None, 'temporary cleared')
            snapshots[t] = {'rows': [dict(row) for row in state.rows], 'roles': roles}
        if first < t <= last:
            propagate(unit, event)
            need(unit == ({temporary: Q(1)} if t < last else {}),
                 'original events retain residual line, then erase it')
        if t == last:
            break
    need(word['program'][last] == ['CLEAR', temporary, chart],
         'final residual erasure event')
    n = word['public']
    columns = [{r: Q(1)} for r in range(n)] + [{} for _ in range(word['owned_fields'])]
    for t in range(len(word['program']) - 1, first - 1, -1):
        if t in snapshots:
            snapshots[t]['suffix'] = {r: dict(columns[r]) for r in snapshots[t]['roles']}
        reverse_event(columns, word['program'][t])
    basis = [snapshots[first]['suffix'][r] for r in chosen]
    minor = [[column.get(r, Q(0)) for column in basis] for r in outside_rows]
    need(all(minor[i][j] == 0 for i in range(5) for j in range(i)),
         'fixed outside minor is upper triangular')
    need([minor[i][i] for i in range(5)] == [1, -1, 1, -1, -2],
         'fixed outside minor has determinant -2')

    def in_fixed_span(column):
        coefficients = [Q(0)] * 5
        for i in range(4, -1, -1):
            coefficients[i] = (column.get(outside_rows[i], Q(0)) -
                               sum(minor[i][j] * coefficients[j] for j in range(i + 1, 5))) / minor[i][i]
        residual = dict(column)
        for vector, coefficient in zip(basis, coefficients):
            add(residual, vector, -coefficient)
        need(not residual, 'full public suffix column belongs to fixed span W')

    checks = 0
    for t in range(first, 13652):
        snapshot = snapshots[t]
        for r, column in snapshot['suffix'].items():
            in_fixed_span(column)
            v = inverse_endpoint(word, column)
            residual = {f: value for f, row in enumerate(snapshot['rows'])
                        if (value := sum(a * v[k] for k, a in row.items() if k in v) - (f == r))}
            need(set(residual) <= {temporary},
                 'every chart-local control preserves the residual line')
            checks += 1
    for cut in (13637, 13639):
        snapshot = snapshots[cut]
        column = snapshot['suffix'][572]
        in_fixed_span(column)
        v = inverse_endpoint(word, column)
        residual = {f: value for f, row in enumerate(snapshot['rows'])
                    if (value := sum(a * v[k] for k, a in row.items() if k in v) - (f == 572))}
        need(residual == {temporary: Q(1)}, 'initial delta is minus retained-copy unit')
    return {'cuts': [13637, 13639], 'chart': chart, 'residual_field': temporary,
            'active_windows': [first, 13651], 'active_window_count': 15,
            'target_projection_and_span_checks': checks,
            'no_carrier_windows': [13652, 13655], 'clear_event': last,
            'fixed_span_columns': chosen, 'outside_rows': outside_rows,
            'outside_minor': [[str(a) for a in row] for row in minor],
            'determinant': '-2', 'fixed_span_dimension': 5}


def control_checks():
    path = HERE / 'controls.py'
    module = types.ModuleType('local_controls')
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    receipt = module.run_controls()
    kernel_cases = 0
    for m, n, alphabet in ((2, 1, (-1, 0, 1)), (2, 2, (-1, 0, 1)), (3, 2, (0, 1))):
        for matrix in module.matrices(m, n, alphabet):
            rows = [{j: Q(a) for j, a in enumerate(row) if a} for row in matrix]
            relations = left_relations(rows, range(m))
            need(len(relations) == m - module.rank(matrix), 'kernel nullity vs independent oracle')
            relation_matrix = [[c.get(j, 0) for j in range(m)] for c in relations]
            need(module.rank(relation_matrix) == len(relations), 'kernel independence')
            for coeff in relations:
                row = {}
                for r, a in coeff.items():
                    add(row, rows[r], a)
                need(not row, 'kernel equation')
            kernel_cases += 1
    small = {'public': 2, 'owned_fields': 1, 'initial': [0, 0]}
    state = State(small)
    events = [('INIT', 2, 0), ('COPY', 2, 0, '1', 0),
              ('ADD', 1, 2, '-2', 0), ('SCALE', 0, '1/2', 0),
              ('MOVE', 2, 0, 1), ('CLEAR', 2, 1)]
    vectors = [{0: Q(1)}, {1: Q(1)}, {0: Q(-2), 1: Q(3)}]
    for event in events:
        state.event(event)
        for vector in vectors:
            direct = {r: a for r, row in enumerate(state.rows)
                      if (a := sum(v * vector.get(k, 0) for k, v in row.items()))}
            need(state.multiply(vector) == direct, 'sparse transpose agrees with literal rows')
    need(state.rows == [{0: Q(1, 2)}, {0: Q(-2), 1: Q(1)}, {}], 'literal opcode control endpoint')
    need(inverse_endpoint({'live': [0]}, {0: Q(2), 112: Q(3)}) == {0: Q(2), 112: Q(1)},
         'production endpoint inverse retains the shear correction')
    columns = [{0: Q(1)}, {1: Q(1)}, {}]
    for event in reversed(events):
        reverse_event(columns, event)
    need(columns[:2] == [{0: Q(1, 2), 1: Q(-2)}, {1: Q(1)}], 'suffix transpose opcode control')
    for vector in vectors:
        value = dict(vector)
        for event in events:
            propagate(value, event)
        need(value == state.multiply(vector), 'vector propagation agrees with complete prefix')
    rows = [{0: Q(1)}, {1: Q(1)}, {0: Q(1)}]
    relations = left_relations(rows, range(3))
    need(any(c.get(0) for c in relations), 'duplicate-pivot carrier must be detected')
    wrong = {0: Q(1), 2: Q(1)}
    row = {}
    for r, a in wrong.items():
        add(row, rows[r], a)
    need(bool(row), 'wrong-sign carrier must reject')
    receipt['production_kernel_oracle_cases'] = kernel_cases
    receipt['production_interpreter_vectors'] = len(events) * len(vectors)
    return receipt


def main():
    word = json.loads(gzip.decompress(authenticated(ROOT / WORD, WORD_SHA)))
    need((word['public'], word['owned_fields'], len(word['program'])) == (770, 29, 22803), 'selected word dimensions')
    endpoint(word)
    census = census_module()
    counts, all_classes = census.census(word, 'empty')
    expected_counts = {'evaluations': 8734, 'kind_leak': 4033, 'kind_pairing': 4,
                       'no_helper_prefix': 6275, 'pivots': 516, 'witnesses': 0}
    need(counts == expected_counts, 'retained class census')
    classes = [c for c in all_classes if c['kind'] == 'leak']
    suffix = suffix_columns(word, classes)
    need(len(suffix) == len(classes), 'distinct class keys')
    result = information_certificate(word, classes, suffix)
    need(result['certified_information_loss'] == 4009 and len(result['residual_cases']) == 24, 'information boundary counts')
    need(result['transcript_sha256'] == 'd4a1ba5ddfc72cdc34425f3849b2a00128fad3833ef8c6ab04a905181c8e748c',
         'full information certificate transcript')
    result['class_counts'] = counts
    result['local_carriers'] = local_carriers(word, result['residual_cases'])
    need(len(result['local_carriers']['carrier_classes']) == 2, 'two carrier classes')
    need(len(result['local_carriers']['no_carrier_residual_classes']) == 22, 'twenty-two carrier exclusions')
    result['dynamic_repair_obstruction'] = dynamic_repair_obstruction(word, result['local_carriers']['carrier_classes'])
    result['controls'] = control_checks()
    print(json.dumps(result, indent=2, sort_keys=True))
    print('PASS_P104_COMBINATION_CARRIER_BOUNDARY')


if __name__ == '__main__':
    main()
