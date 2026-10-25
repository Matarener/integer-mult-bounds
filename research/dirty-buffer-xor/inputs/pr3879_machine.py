"""Literal two-tape, four-symbol machines for XOR record permutations.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
Compile-time integers generate a finite transition table. The online runner
uses only the table, scanned symbols, unit moves, writes and finite state.
"""
from dataclasses import dataclass

ZERO,ONE,SEP,BLANK=range(4)
ALPHABET=range(4)


def need(ok,message):
    if not ok:
        raise ValueError(message)


def integer(n,minimum,name):
    need(type(n) is int and n>=minimum,name)


def reverse_bits(delta,h):
    value=0
    for _ in range(h):
        value=2*value+(delta&1)
        delta >>= 1
    return value


def variation(h,delta):
    integer(h,0,'dimension')
    integer(delta,0,'mask')
    need(delta < 1 << h,'mask range')
    value=0
    for k in range(1,h+1):
        low=delta&((1 << (k-1))-1)
        jump=1+2*low if not ((delta>>(k-1))&1) else (1 << k)-1-2*low
        value=2*value+jump
    return value


@dataclass
class Machine:
    h:int
    delta:int
    operations:tuple[str,...]
    table:dict
    halt:int
    mode:str='copy'

    @property
    def input_travel(self):
        return sum(op in ('R0','L0') for op in self.operations)


def compile_machine(h,delta):
    integer(h,0,'dimension')
    integer(delta,0,'mask')
    n=1 << h
    need(delta<n,'mask range')
    operations=[]
    position=0
    for j in range(n):
        source=j^delta
        step=source-position
        operations.extend(['R0' if step>0 else 'L0']*abs(step))
        operations.append('C')
        position=source+1  # copying ends at the following separator
    operations.extend(['L0']*position)
    operations.extend(['L1']*n)
    table={}
    for i,op in enumerate(operations):
        entry,scan,next_state=2*i,2*i+1,2*i+2
        for a in ALPHABET:
            for b in ALPHABET:
                if op=='C':
                    if a==SEP:table[(entry,a,b)]=(scan,None,SEP,1,1)
                    if a in (ZERO,ONE):table[(scan,a,b)]=(scan,None,a,1,1)
                    elif a==SEP:table[(scan,a,b)]=(next_state,None,SEP,0,0)
                elif op in ('R0','L0'):
                    direction=1 if op=='R0' else -1
                    if a==SEP:table[(entry,a,b)]=(scan,None,None,direction,0)
                    if a in (ZERO,ONE):table[(scan,a,b)]=(scan,None,None,direction,0)
                    elif a==SEP:table[(scan,a,b)]=(next_state,None,None,0,0)
                elif op=='L1':
                    if b==SEP:table[(entry,a,b)]=(scan,None,None,0,-1)
                    if b in (ZERO,ONE):table[(scan,a,b)]=(scan,None,None,0,-1)
                    elif b==SEP:table[(scan,a,b)]=(next_state,None,None,0,0)
                else:raise ValueError('unknown macro')
    machine=Machine(h,delta,tuple(operations),table,2*len(operations))
    expected=variation(h,delta)+1+2*reverse_bits(delta,h)
    need(machine.input_travel==expected,'closed travel formula')
    need(expected <= (h+1)*n,'travel upper bound')
    need(len(table)==16*len(operations),'complete finite transition inventory')
    return machine


def inplace_travel(h,delta):
    integer(h,0,'dimension');integer(delta,0,'mask')
    n=1 << h;need(delta<n,'mask range')
    if delta==0:return 0
    top=1 << (delta.bit_length()-1)
    return (n-2)*top+2*n-2


