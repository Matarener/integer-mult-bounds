#!/usr/bin/env python3
"""Mutation and contract controls for the new tail only. Apache-2.0."""
from __future__ import annotations
import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('role_exchange', P/'verify.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
R,A,J,N,B = m.geometry()
ops = m.program(J,N,B)


def reject(word):
    try:
        state,frames,_,_ = m.execute(A,word)
        m.verify_endpoint(state,frames,A,J,N,B)
    except ValueError:
        return
    raise ValueError('mutation accepted')


def main():
    cases = 0
    word = ops[:]
    k = next(i for i,op in enumerate(word) if op[0] == 'add')
    op = word[k]
    word[k] = op[:-1]+(-op[-1],)
    reject(word); cases += 1
    for kind in ('double','lift','drop'):
        word = ops[:]
        del word[next(i for i,op in enumerate(word) if op[0] == kind)]
        reject(word); cases += 1
    # Omit the old-Y subtraction; roots alone must not substitute for dirty Y.
    reject([op for op in ops if not(op[0]=='add' and op[1] in [104+j for j in J])]); cases += 1
    # Replacing the data pivot by an old arbitrary dirty helper is not free.
    word = ops[:]
    k = next(i for i,op in enumerate(word) if op[0] == 'add')
    word[k] = ('add',208,word[k][2],word[k][3])
    reject(word); cases += 1
    state,frames,_,_ = m.execute(A,ops)
    m.verify_endpoint(state,frames,A,J,N,B)
    m.need(any(state[104+i] != [m.F(k in (i,104+i)) for k in range(280)] for i in N),
           'old bank names falsely accepted as corrected outputs'); cases += 1
    # The source-preserving correction is unimodular, despite rank(C mod 3)=96.
    shear = [[m.F(i==j) for j in range(208)] for i in range(208)]
    for i in range(104):
        for j in range(104):
            shear[104+i][j] = m.F(i==j)-A[i][j]
    m.need(m.mod_rank(shear)==208, 'scope control: ordinary shear'); cases += 1
    result = m.calculate()
    bad = dict(result); bad['schema_version'] = True
    m.need(m.encoded(bad) != m.encoded(result), 'Boolean schema accepted'); cases += 1
    bad = dict(result); bad['tail_native_profile'] = {'1': 104}
    m.need(m.encoded(bad) != m.encoded(result), 'half-price frame invoice accepted'); cases += 1
    # Authenticating the source is mandatory in normal mode, even without a checkout.
    with tempfile.TemporaryDirectory() as d:
        q = Path(d)/'duplicate.json'; q.write_text('{"schema_version":1,"schema_version":1}')
        try:
            m.load(q)
        except ValueError:
            pass
        else:
            raise ValueError('duplicate JSON key accepted')
    cases += 1
    # A single original integer basis input attains denominator four transiently.
    m.need(result['maximum_scalar_coefficient_denominator']==4, 'sharp scalar grid')
    cases += 1
    # Actual isolated CLI rejection, including immutable bytes after failure.
    with tempfile.TemporaryDirectory() as d:
        q = Path(d)
        (q/'verify.py').write_bytes((P/'verify.py').read_bytes())
        for label, replacement, expected in (
            ('boolean', dict(result, schema_version=True), 'typed result mismatch'),
            ('invoice', dict(result, tail_native_profile={'1':104}), 'typed result mismatch'),
        ):
            (q/'RESULT.json').write_text(json.dumps(replacement))
            before = {f.name:f.read_bytes() for f in q.iterdir() if f.is_file()}
            run = subprocess.run([sys.executable,'-I','-O','-B',str(q/'verify.py'),'--algebra-only'],capture_output=True,text=True)
            m.need(run.returncode != 0 and expected in run.stderr and not run.stdout, 'CLI '+label)
            m.need(before == {f.name:f.read_bytes() for f in q.iterdir() if f.is_file()}, 'CLI changed files')
            cases += 1
        (q/'RESULT.json').write_text(json.dumps(result))
        run = subprocess.run([sys.executable,'-I','-B',str(q/'verify.py')],capture_output=True,text=True)
        m.need(run.returncode != 0 and 'FileNotFoundError' in run.stderr and not run.stdout, 'missing source accepted')
        cases += 1
    print(f'PASS_P104_ROLE_EXCHANGE_CONTROLS cases={cases} positive=1')

if __name__ == '__main__':
    main()
