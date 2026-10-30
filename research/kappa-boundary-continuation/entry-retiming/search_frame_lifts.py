#!/usr/bin/env python3
"""One-event monotone frame lifts; exact local child-profile redistribution."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import importlib.util,json,math,copy
p=Path(__file__).with_name('complete_candidate.py');s=importlib.util.spec_from_file_location('candidate',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
w=m.read(Path(__file__).resolve().parents[2]/'kappa-global-continuation/inputs/kappa-consumer-followup/artifact/live-source/research/staged544-producer-return/words/BORROW-WORD-43base.json.gz')
full=m.basis(1<<i for i in range(9));kept=[r for r in range(704) if r not in set(w['removed'])]
cur={r:m.basis([w['ports'][r]]) if r<112 else m.basis(w['start_extra'].get(str(r),[])) for r in kept}
final={r:full if r<112 or r>=224 else m.basis(x for x in range(1,512) if (x&w['ports'][r-112]).bit_count()%2==0) for r in kept}
for hs,f in w['helper_final'].items():final[int(hs)]=m.basis(f)
seq=[]
for i,e in enumerate(w['A']):seq.append(('A',i,e))
for k,h in enumerate(w['centers']):seq.append(('PIN',k,['scale',h,1,1,w['center_frames'][k]]))
for j in range(112):seq.append(('PIN',8+j,['scale',112+j,1,1,w['target_levels'].get(str(j),[])]))
by={}
for j,(pos,r,G,f,t) in enumerate(w['warps']):by.setdefault(pos,[]).append(('WARP',j,['warp',r,j+1,f,t]))
for i in range(len(w['B'])+1):
 seq.extend(by.get(i,[]))
 if i<len(w['B']):seq.append(('B',i,w['B'][i]))
for i,e in enumerate(w['restore']):seq.append(('restore',i,e))
for r,f in final.items():seq.append(('PIN',r,['scale',r,1,1,list(f)]))
prev=[]
for part,i,e in seq:
 prev.append({r:cur[r] for r in m.regs(e)})
 for r in m.regs(e):cur[r]=m.basis(e[-1])
nxt={r:final[r] for r in kept};afters=[None]*len(seq)
for k in range(len(seq)-1,-1,-1):
 part,i,e=seq[k];afters[k]={r:nxt[r] for r in m.regs(e)}
 for r in m.regs(e):nxt[r]=m.basis(e[-2] if e[0]=='warp' else e[-1])
baseprof=m.profile(w)[0];cands=[]
for k,(part,i,e) in enumerate(seq):
 if part not in ('A','B','restore') or e[0]=='warp':continue
 old=m.basis(e[-1]);rs=m.regs(e)
 common=set.intersection(*(m.span(afters[k][r]) for r in rs));g=m.basis(common)
 if len(g)<=len(old):continue
 if not m.contained(old,g):continue
 delta=Counter()
 for r in rs:
  l=len(prev[k][r]);o=len(old);nn=len(afters[k][r]);gg=len(g)
  for rr,cc in [(o-l,-1),(nn-o,-1),(gg-l,1),(nn-gg,1)]:
   if rr:delta[rr]+=cc
 delta={r:n for r,n in delta.items() if n}
 if not delta:continue
 val=sum(n*r**(1-.0017305784372662468) for r,n in delta.items())
 if val < -1e-10:
  changed=copy.deepcopy(w);changed[part][i][-1]=list(g)
  try:prof,wi=m.profile(changed)
  except ValueError:continue
  exactdelta={r:prof.get(r,0)-baseprof.get(r,0) for r in set(prof)|set(baseprof) if prof.get(r,0)!=baseprof.get(r,0)}
  if exactdelta!=delta:continue
  cands.append({'part':part,'index':i,'old_frame':list(old),'new_frame':list(g),'delta':delta,'discovery_tariff_delta':val,'gate':e})
cands.sort(key=lambda x:x['discovery_tariff_delta'])
out=Path(__file__).with_name('FRAME-LIFT-SEARCH.json');m.write(out,{'status':'SCOPED_MONOTONE_SINGLE_EVENT_DISCOVERY','candidate_count':len(cands),'candidates':cands})
print('CANDIDATES',len(cands));print(json.dumps(cands[:15],indent=2))
