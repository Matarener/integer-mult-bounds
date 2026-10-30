#!/usr/bin/env python3
"""Independent stdlib check of PR6030's uniform-compiler application.

Binds the selected PR6030 invoice (targets/paid in its RESULT.json) to the
hypotheses of the higher-moment paid-tail theorem (sec. 2) and the
logarithmic-majorant theorem (sec. 4) as stated in
research/higher-moment-strictification/README.md, and recomputes every
instantiated inequality without importing any repository engine
(no pricing.py, higher-moment verify.py or mixed_target_probe.py).

Real powers use Python's decimal ln/exp, which the language documents as
correctly rounded; every derived real is widened by a relative pad far above
the accumulated rounding error. Integer and rational conditions are exact.

Prepared for JosieElliston with Claude Opus 5.5 (Anthropic) via Claude Code.
Apache-2.0.
"""
from decimal import Decimal as D, Context, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_EVEN, localcontext
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULT = ROOT / 'research/p104-helper470-twin-rung-removal/RESULT.json'
THEOREM = ROOT / 'research/higher-moment-strictification/README.md'
CLAIM = ROOT / 'certificates/frontier6030/CLAIM.json'
PRECOMPILE = ROOT / 'research/higher-moment-strictification/vendor/FINITE-PRECOMPILATION.md'
FINE = ROOT / 'research/selective-borrowing-outer-retune/outer/FINE-PADDING-COMPOSITION.md'
TABLE = ROOT / 'research/selective-borrowing-outer-retune/vendor/pr1673/capped-phase-fusion/OUTER-AUDIT.md'
PINS = {
    RESULT: None, THEOREM: None, CLAIM: None, PRECOMPILE: None,
    FINE: None, TABLE: None,  # filled from SOURCES.json
}
PREC = 90
MARKER = 'PASS_P104_6030_COMPILER_BINDING'


def need(ok, what):
    if not ok:
        raise SystemExit('FAIL: ' + what)


def pins():
    src = json.loads((HERE / 'SOURCES.json').read_text())
    for row in src['files']:
        path = ROOT / row['path']
        if path in PINS:
            got = sha256(path.read_bytes()).hexdigest()
            need(got == row['sha256'], f'pinned bytes of {row["path"]}')
            PINS[path] = got
    need(all(PINS.values()), 'every live input is pinned in SOURCES.json')


# Directed-rounding interval arithmetic.  +, -, *, / are rounded exactly in
# the requested direction by decimal contexts.  decimal's ln/exp are documented
# as correctly rounded (half-even), so their error is at most half an ulp, i.e.
# below |r|*10^(1-PREC); each such result is widened outward by that amount.
DN = Context(prec=PREC, rounding=ROUND_FLOOR, Emax=10 ** 6, Emin=-10 ** 6)
UP = Context(prec=PREC, rounding=ROUND_CEILING, Emax=10 ** 6, Emin=-10 ** 6)
NEAR = Context(prec=PREC, rounding=ROUND_HALF_EVEN, Emax=10 ** 6, Emin=-10 ** 6)
ULP = D(10) ** (1 - PREC)


def qi(x):
    """Enclosure of the rational x."""
    x = Q(x)
    n, d = D(x.numerator), D(x.denominator)
    return (DN.divide(n, d), UP.divide(n, d))


def add(a, b):
    return (DN.add(a[0], b[0]), UP.add(a[1], b[1]))


def sub(a, b):
    return (DN.subtract(a[0], b[1]), UP.subtract(a[1], b[0]))


def mul(a, b):
    lo = min(DN.multiply(x, y) for x in a for y in b)
    hi = max(UP.multiply(x, y) for x in a for y in b)
    return (lo, hi)


def div(a, b):
    need(b[0] > 0, 'positive divisor interval')
    lo = min(DN.divide(x, y) for x in a for y in b)
    hi = max(UP.divide(x, y) for x in a for y in b)
    return (lo, hi)


def widen(r):
    w = UP.multiply(abs(r), ULP)
    return (DN.subtract(r, w), UP.add(r, w))


def ln_i(a):
    need(a[0] > 0, 'positive logarithm argument')
    return (widen(NEAR.ln(a[0]))[0], widen(NEAR.ln(a[1]))[1])


