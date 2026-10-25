"""Exact small noncommuting-Q model for E-code adapters; no caller claim."""
from fractions import Fraction as F
from pathlib import Path
import json,argparse
class C:
 def __init__(self,a=0,b=0):self.a=F(a);self.b=F(b)
 def __add__(x,y):
  if not isinstance(y,C):y=C(y)
  return C(x.a+y.a,x.b+y.b)
 __radd__=__add__
 def __neg__(x):return C(-x.a,-x.b)
 def __sub__(x,y):return x+-cv(y)
 def __rsub__(x,y):return cv(y)+-x
 def __mul__(x,y):
  y=cv(y);return C(x.a*y.a-x.b*y.b,x.a*y.b+x.b*y.a)
 __rmul__=__mul__
 def __eq__(x,y):y=cv(y);return x.a==y.a and x.b==y.b
 def __bool__(x):return bool(x.a or x.b)
def cv(x):return x if isinstance(x,C)else C(x)
def zeros(n):return [[C()for j in range(n)]for i in range(n)]
def ident(n):return [[C(i==j)for j in range(n)]for i in range(n)]
def add(A,B):return [[a+b for a,b in zip(x,y)]for x,y in zip(A,B)]
def scale(a,A):return [[a*x for x in row]for row in A]
def mul(A,B):
 n=len(A);O=zeros(n)
 for i in range(n):
  for k in range(n):
   if A[i][k]:
    for j in range(n):
     if B[k][j]:O[i][j]=O[i][j]+A[i][k]*B[k][j]
 return O
def prod(*As):
 out=ident(len(As[0]))
 for A in As:out=mul(out,A)
 return out
def block(A,B,Cc,D):return [a+b for a,b in zip(A,B)]+[a+b for a,b in zip(Cc,D)]
def diag(A,B):return block(A,zeros(len(A)),zeros(len(A)),B)
def lower(A):return block(ident(len(A)),zeros(len(A)),A,ident(len(A)))
def upper(A):return block(ident(len(A)),A,zeros(len(A)),ident(len(A)))
def need(a,b,why):
 if a!=b:raise ValueError(why)
