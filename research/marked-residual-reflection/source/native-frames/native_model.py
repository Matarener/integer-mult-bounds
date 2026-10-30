"""Pinned Gaussian Clifford model for common2/fresh2 native bridges.
Apache-2.0; substantial OpenAI Codex assistance. Frozen imports are read only.
"""
from pathlib import Path
import hashlib,importlib.util,sys
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
PIN='20ecf2891d80b5acf18d980b2164fb44ea7faa90'
CE_PATH=BASE/'vendor/clifford_exact.py'
CE_SHA='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'
BOUND_PATH=BASE/'vendor/full_stabilizer_bound.py'
BOUND_SHA='f073a00ad4831616e873eb110fd33ad7226010a7c2f6cfa6a6b63167bf58ef75'
def need(ok,why):
 if not ok:raise ValueError(why)
def load(name,path,sha):
 need(hashlib.sha256(path.read_bytes()).hexdigest()==sha,'source pin '+str(path))
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
ce=load('native_frames_pinned_clifford',CE_PATH,CE_SHA)
b=load('native_frames_frozen_independent',BOUND_PATH,BOUND_SHA)
def mul(*ops):return b.standard_product(ce,*ops)
def same(a,c,why,phase=True):
 need(a.tab==c.tab,why+' signed tableau')
 if phase:need(b.sparse_column(a)==b.sparse_column(c),why+' actual Gaussian phase')
def phase(n,p):return ce.Op(n,ce.identity(n),[('phase',p%4)])
def symplectic_defect_rank(op):
 return b.binary_rank(x^y for x,y in zip(b.binary_tableau(op),b.binary_tableau(ce.ident(op.n))))
def pauli(n,x=0,z=0,p=0):
 out=ce.diag(n,[0]*n,[2*((z>>j)&1)for j in range(n)])
 return mul(phase(n,p),ce.xgate(n,x),out)
def conjugated_pauli(op,x=0,z=0,p=0):
 triple=ce.apply(op.tab,(x,z,p));return pauli(op.n,*triple),triple
class Model:
 def __init__(self,f=1,stages=4):
  need(f>=1 and stages>=1,'positive chunk/stages');self.f=f;self.stages=stages;self.n=(2+2*stages)*f;self.I=ce.ident(self.n)
  self.N=self.Npair(0,1);self.U=self.Hp(0);self.V=mul(self.N,self.U.adjoint())
  self.P=[self.swap_pair(s+1)for s in range(stages)];self.T=[self.Npair(2+2*s,3+2*s)for s in range(stages)]
  self.Q=ce.xgate(self.n,1)
 def Hp(self,chunk):
  out=self.I
  for j in range(self.f):
   bit=chunk*self.f+j;alpha=[0]*self.n;alpha[bit]=2
   out=mul(ce.diag(self.n,[0]*self.n,alpha),ce.cgate(self.n,1<<bit).adjoint(),out)
  return out
 def Hq(self,chunk):
  out=self.I
  for j in range(self.f):
   bit=chunk*self.f+j;alpha=[0]*self.n;alpha[bit]=2
   out=mul(ce.diag(self.n,[0]*self.n,alpha),ce.cgate(self.n,1<<bit),out)
  return out
 def Npair(self,p,q):return mul(phase(self.n,1),self.Hp(p),self.Hq(q))
 def swap_pair(self,s):
  rows=[1<<j for j in range(self.n)]
  for k in range(2*self.f):rows[k],rows[2*s*self.f+k]=rows[2*s*self.f+k],rows[k]
  return ce.perm(self.n,rows)
 def prefix(self,s):return mul(self.I,*self.T[:s])
 def phi(self,a):return mul(self.N.adjoint(),a,self.N)
 def tau(self,a):return mul(self.U,a,self.U.adjoint())
 def upsilon(self,a):return mul(self.V,a,self.V.adjoint())
 def pqqp(self):
  need(self.stages>=4,'pqqp uses4 stages');gs=[self.I,self.I];controls=[];F=self.I
  for s,(kind,W) in enumerate(zip('FGFG',[self.U,self.V,self.V,self.U])):
   required=self.phi(gs[1])if kind=='F'else mul(W,self.N.adjoint(),gs[1],self.N,W.adjoint())
   L=mul(required,gs[0].adjoint());controls.append(L);gs[0]=required
   if kind=='F':gs=[gs[0],mul(W,self.P[s],gs[1],W.adjoint())]
   else:gs=[mul(W.adjoint(),gs[0],W),mul(self.P[s],gs[1])]
   F=mul(self.T[s],F)
  return gs,controls
