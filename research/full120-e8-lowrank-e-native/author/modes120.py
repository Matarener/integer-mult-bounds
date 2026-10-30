"""Exact full120 modal recoder, physical E code, and structured odd3 invoice.

The ordinary owner matrices act once on fields. Address words alone tensor
lift with positive field width. No all-family dense matrix is materialized.
"""
import argparse,gzip,hashlib,json,sys
from collections import Counter
from fractions import Fraction as F
from itertools import product
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'inputs'
KERNEL_PIN='0b526f1a38a73a82ae66e1b0182ed2fa8c14e16d703cd38fff4dc491d3b7c15b'
NATIVE_PIN='87d7cad7133ed0a2950b1d4fa2397e20e3c7bcedb90db95a15130aa03da543ae'
ROOT_PIN='1aeba5ae2276ff58e24ed9ca84f08830c0bb7321432bc74e42472f0029bfb1c2'
def need(q,s):
 if not q:raise ValueError(s)
def canonical(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def loadgz(name,pin):
 p=json.loads(gzip.decompress((SOURCE/name).read_bytes()));need(hashlib.sha256(canonical(p)).hexdigest()==pin,'pinned '+name);return p
def eye(n):return [[F(i==j)for j in range(n)]for i in range(n)]
def mm(A,B):
 out=[[F()for _ in B[0]]for _ in A]
 for i,r in enumerate(A):
  for k,a in enumerate(r):
   if a:
    for j,b in enumerate(B[k]):
     if b:out[i][j]+=a*b
 return out
def rowword(word,n=120):
 A=eye(n)
 for e in word:
  if e[0]=='SWAP':A[e[1]],A[e[2]]=A[e[2]],A[e[1]]
  elif e[0]=='SCALE':A[e[1]]=[F(e[2],e[3])*x for x in A[e[1]]]
  else:
   need(e[0]=='ADD','owner elementary opcode');i,j=e[1:3];q=F(e[3],e[4]);A[i]=[x+q*y for x,y in zip(A[i],A[j])]
 return A
def transword(word):
 return [[e[0],e[2],e[1],*e[3:]]if e[0]=='ADD'else e for e in reversed(word)]
def scalar_K(native):
 K=[[F()for _ in range(120)]for _ in range(120)]
 for i,r in native['literal_scalar_K_rows'].items():
  for j,num,den in r:K[int(i)][int(j)]=F(num,den)
 return K
def countword(w):return dict(sorted(Counter(e[0]for e in w).items()))
def calculate():
 kernel=loadgz('KERNEL-PROGRAM.json.gz',KERNEL_PIN)
 native=loadgz('NATIVE120-NATIVE-PROGRAM.json.gz',NATIVE_PIN)
 root=loadgz('K-PROGRAM.json.gz',ROOT_PIN)
 T=[[F(x)for x in r]for r in kernel['T120']];Ti=[[F(x)for x in r]for r in kernel['T_inverse120']]
 to=kernel['to_modal_kernel_word'];fr=kernel['from_modal_kernel_word']
 need(rowword(to)==Ti and rowword(fr)==T,'both actual elementary words independently replayed')
 need(mm(T,Ti)==eye(120)and mm(Ti,T)==eye(120),'both all14400 exact inverse entries')
 M=[[F(x)for x in r]for r in kernel['root_M120x8']]
 C=[[sum(x*y for x,y in zip(r,s))/4 for s in M]for r in M]
 need(all(T[i][:8]==M[i]for i in range(120)),'first8 columns are actual M')
 need(all(Ti[a][i]==M[i][a]/60 for a in range(8)for i in range(120)),'modal analysis is actual M^T/60')
 need(all(sum(M[i][a]*T[i][b]for i in range(120))==0 for a in range(8)for b in range(8,120)),'remaining112 columns in actual kernel')
 K=scalar_K(native);need(mm(K,K)==eye(120),'actual native K^2=I')
 need(mm(K,M)==[[-x for x in r]for r in M],'actual native K M=-M')
 need(mm(K,C)==[[-x for x in r]for r in C]and mm(C,K)==[[-x for x in r]for r in C],'both K C=-C')
 E=[[K[i][j]+C[i][j]/14 for j in range(120)]for i in range(120)]
 Ei=[[K[i][j]+C[i][j]for j in range(120)]for i in range(120)]
 need(mm(E,Ei)==eye(120)and mm(Ei,E)==eye(120),'actual E and inverse all14400 entries')
 # Code evaluation means T^-1, A scale, T, then K, with scalar coefficients
 # once. The negative A-inverse modal scale must not be lost.
 def code(sc):
  U=[[T[i][j]*(sc if j<8 else 1)for j in range(120)]for i in range(120)]
  return mm(K,mm(U,Ti))
 need(code(F(-1,14))==E and code(F(-14))==Ei,'literal modal scales implement E and E inverse')
 wrong=code(F(1,14));need(wrong!=E,'wrong inverse modal sign rejected')
 need(mm(K,Ei)==[[F(i==j)-C[i][j]for j in range(120)]for i in range(120)],'K Ei+C=I exact')
 need(mm(C,Ei)==[[14*x for x in r]for r in C],'post-precode source is not original source')
 need(mm(C,Ei)!=C,'late original-ground modal gather rejected')
 # U25 is the one common physical chart used by the actual whole native.
 template=json.loads((SOURCE/'K-TEMPLATE.json').read_bytes());orth=template['orthonormal_basis_raw27']
 dot=lambda x,y:(x&y).bit_count()&1
 need(len(orth)==25 and all(dot(x,y)==int(i==j)for i,x in enumerate(orth)for j,y in enumerate(orth)),'actual U25 orthonormal chart')
 need(all(len({((x>>(9*j))&511).bit_count()%2 for j in range(3)})==1 for x in orth),'common equal-block-parity U25')
 sectors=[];h=0
 for flags in product([0,1],repeat=3):
  a=sum(flags);dim=8**a*112**(3-a);lam=F(225,2)if a==2 else F(-1350)if a==3 else F()
  if lam:h+=dim
  sectors.append({'modal_axis_flags':list(flags),'dimension':dim,'C_eigenvalue':str(lam),'A_scale':str(1-lam),'A_inverse_scale':str(1/(1-lam))})
 need(h==22016,'global actual rank22016')
 # Scalar Kodd majority formula on eight sign sectors. On every active C
 # sector at least two factors are modal, and hence have K sign minus.
 for signs in product([-1,1],repeat=3):
  majority=F(sum(signs)-signs[0]*signs[1]*signs[2],2)
  need(majority in[-1,1],'Kodd involution on all eigenspaces')
  if signs.count(-1)>=2:need(majority==-1,'Kodd=-I on C support')
 counts=countword(to);need(counts==countword(fr)=={'ADD':7042,'SCALE':84,'SWAP':91},'actual kernel elementary tariff')
 def invoice(k,v,rank,rowterms,scratch,n):
  b=k*v//120
  code={'ADD':2*b*counts['ADD']+rowterms*v,'SCALE':2*b*counts['SCALE']+rank,'SWAP':2*b*counts['SWAP']+v,'physical_L_field_map':2*v,'OWN_ZERO':v,'CLEAR':v,'peak_scratch':scratch}
  query={'ADD':4*b*counts['ADD']+rank,'SCALE':4*b*counts['SCALE'],'SWAP':4*b*counts['SWAP'],'physical_L_field_map':4*v,'COPY':rank,'CLEAR':rank,'paid':{str(n):rank}}
  upper=dict(query);upper['ADD']+=rank;upper['OWN_ZERO']=rank;upper['CLEAR']=2*rank
  return {'axis_word_batches_per_direction':b,'ordinary_code_E_or_inverse':code,'original_ground_query_plus_scatter':query,'query_or_transpose_upper':upper,'owned_inverse_peak_upper':v+rank+scratch}
 invoices={'base120':invoice(1,120,8,4,8,9),'odd3':invoice(3,120**3,h,76,512,25)}
 payload={'schema':'full120-positive-E-structured-constructor/v1','kernel_science_sha256':KERNEL_PIN,'native120_science_sha256':NATIVE_PIN,'native512_science_sha256':ROOT_PIN,'base_modal_scale':{'E':'-1/14','E_inverse':'-14'},'odd3_sectors':sectors,'base_owner_recoder':{'to':'inputs/KERNEL-PROGRAM.json.gz:to_modal_kernel_word','from':'inputs/KERNEL-PROGRAM.json.gz:from_modal_kernel_word'},'global_owner_recoder':{'ambient':25,'selector_shape':[120,120,120],'physical_normalizers':'Actual K-TEMPLATE U25 chart and q tuple; ordinary exact signed Clifford L_i from actual K native constructor. These address monomials commute with R25 with phase; no claim they commute Q or D separately.','orthonormal_basis_raw27':orth,'loop':'For axis a=0,1,2 and lexicographic other selector coordinates in0..119 apply the emitted120-field word on that axis. Restore in reverse axis order using the inverse word.','scalar_coefficients':'Each owner coefficient acts once; only address monomials tensor lift with field width.'},'code_recipe':['Apply each actual physical L_i to its field.','Apply to-modal word in place on each selector axis.','SCALE active sectors by A_inverse_scale for E or A_scale for E_inverse.','Restore from-modal words in reverse axis order.','Apply actual scalar K (base8cube/odd3 512cube) into owned zero output scratch, read all inputs, SWAP outputs into mains, CLEAR old mains from scratch; reuse8/512 fields.','Apply L_i inverse.'],'query_recipe':['On unchanged original ground Y apply L_i then to-modal selector words.','COPY every active coordinate into its owned mode; restore original Y exactly via inverse recoder and L_i inverse.','Apply one full positive R9 or R25 to each owned mode.','After native B but before postX(E_inverse), apply L_i and to-modal words to X, ADD -lambda times each retained mode at its active coordinate, then restore and L_i inverse.','CLEAR modes only after their final scatter. In inverse schedule original Y is first acquired using the actual source-contact inverse, before query.'],'physical_operator_claim':'C_phys=L^-1 Cscalar L commutes R. E=K(I-C)^-1, E_inverse=K+C. The emitted ordinary code uses no Q-conjugation assumption. Backward output is H(E_inverse)B0, forward obtained from owned inverse transpose is H(E)F0. H(T)=diag(T,Q^-1 T Q).','global_scalar_C':'(C1 C2+C1 C3+C2 C3-C1 C2 C3)/2; factors act on distinct owner selector axes.','global_scalar_K':'(K1+K2+K3-K1 K2 K3)/2; actual76-entry rows, row-l1=7.','invoices':invoices}
 result={'schema':'full120-E-modal-structured-proof/v1','status':'PASS_EXPLICIT_POSITIVE_E_CONSTRUCTOR','base_E_and_inverse_all14400_entries':True,'base_recoder_replay_entries':28800,'base_K_C_compatibility':True,'original_ground_timing_control_rejected':True,'modal_inverse_sign_control_rejected':True,'global_dimension':120**3,'global_nonzero_modes':h,'global_C_eigenvalues':['225/2','-1350'],'global_E_eigenvalues_on_active':['2/223','-1/1351'],'query_paid_per_local_module':{'25':h},'native_paid_per_local_module':{str(r):120**3 for r in[8,9,15,16]},'base_local_module_paid':{str(r):120 for r in[2,3,5,6]}|{'9':8},'invoices':invoices,'kernel_science_sha256':KERNEL_PIN,'scientific_payload_sha256':hashlib.sha256(canonical(payload)).hexdigest(),'negative_terminal':'UNKNOWN','whole_caller_or_new_kappa':False,'scope':'Actual base native and512 native template pins, exact scalar recoder/mode proof, owned source checkpoint and small noncommuting-Q fulloperator fixture jointly compose this structured constructor. No1,728,000-by1,728,000 matrix or full3375 native phase stream is claimed expanded. Positive E code/query only; no ordinary negative decoder or formal supplier admission.'}
 return result,payload
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r,p=calculate()
 for name,obj in [('MODES120.json',r),('MODES120-PROGRAM.json',p)]:
  if a.write:(HERE/name).write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')
  else:need(json.loads((HERE/name).read_bytes())==obj,'read-only '+name)
 print(json.dumps(r,sort_keys=True))
