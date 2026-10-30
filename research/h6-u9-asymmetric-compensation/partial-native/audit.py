#!/usr/bin/env python3
"""Local finite exact-phase audit of the two frozen asymmetric H6 U9 banks.

The inherited lowerer emits recipes. Independent raw-field Gaussian-dyadic
and signed-Pauli interpreters below check those serialized recipes. Nothing
is written to the source checkout or the frozen construction directory.
"""
from pathlib import Path
from functools import lru_cache
from collections import Counter
import copy
import hashlib
import importlib.util
import json
import sys
import time

sys.dont_write_bytecode = True
import numpy as np

HERE = Path(__file__).resolve().parent
RUN = HERE.parent
INPUT = RUN / 'bulk-partial'
ROOT = Path('/Users/ross/git/math/integer-mult-bounds')
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
N = 17
SIZE = 1 << N


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


pc = load_module('partial_native_compiler', ROOT / 'research/h6-compensation-network/physical_compiler/compile.py')
ce = pc.ce
literal_zero_state = ce.Op.zero_state


def bitpar(x):
    return int(x).bit_count() % 2


def matvec(rows, value):
    result = 0
    for bit, row in enumerate(rows):
        if bitpar(row & value):
            result |= 1 << bit
    return result


def inverse_rows(rows):
    n = len(rows)
    left = list(map(int, rows))
    right = [1 << i for i in range(n)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if left[i] & (1 << col)), None)
        need(pivot is not None, 'singular serialized address matrix')
        left[col], left[pivot] = left[pivot], left[col]
        right[col], right[pivot] = right[pivot], right[col]
        for row in range(n):
            if row != col and left[row] & (1 << col):
                left[row] ^= left[col]
                right[row] ^= right[col]
    need(left == [1 << i for i in range(n)], 'address inverse did not reduce to identity')
    return tuple(right)


def transposed(rows):
    n = len(rows)
    return tuple(sum(((rows[j] >> i) & 1) << j for j in range(n)) for i in range(n))


def binary_rank(vectors):
    pivots = {}
    for value in map(int, vectors):
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def pauli_product(a, b):
    x, z, p = a
    y, w, q = b
    return x ^ y, z ^ w, (p + q + 2 * bitpar(z & y)) % 4


def apply_tableau(tableau, value):
    x, z, phase = value
    n = len(tableau) // 2
    out = (0, 0, phase)
    for i in range(n):
        if x & (1 << i):
            out = pauli_product(out, tableau[i])
    for i in range(n):
        if z & (1 << i):
            out = pauli_product(out, tableau[n + i])
    return out


def identity_tableau(n):
    return tuple([(1 << i, 0, 0) for i in range(n)] + [(0, 1 << i, 0) for i in range(n)])


def monomial_tableau(rec, n):
    rows = tuple(rec['matrix_rows'])
    qrows = tuple(rec['quadratic_rows'])
    alpha = tuple(rec['linear_Z4'])
    b = rec['offset']
    need(len(rows) == len(qrows) == len(alpha) == n, 'monomial field length')
    need(all(0 <= x < (1 << n) for x in rows + qrows), 'serialized row range')
    need(0 <= b < (1 << n) and 0 <= rec['phase'] < 4, 'serialized offset/phase range')
    need(transposed(qrows) == qrows, 'phase matrix must be symmetric')
    need(all(0 <= a < 4 and a % 2 == ((qrows[i] >> i) & 1) for i, a in enumerate(alpha)), 'quadratic diagonal parity')
    gi_t = transposed(inverse_rows(rows))
    gcols = transposed(rows)
    out = []
    for i in range(n):
        z = matvec(gi_t, qrows[i])
        out.append((gcols[i], z, (alpha[i] + 2 * bitpar(b & z)) % 4))
    for i in range(n):
        z = matvec(gi_t, 1 << i)
        out.append((0, z, 2 * bitpar(b & z)))
    return tuple(out)


