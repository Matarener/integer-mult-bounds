#!/usr/bin/env python3
"""Dynamic optimization of direct/native stages in minimal-cut path controllers.

This discovery program uses floating moment scores. Its selected histograms
must separately receive exact interval, native, and phase certificates.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import math
import time

H={4:26,5:2,7:29,8:42,9:309}
L={1:2253,2:515,3:445,4:102,5:40,8:8}
HERE=Path(__file__).resolve().parent


def branch(length,powers):
    if length==0:
        return {0:(0.,0),1:(0.,1)}
    state={i:(0.,(1<<i)-1) for i in range(3)}
    for j in range(1,length+1):
        new={}
        for count,(score,mask) in state.items():
            for even in (0,1):
                val=score+224*(powers[1+8*(count+even)]-powers[8*count]-even*powers[8])
                m=mask|(even<<(2*j))
                for odd in ((0,1) if j<length else (0,)):
                    n=count+even+odd
                    mm=m|(odd<<(2*j+1))
                    if n not in new or val>new[n][0]:
                        new[n]=(val,mm)
        state=new
    return state


def keep_mask(p,cut):
    return (sum(1<<(2*j+1) for j in range(p-1))+
            sum(1<<(2*j) for j in range(cut))+
            sum(1<<(2*(p-1)+j) for j in range(cut,p-1)))


def profile(p,cut,mask):
    n=mask.bit_count();stages=2*p+1
    paid=Counter({k:v*n for k,v in L.items()})
    productive=Counter({k:v*n for k,v in H.items()})
    paid[1]+=112*(stages-n)
    productive[1+8*n]+=224
    for length,reverse in ((cut,False),(p-1-cut,True)):
        for j in range(1,length+1):
            support=list(range(2*j+1))
            if reverse:
                support=[2*p-s for s in support]
            r=sum((mask>>s)&1 for s in support)
            productive[1+8*r]+=224
            r0=sum((mask>>s)&1 for s in support[:-1])
            if r0:
                paid[8*r0]+=224
    for j in range(1,p):
        if (mask>>(2*j))&1:
            paid[8]+=224
    paid={k:v for k,v in sorted(paid.items()) if v}
    productive={k:v for k,v in sorted(productive.items()) if v}
    def margin(kappa):
        tau=1-kappa
        return sum(v*k**tau for k,v in productive.items())-sum(v*k**tau for k,v in paid.items())
    if margin(0)<=0:
        root=0
    else:
        lo,hi=0.,.03
        for _ in range(48):
            mid=(lo+hi)/2
            if margin(mid)>0:
                lo=mid
            else:
                hi=mid
        root=lo
    return dict(p=p,cut=cut,keep=keep_mask(p,cut),native_mask=mask,native_stages=n,
                direct_stages=[s for s in range(stages) if not(mask>>s&1)],
                target=productive,paid=paid,kappa=root,rank_mass_gap=margin(0))


def optimize(max_p,kappa,all_cuts=True):
    powers=[0.]+[r**(1-kappa) for r in range(1,8*(2*max_p+1)+2)]
    delta=112+sum(v*powers[k] for k,v in H.items())-sum(v*powers[k] for k,v in L.items())
    branches=[branch(b,powers) for b in range(max_p)]
    answers=[]
    for p in range(1,max_p+1):
        best=(-float('inf'),None,None)
        cuts=range(p) if all_cuts else ((p-1)//2,)
        for cut in cuts:
            right=p-1-cut
            for nl,(sl,ml) in branches[cut].items():
                for nr,(sr,mr) in branches[right].items():
                    for middle in (0,1):
                        n=nl+nr+middle
                        score=sl+sr+n*delta-112*(2*p+1)+224*powers[1+8*n]
                        if score>best[0]:
                            right_mask=sum(1<<(2*p-s) for s in range(2*right+1) if mr>>s&1)
                            native=ml|right_mask|(middle<<(2*cut+1))
                            best=(score,cut,native)
        row=profile(p,best[1],best[2]);row['score_at_test_kappa']=best[0]
        answers.append(row)
    return answers


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-p',type=int,default=40)
    parser.add_argument('--kappa',type=float,default=.0028)
    parser.add_argument('--balanced-only',action='store_true')
    parser.add_argument('--summary',action='store_true',help='Keep compact per-p profiles and the complete winner')
    parser.add_argument('--out',type=Path,default=HERE/'DIRECT-STAGE-DP.json')
    args=parser.parse_args();started=time.monotonic()
    rows=optimize(args.max_p,args.kappa,not args.balanced_only)
    best=max(rows,key=lambda x:x['kappa'])
    summary_keys=('p','cut','keep','native_mask','native_stages','kappa','rank_mass_gap','score_at_test_kappa')
    saved_rows=[{k:row[k] for k in summary_keys} for row in rows] if args.summary else rows
    result=dict(test_kappa=args.kappa,all_cuts=not args.balanced_only,profiles=saved_rows,best=best,
                seconds=time.monotonic()-started)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    for row in rows:
        print(json.dumps({k:row[k] for k in ('p','cut','kappa','native_stages','direct_stages','score_at_test_kappa')}),flush=True)
    print('BEST',json.dumps(best),flush=True)


if __name__=='__main__':
    main()
