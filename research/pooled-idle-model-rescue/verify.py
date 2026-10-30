#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pooled per-replica idle model: convert #1685's optimum into a ceiling, and show that
the two-unpaid-coordinates premise is admissible here though not in the per-call model.

Imports the credited exact rational interval arithmetic of
`research/complex-local-word-ceiling/ceiling.py`. Does not reimplement it.

Produced by Nick Petalas with AI assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
import platform
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import pooled as P  # noqa: E402
from pooled import C  # noqa: E402

SELECTED_LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
M = 73
PAIRS, PORTS, STAGES, CENTRE = 4, 112, 9, 64
REPLICAS = 16
FAMILIES_PER_REPLICA = 2 * PAIRS * PORTS             # 896 live data families per replica
W_PER_CALL = Q(FAMILIES_PER_REPLICA, STAGES)         # 896/9 live families per call
CALLS = STAGES * REPLICAS                       # 9 stage invocations x 16 replicas = 144 calls
W_REPLICA = W_PER_CALL * CALLS                       # 14336 live families pooled
GRID = Q(1, 10 ** 15)
SELECTED_KAPPA = Q(836330098538459, 500000000000000000)
# Published realised per-replica idle histograms (PR #1685 README; incumbent README).
REALIZED_IDLE = {
    'selected_1094': {1: 2276, 3: 377, 7: 7, 48: 4866},
    'pr1042': {1: 2249, 2: 1, 3: 400, 7: 3, 16: 47, 48: 4850},
}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def source_sha256():
    out = {}
    for rel in ('research/complex-local-word-ceiling/ceiling.py',
                'research/complex-local-word-ceiling/verify.py',
                'research/complex-local-word-ceiling/levers.py',
                'research/idle-packing-stability/verify.py',
                'research/idle-packing-stability/README.md',
                'certificates/selected-result.json',
                'research/community-frontier1094-audit/ASSEMBLY.json'):
        out[rel] = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
    return out


# ---------------------------------------------------------------- controls

def exhaustive_idle_optimum_control():
    """Dynamic programming over ALL integer histograms: the closed form is the exact optimum.

    For every integer mass <= 40 and cap <= 9 no partition is skipped, because dp[s] ranges
    over every admissible final child rank.
    """
    checked = 0
    m, a = 9, Q(1, 10)
    for R in range(2, 10):
        for mass in range(0, 41):
            dp = [None] * (mass + 1)
            dp[0] = Q(0)
            for s in range(1, mass + 1):
                best = None
                for r in range(1, min(R, s) + 1):
                    if dp[s - r] is not None:
                        v = dp[s - r] + C.child_cost(r, m, a)[0]
                        if best is None or v < best:
                            best = v
                dp[s] = best
            greedy = Q(0)
            for r, n in P.optimal_idle_histogram(mass, R).items():
                greedy += n * C.child_cost(r, m, a)[0]
            require(dp[mass] is not None, 'dp unreachable')
            require(greedy == dp[mass],
                    'closed form is not the integer optimum (mass %d cap %d)' % (mass, R))
            checked += 1
    return checked


def realised_packing_exclusion_control(ceiling):
    """Both published realised idle histograms are inadmissible at the pooled ceiling.

    Prices the COMPLETE replica: the local word once per call plus the published idle
    histogram, over W = 14336 live families.
    """
    out = {}
    for label, hist in REALIZED_IDLE.items():
        mass = sum(r * n for r, n in hist.items())
        require(mass == 1646 * CALLS, '%s idle mass changed: %d' % (label, mass))
        require(all(1 <= r <= C.max_idle_rank(M) for r in hist),
                '%s idle rank outside the outer halving guard' % label)
        full = {r: CALLS * n for r, n in SELECTED_LOCAL.items()}
        for r, n in hist.items():
            full[r] = full.get(r, 0) + n
        lo, hi = P.histogram_moment(full, M, W_REPLICA, ceiling)
        require(lo > 1, '%s realised packing not excluded at the pooled ceiling' % label)
        out[label] = {'moment_over_1e15': int(lo * 10 ** 15), 'excluded': True}
    return out


