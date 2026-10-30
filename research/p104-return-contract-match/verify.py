#!/usr/bin/env python3
"""Matched formal P104 return adapters. ToikY with OpenAI Codex; Apache-2.0."""
from __future__ import annotations
import ast
from collections import Counter
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PINS = {'caller-PROOF.md': '9bfcc4599a829c5ec8d7e984279709251e8e60085162dcec965e97427971723c', 'caller-verify.py': 'f25cfc3ff2a42d4c7a5456d8836deb45ac61c6ae8cfd56ee73f6c8b92f28d3b7', 'consumer-PROOF.md': 'b6b112b537f7f8077afaae237513711c5b61a4fa0d542551e3142b674131030b', 'consumer-verify.py': 'c662bed19551803e73d1531a789f43d8499b3a61172df87650aebef5ae656821', 'geometry.json': '8212331ef435650469b6fca71448bcc2915a0cab46562acc41c5fc2a3dfa56c7'}
J_FIXED = [0, 1, 3, 6, 22, 31, 93, 103]
EXPECTED_COUNTS = {
    'caller': {'lift':96, 'drop':96, 'add':1152, 'half':104, 'double':104},
    'consumer': {'lift':96, 'drop':96, 'add':960, 'half':104, 'double':104},
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def sources():
    for name, digest in PINS.items():
        raw = (HERE/'sources'/name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == digest, 'source bytes: '+name)


def geometry():
    """Separate full-sign enumeration, retaining the source's canonical port order."""
    data = json.loads((HERE/'sources/geometry.json').read_text())
    roots = set()
    for a in range(8):
        for b in range(a+1, 8):
            for sign in [1, -1]:
                row = [0]*8
                row[a], row[b] = 2, 2*sign
                roots.add(tuple(row))
    for row in itertools.product([1, -1], repeat=8):
        if row[0] == 1 and row.count(-1) % 2 == 0:
            roots.add(row)
    removed = {tuple(r) for r in data['F0']+data['C']}
    need(len(roots)==120 and len(removed)==16 and removed <= roots, 'root domain')
    ports = sorted(roots-removed)
    J = J_FIXED.copy()
    N = [i for i in range(104) if i not in J]
    dot = lambda u,v: sum(a*b for a,b in zip(u,v))
    need(all(dot(ports[j], ports[k])==8*(j==k) for j in J for k in J), 'pivots')
    B = [[F(dot(ports[j], ports[n]), 8) for n in N] for j in J]
    need(sum(c!=0 for row in B for c in row)==384, 'B support')
    need(all(c in [0,F(1,2),F(-1,2)] for row in B for c in row), 'B alphabet')
    return B,J,N


def build_program(which, B, J, N):
    """Use only the authenticated predecessor schedule builders, never its evaluator."""
    need(which in EXPECTED_COUNTS, 'unknown adapter')
    tree = ast.parse((HERE/'sources'/f'{which}-verify.py').read_text())
    wanted = {'return_adapter', 'scatter'} if which=='caller' else {'return_adapter'}
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name in wanted]
    need({node.name for node in nodes} == wanted, 'source builder coverage')
    namespace = {'__builtins__': {'int': int, 'enumerate': enumerate}}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<pinned builders>', 'exec'), namespace)
    if which=='caller':
        return [tuple(op) for op in namespace['return_adapter'](J,N,B)]
    raw = namespace['return_adapter'](B,J,N)
    out = []
    for op in raw:
        kind, name = op[:2]
        index = int(name[1:]) + (104 if name[0]=='Y' else 0)
        if kind in ['up','down']:
            need(op[2]==index%104, 'transport port')
            out.append(('lift' if kind=='up' else 'drop',index))
        elif kind=='scale':
            need(F(op[2]) in [F(1,2),F(2)], 'scale alphabet')
            out.append(('half' if F(op[2])==F(1,2) else 'double',index))
        else:
            need(kind=='add', 'source opcode')
            src = int(op[2][1:]) + (104 if op[2][0]=='Y' else 0)
            out.append(('add',index,src,op[3]))
    return out


