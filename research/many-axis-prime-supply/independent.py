#!/usr/bin/env python3
"""Independent many-axis prime-supply review; imports no primary executable.

FKS Corollary22 is an external analytic premise, not established by a finite
check. New work: ToikY with substantial OpenAI Codex assistance, Apache-2.0.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import json
from math import gcd
from pathlib import Path


HERE=Path(__file__).resolve().parent
PINS={'PR3935-README.md': (6383, '7a7f218579ae4ff192bd4b7fdf00ba008117f6d6fbcb3a70e2d021be5bf8a209', '2b665e76b4e86421bbea53b2252df8e81c91b290'), 'PR3935-tensor_plan.py': (12079, '474730f42fcd2bd24720af4e08c71fb51cc374c3e16b8b6d7e565900f1a9e7c3', '239caba2d2ccf2640c36d377949df3fb6a920cf0'), 'PR4024-PROOF.md': (11035, '7b141475955cc372c5936118ff16e8748b589b93de2d26b76da28feec9b45de4', '479a2b727b67b88efc8bdc64bde340a1c0d95ec3'), 'PR4024-README.md': (5356, '2f179858402d1eac28b1da46139fa3198a625375532cc2c53a01c1ffc565281b', '63648c961b96c6c76c305471b102e26d6b861d1b'), 'source08-assembly.tex': (46444, '763d7945b1e1ec4ebae9b799bcefcc45fa9bae6e2ffad799868a9c3d513dbd4a', '337810a1d9a58a2ecf14123420923c039ba322a6')}

def authenticate():
    for name,(length,sha,blob) in PINS.items():
        path=HERE/'source'/name
        need(not path.is_symlink(),'independent source symlink')
        raw=path.read_bytes()
        need(len(raw)==length and hashlib.sha256(raw).hexdigest()==sha,'independent source SHA: '+name)
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==blob,'independent source Git blob: '+name)

def need(test,message):
    if not test:raise ValueError(message)


def period_sufficient(ell,K):
    need(type(ell) is int and type(K) is int and ell>=3 and K>=0,'symbolic period domain')
    return K.bit_length()<=ell-3

def symbolic_threshold():
    """Tiny integers/rationals only; never form 2**(2**32)."""
    ell0=1<<32;z0=1<<16
    need(z0*z0==ell0,'threshold square')
    need(Fraction(5,2)**7>480,'log480<7 from e>5/2')
    need(2**5>24,'log24<5 from e>2')
    need(Fraction(8476,10000)**2>Fraction(1,2),'FKS weakened exponential')
    need(2*Fraction(92211,10000)<20,'two FKS error constants')
    first=z0//4-7-671*16;second=ell0//4-5-669*32
    need(first>0 and z0>4*671,'first uniform threshold and derivative')
    need(second>0 and ell0>4*669,'second uniform threshold and derivative')
    example_d=ell0**333
    need(2<=example_d<=ell0**334 and ell0<8*example_d,'new domain example fails old logt>8d premise')
    need(period_sufficient(ell0,ell0**10),'symbolic polynomial period example')
    return dict(ell0=ell0,dimension_exponent=334,sqrt_ell0=z0,
                new_regime_example={'ell':ell0,'d_power':333,'d_bit_length':example_d.bit_length(),'old_logt_gt_8d_fails':True,'no_target_power_or_axis_list_materialized':True},
                first_log_margin_lower=first,second_log_margin_lower=second,
                first_derivative_margin=z0-4*671,second_derivative_margin=ell0-4*669)


def sieve(limit):
    """Independent small-fixture Eratosthenes oracle, not trial division."""
    need(type(limit) is int and 2<=limit<=1<<20,'finite sieve bound')
    prime=bytearray(b'\1')*(limit+1);prime[:2]=b'\0\0';p=2
    while p*p<=limit:
        if prime[p]:
            start=p*p;prime[start:limit+1:p]=b'\0'*(((limit-start)//p)+1)
        p+=1
    return prime


def interval(t,d):
    return Fraction(t*(3*d-1),3*d),Fraction(t*(4*d-1),4*d)


def oracle(ell,flags,target_halo=16,w=2):
    need(type(ell) is int and 3<=ell<=20,'small finite ell')
    need(type(flags) in (tuple,list) and flags and all(type(f) is int and f in (0,1) for f in flags),'complete finite flag grammar')
    need(flags[-1]==1,'final target axis is r')
    need(type(target_halo) is int and target_halo>=0 and type(w) is int and w>=0,'period parameters')
    D=len(flags);d=D+1;r=1<<ell;prime=sieve(r);pools={}
    for flag in (0,1):
        t=r if flag else r//2;a,b=interval(t,d)
        lo=a.numerator//a.denominator+1;hi=b.numerator//b.denominator
        pools[flag]=[n for n in range(lo,hi+1) if prime[n]]
    used={0:0,1:0};lengths=[];targets=[]
    for flag in flags:
        need(used[flag]<len(pools[flag]),'insufficient primes in small fixture; not production theorem')
        lengths.append(pools[flag][used[flag]]);used[flag]+=1;targets.append(r if flag else r//2)
    for s,t in zip(lengths,targets):
        gap=t-s
        need(s>2 and s%2==1 and prime[s],'odd prime source axis')
        need(4*d*gap>s and (2*d-1)*gap<s,'literal source ratio predicates')
        need(s>2*(target_halo+2*w),'literal source period predicate')
        need(0<s<t<2*s,'literal near-one source predicate')
    need(len(set(lengths))==D,'all actual source lengths distinct')
    need(all(gcd(a,b)==1 for i,a in enumerate(lengths) for b in lengths[:i]),'pairwise coprime')
    need(all(gcd(s,r)==1 for s in lengths),'coprime to power-of-two target')
    S=T=1
    for s,t in zip(lengths,targets):S*=s;T*=t
    need(3*S>2*T,'source/target product ratio exceeds2/3')
    need(Fraction(1)-Fraction(D,3*d)>Fraction(2,3),'Bernoulli lower bound')
    source_bits=bytes((s>>bit)&1 for s in lengths for bit in range(ell))
    flag_bits=bytes(flags[:-1])
    return dict(ell=ell,D=D,d=d,flags=list(flags),targets=targets,primes=lengths,
                source_bits_sha256=hashlib.sha256(source_bits).hexdigest(),
                flag_bits_sha256=hashlib.sha256(flag_bits).hexdigest(),S=S,T=T,
                source_bit_length=D*ell,flag_bit_length=D-1,source_guard_checks=D,
                encoded_execution=False,production_tensor_execution=False,
                address_bits=sum(ell if f else ell-1 for f in flags),
                band_prime_counts={str(k):len(v) for k,v in pools.items()})


def no_duplicates(pairs):
    out={}
    for key,value in pairs:
        need(key not in out,'duplicate receipt key')
        out[key]=value
    return out


def check_receipt(path):
    receipt=json.loads(path.read_text(),object_pairs_hook=no_duplicates)
    need(type(receipt) is dict and type(receipt.get('schema_version')) is int and receipt['schema_version']==1,'receipt schema')
    need(receipt.get('mode')=='host-reference' and receipt.get('encoded_execution') is False,'host-reference scope')
    need(type(receipt.get('cases')) is list and receipt['cases'],'nonempty finite cases')
    for row in receipt['cases']:
        expected=oracle(row['ell'],row['flags'],row.get('target_halo',16),row.get('w',2))
        for key,value in expected.items():
            if key=='band_prime_counts':continue
            need(key in row and type(row[key]) is type(value) and row[key]==value,'independent exact field: '+key)
    threshold=receipt['threshold']
    exact={'ell0':1<<32,'dimension_power':334,'z0':1<<16,'error_log_upper':10743,
           'error_exponential_lower':16384,'volume_log_upper':21413,'volume_exponential_lower':1<<30,
           'analytic_input_imported':True,'analytic_input_reproved':False,'giant_power_constructed':False}
    for key,value in exact.items():
        need(key in threshold and type(threshold[key]) is type(value) and threshold[key]==value,'independent symbolic threshold field: '+key)
    return len(receipt['cases'])


def audit():
    configs=((8,[1]),(12,[0,1,1]),(14,[1,0,1,1]),(14,[0,1,0,1,0,1]))
    return {'threshold':symbolic_threshold(),'cases':[oracle(ell,flags) for ell,flags in configs]}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,default=HERE/'RESULT.json');parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
    try:
        result=audit()
        if args.self_test:count=len(result['cases'])
        else:
            authenticate();count=check_receipt(args.receipt)
        print('PASS_INDEPENDENT_MANY_AXIS_PRIME_SUPPLY cases='+str(count)+' external_FKS_premise no_production_prime_search')
    except Exception as error:
        raise SystemExit('FAIL_INDEPENDENT_MANY_AXIS_PRIME_SUPPLY '+str(error))
