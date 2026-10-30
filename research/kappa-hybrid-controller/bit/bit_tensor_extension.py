#!/usr/bin/env python3
"""Exact p3 BIT strictification and delayed-cover parameters.

The source-dependent check needs the unmodified PR4359 checkout. Arithmetic
without source replay is diagnostic only. Original primitive: DreamingOfClouds
PR589, eumemic PR555/543; global controller and delayed cover: zxv PR4359.
Native tensor substitution extends the proof of PR4412/4414. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from math import factorial
from pathlib import Path
import argparse, json, sys

T = {8:3073,22:444,50:222}
P = {1:9261,2:9394,3:553,4:308,5:714,6:77,7:577,14:444}
TESTED=Q('0.00292')
UNIFORM=Q('0.002915')
COVERED=Q('0.00291')
ADMITTED=Q('0.0029')
POWER=4000
SOURCE_HASHES={
    'mixed_productive_bit.py':'b32291b0db7fc0d332ec444c70746ab0fb03351d2e50546f8bcb64060e3ff95e',
    'bit_native_binding.py':'bf6374225f388e7531fa6475cc255bd430100ff62c38d582c41601f0739de7b7',
    'DELAYED-COVER-BRIDGE.md':'9731b93026717f5fa15851e3633cbb4bdc76eba2bffb9d6b4a3b69f7dd502443',
    'MIXED-PRODUCTIVE-BIT.json':'2f69a19f417c0e0d141c180f9b2fae3d358391b9a230f5848ee07c45450e70bf',
    'sources/pr589-regenerated/WORD.json.gz':'e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f',
    'sources/pr589-regenerated/records/frames.json':'d006b3bfe0c04afecfea7aecfa59dfe4298b99501c70da3938e40289bc2f5010',
    'sources/pr589-regenerated/records/249-records.bin':'ea44aa047a2a9cf034de8b56b2166c49cf2dbdf9cd9ed6a20299a4f2b05ef09a',
}

def need(ok,label):
    if not ok: raise ValueError(label)

@lru_cache(None)
def log_bounds(n):
    n=Q(n); power=0
    need(n>=1,'Logarithm domain')
    while n>2:n/=2;power+=1
    x=(n-1)/(n+1); count=80
    lo=2*sum((x**(2*k+1)/(2*k+1)for k in range(count)),Q(0))
    hi=lo+2*x**(2*count+1)/((2*count+1)*(1-x*x))
    if power:
        a,b=log_bounds(2);lo+=power*a;hi+=power*b
    return lo,hi

def exp_bounds(x):
    need(0<=x<Q(1,10),'Small positive exponential domain')
    count=28
    lo=sum((x**k/factorial(k)for k in range(count+1)),Q(0))
    return lo,lo+x**(count+1)/factorial(count+1)/(1-x/(count+2))

def powers(n,c):
    a,b=log_bounds(n)
    return exp_bounds(c*a)[0],exp_bounds(c*b)[1]

def moment(prof,c):
    lo=hi=Q(0)
    for n,count in prof.items():
        a,b=powers(n,c);lo+=count*n/b;hi+=count*n/a
    return lo,hi

def source_replay(root):
    folder=root/'research/kappa-rebuild/bit'
    for path,wanted in SOURCE_HASHES.items():
        need(sha256((folder/path).read_bytes()).hexdigest()==wanted,'Source byte authentication: '+path)
    relative=Path('research/kappa-next-regime/bit-compression/carrier-reuse/reference/joint_pair_dag.py')
    dependency=root/relative
    if not dependency.exists():
        dependency=root/'research/kappa-0023-productive-jobs/dependencies'/Path(*relative.parts[1:])
    need(sha256(dependency.read_bytes()).hexdigest()==
         '8a0de761642d21919e969475c3f13e5d01a4bae7343c1e1f37c586d94b676a85',
         'Source interval dependency used by the unchanged BIT generator')
    spec=spec_from_file_location('joint_pair_dag',dependency)
    source_interval=module_from_spec(spec);sys.modules['joint_pair_dag']=source_interval
    spec.loader.exec_module(source_interval)
    sys.path.insert(0,str(folder))
    import mixed_productive_bit as B
    import bit_native_binding as N
    local,streams,audit=B.audit_local(folder/'sources/pr589-regenerated/WORD.json.gz')
    native=N.run()
    need(native['ambient_rank']==50,'Pinned source native ambient rank')
    need(native['targets']==T,'Every independent productive role')
    coeff,events,idle=B.physical_controller(3,43)
    factor=B.simultaneous_monomial_factor(coeff)
    need(factor is not None,'Exact source polynomial factorization')
    targets=Counter({8:7*439})
    for term in factor['diagonal_monomials']:
        targets[(term&1)+7*(term>>1).bit_count()]+=111
    paid=Counter({r:7*n for r,n in B.LOCAL.items()})
    windows=[]
    for row in idle:
        if row['retained']:
            paid[row['rank']]+=222
            windows.append(row)
    need(dict(targets)==T and dict(paid)==P,'Whole idle invoice from literal controller')
    split=Counter(paid);split[7]+=2*split.pop(14)
    need(dict(split)==native['paid'],'Disjoint rank-seven splitting reproduces source invoice')
    need(sum(n*r for r,n in P.items())==sum(n*r for r,n in native['paid'].items()),
         'Whole idle replacement preserves every rank-one charge')
    need(len(windows)==4 and [w['rank']for w in windows]==[14,7,7,14],
         'All four literal complete idle operators')
    return {'status':'PASS_SOURCE_NATIVE_AND_WHOLE_IDLE_REPLAY',
            'local_arbitrary_columns':661,'global_productive_fields':3739,
            'complete_idle_windows':windows,'raw_owned_COPY_episodes':63,
            'raw_scalar_ADD_allowance':174908,
            'source_sha256':SOURCE_HASHES,
            'forward_reverse_local_audit':audit['status'],
            'native_audit':native['status']}

def arithmetic():
    tlo,thi=moment(T,TESTED);plo,phi=moment(P,TESTED)
    T1=sum(n*r for r,n in T.items());P1=sum(n*r for r,n in P.items())
    need(T1==45452 and P1==45227,'Complete rank-one masses')
    alpha=phi/tlo
    gamma=Q(P1)/(powers(7,TESTED)[0]*tlo)
    need(alpha<1-Q(1,125000),'Strict tested mixed moment with certified margin')
    need(gamma<Q(399,400),'Separate rank-one tail inequality')
    need(Q(399,400)**400<Q(1,2),'Exact tail decay block')
    bound=Q(1,1+Q(POWER,125000))+2*Q(1,2)**(POWER//400)
    need(bound<1,'Finite complete paid moment including the entire split tail')
    need(7**16<8**15,'Strict separation exponent below fifteen sixteenths')
    need(50<2**6 and 7<2**3,'Exact ambient and exit coefficient bounds')
    t,z=1-TESTED,1-UNIFORM
    z0=(t+z)/2;delta=z0-t;h=Q(1,16)
    B=(3+6*h)*POWER;debt=1+6*POWER*(1-z0)
    H0=((B*delta+debt)/(h*delta)).__ceil__()
    H1=(H0*(1-z0)/(z-z0)).__floor__()+1
    need(H0>=6*POWER and H1*(z-z0)>H0*(1-z0),'Explicit sufficient uniform rank')
    covergap=UNIFORM-COVERED
    need(covergap>0,'Delayed-cover slack')
    prime=256/covergap
    complete_cover=(1+covergap/4)/(1+covergap/2)
    need(complete_cover<1,'All bad-class fallback fits before lowering final leaves')
    atom=Q(3,1000);old=Q(384599,10**10)
    ordinary=(1-atom)*COVERED+atom*old
    need(atom>ordinary>ADMITTED>0 and atom<1-ordinary,'Ordinary adapter and stock costs')
    need(max(P)>min(T),'Raw rule does need strictification')
    need(moment(T,Q('.003'))[1]<moment(P,Q('.003'))[0],
         'Reject an unsupported raw saving of .003')
    return {'status':'PASS_EXACT_BIT_TENSOR_ARITHMETIC','tested_saving':TESTED,
            'compiled_uniform_saving':UNIFORM,'covered_saving':COVERED,
            'ordinary_saving':ordinary,'admitted_BIT_saving':ADMITTED,
            'targets':T,'paid':P,'target_rank_mass':T1,'paid_rank_mass':P1,
            'positive_rank_surplus':T1-P1,
            'alpha_upper':1-Q(1,125000),'gamma_upper':Q(399,400),
            'tensor_power':POWER,'cutoff_encoding':'7^'+str(POWER),
            'complete_normalized_paid_moment_upper':bound,
            'strictification_margin':1-bound,
            'uniform_compiler':{'H0':H0,'H1':H1,'N_encoding':'2^'+str(H1),
                                'theta_upper':Q(15,16),'h':h,'delta':delta,
                                'exit_log2_upper':B,'negative_log2_eta_upper':debt},
            'cover':{'prime_coefficient_times_N5':prime,'gap':covergap,
                     'complete_moment_upper':complete_cover},
            'ordinary':{'atom_power':atom,'old_saving':old,
                        'linear_adapter_gap':atom-ordinary,
                        'stock_absorption_gap':1-ordinary-atom,
                        'admission_gap':ordinary-ADMITTED},
            'materialized_tensor_or_uniform_word':False}

def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
    if isinstance(x,list):return [encode(v)for v in x]
    return x

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path);p.add_argument('--out',type=Path)
    args=p.parse_args();result=arithmetic()
    if args.source_root:result['native_source']=source_replay(args.source_root)
    else:result['native_source']={'status':'NOT_REPLAYED_ARITHMETIC_ONLY'}
    payload=json.dumps(encode(result),indent=2,sort_keys=True)+'\n'
    if args.out:args.out.write_text(payload)
    print(payload,end='')
