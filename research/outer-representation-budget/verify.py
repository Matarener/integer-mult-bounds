#!/usr/bin/env python3
"""Exact outer region for prescribed precision/stock envelopes.

zxv, with substantial OpenAI Codex assistance. Apache-2.0.
Unchanged ledger: zxv PR4359. Unpenalized region: Nick Petalas PR5984.
Arithmetic evidence only; no supplier admission or new kappa.
"""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import json
import random
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CAP, ATOM = F(1, 32), F(1, 250)
LEDGER = 'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'


def need(value, message):
    if not value:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    pins = {}
    for row in manifest['files']:
        if row['usage'] == 'input':
            raw = (ROOT/row['path']).read_bytes()
            need(sha256(raw).hexdigest() == row['sha256'], 'Source changed: '+row['path'])
            pins[row['path']] = row['sha256']
    # Direct compilation avoids a preexisting bytecode import.
    module = types.ModuleType('pinned_outer_ledger')
    module.__file__ = str(ROOT/LEDGER)
    exec(compile((ROOT/LEDGER).read_bytes(), module.__file__, 'exec'), module.__dict__)
    pricing = (ROOT/'research/p104-helper470-twin-rung-removal/pricing.py').read_text()
    need('outer_module.ledger(params)' in pricing, 'Selected ledger call')
    need("params['beta']*(1-atom)" in pricing, 'Fourth selected functional check')
    return module, pins


def source_values(module, p):
    out = module.ledger(p)
    need(len(out['strict_checks']) == 54 and len(out['functional_checks']) == 3,
         'Pinned 54+3 inventory')
    need(len(out['margins']) == 9, 'Nine actual outer rows')
    values = dict(out['strict_checks'], **out['functional_checks'])
    values['actual_new_BIT_stock_sublinear'] = p['beta']*(1-ATOM)
    return out, values


def evaluate(module, p, rho, nu, zeta, cutoff):
    """Retain every original predicate, charge fallback, append five checks."""
    out, values = source_values(module, p)
    s = zeta/(1-nu)
    margins = dict(out['margins'])
    margins['group_scans'] -= cutoff
    values['group_scans_above_kappa'] = margins['group_scans']-p['kappa']
    values.update(representation_global_guard=1-rho*p['epsilon'],
                  representation_group_guard=1-rho*p['beta'],
                  representation_total_stock=p['beta']*(1-nu)-zeta,
                  cutoff_above_stock_boundary=cutoff-s,
                  cutoff_below_group=p['beta']-cutoff)
    need(len(values) == 63, 'All 58 inherited and five representation checks')
    return values, margins


def region(module, U, B, kappa, rho, nu, zeta):
    need(rho >= 1 and 0 <= nu < 1 and zeta >= 0 and U > 0 and B > 0,
         'Declared envelope domain')
    M, R, s = min(U, B, CAP), 1/rho, zeta/(1-nu)
    return s < 2*R-1 and module.OLD_BASELINE < kappa < min(M*R, R-s)


def witness(U, B, kappa, rho, nu, zeta):
    M, R, s = min(U, B, CAP), 1/rho, zeta/(1-nu)
    lower = max(kappa/M, kappa+s, (1+s)/2)
    need(lower < R, 'Witness needs strict representation room')
    eps = (lower+R)/2
    q = (kappa/eps+M)/2
    a, b = (2*q+M)/3, (q+2*M)/3
    eta = min((2*eps-1-s)/2, (eps-s-kappa)/2, (1-eps)/2)
    beta = 2*eps-1-eta
    h = min((eps-F(1, 2))/2, F(1, 64))
    p = dict(kappa=kappa, complex_uniform_saving=U, bit_saving=B,
             q=q, a=a, b=b, epsilon=eps, beta=beta,
             stop=(b-a)/(2*b), r0=(1-rho*eps)/4,
             layout=F(3, 32)-eps*q-h)
    gap = 1-eps+beta-s-kappa
    delta = min(beta-s, gap, eps-s-kappa)/4
    need(delta > 0, 'Strict cutoff absorbs fixed polylogarithms')
    return p, s+delta


