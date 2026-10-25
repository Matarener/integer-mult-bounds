# SPDX-License-Identifier: Apache-2.0
"""Exact dirty scalar blocks, adapted from PR3941; retained auditors are separate."""
from fractions import Fraction as Q
import hashlib,json

def need(ok,why):
    if not ok:raise ValueError(why)

def object_hash(x):
    return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def block_matrix(gates,registers=None):
    """Own rational scalar-block check, independent of retained interpreters.

    Every input row is an independent symbol, so equality is on all dirty states.
    Frames are checked separately; native gates are forbidden in this block.
    """
    if registers is None:registers=sorted({r for g in gates for r in (g[1:3] if g[0]=='add' else g[1:2])})
    rows={r:{r:Q(1)} for r in registers}
    for g in gates:
        if g[0]=='scale':
            q=Q(g[2],g[3]);need(q!=0,'zero scalar')
            rows[g[1]]={k:v*q for k,v in rows[g[1]].items()}
        else:
            need(g[0]=='add' and g[1]!=g[2],'non-scalar block or self ADD')
            q=Q(g[3],g[4]);need(q!=0,'zero ADD')
            for k,v in rows[g[2]].items():
                z=rows[g[1]].get(k,0)+q*v
                if z:rows[g[1]][k]=z
                else:rows[g[1]].pop(k,None)
    return [[str(rows[r].get(c,0)) for c in registers] for r in registers]

def block_equal(before,after):
    regs=sorted({r for g in before+after for r in (g[1:3] if g[0]=='add' else g[1:2])})
    b,a=block_matrix(before,regs),block_matrix(after,regs)
    need(a==b,'arbitrary-dirty scalar block differs')
    return {'registers':regs,'matrix_sha256':object_hash(a)}

def first_block(w,new,rec):
    lo=min(rec['index'],rec['cut']);hi=max(rec['index']+1,rec['cut'])
    return block_equal(w[rec['section']][lo:hi],new[rec['section']][lo:hi])

