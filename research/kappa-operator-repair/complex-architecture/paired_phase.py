#!/usr/bin/env python3
"""Exact two-bank rank reduction, its tensor correction, and the complete bill.

New experiment with substantial OpenAI assistance, Apache-2.0. The native
Clifford compiler and the actual quartet residual are credited to their pinned
PR4045 / PR2226 / adaptive-supplier lineage. No new kappa is admitted here.
"""
from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CLIFFORD = ROOT / 'research/kappa-operator-repair/sources/PR4045/research/staged544-joint-child-rank-interface/frozen/clifford_exact.py'
MOMENT = ROOT / 'research/native-complex-moment552/engines/moment.py'
INVOICE = ROOT / 'research/kappa-operator-repair/composed-supplier/invoice/RESULT.json'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def matrix_product(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)) for i in range(2))


I = ((1, 0), (0, 1))
H = ((1, 1), (1, -1))
HINV = tuple(tuple(Q(x, 2) for x in row) for row in H)


def zgate(bit):
    return ((1, 0), (0, (-1)**bit))


def xgate(bit):
    return matrix_product(matrix_product(H, zgate(bit)), HINV)


def tensor_character(character, f):
    """Actually multiply all 2x2 bank-label commutators, over exact integers."""
    result = I
    target = retained = linear = 0
    for t in range(f):
        x, y, z, w = [(character >> (j*f+t)) & 1 for j in range(4)]
        a, b = x ^ y, y ^ z
        comm = I
        for gate in (zgate(b), xgate(a), zgate(b), xgate(a)):
            comm = matrix_product(gate, comm)
        assert comm == tuple(tuple((-1)**(a*b)*v for v in row) for row in I)
        result = matrix_product(comm, result)
        target += x+y+z+w
        retained += (x ^ y ^ z)+w
        linear ^= y
    result = tuple(tuple((-1)**linear*v for v in row) for row in result)
    exponent = (target-retained) % 4
    assert exponent in (0, 2)
    desired = tuple(tuple((-1)**(exponent//2)*v for v in row) for row in I)
    assert result == desired
    return result[0][0], linear, exponent


def walsh(values):
    out = list(values)
    width = 1
    while width < len(out):
        for base in range(0, len(out), 2*width):
            for j in range(width):
                a, b = out[base+j], out[base+j+width]
                out[base+j], out[base+j+width] = a+b, a-b
        width *= 2
    return out


def add_vector(a, b, coefficient=Q(1)):
    return [(x+coefficient*u, y+coefficient*v) for (x,y),(u,v) in zip(a,b)]


def scale_vector(a, coefficient):
    return [(coefficient*x, coefficient*y) for x,y in a]


def translate(a, mask):
    return [a[j ^ mask] for j in range(len(a))]


def bulk_hadamard(u, v, inverse=False):
    # Literal two ADDs and one scale, with exact dyadic coefficients.
    if inverse:
        v = add_vector(v, u, Q(-1))
        v = scale_vector(v, Q(-1, 2))
        u = add_vector(u, v, Q(-1))
    else:
        u = add_vector(u, v)
        v = scale_vector(v, Q(-2))
        v = add_vector(v, u)
    return u, v


def bulk_x(u, v, mask):
    u, v = bulk_hadamard(u, v, inverse=True)
    v = translate(v, mask)
    return bulk_hadamard(u, v)


def gaussian_column(op, basis):
    values, denominator = op.zero_state(basis)
    return [(Q(a, 2**denominator), Q(b, 2**denominator)) for a,b in values]


def literal_f1(C, retained, target):
    """All 32 independent coefficient inputs; the other bank starts at zero.

    Linearity of these exact all-column checks proves arbitrary values in both
    banks simultaneously. No clean-bank hypothesis enters the identity.
    """
    zero = [(Q(0), Q(0))]*16
    negatives = 0
    for bank in range(2):
        for basis in range(16):
            u, v = (gaussian_column(retained, basis), zero) if bank == 0 else (zero, gaussian_column(retained, basis))
            v = translate(v, 6)
            u, v = bulk_x(u, v, 3)
            v = translate(v, 6)
            u, v = bulk_x(u, v, 3)
            expected = (gaussian_column(target, basis), zero) if bank == 0 else (zero, gaussian_column(target, basis))
            if (u, v) != expected:
                negatives += 1
            u, v = translate(u, 2), translate(v, 2)
            assert (u, v) == expected, (bank, basis)
    assert negatives == 32
    return {'independent_coefficient_inputs': 32, 'exact_gaussian_dyadic': True,
            'both_arbitrary_dirty_banks': True, 'omit_common_translation_rejected_columns': negatives}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--max-f', type=int, default=3, choices=range(1, 5))
    args = parser.parse_args()
    if not args.output.is_absolute():
        parser.error('--output must be an absolute fresh directory')
    args.output.mkdir(parents=True, exist_ok=False)
    C, M = load(CLIFFORD, 'paired_phase_clifford'), load(MOMENT, 'paired_phase_moment')
    assert matrix_product(H, HINV) == I == matrix_product(HINV, H)
    assert xgate(0) == I and xgate(1) == ((0, 1), (1, 0))
    target = C.fourier(4)
    retained = C.cgate(4, 7).then(C.cgate(4, 8))
    correction = retained.adjoint().then(target)
    target_recipe, _ = C.lower_child(target)
    retained_recipe, retained_native = C.lower_child(retained)
    correction_recipe, correction_native = C.lower_child(correction)
    assert [target_recipe['rank'], retained_recipe['rank'], correction_recipe['rank']] == [4, 2, 2]
    for basis in range(16):
        assert gaussian_column(retained_native, basis) == gaussian_column(retained, basis)
        assert gaussian_column(correction_native, basis) == gaussian_column(correction, basis)
        assert gaussian_column(retained.then(correction_native), basis) == gaussian_column(target, basis)
    literal = literal_f1(C, retained, target)
    tensors = []
    for f in range(1, args.max_f+1):
        signs = []
        omitted = 0
        for character in range(1 << (4*f)):
            sign, linear, _ = tensor_character(character, f)
            signs.append(int(sign))
            omitted += int(bool(linear))
        kernel = walsh(signs)
        values = Counter(v for v in kernel if v)
        assert sum(values.values()) == 4**f
        assert set(abs(v) for v in values) == {2**(3*f)}
        assert omitted == (1 << (4*f-1))
        tensors.append({'f': f, 'all_characters_checked': len(signs), 'matrix_identity': True,
                        'correction_kernel_support_per_row': 4**f,
                        'absolute_nonzero_coefficient': str(Q(1, 2**f)),
                        'kernel_numerator_histogram': dict(sorted(values.items())),
                        'kernel_common_denominator': len(signs),
                        'omit_common_translation_rejected_characters': omitted,
                        'literal_bulk_ADDs': 8*f, 'literal_bulk_scales': 4*f,
                        'literal_one_bank_translations': 4*f+2,
                        'paid_native_rank_per_bank': 2*f})
    # Bind the actual shared P -> Q quartet transition, not an invented frame.
    word_path = ROOT/'research/kappa-adaptive-continuation/native-alternatives/candidate/BORROW-WORD-43base.json.gz'
    word = json.loads(gzip.decompress(word_path.read_bytes()))
    entrance, observation = [45], [409, 80, 40, 5, 2]
    for helper in (600, 601, 602, 604):
        assert word['start_extra'][str(helper)] == entrance
        first_write = next(e for e in word['B'] if e[1] == helper)
        assert first_write[0] == 'add' and first_write[-1] == observation
    actual = C.canonical_frame(9, tuple(entrance)).adjoint().then(C.canonical_frame(9, tuple(observation)))
    actual_recipe, actual_native = C.lower_child(actual)
    assert actual_recipe['rank'] == 4
    for basis in range(512):
        assert gaussian_column(actual, basis) == gaussian_column(actual_native, basis)
    actual_binding = {'entrance': entrance, 'observation': observation, 'rank': 4,
                      'exact_all_native_columns_checked': 512, 'recipe': actual_recipe,
                      'composition': 'Retain both monomial wrappers; replace each canonical rank4 interior by the proved rank2 plus correction pair.'}
    invoice = json.loads(INVOICE.read_bytes())
    profile = {int(r): count for r,count in invoice['profile'].items()}
    calls, m, W, a = invoice['calls'], 73, invoice['productive_families'], Q(349, 200000)
    ideal, paid = dict(profile), dict(profile)
    ideal[4] -= 2*calls
    ideal[2] += 2*calls
    paid[4] -= 2*calls
    paid[2] += 4*calls
    def decimals(interval):
        return [M.decimal(x) for x in interval]
    before = M.moment(profile, m, W, a)
    uncharged = M.moment(ideal, m, W, a)
    after = M.moment(paid, m, W, a)
    assert uncharged[1] < 1 < before[0] < after[0]
    def excess(interval):
        return decimals(tuple((x-1)*m*W for x in interval))
    pricing = {'status': 'OPTIMISTIC_INTERFACE_ARITHMETIC_AND_FULL_CORRECTOR_COST_NO_SUPPLIER_ADMISSION',
               'a': str(a), 'dimension': m, 'productive_families': W, 'calls': calls,
               'normalization': 'H_m(r)=r*(m/r)^a. Excess=(moment-1)*m*W equals m^a times the raw excess sum n*r^(1-a)-W*m^(1-a).',
               'baseline_global_excess': excess(before), 'baseline_per_call_excess': decimals(tuple((x-1)*m*W/calls for x in before)),
               'uncorrected_rank_replacement': {'remove': {'4': 2}, 'add': {'2': 2},
                                                'global_excess': excess(uncharged),
                                                'admitted': False},
               'paid_rank_replacement': {'remove': {'4': 2}, 'add': {'2': 4},
                                        'global_excess': excess(after),
                                        'weighted_cost_increase_per_call': decimals(tuple((hi-lo)*m*W/calls for hi,lo in [(after[0],before[1]),(after[1],before[0])])),
                                        'fails_target': True},
               'owner_and_stock_treatment': 'Retained for this favorable screen. No new owner freedom is credited; no all-size native invocation is claimed.',
               'no_new_kappa': True}
    source_paths = [Path(__file__), CLIFFORD, MOMENT, INVOICE,
                    word_path]
    result = {'status': 'EXACT_CHANGED_TWO_BANK_INTERFACE_FULL_PAID_CORRECTION_LOSES',
              'literal_f1': literal, 'tensor_cases': tensors, 'actual_quartet_binding': actual_binding,
              'native_recipes': {'target': target_recipe, 'retained': retained_recipe, 'correction': correction_recipe},
              'pricing': pricing,
              'uniform_identity': 'Per tensor factor X_a Z_b X_a Z_b=(-1)^(ab) I; the f commuting scalar signs multiply exactly.',
              'uniform_resource_limit': 'The explicit correction uses f sequential bulk commutators. A native rank2 correction per bank is uniform but gives 4H2 instead of 2H4 and loses.',
              'scope_of_nonmonomial_support_argument': 'K_f is Fourier-diagonal. In coefficient coordinates every row has 4^f nonzero entries. It is not a pointwise sign, permutation, or D P D-adjoint monomial. This is not a general arithmetic-circuit lower bound.',
              'source_sha256': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in source_paths},
              'new_kappa': False}
    (args.output/'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'tensor_cases': tensors, 'pricing': pricing}, indent=2))


if __name__ == '__main__':
    main()
