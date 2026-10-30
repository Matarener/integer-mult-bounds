#!/usr/bin/env python3
"""Exact, standard-library group-ring replay for the two specified alphabets.

Passing establishes a finite uniform operator identity, not a tape supplier.
Group elements are never identified merely because one tensor specialization
has the same action. Scalar coefficients are F2 (bit) or integers (complex).
"""
import json
from pathlib import Path
import sys


def identity(W):
    return tuple(tuple(int(i==j) for j in range(W)) for i in range(W))


def outer(u,v):
    return tuple(tuple(x*y for y in v) for x in u)


def mm(A,B):
    return tuple(tuple(sum(a*b for a,b in zip(row,col)) for col in zip(*B)) for row in A)


def add_term(out,key,coeff,mod=None):
    old=out.get(key,tuple(tuple(0 for x in row) for row in coeff))
    val=tuple(tuple((a+b)%mod if mod else a+b for a,b in zip(ra,rb)) for ra,rb in zip(old,coeff))
    if any(any(row) for row in val):
        out[key]=val
    else:
        out.pop(key,None)


def bit_replay(word,W=4):
    zero=(0,)*9
    state={zero:identity(W)}
    for move in word:
        B=tuple(move['B'])
        u,v=move['u'],move['v']
        assert sum(a*b for a,b in zip(u,v))%2==1
        assert len(B)==9 and len(u)==len(v)==W
        # All 2x2 minors vanish and the frame is nonzero: rational rank one.
        assert any(B)
        assert all(B[3*i+j]*B[3*k+l]==B[3*i+l]*B[3*k+j]
                   for i in range(3) for k in range(3) for j in range(3) for l in range(3))
        N=outer(u,v)
        nxt=dict(state)
        for A,coeff in state.items():
            part=mm(N,coeff)
            add_term(nxt,A,part,2)
            add_term(nxt,tuple(a+b for a,b in zip(A,B)),part,2)
        state=nxt
    target=tuple(2*int(i//3==i%3) for i in range(9))
    return state=={target:identity(W)},len(state)


def normalize(shift,re,im):
    while shift and all(x%2==0 for x in re+im):
        shift-=1
        re=tuple(x//2 for x in re)
        im=tuple(x//2 for x in im)
    return shift,tuple(re),tuple(im)


GI=normalize(0,tuple(int(i==j) for i in range(8) for j in range(8)),(0,)*64)


def had(key,direction,covector):
    assert direction and covector and (direction&covector).bit_count()%2
    shift,re,im=key
    out_re=[]
    out_im=[]
    for x in range(8):
        sign=-1 if (x&covector).bit_count()%2 else 1
        for j in range(8):
            a=sign*re[8*x+j]+re[8*(x^direction)+j]
            b=sign*im[8*x+j]+im[8*(x^direction)+j]
            out_re.append(a-b)
            out_im.append(a+b)
    return normalize(shift+1,tuple(out_re),tuple(out_im))


def cnot(key,control,target):
    shift,re,im=key
    perm=[x^(((x>>control)&1)<<target) for x in range(8)]
    return normalize(shift,tuple(re[8*x+j] for x in perm for j in range(8)),
                     tuple(im[8*x+j] for x in perm for j in range(8)))


def complex_replay(word,insertions=None,W=3):
    state={GI:identity(W)}
    for t,move in enumerate(word):
        if insertions and t in insertions:
            role,control,target=insertions[t]
            nxt={}
            for key,coeff in state.items():
                stationary=tuple(tuple(0 if i==role else x for x in row) for i,row in enumerate(coeff))
                moving=tuple(tuple(x if i==role else 0 for x in row) for i,row in enumerate(coeff))
                add_term(nxt,key,stationary)
                add_term(nxt,cnot(key,control,target),moving)
            state=nxt
        u,v=move['u'],move['v']
        assert len(u)==len(v)==W and sum(a*b for a,b in zip(u,v))==1
        N=outer(u,v)
        nxt=dict(state)
        for key,coeff in state.items():
            part=mm(N,coeff)
            add_term(nxt,key,tuple(tuple(-x for x in row) for row in part))
            add_term(nxt,had(key,*move['frame']),part)
        state=nxt
    target=GI
    for i in range(3):
        target=had(target,1<<i,1<<i)
    return state=={target:identity(W)},len(state)


def naive(side,W):
    out=[]
    for role in range(W):
        for axis in range(3):
            uv=[int(i==role) for i in range(W)]
            move=dict(u=uv,v=list(uv))
            if side=='bit':
                move['B']=[2*int(j==3*axis+axis) for j in range(9)]
            else:
                move['frame']=[1<<axis,1<<axis]
            out.append(move)
    return out


def checks():
    bw=naive('bit',4)
    cw=naive('complex',3)
    assert bit_replay(bw)==(True,1)
    assert not bit_replay(bw[:-1])[0]
    assert complex_replay(cw)==(True,1)
    assert not complex_replay(cw[:-1])[0]
    assert not complex_replay(cw,{2:(0,0,1)})[0]
    # Nontrivial mixing: conjugate every scalar projector by the same CNOT.
    for side,word,W,fn in [('bit',bw,4,bit_replay),('complex',cw,3,complex_replay)]:
        S=[list(row) for row in identity(W)]
        S[0][1]=1
        Sinv=[list(row) for row in identity(W)]
        Sinv[0][1]=1 if side=='bit' else -1
        conjugated=[]
        for move in word:
            u=[sum(S[i][k]*move['u'][k] for k in range(W)) for i in range(W)]
            v=[sum(move['v'][k]*Sinv[k][i] for k in range(W)) for i in range(W)]
            if side=='bit':
                u=[x%2 for x in u];v=[x%2 for x in v]
            conjugated.append(dict(move,u=u,v=v))
        assert fn(conjugated,W=W)==(True,1)
    # Finite-field alias: I -> shear I+3E00 agrees modulo 3, not uniformly.
    alias=[dict(move) for move in bw]
    alias[0]=dict(alias[0],B=[8,0,0,0,0,0,0,0,0])
    assert all((a-b)%3==0 for a,b in zip(alias[0]['B'],bw[0]['B']))
    assert not bit_replay(alias)[0]
    # One-column linear dependence is not a group-ring identity:
    # I + (-I) vanishes at f=1, but gives 2I at f=2.
    minusI=normalize(0,tuple(-x for x in GI[1]),GI[2])
    assert minusI!=GI
    assert all(a+b==0 for a,b in zip(GI[1],minusI[1]))
    assert 1**2+(-1)**2==2
    return dict(positive_uniform_controls=4,deleted_child_controls=2,
                misplaced_free_map_rejected=True,finite_field_alias_rejected=True,
                one_column_cancellation_not_uniform=True)


if __name__=='__main__':
    result={'controls':checks()}
    for name in sys.argv[1:]:
        data=json.loads(Path(name).read_text())
        if data.get('candidate'):
            if data['side']=='bit':
                passed,terms=bit_replay(data['candidate'],data['W'])
            else:
                ins={int(k):v for k,v in data.get('insertions',{}).items()}
                passed,terms=complex_replay(data['candidate'],ins,data['W'])
            result[name]={'uniform_identity':passed,'remaining_group_terms':terms}
        else:
            result[name]={'uniform_identity':'not tested: no candidate',
                          'screen_result':data['result']}
    print(json.dumps(result,indent=2))
