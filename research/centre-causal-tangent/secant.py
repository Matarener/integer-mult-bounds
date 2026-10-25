#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact two-point gate on scalar oracles +1 and -1, not one fixed native F.

Clear1nsight, substantial OpenAI assistance. Causal feedback formula retains
Tekalign/PR2814 attribution. Main input/response ranks retain PR2622/2763 credit.
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import types

HERE=Path(__file__).resolve().parent
v=types.ModuleType('tangent_source'); v.__file__=str(HERE/'verify.py')
exec(compile((HERE/'verify.py').read_bytes(),v.__file__,'exec'),v.__dict__)


def local_feedback(program):
    state={('L',i):{} for i in range(704)}; rows={}; order=[]
    for e in program:
        if e[0]=='scalar':
            op=e[1]; kind,d=op[0],tuple(op[1])
            if kind=='clear': state[d]={}
            elif kind=='copy': state[d]=dict(state[tuple(op[2])])
            elif kind=='scale': state[d]={k:x*Q(op[2],op[3]) for k,x in state[d].items()}
            elif kind=='add': v.axpy(state[d],state[tuple(op[2])],Q(op[3],op[4]))
            else: raise ValueError('unknown feedback scalar')
        elif e[0]=='center':
            k=e[1]; v.need(k not in rows,'unique feedback site')
            rows[k]=dict(state['C',k]); order.append(k); v.axpy(state['C',k],{k:Q(1)})
        else: v.need(e[0] in v.LOCAL_SKIP,'feedback local event')
    v.need(set(order)==set(range(8)),'feedback sites complete')
    return rows,order


def feedback(data):
    calls,_=v.bind(data)
    local={o:v.local_model(data['program'][o]) for o in ('forward','backward')}
    lf={o:local_feedback(data['program'][o]) for o in local}
    state=[{} for _ in range(14336)]; K=[None]*1152; actual_order=[]; used=0
    for e in data['global']['execution_schedule']:
        kind=e['kind']
        if kind=='local_cover_sweep':
            c=calls[v.call_key(e)]; owners=[x[0] for x in c['owners']]; o=c['orientation']
            queries,_,impulses=local[o]; within,order=lf[o]
            for k in order:
                i=8*used+k; row={}
                for r,q in queries[k].items(): v.axpy(row,state[owners[r]],q)
                v.axpy(row,{8*used+j:q for j,q in within[k].items()})
                K[i]=row; actual_order.append(i)
            for p in range(112):
                d,s,q=(112+p,p,1) if o=='forward' else (p,112+p,-1)
                v.axpy(state[owners[d]],state[owners[s]],Q(q))
            for r,row in enumerate(impulses): v.axpy(state[owners[r]],{8*used+k:q for k,q in row.items()})
            used+=1
        elif kind=='bridge': v.bridge((state,),e)
        elif kind=='terminal':
            for pair in range(4):
                for p in range(112):
                    x=896*e['replica']+224*pair+p; y=x+112
                    state[x],state[y]=state[y],{k:-q for k,q in state[x].items()}
        else: v.need(kind in v.SKIP,'feedback global event')
    triangular(K,actual_order)
    return K,actual_order


def triangular(K,order):
    v.need(sorted(order)==list(range(len(K))),'complete chronological permutation')
    position={i:k for k,i in enumerate(order)}
    v.need(all(row is not None and all(position[j]<position[i] for j in row)
               for i,row in enumerate(K)),'strict causal feedback')


def solve(K,order,rhs,delta):
    triangular(K,order); out=[Q(0)]*len(K)
    for i in order: out[i]=delta*(rhs[i]+sum((q*out[j] for j,q in K[i].items()),Q(0)))
    return out