def pooled_vs_percall_ordering_control():
    """The pooled ceiling is at least the per-call ceiling: pooling only relaxes."""
    import random
    rng = random.Random(20261018)
    checked = 0
    widths = set()
    for _ in range(240):
        m = rng.choice([9, 13, 17, 23, 29, 37, 45, 51, 64, 73])
        if C.max_idle_rank(m) < 2:
            continue
        stages = rng.choice([3, 5, 9])
        reps = rng.choice([1, 2, 4, 16])
        pairs = rng.choice([2, 3, 4])
        ports = rng.choice([32, 48, 64, 112])
        fam = 2 * pairs * ports
        calls = stages * reps          # one invocation per stage per replica
        W = fam * reps                # live families pooled over the replicas
        w = Q(fam, stages)            # live families carried by one call
        centre = rng.choice([16, 32, 64])
        unpaid = rng.choice([1, 2])
        local = {}
        for _ in range(rng.randint(1, 5)):
            r = rng.randint(1, max(1, m - unpaid - 1))
            local[r] = local.get(r, 0) + rng.randint(1, 60)
        # Shrink to fit the per-call coverage budget so admissible templates are common.
        budget = (m - unpaid) * w + centre
        while local and sum(r * n for r, n in local.items()) > budget:
            r = max(local, key=lambda k: (local[k], k))
            local[r] -= 1
            if local[r] == 0:
                del local[r]
        if not local:
            continue
        q = None
        try:
            q = P.replica_model(local, m, w, calls, centre, unpaid)
        except ValueError:
            continue
        a = Q(rng.randint(1, 400), 10 ** 6)
        opt = P.optimal_idle_histogram(int(q['idle_mass']), q['R'])
        hist = {r: calls * n for r, n in local.items()}
        for r, n in opt.items():
            hist[r] = hist.get(r, 0) + n
        plo, phi = P.histogram_moment(hist, m, W, a)
        # The per-call relaxation is the fractional incumbent priced on one call.
        flo, fhi = C.relax(local, m, fam, stages, centre, a, unpaid=unpaid)
        require(phi >= flo, 'pooled integer moment below the per-call fractional relaxation')
        require(plo <= phi, 'pooled envelope inverted')
        widths.add(m)
        checked += 1
    require(len(widths) >= 8, 'ordering control covered too few widths: %r' % sorted(widths))
    return checked, sorted(widths)


def rejection_controls():
    """Five semantic rejections: each must fail loudly rather than return a bracket."""
    cases = []

    def fails(fn, label):
        try:
            fn()
        except ValueError:
            cases.append(label)
            return
        raise AssertionError('control did not reject: ' + label)

    fails(lambda: P.pooled_ceiling(SELECTED_LOCAL, M, W_PER_CALL, CALLS, CENTRE,
                                   unpaid=2, R=52), 'rank cap 52 violates the halving guard')
    fails(lambda: C.model({1: 99999999}, M, FAMILIES_PER_REPLICA, STAGES, CENTRE),
          'local word pays more mass than the coverage law allows')
    fails(lambda: P.pooled_ceiling(SELECTED_LOCAL, M, W_PER_CALL, CALLS, CENTRE,
                                   unpaid=M), 'unpaid coordinate count equal to m rejected')
    fails(lambda: P.optimal_idle_histogram(10, 0), 'zero idle rank cap rejected')
    fails(lambda: P.replica_model(SELECTED_LOCAL, M, W_PER_CALL, 0, CENTRE),
          'zero call count rejected')
    return cases


