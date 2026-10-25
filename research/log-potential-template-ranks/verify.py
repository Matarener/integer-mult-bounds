#!/usr/bin/env python3
"""Exact premises of README.md's logarithmic leaf-count majorant.

Leaf arithmetic is separately implemented. The pinned outer ledger function
is executed as a second arithmetic oracle; this is not native/outer admission.
zxv, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True


def need(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(None)
def log_bounds(n):
    """ln(n): rational 2*atanh series after binary range reduction."""
    need(isinstance(n, int) and n >= 1, 'positive integer logarithm')

    def series(x):
        u = (x-1)/(x+1)
        power, total, count = u, Q(0), 80
        for j in range(count):
            total += 2*power/(2*j+1)
            power *= u*u
        tail = 2*power/((2*count+1)*(1-u*u))
        return total, total+tail

    k = n.bit_length()-1
    a, b = series(Q(2))
    c, d = series(Q(n, 2**k))
    return k*a+c, k*b+d


def exp_bounds(x):
    """Positive Taylor terms with a geometric bound on the omitted tail."""
    need(0 <= x < 1, 'exponential enclosure domain')
    total = term = Q(1)
    count = 48
    for j in range(1, count+1):
        term = term*x/j
        total += term
    following = term*x/(count+1)
    return total, total+following/(1-x/(count+2))


@lru_cache(None)
def rank_power(n, saving):
    a, b = log_bounds(n)
    return Q(n)/exp_bounds(saving*b)[1], Q(n)/exp_bounds(saving*a)[0]


def display(pair):
    scale = 10**30
    low, high = pair
    a = low.numerator*scale//low.denominator
    b = -((-high.numerator*scale)//high.denominator)

    def fixed(v):
        sign = '-' if v < 0 else ''
        s = str(abs(v)).rjust(31, '0')
        return sign+s[:-30]+'.'+s[-30:]

    return {'lower': fixed(a), 'upper': fixed(b)}


def moment_margin(targets, paid, saving):
    signed = Counter(targets)
    signed.subtract(paid)
    low = high = Q(0)
    for n, count in signed.items():
        a, b = rank_power(n, saving)
        low += count*(a if count >= 0 else b)
        high += count*(b if count >= 0 else a)
    return low, high


def eta_power(m, saving, q):
    # eta=(1-saving)*m^(-saving).
    a, b = log_bounds(m)
    return ((1-saving)**q/exp_bounds(q*saving*b)[1],
            (1-saving)**q/exp_bounds(q*saving*a)[0])


def final_test(H, gap, q):
    """(H+1) < 2^(q*gap*H), by exact integer powers."""
    power = q*gap*H
    return (H+1)**power.denominator < 2**power.numerator


def grid_rank(gap, q, step=1000):
    # g(H)=q*gap*H*ln(2)-ln(H+1) has g(0)=0, g'(0)<0, g''>0.
    # It has one positive crossing, so binary search cannot skip a win.
    need(0 < q*gap < 1, 'one positive crossing')
    low, high = 0, 1
    while not final_test(step*high, gap, q):
        low, high = high, high*2
    while high-low > 1:
        mid = (low+high)//2
        if final_test(step*mid, gap, q):
            high = mid
        else:
            low = mid
    return step*high


def profile(raw):
    result = {int(k): v for k, v in raw.items()}
    need(result and all(k >= 1 and isinstance(v, int) and v > 0
                        for k, v in result.items()), 'positive integer histogram')
    return result


def check_case(name, targets, paid, saving, uniform_saving, theta, q, previous, step=1000):
    targets, paid = profile(targets), profile(paid)
    m, kmin, rmax = max(targets), min(targets), max(paid)
    need(1 <= rmax < kmin <= m, 'strict mixed separation')
    need(0 < uniform_saving < saving < 1 and 0 < theta < 1, 'strict exponents')
    need(isinstance(q, int) and q >= 1, 'positive integer q')
    margin = moment_margin(targets, paid, saving)
    need(margin[0] > 0, 'unit t-superpotential')
    a, b = theta.numerator, theta.denominator
    need(rmax**b < kmin**a, 'exit power bound')
    shift_left, shift_right = 2**(b-a)*rmax**b, m**a
    need(shift_left <= shift_right, 'shifted logarithm contraction')
    eta = eta_power(m, saving, q)
    need(eta[0] > theta, 'eta^q > theta')
    base_upper = exp_bounds(q*saving*log_bounds(m)[1])[1]
    need(base_upper < 2, 'ordinary base ranks fit the majorant')
    gap = saving-uniform_saving
    H = grid_rank(gap, q, step)
    need(H >= m.bit_length(), 'winning rank exceeds the base')
    need(final_test(H, gap, q), 'strict final uniform moment')
    need(not final_test(H-step, gap, q), 'previous grid rank fails')
    need(eta_power(m, saving, q+1)[1] < theta, 'q+1 fails this contraction')
    need(previous['targets'] == {str(k): v for k, v in targets.items()}
         and previous['paid'] == {str(k): v for k, v in paid.items()}
         and Q(previous['tested_mixed_saving']) == saving
         and Q(previous['theta_upper']) == theta, 'unchanged predecessor invoice')
    power = q*gap*H
    old_H = previous['N']['H1']
    return {
        'family': name, 'targets': targets, 'paid': paid,
        'tested_mixed_saving': str(saving), 'uniform_saving': str(uniform_saving),
        't': str(1-saving), 'z': str(1-uniform_saving),
        'theta_upper': str(theta), 'logarithm_power': str(Q(1, q)),
        'strict_unit_moment_margin': display(margin),
        'eta_to_q': display(eta),
        'eta_to_q_minus_theta': display((eta[0]-theta, eta[1]-theta)),
        'shift_integer_test': {'left': shift_left, 'right': shift_right},
        'base_m_to_q_saving_upper': display((Q(1), base_upper))['upper'],
        'majorant': 'L(n) <= n^t * (1+log2(n))^(1/q), n>=1; L(0)=0',
        'N': {'encoding': '2^H', 'H': H},
        'final_integer_test': {
            'left_base': H+1, 'left_exponent': power.denominator,
            'right_base': 2, 'right_exponent': power.numerator, 'relation': '<'},
        'previous_H': old_H, 'exponent_reduction_factor': str(Q(old_H, H)),
        'grid_step': step,
        'previous_uniform_saving': previous['uniform_saving'],
        'controls': {'previous_grid_point_fails_final_majorant': True,
                     'q_plus_one_fails_contraction': True},
        'materialized_word': False,
    }


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def authenticate_sources():
    inputs = {}
    for row in read(HERE/'VENDOR.json')['files']:
        need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
             'changed predecessor input: '+row['path'])
        inputs[row['path']] = row['sha256']
    return inputs


def retuned_outer(complex_case, bit_case):
    """Reprice the complete nine-row ledger and all inherited predicates.

    The AST oracle executes only the pinned ledger function and its historic
    comparison constants. Its old m=73 native admission code is never run.
    """
    old = read(HERE/'vendor/OUTER-PARAMETERS.json')
    p = {k: Q(v['rational']) if isinstance(v, dict) and 'rational' in v else v
         for k, v in old['outer']['parameters'].items()}
    conversion = read(HERE/'vendor/BIT-ALLSIZE-PARAMETERS.json')
    atom, old_leaf = Q(conversion['atom_power']), Q(conversion['old_ordinary_saving'])
    bare = Q(bit_case['uniform_saving'])
    cover_gap = Q(conversion['C0_minus_C1'])
    covered = bare-cover_gap
    ordinary = (1-atom)*covered+atom*old_leaf
    p.update(b=Q('0.0023004'), q=Q('0.0023002'),
             effective_saving=Q('0.0023003'), BIT_saving=Q('0.002301'),
             complex_uniform_saving=Q(complex_case['uniform_saving']))
    eps, beta, outer_q, effective = (p[k] for k in
                                    ('epsilon', 'group_beta', 'q', 'effective_saving'))
    p['lambda'] = 1-(outer_q+effective)/2
    p['lambda_prime'] = 1-outer_q
    c = (3-p['Strassen_exponent'])/2
    p['cap_xi'] = eps*(1+outer_q)-c+p['layout_slack']
    xi, target, stop = p['cap_xi'], p['kappa'], p['stop']
    own = {
        'main_transform': eps*outer_q,
        'global_coordinate_router': effective,
        'fused_gaussian': 1-eps+outer_q*beta,
        'group_bit_router': 1-eps+effective*beta,
        'group_scans': 1-eps+beta,
        'boundary_algebraic_matrix': c+xi-eps,
        'sparse_union_movement': xi+Q(1, 2)-eps,
        'polynomial_products': eps,
        'microbox_face_corrections': 1-(eps+beta+p['halo_power']-p['core_power']+2),
    }
    need(all(v > target for v in own.values()), 'retuned nine outer cost rows')
    sigma, tau = 1-p['b'], 1-effective
    internal = tau+(1-stop)*max(sigma-tau, Q(0))
    leaf = sigma+stop*(1-sigma)
    checks = {
        'uniform_complex_above_b': p['complex_uniform_saving']-p['b'],
        'ordinary_BIT_above_admitted': ordinary-p['BIT_saving'],
        'admitted_BIT_above_effective': p['BIT_saving']-effective,
        'selected_complex_above_effective': p['b']-effective,
        'lambda_above_internal': p['lambda']-internal,
        'lambda_above_sigma': p['lambda']-sigma,
        'lambda_prime_above_lambda': p['lambda_prime']-p['lambda'],
        'lambda_prime_above_leaf': p['lambda_prime']-leaf,
        'semantic_main_guard': 1-eps,
        'semantic_group_guard': 1-beta,
        'BIT_row_stock_sublinear': beta*(1-atom),
        'group_below_dimension': eps-beta,
        'global_gamma_spare': 1-eps-p['r0'],
        'fine_prime_group_guard': 1-(2*xi-2)-p['r0']-beta,
        'descriptor_complete_fiber': 1-eps,
        'explicit_metadata_halo': p['core_power']-p['halo_power']-eps-beta-1,
        'membership_record_budget': 1-beta-2*(1-eps),
        'short_record_fallback': eps-effective,
        'BIT_linear_adapter': atom-ordinary,
        'BIT_borrowed_stock': 1-ordinary-atom,
        'BIT_cover_gap': cover_gap,
        'fine_prime_umbrella': 10-(2*p['theta_power']+2+Q(1, 2)),
    }
    need(all(v > 0 for v in checks.values()), 'retuned functional interfaces')
    need(cover_gap == Q(1, 100000), 'unchanged delayed-cover prime bound')
    fallback = (1+cover_gap/4)/(1+cover_gap/2)
    need(fallback == Q(conversion['prime_rule']['complete_moment_upper']),
         'same fully charged cover/fallback moment')
    source = ast.parse((HERE/'vendor/check_ledger.py').read_text())
    function = next(node for node in source.body
                    if isinstance(node, ast.FunctionDef) and node.name == 'ledger')
    constants = [node for node in source.body if isinstance(node, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id.startswith('KAPPA_')
                         for t in node.targets)]
    baseline = Q('0.001730970419199163702738')
    env = {'Q': Q, 'R0': p['r0'], 'ZETA': Q(1, 10**8), 'SLACK': p['layout_slack'],
           'STOP': stop, 'FLOOR': 10**7, 'BACKOFF': Q(1, 10**7),
           'EPS': eps, 'BETA': beta, 'THETA_POWER': Q(p['theta_power']),
           'HALO_POWER': p['halo_power'], 'CORE_POWER': p['core_power'],
           'STRASSEN_TAU': p['Strassen_exponent'],
           'b': p['b'], 'q': outer_q, 'a': effective, 'bit': p['BIT_saving'],
           'online': baseline, 'old': baseline}
    module = ast.fix_missing_locations(ast.Module(body=constants+[function], type_ignores=[]))
    exec(compile(module, 'pinned check_ledger.py:ledger', 'exec'), env)
    oracle = env['ledger']('retuned_kappa_0023_smaller_ranks')
    need(oracle['kappa'] == target == Q('0.0023'), 'same declared kappa after grid/backoff')
    need(oracle['margins'] == own, 'all nine rows match the inherited oracle')
    need(len(oracle['strict_checks']) == 63 and
         all(v > 0 for v in oracle['strict_checks'].values()), 'all 63 inherited predicates')
    controls = {}
    for name, options in (
        ('epsilon_one', {'eps_': Q(1)}),
        ('zero_layout_slack', {'slack': Q(0)}),
        ('group_equals_dimension', {'beta_': eps}),
        ('unfunded_old_per_axis_scan', {'old_scan': True}),
    ):
        invalid = env['ledger']('reject_'+name, **options)
        failed = sorted(k for k, v in invalid['strict_checks'].items() if v <= 0)
        need(failed, 'outer control accepted: '+name)
        controls[name] = failed
    return {
        'parameters': {k: str(v) for k, v in p.items()},
        'nine_cost_savings': {k: str(v) for k, v in own.items()},
        'minimum_saving_minus_kappa': str(min(own.values())-target),
        'functional_gaps': {k: str(v) for k, v in checks.items()},
        'inherited_predicates': {k: str(v) for k, v in oracle['strict_checks'].items()},
        'grid_floor': 10**7, 'grid_backoff': '1/10000000',
        'BIT_before_cover': str(bare), 'BIT_after_cover': str(covered),
        'BIT_ordinary_saving': str(ordinary),
        'BIT_atom_power': str(atom), 'BIT_old_leaf_saving': str(old_leaf),
        'BIT_prime_coefficient': str(256/cover_gap),
        'BIT_fallback_moment_upper': str(fallback), 'rejected_controls': controls,
        'scope': 'Exact parameter compatibility under the pinned native/cover/support/outer hypotheses; not a fresh native admission or full replay.',
    }


def verify():
    sources = authenticate_sources()
    old = read(HERE/'vendor/EXPLICIT-TEMPLATE-BOUNDS.json')['cases']
    cover = read(HERE/'vendor/P3-NATIVE-COVER.json.gz')['cover']
    bit = next(row for row in read(HERE/'vendor/MIXED-PRODUCTIVE-BIT.json')['candidates']
               if row['pairs'] == 3 and row['keep_idle_mask'] == 43)
    args = [
        ('complex/same-savings', cover['targets'], cover['paid'], Q('0.002305'), Q('0.002304'), Q(9, 10), 9, old[0]),
        ('BIT/same-savings', bit['targets'], bit['paid'], Q('0.002769'), Q('0.002760'), Q(15, 16), 4, old[1]),
        ('complex/kappa-0023', cover['targets'], cover['paid'], Q('0.002305'), Q('0.0023005'), Q(9, 10), 9, old[0]),
        ('BIT/kappa-0023', bit['targets'], bit['paid'], Q('0.002769'), Q('0.002318'), Q(15, 16), 4, old[1], 100),
    ]
    cases = [check_case(*arg) for arg in args]
    rejected = []
    for arg in args:
        bad_paid = dict(arg[2])
        bad_paid['1'] = 10**9
        mutations = (
            ('lost_unit_superpotential', (*arg[:2], bad_paid, *arg[3:]), 'unit t-superpotential'),
            ('lost_strict_separation', (arg[0], {'1': 1}, *arg[2:]), 'strict mixed separation'),
            ('q_plus_one', (*arg[:6], arg[6]+1, *arg[7:]), 'eta^q > theta'),
        )
        for label, mutated, expected in mutations:
            try:
                check_case(*mutated)
            except ValueError as error:
                need(str(error) == expected, 'wrong rejection point: '+label)
                rejected.append({'family': arg[0], 'mutation': label, 'rejected_at': str(error)})
            else:
                raise ValueError('negative control accepted: '+label)
    return {
        'schema': 'logarithmic-uniform-template-ranks/1',
        'status': 'PASS_LOGARITHMIC_MAJORANT_RANKS', 'cases': cases,
        'kappa_0023_retuned_outer': retuned_outer(cases[2], cases[3]),
        'rejected_mutations': rejected, 'input_sha256': sources,
        'verifier_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'proof_dependency': 'README.md and PR4359 finite source/exit compiler with its native closure hypotheses',
        'scope': 'Smaller sufficient ambient ranks; no emitted supplier, complete constant bounds, native admission, or new kappa.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='write a new receipt instead of comparing RESULT.json')
    args = parser.parse_args()
    result = verify()
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.out:
        need(not args.out.exists(), 'output must be a new file')
        args.out.write_text(encoded)
    else:
        need(read(HERE/'RESULT.json') == json.loads(encoded), 'committed receipt differs')
    print(json.dumps({'status': result['status'], 'ranks': [
        {'family': row['family'], 'N': row['N']} for row in result['cases']],
        'rejected_mutations': len(result['rejected_mutations'])}))


if __name__ == '__main__':
    main()
