#!/usr/bin/env python3
"""Exact source-normalizer and obstruction-escape checks for an unpaired reflection.
Apache-2.0; substantial OpenAI Codex assistance. No positive caller claimed.
"""
from pathlib import Path
import argparse,hashlib,json
from audit_marked_plane_bound import Q,ZERO,ONE,II,plus,neg,mul,conj,mm,scale
from chronology import need
HERE=Path(__file__).resolve().parent

def iphase(k):return(ONE,II,neg(ONE),neg(II))[k%4]
def dot(a,b):return(a&b).bit_count()%2
def apply(v,w):return w^(v if dot(v,w)else 0)
def degree(w,L):return sum((1 if j%2==0 else -1)*((w>>j)&1)for j in range(2*L))
def entry(i,j,L):
    phase=iphase(L+degree(j,L)-degree(i,L))
    return mul((Q(-1 if dot(i,j)else 1,1<<L),Q(0)),phase)
def tensor_entry(i,j,L,Hp,Hq):
    z=iphase(L)
    for k in range(2*L):z=mul(z,(Hp if k%2==0 else Hq)[(i>>k)&1][(j>>k)&1])
    return z

def run():
    a=(Q(1,2),Q(1,2));b=(Q(1,2),Q(-1,2));C=[[a,b],[b,a]];Ci=[[conj(x)for x in r]for r in C];Z=[[ONE,ZERO],[ZERO,neg(ONE)]];Hp=mm(Z,Ci);Hq=mm(Z,C)
    for L in(1,2,3):
        for i in range(1<<(2*L)):
            for j in range(1<<(2*L)):need(entry(i,j,L)==tensor_entry(i,j,L,Hp,Hq),'actual typed native equals exact D-Walsh-D formula')
    L=3;v=sum(1<<j for j in(0,1,2,4));dim=1<<(2*L)
    need(v.bit_count()%2==0 and degree(v,L)==2,'unpaired reflection has evenweight and typeddegree2')
    for i in range(dim):
        need(apply(v,apply(v,i))==i,'actual ADDRESS reflection involution')
        for j in range(dim):
            need(dot(apply(v,i),apply(v,j))==dot(i,j),'binary orthogonality')
            need(entry(apply(v,i),j,L)==entry(i,apply(v,j),L),'literal source normalizer commutes complete native E3')
        phase=(degree(i,L)-degree(apply(v,i),L))%4
        need(phase==0,'typed phase correction is exactly absent')
    original=1<<1;moved=apply(v,original)
    marked=lambda w:[j for j in range(L)if((w>>(2*j))&1)!=((w>>(2*j+1))&1)]
    need(marked(original)==[0]and marked(moved)==[0,1,2],'explicit actual X-character leakage from one marked plane to three')
    paired=(1<<4)-1
    need(any(entry(apply(paired,i),j,L)!=entry(i,apply(paired,j),L)for i in range(dim)for j in range(dim)),'plain paired reflection fails without its phase correction')
    paired_checks=0
    for w in range(dim):
        old=marked(w)
        if len(old)!=1:continue
        # R=Z_v P_A; in X characters this acts by w -> A w + v.
        transformed=apply(paired,w)^paired
        need(marked(transformed)==old,'proper paired reflection preserves one marked residual owner')
        owner=old[0];need(((w>>(2*owner))&1)==((transformed>>(2*owner))&1),'proper paired reflection commutes marked sign')
        paired_checks+=1
    return dict(status='PASS_INDEPENDENT_UNPAIRED_REFLECTION_RESOURCE',no_new_kappa=True,producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),helper_sha256=hashlib.sha256((HERE/'audit_marked_plane_bound.py').read_bytes()).hexdigest(),support_chunks=['p0','q0','p1','p2'],binary_vector=v,ambient_old_planes=3,physical_map='A=I+v v^T over F2, applied independently to each bit position of the four selected chunks.',native_cost=0,source_normalizer_identity='R E3=E3 R exactly, R^2=I, R=P_A with no hidden diagonal phase.',all_parameter_proof='For full old progress E_L=i^L D^-1 H_(2L) D, d(x)=sum_p x-sum_q x. Binary orthogonality makes P_A commute H. For A=I+vv^T, if v.x=1 the typed phase d(x)-d(Ax)=2-d(v) mod4. The chosen three-p/one-q vector has d(v)=2, so D^-1 P_A D=P_A. The identity tensorizes bitwise for every f. On the simultaneous X-character input q0=(1,...,1), all other chunks zero, A maps to p0=p1=p2=(1,...,1), all q zero: one marked residual becomes three, so the old invariant-subspace gate is inapplicable.',finite_checks={'native_formula_planes':[1,2,3],'normalizer_all_matrix_entries':dim*dim,'one_bit_dimension':dim,'paired_control_marked_states':paired_checks},escape_witness={'X_character_before':original,'X_character_after':moved,'marked_planes_before':[0],'marked_planes_after':[0,1,2]},limits=['This is an exact native-zero ADDRESS resource and a scope escape, not a cheaper complete supplier.','A real source insertion must charge its ADDRESS scans, preserve actual current-source access, and bind all output/readers and inverse cleanup.','No new kappa, complete caller, precision, ownership or BIT compatibility is supplied by this resource.'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();o=json.loads(json.dumps(run()));p=HERE/'INDEPENDENT-PARTIAL-REFLECTION.json'
    if a.write:p.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n')
    else:need(json.loads(p.read_bytes())==o,'saved reflection audit differs')
    print(o['status'],'allf proof; exact64x64commutation; markedspaceleak; no completecaller')
if __name__=='__main__':main()
