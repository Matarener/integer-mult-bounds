#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""First-variation gate for the selected SCALAR projected centre programme.

Clear1nsight with substantial OpenAI assistance. The observation/response
reconstruction adapts the credited PR2199/2622/2763 mathematics. This does not
model native Fourier operators or prove a native recursive-call lower bound.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
ARCHIVE_SHA = 'f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6'
MEMBERS = {
 'global': ('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz','2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760'),
 'program': ('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz','241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a'),
}
SKIP = {'idle_cover_sweep','terminal_Y_translations','bank_padding_cover_sweep','translate_every_live_family'}
LOCAL_SKIP = {'phase','climb','adapter','residual_adapter'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def row_digest(rows):
    return sha256(canon([{str(k): str(v) for k,v in sorted(r.items())} for r in rows])).hexdigest()


def load(root=ROOT):
    path = root / ARCHIVE
    need(path.is_file() and not path.is_symlink(), 'regular selected archive')
    need(sha256(path.read_bytes()).hexdigest() == ARCHIVE_SHA, 'selected archive hash')
    result = {}
    with tarfile.open(path) as archive:
        for key,(name,digest) in MEMBERS.items():
            matches = [m for m in archive.getmembers() if m.name == name]
            need(len(matches) == 1 and matches[0].isfile(), 'unique regular source member')
            data = archive.extractfile(matches[0]).read()
            need(sha256(data).hexdigest() == digest, 'source member hash: '+key)
            result[key] = json.loads(gzip.decompress(data))
    return result


def axpy(dest, source, factor=Q(1)):
    for key,value in list(source.items()):
        new = dest.get(key,Q(0)) + factor*value
        if new: dest[key] = new
        else: dest.pop(key,None)


def local_model(program):
    state = {('L',i):{i:Q(1)} for i in range(704)}
    responses = {('L',i):{} for i in range(704)}
    queries = {}
    for event in program:
        kind = event[0]
        if kind == 'scalar':
            op = event[1]; name,dest = op[0],tuple(op[1])
            for stream in (state,responses):
                if name == 'clear': stream[dest] = {}
                elif name == 'copy': stream[dest] = dict(stream[tuple(op[2])])
                elif name == 'scale': stream[dest] = {k:v*Q(op[2],op[3]) for k,v in stream[dest].items()}
                elif name == 'add':
                    need(dest != tuple(op[2]), 'distinct ADD roles')
                    axpy(stream[dest],stream[tuple(op[2])],Q(op[3],op[4]))
                else: raise ValueError('unknown scalar instruction')
        elif kind == 'center':
            k=event[1]; need(k not in queries and event[4] == 8, 'centre binding')
            queries[k] = dict(state['C',k])
            axpy(responses['C',k],{k:Q(1)})
        else: need(kind in LOCAL_SKIP, 'unknown local event')
    need(set(queries) == set(range(8)), 'eight local queries')
    need(all(not r for k,r in state.items() if k[0] != 'L'), 'baseline private cleanup')
    need(all(not r for k,r in responses.items() if k[0] != 'L'), 'response private cleanup')
    ordinary=[state['L',i] for i in range(704)]
    return [queries[i] for i in range(8)],ordinary,[responses['L',i] for i in range(704)]


def call_key(c):
    return tuple(c[k] for k in ('time','replica','stage','provider_id'))


def bind(data):
    template=data['global']; need(template['live'] == 14336, 'live stock')
    calls={call_key(c):c for c in template['calls']}
    need(len(calls) == 144, 'call count')
    for c in calls.values():
        owners=[x[0] for x in c['owners']]
        need(len(owners)==len(set(owners))==704 and all(0<=x<14336 for x in owners),'owner injection')
        need(sha256(canon(data['program'][c['orientation']])).hexdigest() == c['local_program_sha256'],'call/program binding')
        base=896*c['replica']+224*c['pair']
        need(owners[:224]==list(range(base,base+224)), 'bridge/data owner binding')
    order=[calls[call_key(e)] for e in template['execution_schedule'] if e['kind']=='local_cover_sweep']
    need(len(order)==144 and len({call_key(c) for c in order})==144, 'schedule bijection')
    return calls,order


def bridge(states,e):
    b=896*e['replica']; d=b+224*e['dst']; s=b+224*e['src']; g=e['coefficient']
    need(e['dst']!=e['src'] and g in (-1,1) and 0<=e['replica']<16
         and all(0<=e[k]<4 for k in ('dst','src')), 'paired bridge')
    for p in range(112):
        for state in states:
            axpy(state[d+p],state[s+p],Q(g))
            axpy(state[s+112+p],state[d+112+p],Q(-g))


def factors(data):
    calls,order=bind(data)
    local={o:local_model(data['program'][o]) for o in ('forward','backward')}
    for orientation,(_,endpoint,_) in local.items():
        expected=[{i:Q(1)} for i in range(704)]
        for p in range(112):
            d,s,g=(112+p,p,1) if orientation=='forward' else (p,112+p,-1)
            axpy(expected[d],expected[s],Q(g))
        need(endpoint==expected,'independently derived local endpoint')
    base=[{i:Q(1)} for i in range(14336)]
    response=[{} for _ in base]; history=[]; used=0
    for e in data['global']['execution_schedule']:
        kind=e['kind']
        if kind=='local_cover_sweep':
            c=calls[call_key(e)]; owners=[x[0] for x in c['owners']]
            queries,_,impulses=local[c['orientation']]
            for form in queries:
                row={}
                for r,g in form.items(): axpy(row,base[owners[r]],g)
                history.append(row)
            for p in range(112):
                d,s,g=(112+p,p,1) if c['orientation']=='forward' else (p,112+p,-1)
                for state in (base,response): axpy(state[owners[d]],state[owners[s]],Q(g))
            for r,row in enumerate(impulses):
                axpy(response[owners[r]],{8*used+k:g for k,g in row.items()})
            used+=1
        elif kind=='bridge': bridge((base,response),e)
        elif kind=='terminal':
            need(e['pairs']==4 and 0<=e['replica']<16,'four terminal pairs')
            for pair in range(4):
                for p in range(112):
                    x=896*e['replica']+224*pair+p; y=x+112
                    for state in (base,response): state[x],state[y]=state[y],{k:-v for k,v in state[x].items()}
        else: need(kind in SKIP,'unknown global projection event')
    need(base==[{i:Q(1)} for i in range(14336)],'complete baseline identity')
    return history,response,order


def rank_mod(rows,prime,largest=False):
    pivots={}
    for original in (reversed(rows) if largest else rows):
        row={k:(v.numerator*pow(v.denominator,-1,prime))%prime for k,v in original.items()}
        row={k:v for k,v in row.items() if v}
        while row:
            at=max(row) if largest else min(row)
            if at not in pivots:
                inv=pow(row[at],-1,prime); pivots[at]={k:v*inv%prime for k,v in row.items()}; break
            scale=row[at]
            for k,v in pivots[at].items():
                value=(row.get(k,0)-scale*v)%prime
                if value: row[k]=value
                else: row.pop(k,None)
    return len(pivots), sorted(pivots)


def literal_dual(data,initial,reciprocal):
    """Separate full scalar interpreter over Q[epsilon]/epsilon^2.

    Does not call local_model, factors, bridge, or use their endpoint formulas.
    Every archived scalar instruction is executed, with centre multiplier
    1+epsilon, or 1-epsilon at backward calls in reciprocal mode.
    """
    state=[(Q(x),Q(0)) for x in initial]; bykey={call_key(c):c for c in data['global']['calls']}
    scalar=centres=0
    for e in data['global']['execution_schedule']:
        kind=e['kind']
        if kind=='local_cover_sweep':
            c=bykey[call_key(e)]; owners=[a[0] for a in c['owners']]; local={('L',r):state[o] for r,o in enumerate(owners)}
            sign=-1 if reciprocal and c['orientation']=='backward' else 1
            for event in data['program'][c['orientation']]:
                if event[0]=='scalar':
                    op=event[1]; name,d=op[0],tuple(op[1]); scalar+=1
                    if name=='clear': local[d]=(Q(0),Q(0))
                    elif name=='copy': local[d]=local[tuple(op[2])]
                    elif name=='scale':
                        a,b=local[d]; q=Q(op[2],op[3]); local[d]=(q*a,q*b)
                    elif name=='add':
                        a,b=local[d]; x,y=local[tuple(op[2])]; q=Q(op[3],op[4]); local[d]=(a+q*x,b+q*y)
                    else: raise ValueError('unknown dual scalar')
                elif event[0]=='center':
                    d=('C',event[1]); a,b=local[d]; local[d]=(a,b+sign*a); centres+=1
                else: need(event[0] in LOCAL_SKIP,'unknown dual local event')
            need(all(v==(0,0) for k,v in local.items() if k[0]!='L'),'dual private restoration')
            for r,o in enumerate(owners): state[o]=local['L',r]
        elif kind=='bridge':
            b=896*e['replica']; dx=b+224*e['dst']; sx=b+224*e['src']; gain=e['coefficient']
            for p in range(112):
                d,s=dx+p,sx+p
                state[d]=tuple(a+gain*b for a,b in zip(state[d],state[s]))
                state[s+112]=tuple(a-gain*b for a,b in zip(state[s+112],state[d+112]))
        elif kind=='terminal':
            for pair in range(e['pairs']):
                for p in range(112):
                    x=896*e['replica']+224*pair+p; y=x+112
                    state[x],state[y]=state[y],tuple(-a for a in state[x])
        else: need(kind in SKIP,'unknown dual global event')
    need([a for a,b in state]==list(map(Q,initial)),'dual baseline equality')
    need(centres==1152,'dual centre occurrences')
    return [b for a,b in state],scalar


def run(data):
    C,B,order=factors(data)
    ranks={}
    for p,reverse in ((2147483647,False),(2305843009213693951,True)):
        cr,_=rank_mod(C,p,reverse); br,_=rank_mod(B,p,reverse)
        need(cr==br==1152,'full source and response ranks')
        ranks[str(p)]={'source_rank':cr,'response_rank':br}
    probes=[]
    initial=[Q((i*i+17*i+11)%31-15,8) for i in range(14336)]
    inputs=[sum((v*initial[k] for k,v in row.items()),Q(0)) for row in C]
    for reciprocal in (False,True):
        signs=[-1 if reciprocal and c['orientation']=='backward' else 1 for c in order for _ in range(8)]
        want=[sum((v*signs[k]*inputs[k] for k,v in row.items()),Q(0)) for row in B]
        got,count=literal_dual(data,initial,reciprocal)
        need(got==want,'full literal derivative equals B diag(sign) C')
        need(count==2835792,'all archived scalar operations retained')
        probes.append({'reciprocal':reciprocal,'scalar_operations':count,'nonzero_outputs':sum(bool(x) for x in got),
                       'derivative_sha256':sha256(canon(list(map(str,got)))).hexdigest()})
    return {'schema_version':1,'status':'PASS_CENTRE_CAUSAL_TANGENT','calls':144,'sites':1152,'live':14336,
            'source_rows_sha256':row_digest(C),'response_rows_sha256':row_digest(B),'rank_certificates':ranks,
            'first_variation_rank':1152,'scalar_oracle_minimum':1152,'half_share_576_rejected':True,
            'schedule_counts':dict(sorted(Counter(e['kind'] for e in data['global']['execution_schedule']).items())),
            'literal_dual_probes':probes,'fixed_native_operator_bound_claimed':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--emit',action='store_true',help='Discovery output; skips committed receipt equality')
    args=parser.parse_args()
    result=run(load(args.root))
    expected=HERE/'RESULT.json'
    if not args.emit:
        need(expected.is_file() and not expected.is_symlink(),'missing regular committed result')
        need(canon(json.loads(expected.read_bytes()))==canon(result),'typed result mismatch')
    print('RESULT_JSON='+canon(result).decode()); print(result['status'])


if __name__=='__main__': main()
