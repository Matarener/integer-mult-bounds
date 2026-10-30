#!/usr/bin/env python3
"""Bind PR6030's remaining 30 strict and 4 functional outer checks to written sources.

PR6109 (research/p104-6030-compiler-binding) recomputed 24 of the 54 strict
outer checks of the selected PR6030 record from written sources and left 30
strict and 4 functional checks open. This verifier takes those 34 rows. For
each one it

  * names the written statement it instantiates and checks that the statement
    text is present in a SHA256-pinned file;
  * evaluates the written formula on PR6030's parameter point with exact
    rationals, without importing any repository code (no endpoint.py,
    pricing.py or outer ledger);
  * requires the value to be positive and to equal the value serialized in
    PR6030's RESULT.json.

It also instantiates the order hypotheses of the stopped-recursion layer
theorem in notes/batched-complex-rows.tex (a proof supplement pinned by the
selected record), reports which ledger row carries each one, and lists the two
hypotheses it does not check (NOT_CHECKED).

Prepared for JosieElliston with Claude Opus 5.5 (Anthropic) via Claude Code.
Apache-2.0.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MARKER = 'PASS_P104_6030_OUTER_ROW_BINDING'

P = {
    'selected': 'certificates/selected-result.json',
    'manifest': 'certificates/frontier6030-source.json',
    'result': 'research/p104-helper470-twin-rung-removal/RESULT.json',
    'bit': 'research/query-thinned-controllers/RESULT.json',
    'rows': 'notes/batched-complex-rows.tex',
    'layout': 'notes/compact-control-layout.tex',
    'assembly': 'notes/stopped-product-assembly.tex',
    'support': 'research/selective-borrowing-outer-retune/vendor/pr1673/capped-phase-fusion/SUPPLIER-SUPPORT-AUDIT.md',
    'fine': 'research/selective-borrowing-outer-retune/vendor/pr1786/FINE-PRIME-PADDING.md',
    'transfer': 'research/pr4359-p7-padding/source/research/kappa-rebuild/transfer-audit/OUTER-TRANSFER-AUDIT.md',
    'endpoint': 'research/pr4359-compiler-refill/ENDPOINT.md',
    'note1673': 'research/selective-borrowing-outer-retune/vendor/pr1673/capped-phase-fusion/phase_fusion_note.tex',
}

# Written statements, verbatim fragments of the pinned files.
FRAG = {
    # Stopped-recursion layer theorem (selected proof supplement).
    'beta': ('rows', r'Fix rational $0<\beta<1$ and stop at $e<d^\beta$'),
    'psi': ('rows', r'Suppose $\Psi_{\rm c}(\sigma)<1$ for $0<\sigma<1$.'),
    'chi': ('rows', r'\chi=\tau+(1-\beta)\max\{\sigma-\tau,0\},'),
    'leafwork': ('rows', r'O\bigl(d^{\sigma+\beta(1-\sigma)}\bigr)'),
    'lam': ('rows', r"\max\{\tau,\sigma,\chi\}<\lambda<\lambda'<1,"),
    'lamp': ('rows', r"\max\{\sigma+\beta(1-\sigma),1-c,0\}<\lambda'"),
    'tau01': ('layout', r'Choose $0<\tau<1$'),
    'kc': ('layout', r'For large $p$, $K\ge d^c/2$'),
    # PR1673 support-local supplier: tau, q<a, and the replaced K.
    'tau_a': ('support', 'Let tau=1-a. The retained stopped branching argument gives O(V h^(1-q) polylog p) for each phase, with q<a and the same strict complex/leaf margin as the retained supplier.'),
    'k128': ('support', 'K=128G satisfies the displayed finite inequality directly.'),
    'exposure': ('support', 'O(V_node h^(1-a) polylog(p))'),
    'shrink': ('support', 'h_(j+1)<=h_j/16'),
    # Selected assembly lineage: internal exponent is tau when sigma<tau.
    'sig_tau': ('assembly', r"Since $\sigma<\tau$, the internal paid-adapter"),
    # PR4359 outer transfer audit, section 6 and section 5.
    'eff': ('transfer', 'The effective BIT saving is below both the\nactual ordinary BIT saving and the selected complex saving.'),
    'below': ('transfer', "internal and leaf exponents are strictly below the selected `lambda` and\n`lambda_prime`, respectively."),
    'groupbeta': ('transfer', 'fit the full `Theta(p)`-bit tensor because\n`group_beta<1`.'),
    'eps_abs': ('transfer', 'The first two absorb every new fixed semantic, movement and row constant;\nthe next two retain the precision and fine-prime spare powers.'),
    'reserve': ('transfer', 'group_beta*(1-0.003) > 0.'),
    'reserve_why': ('transfer', 'The last\nensures the changed BIT reserve is sublinear in the active grouped width'),
    'sublog': ('transfer', 'Polynomial description/preparation\ncosts are absorbed by the retained complete superpolynomial record fibers\nwhen `epsilon<1`'),
    'theta2': ('endpoint', 'halo power `48`, core power `128`, and theta power `2`.'),
    'chain': ('endpoint', '0 < q < a < b < uniform < C_test < 0.002306 < 0.0027,'),
    'geo': ('endpoint', '`0 < beta < epsilon`, `b < 1/32`, `epsilon>a`, and the unchanged integer'),
    'internal_tau': ('endpoint', 'For the stopped supplier, `sigma=1-b < tau=1-a`, so its internal exponent is\n`tau`.'),
    'leafeff': ('note1673', r'Using supplier stopping exponent $10^{-9}$ gives a strict leaf saving above $a_{\rm eff}$ and $q$.'),
    'leafgap': ('endpoint', '(1-stop)*b-a           = d*(1-b),'),
    'lamdef': ('endpoint', 'With `lambda=1-(q+a)/2` and `lambda_prime=1-q`, the delicate gaps are'),
    'xidef': ('endpoint', 'xi = epsilon*(1+q) - 3/32 + layout = 29/32 + (1-d)*q.'),
    'keygap': ('endpoint', 'and the group key gap is `2*d`.'),
    'baseline': ('endpoint', "The source's historical-baseline comparison is a\nreporting check, rather than an admission hypothesis"),
    'bit27': ('endpoint', 'Keep the ordinary BIT saving `0.0027`'),
    # PR1786 fine-prime padding: halo, core, locality and conditioning.
    'halo_side': ('fine', '128-48-beta>0, 48>43.'),
    'xi2': ('fine', '1/2<xi<epsilon, xi<2,'),
    'halo_cost': ('fine', "Its paid cost power is\n`epsilon+beta+48-128+2`; its halo-volume margin is `128-48-beta>0`."),
    'halo48': ('fine', 'a halo `A=C_A p^48` covers it.'),
    'neumann': ('fine', 'With `J=ceil(p^42)`'),
    'band': ('fine', 'The bandwidth is at most `2WJ+W`.'),
    'p10': ('fine', 'a conservative common eventual bound p^10 covers'),
    'cond': ('fine', 'the exponential\nfactor is at most p^2 eventually, theta^-2<=16p^4, and alpha^5 is'),
    'gamma': ('fine', '1-epsilon-r0>0,'),
    'gauge': ('fine', '1-(2xi-2)-r0-beta=0.184140990423...>0,'),
}


def need(ok, what):
    if not ok:
        raise SystemExit('FAIL: ' + what)


def load():
    src = json.loads((HERE / 'SOURCES.json').read_text())
    pinned = {row['path']: row['sha256'] for row in src['files']}
    text = {}
    for key, rel in P.items():
        need(rel in pinned, f'{rel} is pinned in SOURCES.json')
        raw = (ROOT / rel).read_bytes()
        need(sha256(raw).hexdigest() == pinned[rel], f'pinned bytes of {rel}')
        text[key] = raw.decode()
    for name, (key, frag) in FRAG.items():
        need(frag in text[key], f'statement fragment {name!r} in {P[key]}')
    return text


def family(kappa, tested):
    """The review's parameter family (PR6030 PROOF-REVIEW.md), restated here."""
    d = (tested - kappa) / 7
    return {'kappa': kappa, 'tested_saving': tested, 'd': d,
            'complex_uniform_saving': kappa + 6 * d, 'b': kappa + 5 * d,
            'a': kappa + 4 * d, 'q': kappa + 3 * d, 'epsilon': 1 - d,
            'beta': 1 - 3 * d, 'r0': d / 10, 'stop': d, 'layout': d}


