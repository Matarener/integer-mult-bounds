#!/usr/bin/env python3
"""Verify the independent audit of PR6114 (controller income bound). Standard library only.

    python3 -B research/p104-controller-income-audit/verify.py          # check RESULT.json
    python3 -B research/p104-controller-income-audit/verify.py --write  # regenerate it

Josie Elliston with Claude Code (Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import audit as A  # noqa: E402

CONTROLLERS = {
    'kappa_backward_controller': 'research/kappa-backward-controller-20261023/CONTROLLER.json',
    'joint_helper_lattice': 'research/joint-helper-lattice/CONTROLLER.json',
    'p104_productive_controller': 'research/p104-productive-controller/CONTROLLER.json',
}
D = 8  # rank per stage lift per bank


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    inputs = [f for f in pins['files'] if f['usage'] == 'input']
    for f in inputs:
        need(sha256((ROOT / f['path']).read_bytes()).hexdigest() == f['sha256'], 'pinned input ' + f['path'])
    need(sorted(f['path'] for f in inputs) == sorted(CONTROLLERS.values()), 'input set')
    return len(inputs)


def audit_controller(name, path):
    word = json.loads((ROOT / path).read_text())
    n = 2 * word['pairs']
    need(n == 32, name + ': 32 banks')
    # boundaries: exact constant rational programs, invertible
    for side in ('left', 'right'):
        M = A.run_program(word['boundaries'][side + '_program'], n)
        need(M == [[F(x) for x in row] for row in word['boundaries'][side]], name + ': boundary program ' + side)
        need(A.rank(M) == n, name + ': invertible ' + side + ' boundary')
    out, cnt = A.exact_replay(word)
    diag = [tuple(t) for t in word['diagonal']]
    expected = [[({diag[i]: F(1)} if i == j else {}) for j in range(n)] for i in range(n)]
    need(out == expected, name + ': exact Laurent outputs equal the declared diagonal')
    odd = sum(1 for t in diag if t[0] % 2)
    need(odd == n and all(abs(t[0]) == 1 for t in diag), name + ': every output an odd monomial Q^+-1 D^S')
    thick, thin = cnt['LOCAL'], cnt['QUERY_SHEAR']
    s = thick + thin
    # determinant identity (stage exponents and central exponent of det)
    stage_mass = sum(sum(t[1:]) for t in diag)
    need(all(max(t[1:]) <= 1 for t in diag), name + ': stage sets, no repeated stage in an output')
    need(stage_mass == cnt['lifts'], name + ': sum |S_i| = row-stage lifts (det D-exponent)')
    need(sum(t[0] for t in diag) == cnt['qpower'], name + ': sum of central exponents = net Q_POWER (det Q-exponent)')
    for st in range(A.NS):
        per_stage_out = sum(t[1 + st] for t in diag)
        per_stage_lift = 0
        for e in word['physical_events']:
            if e[0] == 'LOCAL' and e[1] == st:
                per_stage_lift += 2
            if e[0] == 'IDLE' and st in e[2]:
                per_stage_lift += 2
        need(per_stage_out == per_stage_lift, name + ': per-stage det identity at D_%d' % st)
    targets = sum(1 + D * sum(t[1:]) for t in diag)
    income = targets - D * cnt['lifts'] - thin
    need(income == odd - thin == thick - 1, name + ': income = outputs - thin = thick - 1')
    # specialized even-part traces with random nonzero stage values (PR6114 used D_s -> 1)
    rng = random.Random('s46-' + name)
    receipts = {}
    for theta in (F(13, 7), F(19, 11)):
        r = A.random_rationals(rng, A.NS)
        trace, deltas, free_changes, out_even = A.image_trace(word, theta, r)
        need(free_changes == 0, name + ': no free event changes the even rank')
        need(deltas[0] == 0, name + ': first paid shear leaves the even rank unchanged')
        need(all(d in (0, -1, 1) for d in deltas), name + ': each paid shear moves the even rank by at most one')
        need(trace == [n] + [n - max(0, k - 1) for k in range(1, s + 1)], name + ': trace n, n, n-1, ..., 0')
        need(all(not any(row) for row in out_even), name + ': all outputs have zero even part in the image')
        receipts[str(theta)] = {'even_rank_trace': trace, 'stage_values_sha256':
                                sha256(','.join(map(str, r)).encode()).hexdigest()}
    return {'path': path, 'events': len(word['physical_events']), 'thick': thick, 'thin': thin,
            'paid_shears': s, 'odd_outputs': odd, 'bound_s_minus_1': s - 1, 'row_stage_lifts': cnt['lifts'],
            'output_stage_mass': stage_mass, 'net_q_power': cnt['qpower'], 'targets_rank_sum': targets,
            'paid_lifts_rank': D * cnt['lifts'], 'income': income, 'image_receipts': receipts}


def main():
    pinned = authenticate()
    result = {'audited_pr': 6114, 'audited_head': '3183c6553e5559df8807fde4fec27e2403f3040a',
              'pinned_inputs': pinned, 'controllers': {}}
    for name, path in CONTROLLERS.items():
        result['controllers'][name] = audit_controller(name, path)
    c1 = A.laurent_entry_control()
    need(c1['entry_even_rank'] == 2 and c1['exceeds_constant_entry_bound'], 'Laurent-entry control twists 2 with 2 shears')
    c2 = A.odd_translation_control()
    need(c2['odd_rows'] == 1 and c2['final_even_rank'] == 1, 'paid odd translation twists 1 with 1 job')
    c3 = A.two_row_job_control()
    need(c3['odd_rows'] == 2 and c3['even_rank_before'] - c3['even_rank_after'] == 2, 'two-row job drops rank by 2')
    rnd = [A.one_destination_random('s46-%d-%d' % (n, k), w, n, ln) for n, k, w, ln in ((2, 0, 400, 6), (4, 1, 300, 10), (6, 2, 100, 24))]
    need(all(r['max_excess_over_bound'] <= 0 for r in rnd), 'one-destination generalization')
    result['scope_controls'] = {'laurent_entry_boundary': c1, 'paid_odd_translation': c2, 'two_row_paid_job': c3,
                                'one_destination_random': rnd}
    text = json.dumps(result, indent=1, sort_keys=True) + '\n'
    target = HERE / 'RESULT.json'
    if '--write' in sys.argv:
        target.write_text(text)
    else:
        need(target.read_text() == text, 'RESULT.json matches the recomputed audit')
    for name, c in result['controllers'].items():
        print('%-27s thick=%d thin=%d shears=%d odd=%d income=%d (=thick-1)' % (
            name, c['thick'], c['thin'], c['paid_shears'], c['odd_outputs'], c['income']))
    print('controls: Laurent entry 2 odd / 2 shears; paid Q 1 odd / 1 job; two-row job 2 odd / 1 job;',
          'one-destination random words %d paid jobs within bound' % sum(r['paid_jobs_total'] for r in rnd))
    print('PASS p104-controller-income-audit')


if __name__ == '__main__':
    main()
