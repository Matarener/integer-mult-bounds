#!/usr/bin/env python3
"""Halving degree of the selected complex finite invoice under the inherited degree-t ledger:
exact t_max, the admissible (child rank R, stock bits S) region, and ideal local-word
ceilings at R = 51, 57, 72.

Scoped finite statement under inherited hypotheses (see PROOF.md). No kappa, no supplier.
usage: verify.py [--write]   (default: recompute and require byte equality with RESULT.json)
Sagar Thakrar (thakrarsagar), with substantial AI assistance from Claude (Anthropic,
Claude Opus 5.5). Apache-2.0.
"""
import hashlib, json, sys, tarfile
from decimal import Decimal as D, Context, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN
from fractions import Fraction as Q
from pathlib import Path

if not __debug__:
    raise SystemExit('run without -O: assertions are the checks')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
M = 73                                   # complex parent dimension (assemble.py halving 73*73)
SEL = 'research/complex-sw4-frame8/code/'  # selected assembler (SELECTED-SOURCE.json manifest)
RETAINED = 20161                         # assemble.py:159 retained_row_coefficient
RESERVE, FACTOR = 10 ** 6, Q(51, 25)     # assemble.py:213 degree_gap = 10**6 - (51/25)*20161
BIT_RESERVES = 9909 + 252                # invoice_allcold.py:278; notes/*-assembly.tex
PAYLOAD = 512                            # invoice_allcold.py:263 payload=512
INVOICE = 'candidate/strict/global/audit/PREFIX-AND-INVOICE.json'
INVOICE_SHA = '212cf4ee3b16081bf66f300fa18b4070d25c17210c21c78c2967892c91870d12'
FAMILIES, STAGES, CENTRE = 2 * 4 * 112, 9, 64   # complex-local-word-ceiling model
T_RANGE = range(2, 201)


def text(rel):
    return (ROOT / rel).read_text()


