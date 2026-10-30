#!/usr/bin/env python3
"""Independent cut58 planning matrix audit; no supplier improvement. Apache-2.0."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import json,sys,types,hashlib,argparse
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;R=HERE.parent;S=R/'early-cut58-planning'
p=R/'coupled-tail-independent-review/audit_tail.py';h=types.ModuleType('frozen_tail_review');h.__file__=str(p);exec(compile(p.read_bytes(),str(p),'exec',optimize=0),h.__dict__)
a=h.a;ind=h.ind;qc=h.qc
def need(v,s):
 if not v:raise ValueError(s)
def shadow(E,n,m):
 M=ind.identity(n,m)
 for e in E:
  if e['kind']=='ADD':M[e['dst']]=[ind.add(x,ind.scale(y,Fraction(e['coefficient'])))for x,y in zip(M[e['dst']],M[e['src']])]
  elif e['kind']=='SCALE':M[e['bank']]=[ind.scale(x,Fraction(e['coefficient']))for x in M[e['bank']]]
  elif e['kind']=='BANK_SWAP':i,j=e['banks'];M[i],M[j]=M[j],M[i]
  else:
   U=a.oldexpr(qc.decode(e,m));M[e['bank']]=[ind.product(U,x)for x in M[e['bank']]]
 return M
def run():
 need(a.sha(S/'MANIFEST.json')=='2b5df5dc85e4799116177fac51ffc801357c243189b80563891cb534d1ce6a12','assigned manifest')
 for x in json.loads((S/'MANIFEST.json').read_text())['files']:need(a.sha(S/x['path'])==x['sha256'],'source pin '+x['path'])
 f=json.loads((S/'CUT58.json').read_text());n,m=6,12;E,Ei=f['events'],f['inverse_events'];ad=json.loads((R/'two-site-continuation/ADMITTED-TWO-SITE-FUSIONS.json').read_text())['fixtures'][0]
 clean=lambda es:[{k:v for k,v in e.items()if k!='x_monomial'}for e in es]
 need(ad['q']==2 and clean(E)==ad['events'][58:] and clean(Ei)==ad['inverse_events'][:len(E)],'complete actual admitted source forward/inverse slices')
 used=set();cache={}
 for e in E+Ei:
  if e['kind']in('ADD','SCALE','BANK_SWAP'):continue
  h.unary(e,m);ind.native_check({k:v for k,v in e.items()if k!='x_monomial'},f['native_recipe_pool'],m,cache)
  if e['kind']=='NATIVE':used.add(e['native_recipe_id'])
 need(used==set(f['native_recipe_pool']),'used-only selected source recipes')
 M,Mi=h.replay(E,n,m),h.replay(Ei,n,m);I=ind.identity(n,m)
 need(ind.mm(M,Mi)==I==ind.mm(Mi,M),'both arbitrary-current-input inverse orders')
 need(M==[[ind.old.serialized_family(x)for x in row]for row in f['complete_local_matrix']],'saved matrix')
 need(Mi==[[ind.old.serialized_family(x)for x in row]for row in f['complete_local_inverse']],'saved inverse')
 ops={k:qc.decode(dict(x_monomial=v),m)for k,v in f['operators'].items()};T,K,W,P,RR=[ops[k]for k in('T','K','W','P','reverse_current')]
 need(a.oldexpr(RR@P)==ind.scale(a.oldexpr(T),-1) and a.eq(K@T,T@K)and a.eq(W@T,T@W),'RP=-T and exact commutation including global phase')
 Z={};Id=a.oldexpr(qc.identity(m));expr=a.oldexpr
 target=[[Z for j in range(n)]for i in range(n)]
 target[0][0]=expr(K@T);target[1][0]=ind.scale(expr(W@K@T),-1);target[1][2]=ind.add(expr(T),ind.scale(expr(W@T),-1));target[1][3]=ind.scale(expr(T),-1);target[1][4]=ind.scale(expr(W@T@K),-1)
 target[2][0]=ind.scale(expr(K@T),-1);target[2][2]=expr(T);target[2][3]=ind.scale(expr(T),-1);target[2][4]=ind.scale(expr(T@K),-1)
 target[3][0]=ind.scale(expr(K@W@K@T),-1);target[3][1]=expr(K@T);target[3][2]=ind.add(expr(K@T),ind.scale(expr(K@W@T),-1));target[3][4]=ind.scale(expr(K@W@T@K),-1);target[4][4]=expr(T@K);target[5][5]=expr(T)
 need(M==target,'all six independent matrix rows in prose')
 simple=f['simplified_rank_neutral_events'];need(shadow(simple,n,m)==M,'rank-neutral operator factorization all-f phases')
 hist=Counter(e['rank_per_f']for e in E if e['kind']=='NATIVE');shist=Counter(e['rank_per_f']for e in simple if e['kind']=='NATIVE');pre=sum(e['rank_per_f']for e in ad['events'][:58]if e['kind']=='NATIVE')
 need(pre==54 and hist==shist=={2:9,4:1}and pre+sum(r*c for r,c in hist.items())==76,'actual prefix/suffix and neutral invoices')
 mutant=[e for e in E if 'odd b accumulator'not in e['label']];need(len(mutant)<len(E)and h.replay(mutant,n,m)!=M,'actual accumulator omission rejected')
 wrong=[row[:]for row in target];wrong[1][3]=expr(T);need(wrong!=M,'lost RP minus sign rejected')
 return dict(status='PASS_INDEPENDENT_CUT58_PLANNING_MATRIX',q=2,banks=6,ambient_arity=12,all_current_input_columns=6,literal_inverse_orders=2,phase_scope='All positive f by exact four-residue tensor-family Gaussian algebra',prefix_native_mass=54,suffix_native_histogram=dict(hist),suffix_native_mass=22,whole_native_mass=76,stock=72,neutral_factorization_mass=22,used_selected_source_recipes=len(used),controls=['actual odd b accumulator omission','lost RP=-T sign'],limits='Planning-only. Neutral serialized schema is operator-verified, not independently selected-native admitted. No cost16 suffix, all-q compiler, native saving or kappa claim.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args();out=json.loads(json.dumps(run()));dest=HERE/'AUDIT.json'
 if args.write:dest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 else:need(json.loads(dest.read_text())==out,'saved independent result')
 print(out['status'])
