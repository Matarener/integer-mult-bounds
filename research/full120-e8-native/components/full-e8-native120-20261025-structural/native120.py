"""Full120 E8 n9 native F/B words, including absolute phases.

Phase tools are credited copies of the whole-K PR5464 predecessor. All
240 original main fields are independent; no helper or supplied query is
assumed. Default reads and verifies its semantic payload without writing.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from hashlib import sha256
import argparse,gzip,importlib.util,json,sys
HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
def need(ok,why):
 if not ok:raise ValueError(why)
def canonical(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def basis(rows):
 p={}
 for x in rows:
  for j in sorted(p,reverse=True):
   if x>>j&1:x^=p[j]
  if x:p[x.bit_length()-1]=x
 return tuple(p[j]for j in sorted(p,reverse=True))
def calculate(mid=3):
 need(mid in [3,6],'declared intermediate dimensions')
 pins={'inputs/NORMALIZERS120.json':'0a27b5be30a78c0f418860c65eea2dd4221fc026cf9f2c86b7a8e865ab4d42df','inputs/clifford_exact.py':'2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962','frame_tools.py':'e5b2ea1f60d554b3a285569602360c663ee8b387350424678b3bd0b0b5432bf4','inputs/COVER.json':'151c03c9f527e1bc242e0e6d50bee51f7db3163e4a7ae6a9e54e129328f09f89'}
 for f,p in pins.items():need(sha256((HERE/f).read_bytes()).hexdigest()==p,'source pin '+f)
 ce=load('two_cube_clifford',HERE/'inputs/clifford_exact.py');frames=load('two_cube_frames',HERE/'frame_tools.py');peak=[1];sparse,monomial=frames.install(ce,need,peak)
 normal=json.loads((HERE/'inputs/NORMALIZERS120.json').read_bytes());cover=json.loads((HERE/'inputs/COVER.json').read_bytes());roots=list(zip(*normal['mode_columns']));chosen=[(i,r['ports'])for i,r in enumerate(cover['cover15'])];ports=sum([ps for _,ps in chosen],[]);NPORT=len(ports);need(NPORT==120 and sorted(ports)==list(range(120)),'actual15cube full120 partition');n=9;R=ce.fourier(n);Q=ce.fourier(n,[0]);D=ce.fourier(n,range(1,n));defs={};anchors=[]
 def define(word):
  word=json.loads(json.dumps(word));key=sha256(canonical(word)).hexdigest();defs[key]=word;return key
 def literal(word):
  op=ce.ident(n)
  for e in word:
   if e[0]=='P':a=ce.perm(n,e[1])
   elif e[0]=='D':a=ce.diag(n,e[1],e[2])
   elif e[0]=='X':a=ce.xgate(n,e[1])
   elif e[0]=='phase':a=ce.Op(n,ce.identity(n),[tuple(e)])
   else:need(e[0]=='C','known literal');a=ce.cgate(n,e[1],e[2])
   op=op.then(a)
  return op
 phase_checks=[0]
 def equal(A,B,label):
  need(A.tab==B.tab,label+' signed tableau');need(sparse(A)==sparse(B),label+' absolute zero column');phase_checks[0]+=1
 def path(before,axes,after,expected):
  need(all(e[0]in('P','D','X','phase')for e in before+after),'ordinary-only path wrappers')
  actual=literal(before).then(ce.fourier(n,axes)).then(literal(after));equal(actual,expected,'actual paid path')
  need(ce.rank([x for x,z,p in actual.tab[n:]])==len(axes),'paid rank')
  return {'before_monomial':define(before),'child_axes':list(axes),'after_monomial':define(after),'rank':len(axes)}
 normalizers={p:literal(normal['ports'][p]['K_word'])for p in ports};qs={p:normal['ports'][p]['q']for p in ports}
 for p,L in normalizers.items():equal(L.then(R),R.then(L),'actual old normalizer centralizes full R')
 Krows={};group_records=[];program=[]
 def mono(role,p,word,label):program.append(['MONOMIAL',role,p,define(word),label])
 def paid(role,p,old,new,rec):program.append(['PAID_PATH',role,p,old,new,rec])
 for p in ports:
  own=ce.canonical_frame(n,[qs[p]])
  mono('X',p,monomial(Q.adjoint().then(normalizers[p]).then(own)).circuit,'virtual_Q_source_entry')
  mono('Y',p,normalizers[p].circuit,'original_ground_reader_entry')
 for g,(support,ps)in enumerate(chosen):
  parity={p:side for side,cls in enumerate(cover['cover15'][g]['source_parity_classes'])for p in cls};need(set(parity)==set(ps),'actual graph-derived cover bipartition')
  for r in ps:Krows[r]={s:F(int(r==s))-F(sum(a*b for a,b in zip(roots[r],roots[s])),4)for s in ps};Krows[r]={s:v for s,v in Krows[r].items()if v}
  need(all(len(Krows[r])==4 and all(abs(v)==F(1,2)for v in Krows[r].values())for r in ps),'actual four signed half K rows')
  for parity_bit in [0,1]:
   sources=[p for p in ps if parity[p]==parity_bit];readers=[p for p in ps if parity[p]!=parity_bit];S=list(basis(qs[p]for p in sources));other=basis(qs[p]for p in readers)
   need(len(S)==len(other)==3 and all(not((a&b).bit_count()&1)for a in S for b in other),'actual orthogonal S3 classes')
   original_S3=list(S)
   for v in ce.nullspace(other,n):
    if len(S)==mid:break
    if len(basis(S+[v]))>len(S):S.append(v)
   need(len(S)==mid and all(not((a&b).bit_count()&1)for a in S for b in other),'actual S'+str(mid)+' extension inside all reader q-perps')
   Phi=ce.canonical_frame(n,S);cols=ce.basis_extend(S,n);K=frames.native_K(ce,cols);T,anchor=frames.native_full_conjugate(ce,need,monomial,cols);anchors.append(anchor);chart='cube%d:S%d:%d'%(g,mid,parity_bit)
   entry=path(K.adjoint().circuit,range(mid),K.circuit,Phi);exit=path(K.adjoint().circuit,range(mid,n),T.circuit,Phi.adjoint().then(R))
   for p in sources:
    own=ce.canonical_frame(n,[qs[p]]);flag=[qs[p]]
    for v in S:
     if len(basis(flag+[v]))>len(flag):flag.append(v)
    flags=ce.basis_extend(flag,n);Ks=frames.native_K(ce,flags);small=frames.flag_frame(ce,flags,1);wide=frames.flag_frame(ce,flags,mid)
    before=monomial(own.adjoint().then(small));after=monomial(wide.adjoint().then(Phi));rec=path(before.circuit+Ks.adjoint().circuit,range(1,mid),Ks.circuit+after.circuit,own.adjoint().then(Phi));paid('X',p,'line:'+str(p),chart,rec)
   for p in readers:paid('Y',p,'ground',chart,entry)
   for r in readers:
    for s,v in sorted(Krows[r].items()):need(s in sources,'actual K cross-parity');program.append(['ADD','Y',r,'X',s,v.numerator,v.denominator,chart])
   for p in sources:paid('X',p,chart,'full9',exit)
   for p in readers:
    V=S[:]
    for v in ce.nullspace((qs[p],),n):
     if len(basis(V+[v]))>len(V):V.append(v)
    need(len(V)==8,'qperp8');vc=ce.basis_extend(V,n);Kv=frames.native_K(ce,vc);low=frames.flag_frame(ce,vc,mid);target=frames.flag_frame(ce,vc,8)
    before=monomial(Phi.adjoint().then(low));rec=path(before.circuit+Kv.adjoint().circuit,range(mid,8),Kv.circuit,Phi.adjoint().then(target));paid('Y',p,chart,'qperp8:'+str(p),rec)
    Tv,anchor=frames.native_full_conjugate(ce,need,monomial,vc);anchors.append(anchor)
    wrapper=monomial(Kv.adjoint().then(ce.fourier(n,[8])).then(Tv).then(normalizers[p].adjoint()).then(Q.adjoint()));equal(wrapper,target.adjoint().then(normalizers[p].adjoint()).then(D),'reader output wrapper')
    mono('Y',p,wrapper.circuit,'reader_D_output')
   group_records.append({'cube':g,'source_parity':parity_bit,'sources':sources,'readers':readers,'original_S3':original_S3,'S'+str(mid):S})
 for p in ports:mono('X',p,normalizers[p].adjoint().circuit,'source_D_output')
 def conjugate(word):
  out=[]
  for e in word:
   if e[0]=='D':out.append(['D',e[1],[(-v)%4 for v in e[2]]])
   elif e[0]=='phase':out.append(['phase',(-e[1])%4])
   else:need(e[0]in('P','X'),'conjugated monomial');out.append(e)
  return out
 backward=[]
 for p in ports:backward.append(['MONOMIAL','X',p,define([['X',1]]),'input_Q_minus2'])
 for e in program:
  if e[0]=='MONOMIAL':backward.append(['MONOMIAL',e[1],e[2],define(conjugate(defs[e[3]])),'inverse_transpose_'+e[4]])
  elif e[0]=='ADD':backward.append(['ADD',e[3],e[4],e[1],e[2],-e[5],e[6],'conjugate:'+e[7]])
  else:
   rec=e[5];new={'before_monomial':define(conjugate(defs[rec['before_monomial']])),'child_axes':rec['child_axes'],'after_monomial':define([['X',sum(1<<a for a in rec['child_axes'])]]+conjugate(defs[rec['after_monomial']])),'rank':rec['rank']}
   backward.append(['PAID_PATH',e[1],e[2],'conjugate:'+e[3],'conjugate:'+e[4],new])
 for p in ports:backward.extend([['MONOMIAL','X',p,define([['X',511]]),'output_D2_Q2'],['MONOMIAL','Y',p,define([['X',510]]),'output_D2']])
 def unary(e):
  if e[0]=='MONOMIAL':return literal(defs[e[3]])
  rec=e[5];return literal(defs[rec['before_monomial']]).then(ce.fourier(n,rec['child_axes'])).then(literal(defs[rec['after_monomial']]))
 def replay(word):
  rows={(r,p):{(r,p):(F(1),ce.ident(n))}for r in ['X','Y']for p in ports};paidbill=Counter();ordinary=Counter();charts={(r,p):'line:'+str(p)if r=='X'else'ground'for r,p in rows}
  isback=word is backward
  if isback:charts={f:'conjugate:'+s for f,s in charts.items()}
  for e in word:
   if e[0]=='ADD':
    _,dr,dp,sr,sp,a,b,ch=e;need(charts[dr,dp]==charts[sr,sp]==ch,'same physical ADD chart');ordinary['ADD']+=1
    for key,(c,op)in rows[sr,sp].items():need(key not in rows[dr,dp],'independent source appears once per output');rows[dr,dp][key]=(c*F(a,b),op)
   else:
    f=(e[1],e[2]);U=unary(e);rows[f]={key:(c,op.then(U))for key,(c,op)in rows[f].items()}
    if e[0]=='PAID_PATH':need(charts[f]==e[3],'actual paid entrance');charts[f]=e[4];paidbill[e[5]['rank']]+=1;ordinary.update(x[0]for k in ['before_monomial','after_monomial']for x in defs[e[5][k]])
    else:ordinary.update(x[0]for x in defs[e[3]])
  return rows,dict(sorted(paidbill.items())),dict(sorted(ordinary.items()))
 Frows,fb,fo=replay(program);Brows,bb,bo=replay(backward)
 for p in ports:
  need(set(Frows['X',p])=={('X',p)}and set(Brows['Y',p])=={('Y',p)},'autonomous independent diagonal fields')
  equal(Frows['X',p]['X',p][1],D,'F source D');equal(Brows['Y',p]['Y',p][1],D,'B source D')
  equal(Frows['Y',p]['Y',p][1],D,'F reader D');equal(Brows['X',p]['X',p][1],D,'B reader D')
  need(set(Frows['Y',p])=={('Y',p)}|{('X',s)for s in Krows[p]},'F all original independent columns');need(set(Brows['X',p])=={('X',p)}|{('Y',s)for s in Krows[p]},'B all original independent columns')
  for s,c in Krows[p].items():
   need(Frows['Y',p]['X',s][0]==c and Brows['X',p]['Y',s][0]==-c,'actual K scalar coefficients')
   equal(Frows['Y',p]['X',s][1],Q.adjoint().then(normalizers[s]).then(normalizers[p].adjoint()).then(D),'F raw endpoint')
   equal(Brows['X',p]['Y',s][1],normalizers[s].then(normalizers[p].adjoint()).then(Q).then(D),'B raw endpoint')
 expected_bill=Counter()
 for r in [mid-1,mid,n-mid,n-1-mid]:expected_bill[r]+=NPORT
 need(fb==bb==dict(expected_bill),'complete full120 paid bill')
 M=[roots[p]for p in ports];FC=[[sum(a*b for a,b in zip(M[i],M[j]))//1 for j in range(NPORT)]for i in range(NPORT)]
 FC=[[F(x,4)for x in row]for row in FC];K=[[Krows[p].get(q,F())for q in ports]for p in ports]
 need(all(sum(K[i][j]*K[j][k]for j in range(NPORT))==int(i==k)for i in range(NPORT)for k in range(NPORT)),'full120 scalar involution')
 need(all(sum((int(i==j)-K[i][j])*FC[j][k]for j in range(NPORT))==2*FC[i][k]for i in range(NPORT)for k in range(NPORT)),'BC=2C actual mode range')
 gram=[[sum(row[i]*row[j]for row in M)for j in range(8)]for i in range(8)];need(gram==[[int(i==j)*60 for j in range(8)]for i in range(8)],'actual eight orthogonal mode norms')
 controls={};bad=[list(e)for e in program];i=next(i for i,e in enumerate(bad)if e[0]=='ADD');old=bad[i];bad[i]=list(old);bad[i][5]+=1;mut=replay(bad)[0];controls['actual_K_coefficient_mutation_rejected']=mut[old[1],old[2]][old[3],old[4]][0]!=Frows[old[1],old[2]][old[3],old[4]][0]
 bad=[list(e)for e in program];i=next(i for i,e in enumerate(bad)if e[0]=='ADD');bad[i][-1]='wrong_actual_frame'
 try:replay(bad)
 except ValueError:controls['actual_wrong_ADD_chart_rejected']=True
 first=program[0];oldkey=first[3];defs[oldkey].append(['phase',1]);mut=replay(program)[0]['X',first[2]]['X',first[2]][1];defs[oldkey].pop();controls['same_tableau_ordinary_phase_i_rejected']=mut.tab==D.tab and sparse(mut)!=sparse(D)
 bad=[e for e in program if not(e[0]=='PAID_PATH'and e[1]=='X'and e[2]==ports[0]and e[5]['rank']==n-mid)];mut=replay(bad)[0]['X',ports[0]]['X',ports[0]][1];controls['actual_missing_source_full_exit_rejected']=mut.tab!=D.tab or sparse(mut)!=sparse(D)
 need(len(controls)==4 and all(controls.values()),'all actual native mutation controls')
 payload={'schema':'balanced-S'+str(mid)+'-full120-E8-native-phase-word/v1','axis_dimension':9,'port_order':ports,'groups':group_records,'source_pins':pins,'definitions':defs,'forward_program':program,'backward_program':backward,'literal_scalar_K_rows':{str(r):[[s,v.numerator,v.denominator]for s,v in row.items()]for r,row in Krows.items()},'normalizer_words':{str(p):define(normalizers[p].circuit)for p in ports},'roots_M120x8':M,'mode_gram':gram,'F_C_denominator':4,'native_full_conjugate_anchors':anchors,'original_main_fields':[['X',p]for p in ports]+[['Y',p]for p in ports],'contract':'F_K=diag(D,D)L(C_K Q^-1); B_K=diag(D,D)U(-Q C_K), C_K=diag(L_i^-1) K diag(L_i), Q=C0,D=C_[1,9). All original main fields independent at ground. No external supplied query.','width_contract':'Every one-copy address word tensor-lifts; phase theta becomes i^(f theta). Every owner coefficient is applied once, never raised to f.'}
 payload=json.loads(canonical(payload));report={'schema':'balanced-S'+str(mid)+'-full120-E8-native-phase-receipt/v1','status':'PASS_EXACT_ORIGINAL_MAIN_OPERATOR_COLUMNS_AND_PHASES','axis_dimension':9,'original_main_fields':240,'source_cube_indices':list(range(15)),'port_order':ports,'paid_profile_forward':fb,'paid_profile_backward':bb,'ordinary_forward':fo,'ordinary_backward':bo,'absolute_phase_operator_checks':phase_checks[0],'all_independent_main_operator_entries':1440,'low_rank_sparse_peak':peak[0],'owned_fields':0,'helpers':0,'COPY':0,'CLEAR':0,'mode_rank':8,'mode_eigenvalue_multiplicities':{'15':8},'mutation_controls':controls,'scientific_payload_sha256':sha256(canonical(payload)).hexdigest(),'source_pins':pins,'scope':'Actual phase-complete full120 n9 F_K/B_K native with240 arbitrary independent original fields. It does not implement the paid modal correction, terminal E decoder, whole caller or new kappa.'}
 return json.loads(canonical(report)),payload
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');ap.add_argument('--middle',type=int,choices=[3,6],default=3);a=ap.parse_args();r,p=calculate(a.middle);prefix='NATIVE120'if a.middle==3 else'SATURATED120';rf=HERE/(prefix+'-NATIVE.json');pf=HERE/(prefix+'-NATIVE-PROGRAM.json.gz')
 if a.write:rf.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');pf.write_bytes(gzip.compress(canonical(p),mtime=0))
 else:need(json.loads(rf.read_bytes())==r,'readonly native receipt');need(json.loads(gzip.decompress(pf.read_bytes()))==p,'readonly semantic native program')
 print(json.dumps(r,sort_keys=True))
