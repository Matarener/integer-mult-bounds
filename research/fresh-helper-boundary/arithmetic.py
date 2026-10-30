"""Exact mixed moment, charged strictification and complete consumer ledger.

Apache-2.0. OpenAI Codex assistance; interval arithmetic and charged tail
proof: zxv / PR4433. Compiler: Jacob Alan Sussman's mixed flow.
"""
from collections import Counter
from fractions import Fraction as Q
import json
from pathlib import Path
import native

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KAPPA = Q('.00272124')
TESTED = Q('.00272125')
ROOT_LOW = Q('.0027212601275')
ROOT_HIGH = Q('.0027212601276')
PREVIOUS = Q('.00268647')

def need(ok, why):
    if not ok:
        raise ValueError(why)

def encode(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): encode(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [encode(v) for v in x]
    return x

def run(local):
    E = native.load(ROOT/'research/higher-moment-strictification/verify.py', 'fresh_boundary_intervals')
    case = native.read(ROOT/'research/pr4359-p7-padding/P7-FACTOR.json')
    A = native.load(ROOT/'research/kappa-rebuild/transfer-audit/p3_native_audit.py', 'fresh_boundary_laurent')
    A.replay(case)
    need(case['pairs'] == 7 and case['keep_idle_mask'] == 232127, 'Actual selected p7 controller')
    helpers = {int(k): v for k, v in local['helpers'].items()}
    unit_paid = {int(k): v for k, v in local['paid'].items()}
    targets = Counter({r: 15*n for r, n in helpers.items()})
    targets.update({int(r): n for r, n in case['endpoint_after_stated_free_Pauli_normalization'].items()})
    paid = Counter({r: 15*n for r, n in unit_paid.items()})
    for window in case['retained_idle_windows']:
        paid[window['rank']] += 224
    need(sum(targets.values()) == 7688 and sum(paid.values()) == 53133, 'Complete fields and paid calls')
    target_mass = sum(r*n for r, n in targets.items())
    paid_mass = sum(r*n for r, n in paid.items())
    need((target_mass, paid_mass) == (133718, 133110), 'Complete rank-one invoice')
    need(target_mass-paid_mass == 608, 'The inherited raw surplus is preserved')
    def margin(c):
        t, p = E.moment(targets, 1-c), E.moment(paid, 1-c)
        return t[0]-p[1], t[1]-p[0]
    need(margin(ROOT_LOW)[0] > 0 and margin(ROOT_HIGH)[1] < 0, 'Certified changed-profile root bracket')
    need(KAPPA < TESTED < ROOT_LOW, 'Strict supplier and outer headroom')
    # An interval proof over real C, rather than signs only at a finite mesh.
    signed = {r: targets[r]-paid[r] for r in targets.keys() | paid.keys()}
    derivative_lower = None
    for i in range(16):
        left, right = Q(i, 320), Q(i+1, 320)
        lower = Q(0)
        for r, count in signed.items():
            power = E.power(r, 1-right if count > 0 else 1-left)
            term = E.mul(power, E.log_bounds(r))
            lower += count*term[0 if count > 0 else 1]
        derivative_lower = lower if derivative_lower is None else min(derivative_lower, lower)
    need(derivative_lower > 0, 'Moment is strictly decreasing on [0,1/20]')
    negative_upper = None
    for i in range(128):
        left, right = Q(1,20)+Q(19*i,2560), Q(1,20)+Q(19*(i+1),2560)
        upper = sum(count*E.power(r, 1-left if count > 0 else 1-right)[1 if count > 0 else 0]
                    for r, count in signed.items())
        negative_upper = upper if negative_upper is None else max(negative_upper, upper)
    need(negative_upper < 0, 'Every C in [1/20,1] has negative moment')
    t, v, c, b, u = 1-TESTED, 150, 10, 15, Q(3,10)
    target = E.moment(targets, t)
    alpha = E.divide(E.moment(paid,t), target)
    gamma = E.divide(E.moment(paid,t+u), E.mul(E.power(c,u),target))
    delta = E.divide((Q(sum(targets.values())*b),)*2, E.mul(E.power(c,TESTED),target))
    limits = (1-Q(16,10**9), Q(911,1000), Q(173,200))
    for bounds, limit in zip((alpha,gamma,delta),limits):
        need(0 < bounds[0] <= bounds[1] < limit < 1, 'Certified complete tail limit')
    a, g, d = limits
    normalized_upper = 1/(1+v*(1-a))+2*g**v+2*d**v
    need(normalized_upper < 1, 'All product, original paid tail and padding charges fit')
    need(1 < c < b < 121 and t+u >= 1, 'Strictification hypotheses')
    # PR4433's logarithmic majorant, rebound to this changed complete invoice.
    theta, power = Q(6,7), 13
    eta = E.scale(E.exp_interval(E.scale(E.log_bounds(121),-v*TESTED)),t)
    need(10**7 < 15**6 and 2*(10**v)**7 <= (121**v)**6, 'Actual exit cutoff and shifted logarithm')
    need(eta[0] > theta**power, 'Strict exit versus complement contraction')
    need(E.exp_interval(E.scale(E.log_bounds(121),v*TESTED))[1] < 2**power, 'Full initial rank range')
    gap = (TESTED-KAPPA)/7
    need(gap.numerator == 1, 'Explicit integer grid for the uniform rank')
    step = gap.denominator
    def wins(j):
        return (step*j+1)**power < 2**j
    lo, hi = 1, 2
    while not wins(hi):
        lo, hi = hi, 2*hi
    while hi-lo > 1:
        mid = (hi+lo)//2
        if wins(mid): hi = mid
        else: lo = mid
    H = step*hi
    need(H > 7*v and wins(hi) and not wins(hi-1), 'Strict finite uniform-rank integer test')
    # The original BIT proof already supplies the stronger, unrelaxed value.
    bit = native.read(ROOT/'research/kappa-rebuild/bit/BIT-ALLSIZE-PARAMETERS.json')
    bit_raw = (1-Q(bit['atom_power']))*Q(bit['C1_after_cover'])+Q(bit['atom_power'])*Q(bit['old_ordinary_saving'])
    bit_admitted = Q('.00273')
    need(bit_raw == Q(bit['ordinary_saving_before_final_relaxation']) > bit_admitted > KAPPA, 'Retain the existing stronger BIT conversion')
    need(Q(bit['atom_power']) > bit_raw and 1-bit_raw-Q(bit['atom_power']) > 0, 'Both BIT adapter/stock gaps')
    O = native.load(ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py', 'fresh_boundary_outer')
    params = {'kappa': KAPPA, 'tested_saving': TESTED,
              'complex_uniform_saving': KAPPA+6*gap, 'b': KAPPA+5*gap,
              'a': KAPPA+4*gap, 'q': KAPPA+3*gap, 'bit_saving': bit_admitted,
              'epsilon': 1-gap, 'beta': 1-3*gap, 'r0': gap/10,
              'stop': gap, 'layout': gap, 'd': gap}
    outer = O.ledger(params)
    need(len(outer['strict_checks']) == 54 and len(outer['functional_checks']) == 3, 'Complete consumer predicate inventory')
    need(all(value > 0 for group in ('strict_checks','functional_checks') for value in outer[group].values()), 'Every inherited consumer predicate')
    controls = {}
    for label, patch in [('old_BIT_relaxation', {'bit_saving': Q('.0027')}),
                         ('closed_uniform_gap', {'complex_uniform_saving': params['b']}),
                         ('closed_epsilon', {'epsilon': Q(1)}),
                         ('unfunded_outer', {'kappa': TESTED})]:
        bad = O.ledger(dict(params,**patch))
        failed = [key for key,value in bad['strict_checks'].items() if value <= 0]
        need(failed, 'Reject '+label); controls[label] = failed
    return encode({'status':'PASS_CHANGED_NATIVE_PROFILE_STRICTIFICATION_AND_COMPLETE_OUTER',
        'kappa':KAPPA, 'tested_saving':TESTED, 'gain_over_PR4416':KAPPA-PREVIOUS,
        'relative_gain_over_PR4416':(KAPPA-PREVIOUS)/PREVIOUS,
        'targets':dict(sorted(targets.items())), 'paid':dict(sorted(paid.items())),
        'productive_fields':sum(targets.values()), 'paid_calls':sum(paid.values()),
        'root_bracket':[ROOT_LOW,ROOT_HIGH], 'headroom_from_declared_to_root':[ROOT_LOW-KAPPA,ROOT_HIGH-KAPPA],
        'fixed_profile_ceiling':{'decreasing_C_interval':['0','1/20'],
            'negative_derivative_upper':E.display((-derivative_lower,)*2),
            'remaining_C_interval':['1/20','1'], 'negative_moment_upper':E.display((negative_upper,)*2)},
        'strictification':{'tensor_power':v,'cutoff_base':c,'target_floor_base':b,'tail_offset':u,
            'alpha':E.display(alpha),'gamma':E.display(gamma),'delta':E.display(delta),
            'rational_upper_limits':limits, 'normalized_paid_upper':normalized_upper,
            'gap':E.display((1-normalized_upper,)*2)},
        'compiler':{'theta_upper':theta,'logarithm_power':power,'eta':E.display(eta),
            'uniform_saving':params['complex_uniform_saving'],'gap':gap,'H':H,
            'N':'2^'+str(H), 'integer_test_exponent':hi, 'word_materialized':False},
        'BIT':{'inherited_unrelaxed_saving':bit_raw,'admitted':bit_admitted,'gap':bit_raw-bit_admitted},
        'outer':outer, 'negative_controls':controls})

if __name__ == '__main__':
    result = run(native.read(HERE/'NATIVE-RESULT.json.gz'))
    (HERE/'ARITHMETIC-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','kappa','gain_over_PR4416','root_bracket','compiler')},sort_keys=True))
