#!/usr/bin/env python3
"""Paid native-chart retiming as a signed binary graph optimization.

The optimization is only a search. Every output is checked by independent
exact all-column replay; a solver bound is not called a mathematical proof.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from collections import Counter
import argparse, hashlib, json, sys
from chronology import need
from batch_paid_progress import operator, replay
from native_chart_search import compile_word
HERE=Path(__file__).resolve().parent


def graph(events,banks,planes):
    state=[[(0,0)]*planes for unused in range(banks)]
    edges=[];choices=[];nodes=1
    for e in events:
        if e['kind']=='ADD':
            chosen=list(range(nodes,nodes+planes));nodes+=planes;choices.append(chosen)
            for bank in(e['dst'],e['src']):
                for j,(v,c)in enumerate(state[bank]):edges.append((v,chosen[j],c))
                state[bank]=[(v,0)for v in chosen]
        elif e['kind']=='BANK_SWAP':
            i,j=e['banks'];state[i],state[j]=state[j],state[i]
        else:
            g=operator(e['operator']);old=state[e['bank']];new=[None]*planes
            for j,(v,c)in enumerate(old):
                dest=g.perm[j];new[dest]=(v,c^((g.mask>>dest)&1))
            state[e['bank']]=new
    for row in state:
        for v,c in row:edges.append((v,0,c))
    return nodes,edges,choices


def main():
    import numpy as np
    import scipy
    from scipy.optimize import milp,Bounds,LinearConstraint
    from scipy.sparse import coo_array
    ap=argparse.ArgumentParser();ap.add_argument('--source',default='INDEPENDENT-HANDOFF-SIX.json');ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--output',default='SIGNED-CHART-HANDOFF-SIX.json');args=ap.parse_args()
    source=Path(args.source);source=source if source.is_absolute()else HERE/source
    raw=source.read_bytes();data=json.loads(raw);events=data['events']
    banks=data.get('width',6);ambient=data.get('ambient_arity',12);planes=ambient//2
    nodes,edges,choices=graph(events,banks,planes);m=len(edges);nv=nodes+2*m
    rows=[];cols=[];values=[];rhs=[]
    for k,(a,b,c)in enumerate(edges):
        for col,value in((a,1),(b,1),(nodes+k,-1),(nodes+m+k,-2)):
            rows.append(k);cols.append(col);values.append(value)
        rhs.append(-c)
    A=coo_array((values,(rows,cols)),shape=(m,nv)).tocsc()
    objective=np.zeros(nv);objective[nodes:nodes+m]=2
    lower=np.zeros(nv);upper=np.ones(nv);upper[0]=0
    result=milp(objective,integrality=np.ones(nv),bounds=Bounds(lower,upper),constraints=LinearConstraint(A,rhs,rhs),options={'time_limit':args.seconds,'mip_rel_gap':0})
    need(result.x is not None,'optimizer returned no candidate')
    assignment=[int(round(x))for x in result.x]
    need(all(abs(x-z)<1e-6 for x,z in zip(result.x,assignment)),'candidate exactly roundable to binary')
    need(assignment[0]==0 and all(v in(0,1)for v in assignment),'all variables binary')
    for k,(a,b,c)in enumerate(edges):need(assignment[a]+assignment[b]+c-assignment[nodes+k]-2*assignment[nodes+m+k]==0,'exact integer edge equation')
    masks=[sum(assignment[v]<<j for j,v in enumerate(chosen))for chosen in choices]
    compiled=compile_word(events,banks,planes,ambient,masks)
    need(replay(compiled,banks,planes)==replay(events,banks,planes),'exact all-column changed word and both inverse orders')
    H=Counter(e['operator']['native_arity']for e in compiled if e['kind']=='NATIVE');mass=sum(r*c for r,c in H.items())
    need(mass==2*sum(assignment[nodes:nodes+m]),'compiled rank mass equals exact graph objective')
    out=dict(status='PASS_EXACT_SIGNED_GRAPH_RETIMING_CANDIDATE',no_new_kappa=True,source_path=str(source),source_sha256=hashlib.sha256(raw).hexdigest(),producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scipy_version=scipy.__version__,solver_status=int(result.status),solver_message=result.message,solver_float_lower_bound=getattr(result,'mip_dual_bound',None),solver_float_gap=getattr(result,'mip_gap',None),nodes=nodes,edges=m,choices=masks,histogram=dict(sorted(H.items())),native_mass=mass,stock=banks*ambient,deficit=banks*ambient-mass,width=banks,ambient_arity=ambient,events=compiled,limits=['A numerical optimizer produced the candidate; no optimum or impossibility theorem is claimed.','The serialized word is independently checked exactly on all original columns and both inverse orders.','Complete native/precision/ownership/source/tape and compatible BIT obligations remain.'])
    (HERE/args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'],dict(H),'mass',mass,'stock',banks*ambient,'solver',result.status,'lowerbound',out['solver_float_lower_bound'])
if __name__=='__main__':main()
