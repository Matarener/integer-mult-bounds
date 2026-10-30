#!/usr/bin/env python3
"""Verify the per-port floor of fifteen rank-one requests for the thin QUERY_SHEAR stages.  Apache-2.0.

Prepared for Matarener with Claude (Anthropic), via Claude Code.  Python 3.12, standard library only.
Checks: (0) pinned inputs; (1) on the three retained p16 controllers (PR5398 direct controller, the joint-helper
lattice source and the p104 productive all-forward controller) the fifteen shear results are linearly independent
modulo everything free, for two values of the central square, so at least fifteen rank-one requests per port are
needed, and each result is independent of the free span plus the other fourteen; (2) the greedy causal realization
uses exactly fifteen; (3) controls: a redundant sixteenth shear (the output of the last full call) is recognised as free (floor stays fifteen), the
flawed model that treats present contents as free collapses to 0, and declaring odd central powers free collapses
to 0; (4) RESULT.json equals the recomputed receipt.
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


def main():
    t0 = time.time()
    P = load('p104_port_floor', HERE/'portfloor.py')
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source pin ' + row['path'])
    print('pins ok', flush=True)
    result = {'controllers': {}, 'controls': {}}
    for name, rel in CONTROLLERS.items():
        word = P.read(ROOT/rel)
        receipts = {}
        for theta in THETAS:
            r = P.analyse(word, Q(theta))
            need(r['query_shears'] == 15 and r['locals'] == 18, name + ': 15 thin stages and 18 full calls')
            need(r['floor'] == 15, name + ' theta ' + theta + ': floor 15')
            need(r['greedy_queries'] == 15 and all(row[3] == 'query' for row in r['greedy_log']), name + ': greedy 15')
            need(r['independent_of_all_others'] == [1] * 15, name + ': every result independent of the other fourteen')
            receipts[theta] = r
        need(receipts[THETAS[0]]['greedy_log'] == receipts[THETAS[1]]['greedy_log'], name + ': same stages')
        result['controllers'][name] = {'path': rel, 'events': receipts[THETAS[0]]['events'],
                                       'stages': [row[1] for row in receipts[THETAS[0]]['greedy_log']],
                                       'receipts': receipts}
        print(name, 'events', receipts[THETAS[0]]['events'], 'dim free', receipts[THETAS[0]]['dim_free'],
              'dim free+needs', receipts[THETAS[0]]['dim_free_plus_needs'], 'floor', receipts[THETAS[0]]['floor'],
              'greedy', receipts[THETAS[0]]['greedy_queries'], flush=True)
    # controls on the productive controller
    word = P.read(ROOT/CONTROLLERS['p104_productive'])
    # a sixteenth shear appended after the last full call, on that call's pair and orientation: its result
    # Q^{-1} x is exactly the paid output of that call, so the model must recognise it as free
    dup = deepcopy(word)
    last = [e for e in dup['physical_events'] if e[0] == 'LOCAL'][-1]
    dup['physical_events'].append(['QUERY_SHEAR'] + last[1:])
    r = P.analyse(dup, Q(THETAS[0]))
    need(r['query_shears'] == 16 and r['floor'] == 15 and r['greedy_queries'] == 15 and r['greedy_log'][-1][3] == 'free'
         and r['independent_of_all_others'] == [1] * 15 + [0], 'redundant sixteenth shear is free')
    result['controls']['redundant_sixteenth_shear'] = {'inserted': ['QUERY_SHEAR'] + last[1:], 'query_shears': 16,
                                                       'floor': r['floor'], 'greedy_queries': r['greedy_queries'],
                                                       'independent_of_all_others': r['independent_of_all_others']}
    r = P.analyse(word, Q(THETAS[0]), contents_free=True)
    need(r['floor'] == 0, 'flawed contents-free model collapses')
    result['controls']['contents_free_model'] = {'dim_free': r['dim_free'], 'floor': r['floor']}
    r = P.analyse(word, Q(THETAS[0]), free_odd=True)
    need(r['floor'] == 0 and r['greedy_queries'] == 0, 'odd central powers free collapses')
    result['controls']['odd_powers_free'] = {'dim_free': r['dim_free'], 'floor': r['floor'], 'greedy_queries': r['greedy_queries']}
    print('controls', result['controls'], flush=True)
    result['summary'] = {'floor_per_port': 15, 'thin_stages': 15,
                         'ports': {'pr5398_direct': 112, 'p104_productive': 104},
                         'minimum_requests': {'pr5398_direct': 15 * 112, 'p104_productive': 15 * 104},
                         'atlas_P8_target': 528}
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(json.dumps(result, indent=1, sort_keys=True) + '\n')
    need(json.loads((HERE/'RESULT.json').read_text()) == result, 'RESULT.json equals the recomputed receipt')
    print('PASS_P104_THIN_QUERY_PORT_FLOOR %.1fs' % (time.time() - t0))


if __name__ == '__main__':
    main()
