#!/usr/bin/env python3
"""Read-only exact right-kernel check for the complete frozen full history.

Replays the actual signed-native provider and checks H K = 0 by cancellation
of identical literal monomial operators, separately for every original-input
column. No discovery eliminator, finite-field rank test, width-one matrix-sum
identity, or operator-polynomial inverse is used. Apache-2.0; substantial
OpenAI Codex assistance for THU New Media Research Center (@thu-nmrc).
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import argparse, importlib.util, json, sys
HERE = Path(__file__).resolve().parent
KERNEL_SHA = 'ad403cdd98975ae9a8033afff5a86f96d055e44c5be19c1f171387cf26cd3b81'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def y_identity(kernel):
    return all(kernel[112+j] == {j: F(1)} for j in range(112))


def residual(row, kernel):
    """Multiply one actual H row by scalar K, retaining literal operator IDs."""
    out = {}
    for (role, operator), value in row.items():
        need(role[0] == 'L' and 0 <= role[1] < 632,
             'every observable depends only on the 632 original logical inputs')
        for column, scalar in kernel[role[1]].items():
            key = column, operator
            q = out.get(key, F(0)) + value * scalar
            if q:
                out[key] = q
            else:
                out.pop(key, None)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runtime', type=Path, default=HERE)
    ap.add_argument('--write', action='store_true', help='author the frozen result; default only compares')
    args = ap.parse_args()
    runtime = args.runtime.resolve()
    need((runtime/'native.py').is_file() and (runtime/'monomial.py').is_file(),
         'actual native runtime directory')
    sys.path.insert(0, str(runtime))
    import native as N
    import monomial as M
    raw = (HERE/'KERNEL.json').read_bytes()
    need(sha256(raw).hexdigest() == KERNEL_SHA, 'frozen sparse kernel bytes')
    certificate = json.loads(raw)
    need(certificate['schema'] == 'native-full-history-Y-kernel/v1', 'kernel schema')
    need(certificate['original_input_roles'] == 632 and certificate['free_Y_columns'] == 112,
         'kernel dimensions')
    need(sha256((runtime/'native.py').read_bytes()).hexdigest() == certificate['source_native_sha256'],
         'source native interpreter pin')
    need(sha256((runtime/'monomial.py').read_bytes()).hexdigest() == certificate['source_monomial_sha256'],
         'literal signed-monomial evaluator pin')
    encoded_rows = certificate['rows']
    need(len(encoded_rows) == 632, 'one kernel row for every independent original input')
    kernel = []
    for encoded in encoded_rows:
        row = {}
        for column, coefficient in encoded:
            value = F(coefficient)
            need(isinstance(column, int) and 0 <= column < 112 and column not in row and value,
                 'unique nonzero scalar kernel entry')
            row[column] = value
        kernel.append(row)
    need(y_identity(kernel), 'K_Y is exactly the identity: every original Y deformation is available')
    need(kernel[:112] == kernel[112:224] and all(not row for row in kernel[224:]),
         'explicit K=(I,I,0): equal X/Y displacement and unchanged independent helpers')

    source, provider = N.read('source'), N.read('provider')
    canon = source['canonical']
    N.initialize(canon)
    histories, final, frames, full = N.native_replay(canon, provider['word'], True)
    need(len(histories) == 4891, 'all distinct frozen backward full-frame histories')
    need(len(N.operators) == 215, 'actual signed native operator registry')
    literal_columns = [list(M.decode(op)) for op in N.operators]
    need(all(len(columns) == 512 and len({v//4 for v in columns}) == 512
             and all(0 <= v < 2048 for v in columns) for columns in literal_columns),
         'every operator is an actual one-column signed monomial permutation')
    need(len(set(N.operators)) == len(N.operators), 'literal operator canonicalization')
    need(N.operators[0] == M.IDENTITY, 'literal identity index')
    terms = 0
    active_terms = 0
    for j, row in enumerate(histories):
        need(all(0 <= operator < len(N.operators) for role, operator in row),
             'every history term uses the fresh literal operator registry')
        need(not residual(row, kernel), 'exact H K = 0 at history ' + str(j))
        terms += len(row)
        active_terms += sum(bool(kernel[role[1]]) for role, operator in row)
    need(terms == 119515, 'full actual-history term count')

    def extra_case(label, program, backward, case_kernel):
        # A fresh module instance gives each source case its own authenticated
        # literal registry, without changing the accepted runtime on disk.
        spec = importlib.util.spec_from_file_location('kernel_native_' + label, runtime/'native.py')
        fresh = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fresh)
        fresh.initialize(canon)
        case_histories, _, _, _ = fresh.native_replay(canon, program, backward)
        case_terms = sum(map(len, case_histories))
        case_active = 0
        for j, row in enumerate(case_histories):
            need(not residual(row, case_kernel), 'exact ' + label + ' HK=0 at history ' + str(j))
            case_active += sum(bool(case_kernel[role[1]]) for role, operator in row)
        columns = [list(M.decode(op)) for op in fresh.operators]
        need(len(set(fresh.operators)) == len(fresh.operators), label + ' literal operator uniqueness')
        return {
            'direction': 'raw backward' if backward else 'forward',
            'full_frame_histories': len(case_histories), 'history_exact_terms': case_terms,
            'history_terms_with_nonzero_kernel_row': case_active,
            'literal_group_operators': len(fresh.operators),
            'literal_decoded_operator_columns_sha256': sha256(json.dumps(columns, separators=(',', ':')).encode()).hexdigest(),
            'kernel_formula': 'K_X=I_112, K_Y=I_112, K_helpers=0_408x112' if backward else 'K_X=0_112x112, K_Y=I_112, K_helpers=0_408x112',
            'exact_HK_zero': True,
        }

    forward_kernel = [{} for _ in range(112)] + [{j: F(1)} for j in range(112)] + [{} for _ in range(408)]
    need(len(forward_kernel) == 632 and y_identity(forward_kernel), 'explicit forward kernel target freedom')
    source_backward = extra_case('source_backward', source['programs']['backward'], True, kernel)
    source_forward = extra_case('source_forward', source['programs']['forward'], False, forward_kernel)
    need(source_backward['full_frame_histories'] == 5019 and source_backward['history_exact_terms'] == 80001,
         'frozen source-backward observation family')
    need(source_forward['full_frame_histories'] == 4968 and source_forward['history_exact_terms'] == 94137,
         'frozen source-forward observation family')

    # Four controls test distinct proof obligations. These deliberately altered
    # test objects are not claimed to be legal alternate native producers.
    zero_kernel = [{} for _ in range(632)]
    need(all(not residual(row, zero_kernel) for row in histories), 'zero-kernel test baseline')
    control_target = not y_identity(zero_kernel)
    need(control_target, 'control: the vacuous zero kernel must fail target freedom')

    missing = [dict(row) for row in kernel]
    missing[0] = {}
    missing_failures = [j for j, row in enumerate(histories) if residual(row, missing)]
    need(missing_failures, 'control: deleting the X_0 compensator must expose a history')

    sign_index = next(j for j, row in enumerate(histories)
                      if any(role[1] < 112 for role, operator in row))
    corrupted = dict(histories[sign_index])
    term = next(key for key in corrupted if key[0][1] < 112)
    corrupted[term] = -corrupted[term]
    sign_residual = residual(corrupted, kernel)
    need(sign_residual, 'control: changing one signed X observation term must break cancellation')

    side_observation = {(('L', 112), 0): F(1)}
    side_residual = residual(side_observation, kernel)
    need(side_residual, 'control: adding an original/lower-frame Y side observation must break the barrier')

    operator_digest = sha256(json.dumps(literal_columns, separators=(',', ':')).encode()).hexdigest()
    result = {
        'schema': 'native-full-history-direct-scalar-kernel/v1',
        'status': 'PASS_EXACT_ALL_WIDTH_FULL_HISTORY_Y_BLINDNESS',
        'kernel_sha256': KERNEL_SHA,
        'source_native_sha256': certificate['source_native_sha256'],
        'source_monomial_sha256': certificate['source_monomial_sha256'],
        'source_inputs': {name: {'path': path, 'sha256': digest}
                          for name, (path, digest) in sorted(N.INPUTS.items())},
        'direction': 'raw backward',
        'full_frame_histories': len(histories),
        'history_exact_terms': terms,
        'history_terms_with_nonzero_kernel_row': active_terms,
        'original_input_rows': 632, 'free_Y_columns': 112,
        'kernel_nonzero_rows': sum(bool(row) for row in kernel),
        'kernel_scalar_terms': sum(len(row) for row in kernel),
        'kernel_formula': 'K_X=I_112, K_Y=I_112, K_helpers=0_408x112',
        'literal_group_operators': len(N.operators),
        'literal_decoded_operator_columns_sha256': operator_digest,
        'cases': {
            'provider_backward': {
                'direction': 'raw backward', 'full_frame_histories': len(histories),
                'history_exact_terms': terms, 'history_terms_with_nonzero_kernel_row': active_terms,
                'literal_group_operators': len(N.operators),
                'literal_decoded_operator_columns_sha256': operator_digest,
                'kernel_formula': 'K_X=I_112, K_Y=I_112, K_helpers=0_408x112',
                'exact_HK_zero': True,
            },
            'source_backward': source_backward,
            'source_forward': source_forward,
        },
        'negative_controls': {
            'zero_kernel_passes_HK_but_fails_Y_identity': control_target,
            'deleted_X0_compensator': {'rejected': True, 'failing_histories': len(missing_failures),
                                        'first_failing_history': missing_failures[0]},
            'one_signed_X_history_coefficient': {'rejected': True, 'history': sign_index,
                                                  'residual_literal_terms': len(sign_residual)},
            'original_Y_side_observation': {'rejected': True, 'residual_literal_terms': len(side_residual)}
        },
        'all_width_lift': 'Every coefficient of HK cancels between identical actual signed monomial operators, before numerical evaluation. Literal products and phase identities lift to every positive tensor width, with exterior scalar rational coefficients unchanged.',
        'information_consequence': 'For every logical original Y displacement v, displace logical original X by the same v in either backward case, or leave X unchanged in the source-forward case; leave all 408 independent helper inputs fixed. Every full-frame history is identical. Thus a decoder receiving only that complete history cannot determine a nonconstant Y-only function, even with arbitrary nonlinear postprocessing.',
        'physical_coordinates': 'Logical original-input coordinates are used. Each physical independent input differs by an invertible birth-chart right factor. Conjugating the input displacement by those factors preserves HK=0 and arbitrary variation of physical Y; this is not a claim that the physical input embedding is scalar-only or free.',
        'scope': 'Only the frozen #5402 raw-backward provider and original source-backward/source-forward full-frame observation families, each considered separately. The decoder is not also given lower-frame values, original inputs, new paid observations, or a changed producer. Source native, phase and compiler premises are inherited.',
        'width_one_matrix_sum_relations_used': False,
        'polynomial_operator_inverses_used': False,
        'module_factorization_required_at_runtime': False,
        'new_observation_or_kappa': False,
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write:
        (HERE/'KERNEL-RESULT.json').write_text(encoded)
    else:
        need(json.loads((HERE/'KERNEL-RESULT.json').read_text()) == result,
             'stable direct-kernel receipt differs')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