def exp_i(a):
    return (widen(NEAR.exp(a[0]))[0], widen(NEAR.exp(a[1]))[1])


def power(r, s):
    """Enclosure of r^s for integer r >= 1 and rational s."""
    if r == 1:
        return (D(1), D(1))
    return exp_i(mul(qi(s), ln_i(qi(r))))


def moment(inv, s):
    total = (D(0), D(0))
    for r, n in inv.items():
        total = add(total, mul(qi(n), power(r, s)))
    return total


def theorem_text():
    text = THEOREM.read_text(encoding='utf-8')
    # Statement fragments this checker instantiates; a changed statement fails.
    for frag in ('u >= C,  sigma = t+u >= 1,', 'J = c^v,  L = b^v.',
                 'alpha^v + 2 gamma_u^v + 2 delta^v,', 'alpha   = P_t / T_t,',
                 'gamma_u = P_(t+u) / (c^u T_t),', 'delta   = B b / (c^C T_t).',
                 'theta = log(r_max)/log(k_min) < 1.',
                 '2^(b−a) r_max^b <= m^a,', 'theta_bar^p < eta = t m^(t−1),',
                 'm^(1−t) < 2^p.', '(1+H)^p < 2^((z−t)H)'):
        need(frag in text, f'theorem statement fragment present: {frag!r}')
    # m is the largest productive (target) rank, k_min the least, r_max the largest paid.
    pre = PRECOMPILE.read_text(encoding='utf-8')
    for frag in ('Put `m=max{k:W_k>0}`, `k_min=min{k:W_k>0}`, and', '`r_max=max{r_j}`. Require `r_max<k_min`.'):
        need(frag in pre, f'precompilation definition present: {frag!r}')


