#!/usr/bin/env python3
"""Independent-stage physical idle allocation in a fixed scalar controller.

Each local stage may apply its D_s to any additional physical fields at
the same time cut.  Conjugating this field projector by the exact Q-Laurent
prefix exposes whether it is constant and compatible with the final Q
eigenspaces.  Compatible stage projectors are simultaneously refined.
This is a broader discovery probe, with native hosting and transfer open.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import math
import time

import complex_controller_factor as C
import mixed_productive_bit as B

HERE = Path(__file__).resolve().parent


def addpoly(a, b, shift=0, coefficient=1):
    result = dict(a)
    for power, value in b.items():
        key = power+shift
        result[key] = result.get(key, 0)+coefficient*value
        if not result[key]:
            del result[key]
    return result


def mulpoly(a, b):
    out = {}
    for power, value in a.items():
        out = addpoly(out, b, power, value)
    return out


def scalar_prefixes(p):
    n = 2*p
    identity = [[{0:1} if i == j else {} for j in range(n)] for i in range(n)]
    matrix = [[dict(x) for x in row] for row in identity]
    inverse = [[dict(x) for x in row] for row in identity]
    cuts, events = [], []

    def add(d, s, coefficient, q=0):
        matrix[d] = [addpoly(a, b, q, coefficient) for a, b in zip(matrix[d], matrix[s])]
        for row in inverse:
            row[s] = addpoly(row[s], row[d], q, -coefficient)
        events.append(["ADD", d, s, coefficient, q])

    def local(stage, pair, reverse):
        x, y = 2*pair, 2*pair+1
        if reverse:
            x, y = y, x
        add(y, x, -1 if reverse else 1, 1 if reverse else -1)
        transported = []
        for k in range(n):
            polynomial = {}
            for i in range(n):
                for j in range(n):
                    for power, value in mulpoly(inverse[i][k], matrix[k][j]).items():
                        polynomial.setdefault(power, [[0]*n for _ in range(n)])[i][j] += value
            transported.append({power:a for power,a in polynomial.items() if any(any(row) for row in a)})
        cuts.append(dict(stage=stage, pair=pair, transported=transported))

    def bridge(d, s, coefficient):
        add(2*d, 2*s, coefficient)
        add(2*s+1, 2*d+1, -coefficient)

    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1:
            bridge(j, j+1, 1)
        local(2*j+2, j, False)
        if j < p-1:
            bridge(j, j+1, -1)
    for j in reversed(range(p-1)):
        bridge(j+1, j, 1)
    for j in range(p):
        matrix[2*j], matrix[2*j+1] = matrix[2*j+1], [{q:-v for q,v in entry.items()} for entry in matrix[2*j]]
    coefficients = {}
    for i, row in enumerate(matrix):
        for j, entry in enumerate(row):
            for q, value in entry.items():
                coefficients.setdefault((q,), [[Q(0)]*n for _ in range(n)])[i][j] += value
    coefficients = {q:a for q,a in coefficients.items() if any(any(row) for row in a)}
    factor = C.factor(coefficients)
    B.need(factor is not None, "Scalar Q controller diagonalizes")
    total = [[sum(a[i][j] for a in coefficients.values()) for j in range(n)] for i in range(n)]
    total_inverse = B.rational_inverse(total)
    end = {q[0]:B.matrix_multiply(total_inverse,a) for q,a in coefficients.items()}
    return cuts, end, factor, events


def commute(a, b):
    return multiply(a,b) == multiply(b,a)


def multiply(a, b):
    n = len(a)
    output = [[0]*n for _ in range(n)]
    for i,row in enumerate(a):
        for k,value in enumerate(row):
            if value:
                for j,second in enumerate(b[k]):
                    if second:
                        output[i][j] += value*second
    return output


def candidates(cut, end, p):
    n = 2*p
    active = 3 << (2*cut["pair"])
    result = []
    for mask in range(1 << n):
        if mask & active != active:
            continue
        coefficients = {}
        for k in range(n):
            if mask >> k & 1:
                for q, a in cut["transported"][k].items():
                    target = coefficients.setdefault(q, [[0]*n for _ in range(n)])
                    for i in range(n):
                        for j in range(n):
                            target[i][j] += a[i][j]
        coefficients = {q:a for q,a in coefficients.items() if any(any(row) for row in a)}
        if set(coefficients) != {0}:
            continue
        a = coefficients[0]
        if not all(commute(a,b) for b in end.values()):
            continue
        result.append(dict(field_mask=mask, rank=mask.bit_count(), projector=a))
    return result


def refine(joint, projector, stage):
    result = {}
    for (q, mask), a in joint.items():
        yes = multiply(a, projector)
        no = [[x-y for x,y in zip(row, second)] for row,second in zip(a,yes)]
        if any(any(row) for row in yes):
            result[(q,mask | (1 << stage))] = yes
        if any(any(row) for row in no):
            result[(q,mask)] = no
    return result


def search(p, Ctarget=0.003, limit=200000):
    start = time.monotonic()
    cuts, end, factor, events = scalar_prefixes(p)
    choices = [sorted(candidates(cut,end,p),key=lambda c:(c['rank'],c['field_mask'])) for cut in cuts]
    print(json.dumps(dict(pairs=p, stage_candidate_counts=list(map(len,choices)))),flush=True)
    n = 2*p
    end = {q:[[int(x) if x.denominator==1 else x for x in row] for row in a] for q,a in end.items()}
    compatibility = {}
    for s, menu in enumerate(choices):
        for t in range(s):
            compatibility[(s,t)] = [[commute(a['projector'],b['projector']) for b in choices[t]] for a in menu]
    leaves, best, compatible = 0, None, []
    local = {1:2487,2:713,3:224,4:102,5:20,8:8}
    helpers = {5:28,6:18,7:56,8:93,9:213}
    padding = sum(count*(9-rank)**(1-Ctarget) for rank,count in helpers.items() if rank<9)
    base_paid = (2*p+1)*(sum(count*rank**(1-Ctarget) for rank,count in local.items())+padding)
    helper_credit = (2*p+1)*sum(helpers.values())*9**(1-Ctarget)
    histograms = {}

    def visit(stage, selected, joint, extra):
        nonlocal leaves, best
        if leaves >= limit:
            return
        if stage == len(choices):
            leaves += 1
            targets = Counter()
            for (q, mask), a in joint.items():
                rank = sum(a[i][i] for i in range(n))
                B.need(rank.denominator == 1 if isinstance(rank,Q) else True, "Projector rank integral")
                targets[1+8*mask.bit_count()] += 112*int(rank)
            margin = helper_credit+sum(count*r**(1-Ctarget) for r,count in targets.items())-base_paid-extra*112*8**(1-Ctarget)
            case = dict(field_masks=[choices[s][j]["field_mask"] for s,j in enumerate(selected)],
                        extra_rank8_fields=extra, targets=dict(sorted(targets.items())),
                        margin_at_target=margin,
                        diagonal_spectral_blocks=[dict(q=q, stages=[s for s in range(2*p+1) if mask>>s&1],
                                                       multiplicity=int(sum(a[i][i] for i in range(n))))
                                                  for (q,mask),a in sorted(joint.items())])
            signature=json.dumps(case['targets'],sort_keys=True)+':'+str(extra)
            histograms.setdefault(signature,case)
            if best is None or margin > best["margin_at_target"]:
                best=case
            return
        for index,candidate in enumerate(choices[stage]):
            if all(compatibility[(stage,s)][index][j] for s,j in enumerate(selected)):
                visit(stage+1, selected+[index], refine(joint,candidate["projector"],stage), extra+candidate["rank"]-2)

    visit(0, [], {(q,0):a for q,a in end.items()}, 0)
    return dict(schema="independent-stage-field-projector-probe/1", pairs=p,
                candidate_counts=list(map(len,choices)), compatible_leaves=leaves,
                limit=limit, enumeration_complete=leaves<limit,
                target_C=str(Ctarget), best=best, distinct_invoices=list(histograms.values()),
                candidate_menus=[dict(stage=s, candidates=[dict(field_mask=c['field_mask'],rank=c['rank'],
                                                               projector=C.serialize_matrix(c['projector'])) for c in menu])
                                 for s,menu in enumerate(choices)],
                source_sha256={Path(__file__).name:sha256(Path(__file__).read_bytes()).hexdigest()},
                runtime_seconds=time.monotonic()-start, new_kappa=False,
                scope="Exact Q-projector compatibility; floating complete all-fresh helper screen only. Native idle placement, explicit L/R, hosting and transfer remain open.")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pairs',type=int,default=3)
    parser.add_argument('--limit',type=int,default=200000)
    parser.add_argument('--target',type=float,default=0.003)
    args=parser.parse_args()
    B.need(1<=args.pairs<=6,'Bounded projector probe')
    result=search(args.pairs,args.target,args.limit)
    (HERE/f'STAGE-PROJECTOR-P{args.pairs}.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('candidate_menus','distinct_invoices')},sort_keys=True))


if __name__=='__main__':
    main()
