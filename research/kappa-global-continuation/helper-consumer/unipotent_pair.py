#!/usr/bin/env python3
"""A new zero-repair unipotent pair and its exact final-pair limitation.

The t=14 member differs from the predecessor's t=12 involution. It is an
executable local Gaussian-dyadic alternative; it is not a global supplier.
Apache-2.0, with substantial OpenAI Codex assistance and retained source credit.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import argparse
import gzip
import json
from pathlib import Path

from owner_coupled_factors import module, read, need


def run(followup, out):
    recovered = followup/'artifact/recovered-involutory'
    controller = followup/'artifact/integer-mult-bounds/research/kappa-consumer-followup/controller'
    m, c = module(recovered/'modern_native_component.py'), module(controller/'check_controller.py')
    inp = recovered/'modern-source/inputs'
    receipt = read(inp/'NATIVE-RECEIPT.json')
    need(m.digest(inp/'NATIVE-RECEIPT.json') == m.NATIVE_RECEIPT_SHA, 'source receipt pin')
    out.mkdir(parents=True, exist_ok=True)
    result = {'status': 'PASS_LOCAL_UNIPOTENT_DIRTY_PAIR_WITH_FINAL_PAIR_OBSTRUCTION', 'providers': {},
              'scope': 'Native local t=14 pair only, plus algebraic final B/F boundary limitation for all t. No complete consumer or kappa is admitted.',
              'family': 'D_t=I+(t P_e-K_e)Q, s=t-13. For nonzero Gaussian-dyadic units s, D_t^-1=I-(t P_e-K_e)Q/s is Gaussian-dyadic.',
              'pair': 'F_t(z,y)=(D_t z,y+E D_t z); B_t(z,y)=(D_t^-T z-E^T y,y)=F_t^-T(z,y).',
              'zero_buffer_scope': '91 owned zero buffers inherited from the followup word, not arbitrary dirty initial buffer states.'}
    hosts = (224, 225, 227, 229, 240, 241, 256, 257)
    for name, provider in receipt['providers'].items():
        loc = inp/'native-cache'/provider['word_sha256']/'local'
        for basename in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz'):
            need(m.digest(loc/basename) == provider['complete_native_files']['local/'+basename], 'source payload pin')
        word, old = read(loc/'CANONICAL-WORD.json.gz'), read(loc/'LOCAL-PROGRAMS.json.gz')
        R, K, _, J, _, _ = m.clean_reconstruction(word, old)
        before = m.replay(old['forward'][:old['forward'].index(['phase', 'centers'])])
        H = [{h: value for (h, warp), value in before['L', center].items() if h >= 224 and not warp}
             for center in word['centers']]
        queries = []
        for r, h in zip(R, H):
            row = r.copy(); m.add(row, h); queries.append(row)
        inverse_minor = c.inverse([[row.get(h, Q(0)) for h in hosts] for row in H])
        P = [{} for _ in range(632)]
        for h, row in zip(hosts, inverse_minor):
            P[h] = {k: v for k, v in enumerate(row) if v}
        Kext = K + [{} for _ in range(520)]
        A = []
        for p, k in zip(P, Kext):
            row = {j: -v for j, v in k.items()}; m.add(row, p, Q(14)); A.append(row)
        need(m.matmul(queries, A) == [{} for _ in range(8)], 'unipotent nilpotence Q A14=0')
        N = m.matmul(A, queries)
        need(m.matmul(N, N) == [{} for _ in range(632)], 'N squared is exactly zero')
        D = [row.copy() for row in N]
        inverse = [{j: -v for j, v in row.items()} for row in N]
        for p in range(632):
            m.add(D[p], {p: Q(1)}); m.add(inverse[p], {p: Q(1)})
        identity = [{p: Q(1)} for p in range(632)]
        need(m.matmul(D, inverse) == m.matmul(inverse, D) == identity, 'two-sided dyadic inverse')
        need(m.matmul(D, D) != identity, 'unipotent is not the old involution')
        query_t = [{p: row[k] for p, row in enumerate(A) if k in row} for k in range(8)]
        minus_qt = [{k: -row[p] for k, row in enumerate(queries) if p in row} for p in range(632)]
        codes = {'forward': m.source_code(queries, A, 0, 1),
                 'backward': m.source_code(query_t, minus_qt, 0, 1)}
        inverse_t = [{p: row[j] for p, row in enumerate(inverse) if j in row} for j in range(632)]
        programs, checks = {}, {}
        for orientation in ('forward', 'backward'):
            old_word = old[orientation]
            a, b = old_word.index(['phase', 'centers']), old_word.index(['phase', 'B'])
            raw = old_word[:a] + [['phase', 'centers']] + old_word[b:]
            changed = raw + codes[orientation]
            profile = m.core_frame_check(word, changed)
            need(profile == {1: 2440, 2: 725, 3: 224, 4: 102, 5: 20}, 'same complete native child invoice')
            actual = m.replay(changed)
            for p in range(632):
                rows = D if orientation == 'forward' else inverse_t
                expected = {(j, ()): v for j, v in rows[p].items()}
                if orientation == 'forward' and 112 <= p < 224:
                    m.add(expected, {(j, ()): v for j, v in D[p-112].items()})
                elif orientation == 'backward' and p < 112:
                    m.add(expected, {(112+p, ()): Q(-1)})
                need(actual['L', p] == expected, f'all632 native endpoint columns {name}:{orientation}:{p}')
            need(all(not row for (kind, _), row in actual.items() if kind in 'CZ'), 'owned scratch cleanup')
            programs[orientation] = changed
            checks[orientation] = {'input_columns': 632, 'native_rank_mass': sum(r*n for r, n in profile.items()),
                                   'profile': profile, 'scalar_invoice': m.scalar_bill(changed),
                                   'new_native_children': 0, 'native_frame_chronology': 'complete literal replay'}
        # For every t, E D_t E^T = I-KR = J. In B_t followed by F_u,
        # d z_B / d y = -E^T; hence d x_F / d y = -J independently of t,u.
        # Isolated native stage routes conjugate J by invertible owner maps.
        want_kr = m.matmul(K, R)
        need(any(row for row in want_kr), 'nontrivial final-pair defect')
        need(m.matmul(R, K) == [{i: Q(14)} for i in range(8)], 'rank KR exactly eight')
        p = next(i for i, row in enumerate(R) if row)
        source_port = min(R[p])
        column = {i: row[source_port] for i, row in enumerate(want_kr) if source_port in row}
        need(column, 'explicit final-pair column witness')
        support = sorted({h for row in H for h in row})
        need(len(support) == 106, 'source dirty helper support')
        need(all(word['start'][h] == 0 and word['final'][h] == 1 for h in support), 'actual dirty helper I to FULL boundaries')
        center_ops = [e for e in old['forward'] if e[0] == 'center']
        need(len(center_ops) == 8 and all(e[-1] == 8 and e[3] == 0 for e in center_ops), 'literal inverse rank8 centre endings')
        raw_payload = json.dumps(programs, sort_keys=True, separators=(',', ':')).encode()
        (out/f'UNIPOTENT-PROGRAMS-{name}.json.gz').write_bytes(gzip.compress(raw_payload, mtime=0))
        result['providers'][name] = {'checks': checks, 'word_sha256': provider['word_sha256'],
             'program_payload_sha256': sha256(raw_payload).hexdigest(), 'parameter_t': 14, 'query_eigenvalue_s': 1,
             'final_pair_error_rank': 8, 'final_pair_column_input_port': source_port,
             'final_pair_column_error': {str(k): str(v) for k, v in column.items()},
             'final_pair_exact_statement': 'On arbitrary independent inputs to an isolated B_t/F_u boundary, d X_out/d Y_in=-J, instead of -I. The error KR has rank8. Nonzero stage routes conjugate this defect and cannot make it vanish.',
             'echo_boundary_census': {'query_helpers': len(support), 'I_to_FULL': len(support),
                'same_inverse_C8_boundary_as_forward_centers': 0,
                'scope': 'Changing the right inverse within the actual nonzero H support cannot itself supply the omitted inverse rank8 endpoint. An altered interior program or a paid transport is a separate construction.'}}
    (out/'UNIPOTENT-RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--followup', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'evidence')
    args = parser.parse_args()
    result = run(args.followup, args.out)
    print(result['status'])
    for provider, result in result['providers'].items():
        print(provider, {side: row['scalar_invoice']['real_primitives'] for side, row in result['checks'].items()})
