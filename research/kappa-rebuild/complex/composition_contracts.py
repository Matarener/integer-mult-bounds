#!/usr/bin/env python3
"""Small exact composition laws for the already certified native extensions.

Apache-2.0. Substantial OpenAI assistance. No native body is regenerated here;
this binds the complete native receipt and checks the new matrix implication.
"""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rebuild_native as N


def main():
    p, v, ce, predecessor, pins = N.authenticated()
    geo = N.geometry(v.PACKET)
    queries = [{a: N.Q(1), **geo['L'][k]} for k, a in enumerate(geo['selected'])]
    for i, query in enumerate(queries):
        for j in range(112):
            value = sum((coefficient*geo['H'][r].get(j, 0) for r, coefficient in query.items()), N.Q(0))
            N.need(value == -query.get(j, 0), 'Exact C H = -C at row/column '+repr((i, j)))
    receipt_path = HERE/'extension-certificates/RESULT.json'
    receipt = N.read(receipt_path)
    for provider in receipt['providers'].values():
        info = provider['embedded_logger']
        N.need(N.digest(receipt_path.parent/info['artifact']) == info['sha256'], 'Existing complete native embedded-logger artifact')
    result = dict(schema='fresh-native-query-composition-contracts/1',
                  generator_sha256=N.digest(Path(__file__)), native_extension_receipt_sha256=N.digest(receipt_path),
                  reconstruction_source_sha256=N.digest(HERE/'rebuild_native.py'),
                  status='PASS_EXACT_C_H_NEGATIVE_C_AND_SOURCE_BOUND_NATIVE_COMPOSITION',
                  C='[L,I8] in ordinary/selected port order', C_H_equals_negative_C=True,
                  checked_matrix_coefficients=8*112,
                  embedded_logger_body='Balanced H forward; X is unchanged before the logging suffix.',
                  embedded_logger_endpoint='X_out=X_in; Y_out=Y_in+H X_in; d_out=d_in+C X_in.',
                  append_postX_H_after_logging='X_new=H X_in; d_out=d_in+C X_in=d_in-C X_new.',
                  logging_after_postX_H='d_out=d_in+C H X_in=d_in-C X_in.',
                  wrapped_H_then_logging='X_out=H X_in; Y_out=H(Y_in+X_in); d_out=d_in-C X_in.',
                  helper_output_credit='The eight dirty cache outputs require explicit whole-caller closure before independent helper credit.',
                  no_new_native_children_for_any_of_these_scalar_compositions=True,
                  no_new_kappa_claimed=True)
    N.save(HERE/'COMPOSITION-CONTRACTS.json', result)
    print(result['status'])


if __name__ == '__main__':
    main()
