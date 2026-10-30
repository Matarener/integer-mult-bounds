"""Exact low-rank phases and analytic full-Gaussian native conjugation.

Source Clifford compiler credit retained. No dense 2^n state is allocated.
"""
def install(ce,need,peak):
 def sparse_zero(op,basis_state=0):
  vec={basis_state:(1,0)};den=0
  for e in op.circuit:
   k=e[0]
   if k=='P':vec={ce.mv(e[1],x):a for x,a in vec.items()}
   elif k=='X':vec={x^e[1]:a for x,a in vec.items()}
   elif k=='D':vec={x:ce.mul_i(a,ce.qvalue(e[1],e[2],x,op.n))for x,a in vec.items()}
   elif k=='phase':vec={x:ce.mul_i(a,e[1])for x,a in vec.items()}
   else:
    need(k=='C','literal sparse phase primitive');q,s=e[1:];out={}
    for x in set(vec)|{x^q for x in vec}:
     a,b=vec.get(x,(0,0));c,d=vec.get(x^q,(0,0));v=(a-s*b+c+s*d,b+s*a+d-s*c)
     if v!=(0,0):out[x]=v
    vec=out;den+=1
   peak[0]=max(peak[0],len(vec));need(len(vec)<=(1<<18),'bounded low-rank phase support')
   while den and all(not(a&1)and not(b&1)for a,b in vec.values()):vec={x:(a//2,b//2)for x,(a,b)in vec.items()};den-=1
  return vec,den
 ce.Op.zero_state=sparse_zero
 def monomial(op,known_zero=None):
  n=op.n;T=op.tab;need(all(x==0 and p%2==0 for x,z,p in T[n:]),'physical map is actually monomial')
  G=ce.transpose([x for x,z,p in T[:n]],n);b=ce.mv(G,sum((p//2)<<i for i,(x,z,p)in enumerate(T[n:])))
  gt=ce.transpose(G,n);Q=ce.transpose([ce.mv(gt,z)for x,z,p in T[:n]],n);alpha=[(p-2*ce.parity(b&z))%4 for x,z,p in T[:n]]
  if known_zero is None:
   vec,den=sparse_zero(op);need(den==0 and set(vec)=={b},'rank-zero absolute column');unit=vec[b]
  else:
   known_b,known_phase=known_zero;need(b==known_b,'analytic native anchor address agrees with exact tableau');unit=ce.mul_i((1,0),known_phase)
  phase=[(1,0),(0,1),(-1,0),(0,-1)].index(unit)
  out=ce.diag(n,Q,alpha).then(ce.perm(n,G)).then(ce.xgate(n,b)).then(ce.Op(n,ce.identity(n),[('phase',phase)]))
  need(out.tab==op.tab,'monomial signed tableau equality')
  if known_zero is None:need(sparse_zero(out)==sparse_zero(op),'monomial absolute phase equality')
  return out
 return sparse_zero,monomial

def native_K(ce,cols):
 n=len(cols);G=ce.transpose(tuple(cols),n);gi=ce.inv(G,n);tr=ce.transpose(gi,n)
 Q=tuple((1<<i)^sum(ce.parity(a&b)<<j for j,b in enumerate(tr))for i,a in enumerate(tr))
 return ce.perm(n,G).then(ce.diag(n,Q))

def flag_frame(ce,cols,r):
 K=native_K(ce,cols)
 return K.adjoint().then(ce.fourier(len(cols),range(r))).then(K)

def native_full_conjugate(ce,need,monomial,cols):
 """Compile R K_G R^-1, with a proved closed absolute-column phase."""
 n=len(cols);K=native_K(ce,cols);R=ce.fourier(n);G=ce.transpose(tuple(cols),n);inverse=ce.inv(G,n);invcols=ce.transpose(inverse,n)
 d=sum(((x.bit_count()//2)&1)<<j for j,x in enumerate(invcols));phase=(-d.bit_count())%4
 T=R.adjoint().then(K).then(R)
 out=monomial(T,(d,phase))
 need(all(e[0]in('P','D','X','phase')for e in out.circuit),'no Gaussian in compiled full conjugate')
 return out,{'offset':d,'phase':phase,'proof':'q(y)+wt(G^-1 y)=wt(y)+2d.y mod4. R^-1|0>=((1-i)/2)^n sum_x i^wt(x)|x>. Thus R K_G R^-1|0>=(-i)^wt(d)|d>. Signed tableau fixes the remaining monomial.',
              'native_G_columns':cols}