def literal_minus(data,initial):
    """Independent scalar execution at z=-1, captures every actual innovation."""
    state=list(initial); calls={v.call_key(c):c for c in data['global']['calls']}
    innovations=[None]*1152; used=scalar=0
    for e in data['global']['execution_schedule']:
        kind=e['kind']
        if kind=='local_cover_sweep':
            c=calls[v.call_key(e)]; owners=[x[0] for x in c['owners']]
            work={('L',r):state[f] for r,f in enumerate(owners)}
            for event in data['program'][c['orientation']]:
                if event[0]=='scalar':
                    op=event[1]; name,d=op[0],tuple(op[1]); scalar+=1
                    if name=='clear': work[d]=Q(0)
                    elif name=='copy': work[d]=work[tuple(op[2])]
                    elif name=='scale': work[d]*=Q(op[2],op[3])
                    elif name=='add': work[d]+=Q(op[3],op[4])*work[tuple(op[2])]
                    else: raise ValueError('unknown point scalar')
                elif event[0]=='center':
                    k=event[1]; d=('C',k); innovations[used*8+k]=-2*work[d]; work[d]=-work[d]
                else: v.need(event[0] in v.LOCAL_SKIP,'point local event')
            v.need(all(q==0 for k,q in work.items() if k[0]!='L'),'point private cleanup')
            for r,f in enumerate(owners): state[f]=work['L',r]
            used+=1
        elif kind=='bridge':
            dx=896*e['replica']+224*e['dst']; sx=896*e['replica']+224*e['src']; q=e['coefficient']
            for p in range(112):
                state[dx+p]+=q*state[sx+p]
                state[sx+112+p]-=q*state[dx+112+p]
        elif kind=='terminal':
            for pair in range(e['pairs']):
                for p in range(112):
                    x=896*e['replica']+224*pair+p; y=x+112; state[x],state[y]=state[y],-state[x]
        else: v.need(kind in v.SKIP,'point global event')
    v.need(used==144 and all(x is not None for x in innovations),'point all sites')
    return state,innovations,scalar


def run(data):
    C,B,_=v.factors(data); K,order=feedback(data)
    v.need(v.rank_mod(C,2147483647)[0]==v.rank_mod(B,2147483647)[0]==1152,'secant source/response full rank')
    initial=[Q((13*i+5)%23-11,16) for i in range(14336)]
    rhs=[sum((q*initial[j] for j,q in row.items()),Q(0)) for row in C]
    e=solve(K,order,rhs,Q(-2))
    want=[x+sum((q*e[j] for j,q in row.items()),Q(0)) for x,row in zip(initial,B)]
    got,innovations,scalar=literal_minus(data,initial)
    v.need(got==want and innovations==e,'point replay equals causal resolvent at all outputs and cuts')
    v.need(scalar==2835792,'all point scalar operations')
    omitted=[x+sum((q*(-2*rhs[j]) for j,q in row.items()),Q(0)) for x,row in zip(initial,B)]
    v.need(omitted!=got,'omitted-feedback control distinguishes the exact endpoint')
    bad=[dict(row) for row in K]; bad[order[0]][order[0]]=Q(1)
    try: triangular(bad,order)
    except ValueError: pass
    else: raise ValueError('cyclic feedback accepted')
    return {'schema_version':1,'status':'PASS_CENTRE_TWO_POINT_SECANT','sites':1152,
      'feedback_sha256':v.row_digest(K),'feedback_nonzeros':sum(map(len,K)),
      'chronological_order_sha256':sha256(v.canon(order)).hexdigest(),
      'minus_one_output_sha256':sha256(v.canon(list(map(str,got)))).hexdigest(),
      'minus_one_innovations_sha256':sha256(v.canon(list(map(str,e)))).hexdigest(),
      'literal_scalar_operations':scalar,'changed_outputs':sum(a!=b for a,b in zip(initial,got)),
      'omitted_feedback_differing_outputs':sum(a!=b for a,b in zip(omitted,got)),
      'secant_rank':1152,'minimum_uniform_sign_oracle_queries':1152,
      'fixed_single_native_operator_lower_bound':False,'controls':['cyclic_feedback_rejected','missing_feedback_detected']}


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--emit',action='store_true'); args=parser.parse_args()
    out=run(v.load())
    if not args.emit:
        expected=HERE/'SECANT.json'; v.need(expected.is_file() and not expected.is_symlink(),'committed secant receipt')
        v.need(v.canon(json.loads(expected.read_bytes()))==v.canon(out),'typed secant receipt differs')
    print('SECANT_JSON='+v.canon(out).decode()); print(out['status'])


if __name__=='__main__': main()
