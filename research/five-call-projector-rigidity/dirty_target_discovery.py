"""Test one returned dirty field and balanced degree-two/three targets.

The query tuple has q-1 central targets and one independent identity
target. The first two coefficients and the target projector are exact
necessary conditions. A consistent system is not an endpoint certificate.
"""
import argparse
import json
from pathlib import Path
import time
import exact_replay as e
from mixed_target_discovery import construct


def coefficients(ps,ts,degree):
    q=len(ps[0]);words=[[e.eye(q)],[e.eye(q)]]
    for p,t in zip(ps,ts):
        for channel,query in enumerate([e.eye(q),t]):
            old=[e.mm(query,x) for x in words[channel]]
            words[channel]=[old[0]]+[e.ma(old[j],e.mm(p,old[j-1])) for j in range(1,len(old))]
            if len(old)<=degree:words[channel].append(e.mm(p,old[-1]))
    return words[0][degree],words[1][degree]


def check(q,coupling):
    started=time.monotonic();names,ps,qs,ts,J=construct(q,coupling)
    E=e.eye(q);E[-1][-1]={}
    H,minus=coefficients(ps,ts,1)
    support=e.ma(H,e.mm(e.mm(E,H),E),-1)
    query=e.ma(minus,e.mm(J,H),-1)
    linear=[x for m in [support,query] for row in m for x in row]
    vals=e.linear_solution(linear);steps=[]
    if vals is None:
        status='EXACT_DIRTY_FIRST_COEFFICIENT_CONTRADICTION'
    else:
        ps=[e.ms(p,vals) for p in ps];qs=[e.substitute(x,vals) for x in qs]
        H=e.ms(H,vals)
        K=e.ma(H,[[e.scale(x,2) for x in row] for row in E],-1)
        plus,minus=coefficients(ps,ts,2)
        expected=e.ma(E,[[e.scale(x,2) for x in row] for row in K])
        constraints=[e.ma(e.mm(K,K),K,-1),e.ma(plus,expected,-1),e.ma(minus,e.mm(J,expected),-1)]
        system=qs+[x for m in constraints for row in m for x in row]
        while True:
            reduced=e.row_reduce(system);affine=[p for p in reduced if all(len(m)<=1 for m in p)]
            row={'variables':len({v for p in system for m in p for v in m}),'affine_consequences':len(affine)}
            steps.append(row);print(json.dumps(row),flush=True)
            if any(set(p)=={()} for p in affine):status='EXACT_DIRTY_SECOND_COEFFICIENT_CONTRADICTION';break
            if not affine:status='UNRESOLVED_DIRTY_SYSTEM';break
            vals=e.linear_solution(affine);system=[e.substitute(p,vals) for p in system]
    return {'q':q,'query_extension':coupling,'central_targets':q-1,'dirty_identity_fields':1,
            'higher_stage_target_count':2,'status':status,'steps':steps,
            'seconds':time.monotonic()-started,'new_kappa':False}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--q',type=int,default=7)
    p.add_argument('--coupling',type=int,choices=(0,1),default=1)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args();result=check(args.q,args.coupling)
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
