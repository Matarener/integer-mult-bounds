#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact independent first-frame oracle, dirty-state and invoice failure controls."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from itertools import combinations
import json,types
from pathlib import Path
P=Path(__file__).resolve().parent
V=types.ModuleType('entry');V.__file__=str(P/'verify.py');exec(compile((P/'verify.py').read_bytes(),V.__file__,'exec'),V.__dict__)
S,C,A=V.setup();R=S.R;D=V.module('blocks',P/'dirty_blocks.py');checks=Counter()
def need(ok,why):
    if not ok:raise ValueError(why)
def rejects(fn,label):
    try:fn()
    except (ValueError,C.AuditFailure):checks[label]+=1;return
    raise ValueError('mutation accepted: '+label)
def xor_span(vectors):
    values={0}
    for v in vectors:values|={x^v for x in values}
    return values
def independent_frames(low,high,dimension):
    low_points={x for x in range(512) if low>>x&1};high_points={x for x in range(512) if high>>x&1}
    representatives=[];covered=set(low_points)
    for v in sorted(high_points-low_points):
        if v not in covered:representatives.append(v);covered.update({v^x for x in low_points})
    answer=set()
    for combo in combinations(representatives,dimension-R.rank(low)):
        points={x^y for x in low_points for y in xor_span(combo)}
        if len(points)==1<<dimension:answer.add(sum(1<<x for x in points))
    return answer

def independent_sign(delta):
    caps=[sum(n*min(r,k) for r,n in enumerate(delta)) for k in range(1,10)]
    prefixes=[sum(caps[:j]) for j in range(1,9)]
    return sum(r*n for r,n in enumerate(delta))==0 and all(x>=0 for x in prefixes),caps,prefixes

