"""Explicit rational global20480-mode query and finite ordinary recoder."""
import argparse,hashlib,json
from fractions import Fraction as F
from collections import Counter
from itertools import product
from pathlib import Path
from decimal import Decimal,localcontext
HERE=Path(__file__).resolve().parent
PIN='ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da'
def need(q,s):
 if not q:raise ValueError(s)
def canonical(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def eye(n):return [[F(i==j)for j in range(n)]for i in range(n)]
def inverse(A):
 n=len(A);R=[list(map(F,r))+eye(n)[i]for i,r in enumerate(A)]
 for j in range(n):
  p=next(i for i in range(j,n)if R[i][j]);R[p],R[j]=R[j],R[p];q=R[j][j];R[j]=[x/q for x in R[j]]
  for i in range(n):
   if i!=j and R[i][j]:q=R[i][j];R[i]=[x-q*y for x,y in zip(R[i],R[j])]
 return [r[n:]for r in R]
def matrix_apply_ops(A,ops):
 A=[r[:]for r in A]
 for e in ops:
  if e[0]=='SWAP':A[e[1]],A[e[2]]=A[e[2]],A[e[1]]
  elif e[0]=='SCALE':A[e[1]]=[F(e[2],e[3])*x for x in A[e[1]]]
  else:
   need(e[0]=='ADD','elementary recoder');i,j=e[1:3];q=F(e[3],e[4]);A[i]=[x+q*y for x,y in zip(A[i],A[j])]
 return A
def elementary_to_inverse(A):
 n=len(A);R=[r[:]for r in A];ops=[]
 for j in range(n):
  p=next(i for i in range(j,n)if R[i][j])
  if p!=j:R[p],R[j]=R[j],R[p];ops.append(['SWAP',p,j])
  q=1/R[j][j]
  if q!=1:R[j]=[q*x for x in R[j]];ops.append(['SCALE',j,q.numerator,q.denominator])
  for i in range(n):
   if i!=j and R[i][j]:
    q=-R[i][j];R[i]=[x+q*y for x,y in zip(R[i],R[j])];ops.append(['ADD',i,j,q.numerator,q.denominator])
 need(R==eye(n),'elementary reduction to identity')
 return ops
def inverse_ops(ops):
 out=[]
 for e in reversed(ops):
  if e[0]=='ADD':out.append(['ADD',e[1],e[2],-e[3],e[4]])
  elif e[0]=='SCALE':out.append(['SCALE',e[1],e[3],e[2]])
  else:out.append(e)
 return out
def encode(A):return [[str(x)for x in r]for r in A]
def power_interval(n):
 def log(z):
  v=F();term=z
  for j in range(24):v+=2*term/(2*j+1);term*=z*z
  return v,v+2*term/(49*(1-z*z))
 a=F(605457647,200000000000);k=n.bit_length()-1;l2,u2=log(F(1,3));l,u=log(F(n-2**k,n+2**k));l=(l+k*l2)*a;u=(u+k*u2)*a
 need(0<=l<=u<1,'power interval domain');sums=[]
 for x in [l,u]:
  term=total=F(1)
  for j in range(1,19):term*=x/j;total+=term
  sums.append(total)
 tail=term*u/19/(1-u/20)
 return F(n)/(sums[1]+tail),F(n)/sums[0]
def bounded_margin(rank):
 # 2/3*73^sigma -sum(8,9,15,16)^sigma -(rank/v)*25^sigma.
 l,u=power_interval(73);lo,hi=F(2,3)*l,F(2,3)*u
 for n,c in [(8,F(1)),(9,F(1)),(15,F(1)),(16,F(1)),(25,F(rank,112**3))]:
  l,u=power_interval(n);lo-=c*u;hi-=c*l
 unit=10**18
 return [str(F((lo*unit).__floor__(),unit)),str(F((hi*unit).__ceil__(),unit))]
def calculate():
 template_raw=(HERE/'inputs/K-TEMPLATE.json').read_bytes();need(hashlib.sha256(template_raw).hexdigest()=='7477f45dc0036a1e2da980964a2775696c259be56bc0d4e70ba62788dd853cdf','global whole-K template pin');template=json.loads(template_raw);orth=template['orthonormal_basis_raw27']
 dot=lambda x,y:(x&y).bit_count()&1
 need(len(orth)==25 and all(dot(x,y)==int(i==j)for i,x in enumerate(orth)for j,y in enumerate(orth)),'authenticated global U25 orthonormal chart')
 need(all(len({((x>>(9*j))&511).bit_count()%2 for j in range(3)})==1 for x in orth),'every chart generator lies in equal-block-parity U25')
 characteristic=0
 for x in orth:characteristic^=x
 need(characteristic==(1<<27)-1,'U25 characteristic equals raw allones')
 raw=(HERE/'inputs/NORMALIZERS.json').read_bytes();need(hashlib.sha256(raw).hexdigest()==PIN,'exact frozen root/mode inputs');d=json.loads(raw);need(all(dot(p['q'],p['q'])==1 and p['q']!=511 for p in d['ports']),'all112 base labels normone noncharacteristic');M=[list(map(F,r))for r in zip(*d['mode_columns'])];n=112
 need(len(M)==112 and all(sum(M[i][a]*M[i][b]for i in range(n))==(56 if a==b else 0)for a,b in product(range(8),repeat=2)),'actual M^T M=56I')
 # Deterministic independent pivot rows of M, only eight-dimensional algebra.
 piv=[];R=[]
 for i,row in enumerate(M):
  v=row[:]
  for j,b in R:
   if v[j]:q=v[j];v=[x-q*y for x,y in zip(v,b)]
  j=next((j for j,x in enumerate(v)if x),None)
  if j is not None:
   q=v[j];v=[x/q for x in v];R.append((j,v));piv.append(i)
  if len(piv)==8:break
 free=[i for i in range(n)if i not in piv];Hinv=inverse([[M[piv[j]][a]for j in range(8)]for a in range(8)])
 N=[[F(i==f)for f in free]for i in range(n)]
 for k,f in enumerate(free):
  for j,p in enumerate(piv):N[p][k]=-sum(Hinv[j][a]*M[f][a]for a in range(8))
 need(all(sum(M[i][a]*N[i][b]for i in range(n))==0 for a in range(8)for b in range(104)),'explicit104-dimensional rational kernel')
 T=[M[i]+N[i]for i in range(n)]
 Ti=[[M[j][a]/56 for j in range(n)]for a in range(8)]+[[F(f==j)-sum(M[f][a]*M[j][a]for a in range(8))/56 for j in range(n)]for f in free]
 need(all(sum(T[i][k]*Ti[k][j]for k in range(n))==F(i==j)for i,j in product(range(n),repeat=2)),'all112^2 rational inverse entries')
 # Efficient rank-eight block elimination rather than dense112 elimination.
 # Modal c=M^T y/56 first overwrites only the8 pivot rows invertibly;
 # free y are consumed before their kernel-coordinate updates.
 A8=[[M[piv[j]][a]/56 for j in range(8)]for a in range(8)]
 local=inverse_ops(elementary_to_inverse(A8));invops=[]
 for e in local:
  if e[0]=='SWAP':invops.append(['SWAP',piv[e[1]],piv[e[2]]])
  elif e[0]=='SCALE':invops.append(['SCALE',piv[e[1]],e[2],e[3]])
  else:invops.append(['ADD',piv[e[1]],piv[e[2]],e[3],e[4]])
 for a,p in enumerate(piv):
  for f in free:
   if M[f][a]:q=M[f][a]/56;invops.append(['ADD',p,f,q.numerator,q.denominator])
 for f in free:
  for a,p in enumerate(piv):
   if M[f][a]:q=-M[f][a];invops.append(['ADD',f,p,q.numerator,q.denominator])
 current=list(range(112));desired=piv+free
 for i in range(112):
  j=current.index(desired[i])
  if i!=j:invops.append(['SWAP',i,j]);current[i],current[j]=current[j],current[i]
 fwdops=inverse_ops(invops)
 need(matrix_apply_ops(eye(n),invops)==Ti,'literal in-place T^-1 recoder')
 need(matrix_apply_ops(eye(n),fwdops)==T,'literal in-place T recoder')
 # Bind K/C compatibility using all14 actual localcube matrices.
 groups={}
 for i,r in enumerate(M):groups.setdefault(tuple(j for j,x in enumerate(r)if x),[]).append(i)
 need(len(groups)==14 and all(len(g)==8 for g in groups.values()),'14 actualeight cubes')
 for g in groups.values():
  K=[[F(i==j)-sum(M[g[i]][a]*M[g[j]][a]for a in range(8))/4 for j in range(8)]for i in range(8)]
  need(all(sum(K[i][j]*K[j][k]for j in range(8))==F(i==k)for i,k in product(range(8),repeat=2)),'all actual Kcube involutions')
  need(all(sum(K[i][j]*M[g[j]][a]for j in range(8))==-M[g[i]][a]for i in range(8)for a in range(8)),'actual K acts minusidentity on globalC modes')
 sectors=[];rank=0
 for flags in product([0,1],repeat=3):
  active=sum(flags);dim=8**active*104**(3-active);lam=98 if active==2 else(-1078 if active==3 else 0)
  if lam:rank+=dim
  sectors.append({'active_C_axes':list(flags),'dimension':dim,'F_C_eigenvalue':lam,'A_eigenvalue':1-lam,'A_inverse_eigenvalue':str(F(1,1-lam))})
 need(rank==20480,'exact globalF3 rank20480')
 # Structured global loops are explicit; do not expand all v*GL operations.
 glcounts=Counter(e[0]for e in invops)+Counter(e[0]for e in fwdops);v=112**3;axis_batches=3*112**2
 gather_scatter_counts={k:2*axis_batches*c for k,c in glcounts.items()}
 gather_scatter_counts.update({'field_monomial_pass':4*v,'mode_COPY':rank,'mode_ADD':rank,'mode_CLEAR':rank})
 # Every elementary ADD/SCALE and COPY has a finite field-l2 norm bound.
 # Gaussian children and P/D/X/phase have norm1 at every width.
 glgrowth=F(1)
 for e in invops+fwdops:
  if e[0]=='ADD':glgrowth*=1+abs(F(e[3],e[4]))
  elif e[0]=='SCALE':glgrowth*=max(F(1),abs(F(e[2],e[3])))
 with localcontext()as c:
  c.prec=70;a=Decimal('0.003027288235');sigma=1-a;p=lambda r:(Decimal(r).ln()*sigma).exp();allow=Decimal(2)/3*p(73)-sum(p(r)for r in [8,9,15,16]);cost=Decimal(rank)/v*p(25);costold=Decimal(22016)/v*p(25)
  preflight={'a':str(a),'N':3,'target_grant':{'73':2*v},'base_K_paid':{str(r):3*v for r in [8,9,15,16]},'correction_paid':{'25':3*rank},'per_port_local_K_only_allowance':str(allow),'per_port_local20480H25_cost':str(cost),'conditional_margin20480':str(allow-cost),'conditional_margin22016':str(allow-costold),'certified_margin20480_interval':bounded_margin(20480),'certified_margin22016_interval':bounded_margin(22016),'scope':'Conditional preflight grants both coded E terminals as independent H73. This terminal grant is UNKNOWN and is not a constructed supplier, numerical kappa or formal admission.'}
 need(F(preflight['certified_margin20480_interval'][0])>0 and F(preflight['certified_margin22016_interval'][0])>0,'strict rational positive conditional margins')
 program={'schema':'global-F3-rational-mode-algorithm/v1','normalizer_pin':PIN,'global_orthonormal_basis_raw27':orth,'global_normalizer_rule':['For globalport triple(a,b,c), raw q=q_a | (q_b<<9) | (q_c<<18) from pinned base NORMALIZERS ports.','Its25-bit coordinate is sum(dot(rawq,orth[j])<<j). Base labels have norm1 and are not9-bit allones; all product labels lie in U25, are norm1 and not its characteristic.','If q0=0 take G=T_(e0+q); otherwise choose first j>0 with q_j=0 and G=T_(ej+q) T_(e0+ej).','T_v x=x+(v dot x)v. Put z_j=(wt(row_j G)-1)/2 mod2 and L=Z_z P_G.','Orthogonality and weight congruence prove L R25 L^-1=R25 with exact phase for all positive widths. All scalar owner coefficients act once; only address monomials tensor lift.'],'mode_matrix112x8':encode(M),'kernel_pivot_rows':piv,'kernel_free_rows':free,'T112':encode(T),'T_inverse112':encode(Ti),'literal_T_inverse_elementary_word':invops,'literal_T_elementary_word':fwdops,'global_owner_basis':'T tensor T tensor T, acting on three owner selector coordinates. Each elementary112-owner word repeats for every one of112^2 fixed other-axis coordinates. No tensor power of owner sums in field width.','nonzero_modes':[x for x in sectors if x['F_C_eigenvalue']],'owned_query_word':['Apply each physical L_i to original Y_i (ordinary signed monomial).','For axis0,1,2 and every fixed pair of other owner indices in0..111, apply emitted T_inverse112 word in place.','COPY each coordinate with at least2 modal indices<8 into its own zero field g_t; there are20480.','Restore all original Y by inverse owner-axis words then L_i^-1. All source reads finish before native/precode overwrites.','Apply one native full R25 positive Gaussian to every g_t.','To add -R F_C Y into existing X, apply L_i and T_inverse owner-axis words to X, ADD -lambda_t g_t at each nonzero mode coordinate, restore T words then L_i^-1.','CLEAR every owned g_t after its final scatter.'],'code_E_word':['Normalize each main-bank owner by L_i.','Apply T_inverse on each owner axis.','SCALE each modal sector by (1-lambda_t)^-1 for E or by (1-lambda_t) for E^-1.','Restore T on each owner axis.','Apply actual block-diagonal K_odd on every8x8x8 cube using its literal76-per-row coefficients, owned512-field output scratch; after every source read, SWAP each completed output with its main field, then CLEAR the old main value now in owned scratch. Reuse the512 scratch fields.','Apply L_i^-1 to restore physical coordinates.'],'operator_claim':'F_C=L^-1 T^tensor3 diag(lambda) (T_inverse)^tensor3 L. It commutes with R because every L_i does. K_odd F_C=-F_C and K_odd^2=I, so E=K_odd(I-F_C)^-1 is real symmetric, invertible and commutes with R.'}
 result={'schema':'global20480-mode-query-proof/v1','status':'PASS_EXPLICIT_RATIONAL_MODES_AND_INPLACE_ORDINARY_WORD','normalizer_pin':PIN,'base_dimension':112,'base_C_rank':8,'kernel_dimension':104,'literal_T_inverse_counts':dict(Counter(e[0]for e in invops)),'literal_T_counts':dict(Counter(e[0]for e in fwdops)),'rational_T_inverse_entries_checked':112**2,'global_dimension':v,'sectors':sectors,'nonzero_global_modes':rank,'query_paid_profile_per_full':{'25':rank},'gather_scatter_ordinary_counts':gather_scatter_counts,'query_owned_fields':rank,'ordinary_E_code_per_evaluation':{'ADD':axis_batches*glcounts['ADD']+76*v,'SCALE':axis_batches*glcounts['SCALE']+rank,'SWAP':axis_batches*glcounts['SWAP']+v,'field_monomial_pass':2*v,'OWN_ZERO':v,'CLEAR':v,'reusable_owned_fields':512},'ordinary_query_both_orientations_upper':{'ADD':2*axis_batches*glcounts['ADD']+2*rank,'SCALE':2*axis_batches*glcounts['SCALE'],'SWAP':2*axis_batches*glcounts['SWAP'],'field_monomial_pass':4*v,'COPY':rank,'OWN_ZERO':rank,'CLEAR':2*rank},'ordinary_native_inverse_transpose_and_boundaries_upper':{'ADD':77*v,'P':15*v,'D':15*v,'X':20*v,'phase':6*v,'COPY':v,'OWN_ZERO':v,'CLEAR':2*v},'ordinary_local_module_upper_recipe':'Two ordinary E/E^-1 code evaluations plus one query upper bill plus native inverse-transpose/boundary upper bill. This conservative unified bound covers both orientations; some COPY/ZERO/CLEAR counts intentionally dominate either orientation. Structured loop counts, not an expanded global event list. N3 uses3 modules and3 extra positive-output inverse-code evaluations.','global_inverse_owned_peak_upper':v+rank+512,'field_l2_query_prefix_log2_upper':6*glgrowth.numerator.bit_length()+12,'field_l2_Ecode_prefix_log2_upper':3*glgrowth.numerator.bit_length()+14,'source_contact_extra_owned_for_inverse':v,'reusable_scalar_K_scratch_fields':512,'gather_scatter_GL_norm_product_numerator_bits':glgrowth.numerator.bit_length(),'gather_scatter_GL_norm_product_denominator_bits':glgrowth.denominator.bit_length(),'finite_precision_statement':'Each fixed ordinary elementary ADD norm<=1+abs(c), SCALE norm<=max(1,abs(c)), owned COPY norm<=2, CLEAR norm<=1. Their explicitly counted finite product bounds field-l2 error growth uniformly in positive width; paid Gaussians and signed monomials are unitary. This supplies a finite precision offset, not the unproved outer TM/rounding/storage admission.','preflight':preflight,'scientific_program_sha256':hashlib.sha256(canonical(program)).hexdigest(),'whole_caller_or_kappa':False}
 return json.loads(canonical(result)),program
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r,p=calculate()
 if a.write:(HERE/'MODES.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');(HERE/'MODES-PROGRAM.json').write_text(json.dumps(p,sort_keys=True,indent=2)+'\n')
 else:need(json.loads((HERE/'MODES.json').read_bytes())==r,'readonly modes receipt');need(json.loads((HERE/'MODES-PROGRAM.json').read_bytes())==p,'readonly actual rational basis and elementary words')
 print(json.dumps({k:r[k]for k in ['status','nonzero_global_modes','query_paid_profile_per_full','literal_T_counts','literal_T_inverse_counts','scientific_program_sha256','preflight']},sort_keys=True))
