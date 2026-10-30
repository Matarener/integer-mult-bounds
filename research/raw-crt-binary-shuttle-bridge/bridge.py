# SPDX-License-Identifier: Apache-2.0
"""Literal five-symbol caller; binary callee uses subalphabet {BLANK,ONE}.
JoyboyBrian with substantial OpenAI Codex assistance. No runtime codec callback.
"""
from sources import PROGRAM,BINARY,ACTUAL,need
ZERO,ONE,LEFT,RIGHT,BLANK=range(5)
RAW='RAW'
DESCRIPTORS=('H','A','G','S')
ROLES=(RAW,)+tuple(mode+'_'+r for mode in ('u','t') for r in DESCRIPTORS)+tuple('E_'+r for r in PROGRAM.ROLES)

def assemble(geometry=None):
    geometry=ACTUAL if geometry is None else geometry
    need(set(geometry)=={'u','t'},'two fixed caller modes')
    for g in geometry.values():need(len(g)==4 and all(type(x)is int for x in g) and g[0]>=0 and min(g[1:])>=1,'admitted fixed geometry')
    source,source_entries=PROGRAM.assemble()
    binary,child_entries=BINARY.lower(source,source_entries,PROGRAM.ROLES)
    b=PROGRAM.Builder();entries={};checkpoints={}
    def move(role,n):
        for _ in range(abs(n)):b.move(role,1 if n>0 else -1)
    def block(role,bits,empty=False):
        for i,x in enumerate(bits):
            if empty:b.require(role,BLANK)
            b.write(role,ONE if x else BLANK)
            if i<2:b.move(role,1)
        move(role,-2)
    def paired_rewind(raw,encoded):
        loop,done=b.fresh(),b.fresh();b.mark(loop)
        b.move(raw,-1);move(encoded,-3)
        b.test(raw,LEFT,done,loop);b.mark(done)
        b.move(raw,1);move(encoded,3)
    def erase_origin(encoded):
        move(encoded,-3);block(encoded,(0,0,0))
    def encode(raw,encoded,numeric):
        block(encoded,BINARY.ENCODING[LEFT],True);move(encoded,3)
        loop,z,o,end,other=b.fresh(),b.fresh(),b.fresh(),b.fresh(),b.fresh()
        b.mark(loop);b.test(raw,ZERO,z,other);b.mark(other);b.test(raw,ONE,o,end)
        for label,value in ((z,ZERO),(o,ONE)):
            b.mark(label);block(encoded,BINARY.ENCODING[value],True);move(encoded,3);b.move(raw,1);b.jump(loop)
        b.mark(end);b.require(raw,RIGHT if numeric else BLANK)
        if numeric:block(encoded,BINARY.ENCODING[RIGHT],True)
        paired_rewind(raw,encoded)
    def read_block(role,targets):
        def descend(prefix):
            if len(prefix)==3:
                move(role,-2);b.jump(targets.get(prefix,'reject'));return
            z,o=b.fresh(),b.fresh();b.test(role,ONE,o,z)
            for label,x in ((z,0),(o,1)):
                b.mark(label)
                if x==0:b.require(role,BLANK)
                if len(prefix)<2:b.move(role,1)
                descend(prefix+(x,))
        descend(())
    def decode_install():
        loop,z,o,end=b.fresh(),b.fresh(),b.fresh(),b.fresh();b.mark(loop)
        read_block('E_SOURCE',{BINARY.ENCODING[ZERO]:z,BINARY.ENCODING[ONE]:o,BINARY.ENCODING[BLANK]:end})
        for label,value in ((z,ZERO),(o,ONE)):
            b.mark(label);b.write(RAW,value);block('E_SOURCE',(0,0,0));move('E_SOURCE',3);b.move(RAW,1);b.jump(loop)
        b.mark(end);b.require(RAW,BLANK);paired_rewind(RAW,'E_SOURCE');erase_origin('E_SOURCE')
    def retire_descriptor(raw,encoded):
        loop,end,body=b.fresh(),b.fresh(),b.fresh();b.mark(loop)
        b.test(raw,RIGHT,end,body);b.mark(body);block(encoded,(0,0,0));move(encoded,3);b.move(raw,1);b.jump(loop)
        b.mark(end);block(encoded,(0,0,0));paired_rewind(raw,encoded);erase_origin(encoded)
    # Paid production of both actual descriptor banks; no fixture conversion.
    entries['init_descriptors']=len(b.code)
    for mode,g in geometry.items():
        for name,value in zip(DESCRIPTORS,g):
            role=mode+'_'+name;b.require(role,BLANK);b.write(role,LEFT);b.move(role,1)
            for i in range(max(1,value.bit_length())):
                b.require(role,BLANK);b.write(role,(value>>i)&1);b.move(role,1)
            b.require(role,BLANK);b.write(role,RIGHT);b.rewind(role)
    b.emit('halt','initialized')
    for mode in ('u','t'):
        entries[mode]=len(b.code)
        encode(RAW,'E_SOURCE',False)
        for name in DESCRIPTORS:encode(mode+'_'+name,'E_'+name,True)
        # Establish exact block-aligned blank initial private banks, also charged.
        for name in PROGRAM.PRIVATE:block('E_'+name,(0,0,0),True)
        b.jump((mode,'child',child_entries['init']))
        continuations={'initialized':(mode,'child',child_entries['run']),
                       'returned':(mode,'child',child_entries['install']),
                       'installed':(mode,'child',child_entries['close']),
                       'closed':(mode,'decode')}
        for pc,row in enumerate(binary):
            b.mark((mode,'child',pc));op=row[0]
            if op=='test':b.test('E_'+row[1],ONE if row[2] else BLANK,(mode,'child',row[3]),(mode,'child',row[4]))
            elif op=='write':b.write('E_'+row[1],ONE if row[2] else BLANK)
            elif op=='move':b.move('E_'+row[1],row[2])
            elif op=='jump':b.jump((mode,'child',row[1]))
            elif row[1] in continuations:b.jump(continuations[row[1]])
            else:b.jump('reject')
        b.mark((mode,'decode'));decode_install()
        for name in DESCRIPTORS:retire_descriptor(mode+'_'+name,'E_'+name)
        for name in PROGRAM.PRIVATE:move('E_'+name,-3)
        b.emit('halt','returned')
        checkpoints[mode]={name:b.labels[(mode,'child',pc)] for name,pc in child_entries.items()}
    entries['close_descriptors']=len(b.code)
    for mode in ('u','t'):
        for name in DESCRIPTORS:
            role=mode+'_'+name;b.clear(role);b.move(role,-1);b.require(role,LEFT);b.write(role,BLANK)
    b.emit('halt','closed');b.mark('reject');b.emit('halt','rejected')
    code=b.finish();factor=BINARY.admit(code,entries,ROLES,range(5))
    return code,entries,checkpoints,factor

def capacities(g):
    """Proof/fixture ledger only; never called by the literal machine."""
    H,A,G,S=g;V=A*4**H*G*S;bits=lambda n:max(1,n.bit_length());d=max(H-1,0)
    c={'PRE':bits(A)+d+2,'GAP':bits(G)+d+2,'TAIL':bits(S)+d+2,'SCAN':bits(H)+2,'REMAIN':bits(H)+2}
    c.update({name:bits(n)+H+1 if H else 1 for name,n in [('OUTER',A),('BETWEEN',G),('BITS',S)]})
    c.update({name:V//4+1 if H else 1 for name in ('Q00','Q01','Q10','Q11')})
    c.update(B0=V+1 if H else 1,B1=V+1 if H>=2 else 1,OUTPUT=V+1)
    return {'E_'+name:3*n for name,n in c.items()}|{'E_SOURCE':3*(V+1)}|{'E_'+name:3*(bits(n)+2) for name,n in zip(DESCRIPTORS,g)}
