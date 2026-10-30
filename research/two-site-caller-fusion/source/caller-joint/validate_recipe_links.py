"""Four unchanged source-authenticated recipe functions; unused cold imports omitted. Apache-2.0; Codex assistance."""
from joint_algebra import *

def compile_literal(circuit,n):
 out=ce.ident(n)
 for gate in circuit:
  if gate[0]=='P':op=ce.perm(n,tuple(gate[1]))
  elif gate[0]=='D':op=ce.diag(n,tuple(gate[1]),tuple(gate[2]))
  elif gate[0]=='C':op=ce.cgate(n,gate[1],gate[2])
  elif gate[0]=='X':op=ce.xgate(n,gate[1])
  elif gate[0]=='phase':op=ce.Op(n,ce.identity(n),[tuple(gate)])
  else:raise ValueError('uncovered selected literal '+str(gate[0]))
  out=out.then(op)
 return out

def compile_monomial(rec,n):
 return compile_literal([('D',rec['quadratic_rows'],rec['linear_Z4']),('P',rec['matrix_rows']),('X',rec['offset']),('phase',rec['phase'])],n)

def compile_recipe(rec,n):
 left=compile_monomial(rec['left'],n)
 if not rec['rank']:return left
 need(rec['right']is not None,'nonzero native rank has both literal monomial adapters')
 return compile_monomial(rec['right'],n).then(ce.fourier(n,range(rec['rank']))).then(left)

def embedding_circuit(circuit,embedding,n):
 d=len(embedding);need(len(set(embedding))==d and all(0<=j<n for j in embedding),'recipe embedding injective')
 def bits(x):return sum(((x>>i)&1)<<embedding[i]for i in range(d))
 out=[]
 for gate in circuit:
  typ=gate[0]
  if typ=='P':
   rows=[1<<i for i in range(n)]
   for i,j in enumerate(embedding):rows[j]=bits(gate[1][i])
   out.append(('P',tuple(rows)))
  elif typ=='D':
   rows=[0]*n;alpha=[0]*n
   for i,j in enumerate(embedding):rows[j]=bits(gate[1][i]);alpha[j]=gate[2][i]
   out.append(('D',tuple(rows),tuple(alpha)))
  elif typ in('C','X'):out.append((typ,bits(gate[1]),*gate[2:]))
  elif typ=='phase':out.append(tuple(gate))
  else:raise ValueError('uncovered embedded recipe '+typ)
 return out
