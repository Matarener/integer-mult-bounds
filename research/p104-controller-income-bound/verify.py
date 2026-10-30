#!/usr/bin/env python3
"""Verify the controller income bound: twisted outputs <= paid odd shears - 1.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.
Checks: (0) pinned inputs; (1) on the three retained p16 controllers (PR5398 direct controller, the joint-helper
lattice source and the p104 productive all-forward controller) the even-part rank trace is 32, 32, 31, ..., 0 over
the 33 paid shears for two values of the central square: free operations never change it, every paid shear changes
it by at most one, the first paid shear leaves it unchanged, and all 32 declared diagonal outputs are odd monomials,
so the bound 32 <= 33 - 1 is attained with equality; (2) the per-port controller income computed from the literal
word (target ranks minus paid lifts and thin requests) equals outputs minus thin requests = 17 = thick calls - 1
on all three, with the lift cancellation checked stage by stage (#outputs containing D_s = row-lifts at s, 194 in
all; sum of output Q-exponents = net Q_POWER) and the rank of the left boundary recorded; (3) controls: the two-bank Whitehead word with three odd shears reaches diag(Q, Q^-1) with trace
2, 2, 1, 0; its two-shear prefix leaves one bank with an even part (no diagonal); dropping the last QUERY_SHEAR of the p104
controller leaves a positive even rank and non-twisted outputs; a word that applies Q^{+-1} for free is rejected by the
alphabet; (4) RESULT.json equals the recomputed receipt.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util, json, sys, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTROLLERS = {
    'pr5398_direct': 'research/kappa-backward-controller-20261023/CONTROLLER.json',
    'joint_helper_lattice': 'research/joint-helper-lattice/CONTROLLER.json',
    'p104_productive': 'research/p104-productive-controller/CONTROLLER.json',
}
THETAS = ['7/3', '11/5']


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


def expect_failure(fn, text):
    try:
        fn()
    except ValueError as ex:
        need(text in str(ex), 'expected rejection "%s", got "%s"' % (text, ex))
        return str(ex)
    raise ValueError('control accepted: ' + text)


def main():
    t0 = time.time()
    B = load('p104_income_bound', HERE/'incomebound.py')
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin ' + row['path'])
    print('pins ok', flush=True)
    result = {'controllers': {}, 'controls': {}}
    for name, rel in CONTROLLERS.items():
        word = B.read(ROOT/rel)
        n = 2 * word['pairs']
        receipts = {}
        for theta in THETAS:
            r = B.trace(word['physical_events'], n, Q(theta), word['boundaries'], word['diagonal'])
            r.pop('final_banks')
            need(r['paid_shears'] == 33 and r['thick'] == 18 and r['thin'] == 15, name + ': 18 thick and 15 thin shears')
            need(r['even_rank_trace'] == [32, 32] + list(range(31, -1, -1)), name + ' theta ' + theta + ': rank trace 32,32,31,...,0')
            need(r['twisted_outputs'] == 32 and r['even_zero_outputs'] == 32, name + ': all 32 outputs twisted')
            need(r['bound_satisfied'] and r['twisted_outputs'] == r['paid_shears'] - 1, name + ': bound attained with equality')
            receipts[theta] = r
        inc = B.income(word)
        need(inc['income'] == inc['outputs_minus_thin'] == 17 == receipts[THETAS[0]]['thick'] - 1, name + ': income 17 = thick - 1')
        need(inc['row_lifts_total'] == 194 and inc['left_boundary_rank'] == n, name + ': 194 row-lifts, invertible left boundary')
        result['controllers'][name] = {'path': rel, 'events': len(word['physical_events']), 'receipts': receipts, 'income': inc}
        print(name, 'events', len(word['physical_events']), 'paid shears', receipts[THETAS[0]]['paid_shears'],
              'twisted', receipts[THETAS[0]]['twisted_outputs'], 'income/port', inc['income'], flush=True)
    # controls
    # (a) Whitehead word on one pair: y += Q^-1 x ; x += -Q y ; y += Q^-1 x  (forward, backward, forward LOCAL-free
    #     thin shears), then free ops; the even parts vanish after three shears, not after two
    white = [['QUERY_SHEAR', 0, 0, False], ['QUERY_SHEAR', 1, 0, True], ['QUERY_SHEAR', 2, 0, False]]
    r = B.trace(white, 2, Q(THETAS[0]))
    need(r['even_rank_trace'] == [2, 2, 1, 0] and r['even_zero_outputs'] == 2 and r['bound_satisfied'], 'Whitehead three shears')
    result['controls']['whitehead_three_shears'] = {'trace': r['even_rank_trace'], 'twisted': r['twisted_outputs'],
                                                     'even_zero': r['even_zero_outputs'], 'final': r['final_banks']}
    r2 = B.trace(white[:2], 2, Q(THETAS[0]))
    need(r2['even_rank_trace'] == [2, 2, 1] and r2['even_zero_outputs'] == 1, 'two shears leave an even part')
    result['controls']['whitehead_two_shears'] = {'trace': r2['even_rank_trace'], 'even_zero': r2['even_zero_outputs']}
    # (b) drop the last thin shear of the p104 controller: rank 1 remains and the declared diagonal fails
    word = B.read(ROOT/CONTROLLERS['p104_productive'])
    cut = deepcopy(word)
    last = max(i for i, e in enumerate(cut['physical_events']) if e[0] == 'QUERY_SHEAR')
    cut['physical_events'].pop(last)
    msg = expect_failure(lambda: B.trace(cut['physical_events'], 32, Q(THETAS[0]), cut['boundaries'], cut['diagonal']), 'declared diagonal output')
    r3 = B.trace(cut['physical_events'], 32, Q(THETAS[0]), cut['boundaries'])
    need(r3['paid_shears'] == 32 and r3['final_even_rank'] >= 1 and r3['even_zero_outputs'] <= 31, 'one shear fewer leaves a positive even rank')
    result['controls']['drop_last_thin_shear'] = {'removed_event_index': last, 'paid_shears': 32, 'final_even_rank': r3['final_even_rank'],
                                                  'even_zero_outputs': r3['even_zero_outputs'], 'rejection': msg}
    # (c) a free odd central power is outside the alphabet
    bad = deepcopy(word)
    bad['physical_events'].insert(0, ['Q_POWER', 0, 1])
    msg = expect_failure(lambda: B.trace(bad['physical_events'], 32, Q(THETAS[0]), bad['boundaries'], bad['diagonal']), 'only even central powers are free')
    result['controls']['free_odd_power_rejected'] = msg
    print('controls ok', flush=True)
    result['summary'] = {'bound': 'twisted outputs <= paid odd shears - 1', 'attained_by': 'all three p16 controllers (32 <= 33 - 1)',
                         'income_per_port': 17, 'income_bound_per_port': 'thick calls - 1',
                         'mass_surplus_formula': 'M = v*income - calls*centre <= calls*(v - centre) - v',
                         'pr5907': {'v': 104, 'calls': 18, 'centre': 56, 'M': 18 * 48 - 104}}
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=1, sort_keys=True) + '\n')
    need(json.loads((HERE/'RESULT.json').read_text()) == result, 'RESULT.json equals the recomputed receipt')
    print('PASS_P104_CONTROLLER_INCOME_BOUND %.1fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
