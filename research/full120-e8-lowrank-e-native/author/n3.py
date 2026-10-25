"""Three distinct fresh stages: literal owned typed E caller and positive exit."""
import argparse,hashlib,importlib.util,json,sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('n3_owned',HERE/'owned_e.py');oe=importlib.util.module_from_spec(spec);sys.modules[spec.name]=oe;spec.loader.exec_module(oe)
C=oe.C;N=16;W=64;MAIN=oe.MAIN

def need(q,s):
 if not q:raise ValueError(s)
def eye(n):return [[C(i==j)for j in range(n)]for i in range(n)]
def zeros(n,m=None):return [[C()for j in range(n if m is None else m)]for i in range(n)]
def plus(A,B):return [[a+b for a,b in zip(r,s)]for r,s in zip(A,B)]
def times(c,A):return [[c*x for x in r]for r in A]
def left(A,B):
 out=zeros(len(A),len(B[0]))
 for i,r in enumerate(A):
  for k,c in enumerate(r):
   if c:
    for j,x in enumerate(B[k]):
     if x:out[i][j]+=c*x
 return out
def prod(*As):
 r=eye(len(As[0]))
 for A in As:r=left(r,A)
 return r
def block(A,B,D,E):return [a+b for a,b in zip(A,B)]+[a+b for a,b in zip(D,E)]
def diag(A,B):return block(A,zeros(len(A)),zeros(len(A)),B)
def perm(fun):
 A=zeros(N)
 for x in range(N):A[fun(x)][x]=C(1)
 return A
def X(q):return perm(lambda x:x^q)
def gate(q,sgn=1):return plus(times(C(F(1,2),F(sgn,2)),eye(N)),times(C(F(1,2),F(-sgn,2)),X(q)))
def swap(x,s):
 b0=x&1;bs=(x>>s)&1
 return x^((1|(1<<s))if b0!=bs else 0)
MAP={}
for s in [1,2,3]:
 MAP[f'P{s}']=perm(lambda x,s=s:swap(x,s));MAP[f'C0{s}']=gate(1);MAP[f'C1{s}']=gate(1<<s);MAP[f'R{s}']=left(gate(1),gate(1<<s));MAP[f'I{s}']=eye(N)
 for q in [1,2,3]:MAP[f'X{q}_{s}']=X((q&1)|((q>>1)<<s))
def mapped(program,s,prefix):
 out=[]
 def f(x):return x if x in MAIN else prefix+x
 for e in program:
  e=list(e);k=e[0]
  if k in ['COPY','ADD']:e[1]=f(e[1]);e[2]=f(e[2])
  else:e[1]=f(e[1])
  if k in ['MONO','PAID']:
   m=e[2];e[2]=(f'X{m[1:]}_{s}'if m.startswith('X')else m+str(s))
  elif k=='ADD':e[5]=e[5]+str(s)
  out.append(e)
 return out

def run(program):
 vals={f:[[C(4*N==0)for k in range(W)]for i in range(N)]for f in MAIN}
 for j,f in enumerate(MAIN):vals[f]=[[C(j*N+i==k)for k in range(W)]for i in range(N)]
 live=set(MAIN);peak=0;paid=Counter();ordinary=Counter()
 for e in program:
  k=e[0]
  if k=='PAID':paid[e[3]]+=1
  else:ordinary[k]+=1
  if k in ['COPY','OWN_ZERO']:
   need(e[1]not in live and e[1]not in MAIN,'owned new/clean')
   vals[e[1]]=[list(r)for r in vals[e[2]]]if k=='COPY'else zeros(N,W);live.add(e[1]);peak=max(peak,len(live)-4)
  elif k=='CLEAR':need(e[1]in live and e[1]not in MAIN,'owned clear');vals[e[1]]=zeros(N,W);live.remove(e[1])
  elif k=='SCALE':need(e[1]in live,'scale live');vals[e[1]]=times(F(e[2],e[3]),vals[e[1]])
  elif k=='ADD':need(e[1]in live and e[2]in live,'source live');vals[e[1]]=plus(vals[e[1]],times(F(e[3],e[4]),left(MAP[e[5]],vals[e[2]])))
  elif k=='SWAP':vals[e[1]],vals[e[2]]=vals[e[2]],vals[e[1]]
  else:need(k in ['MONO','PAID']and e[1]in live,'known unary');vals[e[1]]=left(MAP[e[2]],vals[e[1]])
 need(live==set(MAIN),'clean final owned state')
 return sum([vals[f]for f in MAIN],[]),{'paid':dict(paid),'ordinary':dict(ordinary),'peak_owned_fields':peak}
