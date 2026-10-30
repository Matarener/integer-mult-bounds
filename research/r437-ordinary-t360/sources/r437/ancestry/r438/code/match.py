from pathlib import Path
from collections import Counter,deque
import json,gzip,sys,hashlib
H=Path(sys.argv[1]).resolve();PKG=Path(__file__).resolve().parents[1];BASE=PKG/'data';CODE=PKG/'vendor'
sys.path.insert(0,str(CODE));import hosting_k as HK
parent=json.loads(gzip.decompress((H/'nine/GLOBAL-TEMPLATE.json.gz').read_bytes()));sched=[];idx=0
for e in parent['schedule']:
 if e['kind']=='local_cover_sweep':sched.append(dict(kind='local',stage=e['stage'],pair=e['pair']))
 elif e['kind']=='bridge':sched.append(dict(kind='bridge',dst=e['dst'],src=e['src']))
 elif e['kind']=='idle':sched.append(dict(kind='idle',pair=e['pair'],rank=e['rank'],idx=idx));idx+=1
win={k:x for k,x in HK.windows(sched).items()if x[1]>0 and x[2]}
oy,oz,val=HK.load_selection(BASE/'OLD-SELECTION.json','bit');oldslots,oldrem=HK.expand(win,oy,oz,{s:[(r,8)for r in range(439)]for s in range(9)},222)
oldt=json.loads(gzip.decompress((BASE/'BASELINE-HOST-TEMPLATE.json.gz').read_bytes()))
assert [list(x)for x in oldslots]==oldt['hosting']['slots']
assert oldt['live']==28416 and all(n==0 for n in oldt['banks_per_stage'].values())
# Exact new ideal pattern: ten empty rank42 pieces, one with one8-slot,
# all other pieces completely filled. No optimization or new primitive.
y=oy.copy();assert y[6,()]==9 and y[6,(8,)*5]==213
del y[6,()];del y[6,(8,)*5];y[6,()]=10;y[6,(8,)]=1;y[6,(8,)*5]=211
capacity={i:sum(len(p)*n for(j,p),n in y.items()if j==i)for i in win};assert sum(capacity.values())==9*438
# Deterministic integer maxflow with nine real stage supplies and actual
# untouched-window eligibility edges. This constructs a witness, not LP cost.
N=30;src=0;sink=29;cap=[[0]*N for _ in range(N)]
for s in range(9):cap[src][1+s]=438
for i,(_,_,st)in win.items():
 cap[15+i][sink]=capacity[i]
 for s in st:cap[1+s][15+i]=4000
flow=[[0]*N for _ in range(N)];total=0
while True:
 prev=[-1]*N;prev[src]=src;q=deque([src])
 while q and prev[sink]<0:
  u=q.popleft()
  for v in range(N):
   if prev[v]<0 and cap[u][v]-flow[u][v]>0:prev[v]=u;q.append(v)
 if prev[sink]<0:break
 amount=10**9;v=sink
 while v!=src:u=prev[v];amount=min(amount,cap[u][v]-flow[u][v]);v=u
 v=sink
 while v!=src:u=prev[v];flow[u][v]+=amount;flow[v][u]-=amount;v=u
 total+=amount
assert total==3942
z={(i,8,s):flow[1+s][15+i]for i in win for s in range(9)if flow[1+s][15+i]>0}
proxy=sum(n*(HK.cost(win[i][1],64)-HK.cost(win[i][1]-sum(p),64))for(i,p),n in y.items())
HK.save_selection(H/'SELECTION.json','bit',y,z,proxy)
slots,rem=HK.expand(win,y,z,{s:[(r,8)for r in range(438)]for s in range(9)},222)
assert len(slots)==3942 and set((s,h)for _,_,_,_,s,h in slots)==set((s,h)for s in range(9)for h in range(438))
out=dict(status='ACTUAL_INTEGER_STAGE_WINDOW_MATCHING_PASS_NO_SOLVER',baseline_slotlist_exact_match=True,baseline_slots=3951,new_slots=len(slots),flow=total,patterns=[[i,list(p),n]for(i,p),n in sorted(y.items())],stage_counts=[[i,w,s,n]for(i,w,s),n in sorted(z.items())],remaining_idle=dict(Counter(rem.values())),windows={i:[p,r,sorted(st)]for i,(p,r,st)in win.items()},new_stock_W=28416,no_new_grammar=True,scope='Existing HK.expand packs offsets from0 so every remaining idle is contiguous in the inherited pending-idle ordering; actual emitter/auditor next.')
(H/'MATCHING.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(out,indent=2))
