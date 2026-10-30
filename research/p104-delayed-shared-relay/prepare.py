"""Compose Scratch-net's PR5606 prepared573 retirement with the frozen new word.

PR5606 supplies the elementary preparation mechanism and checker; source bytes
are pinned in SOURCES.json and verify.py checks the exact checker adaptation.
Ali Romman's split machinery and all predecessor notices remain credited.
Adaptation and independent checks prepared with OpenAI Codex for flyingviper.
Apache-2.0.
"""
from pathlib import Path
from copy import deepcopy
from collections import Counter
from fractions import Fraction as Q
import gzip,json,hashlib
import prepared573_local as R

HERE=Path(__file__).resolve().parent

def source_relations(source):
    n=source['public'];P=source['program']
    R.need(n==748 and source['initial'][573]==3 and source['final'][573]==603,'Exact retained rank-two split573')
    sites={}
    for event,terms in [(['MOVE',573,3,595,False],[(573,1),(572,-1),(732,2)]),
                        (['MOVE',573,595,603,False],[(573,1),(572,-1),(710,-2)])]:
        R.need(P.count(event)==1,'Unique paid reconstruction site')
        sites[P.index(event)]=(event,terms)
    rows=[{r:Q(1)} for r in range(n+8)];receipts=[]
    current=source['initial']+[None]*8
    for i,e in enumerate(P):
        if i in sites:
            event,terms=sites[i];v={}
            for r,q in terms:R.add(v,rows[r],Q(q))
            R.need(v=={573:Q(-2)},'Fresh full-input source identity at'+str(i))
            R.need(all(current[r]==event[3] for r,q in terms if r!=573),'Actual reconstruction sources coframed')
            receipts.append({'source_event':i,'move':event,'combination':terms,'original_input_relation':{'573':'-2'}})
        op,r=e[:2]
        if op=='MOVE':current[r]=e[3]
        elif op in ('INIT','CLEAR'):
            rows[r]={};current[r]=e[2] if op=='INIT' else None
        elif op=='SCALE':rows[r]={k:Q(e[-2])*v for k,v in rows[r].items()}
        elif op=='COPY':rows[r]={k:Q(e[-2])*v for k,v in rows[e[2]].items()}
        elif op=='ADD':R.add(rows[r],rows[e[2]],Q(e[-2]))
        else:raise ValueError(op)
    # Check the full incoming arbitrary-input/owned endpoint map as well.
    live=set(source['live'])
    for r,row in enumerate(rows):
        wanted={r:Q(1)} if r<n else {}
        if r-112 in live:wanted[r-112]=Q(1)
        R.need(row==wanted,'Complete source endpoint'+str(r))
    return sites,receipts

def construct(source):
    sites,receipts=source_relations(source);n=source['public']
    word=deepcopy(source);out=[['INIT',573,3]]
    for i,e in enumerate(source['program']):
        if i not in sites:out.append(deepcopy(e));continue
        old,terms=sites[i];f=old[3]
        out.extend([['CLEAR',573,old[2]],['INIT',573,f],['COPY',573,572,'1',f],
                    ['ADD',573,732 if f==595 else 710,'-2' if f==595 else '2',f]])
    out.append(['CLEAR',573,603])
    word.update(schema='p104-composed-prepared-reuse/1',program=out,retired_public=[573],fields=n+8,
                independent_public=[r for r in range(n) if r!=573],owned_roles=[573]+list(range(n,n+8)))
    return word,receipts
