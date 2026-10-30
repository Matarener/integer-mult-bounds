"""Semantic corruption controls, including real Git-free CLI checks.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
from machine import compile_machine, invoice, tape_cost, encode, decode, run, need, SEP
from verify import ROOT, check_result, execute


def rejected(call, label):
    try:
        call()
    except (ValueError, KeyError, TypeError):
        return
    raise ValueError('accepted mutant: '+label)


def main():
    groups=[]
    for args in [(-1,0,0),(2,4,0),(2,-1,0),(2,1,3),(2,1,-1),(True,0,0)]:
        rejected(lambda args=args: compile_machine(*args),'parameter domain')
    rejected(lambda: tape_cost(2,1,0,-1),'negative width')
    groups.append('parameter domains')

    # Full involution and independent-origin replay with different arbitrary dirt.
    for r in range(4):
        words=[tuple(((j+3) >> k)&1 for k in range(4)) for j in range(8)]
        dirt=[tuple(((j*11) >> k)&1 for k in range(4)) for j in range(1 << r)]
        t,end=encode(words,-103); s,send=encode(dirt,77)
        t[-104]=SEP; t[end+1]=0; s[76]=SEP; s[send+1]=1
        machine=compile_machine(3,7,r); cost=tape_cost(3,7,r,4)
        first=run(machine,t,s,-103,77,cost+1)
        second=run(machine,*first['tapes'],-103,77,cost+1)
        need(second['tapes']==[t,s] and second['heads']==(-103,77),'full-tape involution')
        need(first['tapes'][1]==s,'arbitrary borrowed payload')
    groups.append('independent origins and full-tape involution')

    m=compile_machine(1,1,0); a,end=encode([(0,),(1,)],0); d,send=encode([(0,)],0)
    original=(deepcopy(a),deepcopy(d)); cost=tape_cost(1,1,0,1)
    valid=run(m,a,d,limit=cost+1)
    def check(x):check_result(m,x,a,d,[(0,),(1,)],0,0,end,send,cost)
    for label, mutate in [
        ('wrong permutation',lambda x:x['tapes'][0].__setitem__(1,0)),
        ('scratch contamination',lambda x:x['tapes'][1].__setitem__(1,1)),
        ('head not returned',lambda x:x.__setitem__('heads',(1,0))),
        ('outside write',lambda x:x['tapes'][0].__setitem__(-1,1)),
        ('unpaid transition',lambda x:x.__setitem__('steps',cost-1)),
        ('no halt',lambda x:x.__setitem__('halted',False)),
    ]:
        x=deepcopy(valid)
        if label=='outside write':
            x['writes'][0].add(-1)
        mutate(x);rejected(lambda x=x:check(x),label)
    need((a,d)==original,'controls do not mutate caller input')
    groups.append('endpoint restoration footprint and exact halt mutants')

    # Really skip the third streamed exchange in the transition table.
    need(m.operations[6:8]==('S','L'),'control location')
    broken=deepcopy(m); broken.table[(12,SEP,SEP)]=(16,None,None,0,0)
    bad=run(broken,a,d,limit=cost+1)
    need(bad['tapes'][1]!=d,'third exchange is needed for dirty restoration')
    rejected(lambda:check(bad),'missing third exchange')
    groups.append('actual missing-third-exchange machine')

    rejected(lambda:run(m,a,d,limit=cost-1),'bounded incomplete run')
    short,_=encode([()],0)
    rejected(lambda:run(m,a,short,limit=cost+1),'unequal record widths')
    malformed=deepcopy(a);malformed[0]=1
    rejected(lambda:run(m,malformed,d,limit=cost+1),'missing framing')
    jump=deepcopy(m);target,w0,w1,_,move1=jump.table[(0,SEP,SEP)]
    jump.table[(0,SEP,SEP)]=(target,w0,w1,2,move1)
    rejected(lambda:run(jump,a,d,limit=cost+1),'nonunit movement')
    groups.append('framing width move and bounded-failure controls')

    # Smaller scratch is not falsely reported as strictly faster at every mask.
    for h in range(1,8):
        for delta in range(1 << h):
            values=[invoice(h,delta,r)['time_factor'] for r in range(h+1)]
            need(all(b <= a for a,b in zip(values,values[1:])),'monotone tradeoff')
            need(values[-1]==6*(1 << h)*delta.bit_count(),'linear endpoint')
    need(invoice(3,7,0)['time_factor'] > invoice(3,7,2)['time_factor'],'strict useful tradeoff')
    groups.append('tradeoff monotonicity and linear endpoint')

    # Actual outside-Git copies; no simulated verification return codes.
    # Use the caller's temporary root, as with ordinary portable test suites.
    with tempfile.TemporaryDirectory(prefix='dirty-xor-') as temp:
        dst=Path(temp)/'export';shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('__pycache__'))
        argv=[sys.executable]+(['-O'] if not __debug__ else [])+['-B',str(dst/'verify.py')]
        def cli():
            return subprocess.run(argv,cwd=temp,capture_output=True,text=True,timeout=60)
        p=cli();need(p.returncode==0,'actual clean export replay '+p.stderr)
        input_path=dst/'inputs/pr3879_machine.py';saved=input_path.read_bytes()
        input_path.write_bytes(saved+b'\n# corruption control\n')
        p=cli();need(p.returncode!=0 and 'source hash' in p.stderr,'actual source corruption rejected')
        input_path.write_bytes(saved)
        receipt=dst/'RESULT.json';record=json.loads(receipt.read_text(encoding='utf8'))
        record['production_tradeoff'][-1]['total_B_coefficient']-=1
        receipt.write_text(json.dumps(record),encoding='utf8')
        p=cli();need(p.returncode!=0 and 'frozen receipt' in p.stderr,'actual invoice corruption rejected')
    groups.append('real export source and receipt corruption')
    print(json.dumps({'status':'PASS_DIRTY_BUFFER_CONTROLS','groups':groups,
                      'assertions_enabled':__debug__}))


if __name__ == '__main__': main()
