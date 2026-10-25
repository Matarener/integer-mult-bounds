"""Actual signed-native row interpreter.

Event/ownership/version semantics adapted from Mark (Matarener), #5427,
389578f2d3ef075495ce76f08100ac50e18f7d40. Native words by Dillon,
Cao Yifan and the retained Cinna Davis/zxv lineage. The actual monomial
canonicalization and all-width certificate are new. Apache-2.0; substantial
OpenAI Codex assistance for THU New Media Research Center (@thu-nmrc).
"""
from fractions import Fraction as Fr
from pathlib import Path
from hashlib import sha256
import gzip,json
import monomial as M
ROOT=Path(__file__).resolve().parents[2]
INPUTS={
 'source':('research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz','7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'),
 'provider':('research/native-rank8-helper-provider/WORD.json.gz','7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc')}
def need(ok,message):
 if not ok:raise ValueError(message)
def read(name):
 path,digest=INPUTS[name];raw=(ROOT/path).read_bytes();need(sha256(raw).hexdigest()==digest,'source bytes '+path)
 return json.loads(gzip.decompress(raw))
operators=[M.IDENTITY];lookup={M.IDENTITY:0};products={};base={};back={}
def intern(op):
 if op not in lookup:lookup[op]=len(operators);operators.append(op)
 return lookup[op]
def initialize(canon):
 need(len(operators)==1,'one initialization')
 base.update({w['op']:intern(M.native(w['G_columns'])) for w in canon['warps']})
 base.update({-k:intern(M.inverse(operators[v])) for k,v in list(base.items())})
 back.update({k:intern(M.conjugate(operators[v])) for k,v in base.items()})
def left_row(row,op,backward):
 left=(back if backward else base)[op];out={}
 for (role,right),q in row.items():
  pair=left,right
  if pair not in products:products[pair]=intern(M.multiply(operators[left],operators[right]))
  key=role,products[pair];z=out.get(key,0)+q
  if z:out[key]=z
  else:out.pop(key,None)
 return out

def span_set(basis):
    out = {0}
    for v in basis:
        out |= {x ^ v for x in tuple(out)}
    need(len(out) == 1 << len(basis), 'independent frame basis')
    return out

def native_replay(canon, program, backward):
    """Exact rows (convention of research/kappa-owned-relation-20261023/native.py).
    Returns the list of distinct full-frame versions, final rows and final frames."""
    spaces = [span_set(b) for b in canon['frames']]
    full = {i for i, s in enumerate(spaces) if len(s) == 512}
    need(len(full) == 1, 'one full frame')
    rows = {('L', i): {(('L', i), 0): Fr(1)} for i in range(632)}
    frames = {('L', i): canon['start'][i] for i in range(632)}

    def get(r):
        if r not in rows:
            rows[r] = {(r, 0): Fr(1)}
            frames[r] = None
        return rows[r]

    seen, versions = set(), []
    for e in program:
        k, touched = e[0], None
        if k == 'scalar':
            g, frame = e[1], e[2]
            dst = tuple(g[1]); get(dst); touched = dst
            if g[0] == 'clear':
                rows[dst] = {}; frames[dst] = frame
            elif g[0] == 'copy':
                src = tuple(g[2]); need(frames[src] == frame, 'copy frame')
                rows[dst] = dict(get(src)); frames[dst] = frame
            elif g[0] == 'add':
                src = tuple(g[2]); need(frames[src] == frame == frames[dst], 'same-frame ADD')
                q = Fr(g[3], g[4]); r = rows[dst]
                for key, v in get(src).items():
                    nv = r.get(key, 0) + q * v
                    if nv:
                        r[key] = nv
                    else:
                        r.pop(key, None)
            elif g[0] == 'scale':
                q = Fr(g[2], g[3]); rows[dst] = {a: q * v for a, v in rows[dst].items()}
            else:
                raise AssertionError('unknown scalar ' + repr(g[0]))
        elif k == 'warp':
            _, role, op, old, new = e
            dst = tuple(role); get(dst); touched = dst
            need(frames[dst] == old, 'warp input frame')
            rows[dst] = left_row(rows[dst], op, backward)
            frames[dst] = new
        elif k == 'climb':
            dst = ('L', e[2]); need(frames[dst] == e[3], 'climb input frame')
            frames[dst] = e[4]; touched = dst
        elif k == 'center':
            dst = ('C', e[1]); get(dst); frames[dst] = e[3]; touched = dst
        elif k == 'zero_retag':
            dst = ('L', e[1]); need(frames[dst] == e[2] and not rows[dst], 'zero retag on a zero row')
            frames[dst] = e[3]; touched = dst
        else:
            need(k in ('phase', 'adapter'), 'unknown event ' + repr(k))
        if touched is not None and frames[touched] in full and rows[touched]:
            key = frozenset(rows[touched].items())
            if key not in seen:
                seen.add(key); versions.append(dict(rows[touched]))
    return versions, rows, frames, full

def role_class(key):
    r = key[0]
    if r[0] == 'L' and r[1] < 112:
        return 'x'
    if r[0] == 'L' and r[1] < 224:
        return 'y'
    return 'h'
