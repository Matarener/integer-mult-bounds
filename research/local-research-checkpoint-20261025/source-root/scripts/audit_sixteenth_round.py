#!/usr/bin/env python3
"""Bounded domain and mechanism screens; no new supplier or theorem domain.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

import prepare_kappa_sixteenth as prep

D = prep.domain
H, BETA, KAPPA = Q(1, 10**6), Q(1, 100), Q(1, 16)
SOURCES = [
    'notes/structured-bulk-assembly.tex',
    'notes/stopped-product-interface.tex',
    'notes/general-clifford-frames.tex',
    'references/copied-fixed/pr34/ASSEMBLY_PROOF.md',
    'references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md',
    'references/semantic-bulk/rad20/reports/downstream-microbox-resampling.md',
    'references/semantic-bulk/rad20/reports/compact-arbitrary-source-routing.md',
    'research/coordinated-frames-and-entrance-banks/bit/prove.py',
    'research/coordinated-frames-and-entrance-banks/references/pr141/balanced_stopped.py',
    'research/coordinated-frames-and-entrance-banks/RESEARCH-REVIEW.md',
    'research/shared-aggregate-followup/STATUS.md',
    'research/kappa-nine/ASSESSMENT.md',
]


class Interval:
    """Exact outward interval operations, without machine floats."""
    def __init__(self, lo, hi=None):
        D.require(type(lo) in (int, Q) and (hi is None or type(hi) in (int, Q)),
                  'Exact interval endpoints required')
        self.lo, self.hi = Q(lo), Q(lo if hi is None else hi)
        D.require(self.lo <= self.hi, 'Reversed interval')

    @staticmethod
    def cast(x):
        return x if isinstance(x, Interval) else Interval(x)

    def __add__(self, other):
        b = self.cast(other)
        return Interval(self.lo + b.lo, self.hi + b.hi)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -self.cast(other)

    def __rsub__(self, other):
        return self.cast(other) + -self

    def __mul__(self, other):
        b = self.cast(other)
        values = [x * y for x in (self.lo, self.hi) for y in (b.lo, b.hi)]
        return Interval(min(values), max(values))

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = self.cast(other)
        D.require(b.lo * b.hi > 0, 'Interval divisor includes zero')
        return self * Interval(1 / b.hi, 1 / b.lo)

    def record(self):
        return dict(lower=str(self.lo), upper=str(self.hi))


def reduced_slacks(a, b):
    """Algebraically reduced slacks on a<b and beta=1/100, h=1e-6.

    The accompanying note derives the cancellations. Point comparisons with
    the pinned original body are regressions; interval bounds prove the box
    for these reduced expressions, not by extrapolating samples.
    """
    q = a * (1 - 2 * H)
    eps = (1 - H) / (1 + q) if isinstance(a, Q) else Interval(1 - H) / (1 + q)
    G = 1 - H - eps
    r, c = G + H / 2, q + H / 4
    leaf_gap = (1 - BETA) * b - q
    slacks = dict(a_positive=a, a_below_b=b-a, b_below_one_over32=Q(1,32)-b,
        beta_positive=BETA, beta_below_one=1-BETA,
        phase_leaf_above_bit=(1-BETA)*b-a,
        q_positive=q, q_below_internal=2*a*H, q_below_leaf=leaf_gap,
        c_positive=c, c_below_one=1-c, q_below_reservations=H/4,
        lambda_above_tau=a*H, lambda_above_sigma=b-a+a*H,
        lambda_above_internal=a*H, lambda_prime_above_lambda=a*H,
        compact_leaf=leaf_gap, compact_reservations=H/4, lambda_prime_below_one=q,
        epsilon_positive=eps, epsilon_below_one=G+H, guard_width=G+H,
        K_geometry=H-eps*H/4, K_dominates_log=eps*c,
        record_suffix=G+H, phase_local=G+7*H/8, phase_boundary=G+3*H/8,
        gamma_sublinear=H/2, cell_above_band=Q(1,2)-G/2-3*H/4,
        prime_interval_packing=G+H, alpha_positive=r, alpha_below_one=1-r,
        alpha_below_one_fourth=Q(1,4)-r, delta_positive=H/8,
        delta_below_one_eighth=Q(1,8)-H/8, short_record_fallback=eps-a,
        small_field_exposure=H, artificial_boundary=8-eps+3*H/8,
        literal_scalar_guard=Q(1), row_product_gap=Q(1))
    margins = dict(g1=G+H, g2=a, g3=G, g4=a,
                   g5=G+3*H/8, g6=G+7*H/8, g7=eps)
    slacks.update({key+'_above_kappa': value-KAPPA for key,value in margins.items()})
    return slacks


def region_screen():
    a, b = Interval(Q(7,100), Q(71,1000)), Interval(Q(3,40), Q(19,250))
    bounds = {key: Interval.cast(value) for key,value in reduced_slacks(a,b).items()}
    excluded = {'b_below_one_over32', 'literal_scalar_guard', 'row_product_gap'}
    D.require(len(bounds) == 47 and all(v.lo > 0 for k,v in bounds.items() if k not in excluded),
              'Target region failed')
    D.require(bounds['b_below_one_over32'].hi < 0, 'Domain guard unexpectedly passes')
    expected = D.assembly_function(lambda f,row:f, lambda ok,msg:None)
    assumed = dict(bit_uniform=dict(ordinary_saving=Q(1,10)),
                   semantic=dict(C0=1,strict_literal_gap=1), rows=dict(degree_gap=1))
    points = 0
    for aa in (a.lo, (a.lo+a.hi)/2, a.hi):
        for bb in (b.lo, (b.lo+b.hi)/2, b.hi):
            actual = expected(assumed,{},aa,KAPPA,beta=BETA,h=H,a_complex=bb)['constraints']
            D.require(actual == reduced_slacks(aa,bb), 'Reduced expression mismatch')
            points += 1
    budget = prep.prepare()['illustrative_supplier_budget']
    D.require(a.hi < Q(budget['effective_bit']), 'Box exceeds hypothetical bit wrapper')
    return dict(status='44 exponent slacks positive throughout box; bridge gaps assumed; domain guard fails',
                a=a.record(), b=b.record(), beta=str(BETA), backoff=str(H),
                kappa=str(KAPPA), slacks={k:v.record() for k,v in bounds.items()},
                original_body_comparison_points=points,
                note='Point replays check transcription only; exact interval arithmetic bounds the whole box')


def powered_floor(m, cap, mass_fraction, saving):
    D.require(type(saving) is Q and 0 < saving < 1 and 0 < cap < m and
              0 < mass_fraction <= 1, 'Invalid floor inputs')
    return mass_fraction**saving.denominator * Q(m,cap)**saving.numerator


def mechanism_screens():
    name = D.PACKAGE+'certificate.json'
    certificate = json.loads(D.pinned_bytes(D.ROOT/name,D.PINS[name]))
    rows = {}
    for side, saving in [('complex',Q(3,40)),('bit',Q(2,25))]:
        p = certificate[side]['profile']
        m, cap = p['m'], p['maxchild']
        D.require(p['deficit_per_vertex'] == 2*p['v']-3*p['loss'], 'Baseline deficit identity')
        # Optimistically erase all scratch AND losses in that ledger.
        gross_mass = 1-Q(1,m)
        current_cap_floor = powered_floor(m,cap,gross_mass,saving)
        D.require(current_cap_floor > 1, 'Gross ledger unexpectedly passes')
        required_defect = next(r for r in range(1,m)
            if powered_floor(m,cap,1-Q(r,m),saving) < 1)
        gross_required_cap = next(t for t in range(1,m)
            if powered_floor(m,t,gross_mass,saving) < 1)
        scale = Q(p['W_per_vertex']).denominator
        W, mass = int(scale*Q(p['W_per_vertex'])), scale*p['rank_per_vertex']
        actual_fraction = Q(mass,W*m)
        actual_required_cap = next(t for t in range(1,m)
            if powered_floor(m,t,actual_fraction,saving) < 1)
        three_cap = min(3*cap,m-1)
        three_floor = powered_floor(m,three_cap,actual_fraction,saving)
        # Integer concavity relaxation, permitting otherwise illegal global packing.
        n, remainder = divmod(mass,m-1)
        hist = {str(m-1):n}
        if remainder: hist[str(remainder)] = 1
        relaxed = dict(m=m,W_per_vertex=W,rank_per_vertex=mass,
                       deficit_per_vertex=W*m-mass,maxchild=m-1,child_histogram=hist)
        moment = prep.moment_screen(relaxed,saving)
        depth = 1
        while m**depth <= 2*(m-1)**depth: depth += 1
        rows[side] = dict(saving=str(saving), dimension=m,current_maxchild=cap,
            gross_ledger_powered_floor=str(current_cap_floor),
            gross_ledger_excluded=True,
            optimistic_minimum_defect_per_data_role=required_defect,
            optimistic_minimum_maxchild_with_rank_one_budget=gross_required_cap,
            necessary_maxchild_at_current_mass=actual_required_cap,
            three_piece_packing_cap=three_cap,
            three_piece_powered_floor=str(three_floor),
            three_piece_packing_excluded=three_floor>1,
            unrestricted_packing=dict(status='RELAXATION ONLY: cross-edge and cross-role batching unproved',
                scale=scale,roles=W,rank_mass=mass,histogram=hist,moment=moment,
                halving_depth=depth))
    return rows


def audit():
    return dict(status='BOUNDED RESEARCH ROUND; no new bound or domain extension certified',
        source_sha256={**D.PINS,**{p:sha256((D.ROOT/p).read_bytes()).hexdigest() for p in SOURCES}},
        domain_region=region_screen(),mechanisms=mechanism_screens(),
        published_control=D.published_control())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--write',type=Path)
    group.add_argument('--check',type=Path)
    args = parser.parse_args()
    result = audit()
    if args.check:
        D.require(json.loads(args.check.read_text())==result,'Round receipt differs')
        print('PASS domain-box and scoped mechanism screens; no new supplier certified')
    elif args.write:
        args.write.write_text(json.dumps(result,indent=2)+'\n')
    else:
        print(json.dumps(result,indent=2))


if __name__=='__main__':main()
