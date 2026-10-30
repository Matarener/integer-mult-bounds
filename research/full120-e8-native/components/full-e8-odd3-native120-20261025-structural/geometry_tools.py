from pathlib import Path
from fractions import Fraction as F
from itertools import product
from hashlib import sha256
import argparse,importlib.util,json,sys,types
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def need(b,msg):
 if not b:raise ValueError(msg)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);v=importlib.util.module_from_spec(spec);sys.modules[name]=v;spec.loader.exec_module(v);return v
def dot(a,b):return(a&b).bit_count()&1
def basis(rows):
 p={}
 for x in rows:
  while x:
   j=x.bit_length()-1
   if j in p:x^=p[j]
   else:p[j]=x;break
 return list(p.values())
def span_contains(B,x):return len(basis(B+[x]))==len(B)
def radical(B):
 out=[]
 for mask in range(1<<len(B)):
  x=0
  for j,b in enumerate(B):
   if mask>>j&1:x^=b
  if all(not dot(x,b)for b in B):out.append(x)
 return basis(out)
def ortho_basis(B):
 out=[];current=basis(B)
 while current:
  odd=[x for x in current if dot(x,x)];need(odd,'nonalternating residual')
  for v in odd+[odd[0]^x for x in current if not dot(x,x)]:
   if not v or not dot(v,v):continue
   nxt=basis([x^(v if dot(v,x)else 0)for x in current])
   if len(nxt)!=len(current)-1 or(nxt and not any(dot(x,x)for x in nxt)):continue
   break
  else:raise ValueError('orthonormal choice')
  out.append(v);current=nxt
 need(all(dot(x,y)==int(i==j)for i,x in enumerate(out)for j,y in enumerate(out)),'literal full isometry')
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args()
 for name,pin in {'NORMALIZERS.json':'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da','clifford_exact.py':'2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'}.items():need(sha256((HERE/'inputs'/name).read_bytes()).hexdigest()==pin,'source pin '+name)
 base=types.SimpleNamespace(dot=dot,basis=basis,span_contains=span_contains,radical=radical,ortho_basis=ortho_basis)
 ce=load('core_class_clifford',HERE/'inputs/clifford_exact.py')
 data=json.loads((HERE/'inputs/NORMALIZERS.json').read_bytes());roots=list(zip(*data['mode_columns']));labels=[p['q']for p in data['ports']]
 cube=[j for j,row in enumerate(roots)if tuple(i for i,v in enumerate(row)if v)==(0,1,2,3)]
 need(len(cube)==8,'literal firstcube')
 parity={j:sum(roots[j][i]*roots[j][0]<0 for i in range(1,4))&1 for j in cube}
 U=[1|(1<<9)|(1<<18)]+[(1<<(9*b))^(1<<(9*b+j))for b in range(3)for j in range(1,9)]
 orth=base.ortho_basis(U);n=25
 def label(triple):
  raw=sum(labels[p]<<(9*k)for k,p in enumerate(triple))
  return sum(base.dot(raw,v)<<j for j,v in enumerate(orth))
 groups={p:[(t,label(t))for t in product(cube,repeat=3)if(sum(parity[j]for j in t)&1)==p]for p in [0,1]}
 S=base.basis(q for t,q in groups[0]);T=base.basis(q for t,q in groups[1]);D=base.radical(S)
 need(len(S)==len(T)==9 and len(D)==8,'actual9+9 radical8')
 need(all(not base.dot(a,b)for a in S for b in T),'crossparity complete orthogonality')
 need(len(base.basis(S+T))==10,'cube total span10')
 Phi=ce.canonical_frame(n,S)
 grank=lambda op:ce.rank([x for x,z,p in op.tab[n:]])
 source_hist={};reader_hist={}
 for t,q in groups[0]:
  need(base.dot(q,q)==1 and base.span_contains(S,q),'source literal q norm1 in S9')
  rank=grank(ce.canonical_frame(n,[q]).adjoint().then(Phi));source_hist[rank]=source_hist.get(rank,0)+1
 for t,q in groups[1]:
  need(base.dot(q,q)==1 and not base.span_contains(S,q),'reader literal norm1 outside S9')
  V=S[:]
  for v in ce.nullspace((q,),n):
   if len(base.basis(V+[v]))>len(V):V.append(v)
  need(len(V)==24 and all(not base.dot(q,v)for v in V),'actual qperp24 containing S9')
  rank=grank(Phi.adjoint().then(ce.canonical_frame(n,V)));reader_hist[rank]=reader_hist.get(rank,0)+1
 need(source_hist=={8:256}and reader_hist=={15:256},'all literal nestedflag source8/reader15')
 triples=list(product(cube,repeat=3))
 baseK={(a,b):F(int(a==b))-F(sum(x*y for x,y in zip(roots[a],roots[b])),4)for a in cube for b in cube}
 density={};bad=0;coefs={}
 for t in triples:
  count=0
  for u in triples:
   value=(sum((baseK[t[i],u[i]] if all(t[j]==u[j]for j in range(3)if j!=i) else F(0))for i in range(3))-baseK[t[0],u[0]]*baseK[t[1],u[1]]*baseK[t[2],u[2]])/2
   if value:
    count+=1;bad+=int(sum(parity[j]for j in t)%2==sum(parity[j]for j in u)%2);coefs[str(value)]=coefs.get(str(value),0)+1
  density[count]=density.get(count,0)+1
 need(density=={76:512}and not bad,'literalK76crossparitysupport')
 result={'schema':'literal-first-productcube-native-class-audit/v1','cube':cube,'ports_per_parity':256,'source_dimension':len(S),'target_other_parity_dimension':len(T),'source_selfpairing_rank':len(S)-len(D),'source_radical_dimension':len(D),'joint_span':len(base.basis(S+T)),'source_line_to_common_rank':source_hist,'common_to_full25_rank':grank(Phi.adjoint().then(ce.fourier(n))),'ground_to_common_rank':grank(Phi),'common_to_actual_reader_qperp_rank':reader_hist,'source_q_norm1_all':True,'reader_q_norm1_outside_S_all':True,'K_odd_row_density':density,'K_odd_coefficients':coefs,'direct_ordinary_ADDs_both_directions':512*76,'owned_helpers_required_for_direct_ADD':0,'paid_per_port':[8,9,15,16],'scope':'Complete first-cube field/flag rank audit, not yet full absolute-phase emitted core word or wholecaller.'}
 if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:need(json.loads((HERE/'RESULT.json').read_bytes())==json.loads(json.dumps(result)),'stable read-only class audit')
 print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