def outer_rows(res, kappa):
    """Part B: the nine outer savings and the written epsilon/beta constraints.

    Formulas are transcribed from two written sources, not from any ledger
    code: PR1673's cost table (OUTER-AUDIT.md, "Cost ledger") for the rows it
    still states, and FINE-PADDING-COMPOSITION.md sec. 1-2 for the PR1786
    halo/core powers, the Strassen boundary c = 3/32 and the constraint list.
    Each value is compared exactly with the author's RESULT.json entry.
    """
    table = TABLE.read_text(encoding='utf-8')
    for frag in ('| main transform | `1-epsilon*q` |', '| constant global coordinate routing | `1-a_eff` |',
                 '| dense Gaussian groups | `epsilon-q*beta` |', '| grouped bit routing | `epsilon-a_eff*beta` |',
                 '| one/fixed group scans | `epsilon-beta` |', '| polynomial products | `1-epsilon` |',
                 '| core-face corrections | `epsilon+beta+3-8+2` |', 'Use the rational upper bound `omega<45/16`, checked by `7^16<2^45`.'):
        need(frag in table, f'PR1673 cost-table row present: {frag!r}')
    fine = FINE.read_text(encoding='utf-8')
    for frag in ('the polynomial halo p^48 / core p^128',
                 'xi = epsilon(1+q) - c + s (boundary saving = main + s), c = 3/32',
                 'boundary = main + s and union = main + s + 13/32',
                 '1 - epsilon + q beta >= epsilon q', '1 - beta - 2(1-epsilon) > 0',
                 'header / tag per visit: 1 - beta > 0; group below dimension: epsilon - beta > 0',
                 '**1 - epsilon - r0 > 0**', '`source_axis_superpolynomial` 1 - epsilon > 0',
                 'xi = 0.9079 < epsilon (cap_below_cell), xi - 1/2 > 0, guard 1 - (2 xi - 2) - r0 - beta',
                 'core-face corrections epsilon + beta + 48 - 128 + 2 < 0'):
        need(frag in fine, f'fine-padding statement present: {frag!r}')
    outer = res['complete_cost']['outer']
    par = {k: Q(v) for k, v in outer['parameters'].items()}
    # Parameter family from the admission review text: d=(C-kappa)/7, b=k+5d, a=k+4d,
    # q=k+3d, eps=1-d, beta=1-3d; layout s=d and r0=d/10 as recorded.
    C = Q(3125809, 10 ** 9)
    d = (C - kappa) / 7
    a, b, q, eps, beta = kappa + 4 * d, kappa + 5 * d, kappa + 3 * d, 1 - d, 1 - 3 * d
    s_, r0 = par['layout'], par['r0']
    need((par['d'], par['a'], par['b'], par['q'], par['epsilon'], par['beta']) == (d, a, b, q, eps, beta),
         'recorded outer parameters equal the review family')
    need(s_ == d and r0 == d / 10 and par['bit_saving'] == Q(17, 5000), 'layout, r0, admitted BIT')
    tau = Q(45, 16)
    need(7 ** 16 < 2 ** 45, 'omega < 45/16')
    c = Q(3, 32)
    need(c == (3 - tau) / 2, 'c = (3 - tau)/2 = 3/32 (Strassen boundary)')
    xi = eps * (1 + q) - c + s_
    need(xi == par['cap_xi'], 'xi as written')
    halo, core = 48, 128
    cost = {   # power-of-p costs; saving = 1 - cost
        'main_transform': 1 - eps * q,
        'global_coordinate_router': 1 - a,
        'fused_gaussian': eps - q * beta,
        'group_bit_router': eps - a * beta,
        'group_scans': eps - beta,
        'polynomial_products': 1 - eps,
        'microbox_face_corrections': eps + beta + halo - core + 2,
    }
    saving = {k: 1 - v for k, v in cost.items()}
    main = saving['main_transform']
    saving['boundary_algebraic_matrix'] = main + s_          # written: boundary = main + s
    saving['sparse_union_movement'] = main + s_ + Q(13, 32)  # written: union = main + s + 13/32
    need(saving['boundary_algebraic_matrix'] == c + xi - eps, 'boundary = c + xi - eps')
    shown = {k: Q(v) for k, v in outer['margins'].items()}
    need(set(saving) == set(shown) and len(saving) == 9, 'nine outer rows')
    for k, v in saving.items():
        need(v == shown[k], f'outer saving {k} equals RESULT')
        need(v > kappa, f'outer saving {k} above kappa')
    need(min(saving.values()) == main and min(saving, key=saving.get) == 'main_transform',
         'main transform is the limiting row')
    sc = {k: Q(v) for k, v in outer['strict_checks'].items()}
    written = {
        'main_transform_above_kappa': main - kappa,
        'gaussian_above_main': saving['fused_gaussian'] - main,
        'membership_arithmetic_fits_record': 1 - beta - 2 * (1 - eps),
        'union_header_fits_record': 1 - beta,
        'union_tag_work_per_visit_fits_record': 1 - beta,
        'group_below_dimension': eps - beta,
        'global_gamma_power_slack': 1 - eps - r0,
        'source_axis_superpolynomial': 1 - eps,
        'cap_below_cell': eps - xi,
        'cap_above_band': xi - Q(1, 2),
        'group_gauge_power_slack': 1 - (2 * xi - 2) - r0 - beta,
        'strassen_integer_power_gap': Q(2 ** 45 - 7 ** 16),
        'epsilon_positive': eps, 'epsilon_below_one': 1 - eps,
        'group_positive': beta, 'positive_layout_slack': s_,
    }
    written.update({k + '_above_kappa': v - kappa for k, v in saving.items()})
    for k, v in written.items():
        need(k in sc and v == sc[k] and v > 0, f'strict check {k} equals RESULT and is positive')
    need(len(sc) == 54, 'author lists 54 strict checks')
    return {'limiting_row': 'main_transform', 'limiting_slack': str(main - kappa),
            'strict_checks_recomputed_from_written_sources': sorted(written),
            'strict_checks_not_covered': sorted(set(sc) - set(written))}


def lemma_controls():
    """Semantic controls: the checks below can fail."""
    out = {}
    # sec. 2 sigma>=1 restriction: README counterexample t=1/2, sigma=3/4, R=100, J=1.
    with localcontext() as ctx:
        ctx.prec = 40
        false_bound = D(100).sqrt() + 2 * (D(100) ** D('0.75'))
    need(false_bound < 74 < 100, 'sigma<1 extension is false (split charge 100)')
    out['sigma_below_one_counterexample'] = 'actual charge 100 > false bound ' + str(false_bound)[:8]
    # A weaker decay block does not reach 1/16.
    need(not Q(127, 128) ** 128 < Q(1, 16), 'decay 127/128 rejected')
    out['decay_127_128'] = 'rejected: (127/128)^128 >= 1/16'
    # theta_bar too small: 45/46 < log16/log17.
    need(not 16 ** 46 < 17 ** 45, 'theta_bar=45/46 rejected')
    out['theta_bar_45_46'] = 'rejected: 16^46 >= 17^45'
    return out