sources=json.loads((P/'SOURCES.json').read_text())
row=sources['snapshots'][0]
rejects(lambda:V.authenticate((P/row['local']).read_bytes()+b'x',row),'source_corruption')
rejects(lambda:S.frames(1,R.span((1,2,4,8,16)),1),'quotient_resource_guard')
need([len(independent_frames(1,R.span((1,2,4)),d)) for d in range(4)]==[1,7,7,1],'known subspace lattice')
checks['known_lattice']+=1
for tag in ('base','extra'):
    word=V.load(tag);variable,counts,intervals=S.first_moves(word)
    need(variable and all(any(v[4]) and abs(v[2]-(v[2]>v[1])-v[1])==2 for v in variable),'scope includes neutral or wrong displacement')
    for low,high,d in intervals:
        need(set(S.frames(low,high,d))==independent_frames(low,high,d),'all first-frame subspaces')
        checks['independent_frame_intervals']+=1
    # Independent cut enumeration and direct scans of each register's events.
    # No primary candidates/geometry/first_moves routine supplies these prices.
    nodes,where,_=R.tracing(word);expected=set();price_cells=0;neutral_cells=0
    rank=lambda mask:mask.bit_count().bit_length()-1
    for sec in S.PHASES:
      gates=word[sec]
      for lo,hi in R.segments(word,sec):
       occ={}
       for j in range(lo,hi):
        for r in (gates[j][1:3] if gates[j][0]=='add' else gates[j][1:2]):occ.setdefault(r,[]).append(j)
       for i in range(lo,hi):
        g=gates[i]
        if g[0]!='add':continue
        for cut in (i-2,i+3):
         if not lo<=cut<=hi:continue
         crossed=gates[i+1:cut] if cut>i else gates[cut:i]
         legal=all((g[1]!=h[2] and h[1]!=g[2]) if h[0]=='add' else (h[0]=='scale' and h[2]!=0) for h in crossed)
         if not legal:continue
         removal=[0]*10;bounds=[]
         for r in g[1:3]:
          seq=nodes[r];pos=where[((sec,i),r)];a,u=seq[pos][2:4];b=seq[pos+1][3]
          removal[rank(u)-rank(a)]-=1;removal[rank(b)-rank(u)]-=1;removal[rank(b)-rank(a)]+=1
          before=[j for j in occ[r] if j!=i and j<cut];after=[j for j in occ[r] if j!=i and j>=cut]
          a=R.span(tuple(gates[before[-1]][-1])) if before else seq[where[((sec,occ[r][0]),r)]][2]
          b=R.span(tuple(gates[after[0]][-1])) if after else seq[where[((sec,occ[r][-1]),r)]+1][3]
          bounds.append((a,b))
         low=R.join(bounds[0][0],bounds[1][0]);high=bounds[0][1]&bounds[1][1]
         if low&~high:continue
         for d in range(rank(low),rank(high)+1):
          price_cells+=1;delta=removal.copy()
          for a,b in bounds:
           delta[rank(b)-rank(a)]-=1;delta[d-rank(a)]+=1;delta[rank(b)-d]+=1
          delta[0]=0;delta=tuple(delta)
          if not any(delta):neutral_cells+=1;continue
          for frame in independent_frames(low,high,d):expected.add((sec,i,cut,frame,delta))
    actual={(sec,i,cut,frame,delta) for sec,i,cut,frame,delta,_ in variable}
    need(actual==expected and len(actual)==len(variable),'independent first-domain inventory')
    need(price_cells==counts['first_price_cells'] and neutral_cells==counts['neutral_price_cells_excluded'],'independent first price cells')
    checks['independent_first_records']+=len(expected)
    # Direct corridor checks for every generated first: no hidden radius-one start.
    for sec,i,cut,frame,delta,kind in variable:
        crossed=word[sec][i+1:cut] if cut>i else word[sec][cut:i]
        need(len(crossed)==2 and all(R.crosses(word[sec][i],g) for g in crossed),'first corridor')
        ok,caps,prefixes=independent_sign(delta)
        need(ok and any(prefixes),'first is not strictly losing')
        checks['first_scope_and_sign']+=1
    # First-state ordering is deterministic; use one left and one right move.
    for right in (False,True):
        sec,i,cut,frame,delta,_=next(v for v in variable if (v[2]>v[1])==right)
        middle=R.apply_move(word,sec,i,cut,R.basis(frame));lo,hi=min(i,cut),max(i+1,cut)
        D.block_equal(word[sec][lo:hi],middle[sec][lo:hi]);checks['exact_dirty_three_gate_blocks']+=1
        middle['cleanup']=C.derive_cleanup(middle);bill,widths,*_=C.frame_bill(middle)
        middle['report']['local_profile']={str(r):n for r,n in bill.items()}
        A.semantics(C,middle);checks['full_dirty_intermediate_words']+=1
        moved=cut-(cut>i);restored=R.apply_move(middle,sec,moved,i+(moved<i),word[sec][i][-1]);restored[sec][i][-1]=deepcopy(word[sec][i][-1])
        restored['cleanup']=C.derive_cleanup(restored);restored['report']['local_profile']=deepcopy(word['report']['local_profile'])
        need(restored==word,'undo literal source')
        base=C.frame_bill(word)[0];actual=tuple(base.get(r,0)-bill.get(r,0) if r else 0 for r in range(10))
        need(actual==tuple(-n for n in delta),'undo second price')
        need(tuple(a+b for a,b in zip(delta,actual))==S.ZERO,'combined accounting')
        need(not independent_sign(actual)[0],'omitted first loss must look falsely profitable')
        checks['first_loss_accounting_sensitivity']+=1
        bad=deepcopy(middle);bad[sec][moved][3]*=-1;bad['cleanup']=C.derive_cleanup(bad)
        rejects(lambda:A.semantics(C,bad),'wrong_scalar_fresh_cleanup')
        bad=deepcopy(middle);nodes,addresses,_=R.tracing(bad)
        invalid=next((phase,j) for phase in S.PHASES for j,g in enumerate(bad[phase]) if g[0]=='add'
                     and any(nodes[r][addresses[((phase,j),r)]][2]!=1 for r in R.touched(g)))
        bad[invalid[0]][invalid[1]][-1]=[]
        rejects(lambda:C.frame_bill(bad),'illegal_frame')
        bad=deepcopy(middle);bad['cleanup']=[]
        rejects(lambda:A.semantics(C,bad),'omitted_cleanup_arbitrary_dirty')
    # Actual production-path omission of the first loss changes the retained
    # per-state second-price digest; an isolated one-state census suffices.
    mutant=types.ModuleType('omitted_loss');mutant.__file__=str(P/'search.py')
    source=(P/'search.py').read_text();old='delta = tuple(a + b for a, b in zip(first_delta, second_delta))'
    need(source.count(old)==1,'loss mutation preimage')
    exec(compile(source.replace(old,'delta = second_delta'),mutant.__file__,'exec'),mutant.__dict__)
    changed=mutant.variable_census(word,variable[:1],C)
    retained=json.loads((P/('RESULT-'+tag+'.json')).read_text())['pair_census']['variable_frame']['states'][0]
    need(changed['states'][0]['second_histogram_sha256']!=retained['second_histogram_sha256'],'omitted-loss production sensitivity')
    checks['production_first_loss_omission']+=1
    # Actual illegal commutation barrier, checked by production move applier.
    i=next(i for i in range(word['prelude_events'],len(word['A'])-1) if word['A'][i][0]=='add' and not R.crosses(word['A'][i],word['A'][i+1]))
    rejects(lambda:R.apply_move(word,'A',i,i+2,word['A'][i][-1]),'noncommuting_barrier')
    # Existing PR2957 rollback/recovery; credited sensitivity fixture, not a new gain.
    old=deepcopy(word);g,h=old['A'][4043:4045]
    old['A'][4043:4045]=[h[:-1]+[g[-1]],g];old['cleanup']=C.derive_cleanup(old)
    before,widths,*_=C.frame_bill(old);old['report']['local_profile']={str(r):n for r,n in before.items()}
    recovered=R.apply_move(old,'A',4043,4045,h[-1]);recovered['A'][4044][-1]=deepcopy(h[-1]);recovered['cleanup']=C.derive_cleanup(recovered)
    after,widths2,*_=C.frame_bill(recovered);recovered['report']['local_profile']={str(r):n for r,n in after.items()}
    need(recovered==word and widths==widths2,'credited positive source recovery')
    delta=tuple(after.get(r,0)-before.get(r,0) if r else 0 for r in range(10))
    need(delta==(0,1,-1,-1,1,0,0,0,0,0) and not independent_sign(delta)[0],'credited positive sign')
    A.semantics(C,old);A.semantics(C,recovered);checks['credited_positive_dirty_words']+=2
    file=P/('RESULT-'+tag+'.json')
    need(file.is_file(),'missing committed provider receipt')
    result=json.loads(file.read_text())
    for row in result['pair_census']['variable_frame']['profiles']:
        good,caps,prefixes=independent_sign(row['delta'])
        need(good and caps==row['caps'] and prefixes==row['prefixes'] and row['certificate'],'independent combined sign')
        checks['independent_result_signs']+=1