def derived(p, bit_saving, atom, **over):
    p = dict(p)
    sigma, tau = 1 - p['b'], 1 - p['a']
    stop = p['stop']
    chi = tau + (1 - stop) * max(sigma - tau, Q(0))     # written chi, beta := stop
    leaf = sigma + stop * (1 - sigma)                    # written leaf exponent
    lam_p = 1 - p['q']                                   # layer exponent; saving q
    lam = (tau + lam_p) / 2                              # PR141/assembly choice
    xi = p['epsilon'] * (1 + p['q']) - Q(3, 32) + p['layout']
    return dict(p, sigma=sigma, tau=tau, chi=chi, leaf=leaf, lam=lam, lam_p=lam_p,
                xi=xi, bit=bit_saving, atom=atom, **dict(dict(halo=48, core=128, radius=43), **over))


# (row, group, status, fragments, written formula as a function of derived values)
# status: theorem = hypothesis of a written theorem; statement = a written
# sentence asserts the inequality; constant = a fixed written constant;
# reporting = written as a reporting check, not an admission hypothesis.
ROWS = [
    # Stopped-recursion layer theorem, notes/batched-complex-rows.tex.
    ('stop_positive', 'stopped', 'theorem', ['beta'], lambda v: v['stop']),
    ('stop_below_one', 'stopped', 'theorem', ['beta'], lambda v: 1 - v['stop']),
    ('lambda_above_tau', 'stopped', 'theorem', ['lam', 'lamdef'], lambda v: v['lam'] - v['tau']),
    ('lambda_above_sigma', 'stopped', 'theorem', ['lam', 'lamdef'], lambda v: v['lam'] - v['sigma']),
    ('lambda_above_internal', 'stopped', 'theorem', ['lam', 'chi', 'lamdef'], lambda v: v['lam'] - v['chi']),
    ('lambda_prime_above_lambda', 'stopped', 'theorem', ['lam', 'lamdef'], lambda v: v['lam_p'] - v['lam']),
    ('q_positive', 'stopped', 'theorem', ['lam', 'lamdef'], lambda v: 1 - v['lam_p']),
    ('lambda_prime_above_leaf', 'stopped', 'theorem', ['lamp', 'leafwork', 'lamdef'], lambda v: v['lam_p'] - v['leaf']),
    ('q_below_leaf', 'stopped', 'theorem', ['lamp', 'leafwork', 'lamdef'], lambda v: 1 - v['leaf'] - v['q']),
    ('q_below_internal', 'stopped', 'statement', ['below', 'chi'], lambda v: 1 - v['chi'] - v['q']),
    ('leaf_saving_above_effective', 'stopped', 'statement', ['leafeff', 'leafgap'], lambda v: (1 - v['stop']) * v['b'] - v['a']),
    # Effective-saving chain.
    ('q_below_effective', 'effective', 'statement', ['tau_a', 'chain'], lambda v: v['a'] - v['q']),
    ('complex_endpoint', 'effective', 'statement', ['chain'], lambda v: v['b'] - v['q']),
    ('complex_above_effective', 'effective', 'statement', ['eff', 'chain'], lambda v: v['b'] - v['a']),
    ('actual_bit_above_effective', 'effective', 'statement', ['eff'], lambda v: v['bit'] - v['a']),
    ('new_complex_uniform_saving_above_b', 'effective', 'statement', ['psi', 'chain'], lambda v: v['complex_uniform_saving'] - v['b']),
    ('complex_below_one_over_32', 'effective', 'statement', ['geo'], lambda v: Q(1, 32) - v['b']),
    ('short_record_fallback', 'effective', 'statement', ['geo'], lambda v: v['epsilon'] - v['a']),
    # Fine-prime halo, locality and conditioning (PR1786).
    ('microbox_halo_volume', 'halo', 'theorem', ['halo_side', 'halo_cost'], lambda v: v['core'] - v['halo'] - v['beta']),
    ('halo_covers_generic_inverse_radius', 'halo', 'constant', ['halo_side', 'halo48', 'neumann', 'band'], lambda v: Q(v['halo'] - v['radius'])),
    ('cap_below_phase_cell_power', 'halo', 'statement', ['xi2', 'xidef'], lambda v: 2 - v['xi']),
    ('fine_prime_halo_umbrella', 'halo', 'constant', ['p10', 'cond'], lambda v: 10 - (2 * 2 + 2 + Q(1, 2))),
    ('theta_positive_polynomial_power', 'halo', 'constant', ['theta2'], lambda v: Q(2)),
    # Logarithmic guards and record geometry.
    # Written: 1-(2xi-2)-r0-beta>0 and 1-epsilon-r0>0. The serialized rows drop
    # r0 (r0>0), so the written margins imply them; see WRITTEN_STRONGER.
    ('actual_logarithmic_group_guard', 'guards', 'implied', ['gauge', 'xidef'], lambda v: 1 - (2 * v['xi'] - 2) - v['beta']),
    ('actual_logarithmic_gamma_guard', 'guards', 'implied', ['gamma'], lambda v: 1 - v['epsilon']),
    ('alpha_logarithm_absorption', 'guards', 'statement', ['gamma', 'gauge'], lambda v: v['r0']),
    ('group_key_fits_record', 'guards', 'statement', ['keygap'], lambda v: 1 - (v['beta'] + 1 - v['epsilon'])),
    ('support_router_span', 'guards', 'statement', ['groupbeta'], lambda v: 1 - v['beta']),
    ('new_semantic_guard_with_C1_one', 'guards', 'statement', ['eps_abs', 'sublog'], lambda v: 1 - v['epsilon']),
    ('improvement_over_user_baseline', 'guards', 'reporting', ['baseline'], lambda v: v['kappa'] - OLD_BASELINE),
]
FUNCTIONAL = [
    ('new_semantic_group_guard', 'statement', ['groupbeta', 'eps_abs'], lambda v: 1 - v['beta']),
    ('new_BIT_row_stock_sublinear_in_active_group', 'statement', ['reserve', 'reserve_why'], lambda v: v['beta'] * (1 - Q(3, 1000))),
    # Written with the PR4359 atom 0.003; PR6030 substitutes the current atom
    # 1/250 (a data input, not a written inequality).
    ('actual_new_BIT_stock_sublinear', 'substituted', ['reserve', 'reserve_why'], lambda v: v['beta'] * (1 - v['atom'])),
    # Saving = 1 - (written paid cost power epsilon+beta+48-128+2).
    ('fixed_halo_explicit_metadata_branch', 'theorem', ['halo_cost'],
     lambda v: 1 - (v['epsilon'] + v['beta'] + v['halo'] - v['core'] + 2)),
]
WRITTEN_STRONGER = {
    'actual_logarithmic_group_guard': lambda v: 1 - (2 * v['xi'] - 2) - v['r0'] - v['beta'],
    'actual_logarithmic_gamma_guard': lambda v: 1 - v['epsilon'] - v['r0'],
}
# PR4359's historical baseline constant; the row is a reporting check only.
OLD_BASELINE = Q('0.001730970419199163702738')
PR6109_COVERED = 24


