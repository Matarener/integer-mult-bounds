#!/usr/bin/env python3
"""Independent finite controls for the parent's exact quadratic-chart model.

This is a model audit, not selected-native admission or an optimization run.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as F
from functools import lru_cache
import argparse, hashlib, importlib.util, json, sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent / 'root-chronology'
SOURCE = ROOT / 'quadratic_charts.py'
spec = importlib.util.spec_from_file_location('caller_quadratic_reviewed_model', SOURCE)
qc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = qc
spec.loader.exec_module(qc)

def need(ok, message):
    if not ok:
        raise ValueError(message)

def lin(rows, x):
    return sum(((row & x).bit_count() & 1) << i for i, row in enumerate(rows))

@lru_cache(None)
def inverse_rows(rows):
    # Deliberately use complete truth-table inversion, not the reviewed eliminator.
    n = len(rows)
    values = {lin(rows, x): x for x in range(1 << n)}
    need(len(values) == 1 << n, 'independent address inverse exists')
    return tuple(sum(((values[1 << j] >> i) & 1) << j for j in range(n)) for i in range(n))

def literal_x_action(circuit, n, x):
    """Act on an X-character using literal P, C, even-linear D and unit events."""
    phase = 0
    for e in circuit:
        kind = e[0]
        if kind == 'P':
            # Physical |x> -> |A x> gives character address A^{-T}.
            inv = inverse_rows(tuple(e[1]))
            rows = tuple(sum(((inv[j] >> i) & 1) << j for j in range(n)) for i in range(n))
            x = lin(rows, x)
        elif kind == 'C':
            phase += e[2] * ((e[1] & x).bit_count() & 1)
        elif kind == 'D':
            need(not any(e[1]) and all(a % 2 == 0 for a in e[2]), 'source D is an explicit Pauli Z')
            x ^= sum(((a // 2) & 1) << i for i, a in enumerate(e[2]))
        elif kind == 'phase':
            phase += e[1]
        else:
            raise ValueError('uncovered source circuit event ' + kind)
    return x, phase % 4

def check_source_families():
    path = ROOT / 'ENCODED-COMPLETE-Q3.json'
    src = json.loads(path.read_text())
    n = src['ambient_arity']
    points = [0] + [1 << i for i in range(n)] + [(1 << i) | (1 << j) for i in range(n) for j in range(i + 1, n)]
    # Also use high-weight points to detect a mistaken nonquadratic implementation.
    points += [(1 << n) - 1, int('10' * (n // 2), 2), int('01' * (n // 2), 2)]
    count = 0
    wrong_global_witness = None
    for index, e in enumerate(src['events']):
        if e['kind'] in ('ADD', 'BANK_SWAP', 'SCALE'):
            continue
        g = qc.decode(e, n)
        op = e.get('exact_operator', e.get('operator'))
        circuit = op.get('one_coordinate_literal_circuit', op.get('one_bit_circuit'))
        need(circuit is not None, 'every source unary has a complete literal circuit')
        if 'global_i_exponent_by_f_mod4' in op:
            globals_ = tuple(op['global_i_exponent_by_f_mod4'])
        else:
            sign = 2 if op['global_sign'] == -1 else 0
            exponent = op['phase_exponent']
            globals_ = tuple((sign + exponent * (1 - r)) % 4 for r in range(4))
        base0, phase0 = literal_x_action(circuit, n, 0)
        for x in points:
            y, phase = literal_x_action(circuit, n, x)
            need(y == g.act(x), 'source-family exact X-character address')
            # One nonzero coordinate and f-1 zero coordinates suffice once the
            # bitwise tensor construction and Gaussian phase polynomial are fixed.
            for f in (1, 2, 3, 4):
                expected = (globals_[f % 4] + phase + (f - 1) * phase0) % 4
                actual = (g.global_phase + g.q(x) + (f - 1) * g.q(0)) % 4
                need(actual == expected, 'source-family all-f phase normalization')
                if wrong_global_witness is None and f == 2 and g.global_phase % 2:
                    wrong_global_witness = {'event_index': index, 'f': f, 'correct_phase': actual,
                                            'tensoring_the_global_i_phase': (f * g.global_phase + g.q(x) + (f - 1) * g.q(0)) % 4}
        count += 1
    need(wrong_global_witness is not None and wrong_global_witness['correct_phase'] != wrong_global_witness['tensoring_the_global_i_phase'],
         'negative control detects tensoring a once-per-bank phase')
    return {'unary_events': count, 'points_per_event': len(points), 'f_residues': [1, 2, 3, 4],
            'global_phase_negative_control': wrong_global_witness,
            'source_path': str(path), 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}

def symmetric(n, bits):
    rows = [0] * n
    k = 0
    for i in range(n):
        for j in range(i, n):
            if bits >> k & 1:
                rows[i] ^= 1 << j
                if i != j:
                    rows[j] ^= 1 << i
            k += 1
    return tuple(rows)

def walsh_entry_numerator(g, row, column):
    re = im = 0
    for x in range(1 << len(g.rows)):
        p = (g.q(x) + 2 * (((row & g.act(x)).bit_count() + (column & x).bit_count()) & 1)) % 4
        a, b = ((1, 0), (0, 1), (-1, 0), (0, -1))[p]
        re += a
        im += b
    return re, im

def finite_core_controls():
    # Exhaust all 64 symmetric polar forms on three bits. Affine addresses and
    # even linear phases are deliberately present, not just diagonal charts.
    n = 3
    perm = (3, 2, 4)  # invertible transvection
    forms = []
    for bits in range(64):
        A = symmetric(n, bits)
        base = qc.chart(A)
        g = qc.Mono(perm, bits % 8, tuple((a + 2 * ((bits >> i) & 1)) % 4 for i, a in enumerate(base.alpha)), base.quad,
                    bits % 4, (bits // 4) % 4)
        r = qc.rank(g.polar())
        for row in range(1 << n):
            values = [walsh_entry_numerator(g, row, col) for col in range(1 << n)]
            support = [a * a + b * b for a, b in values if a or b]
            need(len(support) == 1 << r, 'complete Walsh row support equals 2^polar_rank')
            need(len(set(support)) == 1 and support[0] == 1 << (2 * n - r), 'complete Walsh magnitude matches native rank')
        forms.append(g)
    composition_checks = 0
    transport_checks = 0
    for j, g in enumerate(forms):
        h = forms[(17 * j + 9) % len(forms)]
        c = g @ h
        inv = g.inv()
        need(g @ inv == inv @ g == qc.identity(n), 'exact inverse preserves the once-only phase')
        for x in range(1 << n):
            need(c.act(x) == g.act(h.act(x)) and c.q(x) == (h.q(x) + g.q(h.act(x))) % 4,
                 'complete phase/address composition')
            need(c.global_phase == (g.global_phase + h.global_phase) % 4, 'once-only phase composition')
            composition_checks += 1
        A = symmetric(n, (13 * j + 1) % 64)
        B = qc.move(g, A)
        need(all((B[i] >> k & 1) == (B[k] >> i & 1) for i in range(n) for k in range(n)), 'transport chart remains symmetric')
        adapter = qc.chart(B).inv() @ g @ qc.chart(A)
        need(not any(adapter.polar()), 'transport adapter has zero polar matrix')
        for x in range(1 << n):
            left, right = g @ qc.chart(A), qc.chart(B) @ adapter
            need((left.act(x), left.q(x), left.global_phase) == (right.act(x), right.q(x), right.global_phase),
                 'literal transport including linear, affine and global phase')
            transport_checks += 1
    # A rank-zero affine/quadratic adapter must be a computational monomial.
    # Conversely a nonzero polar fixture must not be mislabeled native-zero.
    need(qc.rank(qc.chart((1, 0, 0)).polar()) == 1, 'negative control odd linear phase is paid')
    return {'complete_polar_forms': 64, 'complete_Walsh_rows': 64 * 8,
            'complete_composition_points': composition_checks, 'complete_transport_points': transport_checks}

UNITS = ((F(1), F(0)), (F(0), F(1)), (F(-1), F(0)), (F(0), F(-1)))
def plus(a, b):
    return a[0] + b[0], a[1] + b[1]
def scale(c, a):
    return c * a[0], c * a[1]
def unit(p, a):
    return (a, (-a[1], a[0]), (-a[0], -a[1]), (a[1], -a[0]))[p % 4]

def independently_act(events, banks, n, f, column):
    # Direct sparse vector execution, not the parent's operator-entry dictionary.
    state = {column: (F(1), F(0))}
    mask = (1 << n) - 1
    for e in events:
        if e['kind'] == 'ADD':
            d, s, c = e['dst'], e['src'], F(e['coefficient'])
            nxt = dict(state)
            for (bank, x), value in state.items():
                if bank == s:
                    key = d, x
                    nxt[key] = plus(nxt.get(key, (F(0), F(0))), scale(c, value))
            state = {key: val for key, val in nxt.items() if val != (0, 0)}
        elif e['kind'] == 'SCALE':
            c = F(e['coefficient'])
            need(c != 0, 'independent invertible bank scaling')
            state = {key: scale(c, val) if key[0] == e['bank'] else val for key, val in state.items()}
        elif e['kind'] == 'BANK_SWAP':
            a, b = e['banks']
            state = {(b if bank == a else a if bank == b else bank, x): val for (bank, x), val in state.items()}
        else:
            g = qc.decode(e, n)
            nxt = {}
            for (bank, x), val in state.items():
                if bank != e['bank']:
                    nxt[bank, x] = val
                    continue
                y = p = 0
                for t in range(f):
                    z = (x >> (n * t)) & mask
                    y |= g.act(z) << (n * t)
                    p += g.q(z)
                nxt[bank, y] = unit(p + g.global_phase, val)
            state = nxt
    return state

def compile_controls():
    n, banks = 3, 3
    fixtures = [qc.chart(symmetric(n, z)) for z in (13, 41, 55)]
    g = qc.Mono((3, 2, 4), 5, (3, 1, 2), (6, 4, 0), 1, 3)
    def unary(i, op):
        return {'kind': 'NATIVE', 'bank': i, 'x_monomial': op.data()}
    events = [unary(0, g), {'kind': 'SCALE', 'bank': 0, 'coefficient': '-2'},
              {'kind': 'ADD', 'dst': 1, 'src': 0, 'coefficient': '-2'}, unary(2, g.inv()),
              {'kind': 'BANK_SWAP', 'banks': [1, 2]}, {'kind': 'ADD', 'dst': 0, 'src': 2, 'coefficient': '1/2'},
              unary(1, fixtures[0]), {'kind': 'SCALE', 'bank': 1, 'coefficient': '1/2'},
              {'kind': 'ADD', 'dst': 1, 'src': 0, 'coefficient': '-1'}, unary(0, fixtures[1])]
    choices = [symmetric(n, z) for z in (7, 38, 63)]
    compiled = qc.compile_word(events, banks, n, choices)
    need(qc.replay(events, banks, n) == qc.replay(compiled, banks, n), 'parent all-f replay preserves all bank columns')
    checks = 0
    for f in (1, 2):
        for bank in range(banks):
            for x in range(1 << (n * f)):
                need(independently_act(events, banks, n, f, (bank, x)) == independently_act(compiled, banks, n, f, (bank, x)),
                     'independent complete input-column vector replay')
                checks += 1
    # A deliberately unaligned ADD is a defect, even though the source and
    # destination use individually valid chart gauges.
    mutant = list(compiled)
    alignment = next(i for i, e in enumerate(mutant) if e.get('label') == 'paid quadratic chart alignment')
    del mutant[alignment]
    need(any(independently_act(events, banks, n, 1, (b, x)) != independently_act(mutant, banks, n, 1, (b, x))
             for b in range(banks) for x in range(1 << n)), 'negative control rejects missing ADD alignment')
    return {'toy_banks': banks, 'one_coordinate_arity': n, 'complete_input_columns_f1_f2': checks,
            'compiled_native_rank_mass': sum(e.get('rank_per_f', 0) for e in compiled),
            'SCALE_scans_checked': 2, 'missing_alignment_negative_control': 'REJECTED'}

def produce():
    initial = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    out = {'status': 'PASS_SCOPED_INDEPENDENT_QUADRATIC_CHART_MODEL_REVIEW',
           'source_path': str(SOURCE), 'source_sha256': initial,
           'source_family_binding': check_source_families(),
           'finite_core_controls': finite_core_controls(), 'compile_controls': compile_controls(),
           'scope': ['Exact model and phase review; no bounded-search optimality claim.',
                     'For these X-character monomial tensor families, polar rank is exactly the physical Clifford B rank per coordinate.',
                     'The exact all-f closure is an algebraic tensor/phase argument; finite matrix tests are defect controls.',
                     'Every nonzero rank child still needs selected-native lowering, all-f adapters and contraction-cap splitting before supplier admission.',
                     'No source-read, precision, owner, COPY, finite-tape or joint BIT contract is supplied.'],
           'no_new_kappa': True}
    need(initial == hashlib.sha256(SOURCE.read_bytes()).hexdigest(), 'reviewed source stable during controls')
    out['producer_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return out

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = produce()
    path = HERE / 'QUADRATIC-MODEL-REVIEW.json'
    if args.write:
        path.write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == out, 'saved scoped model review differs')
    print(out['status'])

if __name__ == '__main__':
    main()
