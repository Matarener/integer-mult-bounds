#!/usr/bin/env python3
"""Noncommuting p3 BIT H endpoint and complete direct-normalization invoice.

This proves the useful factorization, then refuses the unearned global gain:
three independent interval banks retain a Q-conjugated free monodromy. The
direct endpoint repair costs six times111 rank-one queries, not twice111.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import gzip
import json
import time

import bit_native_binding as N
import mixed_productive_bit as B

HERE = Path(__file__).resolve().parent


def controller(p=3, keep=43):
    n = 2*p
    a = [[{()} if i == j else set() for j in range(n)] for i in range(n)]
    idle, events = [], []
    def add(d, s):
        a[d] = [x ^ y for x, y in zip(a[d], a[s])]
        events.append(['ADD', d, s])
    def shift(r, word):
        a[r] = [{word+term for term in entry} for entry in a[r]]
    def idle_call(pair, stages):
        index = len(idle)
        retained = bool(keep >> index & 1)
        idle.append(dict(index=index, pair=pair, stages=stages, retained=retained))
        if retained:
            for r in (2*pair, 2*pair+1):
                shift(r, tuple(reversed(stages)))
            events.append(['IDLE_T', pair, stages])
    def local(stage, pair, backward):
        x, y = 2*pair, 2*pair+1
        if backward:
            x, y = y, x
        add(y, x)
        shift(x, (stage,))
        shift(y, (stage,))
        events.append(['LOCAL_T', stage, pair, backward])
        if stage % 2 and stage <= 2*p-3:
            idle_call((stage+1)//2, list(range(stage+1)))
        elif stage % 2 == 0 and 2 <= stage <= 2*p-2:
            idle_call(stage//2, [stage])
        elif stage == 2*p:
            for j in range(p-1):
                idle_call(j, list(range(2*j+3, 2*p+1)))
    def bridge(d, s):
        add(2*d, 2*s)
        add(2*s+1, 2*d+1)
    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1:
            bridge(j, j+1)
        local(2*j+2, j, False)
        if j < p-1:
            bridge(j, j+1)
    for j in reversed(range(p-1)):
        bridge(j+1, j)
    for j in range(p):
        a[2*j], a[2*j+1] = a[2*j+1], a[2*j]
    coefficients = B.polynomial_coefficients(a)
    factor = B.simultaneous_monomial_factor(coefficients)
    B.need(factor is not None, 'Exact noncommuting interval-word diagonalization')
    return coefficients, factor, idle, events


def run():
    start = time.monotonic()
    native_path = HERE/'BIT-P3-NATIVE-BINDING.json'
    h_path = HERE/'PR589-H-NATIVE.json.gz'
    h_receipt_path = HERE/'PR589-H-COMPLETION.json'
    native = json.loads(native_path.read_text())
    hword = json.loads(gzip.decompress(h_path.read_bytes()))
    hreceipt = json.loads(h_receipt_path.read_text())
    native_checks = []
    for port in native['ports']:
        p = [[Q(x) for x in row] for row in port['central_projector']]
        rho = [[Q(x) for x in row] for row in port['chart_15']]
        k = [[Q(int(i == j))-p[i][j] for j in range(8)] for i in range(8)]
        old_hole = [[k[i][j] if i < 8 and j < 8 else Q(0) for j in range(15)] for i in range(15)]
        fresh = [[Q(i == j and i >= 8) for j in range(15)] for i in range(15)]
        active = [[p[i][j] if i < 8 and j < 8 else Q(i == j and i >= 8)
                   for j in range(15)] for i in range(15)]
        old_full = [[Q(i == j and i < 8) for j in range(15)] for i in range(15)]
        B.need(N.multiply(N.multiply(rho, old_hole), rho) == fresh,
               'Every other-stage old-hole transform is common at this local vertex')
        B.need(N.multiply(N.multiply(rho, active), rho) == old_full,
               'Own Q b_s becomes common full I8')
        native_checks.append(dict(port=port['port'], old_hole_to_fresh=True,
                                  own_active_to_old_full=True,
                                  all_other_fresh_blocks_fixed=True))
    coefficients, factor, idle, events = controller()
    expected = [(2, 1, 0)]*2+[(6, 5, 4)]*2+[(6, 5, 4, 3, 2, 1, 0)]*2
    B.need(factor['diagonal_monomials'] == expected, 'All six exact interval words')
    left, right = factor['left_rows'], factor['right_rows']
    parity = [0, 1, 0, 1, 1, 0]
    for i in range(6):
        for j in range(6):
            if left[i] >> j & 1:
                B.need(parity[i] == j % 2, 'L S = Sstar L, with no Q-valued coefficient')
            if right[i] >> j & 1:
                B.need(i % 2 == parity[j], 'S R = R Sstar, with no Q-valued coefficient')
    local = Counter({int(r): n for r, n in hreceipt['full_arbitrary_input_checks'][0]['paid'].items()})
    paid = Counter({r: 7*n for r, n in local.items()})
    idle_stages = sum(len(row['stages']) for row in idle if row['retained'])
    paid[7] += 222*idle_stages
    targets = Counter({8: 3073, 22: 444, 50: 222})
    B.need(sum(r*n for r, n in targets.items())-sum(r*n for r, n in paid.items()) == 603,
           'All actual H calls and productive helpers counted')
    corrected = paid.copy()
    corrected[1] += 666
    B.need(sum(r*n for r, n in targets.items())-sum(r*n for r, n in corrected.items()) == -63,
           'Direct Q conjugation does not have a positive rank margin')
    rows = []
    for role, word in enumerate(expected):
        rows.append(dict(role=role, T_word=list(word), H_monodromy=list(word),
                         endpoint='K F' if parity[role] else '(Q K Q) F',
                         interval_target_rank=1+7*len(word), physical_fields=111,
                         free_K_inverse=bool(parity[role]),
                         direct_rank1_normalizer_queries=0 if parity[role] else 222))
    def margins(profile):
        return {str(c): B.interval_row(B.margin_interval(profile, targets, c))
                for c in (Q(0), Q('0.003'), Q('0.0035'), Q('0.004'))}
    return dict(schema='actual-BIT-H-noncommuting-p3-global-probe/1',
                status='PASS_EXACT_ENDPOINT_FACTOR_WITH_UNFUNDED_DIRECT_HEAD_REPAIR',
                physical_local_contract='F_s/B_s = diag(T_s,Q T_s Q) times the Q-valued elementary shear; T_s=H_s b_s, H_s^2=I, [H_s,Q b_s]=0.',
                gauge='S=diag(I,Q) on each pair. Native scalar bridges commute with S. Final pair swaps contribute one common Q on the left.',
                stage_commutation='[H_s,b_t]=0 for s!=t, by the exact native chart identities. Hence each interval product M=K B, and [K,Q B]=0.',
                noncommuting_factor=factor,
                exact_free_word_coefficients={str(k): v for k, v in coefficients.items()},
                boundary_Q_parity=parity, endpoints=rows,
                native_chart_checks=native_checks,
                helper_owners=native['helper_owners'],
                raw_paid=dict(sorted(paid.items())), targets=dict(sorted(targets.items())),
                raw_rank_margin=603, raw_margins=margins(paid),
                direct_normalization=dict(rank1_children=666, paid=dict(sorted(corrected.items())),
                                          rank_margin=-63, margins=margins(corrected)),
                scalar_costs=dict(local_H_unit_ADDs=11955,
                                  common_frame_H_ADDs=1452,
                                  local_common_frame_wrappers=14,
                                  idle_common_frame_H_uses=2*idle_stages,
                                  endpoint_inverse_monodromy_H_uses=26,
                                  global_unit_ADDs_with_direct_normalization=7*11955+(14+2*idle_stages+26)*1452+22*111+12*111+9*111,
                                  owned_clear_or_erase_records=126,
                                  controller_boundary_ADDs_per_port=factor['boundary_unit_ADDs_per_port'],
                                  extra_fixed_cover_routes='Every H use and inverse has its literal per-port right routes; no physical H use is free of linear/routing tariff.'),
                owned_COPY_episodes=63,
                conclusion='The local54-rank saving is real. A full H-only p3 supplier with direct head normalization fails already at C=0. A new way to cancel/share the three interval head monodromies is required.',
                source_sha256={p.name: sha256(p.read_bytes()).hexdigest() for p in
                               (Path(__file__), native_path, h_path, h_receipt_path)},
                runtime_seconds=time.monotonic()-start, new_kappa=False)


if __name__ == '__main__':
    result = run()
    (HERE/'PR589-H-GLOBAL-PROBE.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'raw_paid', 'targets', 'raw_rank_margin', 'direct_normalization', 'runtime_seconds')}, indent=2))
