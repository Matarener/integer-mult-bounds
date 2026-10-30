#!/usr/bin/env python3
"""Changed first-three normalized source retractions, literal J queries.
Apache-2.0; substantial OpenAI Codex assistance. No native saving assumed.
"""
from joint_algebra import *
from joint_prefix import build,metadata
from delivery_core_probe import inverse_events
from nested_prefix import prefixes,mm as pairmm,I as pI,Z as pZ,mul as pairmul,summ as pairsumm

def transported(q,stage,w):
 n=2*q+2;_,pre=prefixes(q,[1]+[0]*(q-1));M,src,dst=pre[stage-1]
 V=[[pI if i==1 else pZ,pI if i>=3 and i%2 else pZ]for i in range(n)]
 B=pairmm(M,V);u=[pairsumm(pairmul(z,c)for z,c in zip(row,w))for row in B]
 need(u[src]==pI,'changed source functional normalized exactly')
 return u

def build_changed(q,overrides):
 W=build(q);metadata(W.events,q);events=list(W.events);m=W.m
 for stage in(3,2,1):
  if stage not in overrides:continue
  u=transported(q,stage,overrides[stage]);indices=[i for i,e in enumerate(events)if e.get('label','').startswith(f'query{stage} ')]
  first,last=min(indices),max(indices);old=events[first:last+1]
  source=next(e for e in old if e['label']==f'query{stage} source J');s=source['bank']
  delivery=next(e for e in old if e['label']==f'query{stage} delivery');swap=next(e for e in old if e['label']==f'query{stage} source swap')
  fresh=[e for e in old if e['kind']=='NATIVE'and e.get('native_family',{}).get('kind')=='N']
  new=[]
  def a(d,c,label):
   if c:new.append({'kind':'ADD','dst':d,'src':s,'coefficient':str(c),'label':label})
  for bank,(aa,bb)in enumerate(u):
   if bank!=s:a(bank,-aa,f'changed core{stage} scalar entrance')
  new.append(source)
  for bank,(aa,bb)in enumerate(u):
   if bank!=s:a(bank,-bb,f'changed core{stage} J-valued pre-delivery')
  new.extend([delivery,swap]+fresh)
  if any(bb for bank,(aa,bb)in enumerate(u)if bank!=s):
   for bank,(aa,bb)in enumerate(u):
    if bank!=s:a(bank,-bb,f'changed core{stage} pre-continuation')
   f=prefix(m,stage);g=f@j_operator(m)@f.inv()
   e={'kind':'NATIVE','bank':s,'x_monomial':g.data(),'rank_per_f':2,'native_family':{'kind':'J','completed':stage,'inverse':False},'label':f'changed core{stage} retained continuation'};metadata([e],q);new.append(e)
  for bank,(aa,bb)in enumerate(u):
   if bank!=s:a(bank,aa,f'changed core{stage} scalar exit')
  events=events[:first]+new+events[last+1:]
 return W,events
if __name__=='__main__':
 W,E=build_changed(2,{2:[pZ,pI]});M=qc.replay(E,W.n,W.m);Mi=qc.replay(inverse_events(E,W.m),W.n,W.m)
 print('publicchanged',[i for i in(0,2,4,5)if M[i]!=W.M[i]])
 need(mm(M,Mi)==mm(Mi,M)==eye(W.n,W.m),'all original columns and literal inverse')
 G=mono(prefix(W.m,5)@j_operator(W.m))
 print('ranks',[[[(qc.rank(g.polar()),str(v[:2]))for g,v in product(G,Mi[i][j]).items()]for j in(1,3)]for i in(1,3)])

# Durable source-bound dual-core derivative. The exploratory main above is
# intentionally superseded by the separate producer dual_core_caller.py.
def dual_prefix(q,fold=False):
 W,E=build_changed(q,{2:[pZ,pI]})
 if not fold:return W,E
 E=[e for e in E if e['label']not in('changed core2 pre-continuation','changed core2 retained continuation')]
 first=next(i for i,e in enumerate(E)if e['label']=='query2 source J');last=next(i for i,e in enumerate(E)if e['label']=='query3 source J')
 at=next(i for i in range(first,last)if E[i]['kind']=='ADD'and E[i].get('dst')==1 and E[i].get('src')==3 and E[i].get('coefficient')=='-1'and E[i]['label']=='initial nested scalar bridge')
 bridge=E.pop(at);p=next(i for i,e in enumerate(E)if e['label']=='query3 source J')
 E=E[:p+1]+[{'kind':'ADD','dst':2,'src':1,'coefficient':'-1','label':'fold dual-core J fanout into next paid source query'},bridge]+E[p+1:]
 return W,E