# Three-gate SCALE-conjugation controls in both directions, with shared dirty rows.
for c in (Fraction(-3,2),Fraction(1,4)):
 for q in (Fraction(-2),Fraction(1,2)):
  for r in range(3):
   for right in (False,True):
    add=['add',0,1,c.numerator,c.denominator,[]];scale=['scale',r,q.numerator,q.denominator,[]];other=['add',2,1,1,1,[]]
    gates=[add,scale,other] if right else [other,scale,add]
    toy={'A':gates,'B':[],'restore':[],'prelude_events':0,'warps':[]}
    changed=R.apply_move(toy,'A',0 if right else 2,3 if right else 0,[])
    D.block_equal(gates,changed['A']);checks['scale_three_gate_matrices']+=1
need((P/'CENSUS.json').is_file() and (P/'LEDGER.json').is_file(),'missing committed summaries')
H=V.module('source_reports',P/'reports.py');census,ledger=H.summaries(P,S)
need(census==json.loads((P/'CENSUS.json').read_text()) and V.normal(ledger)==json.loads((P/'LEDGER.json').read_text()),'source-bound summaries differ')
checks['source_bound_census_and_ledger']+=1
print(json.dumps({'status':'PASS_LOSING_FIRST_D2_CONTROLS','checks':dict(sorted(checks.items())),'new_supplier':False},sort_keys=True))
