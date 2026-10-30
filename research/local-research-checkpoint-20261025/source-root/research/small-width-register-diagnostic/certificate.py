#!/usr/bin/env python3
"""Independent exact certificates; standard library only, no SMT dependency."""
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

from replay import checks


def lee(b):
    b%=4
    return Fraction(min(b,4-b),2)


def pair_character_certificate():
    # lambda_i,s(B) = B_ii + sum_{j!=i} s_j B_ij; target B=2I.
    chars=[]
    for i in range(3):
        others=[j for j in range(3) if j!=i]
        for signs in itertools.product((-1,1),repeat=2):
            q=[0]*9;q[3*i+i]=1
            for j,s in zip(others,signs):q[3*i+j]=s
            chars.append(tuple(q))
    lines=[]
    for v in itertools.product((-1,0,1),repeat=3):
        nonzero=[x for x in v if x]
        if len(nonzero) in (1,2) and nonzero[0]==1:lines.append(v)
    verified=[]
    for v in lines:
        norm=sum(x*x for x in v)
        # Dependence is modulo 4; these four residues cover every integer alpha.
        for alpha in range(4):
            B=tuple(2*alpha*v[i]*v[j]//norm for i in range(3) for j in range(3))
            average=sum((lee(sum(x*y for x,y in zip(q,B))) for q in chars),Fraction(0))/4
            assert average==alpha%2
            verified.append({'line':list(v),'alpha_mod4':alpha,'summed_cost':str(average)})
    target=(2,0,0,0,2,0,0,0,2)
    assert all(lee(sum(x*y for x,y in zip(q,target)))==1 for q in chars)
    # A genuine three-coordinate direction is outside the no-saving bound.
    # Enlarge denominator clearing to 6: 6 P_(111) = 2 all-ones, 6I ≡ 2I.
    triple_B=(2,)*9
    triple_cost=sum((lee(sum(x*y for x,y in zip(q,triple_B))) for q in chars),Fraction(0))/4
    assert triple_cost==3
    return {'functionals':[list(q) for q in chars],
            'checked_residue_cases':len(verified),'cases':verified,
            'target_cost':3,'bound':'3W <= number of odd-amplitude calls <= total paid rank',
            'three_coordinate_projector_cost_under_same_screen':str(triple_cost),
            'scope':'Common target I; abelian rational shear group; scalar F2 mixing; integer multiples of coordinate or signed two-coordinate orthogonal projectors; rank-one paid factors.'}


def symmetric_profile_certificate():
    # All 13 signed-cube lines and the 12 signed permutations of (1,1,2).
    # Clear denominators with B=6A; the target is 6I, still 2I modulo 4.
    classes={}
    for v in itertools.product((-2,-1,0,1,2),repeat=3):
        non=[x for x in v if x];norm=sum(x*x for x in v)
        if not non or non[0]<0 or norm not in (1,2,3,6):continue
        for a in (1,2):
            B=tuple(6*a*v[i]*v[j]//norm for i in range(3) for j in range(3))
            classes.setdefault((norm,a),[]).append(B)
    keys=sorted(classes)
    def profile(q):
        return tuple(sum((lee(sum(x*y for x,y in zip(q,[B[0],B[4],B[8],B[1],B[2],B[5]])))
                          for B in classes[k]),Fraction(0))/len(classes[k]) for k in keys)
    profiles={}
    for q in itertools.product(range(4),repeat=6):
        if sum(q[:3])%2:profiles[q]=profile(q)
    assert len(profiles)==2048
    # A finite signed-permutation average turns each profile into a valid
    # bound on every member of its class, not merely on the class average.
    cube_weights=[(Fraction(2),(0,0,1,0,0,1)),(Fraction(1),(0,0,1,0,1,1))]
    cube_cost=[sum(w*profiles[q][j] for w,q in cube_weights) for j in range(8)]
    assert all(c<=1 for k,c in zip(keys,cube_cost) if k[0]!=6)
    assert sum(w for w,q in cube_weights)==3
    # With the (1,1,2) orbit added, matching primal and dual certificates show
    # the exact optimum of this weighted character-bound LP is 5/2.
    extended_weights=[(Fraction(3,4),(0,0,1,0,0,0)),
                      (Fraction(3,2),(0,0,1,1,1,1)),
                      (Fraction(1,4),(1,1,1,2,2,2))]
    ext_cost=[sum(w*profiles[q][j] for w,q in extended_weights) for j in range(8)]
    assert all(c<=1 for c in ext_cost)
    assert sum(w for w,q in extended_weights)==Fraction(5,2)
    dual=[Fraction(3,4),Fraction(0),Fraction(3,4),Fraction(0),
          Fraction(1,4),Fraction(0),Fraction(3,4),Fraction(0)]
    assert sum(dual)==Fraction(5,2)
    assert all(sum(y*c for y,c in zip(dual,pro))>=1 for pro in profiles.values())
    # Integer amplitudes of other parity classes do not alter the conclusion.
    for Bs in classes.values():
        for B in Bs:
            for q in profiles:
                b=sum(x*y for x,y in zip(q,[B[0],B[4],B[8],B[1],B[2],B[5]]))
                assert lee(3*b)==lee(b) and lee(4*b)==0
    return {'class_order':[list(k) for k in keys],
            'class_sizes':[len(classes[k]) for k in keys],
            'characters_checked':len(profiles),'distinct_profiles':len(set(profiles.values())),
            'signed_cube_bound':'paid rank >= 3W',
            'signed_cube_weights':[[str(w),list(q)] for w,q in cube_weights],
            'signed_cube_costs':[str(c) for c in cube_cost],
            'extended_optimal_weighted_character_bound':'paid rank >= (5/2)W',
            'extended_weights':[[str(w),list(q)] for w,q in extended_weights],
            'extended_costs':[str(c) for c in ext_cost],
            'extended_dual':[str(y) for y in dual],
            'interpretation':'The (1,1,2) orbit escapes this exact weighted-character exclusion. It is not a candidate network or evidence of a saving.'}


def step(state,t,feedback,inverse=False,insertions=None):
    # One column in F5; no scalar matrix or symbolic solver is shared with screen.py.
    r=t%3; axis=t//3
    direction=1<<axis
    v=[0]*3;v[r]=1
    for j,c in zip((j for j in range(3) if j!=r),feedback):v[j]=c
    def free(S):
        if insertions and t in insertions:
            role,cb,tb=insertions[t]
            old=list(S)
            for x in range(8):S[8*role+x]=old[8*role+(x^(((x>>cb)&1)<<tb))]
        return S
    S=list(state)
    if not inverse:S=free(S)
    dot=[sum(v[j]*S[8*j+x] for j in range(3))%5 for x in range(8)]
    coefficient=2 if inverse else 4
    new=[]
    for x in range(8):
        Hdot=coefficient*((-1 if x&direction else 1)*dot[x]+dot[x^direction])
        new.append((S[8*r+x]+Hdot-dot[x])%5)
    S[8*r:8*r+8]=new
    if inverse:S=free(S)
    return tuple(S)


def frontier_hash(states):
    return hashlib.sha256(b''.join(bytes(s) for s in sorted(states))).hexdigest()


def complex_mitm(E,insertions):
    options=list(itertools.product((-1,0,1),repeat=2))
    start=tuple(int(i==0) for i in range(24))
    goal=(4,)*8+(0,)*16
    # Every individual inverse is checked on a complete basis, for every choice.
    for t in range(E):
        for fb in options:
            for j in range(24):
                basis=tuple(int(i==j) for i in range(24))
                assert step(step(basis,t,fb,insertions=insertions),t,fb,True,insertions)==basis
    split=E//2
    left={start};left_counts=[1]
    for t in range(split):
        left={step(s,t,fb,insertions=insertions) for s in left for fb in options}
        left_counts.append(len(left))
    right={goal};right_counts=[1]
    for t in reversed(range(split,E)):
        right={step(s,t,fb,True,insertions) for s in right for fb in options}
        right_counts.append(len(right))
    return {'paid_calls':E,'coefficient_words_covered':9**E,
            'split':split,'forward_unique_counts':left_counts,
            'backward_unique_counts':right_counts,'intersection_size':len(left&right),
            'forward_sha256':frontier_hash(left),'backward_sha256':frontier_hash(right),
            'scope':'Fixed cyclic target-register/coordinate schedule, signed ternary feedback, specified free CNOT placements; exact one-column necessary condition over F5.'}


def target_moments():
    def below(W,s,p,q):
        # (s/(3W))*3^(p/q)<1 iff s^q*3^p<(3W)^q, exactly.
        return pow(s,q)*pow(3,p)<pow(3*W,q)
    assert below(4,11,79,1000)
    assert not below(4,11,2,25)
    assert below(3,8,3,40)
    assert below(64,191,1,255)
    ordinary=Fraction(384599,10**10)
    A=(1-Fraction(3,40))*Fraction(79,1000)+Fraction(3,40)*ordinary
    assert Fraction(7,100)<A<Fraction(3,40)<1-A
    assert Fraction(99,100)*Fraction(3,40)>Fraction(7,100)
    assert Fraction(7,100)/(1+Fraction(7,100))>Fraction(1,16)
    return {'bit_rank_one_target':{'m':3,'W':4,'children':11,'coarse_saving':'79/1000'},
            'complex_rank_one_target':{'m':3,'W':3,'children':8,'saving':'3/40'},
            'hypothetical_bit_wrapper_effective_saving':str(A),
            'status':'Numerical design specifications only; no supplier, domain extension, or finite bridge.'}


def certificate():
    negative=complex_mitm(8,{2:(0,0,1),5:(1,1,2)})
    positive=complex_mitm(9,{})
    assert negative['intersection_size']==0
    assert positive['intersection_size']>0
    return {'status':'No new supplier or kappa; scoped bit theorem and fixed-word complex exclusion.',
            'bit':pair_character_certificate(),'bit_extended':symmetric_profile_certificate(),'complex':negative,
            'complex_positive_control':positive,'uniform_replay_controls':checks(),
            'target_budgets':target_moments(),
            'external_scope_source':{'pr':288,'head':'475a088b5862f75f0b10596cfd6842d19531a5ec',
             'readme_sha256':'c091e98c415e2a80bb28402b789363eb97dd3492061ca8875e421ae437de7482',
             'status':'Written source inspected; its unbundled searches and general proofs not independently reproduced.'}}


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument('--write',action='store_true')
    args=ap.parse_args()
    out=certificate()
    dest=Path(__file__).with_name('certificate.json')
    if args.write:dest.write_text(json.dumps(out,indent=2)+'\n')
    else:assert json.loads(dest.read_text())==out,'certificate drift'
    print(json.dumps({k:v for k,v in out.items() if k not in ('bit','external_scope_source')},indent=2))