# Hypotheses of the written layer theorem that this verifier does not check.
NOT_CHECKED = {
    'Psi_c(sigma)<1': 'stated for the theorem\'s own motif moment; for PR6030 the corresponding premise is the '
                      'complex uniform supplier saving above b (compiler obligation, PR6109 sec. 2/4); only '
                      'b < uniform < C is checked here',
    "1-c<lambda'": 'no ledger row or parameter c; with K=128G no fixed c>0 has K>=d^c/2. Proposed reading, not '
                   'verified: PR1673 SUPPLIER-SUPPORT-AUDIT.md sec. 4-6 replaces the d^max(1-c,0) term by '
                   'support-local exposure O(V h^(1-a) polylog p); only tau<lambda\' is checked here',
}


def theorem_hypotheses(v):
    """The order hypotheses of the written layer theorem (see NOT_CHECKED)."""
    return {
        '0<beta<1 (beta=stop, rational)': 0 < v['stop'] < 1,
        '0<tau<1': 0 < v['tau'] < 1,
        '0<sigma<1': 0 < v['sigma'] < 1,
        'max(tau,sigma,chi)<lambda': max(v['tau'], v['sigma'], v['chi']) < v['lam'],
        "lambda<lambda'": v['lam'] < v['lam_p'],
        "lambda'<1": v['lam_p'] < 1,
        "sigma+beta(1-sigma)<lambda'": v['leaf'] < v['lam_p'],
        "0<lambda'": 0 < v['lam_p'],
    }