def primitive_tableau(gate, n):
    kind = gate[0]
    if kind == 'P':
        rec = dict(matrix_rows=gate[1], offset=0, quadratic_rows=[0] * n, linear_Z4=[0] * n, phase=0)
        return monomial_tableau(rec, n)
    if kind == 'D':
        rec = dict(matrix_rows=[1 << i for i in range(n)], offset=0, quadratic_rows=gate[1], linear_Z4=gate[2], phase=0)
        return monomial_tableau(rec, n)
    if kind == 'X':
        return tuple([(1 << i, 0, 0) for i in range(n)] + [(0, 1 << i, 2 * ((gate[1] >> i) & 1)) for i in range(n)])
    if kind == 'C':
        value, sign = gate[1:]
        return tuple([(1 << i, 0, 0) for i in range(n)] + [(value if value & (1 << i) else 0, 1 << i, (3 * sign) % 4 if value & (1 << i) else 0) for i in range(n)])
    if kind == 'phase':
        return identity_tableau(n)
    raise ValueError(('unknown primitive', gate))


def circuit_tableau(circuit, n):
    out = identity_tableau(n)
    for gate in circuit:
        tab = primitive_tableau(gate, n)
        out = tuple(apply_tableau(tab, p) for p in out)
    return out


def recipe_tableau(rec, n):
    if rec['rank'] == 0:
        return monomial_tableau(rec['left'], n)
    right = monomial_tableau(rec['right'], n)
    left = monomial_tableau(rec['left'], n)
    out = right
    for bit in range(rec['rank']):
        child = primitive_tableau(('C', 1 << bit, 1), n)
        out = tuple(apply_tableau(child, p) for p in out)
    return tuple(apply_tableau(left, p) for p in out)


@lru_cache(maxsize=8)
def addresses(n):
    return np.arange(1 << n, dtype=np.int64)


@lru_cache(maxsize=32)
def affine_map(rows, offset):
    n = len(rows)
    xs = addresses(n)
    out = np.zeros(1 << n, dtype=np.int64)
    for i, row in enumerate(rows):
        parity = np.zeros(1 << n, dtype=np.int64)
        for j in range(n):
            if row & (1 << j):
                parity ^= (xs >> j) & 1
        out |= parity << i
    return out ^ offset


@lru_cache(maxsize=32)
def phase_values(qrows, alpha, phase):
    n = len(alpha)
    xs = addresses(n)
    out = np.full(1 << n, phase, dtype=np.int64)
    for i in range(n):
        xi = (xs >> i) & 1
        out += alpha[i] * xi
        for j in range(i + 1, n):
            if qrows[i] & (1 << j):
                out += 2 * xi * ((xs >> j) & 1)
    return out % 4


def apply_phase(re, im, phase):
    # Branch masks implement the four Gaussian units without float or complex.
    out_re = np.empty_like(re)
    out_im = np.empty_like(im)
    for p in range(4):
        mask = phase == p
        if p == 0:
            out_re[mask], out_im[mask] = re[mask], im[mask]
        elif p == 1:
            out_re[mask], out_im[mask] = -im[mask], re[mask]
        elif p == 2:
            out_re[mask], out_im[mask] = -re[mask], -im[mask]
        else:
            out_re[mask], out_im[mask] = im[mask], -re[mask]
    return out_re, out_im


def reduce_state(re, im, denominator):
    while denominator > 0 and not np.any((re | im) & 1):
        re = re // 2
        im = im // 2
        denominator -= 1
    return re, im, denominator


def act_monomial(re, im, rec):
    phase = phase_values(tuple(rec['quadratic_rows']), tuple(rec['linear_Z4']), int(rec['phase']))
    re, im = apply_phase(re, im, phase)
    target = affine_map(tuple(rec['matrix_rows']), int(rec['offset']))
    out_re, out_im = np.empty_like(re), np.empty_like(im)
    out_re[target] = re
    out_im[target] = im
    return out_re, out_im


def act_c(re, im, denominator, value, sign):
    need(max(int(np.abs(re).max()), int(np.abs(im).max())) < 2 ** 59, 'exact-state integer overflow guard')
    source = addresses((len(re) - 1).bit_length()) ^ value
    ar, ai = re[source], im[source]
    # ((I+X) + sign*i*(I-X))/2, with all old arrays read first.
    nr = re + ar - sign * (im - ai)
    ni = im + ai + sign * (re - ar)
    return reduce_state(nr, ni, denominator + 1)


def initial_state(n, basis=0):
    re = np.zeros(1 << n, dtype=np.int64)
    im = np.zeros_like(re)
    re[basis] = 1
    return re, im, 0


