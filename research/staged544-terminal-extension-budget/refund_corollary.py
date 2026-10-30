"""Optional bounded pivot: terminal rank-one refunds cannot finance extensions.
Reuses verify's exact interval arithmetic; not a second independent implementation.
"""
from collections import Counter
from fractions import Fraction as Q
import json
import verify as v

def check():
    q,pi,mu=v.dual();pi[4]=v.add((1,v.h(1)),(-1,v.h(5)));tight=0;strict=[]
    for cap in (8,16,32,48):
        def rec(w,ns,left):
            if w==10:
                yield tuple(ns),left;return
            for n in range(left//w+1):yield from rec(w+1,ns+[n],left-w*n)
        for ns,left in rec(4,[],cap):
            row=v.add((1,v.h(left)),(-1,mu[cap]),*((-n,pi[w]) for w,n in zip(range(4,10),ns)))
            if not row:tight+=1
            else:
                ab=v.interval(row);v.need(ab[0]>0,'width4 dual infeasibility');strict.append(ab)
    v.need(not v.add((1,pi[4]),(-1,pi[5]),(-1,v.h(1))),'refund exact idle price')
    audit=v.audit_module();sources={}
    for tag in ('base','extra'):
        w=v.read(v.ROOT/f'frozen/WORD-{tag}.json.gz');bill,inventory,chain,start,end=audit.frame_bill(w)
        lower=[];fixed=0
        for key in w['helper_final']:
            r=int(key);charge=chain[r][-1][1];width=audit.dim(end[r])-audit.dim(start[r])
            if charge:
                v.need(charge==1 and width==5,'other protected terminal refund exists')
                # The previous exact frame is the unique dimension-lowering endpoint.
                previous=chain[r][-2][2] if len(chain[r])>=2 else start[r]
                v.need(previous & ~end[r]==0 and audit.dim(previous)==audit.dim(end[r])-1,'refund subspace')
                lower.append(r)
            else:fixed+=1
        v.need(len(lower)==17 and fixed==74,'refund domain')
        sources[tag]={'refundable_registers':sorted(lower),'protected_without_refund':fixed}
    return {'status':'PASS_REFUND_EXTENDED_BUDGET','patterns':tight+len(strict),'symbolic_tight':tight,'strict':len(strict),
      'minimum_positive_reduced_cost':v.brief((min(x[0] for x in strict),min(x[1] for x in strict))),
      'refund_idle_price_minus_terminal_saving':'0 exactly','providers':sources,
      'conclusion':'Any subset of these rank1 refunds ties at best under arbitrary repacking; combining them with positive terminal-only extensions still loses more than the main theorem gap times total added dimensions. Interior changes excluded.'}
def main():
    r=check();expected=v.read(v.ROOT/'REFUND-RESULT.json');v.need(r==expected,'refund result mismatch');print(json.dumps({'status':r['status'],'patterns':r['patterns'],'refundable_per_provider':17},sort_keys=True))
if __name__=='__main__':main()
