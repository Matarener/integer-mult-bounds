#!/usr/bin/env python3
"""Generate a hidden-Y kernel independently, then verify original group rows.

THU New Media Research Center; substantial OpenAI Codex assistance. Apache-2.0.

This reads neither MODULE-CERTIFICATE.json nor search.py. It derives the
candidate without a saved kernel, then compares the derived rows with KERNEL.json.
Augmentation supplies only a candidate. The decisive check multiplies every
original actual-group history row by the candidate and cancels per group ID.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
from collections import Counter,defaultdict
from functools import lru_cache
import argparse,gzip,json,time,sys,struct
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent

def require(ok,message):
 if not ok:raise ValueError(message)

def y_role(role):return role[0]=='L'and 112<=role[1]<224

def linear(columns,x):
 y=0
 for j,col in enumerate(columns):
  if x>>j&1:y^=col
 return y

def own_native(columns):
 a=[sum(((columns[j]>>i)&1)<<j for j in range(9))for i in range(9)];b=[1<<i for i in range(9)]
 for j in range(9):
  pivot=next(i for i in range(j,9)if a[i]>>j&1);a[j],a[pivot]=a[pivot],a[j];b[j],b[pivot]=b[pivot],b[j]
  for i in range(9):
   if i!=j and a[i]>>j&1:a[i]^=a[j];b[i]^=b[j]
 require(a==[1<<i for i in range(9)],'independent GF2 inverse')
 Q=[]
 for i in range(9):
  row=1<<i
  for r in b:
   if r>>i&1:row^=r
  Q.append(row)
 result=[]
 for x in range(512):
  y=linear(columns,x);bits=[i for i in range(9)if y>>i&1]
  phase=sum((Q[i]>>i)&1 for i in bits)+2*sum((Q[i]>>j)&1 for i in bits for j in bits if i<j)
  result.append(4*y+phase%4)
 return tuple(result)

def compose(a,b):return tuple(4*(a[v>>2]>>2)+((a[v>>2]+v)&3)for v in b)
def conjugate(a):return tuple(4*(v>>2)+(-v%4)for v in a)
def inverse(a):
 out=[None]*512
 for x,v in enumerate(a):out[v>>2]=4*x+(-v%4)
 return tuple(out)

def locate(runtime,relative,bare):
 # Same-package default in a research checkout, or two exported input blobs.
 for path in (runtime/'inputs'/bare,runtime/relative,runtime.parents[1]/relative):
  if path.is_file():return path
 raise ValueError('missing runtime input '+relative)

def calculate(runtime,write=False):
 started=time.monotonic();runtime=Path(runtime).resolve()
 s=locate(runtime,'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz','ACTUAL-WORD.json.gz')
 p=locate(runtime,'research/native-rank8-helper-provider/WORD.json.gz','WORD.json.gz')
 require(sha256(s.read_bytes()).hexdigest()=='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05','source pin')
 require(sha256(p.read_bytes()).hexdigest()=='7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc','provider pin')
 canon=json.loads(gzip.decompress(s.read_bytes()))['canonical'];doc=json.loads(gzip.decompress(p.read_bytes()));require(doc['direction']=='backward','backward source')
 operators=[tuple(4*x for x in range(512))];lookup={operators[0]:0}
 def register(op):
  if op not in lookup:lookup[op]=len(operators);operators.append(op)
  return lookup[op]
 warp={}
 for w in canon['warps']:
  forward=own_native(w['G_columns']);warp[w['op']]=register(conjugate(forward));warp[-w['op']]=register(conjugate(inverse(forward)))
 @lru_cache(None)
 def product(a,b):return register(compose(operators[a],operators[b]))
 rows={('L',i):{(('L',i),0):F(1)}for i in range(632)};frames={('L',i):v for i,v in enumerate(canon['start'])};full={i for i,v in enumerate(canon['frames'])if len(v)==9}
 require(full=={1}and canon['frames'][1]==[256,128,64,32,16,8,4,2,1],'standard full frame')
 require(not any(v in full for v in frames.values()),'no initial full-frame fields')
 def get(r):
  if r not in rows:require(r[0]=='C','only owned additional roles');rows[r]={(r,0):F(1)};frames[r]=None
  return rows[r]
 histories=[];events=[];seen=set();counts=Counter()
 for index,event in enumerate(doc['word']):
  kind=event[0];counts[kind]+=1;touched=None
  if kind=='scalar':
   g,chart=event[1:];dst=tuple(g[1]);get(dst);touched=dst
   if g[0]=='clear':require(dst[0]=='C','clear owned only');rows[dst]={};frames[dst]=chart
   elif g[0]=='copy':
    src=tuple(g[2]);get(src);require(dst[0]=='C'and not rows[dst]and frames[src]==chart,'copy owned zero at true chart');rows[dst]=dict(rows[src]);frames[dst]=chart
   elif g[0]=='scale':
    require(frames[dst]==chart,'scale chart');q=F(g[2],g[3]);rows[dst]={k:q*v for k,v in rows[dst].items()if q*v}
   elif g[0]=='add':
    src=tuple(g[2]);get(src);require(dst!=src and frames[src]==frames[dst]==chart,'ADD chart');q=F(g[3],g[4])
    for k,v in list(rows[src].items()):
     z=rows[dst].get(k,F(0))+q*v
     if z:rows[dst][k]=z
     else:rows[dst].pop(k,None)
   else:raise ValueError(g[0])
  elif kind=='warp':
   _,role,op,before,after=event;dst=tuple(role);get(dst);require(frames[dst]==before,'warp chart');rows[dst]={(r,product(warp[op],a)):q for(r,a),q in rows[dst].items()};frames[dst]=after;touched=dst
  elif kind=='climb':
   dst=('L',event[2]);require(frames[dst]==event[3],'paid climb chart');frames[dst]=event[4];touched=dst
  elif kind=='zero_retag':
   dst=('L',event[1]);require(frames[dst]==event[2]and not rows[dst],'exact zero retag');frames[dst]=event[3];touched=dst
  else:require(kind in ('phase','adapter'),'retained marker grammar')
  if touched is not None and frames[touched]in full and rows[touched]:
   tag=frozenset(rows[touched].items())
   if tag not in seen:seen.add(tag);histories.append(dict(rows[touched]));events.append({'event':index,'role':list(touched),'frame':frames[touched]})
 require(len(histories)==4891 and set(rows)=={('L',i)for i in range(632)}|{('C',i)for i in range(9)},'all632 and nine arbitrary owned source roles')
 # Independent Fraction elimination on scalar augmentations. Y columns are
 # always free variables; a pure-Y scalar constraint would reject the model.
 basis={};aug_zero=0
 for history in histories:
  augmented=defaultdict(F)
  for(r,op),q in history.items():augmented[r]+=q
  row={r:q for r,q in augmented.items()if q}
  while row:
   nonY=[r for r in row if not y_role(r)]
   require(nonY,'augmentation has no constraint on independently arbitrary Y')
   pivot=min(nonY);coefficient=row[pivot]
   if pivot not in basis:
    basis[pivot]={r:q/coefficient for r,q in row.items()};break
   for r,q in basis[pivot].items():
    value=row.get(r,F(0))-coefficient*q
    if value:row[r]=value
    else:row.pop(r,None)
  if not row:aug_zero+=1
 require(len(basis)==474,'independent augmentation rank')
 # All unused nonY and all owned columns receive zero compensation. This is
 # a scalar map with K_Y=I, not an inverse address-operator polynomial.
 K={('L',i):({i-112:F(1)}if 112<=i<224 else{})for i in range(632)};K.update({('C',i):{}for i in range(9)})
 for pivot in sorted(basis,reverse=True):
  vector=defaultdict(F)
  for role,q in basis[pivot].items():
   if role!=pivot:
    for j,value in K[role].items():vector[j]-=q*value
  K[pivot]={j:q for j,q in vector.items()if q}
 require(all(K['L',112+j]=={j:F(1)}for j in range(112)),'K_Y exactly identity')
 require(all(not K['C',j]for j in range(9)),'source-owned dirt held fixed by the kernel')
 require(all(K['L',j]=={j:F(1)}for j in range(112))and all(not K['L',j]for j in range(224,632)),
         'independently derived kernel is exactly delta X=delta Y, all helpers fixed')
 declared=json.loads((runtime/'KERNEL.json').read_text())
 require(declared['original_input_roles']==632 and declared['free_Y_columns']==112 and len(declared['rows'])==632,'declared provider kernel shape')
 declared_rows=[{int(j):F(q)for j,q in row}for row in declared['rows']]
 require(all(declared_rows[i]==K['L',i]for i in range(632)),
         'independently derived kernel equals supplied small KERNEL rows')
 def first_failure(kernel):
  for index,row in enumerate(histories):
   residual=defaultdict(F)
   for(role,op),q in row.items():
    for j,value in kernel[role].items():residual[op,j]+=q*value
   residual={key:q for key,q in residual.items()if q}
   if residual:return {'history':index,'event':events[index],'first_nonzero_group_column':list(min(residual)),'coefficient':str(residual[min(residual)]),'residual_terms':len(residual)}
  return None
 require(first_failure(K)is None,'ORIGINAL actual signed-group H_j K = 0, per group element')
 paired_terms=0
 for row in histories:
  pairs=defaultdict(F)
  for(role,op),q in row.items():
   if role[0]=='L'and role[1]<224:pairs[role[1]%112,op]+=q;paired_terms+=1
  require(not any(pairs.values()),'direct literal operator X_i plus Y_i cancellation')
 # Actual failure witnesses, not just assertions about the rank algorithm.
 wrong_y=dict(K);wrong_y['L',112]={};y_control=first_failure(wrong_y);require(y_control is not None,'wrong Y perturbation rejected')
 role=next(r for r in sorted(K)if not y_role(r)and K[r]);j=next(iter(K[role]));wrong_N=dict(K);wrong_N[role]=dict(K[role]);wrong_N[role][j]+=1
 N_control=first_failure(wrong_N);require(N_control is not None,'wrong nonY compensation rejected')
 no_N={r:(v if y_role(r)else{})for r,v in K.items()};no_N_control=first_failure(no_N);require(no_N_control is not None,'uncompensated original Y variation is visible')
 encoded={'schema':'independent-scalar-hidden-Y-kernel/v1','Y_source_roles':list(range(112,224)),'original_input_rows':[{'role':list(r),'coefficients':[[j,str(q)]for j,q in sorted(K[r].items())]}for r in sorted(K)if r[0]=='L'],'owned_input_rows_zero':[list(r)for r in sorted(K)if r[0]=='C'],'definition':'delta logical input_r = sum_j K[r,j] deltaY_j; K_Y=I; every original actual-group full-frame history annihilates this map.'}
 raw=json.dumps(encoded,indent=2,sort_keys=True)+'\n'
 if write:(HERE/'KERNEL-INDEPENDENT.json').write_text(raw)
 used={op for row in histories for role,op in row};base_digest=sha256(b''.join(sorted(struct.pack('<512H',*operators[i])for i in used))).hexdigest()
 require(len(used)==59 and base_digest=='34ad3a3f37a53afd59e0d295d6dffa446819539b9ac46556ef51134eb888d831','independently replayed physical operator set binding')
 result={'status':'PASS_INDEPENDENT_ORIGINAL_GROUP_HISTORY_HIDDEN_Y_KERNEL','method':'Own Fraction elimination of augmentation proposes scalar K; decisive independent verification is H_j K=0 in every actual group coefficient of every original replay row. No decomposition certificate, search import, modular calculation or width-one matrix-sum relation is used. The candidate is derived without reading saved kernel rows, then compared with KERNEL.json.','source_word_sha256':sha256(p.read_bytes()).hexdigest(),'source_payload_sha256':sha256(s.read_bytes()).hexdigest(),'full_frame_histories':4891,'original_history_group_terms':sum(len(row)for row in histories),'paired_X_Y_group_terms_checked':paired_terms,'original_independent_roles':632,'owned_entry_roles':9,'augmentation_nonY_rank':len(basis),'kernel_shape':'K=[I112;I112;0_408], and zero on all nine owned inputs','K_Y_identity_columns':112,'original_K_nonzero_entries':sum(len(v)for r,v in K.items()if r[0]=='L'),'nonzero_nonY_compensating_original_roles':sum(bool(v)and not y_role(r)for r,v in K.items()),'source_owned_compensation_is_zero':True,'actual_group_annihilation_checks':4891,'actual_observation_operator_count':len(used),'actual_observation_operator_set_sha256':base_digest,'kernel_sha256':sha256(raw.encode()).hexdigest(),'controls':{'wrong_Y_row':y_control,'wrong_nonY_compensation':N_control,'Y_variation_without_nonY_compensation':no_N_control,'supplied_original_Y0_identity_observation':{'non_annihilated_Y_column':0,'identity_operator_coefficient':'1'}},'all_width_reason':'Each exact signed group identity lifts by operator composition to every tensor width. H_j K=0 retains scalar owner coefficients outside tensor powers and does not use physical width-one linear relations.','theorem':'At every width, every original Y variation can be compensated by the same logical X variation, with all helpers and owned entries fixed, leaving every admitted full-frame history unchanged. Therefore no nonzero pure-Y linear observation lies in their module even under arbitrary address-End left coefficients; no deterministic postprocessing of only those snapshots can recover a nonconstant function of Y.','physical_chart_guard':'Logical source variables are converted to physical independent inputs by their invertible birth frames. All snapshots share the one full inverse-transpose Gaussian Phi. Right birth factors and common Phi preserve annihilation and the hidden-Y fiber; owned chart/precision execution remains inherited.','limits':'Only the unchanged frozen native full-frame snapshots. Separate reads of partial-frame/main Y, modified paid contacts/history or new supplied correlated observations are outside this theorem. Fixing helper or owned values alone does not evade this particular kernel, because it changes only X and Y. No paid lower bound, new caller or new kappa is asserted.','seconds':time.monotonic()-started}
 return result

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');parser.add_argument('--runtime',type=Path,default=HERE,help='package containing KERNEL.json; sources found in its repository or inputs/');args=parser.parse_args();result=calculate(args.runtime,args.write);path=HERE/'INDEPENDENT-KERNEL-AUDIT.json'
 if args.write:path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 else:
  old=json.loads(path.read_text());old.pop('seconds');new=dict(result);new.pop('seconds');require(old==new,'stable independent kernel audit')
 print(json.dumps({k:result[k]for k in ('status','full_frame_histories','augmentation_nonY_rank','K_Y_identity_columns','original_K_nonzero_entries','seconds')},sort_keys=True))