def raw_state(circuit, n, basis=0):
    re, im, d = initial_state(n, basis)
    for gate in circuit:
        kind = gate[0]
        if kind == 'C':
            re, im, d = act_c(re, im, d, gate[1], gate[2])
        elif kind == 'P':
            target = affine_map(tuple(gate[1]), 0)
            nr, ni = np.empty_like(re), np.empty_like(im)
            nr[target], ni[target] = re, im
            re, im = nr, ni
        elif kind == 'X':
            source = addresses(n) ^ gate[1]
            re, im = re[source], im[source]
        elif kind == 'D':
            re, im = apply_phase(re, im, phase_values(tuple(gate[1]), tuple(gate[2]), 0))
        elif kind == 'phase':
            re, im = apply_phase(re, im, np.full(1 << n, gate[1] % 4, dtype=np.int64))
        else:
            raise ValueError(('unknown literal gate', gate))
    return reduce_state(re, im, d)


def recipe_state(rec, n, basis=0):
    re, im, d = initial_state(n, basis)
    if rec['rank']:
        re, im = act_monomial(re, im, rec['right'])
        for bit in range(rec['rank']):
            re, im, d = act_c(re, im, d, 1 << bit, 1)
    re, im = act_monomial(re, im, rec['left'])
    return reduce_state(re, im, d)


def states_equal(a, b):
    return a[2] == b[2] and np.array_equal(a[0], b[0]) and np.array_equal(a[1], b[1])


def state_receipt(state):
    re, im, d = state
    digest = hashlib.sha256()
    digest.update(int(d).to_bytes(4, 'little'))
    digest.update(re.astype('<i8', copy=False).tobytes())
    digest.update(im.astype('<i8', copy=False).tobytes())
    return dict(denominator_exponent=d, nonzero_complex_coordinates=int(np.count_nonzero(re | im)), sha256=digest.hexdigest())


def counts(rec):
    result = Counter()
    for side in ('right', 'left'):
        m = rec[side]
        if m is None:
            continue
        q = sum((row >> (i + 1)).bit_count() for i, row in enumerate(m['quadratic_rows']))
        linear = sum(a % 4 != 0 for a in m['linear_Z4'])
        global_phase = int(m['phase'] % 4 != 0)
        moved = tuple(m['matrix_rows']) != tuple(1 << i for i in range(N)) or m['offset'] != 0
        result.update(quadratic_factors=q, linear_factors=linear, global_phase_factors=global_phase,
                      unit_phase_factors=q + linear + global_phase, affine_address_passes=int(moved),
                      nontrivial_fused_phase_passes=int(q + linear + global_phase != 0))
    return dict(result)


def check_recipe(rec, expected, n=N):
    tab = recipe_tableau(rec, n)
    raw_tab = circuit_tableau(expected.circuit, n)
    need(tab == raw_tab == expected.tab, f'{rec.get("name", "recipe")}: signed generator mismatch')
    need(binary_rank(x for x, z, p in tab[n:]) == rec['rank'], 'native Fourier child rank mismatch')
    for side in ('left', 'right'):
        if rec[side] is not None:
            mt = monomial_tableau(rec[side], n)
            need(all(x == 0 for x, z, p in mt[n:]), 'nonmonomial serialized adapter')
    a, b = recipe_state(rec, n), raw_state(expected.circuit, n)
    need(states_equal(a, b), f'{rec.get("name", "recipe")}: complete exact phase witness mismatch')
    return state_receipt(a)


def crosscheck_interpreters():
    checks = 0
    for n in (2, 3, 4, 5):
        rows = ce.transpose(ce.basis_extend((3,), n), n)
        q = tuple((1 << i) ^ ((1 << (i + 1)) if i + 1 < n else 0) ^ ((1 << (i - 1)) if i else 0) for i in range(n))
        alpha = tuple(1 + 2 * (i % 2) for i in range(n))
        word = ce.perm(n, rows).then(ce.diag(n, q, alpha)).then(ce.cgate(n, 3)).then(
            ce.fourier(n)).then(ce.xgate(n, 1)).then(ce.Op(n, ce.identity(n), [('phase', 3)]))
        for op in (word, word.adjoint()):
            need(circuit_tableau(op.circuit, n) == op.tab, 'independent primitive signed interpreter disagreement')
            for basis in range(1 << n):
                re, im, d = raw_state(op.circuit, n, basis)
                literal, ld = literal_zero_state(op, basis)
                need(d == ld and list(zip(re.tolist(), im.tolist())) == literal, 'independent literal Gaussian interpreter disagreement')
                accelerated, ad = pc.accelerated_zero_state(op, basis)
                need(ad == ld and accelerated == literal, 'inherited accelerated interpreter disagreement')
                checks += 1
    return checks


