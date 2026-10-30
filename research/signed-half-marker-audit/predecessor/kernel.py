"""A finite binary-tape signed stochastic half. zxv + OpenAI Codex. Apache-2.0."""
from collections import Counter


def need(ok,message):
    if not ok:
        raise ValueError(message)


def compile_gates(width,sign):
    need(type(width) is int and width >= 2 and sign in (-1,1), 'kernel domain')
    r,u,t = width,width+1,width+2
    carry = [t]+list(range(width+3,2*width+2))
    gates = []
    def x(a): gates.append(('X',a))
    def c(a,b): gates.append(('C',a,b))
    def tof(a,b,d): gates.append(('T',a,b,d))
    def swap(a,b): c(a,b);c(b,a);c(a,b)
    def increment():
        for j in range(width-1):
            tof(carry[j],j,carry[j+1])
        for j in range(width):
            c(carry[j],j)
        for j in range(width-2,-1,-1):
            x(j);tof(carry[j],j,carry[j+1]);x(j)
    c(0,r);c(r,0)
    for j in range(width-1):
        swap(j,j+1)
    c(width-2,width-1)
    if sign == 1:
        c(r,t);tof(r,u,t)
        increment()
        tof(r,u,t);c(r,t)
    else:
        tof(r,u,t)
        increment()
        tof(r,u,t)
        for j in range(width): x(j)
        x(t);increment();x(t)
    counts = Counter(g[0] for g in gates)
    want = ({'X':2*width-2,'C':4*width+2,'T':2*width} if sign == 1 else
            {'X':5*width-2,'C':5*width,'T':4*width-2})
    need(dict(counts) == want, 'exact gate invoice')
    need(all(len(set(g[1:])) == len(g)-1 and max(g[1:]) < 2*width+2 for g in gates),
         'distinct bounded gate operands')
    need(all(g[-1] != u for g in gates), 'coin cell is never written')
    return gates


def execute_gates(initial,gates,inverse=False):
    cells = list(initial)
    for gate in reversed(gates) if inverse else gates:
        op,*a = gate
        if op == 'X': cells[a[0]] ^= 1
        elif op == 'C': cells[a[1]] ^= cells[a[0]]
        else: cells[a[2]] ^= cells[a[0]] & cells[a[1]]
    return cells


def compile_tape(gates):
    """Unary head walks: no indexed data access exists in the tape program."""
    out = []
    head = 0
    def visit(position,op):
        nonlocal head
        out.append(('R'*(position-head)) if position >= head else ('L'*(head-position)))
        out.append(op)
        head = position
    for g in gates:
        op,*a = g
        if op == 'X':
            visit(a[0],'X')
        elif op == 'C':
            visit(a[0],'A');visit(a[1],'C');visit(a[0],'A')
        else:
            visit(a[0],'A');visit(a[1],'B');visit(a[2],'T')
            visit(a[1],'B');visit(a[0],'A')
        visit(0,'')
    need(head == 0, 'all gate macros return the data head')
    return ''.join(out)


def execute_tape(initial,code,inverse=False):
    cells = list(initial)
    head = a = b = 0
    moves = work = pc = 0
    writes = set()
    if inverse:
        while pc < len(code):
            pc += 1;work += 1
    while (pc > 0 if inverse else pc < len(code)):
        if inverse:
            pc -= 1
            op = {'L':'R','R':'L'}.get(code[pc],code[pc])
        else:
            op = code[pc];pc += 1
        work += 1
        if op in ('L','R'):
            head += 1 if op == 'R' else -1
            moves += 1
            need(0 <= head < len(cells), 'data head inside declared extent')
        elif op == 'A': a ^= cells[head]
        elif op == 'B': b ^= cells[head]
        elif op == 'X': cells[head] ^= 1;writes.add(head)
        elif op == 'C': cells[head] ^= a;writes.add(head)
        elif op == 'T': cells[head] ^= a & b;writes.add(head)
        else: raise ValueError('invalid finite instruction')
    if not inverse:
        while pc:
            pc -= 1;work += 1
    need(head == pc == a == b == 0, 'both heads and finite control return')
    need(work == 2*len(code), 'payload execution plus program-head return invoice')
    return cells,dict(steps=work+2,boundary_marker_steps=2,data_head_moves=moves,
                      written_cells=sorted(writes))


def encode(x,width,u):
    need(-(1 << (width-1)) <= x < 1 << (width-1) and u in (0,1), 'signed input/coin')
    cells = [(x >> j) & 1 for j in range(width)]+[0]*(width+2)
    cells[width+1] = u
    return cells


def decode(cells,width):
    value = sum(cells[j] << j for j in range(width))
    return value-(1 << width) if cells[width-1] else value


def expected(x,sign,u):
    q,r = divmod(sign*x,2)
    return q+int(u < r),r
