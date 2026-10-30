"""Pinned exact all-f Gaussian X-character operator algebra.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib,importlib.util,sys
sys.dont_write_bytecode=True
OLD=Path('/Users/ross/git/math/.research-automation/runs/kappa-four-coordinate-20261019T0717Z')
PINS={
 'root-chronology/quadratic_charts.py':'de2a36f6a6b567360c90477b58da44e2f1b618fd006d058ab1ea04e983952c3f',
 'native-frames/native_model.py':'6397a86bd3d1461be182fcfa8602b0c70c489964a8c14f12436ba2506e11d9e3',
 'native-frames/even_parity_source.py':'961f136e4bc1b5da930bdd4ba9bbb594892b9e27f7ab44749d747d4fe16b4cb3',
 'caller/nested_prefix.py':'9ec10cb0243c0c829475ad7290f4953cdff27cb0f90f70b687c4bbee98af676b',
 'caller/nested_family.py':'88f425d12baf8a4f849cccd24605f21680eb8ce8d199054db4b4e7734eca72b6',
}
def need(c,m):
 if not c:raise ValueError(m)
for p,h in PINS.items():need(hashlib.sha256((OLD/p).read_bytes()).hexdigest()==h,'frozen source pin '+p)
spec=importlib.util.spec_from_file_location('joint_pinned_quadratic',OLD/'root-chronology/quadratic_charts.py')
qc=importlib.util.module_from_spec(spec);sys.modules[spec.name]=qc;spec.loader.exec_module(qc)
sys.path.insert(0,str(OLD/'caller'));sys.path.insert(0,str(OLD/'native-frames'))
from nested_prefix import skeleton
from nested_family import retraction
from native_model import Model,ce,mul,same
from even_parity_source import kernels

ZERO=(F(0),)*8;ONE=(F(1),F(0))*4
def rotate(v,c,g):
 out=[]
 for r in range(4):
  a,b=v[2*r:2*r+2];out.extend(((a,b),(-b,a),(-a,-b),(b,-a))[(c*r+g)%4])
 return tuple(out)
def cproduct(a,b):
 return tuple(z for r in range(4)for z in(a[2*r]*b[2*r]-a[2*r+1]*b[2*r+1],a[2*r]*b[2*r+1]+a[2*r+1]*b[2*r]))
def normalize(g,v):
 return qc.Mono(g.rows,g.offset,g.alpha,g.quad),rotate(v,g.constant,g.global_phase)
def mono(g,c=1):
 k,v=normalize(g,tuple(F(c)*x for x in ONE));return{k:v}if any(v)else{}
def add(a,b):
 out=dict(a)
 for k,v in b.items():
  w=tuple(x+y for x,y in zip(out.get(k,ZERO),v))
  if any(w):out[k]=w
  else:out.pop(k,None)
 return out
def scale(a,c):return{k:tuple(F(c)*x for x in v)for k,v in a.items()}if c else{}
def product(a,b):
 out={}
 for g,x in a.items():
  for h,y in b.items():
   k,v=normalize(g@h,cproduct(x,y));out=add(out,{k:v})
 return out
def adjoint(a):
 out={}
 for g,v in a.items():
  k,w=normalize(g.inv(),tuple(x if i%2==0 else-x for i,x in enumerate(v)));out=add(out,{k:w})
 return out
def summ(items):
 out={}
 for item in items:out=add(out,item)
 return out
def eye(n,m):
 I=mono(qc.identity(m));return[[dict(I)if i==j else{}for j in range(n)]for i in range(n)]
def mm(A,B):
 n=len(A);return[[summ(product(A[i][k],B[k][j])for k in range(n)if A[i][k]and B[k][j])for j in range(n)]for i in range(n)]
def serial(e):return[{'x_monomial':g.data(),'coefficients_by_f_mod4':[[str(v[2*r]),str(v[2*r+1])]for r in range(4)]}for g,v in sorted(e.items(),key=lambda x:str(x[0]))]
def sm(M):return[[serial(e)for e in row]for row in M]
def n_pair(m,i):
 return qc.old_operator({'operator':{'native_blocks':[i],'block_permutation':list(range(m//2)),'sign':1}},m)
def plane_swap(m,i,j):
 rows=[1<<k for k in range(m)]
 for d in(0,1):rows[2*i+d],rows[2*j+d]=rows[2*j+d],rows[2*i+d]
 return qc.Mono(tuple(rows),0,(0,)*m,(0,)*m)
def j_operator(m):
 return qc.from_function(qc.identity(m).rows,3,lambda x:1+qc.parity(x&5)+qc.parity(x&10),1)
def prefix(m,s):
 out=qc.identity(m)
 for i in range(1,s+1):out=n_pair(m,i)@out
 return out

class Word:
 def __init__(self,n,m):self.n=n;self.m=m;self.M=eye(n,m);self.Mi=eye(n,m);self.events=[]
 def add(self,d,s,c=1,label=''):
  if not c:return
  need(d!=s,'ADD distinct banks')
  self.M[d]=[add(x,scale(y,c))for x,y in zip(self.M[d],self.M[s])]
  for row in self.Mi:row[s]=add(row[s],scale(row[d],-c))
  self.events.append({'kind':'ADD','dst':d,'src':s,'coefficient':str(c),'label':label})
 def unary(self,b,g,label='',native=False,family=None):
  G,Gi=mono(g),mono(g.inv())
  self.M[b]=[product(G,x)for x in self.M[b]]
  for row in self.Mi:row[b]=product(row[b],Gi)
  self.events.append({'kind':'NATIVE'if native else'ADDRESS_OR_UNIT','bank':b,'x_monomial':g.data(),
                      'rank_per_f':qc.rank(g.polar()),'label':label,'native_family':family})
 def swap(self,i,j,label=''):
  self.M[i],self.M[j]=self.M[j],self.M[i]
  for row in self.Mi:row[i],row[j]=row[j],row[i]
  self.events.append({'kind':'BANK_SWAP','banks':[i,j],'label':label})
 def inverse_events(self):
  out=[]
  for e in reversed(self.events):
   d=dict(e)
   if e['kind']=='ADD':d['coefficient']=str(-F(e['coefficient']))
   elif e['kind']!='BANK_SWAP':d['x_monomial']=qc.decode(e,self.m).inv().data()
   if e['kind']not in('ADD','BANK_SWAP')and'one_coordinate_literal_circuit'in e:
    literal=ce.Op(self.m,tuple(tuple(t)for t in e['one_coordinate_tableau']),e['one_coordinate_literal_circuit']).adjoint()
    d['one_coordinate_literal_circuit']=literal.circuit;d['one_coordinate_tableau']=[list(t)for t in literal.tab]
    d['phase_exponent']=-e['phase_exponent']
    if e.get('native_family'):
     d['native_family']=dict(e['native_family']);d['native_family']['inverse']=not e['native_family'].get('inverse',False)
     key=e['native_recipe_id'];d['native_recipe_id']=key[:-3]if key.endswith('inv')else key+'inv'
   out.append(d)
  return out
