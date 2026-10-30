"""Two bounded cross-boundary readout diagnostics. No new supplier.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import argparse
import importlib.util
import json
import math

HERE = Path(__file__).resolve().parent


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, HERE.parent/relative)
    out = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(out)
    return out


B = module('shared_readout_tools', 'shared-core-blocks/audit.py')
A = module('readout_matrix_tools', 'inplace-producer-sixteenth/audit.py')
require, encode, rank, mm = B.require, B.encode, B.H.rank, B.H.mm
eye, zero, sub, add, inverse = A.identity, A.zero, A.sub, A.add, A.inverse


def scalar_core(h=5, deferred=False, omit_old=False, include_events=False):
    """Same characteristic-dependent triple identity, not matched encoding.

    All three invocations use the SAME injection matrix here. The independent
    routing control below tests whether that premise holds for shared banks.
    """
    labels = list(combinations(range(h), 3))
    n = len(labels)
    C = [[len(set(s)&set(t)) % 2 for t in labels] for s in labels]
    V = [[int(i in t) for t in labels] for i in range(h)]
    require([[x % 2 for x in row] for row in mm(list(zip(*V)), V)] == C,
            'incidence central factor')
    rows = [1 << i for i in range(2*n+h)]
    gates = []
    def xor(t, c, kind, stage):
        rows[t] ^= rows[c]
        gates.append((stage, kind, t, c))
    for stage in range(3):
        source, target = (0, n) if stage != 1 else (n, 0)
        if not omit_old:
            for t, label in enumerate(labels):
                for j in label:
                    xor(target+t, 2*n+j, 'old', stage)
        for t in range(n):
            for s in range(n):
                if s != t and C[t][s]:
                    xor(target+t, source+s, 'side', stage)
        for j in range(h):
            for s, label in enumerate(labels):
                if j in label:
                    xor(2*n+j, source+s, 'gather', stage)
        for t, label in enumerate(labels):
            for j in label:
                xor(target+t, 2*n+j, 'new', stage)
        if not deferred:
            for j in range(h):
                for s, label in enumerate(labels):
                    if j in label:
                        xor(2*n+j, source+s, 'cleanup', stage)
    expected = [1 << (n+i) for i in range(n)]+[1 << i for i in range(n)]
    expected += [1 << (2*n+j) for j in range(h)]
    result = dict(h=h, labels=labels, v=n, independent_roles=len(rows),
                binary_central_rank=B.H.binary_rank(
                    [sum(x << j for j, x in enumerate(row)) for row in C]),
                rational_rank_of_binary_matrix=rank(C),
                gates=len(gates), gate_types=dict(Counter(x[1] for x in gates)),
                exact_all_input_map=rows == expected, final_rows=rows,
                expected_rows=expected, deferred=deferred,
                old_response_omitted=omit_old)
    if include_events:
        result['events'] = gates
    return result


def routing_control(scale=1):
    """Replay the same 720-element cover used by the block preparation."""
    g = B.geometry_control(scale)
    G = [tuple(p[i]*scale+j for i in range(6) for j in range(scale))
         for p in permutations(range(6))]
    pos = {p: i for i, p in enumerate(G)}
    identity = tuple(range(6*scale))
    R = (g['r12'], identity, g['r23'])
    H = g['bank_maps']
    # Physical auxiliary a visits invocation a H_j. Data port p visits
    # p R_j. Hence the injected data is p=a H_j R_j^{-1}.
    injection = [[pos[B.compose(B.compose(a, h), r)] for a in G]
                 for h, r in zip(H, R)]  # these R_j are involutions
    N = len(G)
    residuals = []
    for a in range(N):
        row = ((1 << injection[0][a]) ^ (1 << injection[1][a]) ^
               (1 << (N+injection[1][a])) ^ (1 << (N+injection[2][a])))
        residuals.append(row)
    require(any(residuals), 'original routing does not restore carried bank')
    require(all(x.bit_count() == 4 for x in residuals), 'four uncancelled inputs')
    rank_residual = B.H.binary_rank(residuals)
    return dict(scale=scale, group_size=N,
                equal_injections=injection[0] == injection[1] == injection[2],
                bad_auxiliary_rows=sum(x != 0 for x in residuals),
                residual_binary_rank=rank_residual,
                identity_role_sources=[x[pos[identity]] for x in injection],
                residual_weight_histogram=dict(Counter(x.bit_count() for x in residuals)),
                scope='Finite coordinate subgroup routing diagnostic, not a '
                      'generic-group or production supplier certificate.')


def transpose(a):
    return [list(x) for x in zip(*a)]


def projection(rows, h):
    basis = []
    for row in rows:
        if rank(basis+[row]) > len(basis):
            basis.append(row)
    H = [[Q(i == j)-Q(1, 9) for j in range(h)] for i in range(h)]
    U = transpose(basis)
    return mm(mm(U, inverse(mm(mm(basis, H), U))), mm(basis, H))


def partial(P):
    m = len(P)
    K = sub(eye(m), P)
    return [a+b for a, b in zip(K, P)]+[a+b for a, b in zip(P, K)]


def framed_cleanup_control(deferred):
    core = scalar_core(include_events=True)
    h, n, labels = core['h'], core['v'], core['labels']
    vectors = [[Q(i in s) for i in range(h)] for s in labels]
    P = [projection([v], h) for v in vectors]
    R = [projection([v for v, s in zip(vectors, labels) if j in s], h)
         for j in range(h)]
    require(mm(P[0], P[1]) != mm(P[1], P[0]), 'noncommuting source control')
    I, Z = eye(h), zero(h)
    frames = P+[Z]*n+[Z]*h
    starts = frames.copy()
    rows = [1 << i for i in range(2*n+h)]
    hist, costs, cache = Counter(), Counter(), {}
    copied = set()
    def width(A, B):
        key = tuple(tuple(row) for row in sub(A, B))
        if key not in cache:
            cache[key] = rank(key)
        return cache[key]
    def charge(w, kind):
        if w:
            hist[w] += 1
            costs[kind] += w
    def align(role, F, kind):
        charge(width(F, frames[role]), kind)
        frames[role] = F
    for stage, kind, t, c in core['events']:
        if kind == 'new':
            align(t, Z, 'data/center path')
            require(frames[c] == R[c-2*n], 'copied center frame')
            if (stage, c) not in copied:
                charge(rank(frames[c]), 'copied readout')
                copied.add((stage, c))
        else:
            F = Z if kind == 'old' else I if kind == 'cleanup' else (
                P[c % n] if kind == 'side' else R[t-2*n])
            # Keep these boundary transports even when the cleanup XOR is
            # deleted. A producer that deletes them is a different proposal.
            align(t, F, 'data/center path')
            align(c, F, 'data/center path')
            require(frames[t] == frames[c], 'common gate frame')
        if not (deferred and kind == 'cleanup'):
            rows[t] ^= rows[c]
    ends = [I]*n+[sub(I, p) for p in P]+[I]*h
    for role, end in enumerate(ends):
        align(role, end, 'outer endpoints')
    require(rows == core['expected_rows'], 'full arbitrary-input scalar map')
    full = partial(I)
    for out_role, row in enumerate(rows):
        require(row.bit_count() == 1, 'all-role permutation')
        in_role = row.bit_length()-1
        require(mm(partial(ends[out_role]), partial(starts[in_role])) == full,
                'physical full interchange for each original input')
    return dict(deferred=deferred, h=h, independent_roles=2*n+h,
                histogram=dict(sorted(hist.items())), rank=sum(t*c for t, c in hist.items()),
                categories=dict(costs), physical_endpoints_exact=True,
                scalar_gates=sum(not (deferred and kind == 'cleanup')
                                 for stage, kind, t, c in core['events']),
                scope='Complete small bit word with retained frame transports; '
                      'not the production supplier. Full-width children are '
                      'allowed only for this unfavorable diagnostic.')


def direct_fragment(h=5, center=0):
    """One shared central readout to all incident targets, exact rational maps.

    The center's arbitrary content includes both its dirty value and whatever
    central aggregate is currently stored. Source production is held fixed.
    """
    labels = [s for s in combinations(range(h), 3) if center in s]
    vectors = [[Q(i in s) for i in range(h)] for s in labels]
    R = projection(vectors, h)
    I, Z = eye(h), zero(h)
    require(mm(R, R) == R, 'central support projector')
    u = rank(R)
    require(u == h-1, 'plain-triple star dimension')
    baseline, direct = Counter(), Counter()
    # Same 0->R->I physical center path in both words; copy is dependent.
    for hist in (baseline, direct):
        hist[u] += 1
        hist[rank(sub(I, R))] += 1
    baseline[u] += 1  # one transformed copy shared among all target reads
    target_excess = []
    for vector in vectors:
        P = projection([vector], h)
        K = sub(I, P)
        require(mm(R, P) == mm(P, R) == P, 'diagonal signal lies in center')
        baseline[rank(K)] += 1
        direct[u] += 1
        direct[rank(sub(K, R))] += 1
        target_excess.append(u+rank(sub(K, R))-rank(K))
        # Physical y,z at frames 0,R. Baseline: y += D_R z, then y->K.
        # Direct: y->R, y+=z, then y->K; retain center unchanged.
        DR, DK = partial(R), partial(K)
        transition = mm(DK, DR)
        require(mm(transition, DR) == DK, 'same original-target coefficient')
        require(DR != DK, 'omitting final target retreat fails on arbitrary targets')
        require(rank(sub(K, R)) == rank([row[h:] for row in transition[:h]]),
                'physical residual cross rank')
    baseline = {t: n for t, n in sorted(baseline.items()) if t}
    direct = {t: n for t, n in sorted(direct.items()) if t}
    baseline_mass = sum(t*n for t, n in baseline.items())
    direct_mass = sum(t*n for t, n in direct.items())
    require(all(x == 2 for x in target_excess), 'target excursion costs twice line rank')
    require(direct_mass-baseline_mass == 2*len(labels)-u, 'net fragment change')
    differences = {}
    for saving in (Q(2, 25), Q(3, 40)):
        a, b = B.H.moment(baseline, h, 1, saving)
        c, d = B.H.moment(direct, h, 1, saving)
        require(c-b > 0, 'direct fragment increases moment as well as rank')
        differences[str(saving)] = [c-b, d-a]
    return dict(h=h, center_rank=u, target_count=len(labels),
                baseline_children=baseline, direct_children=direct,
                baseline_rank=baseline_mass, direct_rank=direct_mass,
                extra_rank=direct_mass-baseline_mass,
                moment_increase_without_role_normalization=differences,
                exact_arbitrary_target_and_center_maps=True,
                normalization='Unnormalized fragment; no new independent role '
                              'is credited for the copied stream.')


def excursion_controls():
    out = []
    for m, r in ((5, 1), (5, 2), (19, 9)):
        P = [[Q(i == j and i < r) for j in range(m)] for i in range(m)]
        # R is deliberately not a projector in one control. The bound only
        # needs RP=PR=P at the visited gate, not idempotence of R.
        R = [[Q((1 if i < r else 2) if i == j else 0)
              for j in range(m)] for i in range(m)]
        R[0][-1] = 1
        I = eye(m)
        K = sub(I, P)
        require(mm(R, P) == P and mm(P, R) != P, 'one-sided block hypothesis suffices')
        target = rank(R)+rank(sub(K, R))
        require(target >= m+r, 'target detour bound')
        # Conjugate all matrices together to a noncoordinate rational basis.
        S = eye(m)
        S[0][-1] = 1
        Si = inverse(S)
        PP, RR, KK = [mm(mm(S, x), Si) for x in (P, R, K)]
        require(rank(RR)+rank(sub(KK, RR)) == target, 'basis invariance')
        require(mm(RR, PP) == PP, 'transported gate relation')
        sharp = rank(P)+rank(sub(K, P))
        require(sharp == m+r, 'sharp bound at R=P')
        out.append(dict(m=m, r=r, minimum_target_rank=m+r,
                        unvisited_target_floor=m-r,
                        source_floor=m-r, pair_floor=2*m,
                        arbitrary_matrix_control=target))
    return out


def audit():
    baseline, deferred = scalar_core(), scalar_core(deferred=True)
    require(baseline['exact_all_input_map'] and deferred['exact_all_input_map'],
            'complete scalar swap and all dirty centers restored')
    require(baseline['binary_central_rank'] == 5 and
            baseline['rational_rank_of_binary_matrix'] == 10,
            'retained characteristic-dependent central identity')
    bad = scalar_core(deferred=True, omit_old=True)
    require(not bad['exact_all_input_map'], 'old dirty response remains mandatory')
    framed = [framed_cleanup_control(x) for x in (False, True)]
    require(framed[0]['histogram'] == framed[1]['histogram'],
            'deleting scalar cleanup does not delete a recursive child')
    subsets = []
    for h in (5, 6, 23):
        for q in range(1, h+1):
            touched = math.comb(h, 3)-(math.comb(h-q, 3) if h-q >= 3 else 0)
            gap = 2*touched-q*(h-1)
            require(gap >= 0, 'no hybrid star-subset rank improvement')
            subsets.append(dict(h=h, selected_centers=q, diagonal_targets=touched,
                                removed_copy_rank=q*(h-1),
                                target_excursion_floor=2*touched, net_extra_floor=gap))
    return dict(status='Two bounded diagnostics complete; no new supplier or kappa.',
                scalar_deferred_cleanup=dict(baseline=baseline, deferred=deferred,
                    omitted_old_response_rejected=True,
                    interpretation='Aligned injections allow scalar cleanup '
                    'cancellation, but retained frame transitions and copied '
                    'readouts are unchanged. No recursive child is deleted.'),
                shared_bank_routing=[routing_control(s) for s in (1, 2)],
                framed_deferred_cleanup=framed,
                direct_readout_fragment=direct_fragment(),
                target_excursion_controls=excursion_controls(),
                hybrid_star_subsets=subsets,
                scope='Bit-side rational rank diagnostic. All-target direct '
                      'readout exclusion retains original physical role paths '
                      'and cuts; source-span gates satisfy RP=P. No claim '
                      'about arbitrary distributed or changed-endpoint readout.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    value = encode(audit())
    if args.write:
        args.write.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    if args.check:
        require(value == json.loads(args.check.read_text()), 'saved diagnostic')
    print('Boundary readout diagnostics passed; no new supplier or kappa.')
