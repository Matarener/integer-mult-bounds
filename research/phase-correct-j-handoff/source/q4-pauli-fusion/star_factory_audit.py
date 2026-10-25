#!/usr/bin/env python3
"""Exact polar-rank audit of the declared changed-J monomial factories."""
from pathlib import Path
import argparse,hashlib,json
from even_parity_source_independent import binary_rank
HERE=Path(__file__).resolve().parent
def need(x,s):
 if not x:raise ValueError(s)
def compose(g,h):
 p,a=g;r,b=h;n=len(p);inv=[0]*n
 for i,j in enumerate(r):inv[j]=i
 c=list(b)
 for j,row in enumerate(a):
  for k in range(n):
   if row>>k&1:c[inv[j]]^=1<<inv[k]
 return tuple(p[r[i]] for i in range(n)),tuple(c)
def inverse(g):
 p,a=g;n=len(p);r=[0]*n
 for i,j in enumerate(p):r[j]=i
 z=[0]*n
 for j,row in enumerate(a):
  for k in range(n):
   if row>>k&1:z[p[j]]^=1<<p[k]
 return tuple(r),tuple(z)
def fixture(q):
 L=2*q+2;n=2*L;I=(tuple(range(n)),(0,)*n)
 def diag(planes):return tuple(1<<j if j//2 in planes else 0 for j in range(n))
 N=(I[0],diag({0}));E=(I[0],diag(set(range(L))));F=(I[0],diag(set(range(1,L))))
 a=[0]*n
 for j,k in ((0,2),(1,3)):a[j]^=1<<k;a[k]^=1<<j
 a[2]^=1<<2;a[3]^=1<<3
 A=(I[0],tuple(a));J=compose(N,A)
 def P(s):
  p=list(range(n))
  for j in range(2):p[j],p[2*s+j]=p[2*s+j],p[j]
  return tuple(p),(0,)*n
 even=I;star_checks=[]
 for s in range(4,2*q+1,2):
  even=compose(compose(P(s),A),even)
  star_checks.append(binary_rank(even[1]))
 Du=compose(even,compose(P(3),N));Dv=I
 for s in range(5,2*q+2,2):Dv=compose(compose(P(s),N),Dv)
 Xu=compose(F,Du);Xv=compose(F,Dv)
 cleanup=[compose(E,inverse(Xu)),compose(E,inverse(Xv))]
 targetFJ=compose(F,J);cleanupJ=[compose(targetFJ,inverse(Xu)),compose(targetFJ,inverse(Xv))]
 ranks=dict(even_star=binary_rank(even[1]),F_Du=binary_rank(Xu[1]),F_Dv=binary_rank(Xv[1]),
            to_E=[binary_rank(x[1]) for x in cleanup],to_FJ=[binary_rank(x[1]) for x in cleanupJ])
 need(all(x==4 for x in star_checks),'every nonempty distinct-leaf star has exactrank4')
 need(ranks['F_Du']==4*q and ranks['F_Dv']==2*q+4,'all declared complete factory source ranks')
 need(ranks['to_E']==[8,2*q],'direct independent E completion costs2q+8')
 need(compose(Du,inverse(Du))==I and compose(inverse(Dv),Dv)==I,'polar inverse bothorders')
 return dict(q=q,ranks_in_units_f=ranks,retired_h0_h1_sum=6*q+4,required_strictly_above=6*q+8,
             direct_to_E_mass=2*q+8,prefix_available_mass=2*q)
def run():
 cases=[fixture(q) for q in range(2,65)]
 return dict(status='PASS_EXACT_SCOPED_STAR_FACTORY_ARITY_AUDIT',no_new_kappa=True,cases=cases,
  factor_assumptions='A=N^-1J; D_even=product r2..q(P_2r A), Du=D_even P3N, Dv=+/-product r2..q(P_(2r+1)N), F=product freshNs overplanes1..2q+1. Products are chronological left multiplication. These are the declared factored endpoint assumptions, not a proved all-q physical caller.',
  all_q_star_proof='A is X-character diagonal with exact base phase1+2p0+p1+q1+2p0p1+2q0q1. Every P_s fixes anchor1. Its accumulated phase is a star between anchor p/q and two parity sums of distinct leaf p/q coordinates. Its polar image lies in their4-dimensional span; every nonempty distinct-leaf product has rank4. Tensoring gives4f.',
  all_q_full_endpoint_proof='For FDu the one-type polar has two zero rows(common0,last even2q), identity on all other leaf coordinates, anchor diagonalq mod2, andq-1 star edges. Its Schur complement isq-(q-1)=1, giving2q pertype and4q total. FDv is diagonal: itsq-1 old N leaves and last odd2q+1 cancel, leavingq+2 planes, total2q+4.',
  all_q_direct_cleanup_proof='For E(FDu)^-1, removing plane permutations leaves an isolated common0 diagonal direction, an isolated last-even2q diagonal direction, and the anchor/leaf star of rank2 per p/q type; total8. For E(FDv)^-1, the diagonal surviving support has theq-1 old leaves and last odd2q+1, exactlyq planes and rank2q. The saved exact grid checksq2..64. Complete Gaussian adapter recipes for these all-q corrections are not supplied here.',
  current_reader_identity='LetA_old=A_post+b_r, D=B_oJ=P_oN, andv_next=-D v+(B_o-J)A_post. Thenw=v+J A_old obeysw_next=v_next+J A_post=-D(w-Jb_r). The readerJb_r must be the actual completed field at that cut; replacingA_post byA_old gives a defect.',
  reverse_reader_invoice='There areq-1 reverse w updates: one final andq-2 nonfinal. Their declared unfused word w_prev=-D_o^-1 w_next+Jb_r uses one N^-1 P_o^-1 native2f query per update, with the actual completedJb_r reader. This is an invoice for that word, not a lower bound against joint correction/fusion.',
  scope='The star rank cap is exact allq under its displayed factor assumptions. The factor-first retired-helper sum6q+4 misses the required6q+8 gate by4. Direct separate unary completiontoE costs2q+8>prefix2q. This is not a lower bound for joint H/L correction, cross-cut sharing, arbitrary right codes or a different complete caller. No all-q physical current-reader trace or owner allocation is certified.',
  producer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
  source_pins=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [HERE/'even_parity_source_independent.py',HERE.parent/'caller/even_parity_caller.py',HERE.parent/'caller/EVEN-PARITY-CALLER.json',HERE.parent/'caller/EVEN-PARITY-CALLER.md']])
def main():
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();out=json.loads(json.dumps(run()));path=HERE/'STAR-FACTORY-AUDIT.json'
 if a.write:path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
 else:need(json.loads(path.read_text())==out,'saved starfactoryaudit differs')
 print(out['status'],'q2..64')
if __name__=='__main__':main()
