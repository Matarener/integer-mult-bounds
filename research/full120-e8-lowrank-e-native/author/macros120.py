"""Executable phase-complete base120 E macros with owned inverse transpose.

This emits literal finite primitive lists for all240 base main fields. Its
proof is compositional: actual native phase object, exact owner recoder,
actual source-contact compiler, and the displayed noncommuting block algebra.
The1,728,000-owner extension is the separately specified structured loop.
"""
import argparse,gzip,hashlib,importlib.util,json,sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('macros120_modes',HERE/'modes120.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
spec=importlib.util.spec_from_file_location('macros120_checkpoint',HERE/'checkpoint120.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
need=m.need;canonical=m.canonical
def build():
 native=m.loadgz('NATIVE120-NATIVE-PROGRAM.json.gz',m.NATIVE_PIN)
 kernel=m.loadgz('KERNEL-PROGRAM.json.gz',m.KERNEL_PIN)
 cache=json.loads(gzip.decompress((HERE/'BASE120-CHECKPOINT-PROGRAM.json.gz').read_bytes()))
 receipt=json.loads((HERE/'BASE120-CHECKPOINT.json').read_bytes())
 need(hashlib.sha256(canonical(cache)).hexdigest()==receipt['scientific_payload_sha256'],'actual base source-contact payload pin')
 need(cache['source_B_canonical_sha256']==m.NATIVE_PIN,'same actual native source-contact object')
 ports=list(range(120));main=[(b,p)for b in['X','Y']for p in ports];defs={}
 def wordid(w):
  key=hashlib.sha256(canonical(w)).hexdigest();defs[key]=w;return key
 def unary(field,word,label):
  paid=[len(e[1])for e in word if e[0]=='C'];need(len(paid)<=1,'one positive child per unary event')
  return ['U',field,wordid(word),paid[0]if paid else 0,label]
 def mono(bank,p,inverse=False):
  w=native['definitions'][native['normalizer_words'][str(p)]]
  need(all(q[0]in['P','X']or(q[0]=='D'and all(v%2==0 for v in q[2]))or(q[0]=='phase'and q[1]%2==0)for q in w),'actual physical normalizers are real signed permutations')
  return unary([bank,p],c.mono_transform(w)if inverse else w,'physical_L_inverse'if inverse else'physical_L')
 def recoder(bank,direction):
  out=[]
  for e in kernel['to_modal_kernel_word'if direction=='to'else'from_modal_kernel_word']:
   if e[0]=='ADD':out.append(['ADD',[bank,e[1]],[bank,e[2]],e[3],e[4]])
   elif e[0]=='SWAP':out.append(['SWAP',[bank,e[1]],[bank,e[2]]])
   else:out.append(['SCALE',[bank,e[1]],e[2],e[3]])
  return out
 def chart(bank,direction):return [mono(bank,p,direction=='out')for p in ports]
 def code(bank,inverse=False):
  # E=K A^-1; Ei=K A. The active scale is negative in both base cases.
  scale=F(-14)if inverse else F(-1,14)
  out=chart(bank,'in')+recoder(bank,'to')+[['SCALE',[bank,i],scale.numerator,scale.denominator]for i in range(8)]+recoder(bank,'from')
  cubes={group['cube']:sorted(group['sources']+group['readers'])for group in native['groups']}
  need(len(cubes)==15,'all15 actual native cubes')
  for g in cubes.values():
   need(len(g)==8,'explicit native eight-root cube partition')
   out.extend([['OWN_ZERO',['kscratch',j]]for j in range(8)])
   for j,p in enumerate(g):
    out.extend([['ADD',['kscratch',j],[bank,s],num,den]for s,num,den in native['literal_scalar_K_rows'][str(p)]])
   out.extend([['SWAP',[bank,p],['kscratch',j]]for j,p in enumerate(g)])
   out.extend([['CLEAR',['kscratch',j]]for j in range(8)])
  return out+chart(bank,'out')
 def gather():
  return chart('Y','in')+recoder('Y','to')+[['COPY',['mode',a],['Y',a]]for a in range(8)]+recoder('Y','from')+chart('Y','out')+[unary(['mode',a],[['C',list(range(9))]],'original_ground_full_R9_query')for a in range(8)]
 def scatter(sign):
  return chart('X','in')+recoder('X','to')+[['ADD',['X',a],['mode',a],15*sign,1]for a in range(8)]+recoder('X','from')+chart('X','out')
 def original_native():
  out=[]
  for e in native['backward_program']:
   if e[0]=='ADD':out.append(['ADD',[e[1],e[2]],[e[3],e[4]],e[5],e[6]])
   elif e[0]=='PAID_PATH':
    r=e[5];w=native['definitions'][r['before_monomial']]+[['C',r['child_axes']]]+native['definitions'][r['after_monomial']];out.append(unary([e[1],e[2]],w,'actual_native_'+e[0]))
   else:out.append(unary([e[1],e[2]],native['definitions'][e[3]],'actual_native_'+e[0]))
  return out
 def checkpoint_pass(name):
  out=[]
  for e in cache[name]:
   if e[0]!='UNARY':out.append(e);continue
   r=cache['events'][str(abs(e[2]))]['inverse_literal'];need(e[2]<0,'inverse source-contact event orientation')
   if r['kind']=='MONOMIAL':w=cache['monomial_definitions'][r['word']]
   else:w=cache['monomial_definitions'][r['before']]+[['C',r['positive_child_axes']]]+cache['monomial_definitions'][r['after']]
   out.append(unary(e[1],w,'actual_source_checkpoint_'+name))
  return out
 clear_modes=[['CLEAR',['mode',a]]for a in range(8)]
 code_ex=code('X');code_eix=code('X',True)
 back=gather()+code('Y',True)+original_native()+scatter(-1)+code_eix+clear_modes
 inverse=code_ex+checkpoint_pass('source_Y_only_pass')+code('Y')+gather()+scatter(1)+clear_modes+checkpoint_pass('target_X_only_pass')+[['CLEAR',['cache',p]]for p in cache['ports']]
 def transpose(program):
  out=[]
  for e in reversed(program):
   op=e[0]
   if op=='ADD':out.append(['ADD',e[2],e[1],e[3],e[4]])
   elif op=='COPY':out.extend([['ADD',e[2],e[1],1,1],['CLEAR',e[1]]])
   elif op=='CLEAR':out.append(['OWN_ZERO',e[1]])
   elif op=='OWN_ZERO':out.append(['CLEAR',e[1]])
   elif op in['SWAP','SCALE']:out.append(e)
   else:
    need(op=='U','linear transpose primitive opcode')
    # P^T=P^-1, D^T=D, X^T=X, C^T=C, scalar phase unchanged.
    w=[]
    for q in reversed(defs[e[2]]):
     w.append(['P',c.gf_inv(q[1])]if q[0]=='P'else q)
    out.append(unary(e[1],w,'linear_transpose:'+e[4]))
  return out
 tr=transpose(inverse)
 # Boundary: diag(D²,D²) J inverse^T J^-1, J=diag(Q²,I).
 forward=[unary(['X',p],[['X',1]],'input_Q_minus2')for p in ports]+tr+[unary(['X',p],[['X',511]],'output_Dsquare_Qsquare')for p in ports]+[unary(['Y',p],[['X',510]],'output_Dsquare')for p in ports]
 payload={'schema':'literal-full120-base-positive-E-owned-macros/v1','native_science_sha256':m.NATIVE_PIN,'kernel_science_sha256':m.KERNEL_PIN,'actual_source_checkpoint_sha256':receipt['scientific_payload_sha256'],'axis_dimension':9,'main':main,'definitions':defs,'backward':back,'inverse':inverse,'linear_transpose_inverse':tr,'forward':forward,'ordinary_E_X':code_ex,'ordinary_E_inverse_X':code_eix,'operator_ABI':{'backward':'[[E_inverse D, -E_inverse R],[0,D E_inverse]]=H(E_inverse) B0','inverse':'[[D_inverse E,Q E D_inverse],[0,E D_inverse]]','forward':'[[E D,0],[D E Q_inverse,D E]]=H(E) F0','H':'H(T)=diag(T,Q_inverse T Q); R=D Q; E commutes R and is real symmetric. E generally does not commute Q or D.','mode_gather':'Actual original Y before backward precode. Inverse first finishes actual inverse source-Y pass with owned contact cache, then codes Y by E to acquire original ground.'},'width_contract':'Every literal address word tensor lifts; field ADD/SCALE coefficients act once. phase theta is i^(width*theta). Gaussian C_axes inverse is positive C_axes then X_axis_mask. No expanded address matrix is claimed.'}
 return payload
def inspect(program,payload):
 main={tuple(f)for f in payload['main']};live=set(main);peak=0;count=Counter();paid=Counter();coefficient=F(1)
 for e in program:
  op=e[0];count[op]+=1
  if op in['OWN_ZERO','COPY']:
   f=tuple(e[1]);need(f not in live and f not in main,'owned allocation fresh')
   if op=='COPY':need(tuple(e[2])in live,'owned COPY reads initialized field')
   live.add(f);peak=max(peak,len(live)-len(main))
  elif op=='CLEAR':f=tuple(e[1]);need(f in live and f not in main,'owned only CLEAR after use');live.remove(f)
  elif op in['ADD','SWAP']:
   need(tuple(e[1])in live and tuple(e[2])in live,'binary op initialized');need(e[1]!=e[2],'distinct binary fields')
   if op=='ADD':coefficient=max(coefficient,abs(F(e[3],e[4])))
  elif op=='SCALE':need(tuple(e[1])in live,'SCALE initialized');coefficient=max(coefficient,abs(F(e[2],e[3])))
  else:
   need(op=='U'and tuple(e[1])in live,'known initialized unary')
   word=payload['definitions'][e[2]];pc=Counter()
   for q in word:
    if q[0]=='C':paid[len(q[1])]+=1;pc[len(q[1])]+=1
    else:need(q[0]in['P','D','X','phase'],'literal unary opcode');count['physical_'+q[0]]+=1
   need(pc==({e[3]:1}if e[3]else{}),'declared actual child rank')
 need(live==main,'all owned fields cleaned after final use')
 return {'paid':dict(sorted(paid.items())),'ordinary_and_literal_counts':dict(sorted(count.items())),'peak_owned_fields':peak,'maximum_scalar_absolute_coefficient':str(coefficient)}
def scalar_code_replay(program,payload):
 # Common-chart owner projection only; physical L_i normalization and its
 # inverse supply the actual block L_i^-1 E_ij L_j by construction.
 states={('X',p):{p:F(1)}for p in range(120)}
 def add(a,b,q):
  for j,v in states[b].items():
   z=states[a].get(j,F())+q*v
   if z:states[a][j]=z
   else:states[a].pop(j,None)
 for e in program:
  op=e[0];f=tuple(e[1])
  if op=='OWN_ZERO':states[f]={}
  elif op=='CLEAR':del states[f]
  elif op=='SWAP':g=tuple(e[2]);states[f],states[g]=states[g],states[f]
  elif op=='ADD':add(f,tuple(e[2]),F(e[3],e[4]))
  elif op=='SCALE':states[f]={j:F(e[2],e[3])*v for j,v in states[f].items()}
  else:need(op=='U'and e[4]in['physical_L','physical_L_inverse'],'code has only actual physical normalization')
 return [[states['X',p].get(j,F())for j in range(120)]for p in range(120)]
def calculate():
 p=build();receipts={k:inspect(p[k],p)for k in['ordinary_E_X','ordinary_E_inverse_X','backward','inverse','linear_transpose_inverse','forward']}
 expected={2:120,3:120,5:120,6:120,9:8}
 for k in['backward','inverse','linear_transpose_inverse','forward']:need(receipts[k]['paid']==expected,'actual E module paid profile '+k)
 native=m.loadgz('NATIVE120-NATIVE-PROGRAM.json.gz',m.NATIVE_PIN);kernel=m.loadgz('KERNEL-PROGRAM.json.gz',m.KERNEL_PIN)
 K=m.scalar_K(native);M=[[F(x)for x in r]for r in kernel['root_M120x8']];C=[[sum(x*y for x,y in zip(r,s))/4 for s in M]for r in M]
 for name,s in[('ordinary_E_X',F(1,14)),('ordinary_E_inverse_X',F(1))]:
  want=[[K[i][j]+s*C[i][j]for j in range(120)]for i in range(120)]
  need(scalar_code_replay(p[name],p)==want,'actual emitted common-chart code all14400 entries '+name)
 # Structural mutants are meaningful even before a numerical field replay.
 bad=[e for e in p['inverse']if not(e[0]=='COPY'and e[1][0]=='cache')]
 try:inspect(bad,p)
 except ValueError:missing=True
 else:missing=False
 need(missing,'removed actual source caches rejected')
 bad=[list(e)for e in p['backward']];j=next(i for i,e in enumerate(bad)if e[0]=='ADD'and e[2][0]=='mode');bad.insert(j,['CLEAR',bad[j][2]])
 try:inspect(bad,p)
 except ValueError:early=True
 else:early=False
 need(early,'early original-ground mode CLEAR rejected')
 r={'schema':'full120-literal-positive-E-owned-macro-review/v1','status':'PASS_ACTUAL_BASE120_E_MACRO_AND_STRUCTURED_COMPOSITION','main_fields':240,'main_address_axes':9,'all14400_common_chart_code_entries_each_direction':True,'all_literal_owned_lifecycles':True,'actual_native_paid_phase_object':m.NATIVE_PIN,'actual_contact_inverse_and_transpose_all240_independent_operator_rows':'BASE120-CHECKPOINT.json','noncommuting_physical_allcolumn_fixture':'OWNED-E.json:three lambdas15,225/2,-1350;16 independent maincolumns each','noncommuting_generic_operator_identity':p['operator_ABI'],'receipts':receipts,'controls':{'missing_actual_source_cache_rejected':missing,'early_ground_mode_clear_rejected':early},'scientific_payload_sha256':hashlib.sha256(canonical(p)).hexdigest(),'scope':'The emitted base120 primitive words are actual, including every paid child, ordinary address word and phase. Exact common-chart scalarcode replay plus sealed native phase science and actual native owned inverse/transpose prove composition. This checker does not propagate a122880-by122880 dense matrix. The odd3 family uses the explicit structured owner loop and its independently pinned512 native template. No negative E decoder, formal supplier or new kappa.'}
 return json.loads(canonical(r)),json.loads(canonical(p))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r,p=calculate()
 if a.write:(HERE/'MACROS120.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');(HERE/'MACROS120-PROGRAM.json.gz').write_bytes(gzip.compress(canonical(p),mtime=0))
 else:need(json.loads((HERE/'MACROS120.json').read_bytes())==r,'read-only macro receipt');need(json.loads(gzip.decompress((HERE/'MACROS120-PROGRAM.json.gz').read_bytes()))==p,'read-only actual primitive macro')
 print(json.dumps(r,sort_keys=True))
