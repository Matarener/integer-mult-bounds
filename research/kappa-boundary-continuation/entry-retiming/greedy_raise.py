#!/usr/bin/env python3
"""Literal backward maximum-frame pass with fixed native centre/warp pins."""
from pathlib import Path
import importlib.util,copy,json
p=Path(__file__).with_name('complete_candidate.py');s=importlib.util.spec_from_file_location('candidate',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
w=m.read(Path(__file__).resolve().parents[2]/'kappa-global-continuation/inputs/kappa-consumer-followup/artifact/live-source/research/staged544-producer-return/words/BORROW-WORD-43base.json.gz')
full=m.basis(1<<i for i in range(9));kept=[r for r in range(704) if r not in set(w['removed'])]
nxt={r:full if r<112 or r>=224 else m.basis(x for x in range(1,512) if (x&w['ports'][r-112]).bit_count()%2==0) for r in kept}
for hs,f in w['helper_final'].items():nxt[int(hs)]=m.basis(f)
changes=0

def scalar(e):
 global changes
 e=copy.deepcopy(e);g=m.basis(set.intersection(*(m.span(nxt[r]) for r in m.regs(e))));changes+=g!=m.basis(e[-1]);m.need(m.contained(m.basis(e[-1]),g),'frame lowers');e[-1]=list(g)
 for r in m.regs(e):nxt[r]=g
 return e
w['restore']=list(reversed([scalar(e) for e in reversed(w['restore'])]))
by={}
for j,(pos,r,G,f,t) in enumerate(w['warps']):by.setdefault(pos,[]).append((j,r,f,t))
B=[]
for i in range(len(w['B']),-1,-1):
 if i<len(w['B']):B.append(scalar(w['B'][i]))
 for j,r,f,t in reversed(by.get(i,[])):nxt[r]=m.basis(f)
w['B']=list(reversed(B))
for r,f in list(zip(w['centers'],w['center_frames']))+[(112+j,w['target_levels'].get(str(j),[])) for j in range(112)]:nxt[r]=m.basis(f)
A=[]
for e in reversed(w['A']):
 if e[0]=='warp':A.append(e);nxt[e[1]]=m.basis(e[-2])
 else:A.append(scalar(e))
w['A']=list(reversed(A))
prof,wi=m.profile(w);old={1:2440,2:725,3:224,4:102,5:20,8:8}
delta={r:prof.get(r,0)-old.get(r,0) for r in set(old)|set(prof) if prof.get(r,0)!=old.get(r,0)}
value=sum(n*r**(1-.0017305784372662468) for r,n in delta.items())
print('GREEDY_MAX_FRAME',changes,prof,delta,'discovery_tariff',value)
m.write(Path(__file__).with_name('GREEDY-MAX-FRAMES.json'),{'status':'DISCOVERY_NATIVE_FRAME_PASS','changes':changes,'profile':prof,'delta':delta})
if value < -1e-10:
 w['report']['local_profile']={str(r):n for r,n in prof.items()};m.write(Path(__file__).with_name('GREEDY-MAX-WORD.json.gz'),w)
