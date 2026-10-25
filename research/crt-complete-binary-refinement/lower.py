"""Closed finite-value refinement of the exact PR5105 program.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
All enumeration below is static compilation, never an execution primitive.
"""
from itertools import product

WIDTH = 13
RECORDS = frozenset(('R', n) for n in range(4096))


def canon(x):
    if isinstance(x, bool):
        return int(x)  # Python source equality identifies bools with 0 and 1.
    if isinstance(x, tuple):
        return tuple(canon(y) for y in x)
    return x


def operand(a, domains):
    if a[0] == 'c':
        return {canon(a[1])}
    if a[0] == 'r':
        return domains[a[1]]
    if a[0] == 'tuple':
        sets = [operand(x, domains) for x in a[1]]
        size = 1
        for s in sets:
            size *= len(s)
        if size > 8192:
            raise ValueError('static product exceeds explicit compilation budget')
        return set(product(*sets))
    raise ValueError('unsupported operand')


def closure(source, roles, source_registers):
    """Monotone overapproximation; undefined source operations have no successor."""
    regs = {r: {None} for r in source_registers}
    tapes = {r: {'_'} for r in roles}
    for r in ('G', 'H', 'K', 'Y', 'J', 'B'):
        tapes[r].update(('<', '>', '1'))
    tapes['rom'].update(('L', 'R', '0', '1'))
    tapes['data'].update(RECORDS | {'<', '>'})
    changed = True
    rounds = 0
    while changed:
        changed = False
        rounds += 1
        if rounds > 100:
            raise ValueError('finite closure iteration budget')
        for op, *a in source:
            values = set()
            if op == 'read':
                for role in operand(a[0], regs):
                    if role in tapes:
                        values.update(tapes[role])
                dest = a[1]
            elif op == 'write':
                for role in operand(a[0], regs):
                    if role in tapes:
                        old = len(tapes[role]); tapes[role].update(operand(a[1], regs))
                        changed |= len(tapes[role]) != old
                continue
            elif op == 'copy':
                values = operand(a[0], regs); dest = a[1]
            elif op == 'field':
                values = {x[a[1]] for x in operand(a[0], regs)
                          if isinstance(x, tuple) and 0 <= a[1] < len(x)}
                dest = a[2]
            elif op in ('not', 'record', 'eq', 'ne', 'in', 'notin'):
                values = {0, 1}; dest = a[-1]
            elif op in ('xorbit', 'andbit', 'orbit'):
                values = {'0', '1'}; dest = a[-1]
            elif op in ('move', 'branch', 'jump', 'halt'):
                continue
            else:
                raise ValueError('unsupported source opcode ' + op)
            old = len(regs[dest]); regs[dest].update(values)
            changed |= len(regs[dest]) != old
    return regs, tapes, rounds


