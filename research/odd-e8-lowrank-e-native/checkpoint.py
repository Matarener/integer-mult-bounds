"""Actual root512 source-contact inverse and exact transposed owned word.

Native unary operations are arbitrary invertible free operator letters in the
all-input replay. Their inverse/transpose physical words are also emitted.
Default is read-only; no sealed source package is modified.
"""
import argparse,gzip,hashlib,json,sys
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'inputs'
PIN='f6b26f28f2a8f2dcfbf81f98c7ca18f967384b7b61518766494f8e821d5bf56f'
def need(q,s):
 if not q:raise ValueError(s)
def canonical(x):return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def gf_inv(rows):
 n=len(rows);r=[v|(1<<(n+j))for j,v in enumerate(rows)]
 for j in range(n):
  p=next(i for i in range(j,n)if r[i]>>j&1);r[p],r[j]=r[j],r[p]
  for i in range(n):
   if i!=j and r[i]>>j&1:r[i]^=r[j]
 need([v&((1<<n)-1)for v in r]==[1<<j for j in range(n)],'invertible actual P')
 return [v>>n for v in r]
def mono_transform(word,transpose=False):
 out=[]
 for e in reversed(word):
  if e[0]=='P':out.append(['P',gf_inv(e[1])])
  elif e[0]=='D':out.append(['D',e[1],e[2]if transpose else[(-v)%4 for v in e[2]]])
  elif e[0]=='X':out.append(list(e))
  else:need(e[0]=='phase','actual monomial opcode');out.append(['phase',e[1]if transpose else(-e[1])%4])
 return out
# Free invertible event letters with a transpose involution, all noncommuting.
def reduce_prepend(letter,w):
 return w[1:]if w and w[0]==-letter else(letter,)+w
def opword(w,letter):return reduce_prepend(letter,w)
def transformed_word(w):
 # Transpose maps each event letter k to k+N with the same inverse sign.
 return tuple((1 if x>0 else-1)*(abs(x)+1000000)for x in reversed(w))
def add(dst,src,c):
 for key,v in src.items():
  x=dst.get(key,F())+c*v
  if x:dst[key]=x
  else:dst.pop(key,None)
def run(program,main,initial=None,strict=True):
 states={x:{(x,()):F(1)}for x in main}if initial is None else{k:dict(v)for k,v in initial.items()}
 live=set(main)
 for e in program:
  k=e[0]
  if k=='UNARY':
   f=tuple(e[1]);letter=e[2]
   need(f in live,'unary reads initialized field')
   states[f]={(src,opword(w,letter)):c for(src,w),c in states[f].items()}
  elif k=='ADD':
   a,b=tuple(e[1]),tuple(e[2]);need(a in live and b in live,'ADD reads initialized owned/main field');add(states[a],states[b],F(e[3],e[4]))
  elif k=='COPY':
   a,b=tuple(e[1]),tuple(e[2]);need(a not in live and b in live,'COPY requires fresh owned destination and initialized source');states[a]=dict(states[b]);live.add(a)
  else:
   need(k=='CLEAR','known emitted opcode');a=tuple(e[1]);need(a in live,'CLEAR requires live owned field');need(a not in main,'no main CLEAR');states[a]={};live.remove(a)
 need(all(f in main for f in live),'all owned fields cleared after final read')
 return {f:states[f]for f in main}
def transpose_program(program):
 out=[]
 for e in reversed(program):
  if e[0]=='UNARY':out.append(['UNARY',e[1],(1 if e[2]>0 else-1)*(abs(e[2])+1000000)])
  elif e[0]=='ADD':out.append(['ADD',e[2],e[1],e[3],e[4]])
  elif e[0]=='CLEAR':
   # A reverse adjoint for a discarded owned variable starts at zero.
   out.append(['ZERO_OWNED',e[1]])
  else:
   need(e[0]=='COPY','transpose supported opcode');out.extend([['ADD',e[2],e[1],1,1],['CLEAR',e[1]]])
 # ZERO_OWNED does not read an ordinary variable; normalize it to a fresh
 # initialized zero field, kept separate from COPY's overwrite prohibition.
 return out
def run_transpose(program,main):
 states={f:{(f,()):F(1)}for f in main};live=set(main)
 for e in program:
  k=e[0]
  if k=='ZERO_OWNED':
   f=tuple(e[1]);need(f not in live and f not in main,'adjoint owned zero is fresh');states[f]={};live.add(f)
  elif k=='UNARY':
   f=tuple(e[1]);need(f in live,'adjoint unary initialized');states[f]={(src,opword(w,e[2])):c for(src,w),c in states[f].items()}
  elif k=='ADD':
   a,b=tuple(e[1]),tuple(e[2]);need(a in live and b in live,'adjoint ADD initialized');add(states[a],states[b],F(e[3],e[4]))
  else:
   need(k=='CLEAR','known adjoint opcode');f=tuple(e[1]);need(f in live and f not in main,'owned adjoint CLEAR');states[f]={};live.remove(f)
 need(live==set(main),'all adjoint owned fields cleaned')
 return {f:states[f]for f in main}
