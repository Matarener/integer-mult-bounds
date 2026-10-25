#!/usr/bin/env python3
"""Separate integer geometry and per-binary-decrement accounting oracle."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent


def need(ok,msg):
    if not ok:raise ValueError(msg)
def add(*rows):return [sum(v) for v in zip(*rows)]
def mul(n,row):return [n*v for v in row]
def sub(a,b):return [x-y for x,y in zip(a,b)]


def counter(e,I,probe=False):
    # Count input construction, high-zero trimming, clearing and each actual
    # binary decrement by its trailing-zero class. No primary/runtime import.
    b=e.bit_length();z=I-b
    initial=[2*I+5,3*I+3,4*I+8] if e==0 else [2*I+3,I+1+2*z,2*I+4+2*z]
    if probe or not e:
        B=max(1,b);return add(initial,[2*B+5,B+1,2*B+6])
    steps=[]
    for k in range(e,0,-1):
        t=(k&-k).bit_length()-1
        if k==1:steps.append([6,4,8])
        elif k&(k-1)==0:
            B=k.bit_length();steps.append([2*B+3,B+2,2*B+4])
        else:steps.append([2*t+5,t+1,2*t+4])
    return add(initial,*steps,[7,2,8])


def check(receipt):
    need(len(receipt['pairs'])==15,'declared fifteen complete pairs')
    shapes=set();ranges=[]
    for row in receipt['pairs']:
        old,new=row['original'],row['shared'];c=old['case'];shapes.add(c['name'])
        need(type(row['total_action_saving']) is int,'typed complete action gain')
        need(all(type(r[k]) is int and r[k]>0 for r in (old,new) for k in ('index_width','residue_width')),'typed source widths')
        need(old['index_width']==new['index_width'] and old['residue_width']==new['residue_width'] and old['case']==new['case'],'same compared input contexts')
        q,w,n=c['q'],c['w'],c['n'];A=q**w;f=n//64;delta=n%64
        phi=lambda x:x if x<64*f else x+2*delta
        a,b=phi(c['first']),phi(c['second']);width=c['width']
        e=[a,b-a-width,2*n-b-width]
        need(width>0 and a+width<=b and b+width<=2*n,'actual complete disjoint child chunks')
        need(phi(c['first']+width-1)==a+width-1 and phi(c['second']+width-1)==b+width-1,'full physical contiguity')
        B,G,S=c['spectators'];want=[B*A**e[0],A**e[1],S*A**e[2]]
        region=0 if a>=n else 2 if b+width<=n else 1;want[region]*=G
        need(e==old['exponents']==new['exponents'],'independent complete spectator exponents')
        for result in (old,new):
            need(type(result['total_actions']) is int and all(len(v)==3 and all(type(x) is int and x>=0 for x in v) for v in result['actions'].values()),'typed complete source action lanes')
            values=[]
            for encoded in result['output_hex']:
                raw=list(bytes.fromhex(encoded));need(raw[0]==2,'retained LEFT marker')
                end=raw.index(3);digits=raw[1:end]
                need(len(digits)>=2 and digits[-2:]==[1,0] and all(v in (0,1) for v in digits) and all(v==4 for v in raw[end+1:]),'one high zero margin and erased suffix')
                values.append(sum(v<<i for i,v in enumerate(digits)))
            need(values==want and list(map(int,result['output_values']))==want,'independent full marginal bytes/values')
            need(result['borrowed_state_restored'] is True and result['owned_backing_erased'] is True,'complete interval state controls')
            need(result['total_actions']==sum(sum(v) for v in result['actions'].values()),'three disjoint source-action lanes')
        I=old['index_width'];active=[v for v in e if v]
        old_counter=add(*(counter(v,I) for v in e))
        new_counter=add(*(counter(v,I,True) for v in e),*(mul(w,counter(v,I)) for v in active))
        expected={'record':sub(old_counter,new_counter),'index':mul(-w*len(active),[3*I+3,0,2*I+4]),
                  'residue':mul(sum(e)-int(bool(active)),old['radix_invoice'])}
        need(old['radix_invoice']==new['radix_invoice'],'same complete measured source radix invoice')
        actual={k:sub(old['actions'][k],new['actions'][k]) for k in expected}
        need(actual==expected==row['saving'],'independent complete exact action delta')
        gain=old['total_actions']-new['total_actions']
        need(gain==row['total_action_saving']>0,'positive complete declared-case saving')
        ranges.append((gain,old['total_actions']))
    need({'good','unit-across','pair-head','pair-tail','half-head','half-tail'}<=shapes,'all six source branch geometries')
    return {'pairs':len(ranges),'branch_shapes':6,'runtime_imports':0,'counter_oracle':'individual trailing-zero cases, not primary closed form'}


if __name__=='__main__':
    print('PASS_INDEPENDENT_CHILD_SPECTATORS '+json.dumps(check(json.loads((HERE/'CERTIFICATE.json').read_text())),sort_keys=True))