class Lower:
    def __init__(self, source, roles, regs, tapes, fault=None):
        self.source, self.roles, self.domains = source, tuple(sorted(roles)), regs
        self.fault = fault
        values = {'_', None, 0, 1, '0', '1'}
        for domain in (*regs.values(), *tapes.values()):
            values.update(domain)
        def collect(a):
            values.update(operand(a,regs))
            if a[0]=='tuple':
                for x in a[1]:collect(x)
        for row in source:
            for a in row[1:]:
                if isinstance(a, tuple) and a and a[0] in ('c', 'r', 'tuple'):
                    collect(a)
        other = sorted(values - RECORDS - {'_'}, key=repr)
        if len(other) >= 4096:
            raise ValueError('nonrecord code space exhausted')
        self.codes = {'_': 0, **{x: i+1 for i, x in enumerate(other)}}
        self.codes.update({x: 4096+x[1] for x in RECORDS})
        self.reverse = {v: k for k, v in self.codes.items()}
        self.out, self.starts, self.registers = [], [], {}
        self.serial = 0

    def emit(self, *x):
        self.out.append(x)
        return len(self.out)-1

    def temp(self):
        self.serial += 1
        return '$' + str(self.serial)

    def bit(self, name, j):
        key = (name, j)
        if key not in self.registers:
            self.registers[key] = len(self.registers)
        return self.registers[key]

    def setword(self, name, value):
        n = self.codes[canon(value)]
        for j in range(WIDTH):
            self.emit('set', self.bit(name, j), (n >> j) & 1)

    def copyword(self, src, dst):
        for j in range(WIDTH):
            self.emit('copy', self.bit(src, j), self.bit(dst, j))

    def equal(self, src, value=None, other=None):
        flag, scratch = self.temp(), self.temp()
        self.emit('set', self.bit(flag, 0), 0)
        for j in range(WIDTH):
            if other is None:
                self.emit('xor_const', self.bit(src,j), (self.codes[value] >> j)&1, self.bit(scratch,0))
            else:
                self.emit('xor', self.bit(src,j), self.bit(other,j), self.bit(scratch,0))
            self.emit('or', self.bit(flag,0), self.bit(scratch,0), self.bit(flag,0))
        self.emit('not', self.bit(flag,0), self.bit(flag,0))
        return self.bit(flag,0)

    def choose(self, tests, success, failure='reject'):
        """Ordered finite decision chain. All targets resolve to literal PCs."""
        ends = []
        for test, result in tests:
            flag = test()
            branch = self.emit('branch', flag, None, None)
            yes = len(self.out); success(result); ends.append(self.emit('jump', None))
            self.out[branch] = ('branch', flag, yes, len(self.out))
        self.emit('halt', failure)
        for i in ends:
            self.out[i] = ('jump', len(self.out))

    def value(self, a):
        if a[0] == 'r':
            return a[1]
        name = self.temp()
        values = operand(a, self.domains)
        if len(values) == 1:
            self.setword(name, next(iter(values)))
            return name
        if a[0] != 'tuple':
            raise ValueError('unsupported compound value')
        parts = [self.value(x) for x in a[1]]
        def test(v):
            flag = self.bit(self.temp(), 0); self.emit('set', flag, 1)
            for p, x in zip(parts, v):
                eq = self.equal(p, x); self.emit('and', flag, eq, flag)
            return flag
        self.choose([(lambda v=v:test(v), v) for v in sorted(values,key=repr)],
                    lambda v:self.setword(name,v))
        return name

    def boolean(self, flag, dst, negate=False):
        branch = self.emit('branch', flag, None, None)
        yes = len(self.out); self.setword(dst, int(not negate)); end = self.emit('jump',None)
        no = len(self.out); self.setword(dst, int(negate))
        self.out[branch] = ('branch', flag, yes, no)
        self.out[end] = ('jump',len(self.out))

    def truth(self, name):
        flag = self.bit(self.temp(),0); self.emit('set',flag,1)
        for v in self.codes:
            if not v:
                eq = self.equal(name,v); self.emit('not',eq,eq); self.emit('and',flag,eq,flag)
        return flag

    def tapeop(self, op, role, payload):
        def action(r):
            if op == 'move':
                for _ in range(WIDTH-(self.fault == 'short_stride')):
                    self.emit('move',r,payload)
            else:
                for j in range(WIDTH):
                    self.emit('read' if op == 'read' else 'write_reg',r,self.bit(payload,j))
                    if j+1 < WIDTH:self.emit('move',r,1)
                for _ in range(WIDTH-1):self.emit('move',r,-1)
        values = operand(role,self.domains)
        valid = sorted(values & set(self.roles))
        if len(values) == 1 and valid:
            action(valid[0]); return
        value = self.value(role)
        targets=[self.roles[(self.roles.index(r)+1)%len(self.roles)] for r in valid] if self.fault == 'wrong_role' else valid
        self.choose([(lambda r=r:self.equal(value,r),dest) for r,dest in zip(valid,targets)],action)

    def compile(self):
        for op,*a in self.source:
            self.serial=0  # Scratch is dead at every source instruction boundary.
            self.starts.append(len(self.out))
            if op == 'copy':self.copyword(self.value(a[0]),a[1])
            elif op == 'read':self.tapeop(op,a[0],a[1])
            elif op == 'write':self.tapeop(op,a[0],self.value(a[1]))
            elif op == 'move':
                if a[1][0]!='c' or a[1][1] not in (-1,1):raise ValueError('nonunit move')
                self.tapeop(op,a[0],a[1][1])
            elif op in ('eq','ne'):
                left,right=self.value(a[0]),self.value(a[1])
                self.boolean(self.equal(left,other=right),a[2],op=='ne')
            elif op in ('in','notin'):
                if a[1][0]!='tuple':raise ValueError('nonliteral membership')
                left=self.value(a[0]);flag=self.bit(self.temp(),0);self.emit('set',flag,0)
                for x in a[1][1]:
                    eq=self.equal(left,other=self.value(x));self.emit('or',flag,eq,flag)
                self.boolean(flag,a[2],op=='notin')
            elif op == 'not':self.boolean(self.truth(self.value(a[0])),a[1],True)
            elif op == 'record':self.boolean(self.bit(self.value(a[0]),12),a[1])
            elif op == 'field':
                src=self.value(a[0]);valid=[x for x in operand(a[0],self.domains) if isinstance(x,tuple) and a[1]<len(x)]
                self.choose([(lambda x=x:self.equal(src,x),x[a[1]]) for x in sorted(valid,key=repr)],lambda x:self.setword(a[2],x))
            elif op in ('xorbit','andbit','orbit'):
                x=self.equal(self.value(a[0]),'1');y=self.equal(self.value(a[1]),'1')
                flag=self.bit(self.temp(),0);self.emit({'xorbit':'xor','andbit':'and','orbit':'or'}[op],x,y,flag)
                branch=self.emit('branch',flag,None,None);yes=len(self.out);self.setword(a[2],'1');end=self.emit('jump',None);no=len(self.out);self.setword(a[2],'0')
                self.out[branch]=('branch',flag,yes,no);self.out[end]=('jump',len(self.out))
            elif op == 'branch':self.emit('branch',self.truth(self.value(a[0])),('source',a[1]),('source',a[2]))
            elif op == 'jump':self.emit('jump',('source',a[0]))
            elif op == 'halt':self.emit('halt',a[0])
            else:raise ValueError('unsupported source opcode '+op)
        self.starts.append(len(self.out))
        # Scratch belongs to the finite control. Every exit clears all bits.
        count=len(self.registers);offsets=list(range(count,count+len(self.out)+1))
        starts=[offsets[x] for x in self.starts]
        def target(x):
            return starts[x[1]] if isinstance(x,tuple) else offsets[x]
        program=[None]*count
        for (name,j),i in self.registers.items():
            program[i]=('set',i,(self.codes[None] >> j)&1 if name in self.domains else 0)
        statuses=sorted({a[0] for op,*a in self.out if op=='halt'})
        tail={status:count+len(self.out)+i*(count+1) for i,status in enumerate(statuses)}
        for op,*a in self.out:
            if op=='halt':
                program.append(('jump',tail[a[0]]));continue
            elif op=='jump':a[0]=target(a[0])
            elif op=='branch':a[1]=target(a[1]);a[2]=target(a[2])
            program.append((op,*a))
        for status in statuses:
            program.extend(('set',i,0) if self.fault!='keep_control' else ('copy',i,i) for i in range(count))
            program.append(('halt',status))
        return program,starts
