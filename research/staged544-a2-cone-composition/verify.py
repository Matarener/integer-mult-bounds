#!/usr/bin/env python3
"""Current-provider A2 transfer and owner-cone composition.
Chris R / Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
Retained ToikY/PR4019, PR3998 and PR4016 engines are credited reuse.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import argparse,gzip,hashlib,json,sys,types
ROOT=Path(__file__).resolve().parent
PROFILE={1:2482,2:712,3:218,4:109,5:20,8:8}
WIDTHS={5:28,6:18,7:53,8:96,9:213}

def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(p.read_bytes(),object_pairs_hook=unique)
def unique(pairs):
 out={}
 for k,v in pairs:
  need(k not in out,'duplicate JSON key');out[k]=v
 return out
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def module(name,path):
 m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
 exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m
def authenticate():
 manifest=read(ROOT/'SOURCES.json');prefix='research/staged544-a2-cone-composition/'
 for row in manifest['source_exports']:
  need(row['path'].startswith(prefix),'local source namespace');p=ROOT/row['path'][len(prefix):]
  need(not p.is_symlink(),'source symlink');raw=p.read_bytes()
  need(len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],'frozen source hash: '+str(p))
  need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob')
 return manifest
def load_engines():
 authenticate();t=module('retiming',ROOT/'frozen/cone/frozen/retiming.py');core=module('audit_core',ROOT/'frozen/cone/frozen/audit_core.py')
 tariff=module('tariff',ROOT/'frozen/cone/tariff.py');cone=module('credited_cone',ROOT/'frozen/cone/verify.py')
 sep=module('credited_sep',ROOT/'frozen/sep/verify.py')
 return t,core,tariff,cone,sep
def word(tag):
 need(tag in ('base','extra'),'provider');return json.loads(gzip.decompress((ROOT/f'inputs/WORD-{tag}.json.gz').read_bytes()),object_pairs_hook=unique)
def contract(w,records,core):
 need(sum(len(r['support']) for r in records)==len(set().union(*(set(r['support']) for r in records))),'overlapping supports')
 x=deepcopy(w);positions={}
 for section in ('A','B','restore'):
  local=[r for r in records if r['section']==section];starts={r['indices'][0]:r for r in local};skip={i for r in local for i in r['indices'][1:]};out=[]
  for i,g in enumerate(w[section]):
   if section=='B':positions[i]=len(out)
   if i in starts:out.extend(deepcopy(starts[i]['replacement']))
   elif i not in skip:out.append(deepcopy(g))
  if section=='B':positions[len(w[section])]=len(out)
  x[section]=out
 for warp in x['warps']:warp[0]=positions[warp[0]]
 x['cleanup']=core.derive_cleanup(x)
 need(all(x[k]==w[k] for k in w if k not in ('A','B','restore','warps','cleanup')),'unexpected field change')
 need(all(a[1:]==b[1:] for a,b in zip(x['warps'],w['warps'])) and len(x['warps'])==len(w['warps']),'native operator drift')
 return x

def forced_site_frames(w,records,t):
 """Exact backward cap propagation for the two connected replacement gates."""
 nodes,where,baseline=t.tracing(w);result=[]
 for rec in records:
  section,indices=rec['section'],rec['indices'];bounds={};old=Counter()
  for r in rec['support']:
   hits=[i for i in indices if r in t.touched(w[section][i])];seq=nodes[r];a=where[((section,hits[0]),r)];b=where[((section,hits[-1]),r)]
   need(seq[b+1][1]!='map','unanchored native successor');bounds[r]=(seq[a][2],seq[b+1][3])
   for j in range(a,b+2):old[t.rank(seq[j][3])-t.rank(seq[j][2])]+=1
  current={r:p for r,(p,q) in bounds.items()};bill=Counter();flag=[];intervals=[]
  for number,g in enumerate(rec['replacement']):
   a,b=g[1:3];lo=t.join(current[a],current[b]);hi=bounds[a][1]&bounds[b][1]
   if number==0:
    # The first common frame passes through the shared register into gate2.
    # Therefore it must also lie below both gate2 successor caps.
    need(len(set(g[1:3])&set(rec['replacement'][1][1:3]))==1,'two-gate chain')
    for r in rec['replacement'][1][1:3]:hi&=bounds[r][1]
   need(lo==hi,'non-singleton interval: expand certificate explicitly')
   intervals.append({'lower':list(t.basis(lo)),'upper':list(t.basis(hi))})
   for r in (a,b):bill[t.rank(lo)-t.rank(current[r])]+=1;current[r]=lo
   flag.append(list(t.basis(lo)))
  for r,(p,q) in bounds.items():bill[t.rank(q)-t.rank(current[r])]+=1
  need(all(bill[r]==old[r] for r in range(1,10)),'fixed-boundary paid change')
  result.append({'section':section,'indices':indices,'unique_flag':flag,'intervals':intervals,'profile_delta':{}})
 return result

def check_receipt(w,core,sep):
 r=sep.inspect_word(core,w);need(r['profile']==PROFILE and r['helper_widths']==WIDTHS,'current source bill');return r

def provider(tag,full=True):
 t,core,tariff,cone,sep=load_engines();w=word(tag);records=[sep.certify_site(w,s) for s in sep.SITES]
 known=contract(w,records[:1],core);changed=contract(w,records,core)
 receipts={name:check_receipt(x,core,sep) for name,x in (('source',w),('credited_3998',known),('combined',changed))}
 before,after=receipts['credited_3998']['primitive_counts'],receipts['combined']['primitive_counts']
 need((sum(before[s]['add']-after[s]['add'] for s in ('A','B','restore')),before['cleanup']['add']-after['cleanup']['add'])==(7,5),'incremental scalar saving')
 frames=forced_site_frames(w,records,t)
 old_cone,new_cone=cone.census(w),cone.census(changed)
 need(old_cone['total_hyperplanes']==new_cone['total_hyperplanes']==13285 and old_cone['rejected']==new_cone['rejected'],'cone partition changed')
 need(len(old_cone['candidates'])==len(new_cone['candidates'])==5,'cone survivor count')
 # B contractions remove exactly two gates before every surviving cone event.
 for old,new in zip(old_cone['candidates'],new_cone['candidates']):
  expected=deepcopy(old)
  for e in expected['edits']:
   need(e['section']=='B' and e['index']>=54,'cone remap domain');e['index']-=2
  need(expected==new,'cone candidates not exact remapping')
 if full:
  for name,x in (('source',w),('credited_3998',known),('combined',changed)):
   receipts[name]['semantics']=sep.semantics(core,x);print('CHECKED',tag,name,'full723',flush=True)
  need(len({r['semantics']['ordinary_matrix_sha256'] for r in receipts.values()})==1 and len({r['semantics']['dual_matrix_sha256'] for r in receipts.values()})==1,'full operator equality')
 witnesses=[]
 for row in new_cone['candidates']:
  x=cone.apply(changed,row)
  if full:cone.semantics(x)
  witnesses.append({'register':row['register'],'word_sha256':digest(x),'local_delta':row['local_delta'],'owner_debit':row['owner_debit'],'optimistic_complete_delta':row['optimistic_complete_delta']})
 return {'provider':tag,'sites':records,'words':receipts,'fixed_boundary_frames':frames,'cone':new_cone,'cone_witnesses':witnesses,'scalar_saving_vs_3998':{'forward':7,'cleanup':5},'new_kappa':False}

def audit(tag,full=True):
 actual=provider(tag,full);expected=read(ROOT/'RESULT.json')['providers'][tag]
 if not full:
  expected=deepcopy(expected)
  for r in expected['words'].values():r.pop('semantics',None)
 need(canonical(actual)==canonical(expected),'result mismatch');return actual

def main():
 p=argparse.ArgumentParser();p.add_argument('--provider',choices=('base','extra'),default='base');p.add_argument('--quick',action='store_true');p.add_argument('--record',action='store_true');p.add_argument('--tariff',action='store_true');a=p.parse_args()
 if a.record:
  t,c,v,k,s=load_engines();result={'schema_version':1,'tariff':k.tariff_check(),'providers':{tag:provider(tag,True) for tag in ('base','extra')}}
  (ROOT/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print('WROTE combined result')
 elif a.tariff:
  t,c,v,k,s=load_engines();need(k.tariff_check()==read(ROOT/'RESULT.json')['tariff'],'tariff mismatch');print('PASS_OWNER_DUAL_2551_PATTERNS exact_net_zero')
 else:
  audit(a.provider,not a.quick);print('PASS_A2_CONE_COMPOSITION',a.provider,'full='+str(not a.quick),'no_new_kappa')
if __name__=='__main__':
 try:main()
 except Exception as e:print('FAIL_A2_CONE_COMPOSITION '+str(e),file=sys.stderr);raise SystemExit(1)
