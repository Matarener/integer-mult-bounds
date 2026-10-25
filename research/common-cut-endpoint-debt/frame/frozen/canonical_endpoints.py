#!/usr/bin/env python3
"""Exact global native endpoint ranks for the canonical OPEN relay.

Local phases are preserved by literal circuits; global rank is tableau-only.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
import argparse
from hashlib import sha256
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent
P=Path('/Users/ross/git/math');R=HERE.parent;CP=P/'integer-mult-bounds/research/kernel92-frame-composition/vendor/pr531/vendor/clifford/clifford_exact.py'
s=importlib.util.spec_from_file_location('ep_native',CP);ce=importlib.util.module_from_spec(s);sys.modules[s.name]=ce;s.loader.exec_module(ce)
bus=json.loads((HERE/'SOURCE-D4-BUS-INPUT.json').read_text());win=json.loads((HERE/'SOURCE-COMMON-FRAME-INVERSE-SEARCH.json').read_text());winner={r['p']:r for r in win['rows']}

def build(n,ev):
 o=ce.ident(n)
 for e in ev:
  if e[0]=='C':v=ce.cgate(n,e[1],e[2])
  elif e[0]=='P':v=ce.perm(n,e[1])
  elif e[0]=='D':v=ce.diag(n,e[1],e[2])
  elif e[0]=='X':v=ce.xgate(n,e[1])
  elif e[0]=='phase':v=ce.Op(n,ce.identity(n),[tuple(e)])
  else:raise ValueError(e)
  o=o.then(v)
 return o

def completion(p,q):
 cols=[p,q]
 while len(cols)<7:
  char=127
  for v in cols:char^=v
  v=next(v for v in range(1,128)if v.bit_count()%2 and all((v&w).bit_count()%2==0 for w in cols)and(7-len(cols)==1 or v!=char))
  cols.append(v)
 need(all(((v&w).bit_count()%2)==int(i==j)for i,v in enumerate(cols)for j,w in enumerate(cols)),'orthogonal chart completion')
 return cols

def embed(n,ev,axes):
 def v7(v):return sum(((v>>j)&1)<<axes[j]for j in range(7))
 out=[]
 for e in ev:
  if e[0]in('C','X'):out.append((e[0],v7(e[1]),*e[2:]))
  elif e[0]=='phase':out.append(e)
  elif e[0]=='P':
   rows=[1<<j for j in range(n)]
   for i in range(7):rows[axes[i]]=v7(e[1][i])
   out.append(('P',rows))
  elif e[0]=='D':
   rows=[0]*n;alpha=[0]*n
   for i in range(7):rows[axes[i]]=v7(e[1][i]);alpha[axes[i]]=e[2][i]
   out.append(('D',rows,alpha))
  else:raise ValueError(e)
 return build(n,out)

def rank(o):return ce.rank([x for x,z,p in o.tab[o.n:]])

def need(b,m):
 if not b:raise ValueError(m)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');arg=ap.parse_args()
 need(sha256(CP.read_bytes()).hexdigest()=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','compiler pin')
 records=[]
 for g in range(3):
  for j,p in enumerate(bus['groups7'][g]):
   q=bus['groups7'][(g+1)%3][j];r=bus['groups7'][(g+2)%3][j];cols=completion(p,q);G=ce.perm(7,ce.transpose(cols,7))
   if g==2:pre=build(7,winner[p]['pre_events'])
   else:
    u=q^r;rows=[(1<<i)^(u if u>>i&1 else 0)for i in range(7)];pre=ce.perm(7,rows)
   canon=G.then(pre).then(G.adjoint());mon,rec=ce.monomial(canon);gi=ce.inv(rec['matrix_rows'],7)
   corner=[x&3 for x in gi[:2]];cr=ce.rank(corner)
   need(cr==(0 if g==2 else 1),'inverse-pre common principal rank')
   Cp0,Cq0=ce.cgate(7,p),ce.cgate(7,q);M0=Cp0.then(Cq0.adjoint())
   if g==2:
    core=[v[0]for v in bus['groups7']];coords=ce.inv(ce.transpose(core+[5,53,30,96],7),7);Pc=ce.perm(7,coords)
    D=Pc.then(ce.hadamard(7,[3,4])).then(Pc.adjoint()).then(ce.Op(7,ce.identity(7),[('phase',3)]))
    VC=D.then(ce.cgate(7,core[0])).then(ce.cgate(7,core[1]));S=Cp0.adjoint().then(VC)
   else:S=Cp0.adjoint().then(ce.cgate(7,r).adjoint()).then(ce.fourier(7).then(ce.xgate(7,33)))
   sm=M0.then(S);sr,slit=ce.lower_child(sm)
   need(sm.tab==slit.tab and sm.zero_state()==slit.zero_state(),'local S M completephase')
   need(sr['rank']==(3 if g==2 else 5),'local corner invariant rank')
   cases=[]
   for L in(1,3,5,7,9):
    n=2+5*L;total=ce.ident(n)
    for st in range(L):total=total.then(embed(n,mon.circuit,[0,1]+list(range(2+5*st,7+5*st))).adjoint())
    Cp,Cq=ce.cgate(n,1),ce.cgate(n,2);F=ce.fourier(n);Gall=Cp.adjoint().then(Cq.adjoint()).then(F)
    E=Cp.then(total).then(Cp.adjoint())
    ox=Cp.adjoint().then(E).then(Gall).then(Cq);oy=Cq.adjoint().then(E).then(Gall).then(Cp)
    rx,ry=rank(ox),rank(oy)
    need(rx==n and ry==n-4+2*cr,'exact native endpoint ranks')
    cases.append({'L':L,'m':n,'X_rank':rx,'Y_rank':ry,'Y_deficit':n-ry})
   records.append({'group':g,'coordinate':j,'p':p,'q':q,'orthogonal_chart_columns':cols,'canonical_pre_monomial':rec,'inverse_pre_common_corner_rows':corner,'inverse_pre_common_corner_rank':cr,'local_source_times_commonM_native':sr,'cases':cases})
 out={'status':'PASS_CANONICAL_RELAY_GLOBAL_ENDPOINT_RANKS','scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
      'sources':{f:sha256((HERE/f).read_bytes()).hexdigest()for f in('SOURCE-COMMON-FRAME-INVERSE-SEARCH.json','SOURCE-D4-BUS-INPUT.json')},'compiler_sha256':sha256(CP.read_bytes()).hexdigest(),'records':records,
      'chart_caution':'Common axes p,q map to canonical e1,e2. The third odd orbit root is the characteristic=sum of all5 fresh orthonormal coordinates, not a single fresh coordinate.',
      'actual_relay':'F(A): y+=A x; B(A^-1): x-=A^-1 y. SAME pre-X A^-1/post-Y A^-1 gives common increment A^-1 for either orientation. No involution premise. Idle synchronization must use legal future-X/past-Y products and actual owner windows.',
      'global_endpoint':'E=Cp^-1 Ptotal Cp, Ptotal=pre_(L-1)^-1...pre_0^-1. After literal terminal X/Y exchange the isolated X operator is F_global Xp Ptotal, full native rankm. Isolated Y is F_fresh Ptotal (Cp Cq^-1), up rankzero positive-gauge Paulis.',
      'written_rank_proof':'An actual monomial P preserving both ZERO and FULL has symplectic blocks [[G,0],[G+G^-T,G^-T]]. Multiplying F_fresh P M_common with M_common=Cp Cq^-1 gives Bruhat Bblock diag(G_CC,(G^-T)_FF). Complementary principal nullity gives rankB=m-4+2rank(G_CC). Distinct fresh stage supports imply the common corner of Ptotal is the product of the common corners of inverse(pre_s). All four C inverse-pre corners arezero, A/B corners have rank1. This proves C deficit4, A/B deficit at least2 within this disjoint common-code grammar, for arbitrary L; the finite chosen A/B charts attain exactly2.',
      'phase_scope':'Every local source pre is reconstructed as a phase-bearing exact Clifford circuit, orthogonal chart conjugated and monomialized with full tableau+Gaussian phase. Global m17..47 endpoint ranks use exact symplectic tableaus and are invariant under global phase. No global phase lowering, formal kernel or complete native supplier caller is claimed.',
      'all_size_scope':'The written symplectic/nullity proof is all-parameter within its stated fixed common-code/disjoint-fresh model. On f tensor columns the native rank cost multiplies byf. No finite ADD expansion is used.',
      'remaining':['Changed noncommon bank codes, overlapping stage support, retained helper lineages or different chronological supplier words are outside the rank proof.','Positive-rank Y endpoint corrections require actual paid native words, owner capacities and full moments.','No favorable exponent or positive kappa is established.'],
      'attribution':'Complex lane supplies common-F inverse-B winners and full local phase checks. Root derives the general principal-block argument. This lane constructs actual orthogonal common2/fresh5 charts, independently verifies all12 global endpoints and identifies the necessary inverse-pre convention; complex independently reviews complementary nullity.'}
 out=json.loads(json.dumps(out));dest=HERE/'CANONICAL-ENDPOINTS.json'
 if arg.write:dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(dest.read_bytes())==out,'stored canonical endpoint record differs')
 print(out['status']);print('12ports, L1/3/5/7/9: Xfull; Y A/B deficit2,C deficit4')
if __name__=='__main__':main()
