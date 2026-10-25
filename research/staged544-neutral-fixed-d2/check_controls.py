#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent event-order oracle, reduction coverage and adversarial controls."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
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
def independent_sign(delta):
    caps=[sum(n*min(r,k) for r,n in enumerate(delta)) for k in range(1,10)]
    prefixes=[sum(caps[:j]) for j in range(1,9)]
    return sum(r*n for r,n in enumerate(delta))==0 and all(x>=0 for x in prefixes),caps,prefixes
row=json.loads((P/'SOURCES.json').read_text())['snapshots'][0]
rejects(lambda:V.authenticate((P/row['local']).read_bytes()+b'x',row),'source_corruption')
for tag in ('base','extra'):
    word=V.load(tag);variable,counts,_=S.first_moves(word);original_hash=S.digest(word)
    nodes,where,bill=R.tracing(word);expected=set();rejected=0
    # Independent direct monotone event itinerary after literal block permutation.
    # No primary first-frame equality filter or first price routine is used.
    for sec in S.PHASES:
      gates=word[sec]
      for a,b in R.segments(word,sec):
       for i in range(a,b):
        g=gates[i]
        if g[0]!='add':continue
        for cut in (i-2,i+3):
         if not a<=cut<=b:continue
         crossed=gates[i+1:cut] if cut>i else gates[cut:i]
         if not all((g[1]!=h[2] and h[1]!=g[2]) if h[0]=='add' else (h[0]=='scale' and h[2]!=0) for h in crossed):continue
         lo,hi=min(i,cut),max(i+1,cut)
         old=gates[lo:hi];new=(old[1:]+old[:1]) if cut>i else (old[-1:]+old[:-1])
         regs=set(r for h in old for r in (h[1:3] if h[0]=='add' else h[1:2]))
         valid=True;delta=Counter()
         for r in regs:
          positions=[j for j in range(lo,hi) if r in (gates[j][1:3] if gates[j][0]=='add' else gates[j][1:2])]
          start=nodes[r][where[((sec,positions[0]),r)]][2]
          end=nodes[r][where[((sec,positions[-1]),r)]+1][3]
          for sign,sequence in ((-1,old),(1,new)):
           before=start
           for h in sequence:
            if r not in (h[1:3] if h[0]=='add' else h[1:2]):continue
            frame=R.span(tuple(h[-1]))
            if before&~frame:valid=False;break
            d=frame.bit_count().bit_length()-before.bit_count().bit_length()
            if d:delta[d]+=sign
            before=frame
           if before&~end:valid=False
           if valid:
            d=end.bit_count().bit_length()-before.bit_count().bit_length()
            if d:delta[d]+=sign
         if valid:
          need(not any(delta.values()),'independent first not neutral')
          expected.add((sec,i,cut,R.span(tuple(g[-1]))))
         else:rejected+=1
    actual={(sec,i,cut,frame) for sec,i,cut,frame,delta,_ in variable}
    need(actual==expected and rejected==counts['frame_rejected'],'independent first admission differs')
    checks['independent_first_records']+=len(expected);checks['independent_rejections']+=rejected
    # Select every phase, direction and crossed operation pattern present.
    chosen={}
    for ordinal,v in enumerate(variable):
        sec,i,cut,frame,delta,_=v;lo,hi=min(i,cut),max(i+1,cut)
        pattern=''.join(g[0][0] for g in word[sec][lo:hi])
        chosen.setdefault((sec,cut>i,pattern),ordinal)
    for ordinal in sorted(set(chosen.values())):
        sec,i,cut,frame,delta,_=variable[ordinal];lo,hi=min(i,cut),max(i+1,cut)
        middle=S.first_apply(word,sec,i,cut)
        retained=R.apply_move(word,sec,i,cut,word[sec][i][-1])
        need(middle==retained and S.digest(word)==original_hash,'persistent-copy source equality')
        checks['persistent_copy_full_word_equality']+=1
        trace=R.tracing(middle);need(C.frame_bill(middle)[0]==bill==trace[2],'independent full frame invoice')
        inc=S.first_trace(word,middle,(nodes,where,bill),sec,i,cut)
        need(inc==trace,'incremental full trace mismatch')
        geometry=S.first_geometry(word,middle,list(S.geometry(word,sec,(nodes,where,bill))),inc,sec,i,cut)
        need(geometry==list(S.geometry(middle,sec,trace)),'incremental full geometry mismatch')
        checks['incremental_trace_and_geometry']+=1
        # Exact reach, frame intervals and prices at both interior gaps, without
        # the optimized original-bound/partial-block reach selection.
        outside=[j for j,g in enumerate(middle[sec]) if g[0]=='add' and not lo<=j<hi and any(a<=j<b for a,b in R.segments(word,sec))]
        exact=list(S.candidates(middle,sec,outside,window=(lo+1,lo+2),trace=trace))
        bounds=S.corridor_bounds(word);fast=[]
        for target in (lo+1,lo+2):
            selected=[]
            for j in outside:
                a,b=bounds[sec,j];g=middle[sec][j]
                legal=(b>=lo and all(R.crosses(g,h) for h in middle[sec][lo:target])) if j<lo else (a<=hi and all(R.crosses(g,h) for h in middle[sec][target:hi]))
                if legal:selected.append(j)
            fast.extend(S.candidates(middle,sec,selected,window=(target,target),trace=trace,trusted=True))
        need(sorted(exact)==sorted(fast),'two-interior-cut reach/price omission '+repr((ordinal,sec,i,cut,list(set(exact)-set(fast))[:2],list(set(fast)-set(exact))[:2])))
        checks['full_interior_gap_scans']+=1;checks['interior_gap_prices_compared']+=len(exact)
        # Check the baseline-counterpart reduction on deterministic outside ADDs,
        # comparing masks and prices, not merely sign results.
        subset=outside[::max(1,len(outside)//8)]
        before={(j,t,d,L,H,delta) for j,t,d,L,H,delta in S.candidates(word,sec,subset) if t not in (lo+1,lo+2)}
        after={(j,t,d,L,H,delta) for j,t,d,L,H,delta in S.candidates(middle,sec,subset,trace=trace) if t not in (lo+1,lo+2)}
        need(before==after,'outside-gap baseline counterpart mismatch')
        checks['baseline_counterpart_price_comparisons']+=len(before)
    # Real production omission of the second interior cut must change a receipt.
    src=(P/'search.py').read_text();old='for target in (lo+1,lo+2):'
    need(src.count(old)==1,'gap mutation preimage')
    mutant=types.ModuleType('omitted_gap');mutant.__file__=str(P/'search.py')
    exec(compile(src.replace(old,'for target in (lo+1,):'),mutant.__file__,'exec'),mutant.__dict__)
    good=S.variable_census(word,variable[:1]);bad=mutant.variable_census(word,variable[:1])
    need(S.digest(good)!=S.digest(bad) and good['counts']['second_cut_dimensions']>bad['counts']['second_cut_dimensions'],'second-gap omission not detected')
    checks['production_second_gap_omission']+=1
    # Exact semantic failure controls; derive fresh cleanup for wrong scalar.
    sec,i,cut,frame,_,_=variable[0];middle=R.apply_move(word,sec,i,cut,R.basis(frame));moved=cut-(cut>i)
    middle['cleanup']=C.derive_cleanup(middle);middle['report']['local_profile']={str(r):n for r,n in bill.items()}
    A.semantics(C,middle);checks['full_dirty_control_words']+=1
    bad=deepcopy(middle);bad[sec][moved][3]*=-1;bad['cleanup']=C.derive_cleanup(bad)
    rejects(lambda:A.semantics(C,bad),'wrong_scalar_fresh_cleanup')
    bad=deepcopy(middle);bad['cleanup']=[]
    rejects(lambda:A.semantics(C,bad),'omitted_cleanup_arbitrary_dirty')
    bad=deepcopy(middle);ns,ad,_=R.tracing(bad)
    phase,j=next((phase,j) for phase in S.PHASES for j,g in enumerate(bad[phase]) if g[0]=='add' and any(ns[r][ad[((phase,j),r)]][2]!=1 for r in R.touched(g)))
    bad[phase][j][-1]=[];rejects(lambda:C.frame_bill(bad),'illegal_frame')
    j=next(j for j in range(word['prelude_events'],len(word['A'])-1) if word['A'][j][0]=='add' and not R.crosses(word['A'][j],word['A'][j+1]))
    rejects(lambda:R.apply_move(word,'A',j,j+2,word['A'][j][-1]),'noncommuting_barrier')
    # Credited retained Jeremy Kothe PR2957 rollback/recovery positive fixture.
    oldword=deepcopy(word);g,h=oldword['A'][4043:4045]
    oldword['A'][4043:4045]=[h[:-1]+[g[-1]],g];oldword['cleanup']=C.derive_cleanup(oldword)
    before,widths,*_=C.frame_bill(oldword);oldword['report']['local_profile']={str(r):n for r,n in before.items()}
    recovered=R.apply_move(oldword,'A',4043,4045,h[-1]);recovered['A'][4044][-1]=deepcopy(h[-1]);recovered['cleanup']=C.derive_cleanup(recovered)
    after,widths2,*_=C.frame_bill(recovered);recovered['report']['local_profile']={str(r):n for r,n in after.items()}
    need(recovered==word and widths==widths2,'credited positive source recovery')
    delta=tuple(after.get(r,0)-before.get(r,0) if r else 0 for r in range(10))
    need(delta==(0,1,-1,-1,1,0,0,0,0,0) and not independent_sign(delta)[0],'credited positive sign')
    A.semantics(C,oldword);A.semantics(C,recovered);checks['credited_positive_dirty_words']+=2
    receipt=P/('RESULT-'+tag+'.json')
    need(receipt.is_file(),'missing committed full provider receipt')
    if receipt.exists():
      for row in json.loads(receipt.read_text())['pair_census']['variable_frame']['profiles']:
        ok,caps,prefixes=independent_sign(row['delta'])
        need(ok and caps==row['caps'] and prefixes==row['prefixes'] and row['certificate'],'independent result sign')
        checks['independent_result_signs']+=1
for c in (Fraction(-3,2),Fraction(1,4)):
 for q in (Fraction(-2),Fraction(1,2)):
  for r in range(3):
   for right in (False,True):
    add=['add',0,1,c.numerator,c.denominator,[]];scale=['scale',r,q.numerator,q.denominator,[]];other=['add',2,1,1,1,[]]
    gates=[add,scale,other] if right else [other,scale,add]
    toy={'A':gates,'B':[],'restore':[],'prelude_events':0,'warps':[]}
    changed=R.apply_move(toy,'A',0 if right else 2,3 if right else 0,[])
    D.block_equal(gates,changed['A']);checks['scale_three_gate_matrices']+=1
H=V.module('summary_reports',P/'reports.py');census,ledger=H.summaries(P,S)
need(census==json.loads((P/'CENSUS.json').read_text()) and V.normal(ledger)==json.loads((P/'LEDGER.json').read_text()),'source-bound summaries mismatch')
checks['source_bound_census_and_ledger']+=1
print(json.dumps({'status':'PASS_NEUTRAL_FIXED_D2_CONTROLS','checks':dict(sorted(checks.items())),'new_supplier':False},sort_keys=True))