def calculate():
 lam=F(225,2);program=[]
 for s,which in [(1,3),(2,0),(3,3)]:program+=mapped(oe.programs(lam)[which],s,f's{s}_')
 program.extend([['SWAP','X0','Y0'],['SWAP','X1','Y1'],['SCALE','Y0',-1,1],['SCALE','Y1',-1,1]])
 # Postdecode positive half by E3^-1, E2, E1^-1, in that chronology.
 a=F(lam,2);b=1-a;ia=F(lam,2*(lam-1));ib=F(lam-2,2*(lam-1))
 for s,c,d in [(3,a,b),(2,ia,ib),(1,a,b)]:program+=mapped(oe.coded(['Y0','Y1'],c,d,'exit'),s,f'exit{s}_')
 actual,invoice=run(program);Z=zeros(N);I=eye(2*N);Q=diag(gate(1),gate(1));Qi=diag(gate(1,-1),gate(1,-1));Ds=[diag(gate(1<<s),gate(1<<s))for s in [1,2,3]]
 Es=[];Eis=[]
 for s in [1,2,3]:
  K=block(Z,MAP[f'P{s}'],MAP[f'P{s}'],Z);Es.append(plus(times(ia,I),times(ib,K)));Eis.append(plus(times(a,I),times(b,K)))
 B=prod(Es[2],Eis[1],Es[0]);D=prod(*Ds);neg=prod(Qi,B,D);pos=prod(D,Q);target=diag(neg,pos)
 need(actual==target,'all64 arbitrary original main columns, threefreshstage typed endpoint and positiveGaussian')
 need(invoice['paid']=={1:12,2:3},'three same paid module profiles, noIDLE or thin query')
 naive=left(prod(Eis[0],Es[1],Eis[2]),neg)
 need(naive!=prod(Qi,D),'negative B^-1 decoder must not be treated as Gaussian')
 need(left(Q,B)!=left(B,Q),'three-stage code really fails commutation control')
 result={'schema':'N3-owned-E-typed-caller/v1','status':'PASS_THREE_FRESH_STAGE_TYPED_E_CALLER_WITH_ONE_GAUSSIAN_HALF','lambda':str(lam),'ambient_axes':4,'arbitrary_main_fields':4,'complete_main_matrix_dimension':64,'all_original_columns_checked':64,'absolute_phases_exact':True,'invoice':invoice,'new_IDLES':0,'new_thin_queries':0,'codeword':'B_E=E3 E2^-1 E1','negative_endpoint':'Q^-1 B_E D123 on original X','positive_after_ordinary_inverse_code':'D123 Q on original Y, fullrank4','negative_Binverse_naive_Gaussian_claim_rejected':True,'code_Q_noncommuting':True,'scope':'Literal small fulloperator three-stage realization; the global template uses25-axis module on three disjoint24-axis fresh blocks, giving73 ambient axes. Global22016-mode query and actual root512 checkpoint proofs bind that template. Negative endpoint Gaussian admission, full outer precision/TM/storage and kappa remain UNKNOWN.'}
 return json.loads(json.dumps(result)),program
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r,p=calculate()
 if a.write:(HERE/'N3.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');(HERE/'N3-PROGRAM.json').write_text(json.dumps(p,sort_keys=True,indent=2)+'\n')
 else:need(json.loads((HERE/'N3.json').read_bytes())==r,'readonly N3 receipt');need(json.loads((HERE/'N3-PROGRAM.json').read_bytes())==p,'readonly literal N3 word')
 print(json.dumps(r,sort_keys=True))
