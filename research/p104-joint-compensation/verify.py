#!/usr/bin/env python3
"""Exact fixed-owner joint compensator and scoped cost gate. Apache-2.0."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok, message):
    if not ok: raise ValueError(message)

def read(path):
    def unique(pairs):
        d={}
        for k,v in pairs:
            need(k not in d,'duplicate JSON key');d[k]=v
        return d
    return json.loads(path.read_text(),object_pairs_hook=unique)

def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'

def authenticate():
    for r in read(HERE/'SOURCES.json')['files']:
        if r['usage']!='input': continue
        p=ROOT/r['path'];need(not p.is_symlink(),'source symlink')
        b=p.read_bytes();need(hashlib.sha256(b).hexdigest()==r['sha256'],'source hash '+r['path'])
        need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['git_blob'],'source blob')

# Free associative algebra in A,B,T,K, with only TK=KT=1.
# A and B are deliberately NOT commuted in these identities.
def poly(letter=None): return {(() if letter is None else (letter,)):1}
def plus(*args):
    out=Counter()
    for p in args:
        for w,c in p.items():out[w]+=c
    return {w:c for w,c in out.items() if c}
def neg(p):return {w:-c for w,c in p.items()}
def times(p,q):
    out=Counter()
    for w,c in p.items():
        for v,d in q.items():
            stack=[]
            for z in w+v:
                if stack and (stack[-1],z) in [('T','K'),('K','T')]:stack.pop()
                else:stack.append(z)
            out[tuple(stack)]+=c*d
    return {w:c for w,c in out.items() if c}
def mm(a,b):return [[plus(*(times(a[i][k],b[k][j]) for k in range(2))) for j in range(2)] for i in range(2)]
def upper(x):return [[poly(),x],[{},poly()]]
def lower(x):return [[poly(),{}],[x,poly()]]

def algebra():
    I,A,B,T,K=[poly(x) for x in (None,'A','B','T','K')]
    J=[[{},neg(I)],[I,{}]]
    M=mm(upper(neg(B)),lower(A))
    C=[[A,plus(times(A,B),neg(I))],[I,B]]
    need(mm(C,M)==J,'joint endpoint')
    factors=[upper(plus(A,neg(I))),lower(I),upper(plus(B,neg(I)))]
    need(mm(mm(*factors[:2]),factors[2])==C,'three shear factorization')
    G=[[I,{}],[{},K]];Gi=[[I,{}],[{},T]]
    CP=mm(mm(G,C),Gi)
    expected=[[A,times(plus(times(A,B),neg(I)),T)],[K,times(times(K,B),T)]]
    need(CP==expected,'ordered physical conjugation')
    pf=[upper(times(plus(A,neg(I)),T)),lower(K),upper(times(plus(B,neg(I)),T))]
    need(mm(mm(*pf[:2]),pf[2])==CP,'physical factorization')
    need(mm(C,M)!=M,'omitted correction control')
    wrong=upper(times(T,plus(B,neg(I))))
    need(mm(mm(pf[0],pf[1]),wrong)!=CP,'wrong T order control')
    need(mm(pf[0],pf[2])!=CP,'missing middle shear control')
    # All <=2 layer orientations retain at least one identity diagonal block.
    for a,b in itertools.product((upper(A),lower(A)),(upper(B),lower(B))):
        z=mm(a,b);need(z[0][0]==I or z[1][1]==I,'two layer invariant')
    need(C[0][0]!=I and C[1][1]!=I,'nonidentity compensator diagonals')
    return 3

def roots_and_gram():
    roots=set()
    for i,j in itertools.combinations(range(8),2):
        for s in (-1,1):
            r=[0]*8;r[i]=2;r[j]=2*s;roots.add(tuple(r))
    for s in itertools.product((-1,1),repeat=7):
        if s.count(-1)%2==0:roots.add((1,)+s)
    f=read(ROOT/'research/p104-native-channel/inputs/P104-FIXTURE.json')['section4_explicit_P104']
    removed={tuple(x) for x in f['F0']+f['C']}
    ports=sorted(roots-removed);need(len(ports)==104,'P104 count')
    G=[[sum(x*y for x,y in zip(a,b))//4 for b in ports] for a in ports]
    need(all(G[i][i]==2 for i in range(104)),'diagonal')
    need(all(sum(G[i][k]*G[k][j] for k in range(104))==26*G[i][j] for i in range(104) for j in range(104)),'A squared = 13A')
    need(sum(G[i][i] for i in range(104))==208,'trace')
    off=sum(bool(G[i][j]) for i in range(104) for j in range(104) if i!=j)
    need(off==4992 and all(G[i][j] in (-1,0,1) for i in range(104) for j in range(104) if i!=j),'half support')
    # The three-layer word is linear; check each local donor column exactly.
    for j in range(104):
        updates=[(i,G[i][j]) for i in range(104) if i!=j and G[i][j]]
        got=[0]*104
        for i,c in updates:got[i]+=c
        need(got==[G[i][j]-2*(i==j) for i in range(104)],'donor half/add word')
    sectors=[]
    for a,ma in ((0,96),(13,8)):
        for b,mb in ((0,96),(13,8)):
            det=(a-1)*(b-1)-(a*b-1)
            need(det==2-a-b and det!=0,'no fixed spectral sector')
            sectors.append({'a':a,'b':b,'multiplicity':ma*mb,'det_C_minus_I':det})
    return off,sectors

def run():
    authenticate();layers=algebra();off,sectors=roots_and_gram()
    w=read(ROOT/'research/p104-native-channel/inputs/LOWRANK-WITNESS.json')
    hist=Counter(e[4] for e in w['program'] if e[0]=='transport')
    mass=sum(k*v for k,v in hist.items());need(mass==2368,'bare mass')
    progress=sum(len(w['final_frames'][r])-len(fr) for r,fr in w['initial_frames'].items())
    need(progress==2312,'persistent progress')
    n=104;N=n*n;W=2*N+2*n*72;m=81
    residual=m*W-N-2*n*progress
    bare_bill=2*n*mass+residual
    return {'schema_version':1,'status':'scoped_conditional_rejection','n':n,'N':N,'m':m,'W':W,
      'gram_rank':8,'gram_eigenvalues':[0,13],'sectors':sectors,'rank_C_minus_I':2*N,
      'minimum_fixed_owner_shear_layers':layers,'native_channel_mass':mass,'persistent_progress_cap':progress,
      'joint_route':{'positive_rank_one_copy_transforms':3*N,'unit_array_adds':2*n*off+N,
        'private_donor_halves':2*N,'private_initializations':3*N,'private_copies':3*N,'private_erasures':3*N,
        'peak_additional_private_arrays':1,'persistent_helper_changes':0},
      'gate':{'remaining_progress_lower_mass':residual,'capacity':m*W,'bare_lower_mass':bare_bill,
        'free_joint_repair_excess':bare_bill-m*W,'constructed_joint_lower_mass':bare_bill+3*N,
        'constructed_joint_excess':bare_bill+3*N-m*W},
      'frontier_changed':False,'native_complete_caller_constructed':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();got=run()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(got,indent=2)+'\n')
    else:need(canon(read(HERE/'RESULT.json'))==canon(got),'receipt mismatch including types')
    print('PASS joint compensation: exact noncommutative identities, all donor columns, scoped gate')
if __name__=='__main__':main()
