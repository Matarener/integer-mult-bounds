# SPDX-License-Identifier: Apache-2.0
"""Scope D: the complex endpoint and kappa of PR #3633 from the complete profile recounted by audit_owners, with two
rational enclosures, the exact gains over the predecessors, and the improvement tests.

M_T(a) = sum_r n_r r (73/r)^a / (73 * 896 T); C is the largest 24-digit decimal with M_T(C) < 1 and M_T(C + 1e-24)
> 1; kappa = C - 1e-46 - 1e-70 (the inherited outer margins, recorded by every package of this line).  Enclosures:
audit_kappa.moment (atanh/Taylor series with explicit tails, outward rounding to 1e-60; PR3053) and
check_accounting.moment (640-bit fixed point; PR2804).  Both must accept at C and reject at C + 1e-24 (the second
covers ranks {1,2,3,4,5,7,8,16,32,48}, which contain the T488 ranks).  The improvement test asks that each
predecessor's complete profile (at its own T) is rejected at PR3633's C, i.e. the gain is a real moment gain and not
a rounding artefact.  The BIT side is not re-derived: PR3605's recorded unchanged BIT endpoint is only compared.

Rejections raise audit_common.AuditFail('endpoint.<rule>: ...') or the vendored 'kappa.*' rules.
Standard library only.
"""
from fractions import Fraction as Q

from audit_common import need

E24 = Q(1, 10 ** 24)
MARGINS = Q(1, 10 ** 46) + Q(1, 10 ** 70)
LIVE_PER_REPLICA = 896