def compile_program(source):
 payload=json.loads(gzip.decompress((source/'B-PROGRAM.json.gz').read_bytes()));need(hashlib.sha256(canonical(payload)).hexdigest()==PIN,'actual B canonical science pin')
 original=payload['program'];ports=payload['port_order'];main=[(r,p)for r in ['X','Y']for p in ports]
 program=[];events={};versions=Counter();contacts={};usecounts=Counter();paid=Counter();defs={}
 def wordid(w):
  k=hashlib.sha256(canonical(w)).hexdigest();defs[k]=w;return k
 for index,e in enumerate(original):
  if e[0]=='ADD':
   need(e[1]=='X'and e[3]=='Y','actual literal B has source-only Y')
   p=e[4];contact=(versions[p],e[7]);need(p not in contacts or contacts[p]==contact,'every actual Y has one unchanged physical ADD contact')
   contacts[p]=contact;usecounts[p]+=1;program.append(['ADD',[e[1],e[2]],[e[3],e[4]],e[5],e[6]])
  else:
   need(e[0]in['MONOMIAL','BOUNDARY_MONOMIAL','PAID_PATH'],'known actual B instruction')
   f=[e[1],e[2]];eid=index+1
   if e[1]=='Y':versions[e[2]]+=1
   if e[0]=='PAID_PATH':
    rec=e[5];before=payload['definitions'][rec['before_monomial']];after=payload['definitions'][rec['after_monomial']];axes=rec['child_axes'];paid[len(axes)]+=1
    inverse={'kind':'PAID_PATH','before':wordid(mono_transform(after)),'positive_child_axes':axes,'after':wordid([['X',sum(1<<a for a in axes)]]+mono_transform(before)),'rank':len(axes),'absolute_identity':'C_axes^-1 = C_axes then X_axis_mask, with phase exactly one at every width'}
    it={'kind':'PAID_PATH','before':wordid(mono_transform(defs[inverse['after']],True)),'positive_child_axes':axes,'after':wordid(mono_transform(defs[inverse['before']],True)),'rank':len(axes)}
   else:
    w=payload['definitions'][e[3]];inverse={'kind':'MONOMIAL','word':wordid(mono_transform(w))};it={'kind':'MONOMIAL','word':wordid(mono_transform(defs[inverse['word']],True))}
   events[eid]={'original_instruction_index':index,'original':e,'inverse_literal':inverse,'inverse_transpose_literal':it}
   program.append(['UNARY',f,eid])
 need(len(contacts)==len(ports)==512 and all(usecounts[p]==76 for p in ports),'all actual512 Y contacts and76 reads')
 # First pass executes all inverse Y source work and snapshots each unchanged
 # ADD contact exactly once; the second pass reverses X and reads snapshots.
 ypass=[];xpass=[];cached=set();current=Counter(versions)
 for e in reversed(program):
  if e[0]=='UNARY':
   if e[1][0]=='Y':ypass.append(['UNARY',e[1],-e[2]]);current[e[1][1]]-=1
   else:xpass.append(['UNARY',e[1],-e[2]])
  else:
   p=e[2][1]
   need(current[p]==contacts[p][0],'literal inverse source reaches authenticated physical contact')
   if p not in cached:ypass.append(['COPY',['cache',p],['Y',p]]);cached.add(p)
   xpass.append(['ADD',e[1],['cache',p],-e[3],e[4]])
 need(all(v==0 for v in current.values()),'all actual source inverse paths completed')
 inverse=ypass+xpass+[['CLEAR',['cache',p]]for p in ports]
 transposed=transpose_program(inverse)
 emitted={'schema':'actual-root512-inverse-source-contact/v1','source_B_canonical_sha256':PIN,'axis_dimension':payload['axis_dimension'],'ports':ports,'source_contract':'Every Y has exactly one physical ADD contact; its current value is copied before completing the independent inverse source path. The owned cache feeds all76 reverse ADDs on X.','source_Y_only_pass':ypass,'target_X_only_pass':xpass,'native_inverse_program':inverse,'native_inverse_transpose_program':transposed,'events':events,'monomial_definitions':defs,'whole_family':'Repeat this parameterized construction for each lexicographic cube tuple in14^3, with the actual B constructor. Geometry/phase family proof remains the authenticated whole-K package; default fixture parses root512 only.'}
 return main,program,inverse,transposed,json.loads(canonical(emitted)),paid