def bind_sources():
    """Every t-dependent invoice term, bound to literal pinned source text."""
    manifest = json.loads(text(json.loads(text('certificates/selected-result.json'))['source_manifest']))
    for f in ('assemble.py', 'invoice_allcold.py'):
        want = manifest['files'].get(SEL + f)
        assert hashlib.sha256((ROOT / SEL / f).read_bytes()).hexdigest() == want, f'{f} is not the selected source'
    need = {
        SEL + 'invoice_allcold.py': [
            'row=2*stock.bit_length()+9909+252+2*payload',
            'used=max(rebased,parent_pervertex); retained=None; payload=512',
            'half=m//2; group=2**(half*half)',
            'for i in range(1,half+1): group*=2**(2*i)-1',
            'stock,streamed_mass=group*physical,group*mass',
            'logical=group*used+64; router=compiler*(logical+1)*(stock+1)**2',
            'literal=2*g_bound*stock**2+8*streamed_mass+4*stock+4+32*m',
            'tape=2*total_mass+18<c0,row=row<20161,halving=m*m>2*maxchild*maxchild)',
            'inequalities=dict(local_primitive_bound=primitive_bound<2**48,',
            'logical=logical<2**6050,router=router<g_bound,literal=literal<e_bound,',
            'row_prefix_extra=2*payload', 'retained_row_coefficient=20161'],
        SEL + 'assemble.py': [
            "assert 0<finite['physical_row_coefficient']<finite['retained_row_coefficient']==20161",
            "assert finite['physical_row_coefficient']==2*stock.bit_length()+9909+252+1024",
            "row=finite['physical_row_coefficient']<20161,halving=73*73>2*48*48)",
            "'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}",
            'precision=32*73*total_mass*total_mass<2**210000',
            'cut=max(ceil(36/gap**2),ceil(2*(4+512)/gap))',
            'and m*m>2*max(h)**2',
            "bit['bit']['two_level_coefficient_bits']<bit['bit']['charged_two_level_coefficient_bits']==512 and bit['bit']['row_coefficient']<20161"],
        # Lineage bridge text (outside the selected manifest): 20161 is a degree-1 overcharge.
        'research/five-stage-gen4-banks/inputs/complex/retained/FINITE_BRIDGE.txt': [
            'The complex child maximum below m/2 gives halving degree1, while',
            'A=10000+9909+252=20161.', 'Increasing these finite overcharges changes'],
        'research/contextual-provider-pooling/docs/PRIOR-TN27-README.md': ['below the retained20161 allowance'],
        # A selected-manifest lineage assembler certifies the bridge at max(20161, rows).
        'research/direct-delivery504-global/code/assemble.py': [
            "row=max(20161,int(bit['bit']['row_coefficient']),inv['finite']['physical_row_coefficient'])"],
        # The outer engine consumes degree_gap only as a positivity slack (no kappa margin).
        'research/contextual-provider-pooling/engines/outer.py': [
            "row_product_gap=bridge['rows']['degree_gap'])"],
        # The same lineage instantiates the guard at halving degrees 4 and 24: stock bits are
        # multiplied by the least halving degree, 9909+252 is unchanged, the bridge reserve is chosen.
        'notes/paired-cube-assembly.tex': [
            'The least halving degree for $72\\to60$ is four, contributing 10,284 to',
            '10284+9909+252=20445,\\qquad', '70000-\\frac{51}{25}\\,20445=\\frac{141461}{5}>0.',
            'Thus the fixed external reserve $p^{70000}$ suffices.',
            'A full $W$-role permutation costs at most $W^2$ elementary exchanges;',
            'E=64(W+m_c+G+1)^3,\\quad B=s+E,\\quad C_0=32m_cB^2.'],
        'notes/three-stage-cover-assembly.tex': [
            'The least halving degree for $70\\to68$ is 24, contributing 58,344.',
            '58344+9909+252=68505,\\qquad', '160000-\\frac{51}{25}\\,68505=20249.8>0.',
            'A fixed role permutation has at most $W^2$ elementary exchanges; the',
            ' 2GW^2+8s+4W+4+32m_c<E,\\qquad'],
        'notes/three-stage-cover-rows.tex': [
            'The finite cover requires a row divisor $W(w)$ at each coarse level.'],
        'notes/structured-bulk-assembly.tex': [
            ' \\log_2Q\\le\\frac{51}{25}K\\log_2p,',
            'The sufficient stock is $p^{108000}$, since',
            'holds eventually for every fixed $\\epsilon<1$.'],
    }
    for rel, needles in need.items():
        body = text(rel)
        for s in needles:
            assert s in body, f'source binding missing in {rel}: {s}'
    # Precedent arithmetic: contribution = least halving degree * role-stock bits.
    assert least_degree(72, 60) == 4 and 4 * 2571 == 10284 and 10284 + BIT_RESERVES == 20445 > RETAINED
    assert least_degree(70, 68) == 24 and 24 * 2431 == 58344 and 58344 + BIT_RESERVES == 68505
    assert 70000 - FACTOR * 20445 == Q(141461, 5) and 160000 - FACTOR * 68505 == Q(202498, 10)
    return sum(len(v) for v in need.values())


def least_degree(m, r):
    """Least t >= 1 with m^t > 2 r^t (integer arithmetic); None if r >= m."""
    if r >= m:
        return None
    t = 1
    while m ** t <= 2 * r ** t:
        t += 1
    return t


