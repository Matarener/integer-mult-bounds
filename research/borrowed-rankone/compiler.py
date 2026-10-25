"""Exact native power-of-two gauges. Apache-2.0; Dugongue, OpenAI assistance."""
"""Exact integer min-cost circulation for zero-scratch dyadic unit gauges.
Apache-2.0; Dugongue with substantial OpenAI assistance.
"""
from fractions import Fraction as Q

def need(ok,msg):
 if not ok:raise ValueError(msg)

def valuation(q):
 q=Q(q);need(q!=0 and q.denominator&(q.denominator-1)==0,'Nonzero dyadic coefficient')
 n=abs(q.numerator);return (n&-n).bit_length()-1-(q.denominator.bit_length()-1)

def add_cost(q):
 q=Q(q)
 if not q:return 0
 n,d=abs(q.numerator),q.denominator;need(d&(d-1)==0,'Dyadic scalar')
 return 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)

def power(e):return Q(2**e)if e>=0 else Q(1,2**(-e))

def optimize(matrix):
 M=[[Q(x)for x in row]for row in matrix];need(M and M[0]and all(len(r)==len(M[0])for r in M),'Rectangular nonempty matrix')
 m,n=len(M),len(M[0]);N=1+n+m;g=[[]for _ in range(N)];terms=[]
 def edge(u,v,c,k):
  a=len(g[u]);b=len(g[v]);g[u].append([v,b,c,k]);g[v].append([u,a,c,-k]);terms.append((u,a,c,k))
 for i in range(n+m):edge(0,1+i,4,0)
 for j in range(m):
  for i in range(n):
   if M[j][i]:edge(1+i,1+n+j,2,-valuation(M[j][i]))
 total=0;steps=0
 while True:
  dist=[0]*N;pred=[None]*N;x=None
  for _ in range(N):
   x=None
   for u in range(N):
    for k,e in enumerate(g[u]):
     v,rev,cap,cost=e
     if cap and dist[v]>dist[u]+cost:dist[v]=dist[u]+cost;pred[v]=(u,k);x=v
   if x is None:break
  if x is None:break
  for _ in range(N):x=pred[x][0]
  cycle=[];v=x
  while True:
   u,k=pred[v];cycle.append((u,k));v=u
   if v==x:break
  delta=min(g[u][k][2]for u,k in cycle);cycle_cost=sum(g[u][k][3]for u,k in cycle)
  need(delta>0 and cycle_cost<0,'Negative augmenting cycle')
  for u,k in cycle:
   v,rev,cap,cost=g[u][k];g[u][k][2]-=delta;g[v][rev][2]+=delta
  total+=delta*cycle_cost;steps+=1
 p=[x-dist[0]for x in dist];a=p[1:n+1];b=p[n+1:]
 offset=sum(add_cost(x)-2*abs(valuation(x))for row in M for x in row if x)
 primal=4*sum(abs(x)for x in a+b)+2*sum(abs(valuation(x)+b[j]-a[i])for j,row in enumerate(M)for i,x in enumerate(row)if x)
 need(primal==-total,'Exact circulation duality')
 program=[]
 for kind,exps in [('X',a),('Y',b)]:
  for i,e in enumerate(exps):
   if e:program.append(['scale',[kind,i],power(e).numerator,power(e).denominator])
 for j,row in enumerate(M):
  for i,q in enumerate(row):
   if q:
    q*=power(b[j]-a[i]);program.append(['add',['Y',j],['X',i],q.numerator,q.denominator])
 for kind,exps in [('X',a),('Y',b)]:
  for i,e in enumerate(exps):
   if e:program.append(['scale',[kind,i],power(-e).numerator,power(-e).denominator])
 return {'matrix':M,'source_exponents':a,'target_exponents':b,'program':program,'old':sum(add_cost(x)for row in M for x in row),'new':offset+primal,'valuation_objective':primal,'constant':offset,'circulation_cost':total,'cycle_steps':steps,'dual_flows':[[u,g[u][k][0],c,kcost,c-g[u][k][2]]for u,k,c,kcost in terms],'owned_peak':0,'new_recursive_jobs':0}