def compile_record(name, old, new, rank, metadata=None):
    rec, decoded = pc.compile_transition(old, new, rank)
    rec = json.loads(json.dumps(rec))
    rec['name'] = name
    rec.update(metadata or {})
    rec['independent_phase_witness'] = check_recipe(rec, old.adjoint().then(new))
    rec['local_counts'] = counts(rec)
    return rec, decoded


def validate_inputs():
    manifest = json.loads((INPUT / 'MANIFEST.json').read_text())
    need(manifest['source_pin'] == PIN, 'construction source pin changed')
    for name in ('REPORT.md', 'HANDOFF.md', 'FRAME-INPUT.json', 'ASYMMETRIC.json', 'asymmetric.py'):
        need(sha(INPUT / name) == manifest['files'][name]['sha256'], f'frozen construction hash changed: {name}')
    source = json.loads((INPUT / 'FRAME-INPUT.json').read_text())
    need(source['pin'] == PIN, 'frame source pin changed')
    for path, digest in source['source_hashes'].items():
        need(sha(path) == digest, f'pinned compiler input changed: {path}')
    return source


def weighted_count(records, weights):
    out = Counter()
    by_name = {r['name']: r for r in records}
    for name, multiplicity in weights.items():
        out.update({k: multiplicity * v for k, v in by_name[name]['local_counts'].items()})
    out['complex_coordinate_address_moves'] = out['affine_address_passes'] * SIZE
    out['real_component_address_moves'] = 2 * out['complex_coordinate_address_moves']
    out['factorized_unit_phase_coordinate_actions_upper'] = out['unit_phase_factors'] * SIZE
    out['fused_unit_phase_coordinate_actions_upper'] = out['nontrivial_fused_phase_passes'] * SIZE
    return dict(out)


