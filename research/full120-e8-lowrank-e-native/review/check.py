"""Read-only independent norm/invoice review; no dense operator replay."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
from hashlib import sha256
import json,gzip,math,argparse
HERE=Path(__file__).resolve().parent
AUTHOR=Path('/tmp/full-e8-e-adapter120-20261025-structural')
SEAL='cb40b9602eec2c4c8950af4f9e8a06ea0d99db5ca74ceafd8b7781acc0aaccf6'
def need(q,s):
 if not q:raise ValueError(s)
def canon(x):return(json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()
def js(n):return json.loads((AUTHOR/n).read_bytes())
def gz(n):return json.loads(gzip.decompress((AUTHOR/n).read_bytes()))
def pins():
 need(sha256((AUTHOR/'FILES.sha256').read_bytes()).hexdigest()==SEAL,'author seal unchanged')
 n=0
 for line in (AUTHOR/'FILES.sha256').read_text().splitlines():
  h,p=line.split('  ',1);need(sha256((AUTHOR/p).read_bytes()).hexdigest()==h,'author bytes unchanged '+p);n+=1
 return n

def norm_checks():
 pr=js('inputs/prefix/RECEIPT.json');r=js('PRECISION120.json')
 need(set(pr['orientations'])=={'to_modal','from_modal','to_modal_transpose','from_modal_transpose'},'four chronological prefix orientations')
 b=max(F(v['whole_three_axis_l2_amplification_squared_upper'])for v in pr['orientations'].values())
 c=(b.numerator+b.denominator-1)//b.denominator;S=math.isqrt(c)
 if S*S<c:S+=1
 need(S==977096 and S*S>=b and (S-1)**2<b,'independent exact recoder square root')
 rows=gz('inputs/K-PROGRAM.json.gz')['literal_scalar_K_rows'];cols=Counter()
 rmax=F(0);terms=set()
 for row in rows.values():
  terms.add(len(row));rmax=max(rmax,sum(abs(F(n,d))for j,n,d in row))
  for j,n,d in row:cols[j]+=abs(F(n,d))
 need(terms=={76} and rmax==max(cols.values())==7,'actual scalar K row/column Schur bound')
 # An arbitrary incoming scratch vector requires a shear bound, including I
 # on scratch. Triangle gives ||I+N_B|| <=1+||B|| <=8. The reverse transpose
 # has the same operator norm. Projections/SWAP/zero embeddings are <=1.
 need(1+rmax==8,'full arbitrary-scratch shear bound')
 # The restricted-zero embedding sqrt(1+7²) does not follow for a full shear.
 # This is a counterexample to that generic inference, not to actual K.
 ratio=F(7**2+50**2,7**2+1)
 need(ratio>50 and ratio<64,'arbitrary-scratch generic sqrt50 inference rejected')
 C=8*1351*S*S;Q=2*1351*S**4;M=16*C*C*Q;W=M**3*C**3
 need(str(C)==r['code_prefix_suffix_norm_bound'],'same code bound survives')
 need(str(Q)==r['query_gather_scatter_prefix_suffix_norm_bound'],'query count of four recoders')
 need(str(M)==r['local_module_prefix_suffix_norm_bound'],'native2*8 and two codes')
 need(str(W)==r['three_modules_plus_three_positive_exit_codes_norm_bound'],'same three-stage constant')
 need(M<1<<202 and W<1<<764,'advertised powers')
 return {'S':S,'recoder_squared_bound':str(b),'actual_K_terms_each_row':76,
         'actual_K_row_column_l1':'7','arbitrary_scratch_shear_bound':8,
         'generic_sqrt50_counterexample_squared_ratio':str(ratio),
         'unchanged_C':str(C),'unchanged_Q':str(Q),'unchanged_M':str(M),'unchanged_whole':str(W),
         'scope':'All declared whole-field macro prefixes and suffixes; no lowering of SWAP or recursive Gaussian internal arithmetic is granted.'}

def counter_add(*ds):
 out=Counter()
 for d in ds:out.update(d)
 return out

def invoice_checks():
 data=gz('ROOT512-CHECKPOINT-PROGRAM.json.gz');count=Counter();paid=Counter()
 for op in data['native_inverse_program']:
  if op[0]!='UNARY':count[op[0]]+=1;continue
  q=data['events'][str(abs(op[2]))]['inverse_literal']
  if q['kind']=='MONOMIAL':word=data['monomial_definitions'][q['word']]
  else:word=data['monomial_definitions'][q['before']]+[['C',q['positive_child_axes']]]+data['monomial_definitions'][q['after']]
  for e in word:
   if e[0]=='C':paid[len(e[1])]+=1
   else:count[e[0]]+=1
 per={k:F(v,512)for k,v in count.items()}
 need(per=={'ADD':76,'COPY':1,'CLEAR':1,'P':15,'D':15,'X':17,'phase':6},'literal native inverse counts independent census')
 need(paid=={8:512,9:512,15:512,16:512},'native paid profile')
 V=120**3;h=22016;batches=3*120**2
 r=js('PRECISION120.json');kernel=gz('inputs/KERNEL-PROGRAM.json.gz')
 for w in ['to_modal_kernel_word','from_modal_kernel_word']:
  need(Counter(e[0]for e in kernel[w])=={'ADD':7042,'SCALE':84,'SWAP':91},'actual owner instruction census')
 code={'ADD':2*batches*7042+76*V,'SCALE':2*batches*84+h,'SWAP':2*batches*91+V,'P':2*V,'D':2*V,'OWN_ZERO':V,'CLEAR':V}
 # Query and its transpose: each COPY becomes ADD+owned CLEAR; each final
 # owned CLEAR becomes OWN_ZERO. The explicit extra+h ADD covers this.
 query={'ADD':4*batches*7042+2*h,'SCALE':4*batches*84,'SWAP':4*batches*91,'P':4*V,'D':4*V,'COPY':h,'OWN_ZERO':h,'CLEAR':2*h}
 native={'ADD':77*V,'P':15*V,'D':15*V,'X':20*V,'phase':6*V,'COPY':V,'OWN_ZERO':V,'CLEAR':2*V}
 module=counter_add(code,code,query,native)
 whole=counter_add(*([module]*3),*([code]*3),{'SWAP':V,'SCALE':V})
 need(code==r['ordinary_E_or_inverse_code'],'E orientation upper invoice')
 need(query==r['ordinary_query_or_adjoint_upper'],'query both orientations upper invoice')
 need(native==r['ordinary_native_inverse_transpose_boundaries_upper'],'native both orientations upper invoice')
 need(dict(module)==r['ordinary_local_module_upper']and dict(whole)==r['ordinary_N3_plus_positive_exit_upper'],'complete independent structured sums')
 need(r['paid_N3']=={'8':3*V,'9':3*V,'15':3*V,'16':3*V,'25':3*h},'three-stage paid bill')
 need(r['owned_local_and_N3_peak_upper']==V+h+512,'all contact/mode/Kscratch peak covered')
 return {'literal_root512_inverse_counts':dict(count),'inverse_per_owner':{k:str(v)for k,v in per.items()},
         'forward_extra_X_per_owner':3,'transpose_COPY_extra_ADD_per_owner':1,
         'ordinary_code':code,'query_upper':query,'native_upper':native,'module_upper':dict(module),
         'owned_peak_upper':V+h+512,'invoice_orientation':'Direct B needs fewer owned events; inverse requires COPY caches; forward transpose requires OWN_ZERO cache/modes and COPY-adjoint ADD. The unified bill covers each, without charging an owned field as productive mass.'}

def contact_checks():
 source=gz('inputs/B-PROGRAM.json.gz');original=source['program'];versions=Counter();contacts={};reads=Counter()
 for e in original:
  if e[0]=='ADD':
   need(e[1]=='X'and e[3]=='Y','source Y read only by targetADD')
   owner=e[4];v=(versions[owner],e[7]);need(owner not in contacts or contacts[owner]==v,'one unchanged physical source contact')
   contacts[owner]=v;reads[owner]+=1
  elif e[1]=='Y':versions[e[2]]+=1
 need(len(contacts)==512 and set(reads.values())=={76},'actual512 contact contact/read counts')
 cp=gz('ROOT512-CHECKPOINT-PROGRAM.json.gz');current=Counter(versions);seen=set()
 for e in cp['source_Y_only_pass']:
  if e[0]=='UNARY':
   q=cp['events'][str(abs(e[2]))]['original'];need(q[1]=='Y'and e[2]<0,'actual reverse source unary');current[q[2]]-=1
  else:
   need(e[0]=='COPY'and e[1][0]=='cache'and e[2][0]=='Y','only actual source snapshots')
   owner=e[2][1];need(current[owner]==contacts[owner][0]and owner not in seen,'cache captured at actual contact version');seen.add(owner)
 need(len(seen)==512 and all(v==0 for v in current.values()),'source inverse completes after cache')
 base=gz('MACROS120-PROGRAM.json.gz');back=base['backward'];inv=base['inverse']
 queries=[j for j,e in enumerate(back)if e[0]=='U'and e[4]=='original_ground_full_R9_query']
 native=[j for j,e in enumerate(back)if e[0]=='U'and e[4].startswith('actual_native_')]
 need(len(queries)==8 and max(queries)<min(native),'backward original-ground queries precede source-consuming native')
 for program,sign in [(back,-1),(inv,1)]:
  scat=[e for e in program if e[0]=='ADD'and e[2][0]=='mode']
  need(len(scat)==8 and all(F(e[3],e[4])==sign*15 for e in scat),'actual base original-ground correction sign')
 # Linear transpose is bilinear, so SCALE and ADD coefficients retain sign.
 tr=base['linear_transpose_inverse'];expected=[]
 for e in reversed(inv):
  if e[0]=='ADD':expected.append(['ADD',e[2],e[1],e[3],e[4]])
  elif e[0]=='COPY':expected.extend([['ADD',e[2],e[1],1,1],['CLEAR',e[1]]])
  elif e[0]=='CLEAR':expected.append(['OWN_ZERO',e[1]])
  elif e[0]=='OWN_ZERO':expected.append(['CLEAR',e[1]])
  elif e[0]in['SWAP','SCALE']:expected.append(e)
  else:expected.append(None)
 need(len(expected)==len(tr),'literal transpose length')
 need(all(a is None or a==b for a,b in zip(expected,tr)),'every non-address transpose primitive exact coefficient once')
 return {'source_owners':512,'reads_per_owner':76,'actual_snapshot_versions_checked':512,
         'base_query_calls_before_native':len(queries),'base_scatter_signs':[-15,15],
         'transpose_non_address_primitives_checked':sum(a is not None for a in expected),
         'scope':'No physical full-column replay performed here. Actual unary inverse/transpose phase science is pinned in the author package and independently reviewed by root.'}

def calculate():
 n=pins();r={'status':'PASS_READONLY_E120_NORMS_INVOICE_AND_CONTACT_REVIEW',
 'author_package':str(AUTHOR),'author_FILES_sha256':SEAL,'author_files_unchanged':n,
 'norm':norm_checks(),'ordinary_invoice':invoice_checks(),'source_timing_and_transpose':contact_checks(),
 'finding':'Clarify the arbitrary-scratch argument: use full shear norm<=1+||B||<=8. The sqrt(1+7^2) expression only follows from the row/column premise for a zero-scratch embedding. All existing declared constants remain valid.',
 'scope':'Declared whole-field macro l2 norms and structured invoice only. No coordinate fixedpoint/TM theorem, recursive child internal error tariff, negative terminal decoder, complete new supplier, scientific adoption or kappa is established.'}
 r['scientific_payload_sha256']=sha256(canon(r)).hexdigest();return r
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');a=ap.parse_args();r=calculate()
 if a.write:(HERE/'RESULT.json').write_bytes(canon(r))
 else:need(json.loads((HERE/'RESULT.json').read_bytes())==r,'read-only result')
 if not a.write and (HERE/'FILES.json').exists():
  for f in json.loads((HERE/'FILES.json').read_bytes())['files']:
   z=(HERE/f['path']).read_bytes();need(len(z)==f['bytes']and sha256(z).hexdigest()==f['sha256'],'manifest '+f['path'])
 print(json.dumps(r,sort_keys=True))