def least_degree_recurrence(m, r):
    """Implementation cross-check (algebraically the same comparison): iterate the coarse recurrence n -> r*floor(n/m) from n0 = m^T (floors exact)
    and return the first level t with 2*n_t < n0."""
    T = 80
    n0 = n = m ** T
    for t in range(1, T + 1):
        n = r * (n // m)
        if 2 * n < n0:
            return t
    return None


def r_max(t):
    """Largest R with 2 R^t < 73^t."""
    return max(r for r in range(1, M) if 2 * r ** t < M ** t)


def group(half):
    g = 2 ** (half * half)
    for i in range(1, half + 1):
        g *= 2 ** (2 * i) - 1
    return g


def load_invoice():
    with tarfile.open(ROOT / 'research/community-frontier1094-audit/selected-replay.tar.gz') as tf:
        raw = tf.extractfile(INVOICE).read()
    assert hashlib.sha256(raw).hexdigest() == INVOICE_SHA, 'selected invoice bytes changed'
    return json.loads(raw)


def selected_word():
    """Selected complex profile and its per-call local word (same split as complex-local-word-ceiling)."""
    rec = json.loads(text('certificates/selected-result.json'))
    asm = json.loads(text(rec['certificate']))
    ind = json.loads(text('research/community-frontier1094-audit/INDEPENDENT1094.json'))
    H = {int(r): n for r, n in asm['complex_profile'].items()}
    idle = {int(r): n for r, n in ind['owner']['idle'].items()}
    N, W = ind['price']['calls'], ind['price']['live']
    assert H == {int(r): n for r, n in ind['owner']['profile'].items()}
    assert N % STAGES == 0 and W == FAMILIES * (N // STAGES)
    mass = sum(r * n for r, n in H.items())
    assert mass == (M - 1) * W + CENTRE * N
    local = {}
    for r, n in H.items():
        k = n - idle.get(r, 0)
        assert k >= 0 and k % N == 0
        if k:
            local[r] = k // N
    return H, mass, local, Q(asm['bit_lower']), Q(asm['complex_lower']), asm['binding']


def bind_invoice(inv, H, mass):
    """Recompute the selected finite invoice from its own fields: S, row, router, literal, C0."""
    fin = inv['finite']
    g = group(M // 2)
    stock = g * inv['physical']
    S = stock.bit_length()
    assert S == fin['physical_stock_bits'], 'stock bits'
    assert inv['row_prefix_extra'] == 2 * inv['charged_prefix_bits'] == 2 * PAYLOAD, 'prefix'
    assert fin['physical_row_coefficient'] == 2 * S + BIT_RESERVES + inv['row_prefix_extra'], 'row identity'
    assert fin['retained_row_coefficient'] == RETAINED and fin['physical_row_coefficient'] < RETAINED
    assert fin['halving_integer_inequality'] == [M * M, 2 * 48 * 48] and max(H) == 48
    logical = g * inv['conservative_pervertex_used'] + 64
    router = inv['compiler'] * (logical + 1) * (stock + 1) ** 2
    literal = 2 * 2 ** 30000 * stock ** 2 + 8 * g * mass + 4 * stock + 4 + 32 * M
    total = g * mass + 2 ** 100000
    assert inv['local_primitive_bound'] < 2 ** 48 and logical < 2 ** 6050
    assert router.bit_length() == fin['router_bits'] and literal.bit_length() == fin['literal_bits']
    assert (32 * M * total * total).bit_length() == fin['required_C0_bits']
    assert router < 2 ** 30000 and literal < 2 ** 100000 and total < 2 ** 100001
    assert 32 * M * total * total < 2 ** 210000 and 2 * total + 18 < 2 ** 210000
    return S


PREFIX = {'fixed': lambda t: 2 * PAYLOAD, 'per_level': lambda t: t * PAYLOAD}
CAP = {'A_retained': RETAINED, 'B_bridge': (25 * RESERVE - 1) // 51}


def row(t, S, prefix):
    return t * S + BIT_RESERVES + PREFIX[prefix](t)


def bridge_ok(cap):
    return RESERVE - FACTOR * cap > 0


def check_point(t, R, S, reading, prefix, cap=None):
    """Main check: guard m^t > 2R^t, physical row < retained cap, bridge positive at that cap."""
    cap = CAP[reading] if cap is None else cap
    assert t >= 2 and R > 0 and S > 0
    assert M ** t > 2 * R ** t, f'guard fails at t={t}, R={R}'
    assert row(t, S, prefix) < cap, f'row {row(t, S, prefix)} >= cap {cap}'
    assert bridge_ok(cap), 'bridge degree_gap not positive'
    return True


def t_max(S, reading, prefix):
    ok = [t for t in T_RANGE if row(t, S, prefix) < CAP[reading]]
    assert ok == list(range(2, max(ok) + 1)), 'admissible degrees are not an initial segment'
    assert max(ok) < T_RANGE[-1], 'scan range too small'
    return max(ok)


def s_max(t, reading, prefix):
    """Largest S with row(t, S) < cap, i.e. S <= (cap - 1 - 10161 - prefix(t)) / t."""
    return (CAP[reading] - 1 - BIT_RESERVES - PREFIX[prefix](t)) // t


def sharp_row(R, S, prefix):
    """Conditional what-if (not an adopted row bound): the depth component t*S repriced at the sharp
    asymptotic coefficient c = 1/log2(73/R) of selected-coarse-depth-stock, other terms kept; the
    per-level prefix is scaled by the same c. Returns ceil(c*S) + 10161 + prefix, exact away from ties."""
    c = EVEN.divide(EVEN.ln(D(2)), EVEN.ln(EVEN.divide(D(M), D(R))))
    terms = [EVEN.multiply(c, D(S))] + ([EVEN.multiply(c, D(PAYLOAD))] if prefix == 'per_level' else [])
    for x in terms:                                  # 60-digit value is far from an integer
        assert abs(x - x.to_integral_value()) > D('1e-20')
    pre = 2 * PAYLOAD if prefix == 'fixed' else int(terms[1].to_integral_value(rounding=ROUND_CEILING))
    return int(terms[0].to_integral_value(rounding=ROUND_CEILING)) + BIT_RESERVES + pre


# ---------- ideal ceilings: own decimal interval method (correctly rounded ln/exp + 1 ulp) ----------
PREC = 60
EVEN = Context(prec=PREC, rounding=ROUND_HALF_EVEN)
DN = Context(prec=PREC, rounding=ROUND_FLOOR)
UP = Context(prec=PREC, rounding=ROUND_CEILING)


def ln_enc(k):
    v = EVEN.ln(D(k))                     # documented correctly rounded => within 1/2 ulp
    return EVEN.next_minus(v), EVEN.next_plus(v)


def cost_enc(r, a):
    """Enclosure of (r/M)^(1-a) = exp((1-a)(ln r - ln M))."""
    lr, lm = ln_enc(r), ln_enc(M)
    d_lo, d_hi = DN.subtract(lr[0], lm[1]), UP.subtract(lr[1], lm[0])
    oma = EVEN.subtract(D(1), a)
    assert oma + a == 1 and oma > 0
    x_lo, x_hi = DN.multiply(oma, d_lo), UP.multiply(oma, d_hi)
    return EVEN.next_minus(EVEN.exp(x_lo)), EVEN.next_plus(EVEN.exp(x_hi))


def idle_mass(local):
    total = (M - 1) * Q(FAMILIES, STAGES) + CENTRE
    idle = total - sum(r * n for r, n in local.items())
    assert idle.denominator == 1 and idle > 0
    return int(idle)


def relax_dec(local, R, a):
    lo = hi = D(0)
    for r, n in sorted(local.items()):
        c = cost_enc(r, a)
        lo, hi = DN.add(lo, DN.multiply(D(n), c[0])), UP.add(hi, UP.multiply(D(n), c[1]))
    c, I = cost_enc(R, a), idle_mass(local)
    lo = DN.add(lo, DN.divide(DN.multiply(D(I), c[0]), D(R)))
    hi = UP.add(hi, UP.divide(UP.multiply(D(I), c[1]), D(R)))
    return (DN.divide(DN.multiply(lo, D(STAGES)), D(FAMILIES)),
            UP.divide(UP.multiply(hi, D(STAGES)), D(FAMILIES)))


def ceiling_dec(local, R, digits=15):
    """Unique grid cell [j, j+1] * 10^-digits with relax(lo) < 1 < relax(hi)."""
    a = lambda j: D(j).scaleb(-digits)
    lo, hi = 0, 5 * 10 ** (digits - 2)          # [0, 1/20]
    assert relax_dec(local, R, a(lo))[1] < 1 < relax_dec(local, R, a(hi))[0]
    while hi - lo > 1:
        mid = (lo + hi) // 2
        v = relax_dec(local, R, a(mid))
        if v[1] < 1:
            lo = mid
        elif v[0] > 1:
            hi = mid
        else:
            raise AssertionError('decimal enclosure too wide')
    return Q(lo, 10 ** digits), Q(hi, 10 ** digits)


def relax_colkitt(C, local, R, a):
    """Second method: unmodified rational enclosures C.child_cost, own aggregation (no guard call)."""
    lo = hi = Q(0)
    for r, n in local.items():
        c = C.child_cost(r, M, a)
        lo, hi = lo + n * c[0], hi + n * c[1]
    c, k = C.child_cost(R, M, a), Q(idle_mass(local), R)
    w = Q(FAMILIES, STAGES)
    return (lo + k * c[0]) / w, (hi + k * c[1]) / w


def dec(x, n=16):
    x = Q(x)
    return str(Context(prec=n).divide(D(x.numerator), D(x.denominator)))


def main():
    nbind = bind_sources()
    inv = load_invoice()
    H, mass, local, bit_lower, complex_lower, binding = selected_word()
    assert binding == 'complex' and complex_lower < bit_lower
    S = bind_invoice(inv, H, mass)
    assert S == 2642 and inv['finite']['physical_row_coefficient'] == 16469
    # Guard thresholds by two methods, every child rank below m.
    tmin = {}
    for r in range(1, M):
        t1, t2 = least_degree(M, r), least_degree_recurrence(M, r)
        assert t1 == t2, f'guard threshold disagreement at R={r}'
        tmin[r] = t1
    assert least_degree(M, M) is None
    assert tmin[48] == tmin[51] == 2 and tmin[52] == tmin[56] == tmin[57] == 3 and tmin[58] == 4
    assert tmin[72] == 51 and M ** 50 <= 2 * 72 ** 50 and M ** 51 > 2 * 72 ** 51
    rmax = {t: r_max(t) for t in T_RANGE}
    assert all(rmax[t] <= rmax[t + 1] for t in range(2, 200)) and rmax[2] == 51 and rmax[3] == 57
    assert min(t for t in T_RANGE if rmax[t] == 72) == 51
    # Exact degree ledger.
    assert bridge_ok(CAP['B_bridge']) and not bridge_ok(CAP['B_bridge'] + 1) and bridge_ok(RETAINED)
    readings = {}
    for reading in CAP:
        for prefix in PREFIX:
            tm = t_max(S, reading, prefix)
            assert row(2, S, prefix) == 16469
            check_point(tm, rmax[tm], S, reading, prefix)
            readings[f'{reading}/{prefix}'] = dict(
                cap=CAP[reading], t_max=tm, row_at_t_max=row(tm, S, prefix),
                row_at_t_max_plus_1=row(tm + 1, S, prefix), R_max=rmax[tm],
                rank56_idle_admissible=tmin[56] <= tm, R72_admissible=tmin[72] <= tm)
    want = {'A_retained/fixed': 3, 'A_retained/per_level': 3, 'B_bridge/fixed': 181, 'B_bridge/per_level': 152}
    assert {k: v['t_max'] for k, v in readings.items()} == want
    region = {}
    for r in (48, 51, 52, 56, 57, 58, 64, 68, 71, 72):
        t = tmin[r]
        # 0 means no positive stock fits at the least admissible degree
        region[str(r)] = dict(least_degree=t, **{f'S_max[{k}/{p}]': max(s_max(t, k, p), 0) for k in CAP for p in PREFIX})
        for k in CAP:
            for p in PREFIX:
                sm = s_max(t, k, p)
                assert row(t, sm, p) < CAP[k] <= row(t, sm + 1, p)
                assert (S <= sm) == (t <= t_max(S, k, p))
    # Ideal ceilings (optimistic relaxation; no supplier, no kappa claim).
    sys.path.insert(0, str(ROOT / 'research/complex-local-word-ceiling'))
    import ceiling as C
    base = C.ceiling(local, M, FAMILIES, STAGES, CENTRE)          # unmodified, R = 51 from its guard
    old = json.loads(text('research/complex-local-word-ceiling/RESULT.json'))['ceiling']['a_ceiling']
    ceilings, table = {}, {}
    for R in range(51, M):
        lo, hi = ceiling_dec(local, R)
        f_lo, f_hi = relax_colkitt(C, local, R, lo), relax_colkitt(C, local, R, hi)
        assert f_lo[1] < 1 < f_hi[0], f'second method disagrees at R={R}'
        if R == 51:
            assert (lo, hi) == base and str(hi) == old
        table[R] = hi
        if R in (51, 57, 72):
            ceilings[str(R)] = dict(least_degree=tmin[R], a_ceiling=str(hi), a_ceiling_decimal=dec(hi),
                                   kappa_upper_bound_decimal=dec(hi / (1 + hi)))
    a51 = table[51]
    for R in ('57', '72'):
        ceilings[R]['gain_over_R51_percent'] = dec(100 * (Q(ceilings[R]['a_ceiling']) / a51 - 1), 6)
    assert all(table[R] < table[R + 1] for R in range(51, 72))
    # Least child rank whose ideal ceiling exceeds the selected bit endpoint (grid cell entirely above it).
    above = [R for R in table if table[R] - Q(1, 10 ** 15) > bit_lower]
    assert above == list(range(min(above), M)) and table[min(above) - 1] <= bit_lower
    crossing = dict(bit_lower_decimal=dec(bit_lower, 22), least_R_with_ceiling_above_bit=min(above),
                    least_degree=tmin[min(above)], ceiling_at_that_R=dec(table[min(above)]),
                    ceiling_one_rank_below=dec(table[min(above) - 1]))
    for R in ceilings:
        cap = min(Q(ceilings[R]['a_ceiling']), bit_lower)   # the selected bit endpoint caps any conversion
        ceilings[R]['kappa_upper_bound_with_bit_cap_decimal'] = dec(cap / (1 + cap))
    crossing['kappa_cap_from_bit_endpoint_decimal'] = dec(bit_lower / (1 + bit_lower))
    # Conditional what-if under reading A: sharper depth coefficient (selected-coarse-depth-stock).
    sharp = {}
    for prefix in PREFIX:
        ok = [R for R in range(49, M) if sharp_row(R, S, prefix) < RETAINED]
        assert ok == list(range(49, max(ok) + 1))
        Rs = max(ok)
        sharp[f'A_retained/{prefix}'] = dict(R_max=Rs, row_at_R_max=sharp_row(Rs, S, prefix),
                                            row_at_R_max_plus_1=sharp_row(Rs + 1, S, prefix),
                                            ceiling=dec(table[Rs]), gain_over_R51_percent=dec(100 * (table[Rs] / a51 - 1), 5))
    assert {k: v['R_max'] for k, v in sharp.items()} == {'A_retained/fixed': 59, 'A_retained/per_level': 58}
    # Robustness and direct answers.
    prefix3_max = RETAINED - 1 - 3 * S - BIT_RESERVES                 # any prefix(3) <= this admits t = 3 under A
    assert prefix3_max == 2073 and row(3, S, 'fixed') < RETAINED and 256 * 9 > prefix3_max
    depth6 = row(6, S, 'fixed')                                       # kappa010-rank-cap-floor OQ3 (depth six)
    assert depth6 == 27037 and RETAINED <= depth6 < CAP['B_bridge']
    # Conditional what-if (#3667, unadopted): 9909/252 slots slack, lean row t*S + prefix(t) under A.
    lean = {}
    for prefix in PREFIX:
        ts = [t for t in T_RANGE if row(t, S, prefix) - BIT_RESERVES < RETAINED]
        assert ts == list(range(2, max(ts) + 1))
        lean[f'A_retained/{prefix}'] = dict(t_max=max(ts), row_at_t_max=row(max(ts), S, prefix) - BIT_RESERVES,
                                           R_max=rmax[max(ts)])
    assert {k: (v['t_max'], v['R_max']) for k, v in lean.items()} == {'A_retained/fixed': (7, 66), 'A_retained/per_level': (6, 65)}
    assert row(2, S, 'fixed') - BIT_RESERVES == 6308 and max(v['R_max'] for v in lean.values()) < min(above)
    controls = run_controls(S, inv, H, mass)
    return dict(
        status='PASS_COMPLEX_HALVING_DEGREE_INVOICE_SCOPED',
        scope=('Scoped finite invoice statement under inherited PR1087-lineage transfer/bridge hypotheses; '
               'optimistic relaxation; admits nothing; no supplier, no kappa, no frontier change.'),
        source_bindings_checked=nbind,
        selected_invoice=dict(member=INVOICE, sha256=INVOICE_SHA, physical=inv['physical'], stock_bits=S,
                              physical_row=16469, retained_row=RETAINED, row_prefix_extra=inv['row_prefix_extra'],
                              router_bits=inv['finite']['router_bits'], literal_bits=inv['finite']['literal_bits'],
                              required_C0_bits=inv['finite']['required_C0_bits']),
        ledger='Row(t,S) = t*S + 10161 + prefix(t); prefix fixed = 1024 or per_level = 512*t',
        caps=dict(CAP), bridge_gap_at_B_cap=str(RESERVE - FACTOR * CAP['B_bridge']),
        readings=readings, region_by_child_rank=region,
        least_degree_by_rank={str(r): tmin[r] for r in range(48, M)},
        r_max_by_degree={str(t): rmax[t] for t in (2, 3, 4, 5, 6, 8, 10, 16, 25, 50, 51, 152, 181)},
        local_word={str(r): n for r, n in sorted(local.items())}, idle_mass_per_call=idle_mass(local),
        ceilings=ceilings, ceiling_by_rank={str(R): dec(v) for R, v in table.items()},
        bit_endpoint_crossing=crossing, controls=controls,
        invoice_independent=dict(R_max_any_degree=max(rmax.values()), note=('R <= 72 for every t and every child rank, paid or idle: R = 73 never meets the guard. '
                                   'The ceilings price only idle repacking of the fixed selected word.')),
        sharp_depth_coefficient_what_if_A=sharp, A_admits_t3_for_any_prefix3_at_most=prefix3_max,
        lean_row_what_if_A_3667=lean,
        depth6_row_fixed_prefix=dict(row=depth6, fits_A=depth6 < RETAINED, fits_B=depth6 < CAP['B_bridge']))


def must_fail(name, fn, why):
    try:
        fn()
    except AssertionError as e:
        assert why in str(e), f'control {name} failed for another reason: {e}'
        return name
    raise AssertionError(f'control {name} unexpectedly passed')


def run_controls(S, inv, H, mass):
    def mutated(path, value):
        x = json.loads(json.dumps(inv))
        node = x
        for k in path[:-1]:
            node = node[k]
        node[path[-1]] = value
        return lambda: bind_invoice(x, H, mass)
    return [
        must_fail('reading_A_t4', lambda: check_point(4, 57, S, 'A_retained', 'fixed'), 'row 21753 >= cap 20161'),
        must_fail('reading_A_per_level_t4', lambda: check_point(4, 57, S, 'A_retained', 'per_level'), 'row 22777 >= cap 20161'),
        must_fail('guard_R58_t3', lambda: check_point(3, 58, S, 'B_bridge', 'fixed'), 'guard fails at t=3, R=58'),
        must_fail('guard_R72_t50', lambda: check_point(50, 72, S, 'B_bridge', 'fixed'), 'guard fails at t=50, R=72'),
        must_fail('guard_R73_t200', lambda: check_point(200, 73, S, 'B_bridge', 'fixed'), 'guard fails at t=200, R=73'),
        must_fail('reading_B_t182', lambda: check_point(182, 72, S, 'B_bridge', 'fixed'), 'row 492029 >= cap 490196'),
        must_fail('reading_B_per_level_t153', lambda: check_point(153, 72, S, 'B_bridge', 'per_level'), 'row 492723 >= cap 490196'),
        must_fail('bridge_cap_plus_one', lambda: check_point(2, 51, S, 'B_bridge', 'fixed', cap=CAP['B_bridge'] + 1),
                  'bridge degree_gap not positive'),
        must_fail('prefix_mutation', mutated(['row_prefix_extra'], 0), 'prefix'),
        must_fail('stock_bits_mutation', mutated(['finite', 'physical_stock_bits'], S + 1), 'stock bits'),
        must_fail('physical_mutation', mutated(['physical'], inv['physical'] * 2), 'stock bits'),
    ]


if __name__ == '__main__':
    out = json.dumps(main(), indent=2, sort_keys=True) + '\n'
    path = HERE / 'RESULT.json'
    if sys.argv[1:] == ['--write']:
        path.write_text(out)
    else:
        assert sys.argv[1:] == [], __doc__
        assert path.read_text() == out, 'RESULT.json differs from the recomputation'
    r = json.loads(out)
    print(r['status'], {k: v['t_max'] for k, v in r['readings'].items()},
          {k: v['a_ceiling_decimal'] for k, v in r['ceilings'].items()}, len(r['controls']), 'controls')