def main():
    started = time.perf_counter()
    source = validate_inputs()
    small_checks = crosscheck_interpreters()
    ce.Op.zero_state = pc.accelerated_zero_state
    I, F = ce.ident(N), ce.fourier(N)
    records, chains, inverses, geometries = [], [], [], []
    forward_weights, dual_weights, inverse_weights = {}, {}, {}
    lookup = {}
    source_count = 0
    for bank in source['banks']:
        bid = int(bank['bank'])
        U = tuple(bank['geometry']['U'])
        T = ce.canonical_frame(N, U)
        need(tuple(tuple(x) for x in bank['canonical_U_signed_tableau']) == T.tab, 'frozen U representative tableau mismatch')
        need(circuit_tableau(T.circuit, N) == T.tab, 'independent U representative tableau mismatch')
        characteristic = (1 << N) - 1
        need(binary_rank(U) == 9 and binary_rank(U + (characteristic,)) == 9, 'U9 must contain characteristic')
        perp = ce.nullspace(U, N)
        need(len(perp) == 8 and all(bitpar(v) == 0 for v in perp), 'U perpendicular must be alternating8')
        geometries.append(dict(bank=bid, U=list(U), U_rank=9, perpendicular_basis=list(perp),
                               perpendicular_alternating=True, contains_characteristic=True))
        base = f'bank{bid}'
        # U->ZERO is both a native inverse and the actual forward private descent.
        for suffix, old, new, rank in [('ZERO_to_U', I, T, 9), ('U_to_ZERO', T, I, 9),
                                        ('U_to_FULL', T, F, 8), ('FULL_to_U', F, T, 8)]:
            name = base + '_' + suffix
            rec, op = compile_record(name, old, new, rank, dict(bank=bid))
            records.append(rec)
            lookup[name] = op
        forward_weights[base + '_ZERO_to_U'] = 8
        forward_weights[base + '_U_to_ZERO'] = 8
        forward_weights[base + '_U_to_FULL'] = 1088
        dual_weights[base + '_ZERO_to_U'] = 16
        dual_weights[base + '_U_to_FULL'] = 1088
        inverse_weights[base + '_U_to_ZERO'] = 8
        inverse_weights[base + '_ZERO_to_U'] = 8
        inverse_weights[base + '_FULL_to_U'] = 1088
        centre_chain = lookup[base + '_ZERO_to_U'].then(lookup[base + '_U_to_FULL'])
        need(circuit_tableau(centre_chain.circuit, N) == F.tab and states_equal(raw_state(centre_chain.circuit, N), raw_state(F.circuit, N)), 'ordinary centre chain fails exact F residual')
        labels = set()
        need(sum(x['port_multiplicity'] for x in bank['source_transitions']) == 1080, 'bank physical multiplicity')
        for number, src in enumerate(bank['source_transitions']):
            label = int(src['source_label'])
            multiplicity = int(src['port_multiplicity'])
            need(label not in labels and multiplicity == 8 and bitpar(label) == 1 and label != characteristic, 'actual source label census')
            need(binary_rank(U + (label,)) == 9, 'source line outside its declared U')
            labels.add(label)
            A = ce.cgate(N, label)
            name = f'{base}_line{label}_to_U'
            rec, op = compile_record(name, A, T, 8, dict(bank=bid, source_label=label, port_multiplicity=multiplicity))
            need(rec['rank'] == src['B_rank'] and tuple(tuple(x) for x in src['signed_tableau']) == A.adjoint().then(T).tab, 'frozen line transition mismatch')
            records.append(rec)
            forward_weights[name] = dual_weights[name] = multiplicity
            reverse_name = f'{base}_U_to_line{label}'
            inv, inverse_op = compile_record(reverse_name, T, A, 8, dict(bank=bid, source_label=label, port_multiplicity=multiplicity))
            records.append(inv)
            inverse_weights[reverse_name] = multiplicity
            pair = op.then(inverse_op)
            need(circuit_tableau(pair.circuit, N) == I.tab and states_equal(raw_state(pair.circuit, N), raw_state(I.circuit, N)), 'native inverse product is not exact identity')
            inverses.append([name, reverse_name])
            whole = op.then(lookup[base + '_U_to_FULL'])
            expected = A.adjoint().then(F)
            need(circuit_tableau(whole.circuit, N) == expected.tab and states_equal(raw_state(whole.circuit, N), raw_state(expected.circuit, N)), 'complete source path changed inherited endpoint phase')
            chains.append(dict(bank=bid, label=label, multiplicity=multiplicity, recipes=[name, base + '_U_to_FULL'], exact_residual='F C_label^-1', ranks=[8, 8]))
            source_count += 1
            if source_count % 30 == 0:
                print(f'checked {source_count}/270 source labels and {len(records)} serialized recipes', flush=True)
        need(len(labels) == 135, 'distinct labels per bank')
        for a, b in [('ZERO_to_U', 'U_to_ZERO'), ('U_to_FULL', 'FULL_to_U')]:
            word = lookup[base + '_' + a].then(lookup[base + '_' + b])
            need(circuit_tableau(word.circuit, N) == I.tab and states_equal(raw_state(word.circuit, N), raw_state(I.circuit, N)), 'bank inverse pair fails exact identity')
            inverses.append([base + '_' + a, base + '_' + b])
    need(len(records) == 548 and len(chains) == 270, 'complete native recipe coverage')
    need(sum(forward_weights.values()) == sum(dual_weights.values()) == sum(inverse_weights.values()) == 4368, 'weighted transition census')
    paid = Counter()
    by_name = {r['name']: r for r in records}
    for name, multiplicity in forward_weights.items():
        paid[by_name[name]['rank']] += multiplicity
    need(dict(paid) == {8: 4336, 9: 32}, 'complete new positive-child histogram')
    differential = dict(paid)
    differential.update({16: -2160, 17: -32})
    need(sum(r * amount for r, amount in differential.items()) == -128, 'rank mass differential')
    negatives = []
    sample = next(r for r in records if '_line' in r['name'])
    expected = ce.cgate(N, sample['source_label']).adjoint().then(ce.canonical_frame(N, tuple(source['banks'][sample['bank']]['geometry']['U'])))
    for defect in ('global_phase', 'translation', 'child_rank', 'linear_phase', 'quadratic_phase', 'adapter_order'):
        mutant = copy.deepcopy(sample)
        if defect == 'global_phase':
            mutant['left']['phase'] = (mutant['left']['phase'] + 1) % 4
            need(recipe_tableau(mutant, N) == recipe_tableau(sample, N), 'global-phase control should preserve signed tableau')
        elif defect == 'translation':
            mutant['left']['offset'] ^= 1
        elif defect == 'child_rank':
            mutant['rank'] += 1
        elif defect == 'linear_phase':
            mutant['right']['linear_Z4'][0] = (mutant['right']['linear_Z4'][0] + 2) % 4
        elif defect == 'quadratic_phase':
            mutant['left']['quadratic_rows'][0] ^= 2
            mutant['left']['quadratic_rows'][1] ^= 1
        else:
            mutant['left'], mutant['right'] = mutant['right'], mutant['left']
        rejected = False
        try:
            check_recipe(mutant, expected)
        except ValueError:
            rejected = True
        need(rejected, f'negative control accepted: {defect}')
        negatives.append(defect)
    omitted_tail = by_name[chains[0]['recipes'][0]]
    omitted_op = pc.decode(omitted_tail, N)
    label = chains[0]['label']
    need(omitted_op.tab != ce.cgate(N, label).adjoint().then(F).tab, 'omitted source tail should fail endpoint')
    negatives.append('omitted_U_to_FULL_source_tail')
    payload = dict(h=N, phase_convention='Gaussian integer real/imaginary numerator divided by 2^d; C=((1+i)I+(1-i)X)/2',
                   recipes=records, source_chains=chains, inverse_pairs=inverses, geometries=geometries,
                   forward_chronological_multiplicities=forward_weights,
                   same_order_inverse_transpose_multiplicities=dual_weights,
                   time_reversed_adjoint_multiplicities=inverse_weights)
    raw = json.dumps(payload, sort_keys=True, separators=(',', ':')).encode() + b'\n'
    (HERE / 'RECIPES.json').write_bytes(raw)
    result = dict(status='PASS_FINITE_ALL_NEW_U9_EXACT_NATIVE_TRANSITIONS_NO_JOINT_KAPPA', source_pin=PIN,
                  actual_source_ports=2160, distinct_source_labels=270, canonical_banks=2,
                  serialized_recipes=548, signed_pauli_generators_per_recipe=34,
                  exact_phase_witness_coordinates_per_recipe=SIZE,
                  independent_small_all_basis_interpreter_checks=small_checks,
                  native_inverse_pair_checks=len(inverses), complete_source_chain_checks=len(chains), ordinary_centre_chain_checks=2,
                  recipe_rank_histogram=dict(Counter(r['rank'] for r in records)),
                  forward_positive_child_histogram=dict(paid), complete_rank_differential=differential, rank_mass_change=-128,
                  forward_adapter_counts=weighted_count(records, forward_weights),
                  same_order_inverse_transpose_adapter_counts=weighted_count(records, dual_weights),
                  time_reversed_adjoint_adapter_counts=weighted_count(records, inverse_weights),
                  negative_controls_rejected=negatives,
                  adapter_precision=dict(extra_fractional_bits=0, complex_linf_gain=1, real_component_linf_gain=1,
                                         note='Gaussian-unit monomials permute addresses, swap components and change signs. Address and phase evaluation/controller costs remain separately paid.'),
                  physical_child_precision=dict(exact_rank8_child_depth=8, exact_rank9_child_depth=9,
                      complete_new_source_chain_depth_upper=16, complete_new_ordinary_chain_depth_upper=17,
                      private_copy_descent_depth_upper=9,
                      note='Exact-child denominator upper bounds only; no approximate-child error transfer or tape implementation is admitted.'),
                  scalar_invoice_scope='Adapter counts are additional semantic actions on 2^17 complex coordinates per changed transition. The bulk scalar coefficient invoice has its original before-real-imaginary-doubling convention; no mixed units are silently added.',
                  unresolved=['full final H6 compensation word compatibility', 'bank/pad/owner placement', 'physical address/index/tape/controller census', 'whole-word physical input normalization and magnitude', 'approximate-child all-size precision and exact cleanup', 'matching BIT supplier and joint kappa'],
                  recipe_sha256=hashlib.sha256(raw).hexdigest(),
                  source_hashes={str(INPUT / p):sha(INPUT / p) for p in ('FRAME-INPUT.json', 'ASYMMETRIC.json', 'asymmetric.py', 'REPORT.md', 'HANDOFF.md', 'MANIFEST.json')},
                  compiler_hashes=source['source_hashes'],
                  environment=dict(python=sys.version.split()[0], numpy=np.__version__),
                  elapsed_seconds=time.perf_counter()-started,
                  publication='Local only; no primary files changed; no push, PR, post or export.')
    (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'serialized_recipes', 'forward_positive_child_histogram', 'forward_adapter_counts', 'same_order_inverse_transpose_adapter_counts', 'elapsed_seconds')}, indent=2), flush=True)


if __name__ == '__main__':
    main()