def rank_one(M):
 M=[[Q(x) for x in row] for row in M];m,n=len(M),len(M[0])
 pivot=next(((j,i) for j in range(m) for i in range(n) if M[j][i]),None)
 if pivot is None:return None
 j0,i0=pivot;u=[row[i0] for row in M];v=[x/M[j0][i0] for x in M[j0]]
 if any(q.denominator&(q.denominator-1) for q in u+v):return None
 if any(M[j][i]!=u[j]*v[i] for j in range(m) for i in range(n)):return None
 program=[['clear',['T',0]]]
 for i,q in enumerate(v):
  if q:program.append(['add',['T',0],['X',i],q.numerator,q.denominator])
 for j,q in enumerate(u):
  if q:program.append(['add',['Y',j],['T',0],q.numerator,q.denominator])
 program.append(['clear',['T',0]])
 return {'program':program,'new':4+sum(add_cost(q) for q in u+v),'owned_peak':1,'mechanism':'rank-one predecessor macro'}
def encode(x):
 if isinstance(x,Q):return str(x)
 if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
 if isinstance(x,(tuple,list)):return [encode(v) for v in x]
 return x


def borrowed_candidates(matrix):
 """Legal rank-one conjugations, restoring every borrowed persistent field.
 No division by runtime data; all divisions below are coefficient arithmetic.
 """
 M=[[Q(x) for x in row] for row in matrix]
 need(M and M[0] and all(len(row)==len(M[0]) for row in M),'Rectangular nonempty matrix')
 m,n=len(M),len(M[0])
 for row in M:
  for q in row:
   if q:valuation(q)
 out=[]
 def add(dst,src,q):return ['add',dst,src,q.numerator,q.denominator]
 def record(kind,pivot,prep,middle,undo):
  program=prep+middle+undo
  out.append({'mechanism':kind,'pivot':pivot,'preparation_count':len(prep),'program':program,'new':sum(add_cost(Q(e[3],e[4])) for e in program),'owned_peak':0,'new_recursive_jobs':0})
 for i in range(n):
  j0=next((j for j in range(m) if M[j][i]),None)
  if j0 is None:continue
  u=[row[i] for row in M];v=[q/M[j0][i] for q in M[j0]]
  if any(q.denominator&(q.denominator-1) for q in v):continue
  if any(M[j][k]!=u[j]*v[k] for j in range(m) for k in range(n)):continue
  prep=[add(['X',i],['X',k],q) for k,q in enumerate(v) if k!=i and q]
  middle=[add(['Y',j],['X',i],q) for j,q in enumerate(u) if q]
  undo=[add(e[1],e[2],-Q(e[3],e[4])) for e in reversed(prep)]
  record('borrow-source',i,prep,middle,undo)
 for j in range(m):
  i0=next((i for i in range(n) if M[j][i]),None)
  if i0 is None:continue
  v=M[j];u=[row[i0]/M[j][i0] for row in M]
  if any(q.denominator&(q.denominator-1) for q in u):continue
  if any(M[k][i]!=u[k]*v[i] for k in range(m) for i in range(n)):continue
  prep=[add(['Y',k],['Y',j],-q) for k,q in enumerate(u) if k!=j and q]
  middle=[add(['Y',j],['X',i],q) for i,q in enumerate(v) if q]
  undo=[add(e[1],e[2],-Q(e[3],e[4])) for e in reversed(prep)]
  record('borrow-target',j,prep,middle,undo)
 return out

def compile_borrowed(matrix):
 gauge=optimize(matrix)
 candidates=[gauge]+borrowed_candidates(matrix)
 return min(candidates,key=lambda x:x['new'])
