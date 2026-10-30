#!/usr/bin/env python3
"""Exact F2 controller search modulo all equal-clock GL basis changes.

This is a necessary-condition relaxation for integral dual bridge recipes;
it does not search integer coefficient lifts or prove owner realizability.
Each clock group is a symplectically paired pair of row spaces. Arbitrary
GL changes inside it are quotiented by a canonical top basis and its unique
dual bottom basis. Moving one physical pair to a higher existing clock costs
one nonzero idle segment. The local-count rank floor prunes the search.

Apache-2.0. Substantial OpenAI assistance. The rank floor and clock/hosting
model retain the bit589-recipe-floor and PR386/436/442/443/463 lineage.
"""
from argparse import ArgumentParser
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from time import monotonic
import json


K = 0


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def xor_combination(rows, coefficients):
    out = 0
    for i,row in enumerate(rows):
        if (coefficients >> i) & 1:
            out ^= row
    return out


def dot(a,b):
    return (a & b).bit_count() & 1


def symplectic(a,b):
    mask = (1 << K)-1
    return dot(a & mask,b >> K) ^ dot(a >> K,b & mask)


@lru_cache(None)
def canonical(top,bottom):
    """RREF(top), then bottom basis dual to it for the symplectic form."""
    if not top:
        return (),()
    rows = list(top)
    pivot = 0
    for column in range(2*K):
        chosen = next((j for j in range(pivot,len(rows)) if (rows[j] >> column) & 1),None)
        if chosen is None:
            continue
        rows[pivot],rows[chosen] = rows[chosen],rows[pivot]
        for j in range(len(rows)):
            if j != pivot and (rows[j] >> column) & 1:
                rows[j] ^= rows[pivot]
        pivot += 1
        if pivot == len(rows):
            break
    assert pivot == len(rows)
    lookup = {}
    for c in range(1,1 << len(bottom)):
        value = xor_combination(bottom,c)
        label = sum(symplectic(x,value) << j for j,x in enumerate(rows))
        lookup[label] = value
    dual = tuple(lookup[1 << j] for j in range(len(rows)))
    return tuple(rows),dual


@lru_cache(None)
def split_pairs(top,bottom):
    """All possible singled-out physical pairs under the full GL orbit."""
    n = len(top)
    out = []
    combinations_top = [xor_combination(top,c) for c in range(1 << n)]
    combinations_bottom = [xor_combination(bottom,c) for c in range(1 << n)]
    for a in range(1,1 << n):
        x = combinations_top[a]
        for b in range(1,1 << n):
            if not dot(a,b):
                continue
            y = combinations_bottom[b]
            xt = tuple(combinations_top[c] for c in range(1,1 << n) if not dot(c,b))
            yt = tuple(combinations_bottom[c] for c in range(1,1 << n) if not dot(c,a))
            # Select independent bases before canonicalizing the complement.
            xb = []
            for z in xt:
                if rank(xb+[z]) > len(xb):
                    xb.append(z)
            yb = []
            for z in yt:
                if rank(yb+[z]) > len(yb):
                    yb.append(z)
            remainder = canonical(tuple(xb),tuple(yb))
            out.append((x,y,remainder[0],remainder[1]))
    return tuple(out)


def state(groups):
    return tuple(sorted((level,*canonical(top,bottom)) for level,top,bottom in groups if top))


def potential(groups):
    mask = (1 << K)-1
    return rank([x & mask for _,top,_ in groups for x in top])+rank([y >> K for _,_,bottom in groups for y in bottom])


def idle_successors(groups,max_jump):
    for i,(low,top,bottom) in enumerate(groups):
        for j,(high,high_top,high_bottom) in enumerate(groups):
            if high <= low or (max_jump and high-low > max_jump):
                continue
            untouched = [z for t,z in enumerate(groups) if t not in (i,j)]
            for x,y,rest_top,rest_bottom in split_pairs(top,bottom):
                yield state(untouched+[(low,rest_top,rest_bottom),
                                      (high,high_top+(x,),high_bottom+(y,))]),(low,high,x,y)


