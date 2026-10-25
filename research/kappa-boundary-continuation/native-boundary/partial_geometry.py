#!/usr/bin/env python3
"""Exact rank census for256 partially uniform native-chart patterns.

The census supplies no query-child deletion or profitable consumer. Source
clock intervals and native endpoint formulas are explicit. Apache-2.0;
substantial OpenAI Codex assistance.
"""
from argparse import ArgumentParser
from collections import Counter
from pathlib import Path
import json


INTERVALS = [(-1,1),(1,2),(-1,3),(3,4),(-1,5),(5,6),(2,8),(4,8),(6,8),(8,8)]


def census(selected, z=16):
    selected = set(selected)
    dims = [9+8*j+sum(s <= j for s in selected) for j in range(9)]
    normals = [j if j in selected else 0 for j in range(9)]
    m, old, zero = dims[8], Counter(), Counter()
    for previous, level in INTERVALS:
        before, after = dims[previous] if previous >= 0 else 0, dims[level]
        if level == 8:
            old[m-before] += 1
            old[m-before+(2 if normals[previous] else 0)] += 1
            zero[m-before] += 2
        elif previous < 0:
            old[after-1] += 2
            zero[after] += 2
        else:
            old[after-before] += 1
            old[after-before+(2 if normals[level] == 0 and normals[previous] else 0)] += 1
            zero[after-before] += 2
    old.pop(0, None); zero.pop(0, None)
    # A common→fixed return is one signed rank2 operation onY, not two
    # separate rank1 children. Both normals lie in disjoint global blocks.
    returns = sum(j not in selected and j-1 in selected for j in range(1,9))
    gap = Counter({1:224*len(selected)+2*z*(8-len(selected)), 2:112*returns})
    gap = +gap
    old_mass = sum(r*c for r,c in old.items())
    zero_mass = sum(r*c for r,c in zero.items())
    helper_credit = 9*(3278-18*z)
    preconsumer = 9*5070+112*old_mass+z*zero_mass-helper_credit+sum(r*c for r,c in gap.items())
    return dict(common_stages=sorted(selected), dimension=m, z=z,
        stage_full_dimensions=dims, old_current_normal_blocks=normals,
        old_idle_histogram=dict(sorted(old.items())), zero_idle_histogram=dict(sorted(zero.items())),
        old_idle_rank_mass=old_mass, zero_idle_rank_mass=zero_mass,
        gap_native_histogram=dict(sorted(gap.items())), common_to_fixed_returns=returns,
        local_rank_mass=45630, helper_credit=helper_credit,
        complete_preconsumer_rank_mass=preconsumer, productive_fields=896+8*z,
        raw_deficit=m*(896+8*z)-preconsumer,
        proven_query_child_deletions=0)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path(__file__).resolve().parent/'evidence')
    args = parser.parse_args()
    rows = [census([j for j in range(1,9) if mask >> (j-1) & 1]) for mask in range(256)]
    if (rows[0]['raw_deficit'], rows[-1]['raw_deficit']) != (384,0):
        raise ValueError('independent endpoint controls')
    result = dict(status='PASS_PARTIAL_UNIFORM_CHART_RANK_CENSUS', patterns=rows,
        interval_clock=INTERVALS, candidate_count=256,
        scope='Exact child-rank census for the stated mixed chart endpoint formulas; only the all-uniform81 and predecessor all-fixed73 full native traces are separately replayed. No new complete mixed helper allocation or query fusion is supplied.',
        return_native_recipe='For a common→fixed return, Y multiplies C_qprevious C_q0^-1. One H2 on orthogonal axes[qprevious,q0], followed by translationq0, realizes it exactly.',
        local_exterior='Common stages use a fresh9-block and the full previous exterior. Fixed stages useq0 plus a fresh8-block; removeq0 from the old-port exterior and remove the virtual unit from each zero-port exterior.',
        idle_reason='Moving to a fresh current normal fills the previous Y hole while omitting one new direction, preserving raw idle rank. Returning to fixedq0 instead requires both the old-normal fill and an inverseq0; final completion uses this same rule.',
        conclusion='Uniformization has an explicit geometry cost. A prospective fused query word must identify its actual deleted children before this rank census can imply a kappa improvement.')
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'PARTIAL-GEOMETRY-CENSUS.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()
