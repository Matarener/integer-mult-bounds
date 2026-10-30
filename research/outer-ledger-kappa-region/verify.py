#!/usr/bin/env python3
"""Exact kappa region of the selected outer transfer ledger.

Nick Petalas. Apache-2.0. The ledger is zxv's PR4359 outer parameter ledger as
recomputed in research/pr4359-p7-padding endpoint.py and called by the selected
research/p104-helper-subspace-splits/pricing.py; it is loaded unchanged.

Claim checked: for supplier savings U (complex uniform) and B (admitted BIT),
some choice of the free parameters makes all 54 strict and 4 functional checks
positive iff OLD_BASELINE < kappa < min(U, B, 1/32). PROOF.md gives the proof;
this script binds every named check used by the proof to the loaded ledger,
evaluates the explicit witness, and runs failure controls.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import random
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEDGER = ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'
PRICING = ROOT/'research/p104-helper-subspace-splits/pricing.py'
CLAIM = ROOT/'certificates/frontier5599/CLAIM.json'
CAP = Q(1, 32)
ATOM = Q(1, 250)
FREE = ('b', 'a', 'q', 'epsilon', 'beta', 'r0', 'stop', 'layout')
# Checks used by the necessity chain, with their closed forms.
CHAIN = {
    'improvement_over_user_baseline': lambda p, old: p['kappa']-old,
    'main_transform_above_kappa': lambda p, old: p['epsilon']*p['q']-p['kappa'],
    'epsilon_below_one': lambda p, old: 1-p['epsilon'],
    'q_positive': lambda p, old: p['q'],
    'q_below_effective': lambda p, old: p['a']-p['q'],
    'actual_bit_above_effective': lambda p, old: p['bit_saving']-p['a'],
    'complex_above_effective': lambda p, old: p['b']-p['a'],
    'new_complex_uniform_saving_above_b': lambda p, old: p['complex_uniform_saving']-p['b'],
    'complex_below_one_over_32': lambda p, old: CAP-p['b'],
}


def need(value, message):
    if not value:
        raise AssertionError(message)


def load_ledger():
    spec = importlib.util.spec_from_file_location('selected_outer_ledger', LEDGER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(module, p):
    out = module.ledger(p)
    values = dict(out['strict_checks'])
    values.update(out['functional_checks'])
    values['actual_new_BIT_stock_sublinear'] = p['beta']*(1-ATOM)
    return values


def feasible_predicted(old, U, B, kappa):
    return old < kappa < min(U, B, CAP)


def witness(U, B, kappa):
    """The PR4359 family shape with d=(min(U,B,1/32)-kappa)/7."""
    d = (min(U, B, CAP)-kappa)/7
    return {'kappa': kappa, 'complex_uniform_saving': U, 'bit_saving': B,
            'b': kappa+5*d, 'a': kappa+4*d, 'q': kappa+3*d,
            'epsilon': 1-d, 'beta': 1-3*d, 'r0': d/10, 'stop': d, 'layout': d}


def all_positive(values):
    return all(v > 0 for v in values.values())


def check_inventory(module):
    probe = witness(Q('.004'), Q('.005'), Q('.003'))
    values = evaluate(module, probe)
    need(len(values) == 58, 'Inventory: 54 strict plus 4 functional checks')
    out = module.ledger(probe)
    need(len(out['strict_checks']) == 54 and len(out['functional_checks']) == 3,
         'Ledger supplies 54 strict and 3 functional; pricing.py adds the fourth')
    need(set(probe) == set(FREE)|{'kappa', 'complex_uniform_saving', 'bit_saving'},
         'Witness sets exactly the ledger inputs')
    text = PRICING.read_text()
    need('outer_module.ledger(params)' in text and "'p104_productive_outer'" in text,
         'Selected pricing calls this ledger')
    need("params['beta']*(1-atom)" in text, 'Selected fourth functional check')
    return values


def check_chain_bindings(module, rng):
    """Each chain check equals its closed form on random exact inputs."""
    old = module.OLD_BASELINE
    for _ in range(400):
        p = {k: Q(rng.randint(-50, 2000), rng.randint(1, 4000)) for k in FREE}
        p.update(kappa=Q(rng.randint(1, 900), 10**5),
                 complex_uniform_saving=Q(rng.randint(1, 900), 10**5),
                 bit_saving=Q(rng.randint(1, 900), 10**5))
        values = evaluate(module, p)
        for name, form in CHAIN.items():
            need(values[name] == form(p, old), 'Chain binding '+name)
    return len(CHAIN)


def check_witnesses(module, rng):
    old = module.OLD_BASELINE
    count = 0
    grid = [Q('.0025'), Q('.0031'), Q('.0034'), Q('.01'), Q('.02'), Q('.03'),
            Q(1, 32), Q('.05'), Q('.2')]
    for U in grid:
        for B in grid:
            top = min(U, B, CAP)
            for kappa in (old+Q(1, 10**30), (old+top)/2, top-Q(1, 10**30)):
                if not feasible_predicted(old, U, B, kappa):
                    continue
                need(all_positive(evaluate(module, witness(U, B, kappa))),
                     'Witness passes every check')
                count += 1
    for _ in range(300):
        U = Q(rng.randint(1, 10**6), 10**7)
        B = Q(rng.randint(1, 10**6), 10**7)
        top = min(U, B, CAP)
        if top <= old:
            continue
        kappa = old+(top-old)*Q(rng.randint(1, 10**6-1), 10**6)
        need(all_positive(evaluate(module, witness(U, B, kappa))), 'Random witness')
        count += 1
    return count


def check_necessity_samples(module, rng):
    """Random feasible points never exceed the predicted region."""
    old = module.OLD_BASELINE
    hits = 0
    for _ in range(4000):
        U = Q(rng.randint(1, 4*10**5), 10**7)
        B = Q(rng.randint(1, 4*10**5), 10**7)
        top = min(U, B, CAP)
        kappa = Q(rng.randint(1, 4*10**5), 10**7)
        base = witness(max(U, kappa*2), max(B, kappa*2), kappa)
        p = {k: base[k]*(1+Q(rng.randint(-20, 20), 1000)) for k in FREE}
        p.update(kappa=kappa, complex_uniform_saving=U, bit_saving=B)
        if all_positive(evaluate(module, p)):
            need(old < kappa < top, 'Feasible point inside region')
            hits += 1
    need(hits > 0, 'Necessity sampling found feasible points')
    return hits


def check_controls(module):
    old = module.OLD_BASELINE
    U, B = Q('.02'), Q('.012')
    rows = {}
    for name, kappa in (('kappa_equals_BIT', B), ('kappa_at_baseline', old)):
        p = witness(U, B, kappa) if kappa < B else witness(U, B+Q(1, 10**9), kappa)
        p['bit_saving'] = B
        rows[name] = sorted(k for k, v in evaluate(module, p).items() if v <= 0)
    need('actual_bit_above_effective' in rows['kappa_equals_BIT'], 'BIT boundary rejects')
    need(rows['kappa_at_baseline'] == ['improvement_over_user_baseline'], 'Baseline rejects')
    p = witness(Q('.04'), Q('.04'), Q('.03'))
    p['b'] = Q('.0313')
    p['complex_uniform_saving'] = Q('.04')
    rows['b_above_one_over_32'] = sorted(k for k, v in evaluate(module, p).items() if v <= 0)
    need('complex_below_one_over_32' in rows['b_above_one_over_32'], '1/32 row rejects')
    p = witness(Q('.004'), Q('.005'), Q('.003'))
    p['epsilon'] = 1+Q(1, 10**6)
    rows['epsilon_one_or_more'] = sorted(k for k, v in evaluate(module, p).items() if v <= 0)
    need('epsilon_below_one' in rows['epsilon_one_or_more'], 'epsilon row rejects')
    # Old PR4359 control: BIT .0027 fails at the selected kappa.
    claim = json.loads(CLAIM.read_text())
    kappa = Q(claim['kappa'])
    U = {t['family']: Q(t['saving']) for t in claim['uniform_templates']}['complex']
    rows['selected_kappa_BIT_0027'] = 'kappa >= B, so actual_bit_above_effective fails'
    need(not feasible_predicted(old, U, Q('.0027'), kappa), 'Old .0027 control excluded')
    return rows


def selected_corollary(module):
    claim = json.loads(CLAIM.read_text())
    kappa = Q(claim['kappa'])
    templates = {t['family']: Q(t['saving']) for t in claim['uniform_templates']}
    U = templates['complex']
    B = Q(claim['admitted_BIT_saving'])
    top = min(U, B, CAP)
    need(top == U, 'Complex supplier binds the selected ledger')
    need(feasible_predicted(module.OLD_BASELINE, U, B, kappa), 'Selected kappa inside region')
    need(all_positive(evaluate(module, witness(U, B, kappa))), 'Selected witness')
    need(module.OLD_BASELINE < B, 'Admitted BIT above baseline')
    return {'U_complex_uniform': U, 'B_admitted_BIT': B, 'kappa_selected': kappa,
            'ledger_supremum': top, 'selected_gap_to_supremum': top-kappa,
            'BIT_headroom_over_selected_kappa': B-kappa,
            'BIT_threshold_at_selected_kappa': 'any B > kappa'}


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, list):
        return [encode(v) for v in value]
    return value


def main():
    module = load_ledger()
    rng = random.Random(20261027)
    check_inventory(module)
    result = {
        'theorem': 'feasible iff OLD_BASELINE < kappa < min(U, B, 1/32)',
        'OLD_BASELINE': module.OLD_BASELINE,
        'checks_total': 58,
        'chain_checks_bound': check_chain_bindings(module, rng),
        'witnesses_passed': check_witnesses(module, rng),
        'random_feasible_points_inside_region': check_necessity_samples(module, rng),
        'controls': check_controls(module),
        'selected': selected_corollary(module),
    }
    digest = sha256()
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.suffix in {'.py', '.md', '.json'}:
            digest.update(path.name.encode()+b'\0'+path.read_bytes())
    print('RESULT '+json.dumps(encode(result), sort_keys=True))
    print('PACKAGE_SHA256 '+digest.hexdigest())
    print('PASS_OUTER_LEDGER_KAPPA_REGION')


if __name__ == '__main__':
    main()