def local_successors(groups,stage):
    for i,(level,top,bottom) in enumerate(groups):
        if level != stage-1:
            continue
        untouched = [z for j,z in enumerate(groups) if i != j]
        for x,y,rest_top,rest_bottom in split_pairs(top,bottom):
            for reverse in (False,True):
                xx,yy = (x^y,y) if reverse else (x,y^x)
                out = state(untouched+[(level,rest_top,rest_bottom),(stage,(xx,),(yy,))])
                if potential(out) <= 2*K-stage:
                    yield out,(stage,reverse,x,y)


def search(k,budget,max_jump=0,max_states=1000000):
    global K
    K = k
    canonical.cache_clear(); split_pairs.cache_clear()
    started = monotonic()
    stages = 2*K+1
    # Global pair relabeling and swapping top/bottom fix the first local F0.
    start = state([(0,(1,),(1 | (1 << K),)),
                   (-1,tuple(1 << j for j in range(1,K)),tuple(1 << (K+j) for j in range(1,K)))])
    frontier = {start:0}
    logs = []
    completed = False
    for stage in range(1,stages):
        # Every nonzero final climb pays once for each lagging physical pair.
        closure = dict(frontier)
        work = list(frontier)
        index = 0
        while index < len(work):
            groups = work[index]; index += 1
            cost = closure[groups]
            if cost >= budget:
                continue
            for nxt,event in idle_successors(groups,max_jump):
                new_cost = cost+1
                if new_cost < closure.get(nxt,budget+1):
                    closure[nxt] = new_cost; work.append(nxt)
            if len(closure) > max_states:
                return {'status':'STOPPED_STATE_CAP','K':K,'budget':budget,'stage':stage,
                        'closure_states':len(closure),'logs':logs,'seconds':monotonic()-started}
        next_frontier = {}
        for groups,cost in closure.items():
            for nxt,event in local_successors(groups,stage):
                if cost < next_frontier.get(nxt,budget+1):
                    next_frontier[nxt] = cost
        # No future idle segment can be free; keep only possible final budgets.
        frontier = next_frontier
        row = {'stage':stage,'closure':len(closure),'after_local':len(frontier),
               'minimum_idle_cost':min(frontier.values(),default=None),'seconds':monotonic()-started}
        logs.append(row); print(json.dumps(row),flush=True)
        if not frontier:
            completed = True; break
    best = None
    witnesses = []
    if frontier and len(logs) == stages-1:
        completed = True
        for groups,cost in frontier.items():
            assert potential(groups) == 0
            final_cost = cost + sum(len(top) for level,top,_ in groups if level < stages-1)
            if best is None or final_cost < best:
                best = final_cost; witnesses = [groups]
            elif final_cost == best and len(witnesses) < 3:
                witnesses.append(groups)
    return {'status':'EXACT_FINITE_CLOCK_ORBIT_SEARCH_COMPLETE' if completed else 'INCOMPLETE',
            'K':K,'stages':stages,'budget_before_final':budget,'maximum_idle_jump':max_jump or None,
            'minimum_final_idle_segments_found':best,'witness_final_states':witnesses,
            'states_after_last_local':len(frontier),'logs':logs,'seconds':monotonic()-started,
            'scope':'F2 necessary-condition search modulo arbitrary equal-clock dual GL bridges; no integer lift, full profile, hosting, or native claim'}


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--pairs',type=int,required=True)
    ap.add_argument('--idle-budget',type=int,required=True)
    ap.add_argument('--max-jump',type=int,default=0)
    ap.add_argument('--max-states',type=int,default=1000000)
    ap.add_argument('--output',type=Path,required=True)
    args = ap.parse_args()
    result = search(args.pairs,args.idle_budget,args.max_jump,args.max_states)
    result['script_sha256'] = sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('logs','witness_final_states')}),flush=True)


if __name__ == '__main__':
    main()
