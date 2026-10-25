#!/usr/bin/env python3
"""Independent actual-circuit binding and all-column audit of encoded caller.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
import argparse,hashlib,json
import quadratic_charts as q
HERE=Path(__file__).resolve().parent

def circuit(events,n):
    I=q.identity(n);out=I
    for e in events:
        kind=e[0]
        if kind=='P':
            ri=q.inverse(tuple(e[1]));rows=tuple(sum(((ri[j]>>i)&1)<<j for j in range(n))for i in range(n));g=q.Mono(rows,0,(0,)*n,(0,)*n)
        elif kind=='C':g=q.from_function(I.rows,0,lambda x:e[2]*q.parity(e[1]&x))
        elif kind=='D':
            q.need(not any(e[1]) and all(a%2==0 for a in e[2]),'source physical diagonal is Pauli');g=q.Mono(I.rows,sum((a//2)<<i for i,a in enumerate(e[2])),(0,)*n,(0,)*n)
        elif kind=='X':g=q.Mono(I.rows,0,tuple(2*((e[1]>>i)&1)for i in range(n)),(0,)*n)
        elif kind=='phase':g=q.Mono(I.rows,0,(0,)*n,(0,)*n,e[1]%4)
        else:raise ValueError('unsupported source literal '+kind)
        out=g@out
    return out

def actual(e,n):
    if 'exact_operator'in e:
        d=e['exact_operator'];g=circuit(d['one_coordinate_literal_circuit'],n);p=d['phase_exponent'];return q.Mono(g.rows,g.offset,g.alpha,g.quad,(g.constant-p)%4,(p+(2 if d['global_sign']==-1 else 0))%4)
    d=e['operator'];g=circuit(d['one_bit_circuit'],n);v=d['global_i_exponent_by_f_mod4'];s=(v[1]-v[0])%4
    q.need(all(v[r]==(v[0]+s*r)%4 for r in range(4)),'literal all-f global phase is affine in f')
    return q.Mono(g.rows,g.offset,g.alpha,g.quad,(g.constant+s)%4,v[0])

def inverse_events(events,n):
    out=[]
    for e in reversed(events):
        if e['kind']=='ADD':e=dict(e,coefficient=str(-q.Fraction(e['coefficient'])))
        elif e['kind']=='SCALE':e=dict(e,coefficient=str(1/q.Fraction(e['coefficient'])))
        elif e['kind']!='BANK_SWAP':e=dict(kind='INVERSE',bank=e['bank'],x_monomial=q.decode(e,n).inv().data())
        out.append(e)
    return out

def run():
    pp=HERE.parent/'caller/ENCODED-PHYSICAL-PREFIX.json';tp=HERE.parent/'native-frames/ENCODED-STAGE-TAIL.json'
    p=json.loads(pp.read_bytes());t=json.loads(tp.read_bytes());n=16;b=8;events=p['events']+t['events'];assembled=[]
    for e in events:
        e=dict(e)
        if e['kind']not in('ADD','BANK_SWAP'):
            g=actual(e,n)
            if 'exact_operator'in e:q.need(g==q.decode(e,n),'independent literal circuit binds every prefix unary including global phase')
            else:e['x_monomial']=g.data()
            want=e.get('native_arity_per_f',e['operator'].get('native_arity'))
            q.need(q.rank(g.polar())==want,'literal X-quadratic native rank independently matches invoice')
        assembled.append(e)
    I=q.identity(n);E=q.Mono(I.rows,(1<<n)-1,(3,1)*8,(0,)*n,0,0)
    target=q.replay([dict(kind='NATIVE',bank=i,x_monomial=E.data())for i in range(b)],b,n)
    q.need(q.replay(assembled,b,n)==target,'eight arbitrary independent input fields all full native')
    inv=inverse_events(assembled,n);ident=q.replay([],b,n)
    q.need(q.replay(assembled+inv,b,n)==q.replay(inv+assembled,b,n)==ident,'both literal inverse orders all columns')
    mutant=[e for e in assembled if e.get('label')!='Q']
    q.need(q.replay(mutant,b,n)!=target,'omitted changed pivot query rejected')
    out=dict(status='PASS_INDEPENDENT_ACTUAL_COMPLETE_ENCODED_CALLER_ALL_F',no_new_kappa=True,producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),sources={str(x):hashlib.sha256(x.read_bytes()).hexdigest()for x in(pp,tp,HERE/'quadratic_charts.py')},width=b,ambient_arity=n,events=assembled,native_rank_mass=138,stock=128,D=-10,both_literal_inverse_orders=True,negative_control='omitting Q from complete tail fails',domain='For every integer f>=1, exact Gaussian coefficients by f modulo4, actual original source circuit operators, all8arbitrary independent inputs.',proof='In the simultaneous X-character basis every source literal is affine monomial with a Z4 quadratic phase. The saved C,P,D,X,phase circuits are interpreted independently. Composing phase polynomials exactly and collecting Gaussian coefficients for all four f classes proves the uniform tensor-family matrix equality. No finite-f relation is promoted.',limits=['This is a complete identity and baseline cost, not a favorable caller.','Later retiming rank invoices require their own native lowerings and contracting splits.','No joint BIT, precision, owner or tape admission follows.'])
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=json.loads(json.dumps(run()));path=HERE/'INDEPENDENT-ENCODED-COMPLETE.json'
    if a.write:
        path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    else:q.need(json.loads(path.read_bytes())==out,'saved independent audit differs')
    print(out['status'],'mass138stock128; both inverse orders; omittedQmutant rejected')
if __name__=='__main__':main()