def calc():
 # Two owner ports and two address axes; q0=e0, q1=e1, Kscalar=swap.
 # L0=I,L1=address-swap; conjugation makes K blocks equal to P_swap.
 N=4;I=ident(N);P=zeros(N)
 for x in range(N):P[((x&1)<<1)|((x>>1)&1)][x]=C(1)
 def gate(q,s):
  O=scale(C(F(1,2),F(s,2)),I)
  for x in range(N):O[x^q][x]+=C(F(1,2),F(-s,2))
  return O
 Q0=gate(1,1);Qi0=gate(1,-1);D0=gate(2,1);Di0=gate(2,-1)
 Q=diag(Q0,Q0);Qi=diag(Qi0,Qi0);D=diag(D0,D0);Di=diag(Di0,Di0);I=ident(8);Z=zeros(8)
 K=block(zeros(4),P,P,zeros(4));R=mul(D,Q)
 need(mul(K,K),I,'actual K involution');need(mul(K,R),mul(R,K),'actual fullGaussian centralization')
 if mul(K,Q)==mul(Q,K):raise ValueError('noncommuting-Q control lost')
 # FC=lambda*Pminus; active B=I-K=2Pminus, BC=2C.
 Pminus=scale(F(1,2),add(I,scale(-1,K)));out=[]
 FK=mul(diag(D,D),lower(mul(K,Qi)));BK=mul(diag(D,D),upper(scale(-1,mul(Q,K))))
 F0=mul(diag(D,D),lower(Qi));B0=mul(diag(D,D),upper(scale(-1,Q)))
 for lam in [14,98,-1078]:
  FC=scale(lam,Pminus);A=add(I,scale(-1,FC));Ai=add(I,scale(F(lam,1-lam),Pminus))
  need(mul(A,Ai),I,'inverse A exact')
  for name,X,Xinv,residual in [('KA',A,Ai,Ai),('K_Ainverse',Ai,A,A)]:
   E=mul(K,X);Ei=mul(K,Xinv);H=diag(E,prod(Qi,E,Q));Hi=diag(Ei,prod(Qi,Ei,Q));Delta=add(I,scale(-1,residual))
   leftF=prod(diag(E,I),FK,diag(I,E));leftB=prod(diag(Ei,I),BK,diag(I,Ei))
   rightF=prod(H,diag(D,D),lower(mul(residual,Qi)));rightB=prod(Hi,diag(D,D),upper(scale(-1,mul(Q,residual))))
   need(leftF,rightF,'forward E exact adapter');need(leftB,rightB,'backward E inverse exact adapter')
   need(mul(leftF,lower(mul(Delta,Qi))),mul(H,F0),'forward lowrank defect correction')
   need(mul(leftB,upper(scale(-1,mul(Q,Delta)))),mul(Hi,B0),'backward lowrank defect correction')
   # Physical post-native backward correction uses original ground Y only:
   # add -R Delta Y to native X before postX(E^-1).
   scatter=block(Z,scale(-1,mul(Ei,mul(R,Delta))),Z,Z)
   WB=add(leftB,scatter)
   need(WB,mul(Hi,B0),'physical original-ground backward correction')
   if name=='K_Ainverse':
    # Inverse scheduling: source Y native inverse first, with its contact
    # checkpoint retained, then undo correction and finish native X inverse.
    # At matrix level y=E D^-1 Yout is acquired before X's native inverse.
    # The literal K schedule must retain its Y common-frame contact via COPY.
    BKi=mul(upper(mul(Q,K)),diag(Di,Di))
    y_acquire=mul(E,Di)
    undo=block(I,mul(R,mul(FC,y_acquire)),Z,I)
    WBi=prod(diag(I,E),BKi,undo,diag(E,I))
    need(mul(WBi,WB),ident(16),'checkpoint-scheduled physical inverse left')
    need(mul(WB,WBi),ident(16),'checkpoint-scheduled physical inverse right')
    # Transpose the obtained inverse linear algorithm; C^T=C, its inverse
    # is positive C then ordinary X. The boundary is entirely monomial.
    transpose=lambda M:list(map(list,zip(*M)))
    Q2=mul(Q,Q);D2=mul(D,D);J=diag(Q2,I);Jinv=J
    WF=prod(diag(D2,D2),J,transpose(WBi),Jinv)
    need(WF,mul(H,F0),'actual symmetric E duality produces forward code')
   # Omission produces an actual nonzero physical defect, not just syntax.
   if leftF==mul(H,F0)or leftB==mul(Hi,B0):raise ValueError('omitted correction mutation accepted')
   # Q must be in the displayed order: it cannot commute through Delta.
   if mul(Delta,Q)==mul(Q,Delta):raise ValueError('noncommutative defect control lost')
   out.append({'lambda':lam,'E':name,'forward_backward_adapters':True,'corrected_forward_backward':True,'omitted_correction_rejected':True,'Delta_Q_noncommuting':True,'physical_ground_backward_correction':True,'inverse_and_transpose_boundary_checked':name=='K_Ainverse'})
 return {'schema':'source-consuming-E-exact-small-model/v1','status':'PASS_EXACT_LOCAL_IDENTITIES_ONLY','address_axes':2,'owners':2,'complex_rational_main_matrix_dimension':16,'cases':out,'generic_identity':'For X commuting K with E=KX, [E,DQ]=0: postX(E) F_K preY(E)=H(E) diag(D,D) L(X^-1 Q^-1); postX(E^-1) B_K preY(E^-1)=H(E^-1) diag(D,D) U(-Q X^-1).','correction':'Delta=I-X^-1; right-prepend L(Delta Q^-1) or U(-Q Delta) to recover scalar core with codes E/E^-1. For X=A^-1, Delta=F_C exactly, with rank rank(F_C).','remaining':'Literal all-port owned checkpoint/reverse-transpose emitter and ordinary tariff; actual IDLE/boundary endpoints; full negative terminal E-word decoding; complete precision and moment. The inverse source-Y checkpoint schedule is verified here as exact block algebra, not yet a literal owned program.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');a=p.parse_args();r=calc();f=Path(__file__).with_name('E-ADAPTER.json')
 if a.write:f.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
 else:need(r,json.loads(f.read_bytes()),'readonly receipt')
 print(json.dumps(r,sort_keys=True))
