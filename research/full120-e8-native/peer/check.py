"""Independent full120 geometry and exact conditional moment review."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from collections import Counter
import json,importlib.util,sys,argparse
D=Path(__file__).resolve().parent
def need(q,s):
 if not q:raise ValueError(s)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def rank(rows):
 p={}
 for v in rows:
  while v:
   j=v.bit_length()-1
   if j not in p:p[j]=v;break
   v^=p[j]
 return len(p)
def power(n):
 # ln(z) = 2 atanh((z-1)/(z+1)), positive series with a geometric tail.
 def log(t):
  v=F();x=t
  for j in range(24):v+=2*x/(2*j+1);x*=t*t
  return v,v+2*x/(49*(1-t*t))
 a=F(605457647,200000000000);k=n.bit_length()-1;l2,u2=log(F(1,3));l,u=log(F(n-2**k,n+2**k));l=(l+k*l2)*a;u=(u+k*u2)*a
 need(0<=l<=u<1,'exp domain')
 def partial(x):
  term=total=F(1)
  for j in range(1,19):term*=x/j;total+=term
  return total,term
 lo,_=partial(l);hi,t=partial(u);tail=t*u/19/(1-u/20)
 return F(n)/(hi+tail),F(n)/lo
def rounded(interval):
 d=10**18;l,u=interval;return [str(F((l*d).__floor__(),d)),str(F((u*d).__ceil__(),d))]
def budget(v,h):
 l,u=power(73);l*=F(2,3);u*=F(2,3)
 for r,c in [(8,F(1)),(9,F(1)),(15,F(1)),(16,F(1)),(25,F(h,v))]:
  a,b=power(r);l-=c*b;u-=c*a
 need(l>0,'conditional profile margin')
 per_mode=(3*l*v/h,3*u*v/h)
 allowances={}
 for r in [1,4,8]:
  a,b=power(r);q=(per_mode[0]/b,per_mode[1]/a);k=q[0].__floor__();need(q[1]<k+1,'strict integer allowance unique');allowances[str(r)]=k
 return {'V':v,'h':h,'h_over_V':str(F(h,v)),'conditional_margin_per_port_per_call':rounded((l,u)),'whole_N3_margin_per_mode_H1':rounded(per_mode),'integer_paid_allowance_per_mode':allowances,'paid_decoders_constructed':False}
def calculate():
 inputs={str(p.relative_to(D/'inputs')):sha256(p.read_bytes()).hexdigest()for p in(D/'inputs').iterdir()if p.is_file()}
 need(inputs['NORMALIZERS112.json']=='ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da','old geometry pin')
 need(inputs['clifford_exact.py']=='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','CE pin')
 old=json.loads((D/'inputs/NORMALIZERS112.json').read_bytes());cover=json.loads((D/'inputs/COVER.json').read_bytes());normal=json.loads((D/'inputs/NORMALIZERS120.json').read_bytes())
 M=list(map(list,zip(*old['mode_columns'])))+[[2*int(i==j)for j in range(8)]for i in range(8)]
 need(cover['root_M120x8']==M and list(map(list,zip(*normal['mode_columns'])))==M,'all original roots plus eight actual axis roots')
 qs=[z['q']for z in normal['ports']];need(qs==cover['q120']and len(set(qs))==120 and all(q.bit_count()%2 and q!=511 for q in qs),'all actual admissible distinct labels')
 gram=[[sum(m[i]*m[j]for m in M)for j in range(8)]for i in range(8)];need(gram==[[60*int(i==j)for j in range(8)]for i in range(8)],'full tight frame60I')
 dot=lambda a,b:(a&b).bit_count()%2
 C=[[F(sum(x*y for x,y in zip(a,b)),4)for b in M]for a in M]
 A=[[F(i==j)-C[i][j]for j in range(120)]for i in range(120)]
 need(all(bool(A[i][j])==(not dot(qs[i],qs[j]))for i in range(120)for j in range(120)),'all and only native full-A support')
 need(set(sum(bool(x)for x in row)for row in A)=={56},'all row degree56')
 groups=cover['cover15'];flat=[p for g in groups for p in g['ports']];need(sorted(flat)==list(range(120))and len(groups)==15,'exact cover')
 K=[[F()for j in range(120)]for i in range(120)];class_records=[]
 for g in groups:
  ps=g['ports'];P,Q=g['source_parity_classes'];need(len(ps)==8 and sorted(P+Q)==sorted(ps)and len(P)==len(Q)==4,'4+4 partition')
  need(rank(qs[i]for i in P)==rank(qs[i]for i in Q)==3 and rank(qs[i]for i in ps)==4,'actual affine cube label spans')
  need(all(dot(qs[i],qs[j])==0 for i in P for j in Q),'exact cross-class orthogonality')
  for i in ps:
   for j in ps:K[i][j]=A[i][j]
   neigh=[j for j in ps if K[i][j]];need(len(neigh)==4 and all(abs(K[i][j])==F(1,2)for j in neigh),'four actual signed halves')
  need(all(sum(K[i][j]*K[j][k]for j in ps)==int(i==k)for i in ps for k in ps),'cube K involution')
  class_records.append({'ports':ps,'source_q_span':3,'reader_q_span':3,'all_cube_q_span':4})
 need(all(sum(K[i][j]*M[j][a]for j in range(120))==-M[i][a]for i in range(120)for a in range(8)),'K M=-M')
 # This proves KC=CK=-C and C^2=15C using the explicit M factorization.
 ce=load('full120_peer_CE',D/'inputs/clifford_exact.py');ao=load('full120_peer_affine',D/'inputs/affine_oracle.py');R=ce.fourier(9);Q=ce.fourier(9,[0]);newchecks=0
 for p in range(112,120):
  U=ce.ident(9)
  for e in normal['ports'][p]['K_word']:
   if e[0]=='P':V=ce.perm(9,e[1])
   elif e[0]=='D':V=ce.diag(9,e[1],e[2])
   elif e[0]=='X':V=ce.xgate(9,e[1])
   else:need(e[0]=='phase','new normalizer ordinary only');V=ce.Op(9,ce.identity(9),[tuple(e)])
   U=U.then(V)
  need(U.tab[0][0]==qs[p]and U.tab[0][1]==0,'new exact signed axis image')
  need(ao.canonicalize(U.then(R))==ao.canonicalize(R.then(U)),'independent affine fullR absolute phase commutation')
  newchecks+=1
 h=3*8**2*112+8**3;need(h==22016,'actual triple spectral multiplicities')
 new=budget(120**3,h);previous=budget(112**3,20480)
 need(new['integer_paid_allowance_per_mode']=={'1':21,'4':5,'8':2}and previous['integer_paid_allowance_per_mode']=={'1':9,'4':2,'8':1},'strict new conditional allowances')
 return {'status':'PASS_INDEPENDENT_FULL120_COVER_GEOMETRY_PHASE_AND_CONDITIONAL_BUDGET','input_sha256':inputs,'full120_original_roots_and_new8':True,'exact_cover_cubes':class_records,'new8_normalizer_absolute_phase_checks':newchecks,'C_rank':8,'C_eigenvalue':15,'K_squared_I':True,'KM_minus_M':True,'global_C_spectrum':{'0':120**3-h,'225/2':21504,'-1350':512},'previous112':previous,'full120':new,'relative_query_density_reduction':str(F(2126,16875)),'scope':'Geometry and conditional invoice only. Full phase-native main program, actual E caller and negative paid decoder, precision/compiler/outer and adoption are not supplied by this checker.','new_kappa':False,'scientific_admission':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=calculate();r=json.loads(canon(r));f=D/'RESULT.json'
 if a.write:f.write_bytes(canon(r))
 else:need(json.loads(f.read_bytes())==r,'read-only scientific payload')
 print(json.dumps({'status':r['status'],'payload_sha256':sha256(canon(r)).hexdigest(),'wholeN3_H1_allowance_per_mode':21,'native_program_replayed':False,'new_kappa':False},sort_keys=True))
