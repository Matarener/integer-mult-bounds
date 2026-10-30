"""Actual E8 Weyl lifts and phase-complete ordinary normalizers for120 ports."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import argparse,importlib.util,json,sys
HERE=Path(__file__).resolve().parent
CEP='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962'
def need(a,b):
 if not a:raise ValueError(b)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def calculate():
 need(sha256((HERE/'inputs/clifford_exact.py').read_bytes()).hexdigest()==CEP,'exact Clifford compiler pin');ce=load('full120_ce',HERE/'inputs/clifford_exact.py');cover=json.loads((HERE/'COVER.json').read_bytes());old=json.loads((HERE/'inputs/NORMALIZERS112.json').read_bytes());q=cover['q120'];M=cover['root_M120x8'];n=9;c=511;R=ce.fourier(n);Q=ce.fourier(n,[0]);D=ce.fourier(n,range(1,n));ref=[];checks=0
 for ri,qr in enumerate(q):
  u=qr^c;G=tuple((1<<j)^(u if u>>j&1 else 0)for j in range(n));P=ce.perm(n,G)
  need(u.bit_count()%4==2,'all root Weyl transvection weights2mod4')
  for j,qs in enumerate(q):
   need(ce.mv(G,qs)==q[cover['reflection_permutations'][ri][j]],'binary Weyl action equals actual realroot reflection')
  need(all((ce.mv(G,x).bit_count()-x.bit_count())%4==0 for x in range(512)),'actual all-address weight modulo4')
  need(P.then(R).tab==R.then(P).tab and P.then(R).zero_state()==R.then(P).zero_state(),'Weyl P exact signed tableau and absolute phase commutation')
  ref.append(G);checks+=1
 def literal(word):
  U=ce.ident(n)
  for e in word:
   if e[0]=='P':V=ce.perm(n,e[1])
   elif e[0]=='D':V=ce.diag(n,e[1],e[2])
   elif e[0]=='X':V=ce.xgate(n,e[1])
   else:need(e[0]=='phase','ordinary literal only');V=ce.Op(n,ce.identity(n),[tuple(e)])
   U=U.then(V)
  return U
 ports=[dict(p)for p in old['ports']];new=[]
 for p in range(112,120):
  found=next((j,r)for j in range(112)for r,perm in enumerate(cover['reflection_permutations'])if perm[j]==p)
  j,r=found;word=old['ports'][j]['K_word']+[['P',list(ref[r])]];L=literal(word)
  need(ce.mv(ref[r],q[j])==q[p],'actual newly reached rootlabel')
  need(L.then(R).tab==R.then(L).tab and L.then(R).zero_state()==R.then(L).zero_state(),'actual new Li fullR exactcommutation')
  need(L.tab[0][0]==q[p]and L.tab[0][1]==0,'actual Li maps central X translation to q')
  own=ce.canonical_frame(n,[q[p]]);hyper=ce.canonical_frame(n,ce.nullspace([q[p]],n))
  maps={'input_X':Q.adjoint().then(L).then(own),'input_Y':L,'output_X':L.adjoint(),'output_Y':hyper.adjoint().then(L.adjoint()).then(D)}
  compiled={}
  for name,U in maps.items():
   need(ce.rank([x for x,z,t in U.tab[n:]])==0,'actual newly normalized wrapper ordinary')
   out,recipe=ce.monomial(U);need(out.tab==U.tab and out.zero_state()==U.zero_state(),'actual wrapper full signed tableau and absolute phase')
   need(all(e[0]in ['P','D','X','phase']for e in out.circuit),'no hidden Gaussian wrapper')
   compiled[name]={'word':out.circuit,'recipe':recipe}
  rec={'port':p,'q':q[p],'K_word':word,'origin_old_port':j,'weyl_root_reflection':r,'weyl_orthogonal_matrix_rows':ref[r],'compiled_wrappers':compiled}
  ports.append(rec);new.append(rec)
 # Independent actual full scalar K,C proof after the new cube recoding.
 K=[{}for i in range(120)]
 for block in cover['cover15']:
  for i in block['ports']:
   for j in block['ports']:
    a=F(i==j)-F(sum(x*y for x,y in zip(M[i],M[j])),4)
    if a:K[i][j]=a
 C=[[F(sum(x*y for x,y in zip(a,b)),4)for b in M]for a in M]
 need(all(sum(co*F(M[j][a])for j,co in K[i].items())==-M[i][a]for i,a in product(range(120),range(8))),'actual global K M=-M')
 need(all(sum(co*K[j].get(k,F())for j,co in K[i].items())==int(i==k)for i,k in product(range(120),repeat=2)),'actual full120 K squaredI')
 need(all(sum(co*C[j][k]for j,co in K[i].items())==-C[i][k]for i,k in product(range(120),repeat=2)),'all14400 actual K C=-C blocks')
 Ei=[[K[i].get(j,F())+C[i][j]for j in range(120)]for i in range(120)];E=[[K[i].get(j,F())+C[i][j]/14 for j in range(120)]for i in range(120)]
 # Efficient identity follows exactly from the independently checked KC,
 # K^2 and C^2=15C; verify the latter on all blocks using M^TM=60I.
 need(all(F(sum(M[i][a]*60*M[j][a]for a in range(8)),16)==15*C[i][j]for i,j in product(range(120),repeat=2)),'actual allblocks C squared15C')
 payload={'schema':'full120-actual-Weyl-lift-and-normalizers/v1','status':'PASS_FULL120_WEYL_PHASE_LIFTS_AND_NEW8_NORMALIZERS','mode_columns':[list(x)for x in zip(*M)],'ports':ports,'new8':new,'weyl_permutation_rows':ref,'cover15':cover['cover15'],'scalar_K_rows':[[[j,str(a)]for j,a in sorted(row.items())]for row in K],'scalar_C':'MM^T/4','scalar_E':'K+C/14','scalar_E_inverse':'K+C','identity':'K^2=I, KC=CK=-C, C^2=15C; (K+C/14)(K+C)=I','finite_checks':{'all_reflections':120,'weight_congruence_addresses':120*512,'actual_q_actions':120**2,'phase_complete_new8_normalizers':8,'phase_complete_new8_wrappers':32,'global_KM_entries':120*8,'global_KC_entries':120**2,'global_K_squared_entries':120**2},'source_pins':{'NORMALIZERS112':sha256((HERE/'inputs/NORMALIZERS112.json').read_bytes()).hexdigest(),'clifford':CEP,'COVER_semantic':sha256(canon(cover)).hexdigest()},'phase_scope':'Every Weyl lift is an actual ordinary binary P matrix, weight-preserving modulo4, hence fullR commutation including absolute phase for every positive column width. Old Li is followed chronologically by P_Weyl; new8 output/input wrappers are compiled literal P/D/X/phase only. Owner scalar coefficients are applied once outside address tensor powers.','scope':'Actual full120 cube geometry and compatible normalizer/frame data. This does not claim a full native phase word, terminal E decoder, productive caller, new kappa or scientific adoption.','new_kappa':False}
 return json.loads(canon(payload))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();d=calculate();p=HERE/'NORMALIZERS120.json'
 if a.write:p.write_bytes(canon(d))
 else:need(json.loads(p.read_bytes())==d,'read-only new120 normalizer receipt')
 print(json.dumps({k:d[k]for k in ['status','finite_checks','scalar_E','scalar_E_inverse','new_kappa']},sort_keys=True))
