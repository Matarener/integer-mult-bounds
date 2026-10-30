#!/usr/bin/env python3
"""Independent determinant/span-set audit; no producer algebra imports.

Prepared by flyingviper with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import combinations
from pathlib import Path
import json
Q=[(1,1,-1),(1,-1,1),(-1,1,1),(0,1,-1),(1,0,-1),(1,-1,0)]
B=[(1,1,1),(2,1,1),(1,3,1),(0,1,1),(1,0,1),(2,1,0)]
M=((0,0,0,0),(0,1,2,3),(0,2,3,1),(0,3,1,2))
def det(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def need(x,m):
 if not x:raise ValueError(m)
for a,b in combinations(Q,2):need(any(a[i]*b[j]!=a[j]*b[i]for i,j in combinations(range(3),2)),'pair dependence')
old=[[],[],[]];new=[[],[],[]]
for mask in range(64):
 ids=[i for i in range(6)if mask>>i&1]
 full=any(det(*(Q[i]for i in tri))for tri in combinations(ids,3))
 span={(0,0,0)}
 for i in ids:span={tuple(v[j]^M[t][B[i][j]]for j in range(3))for v in span for t in range(4)}
 for j in range(3):
  e=tuple(int(k==j)for k in range(3))
  rational=full or any(det(Q[a],Q[b],e)==0 for a,b in combinations(ids,2))
  if rational:old[j].append(mask);need(e in span,'lost target')
  if e in span:new[j].append(mask)
axes=[tuple(int(i==j)for i in range(3))for j in range(3)]
AQ=axes+Q;AB=axes+B
for a,b in combinations(AQ,2):need(any(a[i]*b[j]!=a[j]*b[i]for i,j in combinations(range(3),2)),'augmented pair dependence')
changes=[]
for mask in range(512):
 ids=[i for i in range(9)if mask>>i&1]
 rq=min(len(ids),2)
 if any(det(*(AQ[i]for i in tri))for tri in combinations(ids,3)):rq=3
 span={(0,0,0)}
 for i in ids:span={tuple(v[j]^M[t][AB[i][j]]for j in range(3))for v in span for t in range(4)}
 need(len(span)in(1,4,16,64),'field span cardinality')
 rb=(1,4,16,64).index(len(span))
 if rq!=rb:changes.append([mask,rq,rb])
need(changes==[[448,2,3]],'exactly the query-only circuit-hyperplane relaxes')
need([[bool(x)for x in c]for c in Q]==[[bool(x)for x in c]for c in B],'source coordinate support equality')
primary=json.loads(Path(__file__).with_name('RESULT.json').read_text(encoding='utf-8'))
for j in range(3):need(old[j]==primary['requests'][j]['Q_recoverable_masks'] and new[j]==primary['requests'][j]['F4_recoverable_masks'],'independent receipt discrepancy')
print(json.dumps({'status':'PASS_INDEPENDENT_DOWLING_SELECTIVE_TRANSFER','target_support_requests':192,'augmented_subsets':512,'rank_changes':changes,'old_counts':list(map(len,old)),'new_counts':list(map(len,new)),'method':'integer determinants and explicit F4 span sets; no producer imports or elimination'}))