def main():
    pins()
    theorem_text()
    res = json.loads(RESULT.read_text())
    claim = json.loads(CLAIM.read_text())
    cc = res['complete_cost']
    T = {int(k): int(v) for k, v in cc['targets'].items()}
    P = {int(k): int(v) for k, v in cc['paid'].items()}
    kappa = Q(claim['kappa'])
    need(kappa == Q(781451, 250000000) == Q(cc['kappa']), 'selected kappa')
    # Independent recount of the invoice totals quoted in the admission review.
    need(sum(T.values()) == 13444 and sum(P.values()) == 66834, 'field and call totals')
    need(sum(r * n for r, n in T.items()) - sum(r * n for r, n in P.items()) == 760,
         'rank-mass surplus 760')
    need(max(P) == 72 and max(T) == 145 and min(T) == 1, 'extreme ranks')

    # Parameters, taken from the admission review text, not from pricing.py.
    C = Q(3125809, 10 ** 9)          # tested saving
    t, u, v, c, b, m = 1 - C, Q(1, 7), 1024, 16, 17, 145
    theta_bar, p = Q(63, 64), 1024
    d = (C - kappa) / 7
    z_minus_t = d                    # uniform saving kappa+6d vs tested kappa+7d
    uniform = Q(claim['uniform_templates'][0]['saving'])
    need(claim['uniform_templates'][0]['family'] == 'complex', 'complex template row')
    need(uniform == kappa + 6 * d and (1 - uniform) - t == z_minus_t, 'z-t = d')
    need(Q(cc['strictification']['tested']) == C, 'tested saving recorded')

    # sec. 2 premises.
    need(0 < C < 1 and u >= C and t + u >= 1, '0<C<1, u>=C, sigma=t+u>=1')
    need(1 < c < b < m and isinstance(v, int) and v >= 1, '1<c<b<m, integer v')

    Tt, Pt, Ptu = moment(T, t), moment(P, t), moment(P, t + u)
    B = sum(T.values())
    alpha = div(Pt, Tt)
    gamma = div(Ptu, mul(power(c, u), Tt))
    delta = div(qi(B * b), mul(power(c, C), Tt))
    reserve, decay = Q(1, 10 ** 12), Q(125, 128)
    need(alpha[1] < qi(1 - reserve)[0], 'alpha < 1 - 10^-12')
    need(gamma[1] < qi(decay)[0] and delta[1] < qi(decay)[0], 'gamma, delta < 125/128')
    # Agreement with the author's displayed 30-digit intervals.
    for name, val in (('alpha', alpha), ('gamma', gamma), ('delta', delta)):
        shown = cc['strictification'][name]
        need(D(shown['lower']) <= val[0] and val[1] <= D(shown['upper']),
             f'{name} inside the author interval')
    # eta capacity and initial range for the tensor-powered unit, m^v.
    ln_theta = ln_i(qi(theta_bar))
    ln_m = ln_i(qi(m))
    ln_eta = sub(ln_i(qi(t)), mul(qi(v * C), ln_m))
    p_ln_theta = mul(qi(p), ln_theta)
    margin_eta = sub(ln_eta, p_ln_theta)
    need(margin_eta[0] > 0, 'theta_bar^p < eta = t m^(v(t-1))')
    need(mul(qi(v * C), ln_m)[1] < mul(qi(p), ln_i(qi(2)))[0], 'm^(v(1-t)) < 2^p')
    eta = exp_i(ln_eta)
    shown = cc['compiler']['eta']
    need(D(shown['lower']) <= eta[0] and eta[1] <= D(shown['upper']), 'eta inside the author interval')
    # Least p for theta_bar=63/64 (headroom, information only), rigorously bracketed.
    p_min = int(ln_eta[1] / ln_theta[0])
    while not mul(qi(p_min), ln_theta)[1] < ln_eta[0]:
        p_min += 1
    need(mul(qi(p_min - 1), ln_theta)[0] > ln_eta[1], 'p_min - 1 rejected: least admissible power')
    # Control: m must be the largest target rank (145^v after completion).  A
    # misreading as the 9-qubit dimension 512 would reject p=1024.
    ln_eta_512 = sub(ln_i(qi(t)), mul(qi(v * C), ln_i(qi(512))))
    p1024_ok_512 = not (ln_eta_512[1] < p_ln_theta[0])
    p_512 = int(ln_eta_512[1] / ln_theta[0])
    while not mul(qi(p_512), ln_theta)[1] < ln_eta_512[0]:
        p_512 += 1

    # Input-sensitive control: drop the 208 productive rank-145 jobs from the
    # same invoice; the alpha test must then reject.
    T_bad = {r: n for r, n in T.items() if r != 145}
    alpha_bad = div(moment(P, t), moment(T_bad, t))
    need(not alpha_bad[1] < qi(1 - reserve)[0], 'control: invoice without rank-145 targets rejected')
    # Exact tail assembly: alpha^v + 2 gamma^v + 2 delta^v < 1.
    need(decay ** 128 < Q(1, 16), '(125/128)^128 < 1/16')
    need(v % 128 == 0, 'v is a whole number of decay blocks')
    need(1 / (1 + v * reserve) + Q(4, 2 ** 32) < 1,
         '(1-x)^v <= 1/(1+vx) and 4*(1/16)^(v/128) charge')
    need(c ** v < b ** v, 'max paid c^v < min target b^v')

    # sec. 4 premises with r_max=c^v, k_min=b^v, m^v.  theta = log16/log17.
    a_, b_ = theta_bar.numerator, theta_bar.denominator
    need(c ** b_ < b ** a_, 'theta = log c/log b < theta_bar = 63/64')
    need(2 ** (b_ - a_) * (c ** v) ** b_ <= (m ** v) ** a_,
         'shifted exits 2^(b-a) r_max^b <= m^a')

    # Final threshold (1+H)^p < 2^((z-t)H) on the grid H = j/(z-t).
    need(z_minus_t.numerator == 1, 'z-t is a unit fraction')
    step = z_minus_t.denominator
    wins = lambda j: (step * j + 1) ** p < 2 ** j
    j = cc['compiler']['integer_test_exponent']
    need(j == 47005 and wins(j) and not wins(j - 1), 'j=47005 passes, 47004 fails')
    # Convexity: g(j)=j ln2 - p ln(1+step j) has g(0)=0, g'(0)=ln2-p*step<0,
    # g''>0, so passing grid points form one final ray and j is the first.
    need(p * step > 1, "g'(0) < 0 (ln2 < 1 < p*step)")
    H = step * j
    need(H == cc['compiler']['H'] == 65807000000000, 'H')
    need(claim['uniform_templates'][0]['rank_encoding'] == f'2^{H}', 'claimed N = 2^H')
    need(H > 8 * v and 2 ** 8 > m, 'N = 2^H exceeds the ambient rank m^v')

    out = {
        'marker': MARKER,
        'inputs_sha256': {str(k.relative_to(ROOT)): v for k, v in PINS.items()},
        'invoice': {'productive_fields': B, 'paid_calls': sum(P.values()),
                    'rank_mass_surplus': 760, 'max_paid': 72, 'max_target': 145},
        'section2': {'C': str(C), 'u': '1/7', 'v': v, 'c': c, 'b': b, 'm': m,
                     'alpha_upper': str(alpha[1])[:22], 'gamma_upper': str(gamma[1])[:22],
                     'delta_upper': str(delta[1])[:22]},
        'section4': {'theta_bar': '63/64', 'p': p, 'ln_eta_minus_p_ln_theta_bar_lower': str(margin_eta[0])[:20],
                     'least_p_at_theta_bar_63_64': p_min,
                     'control_if_m_were_512': {'p_1024_passes': p1024_ok_512, 'least_p': p_512},
                     'grid_step': step, 'j': j, 'H': H},
        'outer_partB': outer_rows(res, kappa),
        'controls': dict(lemma_controls(), invoice_without_rank145_targets='rejected: alpha lower bound '
                         + str(alpha_bad[0])[:12]),
    }
    need(not p1024_ok_512, 'control: m=512 rejects p=1024')
    print(json.dumps(out, indent=1))
    print(MARKER)


if __name__ == '__main__':
    main()