def unpaid_premise_split():
    """At `unpaid = 2` a single CALL has no integer packing; pooling calls has one.

    The per-call live-family count is `w = 896/9`, not an integer, so the per-call residual
    `71*w + 64 - 5586` is `13918/9`. Pooling the replica's nine stage invocations multiplies
    it by nine and clears the denominator. The premise's integrality obstruction is therefore
    an artefact of the per-call accounting, not of the coverage law.
    """
    lmass = sum(r * n for r, n in SELECTED_LOCAL.items())
    per_call_idle = (M - 2) * W_PER_CALL + CENTRE - lmass
    require(per_call_idle.denominator != 1,
            'per-call idle mass at unpaid=2 is unexpectedly integral')
    try:
        P.replica_model(SELECTED_LOCAL, M, W_PER_CALL, 1, CENTRE, unpaid=2)
        raise AssertionError('per-call model accepted a non-integral idle premise')
    except ValueError:
        pass
    levels = {}
    for label, calls in (('one_replica', STAGES), ('sixteen_replicas', CALLS)):
        lo, hi, opt, q = P.pooled_ceiling(SELECTED_LOCAL, M, W_PER_CALL, calls, CENTRE,
                                          grid=GRID, unpaid=2)
        require(q['idle_mass'].denominator == 1, '%s unpaid=2 idle mass not integral' % label)
        require(int(q['idle_mass']) == sum(r * n for r, n in opt.items()),
                '%s unpaid=2 optimum mass mismatch' % label)
        levels[label] = {
            'calls': calls,
            'live_families_W': str(q['W']),
            'idle_mass': int(q['idle_mass']),
            'integer_packing_exists': True,
            'optimum': {str(k): v for k, v in sorted(opt.items())},
            'ceiling': str(hi),
            'ceiling_decimal': float(hi),
            'kappa_cap_decimal': float(hi / (1 + hi)),
            'headroom_pct': float((hi / (1 + hi) - SELECTED_KAPPA) / SELECTED_KAPPA * 100),
        }
    return {
        'per_call_idle_mass': str(per_call_idle),
        'per_call_integer_packing_exists': False,
        'pooled_levels': levels,
        'pooled_idle_mass': levels['sixteen_replicas']['idle_mass'],
        'pooled_integer_packing_exists': True,
        'pooled_optimum': levels['sixteen_replicas']['optimum'],
        'pooled_ceiling': levels['sixteen_replicas']['ceiling'],
        'pooled_ceiling_decimal': levels['sixteen_replicas']['ceiling_decimal'],
        'pooled_kappa_cap_decimal': levels['sixteen_replicas']['kappa_cap_decimal'],
        'pooled_headroom_pct': levels['sixteen_replicas']['headroom_pct'],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    L = SELECTED_LOCAL

    # --- baseline pooled ceiling: converts #1685's proved optimum into a ceiling
    lo, hi, opt, q = P.pooled_ceiling(L, M, W_PER_CALL, CALLS, CENTRE, grid=GRID)
    require(q['idle_mass'] == 237024, 'replica idle mass changed: %s' % q['idle_mass'])
    require(opt == {51: 4647, 27: 1},
            'pooled optimum disagrees with PR #1685: %r' % (opt,))
    # The incumbent fractional ceiling, for comparison.
    # The incumbent prices one call with families = 896 (it divides by `stages` itself).
    frac_lo, frac_hi = C.ceiling(L, M, FAMILIES_PER_REPLICA, STAGES, CENTRE, grid=GRID)
    require(hi <= frac_hi, 'pooled ceiling exceeds the incumbent fractional ceiling')
    require(hi < frac_hi, 'expected a strict tightening against the fractional relaxation')
    # Both sides of the bracket are certified, neither vacuous.
    require(P.histogram_moment(
        {**{r: CALLS * n for r, n in L.items()}, **opt}, M, W_REPLICA, hi)[0] > 1,
        'pooled moment at the ceiling is not above one')
    require(P.histogram_moment(
        {**{r: CALLS * n for r, n in L.items()}, **opt}, M, W_REPLICA, lo)[1] < 1,
        'pooled moment below the ceiling is not below one')
    kappa_pooled = hi / (1 + hi)

    # --- the two-unpaid premise, admissible here but not per call
    unpaid = unpaid_premise_split()

    # --- controls
    n_exh = exhaustive_idle_optimum_control()
    n_mono, widths = pooled_vs_percall_ordering_control()
    rejected = rejection_controls()
    excluded = realised_packing_exclusion_control(hi)

    result = {
        'schema': 'integer-mult-research-result/v1',
        'package': 'pooled-idle-model-rescue',
        'claim': ('Pooling the 144 calls of a replica into one idle child multiset gives '
                  '(a) the ceiling that PR #1685 proved the optimum for but declined to '
                  'state, and (b) an integer packing for the two-unpaid-coordinates premise '
                  'that the per-call model admits no packing for.'),
        'no_new_kappa': True,
        'selected': {
            'local_profile': {str(k): v for k, v in sorted(L.items())},
            'm': M, 'pairs': PAIRS, 'ports': PORTS, 'stages': STAGES, 'centre_per_call': CENTRE,
            'families_per_replica': FAMILIES_PER_REPLICA,
            'replicas': REPLICAS,
            'calls_pooled': CALLS,
            'live_families_per_call': str(W_PER_CALL),
            'live_families_pooled_W': str(W_REPLICA),
        },
        'baseline_unpaid_1': {
            'idle_mass_pooled': int(q['idle_mass']),
            'idle_rank_cap_R': q['R'],
            'pooled_integer_optimum': {str(k): v for k, v in sorted(opt.items())},
            'matches_pr1685_optimum': True,
            'incumbent_fractional_ceiling': str(frac_hi),
            'pooled_integer_ceiling': str(hi),
            'pooled_integer_ceiling_decimal': float(hi),
            'relative_tightening_pct': float((frac_hi - hi) / frac_hi * 100),
            'pooled_kappa_cap_decimal': float(kappa_pooled),
            'pooled_headroom_pct': float((kappa_pooled - SELECTED_KAPPA) / SELECTED_KAPPA * 100),
        },
        'two_unpaid_premise': unpaid,
        'selected_kappa_decimal': float(SELECTED_KAPPA),
        'controls': {
            'exhaustive_integer_idle_optima_checked': n_exh,
            'pooled_not_below_percall_fractional_cases': n_mono,
            'pooled_vs_percall_widths_covered': widths,
            'rejected_invalid_inputs': rejected,
            'published_realised_packings_excluded_at_pooled_ceiling': excluded,
        },
        'sources_sha256': source_sha256(),
        'environment': {'python': platform.python_version(),
                        'implementation': platform.python_implementation()},
    }

    out = HERE / 'RESULT.json'
    if args.write:
        out.write_text(json.dumps(result, indent=1, sort_keys=True) + '\n')
    else:
        want = json.loads(out.read_text())
        require(json.dumps(result, indent=1, sort_keys=True) == json.dumps(want, indent=1, sort_keys=True),
                'committed RESULT.json differs from the recomputed result')

    print('pooled idle %d, R = %d, optimum %s' % (int(q['idle_mass']), q['R'], opt))
    print('incumbent fractional ceiling a < %s' % frac_hi)
    print('pooled integer ceiling       a < %s   (tightening %.4f%%)'
          % (hi, float((frac_hi - hi) / frac_hi * 100)))
    print('pooled kappa cap < %.15f, headroom over selected %+.4f%%'
          % (float(kappa_pooled), float((kappa_pooled - SELECTED_KAPPA) / SELECTED_KAPPA * 100)))
    print('two-unpaid premise: per-call idle %s (no integer packing); pooled idle %d, optimum %s'
          % (unpaid['per_call_idle_mass'], unpaid['pooled_idle_mass'], unpaid['pooled_optimum']))
    print('  two-unpaid pooled ceiling a < %s, kappa cap %.15f, headroom %+.4f%%'
          % (unpaid['pooled_ceiling'], unpaid['pooled_kappa_cap_decimal'],
             unpaid['pooled_headroom_pct']))
    print('controls: %d exhaustive optima, %d ordering cases, %d rejections, %d realised packings excluded'
          % (n_exh, n_mono, len(rejected), len(excluded)))
    print('PASS_POOLED_IDLE_MODEL_RESCUE')


if __name__ == '__main__':
    main()