def compile_inplace(h,delta):
    """In-place XOR permutation with one arbitrary dirty record restored.

    Deliberately space economical: the time bound is quadratic in 2^h.
    The program is fixed once h and delta are fixed; record width is unbounded.
    """
    integer(h,0,'dimension');integer(delta,0,'mask')
    n=1 << h;need(delta<n,'mask range')
    operations=[];position=0
    for a in range(n):
        b=a^delta
        if a>=b:continue
        for address in (a,b,a):
            step=address-position
            operations.extend(['R0' if step>0 else 'L0']*abs(step))
            operations.append('W')
            position=address  # swap rewinds both heads to their record starts
    operations.extend(['L0']*position)
    table={};state=0
    for op in operations:
        count=3 if op=='W' else 2
        entry,scan,next_state=state,state+1,state+count
        for a in ALPHABET:
            for b in ALPHABET:
                if op=='W':
                    rewind=state+2
                    if a==b==SEP:table[(entry,a,b)]=(scan,None,None,1,1)
                    if a in (ZERO,ONE) and b in (ZERO,ONE):
                        table[(scan,a,b)]=(scan,b,a,1,1)
                        table[(rewind,a,b)]=(rewind,None,None,-1,-1)
                    elif a==b==SEP:
                        table[(scan,a,b)]=(rewind,None,None,-1,-1)
                        table[(rewind,a,b)]=(next_state,None,None,0,0)
                else:
                    direction=1 if op=='R0' else -1
                    if a==SEP:table[(entry,a,b)]=(scan,None,None,direction,0)
                    if a in (ZERO,ONE):table[(scan,a,b)]=(scan,None,None,direction,0)
                    elif a==SEP:table[(scan,a,b)]=(next_state,None,None,0,0)
        state=next_state
    machine=Machine(h,delta,tuple(operations),table,state,'inplace')
    need(machine.input_travel==inplace_travel(h,delta),'in-place closed travel')
    return machine


def encode(records,origin=0):
    tape={origin:SEP};position=origin
    for word in records:
        need(all(type(x) is int and x in (0,1) for x in word),'binary record')
        for bit in word:
            position+=1;tape[position]=bit
        position+=1;tape[position]=SEP
    return tape,position


def decode(tape,n,origin=0):
    position=origin
    need(tape.get(position,BLANK)==SEP,'initial separator')
    result=[]
    for _ in range(n):
        position+=1;word=[]
        while tape.get(position,BLANK) in (ZERO,ONE):
            word.append(tape[position]);position+=1
        need(tape.get(position,BLANK)==SEP,'terminated record')
        result.append(tuple(word))
    return result,position


def run(machine,input_tape,output_tape,input_origin=0,output_origin=0,limit=10000000):
    """Execute one literal transition at a time. No address arithmetic here."""
    tapes=[dict(input_tape),dict(output_tape)]
    heads=[input_origin,output_origin]
    minimum=heads.copy();maximum=heads.copy()
    writes=[set(),set()]
    state=steps=0
    while state != machine.halt:
        need(steps<limit,'transition budget exhausted')
        a=tapes[0].get(heads[0],BLANK)
        b=tapes[1].get(heads[1],BLANK)
        action=machine.table.get((state,a,b))
        need(action is not None,'blocked finite control')
        target,w0,w1,m0,m1=action
        need(m0 in (-1,0,1) and m1 in (-1,0,1),'unit tape moves')
        for i,value,move in [(0,w0,m0),(1,w1,m1)]:
            if value is not None:
                need(value in ALPHABET,'finite alphabet write')
                tapes[i][heads[i]]=value;writes[i].add(heads[i])
            heads[i]+=move
            minimum[i]=min(minimum[i],heads[i]);maximum[i]=max(maximum[i],heads[i])
        state=target;steps+=1
    return {'tapes':tapes,'heads':tuple(heads),'steps':steps,
            'minimum':tuple(minimum),'maximum':tuple(maximum),'writes':writes,
            'halted':True}


def exact_cost(machine,records):
    """Independent macro invoice: 2 copies/returns plus input record scans."""
    n=1 << machine.h
    need(len(records)==n,'record cardinality')
    lengths=[len(w) for w in records]
    source=[j^machine.delta for j in range(n)]
    position=0;crossings=[0]*n
    for index in source:
        for edge in range(min(position,index),max(position,index)):
            crossings[edge]+=1
        position=index+1
    for edge in range(position):crossings[edge]+=1
    total=2*sum(lengths)+4*n+sum(c*(b+2) for c,b in zip(crossings,lengths))
    return total,crossings
