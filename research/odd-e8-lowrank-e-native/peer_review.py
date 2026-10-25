"""AI peer review controls; no author code imported, package read-only.

The reviewer authored only the package's separate two_cube_native fixture.
This is not an independent human review, formal proof kernel or priority audit.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
from itertools import product
from hashlib import sha256
from functools import lru_cache
import argparse,gzip,json
HERE=Path(__file__).resolve().parent
DEFAULT=HERE
AUTHOR_METADATA={'FILES.json':'AUTHOR-FILES.json','SOURCES.json':'AUTHOR-SOURCES.json','VERIFY.json':'AUTHOR-VERIFY.json','README.md':'AUTHOR-README.md'}
def author_path(package,name):
 return package/AUTHOR_METADATA.get(name,name)
def need(ok,why):
 if not ok:raise ValueError(why)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def q(a=0,b=0):return(F(a),F(b))
ZERO=q();ONE=q(1)
def qa(x,y):return(x[0]+y[0],x[1]+y[1])
def qn(x):return(-x[0],-x[1])
def qm(x,y):return(x[0]*y[0]-x[1]*y[1],x[0]*y[1]+x[1]*y[0])
def qi(x):
 a,b=x;d=a*a+b*b;return(a/d,-b/d)
def zero(n):return[[ZERO for j in range(n)]for i in range(n)]
def eye(n):return[[ONE if i==j else ZERO for j in range(n)]for i in range(n)]
def add(A,B):return[[qa(a,b)for a,b in zip(r,s)]for r,s in zip(A,B)]
def scale(c,A):return[[qm(c,x)for x in r]for r in A]
def mm(A,B):
 O=zero(len(A));br=[[(j,x)for j,x in enumerate(r)if x!=ZERO]for r in B]
 for i,r in enumerate(A):
  for k,a in enumerate(r):
   if a!=ZERO:
    for j,b in br[k]:O[i][j]=qa(O[i][j],qm(a,b))
 return O
def prod(*As):
 R=eye(len(As[0]))
 for A in As:R=mm(R,A)
 return R
def tr(A):return list(map(list,zip(*A)))
def inv(A):
 n=len(A);R=[r[:]+eye(n)[i]for i,r in enumerate(A)]
 for j in range(n):
  p=next(i for i in range(j,n)if R[i][j]!=ZERO);R[p],R[j]=R[j],R[p];c=qi(R[j][j]);R[j]=[qm(c,x)for x in R[j]]
  for i in range(n):
   if i!=j and R[i][j]!=ZERO:c=qn(R[i][j]);R[i]=[qa(a,qm(c,b))for a,b in zip(R[i],R[j])]
 return[r[n:]for r in R]
def block(A,B,C,D):return[a+b for a,b in zip(A,B)]+[a+b for a,b in zip(C,D)]
def diag(A,B):return block(A,zero(len(A)),zero(len(A)),B)
def upper(A):return block(eye(len(A)),A,zero(len(A)),eye(len(A)))
def lower(A):return block(eye(len(A)),zero(len(A)),A,eye(len(A)))
def controls():
 n=4;I4=eye(n)
 def X(v):return[[ONE if i==j^v else ZERO for j in range(n)]for i in range(n)]
 def C(v,s=1):return add(scale(q(F(1,2),F(s,2)),I4),scale(q(F(1,2),F(-s,2)),X(v)))
 P=[[ONE if i==((j&1)<<1)|((j>>1)&1)else ZERO for j in range(n)]for i in range(n)]
 Q=diag(C(1),C(1));D=diag(C(2),C(2));R=mm(D,Q);K=block(zero(4),P,P,zero(4));I=eye(8);Qi=inv(Q)
 need(mm(K,K)==I and mm(K,R)==mm(R,K),'independent actual small K/R')
 need(mm(K,Q)!=mm(Q,K),'noncommuting control')
 FK=mm(diag(D,D),lower(mm(K,Qi)));BK=mm(diag(D,D),upper(scale(q(-1),mm(Q,K))));F0=mm(diag(D,D),lower(Qi));B0=mm(diag(D,D),upper(scale(q(-1),Q)))
 out=[]
 for lam in [4,98]:
  Cc=scale(q(F(lam,2)),add(I,scale(q(-1),K)));A=add(I,scale(q(-1),Cc));E=mm(K,inv(A));Ei=inv(E)
  need(tr(E)==E and mm(E,R)==mm(R,E)and mm(E,Q)!=mm(Q,E),'symmetric real E, exact R centralization, noncommuting Q')
  H=lambda T:diag(T,prod(Qi,T,Q))
  before=prod(diag(Ei,I),BK,diag(I,Ei));scatter=block(zero(8),scale(q(-1),prod(Ei,R,Cc)),zero(8),zero(8));WB=add(before,scatter)
  need(WB==mm(H(Ei),B0),'actual original-ground backward scatter sign/order')
  Wi=inv(WB);need(mm(Wi,WB)==eye(16),'independent Gaussian-elimination inverse')
  Q2=mm(Q,Q);D2=mm(D,D);J=diag(Q2,I);Jinv=inv(J);WF=prod(diag(D2,D2),J,tr(Wi),Jinv)
  need(WF==mm(H(E),F0),'independent inverse-transpose D2/J boundary')
  badsign=add(before,scale(q(-1),scatter));badacquire=add(before,block(zero(8),scale(q(-1),prod(Ei,R,Cc,Ei)),zero(8),zero(8)))
  need(badsign!=WB and badacquire!=WB,'wrong sign and gathering overwritten E^-1Y rejected')
  need(prod(diag(D2,D2),tr(Wi))!=WF,'omitted J boundary rejected')
  dagger=lambda M:[[ (x[0],-x[1])for x in r]for r in tr(M)]
  need(prod(diag(D2,D2),J,dagger(Wi),Jinv)!=WF,'conjugate transpose is not linear transpose')
  out.append({'lambda':lam,'all_16x16_operator_entries':True,'original_ground_scatter':True,'inverse_transpose_boundary':True,'wrong_sign_wrong_acquire_omitted_J_and_dagger_mutants_rejected':True})
 return out
@lru_cache(None)
def gf_inv(rows):
 n=len(rows);A=[x|(1<<(n+i))for i,x in enumerate(rows)]
 for j in range(n):
  p=next(i for i in range(j,n)if A[i]>>j&1);A[p],A[j]=A[j],A[p]
  for i in range(n):
   if i!=j and A[i]>>j&1:A[i]^=A[j]
 return tuple(x>>n for x in A)
def transform(word,transpose=False):
 O=[]
 for e in reversed(word):
  if e[0]=='P':O.append(['P',list(gf_inv(tuple(e[1])))])
  elif e[0]=='D':O.append(['D',e[1],e[2]if transpose else[(-x)%4 for x in e[2]]])
  elif e[0]=='X':O.append(e)
  else:need(e[0]=='phase','monomial-only definition');O.append(['phase',e[1]if transpose else(-e[1])%4])
 return O
def calculate(package):
 manifest_raw=author_path(package,'FILES.json').read_bytes();need(sha256(manifest_raw).hexdigest()=='2253b65bc0dbccb7c232b555bcf59987082c1babc84b815998f4680de0453496','precision-clarified author package seal');manifest=json.loads(manifest_raw)
 for f,meta in manifest['files'].items():
  raw=author_path(package,f).read_bytes();need(len(raw)==meta['bytes']and sha256(raw).hexdigest()==meta['sha256'],'sealed file '+f)
 files=['PROOF.md','PRECISION-SCOPE.md','README.md','checkpoint.py','owned_e.py','modes.py','n3.py','e_adapter.py','MODES-PROGRAM.json','MODES.json','ROOT-CHECKPOINT-PROGRAM.json.gz','inputs/NORMALIZERS.json','inputs/B-PROGRAM.json.gz','inputs/K-TEMPLATE.json']
 pins={f:sha256(author_path(package,f).read_bytes()).hexdigest()for f in files}
 normal=json.loads((package/'inputs/NORMALIZERS.json').read_bytes());mp=json.loads((package/'MODES-PROGRAM.json').read_bytes());M=[[F(x)for x in r]for r in mp['mode_matrix112x8']];T=[[F(x)for x in r]for r in mp['T112']];Ti=[[F(x)for x in r]for r in mp['T_inverse112']];free=mp['kernel_free_rows']
 need(M==[list(map(F,r))for r in zip(*normal['mode_columns'])],'modal matrix binds actual roots')
 need(all(sum(r[i]*r[j]for r in M)==56*int(i==j)for i,j in product(range(8),repeat=2)),'independent M^TM=56I')
 need(all(T[i][:8]==M[i]for i in range(112)),'first T columns M')
 need(all(sum(M[i][a]*T[i][8+b]for i in range(112))==0 for a in range(8)for b in range(104)),'independent M^TN=0')
 need(all(T[f][8+b]==int(j==b)for j,f in enumerate(free)for b in range(104)),'free N block identity')
 need(Ti[:8]==[[M[i][a]/56 for i in range(112)]for a in range(8)],'top inverse block')
 need(Ti[8:]==[[F(f==j)-sum(M[f][a]*M[j][a]for a in range(8))/56 for j in range(112)]for f in free],'bottom inverse block')
 sectors=[]
 for flags in product([0,1],repeat=3):
  v=[14*x for x in flags];lam=F(v[0]*v[1]+v[0]*v[2]+v[1]*v[2]-v[0]*v[1]*v[2],2);dim=8**sum(flags)*104**(3-sum(flags));sectors.append((flags,lam,dim))
  for signs in product([-1,1],repeat=3):
   if all(not flags[i]or signs[i]==-1 for i in range(3))and lam:need(F(sum(signs)-signs[0]*signs[1]*signs[2],2)==-1,'Kodd=-I on every nonzero C sector')
 need(sum(dim for flags,lam,dim in sectors if lam)==20480,'independent global modal rank')
 orth=mp['global_orthonormal_basis_raw27'];need(len(orth)==25,'25-axis chart');dot=lambda a,b:(a&b).bit_count()&1
 need(all(dot(a,b)==int(i==j)for i,a in enumerate(orth)for j,b in enumerate(orth)),'orthonormal raw27 basis')
 chi=0
 for b in orth:chi^=b
 need(chi==(1<<27)-1,'global characteristic is raw chi27')
 need(all(dot(p['q'],p['q'])==1 and p['q']!=(1<<9)-1 for p in normal['ports']),'all base normone noncharacteristic labels')
 original=json.loads(gzip.decompress((package/'inputs/B-PROGRAM.json.gz').read_bytes()));owned=json.loads(gzip.decompress((package/'ROOT-CHECKPOINT-PROGRAM.json.gz').read_bytes()));need(sha256(canon(original)).hexdigest()=='f6b26f28f2a8f2dcfbf81f98c7ca18f967384b7b61518766494f8e821d5bf56f','actual source B science')
 def tv(v):return[(1<<j)^(v if v>>j&1 else 0)for j in range(25)]
 def matmul(A,B):
  out=[]
  for row in A:
   value=0
   for j,b in enumerate(B):
    if row>>j&1:value^=b
   out.append(value)
  return out
 root_L=0
 for e in original['program']:
  if e[0]!='MONOMIAL'or e[1]!='Y'or e[4]!='inverse_transpose_real_reader_entry':continue
  p=e[2];digits=[p//112**2,(p//112)%112,p%112];raw=sum(normal['ports'][x]['q']<<(9*j)for j,x in enumerate(digits));qp=sum(dot(raw,b)<<j for j,b in enumerate(orth));need(dot(qp,qp)==1 and qp!=(1<<25)-1,'actual root q odd and noncharacteristic')
  if not qp&1:G=tv(1^qp)
  else:
   j=next(j for j in range(1,25)if not(qp>>j&1));G=matmul(tv((1<<j)^qp),tv(1^(1<<j)))
  need(sum((row&1)<<j for j,row in enumerate(G))==qp and all(dot(a,b)==int(i==j)for i,a in enumerate(G)for j,b in enumerate(G)),'actual global normalizer sends e0 to q and is orthogonal')
  alpha=[2*(((row.bit_count()-1)//2)&1)for row in G];expected=[['P',G],['D',[0]*25,alpha]]
  need(original['definitions'][e[3]]==expected,'modal normalizer rule matches actual native B field word and phase');root_L+=1
 need(root_L==512,'all actual root512 physical L words checked')
 words=original['definitions'];versions=Counter();contacts={};reads=Counter();yids=defaultdict(list);xexpected=[];events=owned['events'];newdefs=owned['monomial_definitions'];physical=0
 for index,e in enumerate(original['program']):
  if e[0]=='ADD':
   need(e[1]=='X'and e[3]=='Y','Y sources only');p=e[4];c=(versions[p],e[7]);need(p not in contacts or contacts[p]==c,'single unchanged contact');contacts[p]=c;reads[p]+=1
  elif e[1]=='Y':versions[e[2]]+=1;yids[e[2]].append(index+1)
  if e[0]=='ADD':continue
  ev=events[str(index+1)];need(ev['original_instruction_index']==index and ev['original']==e,'actual event index')
  a,b=ev['inverse_literal'],ev['inverse_transpose_literal']
  if e[0]in['MONOMIAL','BOUNDARY_MONOMIAL']:
   iw=transform(words[e[3]]);need(newdefs[a['word']]==iw,'literal monomial inverse');need(newdefs[b['word']]==transform(iw,True),'literal monomial inverse-transpose')
  else:
   r=e[5];axes=r['child_axes'];before=transform(words[r['after_monomial']]);after=[['X',sum(1<<a for a in axes)]]+transform(words[r['before_monomial']])
   need(a['positive_child_axes']==axes and newdefs[a['before']]==before and newdefs[a['after']]==after,'literal paid inverse includes exact X_mask')
   need(b['positive_child_axes']==axes and newdefs[b['before']]==transform(after,True)and newdefs[b['after']]==transform(before,True),'literal paid inverse-transpose')
  physical+=1
 need(len(contacts)==512 and set(reads.values())=={76},'all actual 512 contacts/38912 reads')
 seen=Counter();snapshot=Counter()
 for e in owned['source_Y_only_pass']:
  p=e[1][1]
  if e[0]=='UNARY':need(e[1][0]=='Y'and e[2]==-yids[p][-1-seen[p]],'reverse Y unary order');seen[p]+=1
  else:need(e[0]=='COPY'and e[1]==['cache',p]and e[2]==['Y',p],'owned contact copy');need(versions[p]-seen[p]==contacts[p][0],'snapshot at actual physical source contact');snapshot[p]+=1
 need(all(seen[p]==versions[p]and snapshot[p]==1 for p in contacts),'one copy and complete Y inverse')
 for index in range(len(original['program'])-1,-1,-1):
  e=original['program'][index]
  if e[0]=='ADD':xexpected.append(['ADD',[e[1],e[2]],['cache',e[4]],-e[5],e[6]])
  elif e[1]=='X':xexpected.append(['UNARY',['X',e[2]],-index-1])
 need(xexpected==owned['target_X_only_pass'],'all reverse X work and ADDs in original reverse order')
 invword=owned['source_Y_only_pass']+xexpected+[['CLEAR',['cache',p]]for p in original['port_order']]
 need(invword==owned['native_inverse_program'],'all contacts clear after last X read')
 tt=[]
 for e in reversed(invword):
  if e[0]=='UNARY':tt.append(['UNARY',e[1],(1 if e[2]>0 else-1)*(abs(e[2])+1000000)])
  elif e[0]=='ADD':tt.append(['ADD',e[2],e[1],e[3],e[4]])
  elif e[0]=='CLEAR':tt.append(['ZERO_OWNED',e[1]])
  else:tt.extend([['ADD',e[2],e[1],1,1],['CLEAR',e[1]]])
 need(tt==owned['native_inverse_transpose_program'],'owned transpose is adjoint accumulation, not inverse CLEAR')
 result={'schema':'E-adapter-AI-peer-static-and-identity-review/v1','status':'PASS_SCOPED_LOCAL_ALGEBRA_AND_STRUCTURED_NATIVE_COMPILATION','reviewer_role':'AI peer, author of two_cube_native fixture only; no claim of independent human/formal-kernel acceptance','reviewed_author_package_seal':sha256(manifest_raw).hexdigest(),'sealed_payload_file_count':len(manifest['files']),'source_package_file_sha256':pins,'small_independent_Qi_controls':controls(),'global_modes':{'M_Gram56I':True,'T_inverse_block_proof':True,'polynomial':'F3(C)=(C1C2+C1C3+C2C3-C1C2C3)/2','nonzero_rank':20480,'Kodd_minus_identity_on_C_modes':True,'global_noncharacteristic_chart':True,'physical_normalizer_rule_matches_actual_root_B':root_L},'actual_native_checkpoint':{'source_contacts':len(contacts),'source_reads':sum(reads.values()),'literal_inverse_and_inverse_transpose_events':physical,'source_inverse_order_and_snapshot_versions':True,'X_reverse_order_and_cache_last_read':True,'owned_transpose_rules':True},'cost_review':'Structured ordinary upper profiles and owned peak v+20480+512 are conservative for the local module. N3 needs3 modules and3 extra code inverses. Mode queries are not productive outputs. Full TM/rounding/routing/storage admission is not supplied.','precision_scope':'Operator norm growth is a finite width-independent field-l2 ABI constant. Per-coordinate fixed-point rounding to field-l2 can require a dimension-dependent precision increment; no uniform componentwise/TM closure is established.','blocking_claims':['Negative Q^-1 B_E D Gaussian admission remains UNKNOWN.','Conditional both-H73 moment is not a constructed supplier or kappa bound.','A public precision claim must retain the field-l2 ABI qualification.'],'theoretical_local_blocker_found':False,'scope':'No author Python code was imported or full package suite repeated. Exact new controls use independently implemented Q(i) matrices; structural native literals, source snapshots and global mode facts are checked independently from serialized inputs.'}
 return result
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=DEFAULT);ap.add_argument('--write',action='store_true');a=ap.parse_args();r=calculate(a.package);f=HERE/'PEER-REVIEW.json'
 if a.write:f.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
 else:need(json.loads(f.read_bytes())==r,'readonly review receipt')
 print(json.dumps({k:r[k]for k in ['status','theoretical_local_blocker_found','actual_native_checkpoint','blocking_claims']},sort_keys=True))
