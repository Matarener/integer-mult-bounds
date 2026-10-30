#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Allocate a minimum pool for fixed weighted, half-open helper lifetimes.

Slots can be noncontiguous. This does not infer lifetimes or prove safe cleanup.
Credits: classical interval coloring; T74 pooling PR2655 and P104 audit PR5717
for repository context. Ali Romman with OpenAI Codex assistance.
"""
import argparse
from bisect import bisect_left
from hashlib import sha256
import heapq
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
try:
    from compare_recursive_invoices import require,_pairs,_integer,_not_integer
finally:
    sys.path.pop(0)

MAX_LIVES=512
MAX_WIDTH=10**60
MAX_CAPACITY=MAX_LIVES*MAX_WIDTH


def _certificate_integer(text):
    # Aggregate pool coordinates can exceed one lifetime's width limit.
    # Bound the token before int(), independently of Python's digit limit.
    require(len(text.removeprefix('-'))<=len(str(MAX_CAPACITY)),
            'certificate integer token exceeds pool capacity digit limit')
    value=int(text)
    require(abs(value)<=MAX_CAPACITY,'certificate integer exceeds maximum pool capacity')
    return value


def validate(problem):
    require(type(problem) is dict and problem.keys()=={'schema','contract','lifetimes'} and
            problem['schema']=='integer-mult-helper-lifetimes/v1','invalid lifetime schema')
    require(type(problem['contract']) is str and 0<len(problem['contract'])<=4096,'invalid contract')
    lives=problem['lifetimes'];seen=set()
    require(type(lives) is list and 1<=len(lives)<=MAX_LIVES,'provide 1..512 lifetimes')
    for row in lives:
        require(type(row) is dict and row.keys()=={'id','start','end','width'},'invalid lifetime fields')
        name,start,end,width=(row[k] for k in ('id','start','end','width'))
        require(type(name) is str and 0<len(name)<=128 and name not in seen,'lifetime IDs must be unique')
        seen.add(name)
        require(type(start) is int and type(end) is int and 0<=start<end<=10**12,'invalid half-open lifetime')
        require(type(width) is int and 1<=width<=MAX_WIDTH,'invalid width')
    return lives


def allocate(problem):
    lives=validate(problem)
    active=[];free=[];allocations={};capacity=0;live_width=0;peak_time=0
    for row in sorted(lives,key=lambda r:(r['start'],r['id'])):
        while active and active[0][0]<=row['start']:
            end,name,width=heapq.heappop(active)
            live_width-=width;free.extend(allocations[name])
        merged=[]
        for lo,hi in sorted(free):
            if merged and lo==merged[-1][1]:merged[-1][1]=hi
            else:merged.append([lo,hi])
        free=merged;need=row['width'];slots=[];remaining=[]
        for lo,hi in free:
            take=min(need,hi-lo)
            if take:slots.append([lo,lo+take]);need-=take
            if lo+take<hi:remaining.append([lo+take,hi])
        free=remaining
        if need:slots.append([capacity,capacity+need]);capacity+=need
        allocations[row['id']]=slots
        heapq.heappush(active,(row['end'],row['id'],row['width']));live_width+=row['width']
        if live_width==capacity:
            peak_time=row['start']
    # Include all lifetimes that start at the peak point, not a partial event batch.
    peak_ids=sorted(r['id'] for r in lives if r['start']<=peak_time<r['end'])
    certificate={'schema':'integer-mult-helper-allocation/v1','capacity':capacity,
                 'allocations':allocations,'peak':{'time':peak_time,'ids':peak_ids}}
    verify(problem,certificate)
    return certificate


def verify(problem,certificate):
    lives=validate(problem);by_id={r['id']:r for r in lives}
    require(type(certificate) is dict and certificate.keys()=={'schema','capacity','allocations','peak'} and
            certificate['schema']=='integer-mult-helper-allocation/v1','invalid allocation schema')
    capacity=certificate['capacity'];allocations=certificate['allocations'];peak=certificate['peak']
    require(type(capacity) is int and 1<=capacity<=MAX_CAPACITY,'invalid pool capacity')
    require(type(allocations) is dict and allocations.keys()==by_id.keys(),'allocation IDs differ')
    pieces=0
    for name,slots in allocations.items():
        require(type(slots) is list and 1<=len(slots)<=MAX_LIVES,'invalid slot list')
        total=0;previous=-1
        for slot in slots:
            require(type(slot) is list and len(slot)==2,'invalid slot range')
            lo,hi=slot
            require(type(lo) is int and type(hi) is int and 0<=lo<hi<=capacity and lo>=previous,
                    'slot ranges overlap, are unsorted, or exceed the pool')
            previous=hi;total+=hi-lo;pieces+=1
        require(total==by_id[name]['width'],'allocated width differs')
    require(pieces<=MAX_LIVES**2,'too many slot ranges')
    # Independently replay range occupancy; ends precede starts at the same time.
    events=sorted([(r['start'],1,r['id']) for r in lives]+[(r['end'],0,r['id']) for r in lives])
    occupied=[]
    for time,kind,name in events:
        for lo,hi in allocations[name]:
            entry=(lo,hi,name);index=bisect_left(occupied,entry)
            if kind==0:
                require(index<len(occupied) and occupied[index]==entry,'release has no live range')
                occupied.pop(index)
            else:
                require((index==0 or occupied[index-1][1]<=lo) and
                        (index==len(occupied) or hi<=occupied[index][0]),'live slot collision')
                occupied.insert(index,entry)
    require(type(peak) is dict and peak.keys()=={'time','ids'} and type(peak['time']) is int,
            'invalid peak witness')
    actual=sorted(r['id'] for r in lives if r['start']<=peak['time']<r['end'])
    require(type(peak['ids']) is list and peak['ids']==actual,'peak live set differs')
    require(sum(by_id[name]['width'] for name in actual)==capacity,'peak does not prove minimum capacity')
    return {'valid':True,'minimum_capacity':capacity,'slot_ranges':pieces,
            'scope':'Minimum for these fixed half-open lifetimes and freely assignable unit slots. '
                    'Ranges may be noncontiguous. Cleanup, ownership, routing and source lifetimes '
                    'are declarations; no native map or kappa improvement is certified.'}


def load(path,limit,*,parse_int=_integer):
    with Path(path).open('rb') as stream:raw=stream.read(limit+1)
    require(len(raw)<=limit,'input exceeds byte limit')
    value=json.loads(raw.decode('utf-8'),object_pairs_hook=_pairs,parse_int=parse_int,
                     parse_float=_not_integer,parse_constant=_not_integer)
    return value,{'path':str(path),'bytes':len(raw),'sha256':sha256(raw).hexdigest()}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lifetimes');parser.add_argument('--verify',metavar='CERTIFICATE.json')
    args=parser.parse_args(argv)
    try:
        problem,pin=load(args.lifetimes,1024*1024);inputs={'lifetimes':pin}
        if args.verify:certificate,inputs['certificate']=load(args.verify,32*1024*1024,
                                                            parse_int=_certificate_integer)
        else:certificate=allocate(problem)
        report=verify(problem,certificate);report['certificate']=certificate;report['inputs']=inputs
        report['schema']='integer-mult-helper-allocation-report/v1';report['contract']=problem['contract']
    except (OSError,ValueError,TypeError,RecursionError) as exc:
        print(json.dumps({'status':'INVALID_HELPER_ALLOCATION','error':str(exc)}),file=sys.stderr);return 2
    print(json.dumps(report,indent=2,sort_keys=True));return 0


if __name__=='__main__':raise SystemExit(main())
