#!/usr/bin/env python3
"""Independent Codex verifier for DLamdata; Apache-2.0.
Derived before comparison with the lead; no predecessor code imports.
Only the root path and this attribution were adapted for publication.
"""
from fractions import Fraction as F
from functools import lru_cache
from math import isqrt
from pathlib import Path
import json
import hashlib

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'research/p104-helper470-twin-rung-removal/RESULT.json'
raw=SOURCE.read_bytes()
r=json.loads(raw)
p={k:F(v) for k,v in r['complete_cost']['outer']['parameters'].items()}

def need(test, message):
    if not test:
        raise ValueError(message)

def selected_checks(p, H):
    u,b,a,q,delta=(p[k] for k in ('complex_uniform_saving','b','a','q','stop'))
    sigma,tau,target=1-b,1-a,1-q
    leaf=sigma+delta*b
    need(0 < sigma < tau < target < 1, 'strict internal exponent order')
    need(0 < delta < 1 and leaf < tau, 'strict leaf gap')
    need(u>b, 'uniform moment gap')
    need(H*(u-b)==47005, 'current compiled-moment bound')
    return dict(sigma=sigma,tau=tau,target=target,leaf=leaf,
                tau_minus_sigma=tau-sigma,tau_minus_leaf=tau-leaf,
                target_minus_tau=target-tau,target_minus_leaf=target-leaf,
                uniform_minus_b=u-b,moment_power=H*(u-b))

s=selected_checks(p,r['complete_cost']['compiler']['H'])
need(p['lambda_prime']==s['target'], 'record target agrees')
need(F(r['complete_cost']['ordinary_BIT']['atom'])==F(1,250),'current atom')
controls=0
for changes in ({'complex_uniform_saving':p['b']},{'q':p['a']},{'stop':F(1)}):
    bad=dict(p,**changes)
    try: selected_checks(bad,r['complete_cost']['compiler']['H'])
    except ValueError: controls+=1
    else: raise ValueError('failed rejection control')

# Exact separate toy recurrence, m=16, P/W=2, sigma=1/2, tau=3/4.
# It has moment 1/2 at sigma and 1/4 at tau. Node work includes every remainder.
def fourth_floor(n):
    return isqrt(isqrt(n))
def cutoff(h):
    t=fourth_floor(h)
    return max(16,t+(t**4<h))

def cost(h,e):
    S=cutoff(h)
    @lru_cache(None)
    def rec(n):
        if n<S: return F(n)
        return F(fourth_floor(n**3)+n%16)+2*rec(n//16)
    return rec(e)

widths=list(range(1,4097))+[10**k+d for k in range(5,13) for d in (-17,-1,0,1,15,16,17)]
for h in widths:
    S=cutoff(h)
    c=cost(h,h)
    # Induction proves F <=4 e^(3/4)+sqrt(S e). This stricter integer lower
    # approximation checks the model without floating-point arithmetic.
    lower_majorant=4*fourth_floor(h**3)+isqrt(S*h)
    need(c<=lower_majorant,'toy stopped recurrence')

# A direct finite deferred schedule checks full coverage (including the tail)
# and volume reset; the bound follows from the independent induction in the note.
phase_cases=0
for g in widths[::17]+[16**k for k in range(1,11)]:
    h=g; total=F(0); processed=0
    while h>32:
        reserve=h//16
        active=h-reserve
        total+=2*(cost(h,active)+fourth_floor(h**3)+1)
        processed+=active
        h=reserve
    total+=h
    processed+=h
    need(processed==g,'selected-axis partition')
    need(total<=55*fourth_floor(g**3),'toy deferred envelope')
    phase_cases+=1

# A genuine bad alternative: eager treatment of floor(g/32) reserved axes.
# At g=16^k its ratio to g^(3/4) grows as 2^k/32 (for k>=2).
eager=[]
for k in range(2,11):
    g=16**k
    ratio=F(g//32,8**k)
    need(ratio==F(2**k,32),'eager linear cost ratio')
    eager.append(str(ratio))

print(json.dumps({'source_sha256':hashlib.sha256(raw).hexdigest(),
                  'selected_exact':{k:str(v) for k,v in s.items()},
                  'selected_rejections':controls,
                  'stopped_toy_cases':len(widths),'deferred_toy_cases':phase_cases,
                  'eager_cost_ratios':eager},indent=2))
print('PASS_INDEPENDENT_DEFERRED_RECURRENCE')