def plus(a, b, c=F(1)):
    result = a.copy()
    for k,v in b.items():
        result[k] = result.get(k,F(0))+c*v
        if result[k]==0:
            del result[k]
    return result


def boundary(B, J, N):
    """280 independent encoded coordinates; no restriction to producer samples."""
    initial = [{i:F(1)} for i in range(280)]
    frames = ['FULL']*280
    for i in N:
        frames[i] = 'H'+str(i)
    for j in J:
        frames[104+j] = 'H'+str(j)
    expected = [row.copy() for row in initial]
    for a,n in enumerate(N):
        expected[n] = plus(initial[n],initial[104+n],-1)
        for b,j in enumerate(J):
            expected[n] = plus(expected[n],initial[j],B[b][a])
        expected[104+n] = initial[n].copy()
    for b,j in enumerate(J):
        expected[j] = initial[j].copy()
        for a,n in enumerate(N):
            expected[j] = plus(expected[j],expected[n],-B[b][a])
    final_frames = ['FULL']*280
    for i in range(104):
        final_frames[104+i] = 'H'+str(i)
    return initial,frames,expected,final_frames


def run(program, state, frames):
    state = [row.copy() for row in state]
    frames = frames.copy()
    counts = Counter()
    for op in program:
        need(len(op)>=2 and type(op[1]) is int and 0<=op[1]<280, 'register')
        kind,dst = op[:2]
        need(kind in ['lift','drop','half','double','add'], 'operation alphabet')
        counts[kind] += 1
        if kind=='lift':
            need(len(op)==2 and dst<208 and frames[dst]=='H'+str(dst%104), 'lift frame')
            frames[dst] = 'FULL'
        elif kind=='drop':
            need(len(op)==2 and dst<208 and frames[dst]=='FULL', 'drop frame')
            frames[dst] = 'H'+str(dst%104)
        elif kind in ['half','double']:
            need(len(op)==2 and frames[dst]=='FULL', 'scale frame')
            factor = F(1,2) if kind=='half' else F(2)
            state[dst] = {k:v*factor for k,v in state[dst].items()}
        else:
            need(len(op)==4 and type(op[2]) is int and 0<=op[2]<280, 'add source')
            src,sign = op[2:]
            need(dst!=src and type(sign) is int and sign in [-1,1], 'unit add')
            need(frames[dst]==frames[src]=='FULL', 'arithmetic frame')
            state[dst] = plus(state[dst],state[src],sign)
    return state,frames,dict(counts)


def check_program(which, program, B, J, N):
    initial,frames,expected,final_frames = boundary(B,J,N)
    actual,returned,counts = run(program,initial,frames)
    need(actual==expected, 'all encoded-input coefficients')
    need(returned==final_frames, 'physical output frames')
    need(counts==EXPECTED_COUNTS[which], 'complete operation invoice')
    return actual,returned,counts


def audit():
    sources()
    B,J,N = geometry()
    reports = {}
    endpoints = []
    for which in EXPECTED_COUNTS:
        program = build_program(which,B,J,N)
        actual,frames,counts = check_program(which,program,B,J,N)
        endpoints.append((actual,frames))
        reports[which] = {'counts':counts,'events':len(program),
                          'rank_mass':counts['lift']+counts['drop']}
    need(endpoints[0]==endpoints[1], 'matched boundaries')
    need(reports['caller']['events']-reports['consumer']['events']==192, 'event saving')
    return {'independent_encoded_inputs':280,'helpers':72,'B_nonzeros':384,
            'adapters':reports,'unit_adds_saved':192,'real_adds_saved_at_512':196608,
            'supplier_admitted':False,'new_kappa':False}


if __name__=='__main__':
    report = audit()
    print('PASS_P104_RETURN_CONTRACT_MATCH '+json.dumps(report,sort_keys=True))
