#!/usr/bin/env python3
"""Independent exact small factors and symbolic counts for a marked-plane cut.
Apache-2.0; substantial OpenAI Codex assistance. Restricted grammar only.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,itertools
from chronology import need
HERE=Path(__file__).resolve().parent
ZERO=(Q(0),Q(0));ONE=(Q(1),Q(0));II=(Q(0),Q(1))
def plus(a,b):return(a[0]+b[0],a[1]+b[1])
def neg(a):return(-a[0],-a[1])
def mul(a,b):return(a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def conj(a):return(a[0],-a[1])
def scale(c,M):return[[mul(c,x)for x in row]for row in M]
def mm(A,B):
    out=[]
    for row in A:
        r=[]
        for col in zip(*B):
            x=ZERO
            for a,b in zip(row,col):x=plus(x,mul(a,b))
            r.append(x)
        out.append(r)
    return out

def run():
    I=[[ONE,ZERO],[ZERO,ONE]];X=[[ZERO,ONE],[ONE,ZERO]];Z=[[ONE,ZERO],[ZERO,neg(ONE)]]
    a=(Q(1,2),Q(1,2));b=(Q(1,2),Q(-1,2));C=[[a,b],[b,a]];Ci=[[conj(x)for x in row]for row in C]
    Hp=mm(Z,Ci);Hq=mm(Z,C)
    need(mm(C,X)==mm(X,C),'chirp commutes every X translation on this bit')
    need(mm(Hp,Hp)==scale(neg(II),I)and mm(Hq,Hq)==scale(II,I),'exact one-bit square phases')
    need(mm(Hp,X)==scale(neg(ONE),mm(X,Hp))and mm(Hq,X)==scale(neg(ONE),mm(X,Hq)),'each typed factor anticommutes X')
    need(mm(C,Ci)==I,'exact Gaussian-dyadic chirp inverse')
    # All-f scalar proof: N_f=i Hp^tensorf Hq^tensorf has square
    # -(-i)^f i^f=-1 and complements every simultaneous X character.
    gauge_checks=[]
    for f in range(1,6):
        for word in range(1<<(2*f)):
            x=word&((1<<f)-1);y=word>>f;op=(1-x.bit_count()+y.bit_count())%4
            comp=((1<<(2*f))-1)^word;xx=comp&((1<<f)-1);yy=comp>>f;ip=(1-xx.bit_count()+yy.bit_count())%4
            need((op+ip)%4==2,'character pair square is -1')
            virtual=word&1;residual=tuple(((word>>j)&1)^virtual for j in range(1,2*f))
            cv=comp&1;cr=tuple(((comp>>j)&1)^cv for j in range(1,2*f))
            need(residual==cr and virtual!=cv,'native flips virtual bit and preserves residual label')
            if virtual==0:
                # v1=i^(op-1) e_complement makes N v0=i v1 and N v1=i v0.
                need(((op-1)+ip)%4==1,'same orbit gauge produces iX on reverse edge')
        gauge_checks.append({'f':f,'all_characters':1<<(2*f),'residual_dimension':1<<(2*f-1)})
    cut_checks=[]
    for L in range(1,9):
        dimension=L*(1<<L)
        for support in range(1<<L):
            # The commutator has a nonzero monomial column precisely when
            # its marked owner belongs to this native support.
            rank=sum(1 for owner in range(L)for x in range(1<<L)if ((x>>owner)&1)!=(((x^support)>>owner)&1))
            need(rank==support.bit_count()*(1<<L),'exact native cut rank')
        # Adjacent whole-plane permutations suffice to generate all permutations.
        for i in range(L-1):
            for owner in range(L):
                moved_owner=i+1 if owner==i else i if owner==i+1 else owner
                for x in range(1<<L):
                    moved=x
                    if((x>>i)&1)!=((x>>(i+1))&1):moved^=(1<<i)|(1<<(i+1))
                    need(((x>>owner)&1)==((moved>>moved_owner)&1),'literal ADDRESS preserves marked cut')
        cut_checks.append({'planes':L,'dimension':dimension,'all_native_supports':1<<L,'full_native_cut_rank':dimension})
    vendor=Path('/Users/ross/git/math/integer-mult-bounds/research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py')
    return dict(status='PASS_INDEPENDENT_MARKED_PLANE_CUT_AUDIT',no_new_kappa=True,producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),source_chirp_formula={'path':str(vendor),'sha256':hashlib.sha256(vendor.read_bytes()).hexdigest(),'binding':'The pinned C branch implements C=(1+i)I/2+(1-i)X/2 exactly; Hp=Z C^-1,Hq=Z C.'},character_checks=gauge_checks,cut_checks=cut_checks,all_parameter_proof='The one-bit identities tensor to N_f^2=-I and complement every simultaneous X character. Pairing complementary characters and using the same Gaussian-unit gauge on every plane gives virtual iX and unchanged residual label. Choose two residual labels; retain the actual invariant subspace with exactly one marked residual. On its L*2^L basis states, C=(-1)^virtual_bit_at_owner. Whole-plane permutations move owner and bits together, and all X translations are diagonal, so every declared free bridge commutes C. A native product on r planes flips the marked bit on exactly r*2^L states, hence commutator rank r*2^L. Rank[C,AB]<=rank[C,A]+rank[C,B] then forces sum r>=nL for n full-native output banks and any restored dirty banks. Multiplying by2f gives rankmass>=n*(2Lf).',scope='Actual normalized N_f plane products, arbitrary Gaussian scalar bank operations, whole-plane ADDRESS permutations and X translations; inverses and free conjugates included. No claim for free Pauli Z, general bit-linear ADDRESS, arbitrary native adapters, changed endpoint targets or partial-progress contracts.',limits=['The general proof is written and the listed finite checks are exact; this is not formal-kernel evidence.','A supplier using additional phase or coordinate operations lies outside the obstruction.'])

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();o=json.loads(json.dumps(run()));f=HERE/'INDEPENDENT-MARKED-PLANE-BOUND.json'
    if a.write:f.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(f.read_bytes())==o,'saved cut audit differs')
    print(o['status'],'character f1..5; all supports L1..8; written all-f/all-L proof')
if __name__=='__main__':main()
