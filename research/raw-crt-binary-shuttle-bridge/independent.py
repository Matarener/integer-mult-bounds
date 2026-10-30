# SPDX-License-Identifier: Apache-2.0
"""Separately written sparse interpreter; retains allocation lengths explicitly."""
def execute(code,initial,entry,cap):
    cells={r:{i:x for i,x in enumerate(a) if x!=4} for r,(a,h) in initial.items()}
    lengths={r:len(a) for r,(a,h) in initial.items()};heads={r:h for r,(a,h) in initial.items()}
    pc=entry;counts=dict(steps=0,reads=0,writes=0,moves=0)
    for _ in range(cap):
        instruction=code[pc];op=instruction[0];counts['steps']+=1
        if op=='halt':return cells,lengths,heads,dict(counts,status=instruction[1])
        if op=='jump':pc=instruction[1];continue
        role=instruction[1];at=heads[role]
        if op=='test':
            counts['reads']+=1
            pc=instruction[3] if cells[role].get(at,4)==instruction[2] else instruction[4]
            continue
        if op=='move':
            heads[role]+=instruction[2];counts['moves']+=1
            if heads[role]<0:raise ValueError('negative independent head')
        elif op=='write':
            counts['writes']+=1;lengths[role]=max(lengths[role],at+1)
            if instruction[2]==4:cells[role].pop(at,None)
            else:cells[role][at]=instruction[2]
        else:raise ValueError('unknown independent instruction')
        pc+=1
    raise ValueError('independent watchdog')
