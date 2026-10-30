#!/usr/bin/env python3
"""Second representation for current-word composition and singleton frames.
Uses ToikY PR4019's separately implemented point-set/coordinate checker,
unchanged and credited. No primary verifier, trace or dirty auditor is imported.
Chris R / Clear1nsight, substantial OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json,types
ROOT=Path(__file__).resolve().parent
PINS={'base':'08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0','extra':'d83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299'}
CHECKER_SHA='47bc548f28200f86d28f1f5f8eb466e588bdc01e31f70580280ea6ac72f400a6'
PROFILE={'1':2482,'2':712,'3':218,'4':109,'5':20,'8':8}
WIDTHS={'5':28,'6':18,'7':53,'8':96,'9':213}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def load():
 path=ROOT/'frozen/sep/independent.py';raw=path.read_bytes();need(hashlib.sha256(raw).hexdigest()==CHECKER_SHA,'separate checker source')
 m=types.ModuleType('credited_point_set_checker');m.__file__=str(path);exec(compile(raw,str(path),'exec'),m.__dict__);return m

def timelines(w,I):
 live=sorted(set(range(704))-set(w['removed']));zero=frozenset((0,));full=frozenset(range(512));current={};finish={};seq={r:[] for r in live}
 for r in live:
  current[r]=I.span((w['ports'][r],)) if r<112 else zero
  finish[r]=frozenset(x for x in range(512) if (x&w['ports'][r-112]).bit_count()%2==0) if 112<=r<224 else full
 for r,b in w['start_extra'].items():current[int(r)]=I.span(tuple(b))
 for r,b in w['helper_final'].items():finish[int(r)]=I.span(tuple(b))
 def event(r,address,frame):
  seq[r].append((address,current[r],frame));current[r]=frame
 def scalar(section,i,g):
  for r in I.support(g):event(r,(section,i),I.span(tuple(g[-1])))
 for i,g in enumerate(w['A']):
  if g[0]=='warp':
   event(g[1],('A-native-in',i),I.span(tuple(g[3])));event(g[1],('A-native-out',i),I.span(tuple(g[4])))
  else:scalar('A',i,g)
 levels={112+int(r):I.span(tuple(b)) for r,b in w['target_levels'].items()}
 for r in range(112,224):event(r,('target',r),levels.get(r,zero))
 for r,b in zip(w['centers'],w['center_frames']):event(r,('centre',r),I.span(tuple(b)))
 warps={}
 for j,warp in enumerate(w['warps']):warps.setdefault(warp[0],[]).append((j,warp))
 for i in range(len(w['B'])+1):
  for j,g in warps.get(i,[]):
   event(g[1],('B-native-in',j),I.span(tuple(g[3])));event(g[1],('B-native-out',j),I.span(tuple(g[4])))
  if i<len(w['B']):scalar('B',i,w['B'][i])
 for i,g in enumerate(w['restore']):scalar('restore',i,g)
 for r in live:event(r,('terminal',r),finish[r])
 return seq

def singleton_check(w,records,I):
 seq=timelines(w,I)
 for rec in records:
  bounds={};section=rec['section'];indices=rec['indices'];old=Counter()
  for r in rec['support']:
   positions=[j for j,(addr,p,q) in enumerate(seq[r]) if addr[0]==section and addr[1] in indices]
   a,b=min(positions),max(positions);bounds[r]=(seq[r][a][1],seq[r][b+1][2])
   for _,p,q in seq[r][a:b+2]:old[I.rank(q)-I.rank(p)]+=1
  cur={r:p for r,(p,q) in bounds.items()};bill=Counter()
  for number,g in enumerate(rec['replacement']):
   a,b=g[1:3];lo=frozenset(x^y for x in cur[a] for y in cur[b]);hi=bounds[a][1]&bounds[b][1]
   if number==0:
    need(len(set(g[1:3])&set(rec['replacement'][1][1:3]))==1,'independent two-gate chain')
    for r in rec['replacement'][1][1:3]:hi=hi&bounds[r][1]
   need(lo==hi==I.span(tuple(g[-1])),'independent singleton interval')
   for r in (a,b):bill[I.rank(lo)-I.rank(cur[r])]+=1;cur[r]=lo
  for r,(p,q) in bounds.items():bill[I.rank(q)-I.rank(cur[r])]+=1
  need(all(old[k]==bill[k] for k in range(1,10)),'independent full local invoice')
 return len(records)

def main():
 I=load();certificate=json.loads((ROOT/'RESULT.json').read_bytes());results={}
 for tag in ('base','extra'):
  raw=(ROOT/f'inputs/WORD-{tag}.json.gz').read_bytes();need(hashlib.sha256(raw).hexdigest()==PINS[tag],'current input hash');w=json.loads(gzip.decompress(raw),object_pairs_hook=I.no_duplicates)
  expected=certificate['providers'][tag];records=I.certified_sites(w);need(records==expected['sites'],'site receipt')
  changed=I.reconstruct(w,records);known=I.reconstruct(w,records[:1]);traces=[]
  for name,x in (('source',w),('credited_3998',known),('combined',changed)):
   profile,widths,trace=I.frame_audit(x);need(profile==PROFILE and widths==WIDTHS,'independent current complete bill');traces.append(trace)
   need(x['cleanup']==I.inverse_cleanup(x),'independent projected cleanup')
   ref=expected['words'][name];need(I.sha(x)==ref['canonical_word_sha256'] and I.sha(x['cleanup'])==ref['cleanup_sha256'],'independent reconstructed digests')
  need(traces[0]==traces[1]==traces[2] and len(traces[0])==149,'149 fixed full-register boundary states')
  need(singleton_check(w,records,I)==8,'singleton sites')
  controls=I.controls(w,records,changed)
  results[tag]={'local_identities':8,'singleton_pairs':8,'boundary_states':149,'semantic_rejections':controls}
 print('PASS_SEPARATE_COMPOSITION '+json.dumps(results,sort_keys=True))
if __name__=='__main__':main()
