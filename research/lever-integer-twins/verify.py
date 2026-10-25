#!/usr/bin/env python3
"""Integer twins of three PR3874 cells; pricing only, no new kappa.

ToikY with substantial OpenAI Codex assistance. Apache-2.0.
Exact log/exp engine is credited reuse of Colkitt/Claude's ceiling.py.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRID = Q(1, 10**12)
TARGET_KAPPA = Q(1, 99)
TARGET_A = TARGET_KAPPA / (1 - TARGET_KAPPA)
# cap, unpaid, centre charge, fixed rank-8 copies, reshapeable mass per call
CELLS = {'selected-r8-u2': (8,2,64,0,5586),
         'shared-r32-u1': (32,1,32,4,5522),
         'free-r16-u1': (16,1,0,0,5522)}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for row in sources['files']:
        if row['usage'] == 'input':
            require(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()
                    == row['sha256'], 'changed source: '+row['path'])
    for row in sources['external_predecessors']:
        require(hashlib.sha256((HERE/row['retained_path']).read_bytes()).hexdigest()
                == row['sha256'], 'changed retained predecessor')


def constants(path):
    values = {}
    for node in ast.parse(path.read_text()).body:
        if not isinstance(node, ast.Assign):
            continue
        t = node.targets[0]
        if isinstance(t,ast.Tuple) and [v.id for v in t.elts] == ['M','FAM','ST']:
            values.update(zip(['M','FAM','ST'],ast.literal_eval(node.value)))
        elif isinstance(t,ast.Name) and t.id in ('WORD','CENTRES','SHAPES','UNPAID'):
            values[t.id] = ast.literal_eval(node.value)
    return values


def optimum(mass, cap):
    require(type(mass) is int and mass >= 0, 'mass must be a nonnegative integer')
    require(type(cap) is int and 0 < cap <= 51, 'invalid rank cap')
    q, r = divmod(mass,cap)
    return {rank:n for rank,n in ((cap,q),(r,1 if r else 0)) if n}


def validate_histogram(hist, mass, cap):
    require(all(type(r) is int and 0<r<=cap and type(n) is int and n>0
                for r,n in hist.items()), 'invalid rank/count')
    require(sum(r*n for r,n in hist.items()) == mass, 'wrong mass')


def histograms(tag, calls, mode):
    require(type(calls) is int and calls>0 and calls%9==0, 'pool must contain 9k calls')
    require(mode in ('uniform','pooled'), 'unknown paid model')
    cap, unpaid, centre, fixed, mass = CELLS[tag]
    families = 896*calls//9
    paid = Counter({r:n*calls for r,n in optimum(mass,cap).items()}
                   if mode=='uniform' else optimum(mass*calls,cap))
    if fixed:
        paid[8] += fixed*calls
    pmass = (mass+8*fixed)*calls
    imass = (73-unpaid)*families+centre*calls-pmass
    idle = optimum(imass,51)
    validate_histogram(dict(paid),pmass,cap)
    validate_histogram(idle,imass,51)
    return dict(paid),idle,families,pmass,imass


def moment(C, hist, families, a):
    require(0<=a<=Q(1,20), 'saving outside search domain')
    lo = hi = Q(0)
    for r,n in hist.items():
        x,y = C.child_cost(r,73,a)
        lo += n*x
        hi += n*y
    return lo/families,hi/families


def bracket(C, hist, families):
    low,high = 0,int(Q(1,20)/GRID)
    require(moment(C,hist,families,0)[1]<1, 'no positive saving')
    require(moment(C,hist,families,high*GRID)[0]>1, 'root outside window')
    while high-low>1:
        mid = (low+high)//2
        lo,hi = moment(C,hist,families,mid*GRID)
        if hi<1:
            low=mid
        elif lo>1:
            high=mid
        else:
            raise ValueError('unresolved grid sign')
    return low*GRID,high*GRID


def encode(hist):
    return {str(r):n for r,n in sorted(hist.items())}


def compute(C):
    rows=[]
    for tag in CELLS:
        for calls in (9,144):
            for mode in ('uniform','pooled'):
                paid,idle,families,pmass,imass=histograms(tag,calls,mode)
                hist=dict(Counter(paid)+Counter(idle))
                lo,hi=bracket(C,hist,families)
                tl,th=moment(C,hist,families,TARGET_A)
                require(th<1 and lo>TARGET_A, 'integer cell misses target')
                require(moment(C,hist,families,lo)[1]<1<moment(C,hist,families,hi)[0],
                        'root bracket signs')
                # Extra work added after the full base histogram, without mass credit.
                ul,uh=C.child_cost(1,73,TARGET_A)
                extra=int((1-th)*families/uh)
                require(th+Q(extra,families)*uh<1<tl+Q(extra+1,families)*ul,
                        'unresolved surcharge boundary')
                rows.append(dict(name=f'{tag}/{calls}/{mode}',cell=tag,calls=calls,
                    paid_mode=mode,families=families,paid_mass=pmass,idle_mass=imass,
                    paid_histogram=encode(paid),idle_histogram=encode(idle),histogram=encode(hist),
                    a_lo=str(lo),a_hi=str(hi),kappa_lo=str(lo/(1+lo)),kappa_hi=str(hi/(1+hi)),
                    target_moment_lo=str(tl),target_moment_hi=str(th),
                    extra_rank1_children_at_target=extra))
    return dict(schema_version=1,width=73,target_kappa=str(TARGET_KAPPA),
                target_a=str(TARGET_A),root_grid=str(GRID),rows=rows)


def controls(C,result):
    require(TARGET_A==Q(1,98) and TARGET_A/(1+TARGET_A)==TARGET_KAPPA, 'target conversion')
    require(Q(1,99)/(1+Q(1,99))!=TARGET_KAPPA, 'weaker target confused with requested target')
    parent=constants(ROOT/'research/complex-local-word-ceiling/levers.py')
    peer=constants(HERE/'predecessor/grid.py')
    require(all(parent[k]==peer[k] for k in ('M','FAM','ST','WORD')), 'source disagreement')
    require((peer['M'],peer['FAM'],peer['ST'])==(73,896,9)
            and sum(r*n for r,n in peer['WORD'].items())==5586
            and peer['CENTRES']==[('sel',64,8),('shr',32,4),('free',0,0)]
            and peer['SHAPES']==['word',8,16,32] and peer['UNPAID']==[1,2],
            'changed predecessor model')
    mass=sum(r*n for r,n in peer['WORD'].items())
    centres={tag:(charge,copies) for tag,charge,copies in peer['CENTRES']}
    require(CELLS == {
        'selected-r8-u2':(8,2,centres['sel'][0],0,mass),
        'shared-r32-u1':(32,1,centres['shr'][0],centres['shr'][1],mass-64),
        'free-r16-u1':(16,1,centres['free'][0],centres['free'][1],mass-64)},
        'cell definition differs from retained predecessor')
    require(C.max_idle_rank(73)==51, 'halving guard')
    require(C.model({8:Q(5586,8)},73,896,9,64,unpaid=2)['idle_mass']==Q(13918,9),
            'two-unpaid idle mass')
    require(C.model(peer['WORD'],73,896,9,64)['idle_mass']==1646, 'baseline mass')
    for row in result['rows']:
        tag,calls,mode=row['cell'],row['calls'],row['paid_mode']
        cap,unpaid,centre,fixed,mass=CELLS[tag]
        profile={cap:Q(mass,cap)}
        if fixed:
            profile[8]=Q(fixed)
        _,relaxed_hi=C.ceiling(profile,73,896,9,centre,grid=GRID,unpaid=unpaid)
        require(Q(row['a_hi'])<=relaxed_hi, 'integer root above fractional relaxation')
        if mode=='uniform':
            other=next(r for r in result['rows'] if r['name']==f'{tag}/{calls}/pooled')
            require(Q(row['a_hi'])<=Q(other['a_lo']), 'paid pooling order')
        if calls==9:
            other=next(r for r in result['rows'] if r['name']==f'{tag}/144/{mode}')
            require(Q(row['a_hi'])<=Q(other['a_lo']), 'idle pooling order')
    # Small independent recurrence over masses checks the optimizer implementation.
    cases=0
    for cap in range(2,9):
        price={r:C.child_cost(r,73,Q(1,100)) for r in range(1,cap+1)}
        lower,upper=[Q(0)],[Q(0)]
        for mass in range(1,33):
            lower.append(min(lower[mass-r]+price[r][0] for r in range(1,min(cap,mass)+1)))
            upper.append(min(upper[mass-r]+price[r][1] for r in range(1,min(cap,mass)+1)))
            h=optimum(mass,cap)
            gl=sum(n*price[r][0] for r,n in h.items())
            gh=sum(n*price[r][1] for r,n in h.items())
            require(lower[mass]<=gh and gl<=upper[mass], 'DP/exchange disagreement')
            cases+=1
    mutations=[lambda:optimum(Q(13918,9),51),lambda:optimum(1,52),lambda:optimum(-1,8),
        lambda:histograms('selected-r8-u2',1,'uniform'),
        lambda:histograms('selected-r8-u2',9,'unknown'),
        lambda:validate_histogram({8:Q(2793,4)},5586,8),
        lambda:validate_histogram({52:1},52,51),
        lambda:validate_histogram({8:698,2:1},5587,8),
        lambda:moment(C,{8:1},1,Q(1,10))]
    for mutate in mutations:
        try:
            mutate()
        except ValueError:
            continue
        raise ValueError('negative control accepted')
    return cases,len(mutations)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    authenticate()
    spec=importlib.util.spec_from_file_location('pinned_ceiling',ROOT/'research/complex-local-word-ceiling/ceiling.py')
    C=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(C)
    result=compute(C)
    cases,mutations=controls(C,result)
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(text)
    else:
        require((HERE/'RESULT.json').read_text()==text, 'receipt mismatch')
    print(f'PASS_LEVER_INTEGER_TWINS rows={len(result["rows"])} dp_cases={cases} rejected={mutations} target_kappa=1/99 target_a=1/98 no_new_kappa')


if __name__=='__main__':
    main()
