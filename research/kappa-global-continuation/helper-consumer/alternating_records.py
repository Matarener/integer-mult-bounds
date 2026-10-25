#!/usr/bin/env python3
"""Routed full-rank record image and an arbitrary-dirty terminal algebra.

The remaining native query/image boundary maps are explicit, unpriced
obligations. They are not silently replaced by scalar maps in a claimed
supplier. The finite scalar test is separately labelled.
Apache-2.0; substantial OpenAI Codex assistance; predecessor credit retained.
"""
from fractions import Fraction as F
from hashlib import sha256
import argparse
import gzip
import json
from pathlib import Path
from owner_coupled_factors import module, need, read, modular_rank


def run(followup, transition, out):
    sym = module(followup/'artifact/integer-mult-bounds/research/kappa-consumer-followup/baseline/symmetric_extended.py')
    c = module(followup/'artifact/integer-mult-bounds/research/kappa-consumer-followup/controller/check_controller.py')
    native = module(followup/'artifact/recovered-involutory/modern_native_component.py')
    G = sym.G
    factors = c.bank_check()['factors']
    a = [[F(v) for v in f['a']] for f in factors]
    b = [[F(v) for v in f['b']] for f in factors]
    routes = read(transition/'evidence/ROUTES.json.gz')
    alternating = read(transition/'evidence/ALTERNATING-RESULT.json')
    need(alternating['local_alphabet'] == 'A_even=[4I8,8iI8], A_odd=[-4I8,8iI8]', 'native alternating alphabet')
    for provider in ('base', 'extra'):
        raw = gzip.decompress((transition/f'evidence/ALTERNATING-PROGRAMS-{provider}.json.gz').read_bytes())
        need(sha256(raw).hexdigest() == alternating['providers'][provider]['emitted_payload_sha256'], 'native alternating emitted word binding')
    for stage in range(9):
        zero = routes[f'{stage}:112']['owner_right_matrix_columns']
        need(all(routes[f'{stage}:{p}']['owner_right_matrix_columns'] == zero for p in range(112, 128)), 'all16 zero ports have same stage route')
        def act(cols, value):
            result = 0
            while value:
                bit = value & -value
                result ^= cols[bit.bit_length()-1]
                value ^= bit
            return result
        need(all(act(zero, act(zero, 1 << k)) == 1 << k for k in range(73)), 'zero owner route inverse')

    # C maps nine query modes to S/T ports in eight input-normalized banks.
    # Ordering of its16 rows: S_X0,T_X0,S_Y0,T_Y0,...,S_Y3,T_Y3.
    C = [[G() for _ in range(9)] for _ in range(16)]
    for j in range(9):
        for bank in range(8):
            C[2*bank][j] = G(a[j][bank] * (1 if j % 2 else -1))
            C[2*bank+1][j] = G(0, -2*a[j][bank])
    # E_b=-S_b/2+iT_b/4, O_b=S_b/2+iT_b/4.
    E = [[G() for _ in range(16)] for _ in range(8)]
    O = [[G() for _ in range(16)] for _ in range(8)]
    for bank in range(8):
        E[bank][2*bank], O[bank][2*bank] = G(F(-1, 2)), G(F(1, 2))
        E[bank][2*bank+1] = O[bank][2*bank+1] = G(0, F(1, 4))
    def combine(rows, coeffs):
        return [sum((q*row[i] for row, q in zip(rows, coeffs)), G()) for i in range(len(rows[0]))]
    left = [None]*9
    left[0] = combine([E[0], E[1], E[3], E[5], E[7]], [1, 1, -1, 1, -1])
    for j, bank in ((2, 1), (4, 3), (6, 5), (8, 7)):
        left[j] = [-v for v in E[bank]]
    for j, banks in ((1, (0, 2)), (3, (2, 4)), (5, (4, 6)), (7, (6,))):
        left[j] = combine([O[bank] for bank in banks], [1]*len(banks))
    def mm(A, B):
        return [[sum((x*y for x, y in zip(row, col)), G()) for col in zip(*B)] for row in A]
    need(mm(left, C) == [[G(i == j) for j in range(9)] for i in range(9)], 'exact Gaussian dyadic left inverse')
    need(all(v.r.denominator & (v.r.denominator-1) == 0 and v.i.denominator & (v.i.denominator-1) == 0 for row in left for v in row), 'left inverse has no odd division')

    # The24-dimensional scalar model has (r=Rx,S,T) in each of8 banks,
    # for one of8 independent query modes. The832 ker(R) data directions
    # are fixed by every defect; hence this model tensors to1024 ports.
    U, V = [], []
    for j in range(9):
        u, v = [G() for _ in range(24)], [G() for _ in range(24)]
        alpha = -4 if j % 2 else 4
        for bank in range(8):
            u[3*bank], u[3*bank+1], u[3*bank+2] = G(-14*a[j][bank]), C[2*bank][j], C[2*bank+1][j]
            v[3*bank], v[3*bank+1], v[3*bank+2] = G(b[j][bank]), G(alpha*b[j][bank]), G(0, 8*b[j][bank])
        U.append(u); V.append(v)
    def dot(x, y):
        return sum((xx*yy for xx, yy in zip(x, y)), G())
    gram = [[dot(v, u) for u in U] for v in V]
    need(all(gram[i][i] == -2 for i in range(9)), 'all diagonal Gram blocks are -2I')
    def apply(state):
        state = state[:]
        for u, v in zip(U, V):
            value = dot(v, state)
            state = [x+y*value for x, y in zip(state, u)]
        return state
    def direct_inverse(state, correct_order=True, include_helpers=True):
        # Query gathering reads all original output values before scattering.
        queries = [dot(v, state) for v in V]
        for j in (range(8, -1, -1) if correct_order else range(9)):
            for k in range(j+1, 9):
                queries[j] += gram[j][k]*queries[k]
        restored = state[:]
        for u, q in zip(U, queries):
            for p in range(24):
                if include_helpers or p % 3 == 0:
                    restored[p] += u[p]*q
        # Erase reversibly: once x is restored, (I-G_lower)q=-Vx.
        # Descending order preserves every old lower-index query block.
        for i in range(8, -1, -1):
            for j in range(i):
                queries[i] -= gram[i][j]*queries[j]
        for i, v in enumerate(V):
            queries[i] += dot(v, restored)
        return restored, queries
    for col in range(24):
        initial = [G(i == col) for i in range(24)]
        restored, scratch = direct_inverse(apply(initial))
        need(restored == initial and not any(scratch), 'all active data and dirty helper basis columns restored')
    dirty = [G((i*7+3) % 13-6, (i*5+1) % 11-5) for i in range(24)]
    altered = apply(dirty)
    need(direct_inverse(altered)[0] == dirty, 'fully nonzero Gaussian dirty test')
    need(direct_inverse(altered, correct_order=False)[0] != dirty, 'upper solve order mutation rejected')
    need(direct_inverse(altered, include_helpers=False)[0] != dirty, 'helper restoration omission rejected')

    # Exact actual-route delta-cover screen for the proposed32-channel
    # X-bank compression. This is a scalar-input slice, not a rank theorem
    # over the full algebra of arbitrary cover operators.
    inp = followup/'artifact/recovered-involutory/modern-source/inputs'
    receipt = read(inp/'NATIVE-RECEIPT.json')
    provider = receipt['providers']['base']
    loc = inp/'native-cache'/provider['word_sha256']/'local'
    word, programs = read(loc/'CANONICAL-WORD.json.gz'), read(loc/'LOCAL-PROGRAMS.json.gz')
    prefix = native.replay(programs['forward'][:programs['forward'].index(['phase', 'centers'])])
    R = [{p: value for (p, warp), value in prefix['L', center].items() if p < 112 and not warp} for center in word['centers']]
    need(native.matmul(R, [{k: row[p] for k, row in enumerate(R) if p in row} for p in range(112)]) == [{k: F(56)} for k in range(8)], 'actual source query Gram')
    for p in range(112):
        need(len({tuple(routes[f'{j}:{p}']['owner_right_matrix_columns']) for j in range(9)}) == 9, 'nine actual route images of delta_identity are distinct')
    image, query = [], []
    for j in range(9):
        for row in R:
            image.append({(bank, p, j): -a[j][bank]*value/4 for bank in (0, 2, 4, 6) for p, value in row.items() if a[j][bank]})
            query.append({(bank, p, j): b[j][bank]*value for bank in (0, 2, 4, 6) for p, value in row.items() if b[j][bank]})
    image_rank, query_rank = modular_rank(image), modular_rank(query)
    need(image_rank['rank'] == 72 and query_rank['rank'] == 64, 'actual route delta slice ranks')

    # Retained scalar grammar explicitly permits clearing owned C scratch.
    # Bind the cheaper cleanup option to literal opcodes, not a Python-only
    # reset. Appending72 simultaneous copies/clears to the actual raw core
    # checks common FULL access, all632 live columns, and zero query outputs.
    center_start = programs['forward'].index(['phase', 'centers'])
    center_end = programs['forward'].index(['phase', 'B'])
    raw_core = programs['forward'][:center_start] + [['phase', 'centers']] + programs['forward'][center_end:]
    owned_copies = [native.scalar(('C', q), ('L', 0), F(1), 1) for q in range(72)]
    owned_clears = [['scalar', ['clear', ['C', q]], 0] for q in range(72)]
    need(native.core_frame_check(word, raw_core+owned_copies+owned_clears) ==
         native.core_frame_check(word, raw_core), '72 owned clears admitted by actual native grammar')
    baseline, cleared = native.replay(raw_core), native.replay(raw_core+owned_copies+owned_clears)
    need(all(cleared['L', p] == baseline['L', p] for p in range(632)), 'owned clear leaves all632 live columns unchanged')
    need(all(not cleared['C', q] for q in range(72)), 'all72 literal owned query clears return zero')
    need(native.scalar_bill(owned_clears)['real_primitives'] == 144, 'exact72-clear scalar charge')
    need(len(word['zero_buffers']) == 91, 'retained owned-zero field envelope')

    out.mkdir(parents=True, exist_ok=True)
    def vals(matrix):
        return [[v.data() for v in row] for row in matrix]
    bank_gram = [[int(sum(x*y for x, y in zip(b[i], a[j]))) for j in range(9)] for i in range(9)]
    ir = {'version': 1, 'status': 'ALGEBRAIC_CONSUMER_WITH_UNLOWERED_NATIVE_BOUNDARIES',
          'owned_query_fields': 72, 'borrowed_extra_inputs_may_be_arbitrary': True,
          'query_gather': [{'stage': j, 'bank_vector': [int(x) for x in b[j]],
             'query_rows': 'Q_j=[R,alpha_j I8,8i I8] after actual stage port routes',
             'alpha_j': -4 if j % 2 else 4,
             'native_obligation': 'V times the input/terminal native gauge inverse on ordinary X ports; tariff unknown'} for j in range(9)],
          'upper_triangular_word': [{'target_query_block': i, 'source_solved_block': j, 'gram_bank_coefficient': bank_gram[i][j]}
                                   for i in range(8, -1, -1) for j in range(i+1, 9) if bank_gram[i][j]],
          'gram_operator': '-(b_i^T a_j)/4 times [sum_p R[:,p]R[:,p]^T P(rho_i,p)P(rho_j,p)^-1 + (alpha_i alpha_j-64) I8 P(rho_i,zero)P(rho_j,zero)^-1]',
          'gram_boundary_cancellation': 'Under physical conjugation Gamma, (V_i Gamma^-1)(Gamma U_j)=V_i U_j; no commutation of Gamma through a port route is used.',
          'query_images': [{'stage': j, 'bank_vector': [int(x) for x in a[j]],
             'image': '-Q_j^T/4 after inverse actual stage port routes',
             'native_obligation': 'Physical terminal gauge times U on ordinary X ports; tariff unknown'} for j in range(9)],
          'cleanup_lower_triangular_word': [{'target_query_block': i, 'source_original_block': j,
              'subtract_gram_bank_coefficient': bank_gram[i][j]}
              for i in range(8, -1, -1) for j in range(i) if bank_gram[i][j]],
          'cleanup_native_regather': 'Add Vphys times the restored entire state to the transformed queries; this is a SECOND physical V boundary pass, with unknown optimized tariff.',
          'cleanup_identity': '(I-G_lower)q=-Vphys x_restored, so every query becomes exactly zero by addition, without overwriting a nonzero register.',
          'cleanup': [{'release_verified_zero_query_field': q} for q in range(72)],
          'admitted_owned_clear_alternative': {'events': owned_clears, 'real_scalar_primitives': 144,
              'physical_boundary_passes': {'query_V': 1, 'image_U': 1},
              'grammar_source': 'modern_native_component.py core_frame_check scalar clear branch admits owned C scratch; replay assigns the owned field zero.',
              'grammar_source_sha256': sha256((followup/'artifact/recovered-involutory/modern_native_component.py').read_bytes()).hexdigest(),
              'all632_live_columns_preserved_by72_simultaneous_query_clear_probe': True,
              'proposed_owned_field_map': [{'query': q, 'retained_zero_buffer_role': word['zero_buffers'][q],
                  'physical_family_formula': f'W+384+{q}'} for q in range(72)],
              'hosting_condition': 'After every local and idle call has returned its private buffers; serial terminal replicas; actual changed global layout must bind W and these reserved91 owned fields.'},
          'R': [{str(p): str(v) for p, v in sorted(row.items())} for row in R],
          'routes_payload_sha256': sha256(gzip.decompress((transition/'evidence/ROUTES.json.gz').read_bytes())).hexdigest(),
          'record_coefficient_matrix_C': vals(C), 'record_left_inverse': vals(left),
          'actual_record_left_inverse': 'First apply the displayed scalar left inverse on128 zero ports, then apply rho_i,zero to each recovered eight-field block i.'}
    raw = json.dumps(ir, sort_keys=True, separators=(',', ':')).encode()
    (out/'ALTERNATING-CONSUMER-IR.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    result = {'status': 'PASS_ROUTED_ALTERNATING_RECORD_LEFT_INVERSE_AND_DIRTY_CONSUMER_ALGEBRA',
              'record_image_rank': 72, 'available_zero_output_fields': 128, 'scalar_coefficient_rank': 9,
              'left_inverse_gaussian_dyadic': True, 'record_left_inverse_actual_operator_identity': True,
              'native_alternating_provider_payloads': {p: alternating['providers'][p]['emitted_payload_sha256'] for p in ('base', 'extra')},
              'dirty_completion': 'M^-1=I+U(I-G_upper)^-1 V; gather, descending upper solve, scatter to every output; apply I-G_lower to stored queries and add V of the restored state, making all72 queries exactly zero.',
              'physical_boundary_passes': {'query_V': 2, 'image_U': 1},
              'query_cleanup_is_arithmetic_not_overwrite': True,
              'owned_clear_alternative_admitted': True,
              'owned_clear_alternative_passes': {'query_V': 1, 'image_U': 1},
              'owned_clear_alternative_real_primitives': 144,
              'owned_clear_grammar_probe_live_input_columns': 632,
              'active_scalar_model_basis_columns_checked': 24, 'active_modes': 8, 'fixed_kernel_data_dimensions': 832,
              'scalar_model_total_dimensions': 1024, 'scalar_model_scope': 'All stages have identical cover routes. The arbitrary-route completion is the ordered-ring proof, not this scalar test.',
              'negative_controls_rejected': ['wrong triangular order', 'omitted dirty helper scatter'],
              'actual_X_image_delta_slice_rank': image_rank, 'actual_X_query_delta_slice_rank': query_rank,
              'delta_slice_scope': 'Input each query field on the identity cover class. These72 image columns (64 nonzero query columns) are independent over Q. This rejects bank-only scalar compression to32; it does not bound arbitrary operator-valued factorizations.',
              'unresolved_native_interfaces': ['literal tariffed physical V query gathering and regathering for erasure', 'literal tariffed physical U scattering', '72-field owned workspace hosting and verified-zero release', 'complete scalar/address/precision charges and changed supplier allocation'],
              'consumer_ir_payload_sha256': sha256(raw).hexdigest()}
    (out/'ALTERNATING-RECORDS-RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--followup', type=Path, required=True)
    parser.add_argument('--transition', type=Path, default=Path(__file__).resolve().parent.parent/'symmetric-transition')
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'evidence')
    args = parser.parse_args()
    result = run(args.followup, args.transition, args.out)
    print(result['status'])
    print('actual routed record image rank72; Gaussian-dyadic left inverse; arbitrary-dirty ordered algebra; native U/V tariffs open')
