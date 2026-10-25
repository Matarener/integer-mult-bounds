#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent finite-frame controls and production-path rejection tests."""
import itertools,json,sys
from collections import Counter
from copy import deepcopy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import verify as V
S=V.S;R=S.R

def need(ok,why):
    if not ok:raise ValueError(why)
def rejects(f,why):
    try:f()
    except Exception:return
    raise ValueError('accepted '+why)
def independent_span(vs):
    pts={0}
    for v in vs:pts|={x^v for x in tuple(pts)}
    return frozenset(pts)
def independent_interval(lo,hi):
    # Choose quotient representatives greedily, then enumerate every subset of
    # all quotient vectors. Dimension<=3 makes this independent 2^(2^q) check tiny.
    have=independent_span(lo);initial=have;reps=[]
    for v in sorted(independent_span(hi)):
        if v not in have:reps.append(v);have=independent_span(list(lo)+reps)
    qpoints=sorted(independent_span(reps));out=set()
    for bits in range(1<<len(qpoints)):
        pts=independent_span(list(lo)+[x for i,x in enumerate(qpoints) if bits>>i&1]);out.add(sum(1<<x for x in pts))
    return out

def main():
    C,A=V.setup();intervals=set();rows=0
    for tag in ('base','extra'):
        result=json.loads((V.P/f'RESULT-{tag}.json').read_text())
        for lo,hi in result['intervals']:
            intervals.add((tuple(lo),tuple(hi)))
        # Independent min-basis reconstruction of every exact sign certificate.
        for row in result['single_profiles']+result['joint_profiles']:
            d=row['delta'];caps=[sum(min(k,j)*n for k,n in enumerate(d)) for j in range(1,10)]
            need(caps==row['caps'],'caps');need(sum(k*n for k,n in enumerate(d))==0,'mass')
            need(all(sum(caps[:j])>=0 for j in range(1,9)),'nonnegative min-basis coefficients');rows+=1
        w=V.load(tag);nodes,where,bill,addresses,pairs=S.topology(w)
        # Independent graph definition: the selected gates share a register and
        # its chronological address list has no intervening fixed event.
        found=set()
        allowed=set(addresses)
        for r,seq in nodes.items():
            positions={x[0]:i for i,x in enumerate(seq) if x[0] in allowed}
            ordered=sorted(positions,key=positions.get)
            for a,b in zip(ordered,ordered[1:]):
                if positions[b]==positions[a]+1:found.add((a,b))
        need(found==set(pairs),'coupled graph')
        # Source, scalar, frame and cleanup faults reach real production checks.
        row=json.loads((V.P/'SOURCES.json').read_text())['snapshots'][0]
        raw=(V.P/row['local']).read_bytes();rejects(lambda:V.authenticate(raw+b' ',row),'source corruption')
        a,b,fa,fb,_=result['whole_word_samples'][0]
        changed=deepcopy(w);changed[a[0]][a[1]][3]+=1
        need(V.scalar_projection(changed)!=V.scalar_projection(w),'scalar mutation missed')
        bad=deepcopy(w);bad[a[0]][a[1]][-1]=[];rejects(lambda:C.frame_bill(bad),'illegal lowered frame')
        bad=deepcopy(w);bad['cleanup']=[]
        need(C.derive_cleanup(bad)!=bad['cleanup'],'cleanup mutation missed')
    for lo,hi in intervals:need(independent_interval(lo,hi)==set(S.frames(R.span(lo),R.span(hi))),'independent quotient enumeration')
    # A genuinely simultaneous legal pair with no legal single-edit intermediate.
    # This is an abstract control, not a staged544 occurrence.
    a=('A',0);b=('A',1);line1=R.span((1,));line2=R.span((2,));full=R.span((1,2))
    tracks=[(0,1,(a,b),full,'climb')];old=Counter({1:2,0:1})
    need(S.bill_delta(tracks,old,{a:line2,b:line2})==(0,)*10,'crossed-line final legal')
    need(S.direct_orders(tracks,old,a,b,line2,line2,line1,line1)==(False,False),'crossed-line detector')
    rejects(lambda:S.bill_delta(tracks,old,{a:line2,b:line1}),'first crossed-line intermediate')
    rejects(lambda:S.bill_delta(tracks,old,{a:line1,b:line2}),'second crossed-line intermediate')
    # Explicit dimension-only false positive on actual B362/B366.
    w=V.load('base');nodes,where,*_=S.topology(w);a=('B',362);b=('B',366)
    bounds,tracks,old=S.model(w,nodes,where,(a,b));la,ha=bounds[a];lb,hb=bounds[b];ha&=hb;lb=R.join(lb,la)
    need(R.rank(la)<=4<=R.rank(ha) and R.rank(lb)<=4<=R.rank(hb),'naive 4,4 admission')
    candidates=[(fa,fb) for fa in S.frames(la,ha) for fb in S.frames(lb,hb) if R.rank(fa)==4 and R.rank(fb)==4 and R.contained(fa,fb)]
    need(not candidates,'false-positive actual frame assignment')
    minimum=R.rank(lb)+max(0,4-R.rank(R.join(la,ha&lb)))
    need(minimum==5,'dimension incompatibility witness')
    # Paid rank exchange has strict concavity sign in the intended direction.
    exchange=(0,1,-2,1,0,0,0,0,0,0)
    need(not R.all_power_nonnegative(exchange),'favorable rank exchange wrongly certified non-improving')
    need(R.all_power_nonnegative(tuple(-x for x in exchange)),'reverse exchange sign')
    print('PASS_STATIONARY_CONTROLS',{'intervals':len(intervals),'sign_rows':rows,'crossed_flag':True,'false_4_4_requires':minimum})
if __name__=='__main__':main()