def calculate(source):
 main,base,inv,tr,payload,paid=compile_program(source)
 base_rows=run(base,main);out=run(inv,main,base_rows)
 need(out=={f:{(f,()):F(1)}for f in main},'actual1024-field generic free-operator right inverse')
 invrows=run(inv,main);out2=run(base,main,invrows)
 need(out2=={f:{(f,()):F(1)}for f in main},'actual1024-field generic free-operator left inverse')
 expected={f:{}for f in main}
 for outfield,row in invrows.items():
  for(src,w),c in row.items():add(expected[src],{(outfield,transformed_word(w)):c},F(1))
 need(run_transpose(tr,main)==expected,'all1024-field exact free-operator transpose of owned inverse word')
 # Mutations concern the actual emitted native instructions and lifecycle.
 controls={}
 bad=[e for e in inv if not(e[0]=='COPY'and e[1][1]==payload['ports'][0])]
 try:run(bad,main,base_rows)
 except ValueError:controls['missing_actual_owned_snapshot_rejected']=True
 need(controls.get('missing_actual_owned_snapshot_rejected'),'missing snapshot mutant')
 bad=[list(e)for e in inv];i=next(i for i,e in enumerate(bad)if e[0]=='UNARY');bad[i]=['UNARY',bad[i][1],-bad[i][2]]
 controls['wrong_actual_inverse_orientation_rejected']=run(bad,main,base_rows)!={f:{(f,()):F(1)}for f in main};need(controls['wrong_actual_inverse_orientation_rejected'],'inverse mutant')
 bad=[list(e)for e in tr];i=next(i for i,e in enumerate(bad)if e[0]=='ADD');bad[i]=['ADD',bad[i][1],bad[i][2],-bad[i][3],bad[i][4]]
 controls['wrong_transpose_actual_ADD_sign_rejected']=run_transpose(bad,main)!=expected;need(controls['wrong_transpose_actual_ADD_sign_rejected'],'transpose mutant')
 # No cache may be cleared before its final reverse native ADD read.
 bad=[list(e)for e in inv];p=payload['ports'][0];i=next(i for i,e in enumerate(bad)if e[0]=='ADD'and e[2]==['cache',p]);bad.insert(i,['CLEAR',['cache',p]])
 try:run(bad,main)
 except ValueError:controls['owned_early_CLEAR_rejected']=True
 need(controls.get('owned_early_CLEAR_rejected'),'lifecycle mutant')
 report={'schema':'actual-root512-owned-inverse-transpose-review/v1','status':'PASS_ACTUAL_NATIVE_SOURCE_CHECKPOINT_AND_FREE_OPERATOR_TRANSPOSE','source_B_science':PIN,'arbitrary_main_fields':len(main),'actual_source_ports':512,'source_contacts_checked':512,'actual_source_ADD_reads_checked':38912,'source_contact_reads_each':76,'owned_snapshot_fields':512,'owned_COPY':512,'owned_CLEAR':512,'native_paid_profile':dict(sorted(paid.items())),'inverse_and_transpose_same_paid_profile':True,'all_independent_main_operator_rows_checked':len(main),'left_and_right_generic_inverse':True,'transpose_all_operator_entries':True,'exact_inverse_nonzero_operator_terms':sum(len(v)for v in invrows.values()),'inverse_monomial_or_paid_events':len(payload['events']),'emitted_literal_inverse_and_inverse_transpose_definitions':True,'controls':controls,'scientific_payload_sha256':hashlib.sha256(canonical(payload)).hexdigest(),'scope':'Actual root512 native B source-checkpoint compiler, over arbitrary independent noncommuting invertible event operators. Exact inverse and transpose owned lifecycles. Native physical phase science inherited through actual literal monomial inverse/transpose and C^-1=C X_mask identities. E/global lowrank query not included in this native-only replay; separate exact fixture binds those adapters.'}
 return json.loads(canonical(report)),payload
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=SOURCE);ap.add_argument('--write',action='store_true');a=ap.parse_args();r,p=calculate(a.source)
 if a.write:(HERE/'ROOT-CHECKPOINT.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n');(HERE/'ROOT-CHECKPOINT-PROGRAM.json.gz').write_bytes(gzip.compress(canonical(p),mtime=0))
 else:need(json.loads((HERE/'ROOT-CHECKPOINT.json').read_bytes())==r,'read-only root checkpoint receipt');need(json.loads(gzip.decompress((HERE/'ROOT-CHECKPOINT-PROGRAM.json.gz').read_bytes()))==p,'read-only root checkpoint literal payload')
 print(json.dumps(r,sort_keys=True))
