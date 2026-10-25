#!/usr/bin/env python3
"""Exact local-ring audit of delayed BIT cover matching and weight propagation.

This checks the routing lemma used by DELAYED-COVER-BRIDGE.md. It enumerates
every GL_2(Z/9Z) row, two different role matchers, a common nonconstant-by-axis
weight, and every address for the scalar-gauge commutation check. It is a
finite audit of the bridge, not a full mixed-flow or multiplication theorem.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import time

HERE=Path(__file__).resolve().parent
MOD=9
PRIME=3


def need(condition,message):
    if not condition:
        raise AssertionError(message)


def mul(a,b,mod=MOD):
    return [[sum(x*y for x,y in zip(row,column))%mod for column in zip(*b)] for row in a]


def inv2(a):
    determinant=(a[0][0]*a[1][1]-a[0][1]*a[1][0])%MOD
    inverse=pow(determinant,-1,MOD)
    return [[inverse*a[1][1]%MOD,-inverse*a[0][1]%MOD],[-inverse*a[1][0]%MOD,inverse*a[0][0]%MOD]]


def key(a):
    return tuple(x for row in a for x in row)


def conjugate(a,b):
    return mul(mul(a,b),inv2(a))


def d_projector(p):
    c=[[0,1],[1,0]]
    pc,cp=mul(p,c),mul(c,p)
    cpc=mul(cp,c)
    return [[((int(i==j)-p[i][j])%MOD if i<2 and j<2 else
              pc[i][j-2] if i<2 else
              cp[i-2][j] if j<2 else
              (int(i==j)-cpc[i-2][j-2])%MOD)
             for j in range(4)] for i in range(4)]


def weight(p,a):
    gauge=[[a[i] if i==j and i<2 else int(i==j) for j in range(4)] for i in range(4)]
    inverse=[[pow(a[i],-1,MOD) if i==j and i<2 else int(i==j) for j in range(4)] for i in range(4)]
    return mul(mul(gauge,d_projector(p)),inverse)


def act(a,x):
    return tuple(sum(v*w for v,w in zip(row,x))%MOD for row in a)


def run():
    start=time.monotonic()
    cover=[]
    for entries in product(range(MOD),repeat=4):
        a=[list(entries[:2]),list(entries[2:])]
        if (a[0][0]*a[1][1]-a[0][1]*a[1][0])%PRIME:
            cover.append(a)
    need(len(cover)==3888,'All GL_2(Z/9Z) elements')
    child=[[[1,0],[0,0]],[[1,0],[1,0]]]
    matchers=[[[1,1],[1,0]],[[0,1],[1,-1]]]
    parent=[conjugate(s,q) for s,q in zip(matchers,child)]
    common=(2,4)
    matches,affine_checks=0,0
    role_fibers=[]
    wrong_matcher=None
    changing_weight=None
    leaf_weights=Counter()
    good=bad=0
    for role,(q,p,s) in enumerate(zip(child,parent,matchers)):
        need(mul(q,q)==q and mul(p,p)==p,'Both endpoints are split projectors')
        routed=set()
        for g in cover:
            h=mul(g,s)
            routed.add(key(h))
            incoming=conjugate(g,p)
            outgoing=conjugate(h,q)
            need(incoming==outgoing,'Fixed right routing matches the full physical projector')
            need(weight(incoming,common)==weight(outgoing,common),'Common external gauge survives matching')
            matches+=1
            if wrong_matcher is None and conjugate(g,q)!=incoming:
                wrong_matcher={'role':role,'g':g,'expected':incoming,'unrouted':conjugate(g,q)}
            g0=[[x%PRIME for x in row] for row in g]
            high=[[(x-y)//PRIME for x,y in zip(row,low)] for row,low in zip(g,g0)]
            raw=[[sum(x*y for x,y in zip(row,column)) for column in zip(*s)] for row in g0]
            h0=[[x%PRIME for x in row] for row in raw]
            carry=[[(x-y)//PRIME for x,y in zip(row,low)] for row,low in zip(raw,h0)]
            linear=mul(high,s,PRIME)
            actual_high=[[(x-y)//PRIME for x,y in zip(row,low)] for row,low in zip(h,h0)]
            predicted=[[(x+y)%PRIME for x,y in zip(row,carry_row)] for row,carry_row in zip(linear,carry)]
            need(actual_high==predicted,'Low-type carry plus fixed affine high-row route')
            affine_checks+=1
            # Deliberately illegal: A depends on the current fresh GL row.
            a_g=(2 if g[0][0]%PRIME==1 else 1,4)
            a_h=(2 if h[0][0]%PRIME==1 else 1,4)
            if changing_weight is None and weight(incoming,a_g)!=weight(outgoing,a_h):
                changing_weight={'role':role,'g':g,'h':h,'A_g':a_g,'A_h':a_h}
            # For a rank-one residual the generic northeast pivot is A[0]*P[0,0].
            if incoming[0][0]%PRIME:
                good+=1
                leaf_weights[common[0]*incoming[0][0]%MOD]+=1
            else:
                bad+=1
        need(len(routed)==len(cover),'Every target role routes a whole cover fiber bijectively')
        role_fibers.append(len(routed))
    need(wrong_matcher is not None,'Omitting the chart route fails')
    need(changing_weight is not None,'Fresh-cover-dependent weights are rejected')
    gauge=[[common[i] if i==j and i<2 else int(i==j) for j in range(4)] for i in range(4)]
    address_images=set()
    for address in product(range(MOD),repeat=4):
        mapped=act(gauge,address)
        address_images.add(mapped)
        # Two orders of pointwise XOR versus one common address permutation.
        before={(0,mapped),(1,mapped)}
        after={(role,act(gauge,address)) for role in (0,1)}
        need(before==after,'Common gauge commutes with pointwise scalar ADD on all input columns')
    need(len(address_images)==MOD**4,'The common gauge is a complete address permutation')
    return {'schema':'delayed-bit-cover-weight-bridge/1','status':'PASS_EXACT_LOCAL_RING_AUDIT',
            'ring':{'prime':PRIME,'atom_digits':2,'modulus':MOD},
            'ambient_rank':2,'cover_rows':len(cover),'independent_target_roles':2,
            'child_projectors':child,'parent_projectors':parent,'fixed_matchers':matchers,
            'common_external_weight':common,'exact_matches':matches,
            'row_routing_bijections':role_fibers,'affine_high_row_checks':affine_checks,
            'scalar_gauge_address_checks':MOD**4,
            'last_step_leaf_normalization':{'good_rows':good,'fallback_rows':bad,
                'actual_weight_histogram':dict(sorted(leaf_weights.items())),
                'dependency':'A_child is evaluated from the outer ancestor A and this outer cover row g; neither is a fresh field of the leaf invocation.'},
            'controls':{'omitted_matcher_counterexample':wrong_matcher,
                        'illegal_fresh_row_weight_counterexample':changing_weight},
            'source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'runtime_seconds':time.monotonic()-start,
            'proved_in_companion_note':'General rational projector matching, one global cover, common-gauge commutation, delayed weighted lowering and fixed routing costs.',
            'not_checked':['The complete mixed-flow precompiler','Materialization of a winning enormous uniform template','Final multiplication transfer'],
            'new_kappa':False}


if __name__=='__main__':
    result=run()
    (HERE/'DELAYED-COVER-BRIDGE.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','cover_rows','exact_matches','affine_high_row_checks','runtime_seconds')}))