def dec24(q):
    n = q * 10 ** 24
    need(n.denominator == 1 and n > 0, 'endpoint.format: not a positive 24-digit decimal')
    n = int(n)
    return '%d.%024d' % (n // 10 ** 24, n % 10 ** 24)


def intkeys(d):
    return dict((int(k), v) for k, v in d.items())


def moments(AK, CA, prof, a, T):
    live = LIVE_PER_REPLICA * T
    own = AK.moment(prof, a, live=live)
    ven = CA.moment(prof, a, live=live)
    need(max(own[0], ven[0]) <= min(own[1], ven[1]), 'endpoint.two_impl: enclosures disjoint at %s' % a)
    return own, ven


def endpoint(AK, CA, prof, T, C):
    """endpoint.accept / endpoint.reject in both implementations."""
    own_c, ven_c = moments(AK, CA, prof, C, T)
    need(own_c[1] < 1 and ven_c[1] < 1, 'endpoint.accept: M(C) not below 1 in both enclosures')
    own_n, ven_n = moments(AK, CA, prof, C + E24, T)
    need(own_n[0] > 1 and ven_n[0] > 1, 'endpoint.reject: M(C + 1e-24) not above 1 in both enclosures')
    return dict(C=dec24(C), M_C_minus_1=['%.4e' % float(own_c[0] - 1), '%.4e' % float(own_c[1] - 1)],
                M_next_minus_1=['%.4e' % float(own_n[0] - 1), '%.4e' % float(own_n[1] - 1)],
                vendored_agrees=True)


def run(AK, CA, recounted, claim, predecessors, bit_endpoint):
    """recounted: profile from audit_owners; claim: PR3633 CLAIM.json; predecessors: {label: (T, profile, kappa)}."""
    prof = intkeys(recounted)
    need(prof == intkeys(claim['profile']), 'endpoint.profile: recounted profile != CLAIM.json profile')
    T = claim['replicas']
    lo, hi = (Q(x) for x in claim['root_interval'])
    need(hi - lo == E24 and (lo * 10 ** 24).denominator == 1, 'endpoint.format: root_interval is not one 24-digit step')
    C = lo
    rec = dict(endpoint=endpoint(AK, CA, prof, T, C))
    kappa = Q(claim['kappa'])
    need(kappa == C - MARGINS and Q(claim['candidate_endpoint']) == kappa,
         'endpoint.kappa: CLAIM kappa/candidate_endpoint != C - 1e-46 - 1e-70')
    rec['kappa'] = str(kappa)
    gains = {}
    for label, (Tp, pp, kp) in sorted(predecessors.items()):
        g = kappa - Q(kp)
        need(g > 0, 'endpoint.gain: no gain over %s' % label)
        own = AK.moment(intkeys(pp), C, live=LIVE_PER_REPLICA * Tp)
        need(own[0] > 1, 'endpoint.improvement: %s profile is not rejected at PR3633 C' % label)
        gains[label] = dict(replicas=Tp, kappa=str(Q(kp)), gain=str(g), gain_float='%.6e' % float(g),
                            predecessor_M_at_C_minus_1='%.3e' % float(own[0] - 1))
    rec['gains'] = gains
    need(C < Q(bit_endpoint), 'endpoint.bit: complex endpoint is not below the recorded unchanged BIT endpoint')
    rec['bit'] = dict(unchanged_bit_endpoint=bit_endpoint, source='PR3605 CLAIM.json (recorded, not re-derived)',
                      complex_binds=True)
    return rec


def controls(AK, CA, AL, recounted, claim, predecessors, bit_endpoint):
    out = []
    E = lambda name, rule, fn: AL.expect(out, name, rule, fn)

    def claim_with(**kw):
        c = dict(claim)
        c.update(kw)
        return c
    lo = Q(claim['root_interval'][0])
    up = lo + E24
    E('claimed_endpoint_one_step_high', 'endpoint.accept',
      lambda: run(AK, CA, recounted, claim_with(root_interval=[str(up), str(up + E24)],
                                                kappa=str(up - MARGINS), candidate_endpoint=str(up - MARGINS)),
                  predecessors, bit_endpoint))
    down = lo - E24
    E('claimed_endpoint_one_step_low', 'endpoint.reject',
      lambda: run(AK, CA, recounted, claim_with(root_interval=[str(down), str(lo)],
                                                kappa=str(down - MARGINS), candidate_endpoint=str(down - MARGINS)),
                  predecessors, bit_endpoint))
    E('kappa_without_second_margin', 'endpoint.kappa',
      lambda: run(AK, CA, recounted, claim_with(kappa=str(lo - Q(1, 10 ** 46))), predecessors, bit_endpoint))
    E('kappa_with_doubled_second_margin', 'endpoint.kappa',
      lambda: run(AK, CA, recounted, claim_with(kappa=str(lo - Q(1, 10 ** 46) - Q(2, 10 ** 70)),
                                                candidate_endpoint=str(lo - Q(1, 10 ** 46) - Q(2, 10 ** 70))),
                  predecessors, bit_endpoint))
    bad = dict(intkeys(recounted))
    bad[48] -= 1
    E('recount_one_idle_48_short', 'endpoint.profile',
      lambda: run(AK, CA, bad, claim, predecessors, bit_endpoint))
    # A predecessor whose profile were one unpaid rank-48 child better per call-normalised replica would still lose;
    # the real control: a hypothetical predecessor at PR3633's own profile is NOT an improvement.
    same = dict(predecessors, hypothetical=(claim['replicas'], claim['profile'], str(Q(claim['kappa']) - Q(1, 10 ** 80))))
    E('predecessor_equal_to_candidate', 'endpoint.improvement',
      lambda: run(AK, CA, recounted, claim, same, bit_endpoint))
    T26, P26, _ = predecessors['PR3626']
    above = dict(predecessors, PR3626=(T26, P26, str(Q(claim['kappa']) + Q(1, 10 ** 30))))
    E('predecessor_kappa_above_candidate', 'endpoint.gain',
      lambda: run(AK, CA, recounted, claim, above, bit_endpoint))
    class DisjointEngine(object):
        @staticmethod
        def moment(prof, a, m=73, live=1):
            lo, hi = CA.moment(prof, a, m=m, live=live)
            return lo + 1, hi + 1
    E('second_enclosure_disjoint', 'endpoint.two_impl',
      lambda: run(AK, DisjointEngine, recounted, claim, predecessors, bit_endpoint))
    E('bit_endpoint_below_complex', 'endpoint.bit',
      lambda: run(AK, CA, recounted, claim, predecessors, '0.001730000000000000000000'))
    return out


# ---------------------------------------------------------------------------------------------------------------
# Downstream: PR #3653 (rohanarun, head 607a09ff) composes roger-sato's PR #3642 retimed supplier words with
# PR3633's literal T488 allocation.  If its words keep the staged helper widths, PR3633's journal (audited in scope B) hosts
# them unchanged, the idle part of the invoice is unchanged, and the complete profile is PR3633's + 4392 (L' - L).
# The fixed-inventory LP of scope A depends on the local bill only through the constant 9L: its optimal basis and dual
# are unchanged, but dual feasibility must be re-certified at the retimed endpoint (retimed_dual_certificate).

def endpoint_of(AK, prof, T, lo_guess, span=Q(1, 10 ** 5)):
    """The 24-digit endpoint of prof by bisection on the 24-digit grid (own enclosure, live 896 T)."""
    live = LIVE_PER_REPLICA * T
    lo = (lo_guess * 10 ** 24).__floor__()
    hi = ((lo_guess + span) * 10 ** 24).__floor__()
    need(AK.moment(prof, Q(lo, 10 ** 24), live=live)[1] < 1 and AK.moment(prof, Q(hi, 10 ** 24), live=live)[0] > 1,
         'downstream.bracket: initial bracket does not straddle 1')
    while hi - lo > 1:
        mid = (lo + hi) // 2
        e = AK.moment(prof, Q(mid, 10 ** 24), live=live)
        if e[1] < 1:
            lo = mid
        elif e[0] > 1:
            hi = mid
        else:
            raise AssertionError('grid point straddles 1')
    return Q(lo, 10 ** 24)


def retimed_dual_certificate(CEIL, basis, a0, a1):
    """downstream.dual: PR3633's optimal basis (scope A) stays dual feasible uniformly on [a0, a1].  The column costs
    (idle children) do not involve the local bill, so the same dual applies to the retimed supplier; this is checked
    at the retimed endpoint, not inferred from the certificate at PR3633's exponent."""
    model = CEIL.MODEL
    y = CEIL.symbolic_dual(model, basis)
    tight = positive = 0
    for cap, q in CEIL.enumerate_patterns(model['widths'], model['caps']):
        rc = dict((r, c) for r, c in CEIL.reduced_cost(model, cap, q, y).items() if c)
        if not rc:
            tight += 1
            continue
        need(CEIL.lower_uniform(rc, a0, a1) > 0,
             'downstream.dual: reduced cost of (%d, %s) not certified positive on [%s, %s]' % (cap, list(q), a0, a1))
        positive += 1
    return dict(tight=tight, strictly_positive_uniform=positive, interval=[dec24(a0), dec24(a1)])


def downstream_3653(AK, CA, AL, CW, words, staged_widths, staged_local, audited_profile, lp_per_replica, outer_claim,
                    CEIL=None, basis=None):
    T, calls = 488, 4392
    locs = []
    for tag, pid in (('base', 'gauge44'), ('extra', 'extra')):
        fr = CW.frame_recount(AL.parse_word(words[tag]))
        need(list(fr['helper_widths']) == list(staged_widths[pid]),
             'downstream.widths: PR3653 %s word changes helper widths' % tag)
        locs.append(dict((int(k), v) for k, v in fr['paid'].items()))
    need(locs[0] == locs[1], 'downstream.local: the two retimed words have different local bills')
    L1, L0 = locs[0], dict((int(k), v) for k, v in staged_local.items())
    prof = dict((int(k), v) for k, v in audited_profile.items())
    for r in set(L0) | set(L1):
        prof[r] = prof.get(r, 0) + calls * (L1.get(r, 0) - L0.get(r, 0))
    prof = dict((r, n) for r, n in sorted(prof.items()) if n)
    lp = dict((int(k), v) for k, v in lp_per_replica.items())
    lp1 = dict(lp)
    for r in set(L0) | set(L1):
        lp1[r] = lp1.get(r, 0) + 9 * (L1.get(r, 0) - L0.get(r, 0))
    need(dict((r, n) for r, n in prof.items()) == dict((r, v * T) for r, v in sorted(lp1.items()) if v),
         'downstream.ceiling: PR3653 profile is not 488 x the LP minimum with the retimed local bill')
    C = endpoint_of(AK, prof, T, Q('0.00173'))
    end = endpoint(AK, CA, prof, T, C)
    cert = retimed_dual_certificate(CEIL, basis, C, C + E24)
    kappa = Q(outer_claim['kappa_rational'])
    need(kappa == C - MARGINS, 'downstream.kappa: PR3653 kappa %s != own endpoint %s - 1e-46 - 1e-70'
         % (outer_claim['kappa'], C))
    return dict(retimed_local_bill=dict(sorted(L1.items())), delta_per_call=dict(
        sorted((r, L1.get(r, 0) - L0.get(r, 0)) for r in set(L0) | set(L1) if L1.get(r, 0) != L0.get(r, 0))),
        profile=prof, endpoint=end, kappa=str(kappa), widths_equal_staged=True,
        profile_equals_488_retimed_lp_minimum=True, dual_certificate_at_retimed_endpoint=cert)


def downstream_controls(AK, CA, AL, CW, words, staged_widths, staged_local, audited_profile, lp_per_replica,
                        outer_claim, CEIL=None, basis=None):
    out = []
    E = lambda name, rule, fn: AL.expect(out, name, rule, fn)
    run = lambda **kw: downstream_3653(AK, CA, AL, CW, kw.get('words', words), kw.get('sw', staged_widths),
                                       staged_local, kw.get('prof', audited_profile), kw.get('lp', lp_per_replica),
                                       kw.get('oc', outer_claim), CEIL, kw.get('basis', basis))
    # A feasible but suboptimal basis: swap the empty capacity-48 pattern for a non-tight one; its dual is not
    # feasible at the retimed endpoint.
    alt = list(basis)
    k = next(i for i, (cap, q) in enumerate(alt) if cap == 48 and not any(q))
    alt[k] = (48, (0, 0, 0, 0, 6, 0))
    E('downstream_dual_of_other_basis', 'downstream.dual', lambda: run(basis=alt))
    sw = dict((pid, list(ws)) for pid, ws in staged_widths.items())
    sw['gauge44'][389] = 8
    E('downstream_staged_width_389_reverted', 'downstream.widths', lambda: run(sw=sw))
    lp = dict(lp_per_replica)
    lp[48] = lp[48] - Q(1, 4)
    E('downstream_lp_minimum_one_quarter_idle48_short', 'downstream.ceiling', lambda: run(lp=lp))
    oc = dict(outer_claim)
    oc['kappa_rational'] = str(Q(outer_claim['kappa_rational']) + E24)
    E('downstream_kappa_one_step_high', 'downstream.kappa', lambda: run(oc=oc))
    return out