def independent_rows(p, cutoff):
    eps, beta, q, a = (p[x] for x in ('epsilon', 'beta', 'q', 'a'))
    xi = eps*(1+q)-F(3, 32)+p['layout']
    return dict(main_transform=eps*q, global_coordinate_router=a,
                fused_gaussian=1-eps+q*beta, group_bit_router=1-eps+a*beta,
                group_scans=1-eps+beta-cutoff,
                boundary_algebraic_matrix=F(3, 32)+xi-eps,
                sparse_union_movement=xi+F(1, 2)-eps,
                polynomial_products=eps, microbox_face_corrections=79-eps-beta)


def positive(values):
    return all(x > 0 for x in values.values())


def certificate_identities(values, p, rho, nu, zeta):
    """Nonnegative-weight obstruction identities; no solver inference."""
    R, s = 1/rho, zeta/(1-nu)
    fit = (values['representation_global_guard']/rho
           + (values['membership_arithmetic_fits_record']
              + values['cutoff_below_group']
              + values['cutoff_above_stock_boundary'])/2)
    paid = (values['representation_global_guard']/rho
            + values['membership_arithmetic_fits_record']
            + values['group_scans_above_kappa']
            + values['cutoff_above_stock_boundary'])
    need(fit == R-(1+s)/2, 'Stock/geometry dual identity')
    need(paid == R-s-p['kappa'], 'Paid fallback dual identity')


