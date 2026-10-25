#!/usr/bin/env python3
"""Exact planning budget for a complex saving above .001745.

The receiver-sharing word and its literal owner invoice are frozen inputs.
The rank-48/51 rows and fusion rows are optimistic construction targets,
not emitted programs. Native word: dataisfire / staged544 lineage, with the
receiver identity credited in kappa-adaptive-continuation. Moment engine:
native-complex-moment552. New calculation with OpenAI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / 'research/kappa-adaptive-continuation/global-budget/receiver-sharing/RESULT.json'
ENGINE = REPO / 'research/native-complex-moment552/engines/moment.py'
TARGET = Q('.001745') + Q(1, 10**46) + Q(1, 10**70)


def load_engine():
    spec = importlib.util.spec_from_file_location('complex_target_moment', ENGINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, default=HERE / 'TARGET-BUDGET.json')
    args = ap.parse_args()
    src = json.loads(SOURCE.read_text())
    E = load_engine()
    T = src['replicas']
    W = src['productive_families']
    profile = {int(r): n for r, n in src['profile'].items()}
    local = {int(r): n for r, n in src['provider_local_profiles']['gauge44'].items()}
    assert T == 360 and W == 896 * T
    assert sum(r*n for r,n in profile.items()) == 65088*T

    def interval(xs):
        return {'rational': list(map(str,xs)), 'decimal': list(map(E.decimal,xs))}

    def H(r):
        l,u = E.logarithm(Q(73,r))
        x,y = E.exponential(TARGET*l,TARGET*u)
        return r*x,r*y

    M = E.moment(profile,73,W,TARGET)
    gap = tuple((x-1)*73*896 for x in M)
    assert 0 < gap[0] <= gap[1]
    fusions = []
    for r,s in ((1,1),(1,2),(2,2),(4,4),(8,8),(8,16),(16,16)):
        x,y,z = H(r),H(s),H(r+s)
        gain = x[0]+y[0]-z[1],x[1]+y[1]-z[0]
        q = gap[1]/(9*gain[0])
        n = q.numerator//q.denominator+1
        assert 9*(n-1)*gain[1] < gap[0]
        assert 9*n*gain[0] > gap[1]
        changed = dict(profile)
        for rank,count in ((r,-n*9*T),(s,-n*9*T),(r+s,n*9*T)):
            changed[rank]=changed.get(rank,0)+count
        fusions.append({'inputs':[r,s], 'output':r+s,
            'weighted_rank_saving':interval(gain),
            'smallest_uniform_occurrences_per_call':n,
            'available_in_current_profile':all(v >= 0 for v in changed.values()),
            'price_only_not_a_native_realization':True})

    idle_mass = 65088-9*sum(r*n for r,n in local.items())
    ideal = []
    for rank in (48,51):
        # Clear the denominator in idle_mass/rank to use integer counts.
        prof = {r:9*n*rank for r,n in local.items()}
        prof[rank] = prof.get(rank,0)+idle_mass
        at = E.moment(prof,73,896*rank,TARGET)
        ideal.append({'idle_rank':rank, 'idle_mass_per_replica':idle_mass,
            'all_idle_mass_fractionally_at_one_rank':True,
            'moment_at_target':interval(at),
            'root':E.certify(prof,73,896*rank),
            'physical_realization':False})
    out = {'status':'EXACT_OPTIMISTIC_COMPLEX_TARGET_BUDGET_NOT_A_NEW_SUPPLIER',
        'target_kappa':'0.001745', 'required_complex_exponent':str(TARGET),
        'outer_loss':str(TARGET-Q('.001745')),
        'baseline_root':src['root'], 'baseline_profile':profile,
        'baseline_local_profile':local,'replicas':T,'productive_families':W,
        'target_moment':interval(M),
        'required_weighted_rank_reduction_per_replica':interval(gap),
        'required_weighted_rank_reduction_per_call':interval(tuple(x/9 for x in gap)),
        'uniform_fusion_targets':fusions, 'ideal_idle_concentrations':ideal,
        'scope':'Frozen legitimate receiver-sharing word and actual owner invoice. Hypothetical fusions and ideal idle concentration carry no feasibility claim. The disputed PR3955 idle overlay is not used as a supplier.',
        'source_pins':{str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (SOURCE,ENGINE,Path(__file__))}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print(out['status'],E.decimal(gap[0]),'uniform_H1_H2_fusions_per_call',fusions[1]['smallest_uniform_occurrences_per_call'])


if __name__ == '__main__':
    main()