def evaluate(v, result_strict, result_functional):
    rows = {}
    for name, group, status, frags, f in ROWS:
        val = f(v)
        need(val > 0, f'{name} strictly positive')
        need(name in result_strict, f'{name} serialized in RESULT.json')
        need(val == result_strict[name], f'{name} equals RESULT.json ({val} vs {result_strict[name]})')
        rows[name] = {'group': group, 'status': status, 'value': str(val),
                      'sources': sorted({P[FRAG[x][0]] for x in frags})}
    func = {}
    for name, status, frags, f in FUNCTIONAL:
        val = f(v)
        need(val > 0, f'{name} strictly positive')
        need(val == result_functional[name], f'functional {name} equals RESULT.json')
        func[name] = {'status': status, 'value': str(val),
                      'sources': sorted({P[FRAG[x][0]] for x in frags})}
    return rows, func


def main():
    text = load()
    selected = json.loads(text['selected'])
    need(selected['kappa'] == '781451/250000000', 'selected record is PR6030 kappa')
    need(selected['proof_supplements'].get(P['rows']) == sha256(text['rows'].encode()).hexdigest(),
         'the stopped-recursion theorem file is the selected proof supplement byte for byte')
    # Every source carrying a row is byte-identical to a file in the selected
    # record's source manifest (possibly at a vendored path). The two notes
    # outside it are cited as lineage context only.
    manifest = json.loads(text['manifest'])['files']
    need(selected['source_manifest'] == P['manifest'], 'manifest is the selected source manifest')
    by_hash = {}
    for path, digest in manifest.items():
        by_hash.setdefault(digest, []).append(path)
    in_manifest = {}
    for key in ('result', 'bit', 'rows', 'support', 'note1673', 'fine', 'transfer', 'endpoint'):
        hits = by_hash.get(sha256(text[key].encode()).hexdigest(), [])
        need(hits, f'{P[key]} is byte-identical to a selected-manifest file')
        in_manifest[P[key]] = P[key] if P[key] in hits else sorted(hits)[0]
    context_only = [P[k] for k in ('layout', 'assembly')]
    result = json.loads(text['result'])['complete_cost']
    outer = result['outer']
    par = {k: Q(x) for k, x in outer['parameters'].items()}
    strict = {k: Q(x) for k, x in outer['strict_checks'].items()}
    functional = {k: Q(x) for k, x in outer['functional_checks'].items()}
    need(len(strict) == 54 and len(functional) == 4, 'RESULT.json has the 54 + 4 inventory')
    kappa, tested = Q(result['kappa']), Q(result['strictification']['tested'])
    need(kappa == Q(selected['kappa']), 'RESULT kappa is the selected kappa')

    fam = family(kappa, tested)
    for k, x in fam.items():
        need(par[k] == x, f'parameter {k} is the review family value')
    bit = json.loads(text['bit'])['ordinary_BIT']
    admitted, atom = Q(bit['admitted']), Q(bit['atom'])
    need(par['bit_saving'] == admitted == Q(17, 5000), 'bit_saving is the admitted BIT saving 17/5000')
    v = derived(fam, admitted, atom)
    need(par['lambda_'] == v['lam'] and par['lambda_prime'] == v['lam_p'] and par['cap_xi'] == v['xi'],
         'serialized lambda, lambda_prime and xi equal the written definitions')

    rows, func = evaluate(v, strict, functional)
    need(len(rows) + PR6109_COVERED == 54 and len(set(rows)) == 30, '30 rows here + 24 in PR6109 = 54')
    hyp = theorem_hypotheses(v)
    need(all(hyp.values()), 'every checked order hypothesis of the layer theorem holds at PR6030')
    stronger = {}
    for name, f in WRITTEN_STRONGER.items():
        need(f(v) > 0 and f(v) < Q(strict[name]), f'written margin of {name} (with r0) is positive and implies the row')
        stronger[name] = str(f(v))
    need(v['sigma'] < v['tau'] and v['chi'] == v['tau'], 'sigma<tau branch: chi = tau, as written')

    # The 1-c<lambda' hypothesis has no ledger row and no ledger parameter c.
    # In the PR1673 support-local supplier K=128G (not K >= d^c/2 for c>0), and
    # the compact-field term is replaced by exposure charges O(V h^(1-a)) =
    # O(V h^tau); the replacement condition tau < lambda' follows from the
    # lambda rows.
    need(v['tau'] < v['lam'] < v['lam_p'], "replacement condition tau < lambda' holds")

    # ENDPOINT.md's written family proof states q < 0.002306 and BIT 0.0027.
    # Neither premise holds at PR6030; the identities it derives still hold.
    premise = {'q_below_0.002306': v['q'] < Q('0.002306'), 'bit_is_0.0027': admitted == Q('0.0027')}
    need(not any(premise.values()), 'ENDPOINT.md loose premises do not apply verbatim to PR6030')
    need((1 - v['stop']) * v['b'] - v['a'] == v['d'] * (1 - v['b'])
         and v['lam_p'] - v['leaf'] == v['d'] * (2 - v['b'])
         and v['lam'] - v['tau'] == v['d'] / 2 and v['lam'] - v['sigma'] == 3 * v['d'] / 2,
         'ENDPOINT.md closed-form gaps hold as identities at the PR6030 point')
    need(kappa < min(v['complex_uniform_saving'], admitted, Q(1, 32)) and kappa > OLD_BASELINE,
         "inside PR5984's region OLD < kappa < min(U, B, 1/32)")

    # Rows that are the same expression in the free outer parameters (not
    # merely equal on the one-parameter family): group by values at PR6030 and
    # at two points whose parameters are chosen independently of each other.
    reference = {'epsilon_below_one (PR6109)': lambda w: 1 - w['epsilon'],
                 'source_axis_superpolynomial (PR6109)': lambda w: 1 - w['epsilon'],
                 'group_below_dimension (PR6109)': lambda w: w['epsilon'] - w['beta'],
                 'union_header_fits_record (PR6109)': lambda w: 1 - w['beta']}
    for name in reference:
        need(reference[name](v) == strict[name.split(' ')[0]], f'{name} reference formula')
    formulas = {name: f for name, _, _, _, f in ROWS}
    formulas.update({name + ' (functional)': f for name, _, _, f in FUNCTIONAL})
    formulas.update(reference)
    free = [dict(kappa=Q(1, 500), tested_saving=Q(1, 300), d=Q(1, 7000), complex_uniform_saving=Q(1, 310),
                 b=Q(1, 320), a=Q(1, 350), q=Q(1, 410), epsilon=Q(97, 100), beta=Q(91, 100),
                 r0=Q(1, 900), stop=Q(1, 77), layout=Q(1, 130)),
            dict(kappa=Q(1, 450), tested_saving=Q(1, 290), d=Q(1, 9000), complex_uniform_saving=Q(1, 295),
                 b=Q(1, 301), a=Q(1, 333), q=Q(1, 380), epsilon=Q(99, 101), beta=Q(89, 97),
                 r0=Q(1, 1300), stop=Q(1, 61), layout=Q(1, 170))]
    points = [v] + [derived(f, Q(1, 250), Q(1, 300)) for f in free]
    groups = {}
    for name, f in formulas.items():
        groups.setdefault(tuple(f(w) for w in points), []).append(name)
    coincident = sorted(sorted(g) for g in groups.values() if len(g) > 1)

    # Controls. Each one changes one input and must be rejected.
    controls = {}

    def rejects(mod, label, test):
        w = derived(dict(fam, **mod.get('fam', {})), mod.get('bit', admitted), atom)
        ok = test(w)
        need(not ok, f'control {label} is rejected')
        controls[label] = 'rejected'

    rejects({'fam': {'stop': Q(0)}}, 'stop = 0 (beta must be positive)', lambda w: theorem_hypotheses(w)['0<beta<1 (beta=stop, rational)'])
    rejects({'fam': {'stop': 1 - fam['q'] / fam['b']}}, 'stop = 1 - q/b (leaf reaches lambda prime)',
            lambda w: theorem_hypotheses(w)["sigma+beta(1-sigma)<lambda'"])
    rejects({'fam': {'q': fam['a']}}, 'q = a (lambda collapses onto tau)',
            lambda w: theorem_hypotheses(w)['max(tau,sigma,chi)<lambda'])
    rejects({'bit': Q('0.0027')}, 'BIT saving 0.0027 (PR4359 value)', lambda w: w['bit'] - w['a'] > 0)
    # The ledger's leaf ordering (1-stop)b > a is stronger than the theorem's
    # sigma+beta(1-sigma) < lambda', i.e. (1-stop)b > q. At stop = d/b every
    # theorem hypothesis holds, but the ledger row (and the PR1673 note's
    # "leaf saving above a_eff") rejects.
    edge = derived(dict(fam, stop=fam['d'] / fam['b']), admitted, atom)
    need(all(theorem_hypotheses(edge).values()), 'stop = d/b satisfies the layer theorem')
    need((1 - edge['stop']) * edge['b'] - edge['a'] == 0, 'stop = d/b is the leaf-ordering edge')
    controls['stop = d/b (layer theorem holds; ledger leaf ordering (1-stop)b > a rejects)'] = 'rejected'
    low = derived(fam, admitted, atom, halo=43)
    for name in ('halo_covers_generic_inverse_radius',):
        f = next(r[4] for r in ROWS if r[0] == name)
        need(not f(low) > 0, 'halo exponent 43 fails the radius row')
    controls['halo exponent 43 (radius row through the row evaluator)'] = 'rejected'
    fat = derived(fam, admitted, atom, core=50)
    f = next(r[3] for r in FUNCTIONAL if r[0] == 'fixed_halo_explicit_metadata_branch')
    need(not f(fat) > 0, 'core exponent 50 fails the core-face saving')
    controls['core exponent 50 (core-face saving through the row evaluator)'] = 'rejected'
    bad = dict(strict)
    bad['lambda_above_tau'] += Q(1, 10**30)
    try:
        evaluate(v, bad, functional)
    except SystemExit:
        controls['RESULT.json lambda_above_tau perturbed by 1e-30'] = 'rejected'
    need('RESULT.json lambda_above_tau perturbed by 1e-30' in controls, 'perturbed RESULT row is caught')

    status = {}
    for r in list(rows.values()) + list(func.values()):
        status[r['status']] = status.get(r['status'], 0) + 1
    print(json.dumps({
        'selected_kappa': str(kappa), 'd': str(v['d']),
        'stopped_theorem': {'source': P['rows'], 'selected_proof_supplement': True,
                            'checked_order_hypotheses': {k: bool(x) for k, x in hyp.items()},
                            'not_checked': NOT_CHECKED,
                            'chi_branch': 'sigma<tau, chi=tau'},
        'selected_manifest_copies': in_manifest, 'context_only_sources': context_only,
        'strict_rows': rows, 'functional_rows': func,
        'status_counts': status,
        'written_margins_with_r0': stronger,
        'endpoint_md_premises_hold': premise,
        'same_expression_in_free_parameters': coincident,
        'controls': controls,
    }, indent=1))
    print(MARKER)


if __name__ == '__main__':
    main()
