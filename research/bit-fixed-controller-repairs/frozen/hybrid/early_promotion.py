#!/usr/bin/env python3
"""Actual port-route witness against free future codes after early promotion.

Read-only reuse of the pinned exact E8 route reconstruction. This establishes
one missing native admission, not an obstruction to all changed controllers.
Apache-2.0; prepared with substantial OpenAI Codex assistance.
"""
import argparse
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OLD = Path('/Users/ross/git/math/.research-automation/runs/'
    'kappa-3605-successor-20261018T0940Z/major-frontier')
ENDPOINT = HERE.parent / 'bit-endpoint'
sys.path.insert(0, str(ENDPOINT))
import expanded_sections as source


def need(p, message):
    if not p:
        raise ValueError(message)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    inp = OLD/'recursive/BIT-THREE-ROW-INPUT.json'
    mat = json.loads(inp.read_bytes())['matrices']
    R, K = mat['R'], mat['K']
    W = K[:]
    for p in (0, 1, 2):
        W[p] = 0
    A = [i ^ row for i, row in zip(source.eye(111), source.product(W, R))]
    p, q = next((p, q) for p, row in enumerate(A)
        for q in source.bits(row) if p != q)
    raw = source.cap.RAW.read_bytes()
    need(sha256(raw).hexdigest() == source.cap.RAW_SHA, 'R438 source pin')
    word = json.loads(gzip.decompress(raw))
    rho, cap, P, geometry = source.roots_and_routes(word)
    # rho_q fixes the source physical root line P_q, whereas rho_p need not.
    delta = list(map(source.F, word['lines'][q])) + [source.F(0)]*7
    target = [row + [source.F(0)]*7 for row in P[p]]
    target += [[source.F(0)]*15 for _ in range(7)]
    relative = source.mm(rho[p], rho[q])
    image = [sum(x*y for x,y in zip(row, delta)) for row in relative]
    target_component = [sum(x*y for x,y in zip(row, image)) for row in target]
    defect = [x-y for x,y in zip(image, target_component)]
    need(any(image[8:]) and any(defect), 'promoted P flag not preserved')
    mod101 = lambda x: x.numerator*pow(x.denominator, -1, 101) % 101
    need(any(map(mod101, image[8:])), 'actual odd field witness')
    # The actual diagonal relative route fixes its own promoted flag.
    diagonal = source.mm(rho[q], rho[q])
    diagonal_image = [sum(x*y for x,y in zip(row, delta)) for row in diagonal]
    need(diagonal_image == delta, 'diagonal preserved-line control')
    zero_flag = [[source.F(0)]*15 for _ in range(15)]
    need(source.mm(relative, zero_flag) == source.mm(zero_flag, relative),
        'unpromoted zero-frame native preparation control')
    data = {
        'status': 'PASS_ACTUAL_EARLY_PROMOTION_LOSES_FUTURE_CODE_ADMISSION',
        'scientific_pin': '20ecf2891d80b5acf18d980b2164fb44ea7faa90',
        'matrix_input_sha256': sha256(inp.read_bytes()).hexdigest(),
        'route_reconstruction_sha256': sha256((ENDPOINT/'expanded_sections.py').read_bytes()).hexdigest(),
        'R438_word_sha256': sha256(raw).hexdigest(),
        'code_offdiagonal': {'output_port': p, 'input_port': q,
            'coefficient': 1},
        'native_address_input': list(map(str, delta)),
        'native_address_output': list(map(str, image)),
        'output_fresh_coordinates_mod101': list(map(mod101, image[8:])),
        'defect_outside_target_Pp': list(map(str, defect)),
        'covered_domain': 'exact rational address geometry and odd ADDRESS field F101; arbitrary binary VALUE delta at the listed input port/address',
        'logical_boundary': 'initial Y ZERO -> P_p costs one111-port rank-one sweep; after promotion same-port X/Y scalar ADD is admitted but generic cross-port future A code is not',
        'reason': 'rho_s,q fixes P_q, but rho_s,p^-1 rho_s,q sends P_q into fresh E_s outside target P_p for p!=q',
        'controls': ['diagonal relative route fixes its physical root line',
            'unpromoted zero flag is preserved by every relative route'],
        'extra_undo_code_redo_charge': {'rank_one_children_per_bank': 222,
            'scalar_access_and_precision': 'additional; not waived'},
        'limits': ['does not exclude a new native factory accepting promoted Y',
            'does not exclude a changed current-word N cancellation',
            'no general lower bound or positive kappa claim'],
        'geometry_receipt': geometry}
    path = HERE/'EARLY-PROMOTION.json'
    if args.write:
        path.write_text(json.dumps(data, sort_keys=True, indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes()) == data, 'stored receipt differs')
    print(data['status'])
    print('offdiagonal', p, q, 'fresh mod101', data['output_fresh_coordinates_mod101'])


if __name__ == '__main__':
    main()