def run():
    module, pins = authenticate()
    rng = random.Random(6056)
    count = excluded = 0
    grid = [F('.0034'), F('.011'), F('.02'), CAP, F('.05')]
    rhos = [F(1), F(5, 4), F(3, 2), F(7, 4), F(199, 100), F(2), F(5, 2)]
    nus = [F(0), ATOM, F(1, 2), F(9, 10)]
    ss = [F(0), F('.001'), F('.05'), F('.25'), F('.5'), F('.98'), F('.995')]
    for U in grid:
        for B in grid:
            for rho in rhos:
                for nu in nus:
                    for s in ss:
                        zeta = s*(1-nu)
                        M, R = min(U, B, CAP), 1/rho
                        top = min(M*R, R-s)
                        if s >= 2*R-1 or top <= module.OLD_BASELINE:
                            excluded += 1
                            continue
                        for kappa in ((module.OLD_BASELINE+top)/2, top-F(1, 10**24)):
                            need(region(module, U, B, kappa, rho, nu, zeta), 'Predicted interior')
                            p, cutoff = witness(U, B, kappa, rho, nu, zeta)
                            values, margins = evaluate(module, p, rho, nu, zeta, cutoff)
                            need(positive(values), 'Every source and changed predicate passes')
                            need(margins == independent_rows(p, cutoff), 'All nine formulas')
                            need(p['epsilon']-cutoff > kappa, 'Full-width residual also paid')
                            certificate_identities(values, p, rho, nu, zeta)
                            count += 1
                        need(not region(module, U, B, top, rho, nu, zeta), 'Supremum excluded')

    # False positive when stock fit is checked but fallback is free.
    U = B = F('.02')
    kappa, rho, nu, zeta = F('.011'), F(1), F(1, 2), F('.4975')
    d = (min(U, B, CAP)-kappa)/7
    p = dict(kappa=kappa, complex_uniform_saving=U, bit_saving=B,
             q=kappa+3*d, a=kappa+4*d, b=kappa+5*d,
             epsilon=1-d, beta=1-3*d, r0=d/10, stop=d, layout=d)
    _, old = source_values(module, p)
    need(positive(old), 'False-positive control passes all original 58 predicates')
    cutoff = F('.995001')
    values, margins = evaluate(module, p, rho, nu, zeta, cutoff)
    failures = sorted(k for k, v in values.items() if v <= 0)
    need(failures == ['group_scans_above_kappa'], 'Only paid fallback rejects')
    certificate_identities(values, p, rho, nu, zeta)
    need(not region(module, U, B, kappa, rho, nu, zeta), 'Exact .005 supremum excludes .011')

    # Corroborate both dual identities on arbitrary rational parameters.
    for _ in range(300):
        p0 = {key: F(rng.randint(-200, 200), rng.randint(1, 1000)) for key in
              ('kappa', 'complex_uniform_saving', 'bit_saving', 'q', 'a', 'b',
               'epsilon', 'beta', 'r0', 'stop', 'layout')}
        rho0, nu0 = F(rng.randint(100, 300), 100), F(rng.randint(0, 90), 100)
        zeta0, cut0 = F(rng.randint(0, 50), 100), F(rng.randint(0, 100), 100)
        vv, _ = evaluate(module, p0, rho0, nu0, zeta0, cut0)
        certificate_identities(vv, p0, rho0, nu0, zeta0)

    # Calibration of the strict recovery radius, not a Gaussian replay.
    for integer in range(-8, 9):
        lo, hi = F(integer)-F(499, 1000), F(integer)+F(499, 1000)
        need((lo+F(1, 2)).__floor__() == integer
             and (hi+F(1, 2)).__floor__() == integer, 'Nearest integer recovery')
    need(F(1, 2)-0 == 1-F(1, 2), 'Half-unit ambiguity')

    selected = json.loads((ROOT/'certificates/frontier6030/CLAIM.json').read_text())
    selected_U = next(F(t['saving']) for t in selected['uniform_templates'] if t['family'] == 'complex')
    selected_B = F(selected['admitted_BIT_saving'])
    examples = []
    for label, U0, B0, rho0, nu0, zeta0, k0 in [
            ('hypothetical_linear_pass', F('.012'), F('.012'), F(1), ATOM, F(0), F('.011')),
            ('hypothetical_superlinear_pass', F('.02'), F('.02'), F(3, 2), F(1, 2), F('.05'), F('.011'))]:
        pp, tt = witness(U0, B0, k0, rho0, nu0, zeta0)
        vv, mm = evaluate(module, pp, rho0, nu0, zeta0, tt)
        need(positive(vv), 'Explicit target-scale example')
        examples.append(dict(label=label, kappa=str(k0), rho=str(rho0), nu=str(nu0),
                             zeta=str(zeta0), parameters={k:str(v) for k,v in pp.items()},
                             cutoff=str(tt), margins={k:str(v) for k,v in mm.items()},
                             minimum_strict_slack=str(min(vv.values()))))
    return dict(status='PASS_OUTER_REPRESENTATION_BUDGET', source_sha256=pins,
                inherited_predicates=58, representation_predicates=5, total_predicates=63,
                witnesses=count, excluded_grid_families=excluded,
                dual_identity_checks=300, exact_supremum='min(M/rho, 1/rho-s)',
                geometry_condition='rho*(1+s)<2',
                selected_U=str(selected_U), selected_B=str(selected_B),
                selected_target_001_supported=region(module, selected_U, selected_B, F('.01'), F(1), ATOM, F(0)),
                free_fallback_false_positive=dict(original_predicates_pass=58,
                    stock_fit_slack=str(values['representation_total_stock']),
                    charged_fallback_saving=str(margins['group_scans']),
                    required_kappa=str(kappa), failures=failures, exact_supremum='1/200'),
                examples=examples,
                scope='Written scoped proof plus exact arithmetic corroboration. Hypothetical contracts only; no implemented supplier, new kappa or framework assumption discharge.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((HERE/'RESULT.json').read_text())
        need(result == expected, 'Receipt differs; review before regenerating')
        print(result['status'], 'witnesses='+str(result['witnesses']),
              'predicates=63 dual_checks=300 RECEIPT_MATCH no_new_kappa')


if __name__ == '__main__':
    main()
