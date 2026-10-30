#!/usr/bin/env python3
"""Exact free-group search of legal pre-target/post-source H wrappers.

An algebraic screen, not an actual native frame certificate.  H_s^2=I is
the only relation; different stages do not commute.  Forward permits H_s
on Y before the call and X after it; backward permits H_s on X before and
Y after.  These are the physical contacts proposed by the caller owner.
The search asks whether these wrappers alone remove the coupled residual
on the terminal hole bank, while a full-frame bank may retain a free word.
Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json

HERE=Path(__file__).resolve().parent
ONE={():1}
ZERO={}

def word(a,b):
    out=list(a)
    for letter in b:
        if out and out[-1]==letter:
            out.pop()
        else:
            out.append(letter)
    return tuple(out)

def add(a,b):
    out=Counter(a)
    out.update(b)
    return {k:v for k,v in out.items() if v}

def multiply(a,b):
    out=Counter()
    for u,c in a.items():
        for v,d in b.items():
            out[word(u,v)]+=c*d
    return {k:v for k,v in out.items() if v}

def mm(a,b):
    return [[add(multiply(a[i][0],b[0][j]),multiply(a[i][1],b[1][j]))
             for j in range(2)] for i in range(2)]

def identity():
    return [[ONE,ZERO],[ZERO,ONE]]

def local(stage,forward,pre,post):
    h={(stage,):1}
    if forward:
        before=[[ONE,ZERO],[ZERO,h if pre else ONE]]
        shear=[[ONE,ZERO],[h,ONE]]
        after=[[h if post else ONE,ZERO],[ZERO,ONE]]
    else:
        before=[[h if pre else ONE,ZERO],[ZERO,ONE]]
        shear=[[ONE,{(stage,):-1}],[ZERO,ONE]]
        after=[[ONE,ZERO],[ZERO,h if post else ONE]]
    return mm(after,mm(shear,before))

def encode(polynomial):
    return [{'word':list(w),'coefficient':c} for w,c in sorted(polynomial.items())]

def run():
    words=[]
    off_diagonal=[]
    for choices in product((0,1),repeat=6):
        result=identity()
        for stage in range(3):
            result=mm(local(stage,stage%2==0,*choices[2*stage:2*stage+2]),result)
        record={'pre_post_bits':list(choices),'operator':[[encode(p) for p in row] for row in result]}
        words.append(record)
        if not result[0][0] and not result[1][1]:
            record['terminal_hole_bank_already_identity']=result[1][0]==ONE
            record['terminal_hole_bank_scalar_sign_only']=result[1][0] in (ONE,{():-1})
            off_diagonal.append(record)
    # The fully wrapped construction has the noncommuting monodromy H2 H1 H0.
    full=identity()
    for s in range(3):
        full=mm(local(s,s%2==0,1,1),full)
    monodromy={(2,1,0):1}
    assert full==[[ZERO,{(2,1,0):-1}],[monodromy,ZERO]]
    assert off_diagonal and not any(r['terminal_hole_bank_scalar_sign_only'] for r in off_diagonal)
    # In the same-owner specialization H0=H1=H2=H, the residual is H, not I.
    same={}
    for w,c in full[1][0].items():
        v=()
        for _ in w:
            v=word(v,(0,))
        same=add(same,{v:c})
    assert same=={(0,):1}
    return {'schema':'free-involution-wrapper-screen/1','status':'PASS_EXACT_SCOPED_SCREEN',
            'source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'menu_size':len(words),'pure_swap_endpoints':off_diagonal,
            'fully_wrapped_monodromy':'H2 H1 H0',
            'identity_hole_residual_found':False,
            'scope':'Only binary single-stage involution wrappers at the stated six contacts. No claim about additional scalar combinations, interstage gadgets, changed heads, or identities among the actual owners.',
            'physical_frame_verification':'Owned by the caller reconstruction; not implied by this abstract screen.',
            'new_kappa':False}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'FREE-INVOLUTION-WRAP-PROBE.json')
    args=parser.parse_args()
    result=run()
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'menu_size':result['menu_size'],'pure_swap_count':len(result['pure_swap_endpoints'])}))

if __name__=='__main__':
    main()
