#!/usr/bin/env python3
"""Concentrate native climbs with a literal forward minimum-frame pass."""
from pathlib import Path
import importlib.util,copy,json
p=Path(__file__).with_name('complete_candidate.py');s=importlib.util.spec_from_file_location('candidate',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
w=m.read(Path(__file__).resolve().parents[2]/'kappa-global-continuation/inputs/kappa-consumer-followup/artifact/live-source/research/staged544-producer-return/words/BORROW-WORD-43base.json.gz')
cur={r:m.basis([w['ports'][r]]) if r<112 else m.basis(w['start_extra'].get(str(r),[])) for r in range(704) if r not in set(w['removed'])}; changes=0

def scalar(e):
 global changes
 e=copy.deepcopy(e);g=m.basis(x for r in m.regs(e) for x in cur[r]);changes+=g!=m.basis(e[-1]);e[-1]=list(g)
 for r in m.regs(e):cur[r]=g
 return e
A=[]
for e in w['A']:
 if e[0]=='warp':
  if cur[e[1]]!=m.basis(e[-2]):A.append(['scale',e[1],1,1,e[-2]])
  A.append(e);cur[e[1]]=m.basis(e[-1])
 else:A.append(scalar(e))
for r,f in list(zip(w['centers'],w['center_frames']))+[(112+j,w['target_levels'].get(str(j),[])) for j in range(112)]:
 if cur[r]!=m.basis(f):A.append(['scale',r,1,1,f]);cur[r]=m.basis(f)
w['A']=A
by={}
for j,(pos,r,G,f,t) in enumerate(w['warps']):by.setdefault(pos,[]).append((j,r,f,t))
B=[]
for i in range(len(w['B'])+1):
 for j,r,f,t in by.get(i,[]):
  if cur[r]!=m.basis(f):B.append(['scale',r,1,1,f]);cur[r]=m.basis(f)
  w['warps'][j][0]=len(B);cur[r]=m.basis(t)
 if i<len(w['B']):B.append(scalar(w['B'][i]))
w['B']=B
w['restore']=[scalar(e) for e in w['restore']]
prof,wi=m.profile(w)
old={1:2440,2:725,3:224,4:102,5:20,8:8}
delta={r:prof.get(r,0)-old.get(r,0) for r in set(old)|set(prof) if prof.get(r,0)!=old.get(r,0)}
print('GREEDY_MIN_FRAME',changes,prof,delta,'discovery_tariff',sum(n*r**(1-.0017305784372662468) for r,n in delta.items()))
m.write(Path(__file__).with_name('GREEDY-MIN-FRAMES.json'),{'status':'DISCOVERY_NATIVE_FRAME_PASS','changes':changes,'profile':prof,'delta':delta})
if sum(n*r**(1-.0017305784372662468) for r,n in delta.items()) < -1e-10:
 w['report']['local_profile']={str(r):n for r,n in prof.items()};m.write(Path(__file__).with_name('GREEDY-MIN-WORD.json.gz'),w)
