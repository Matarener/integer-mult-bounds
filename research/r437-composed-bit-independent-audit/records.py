"""Record-level binding: lower a bitE8/1+mut word to the local-call record stream and replay
records in both orientations.

Record layout (six little-endian int32, as in the selected nine-stage caller's global_k.py on
main): MOVE (0, reg, old frame, new frame, rank increment, 0); ADD (1, dst, src, coef, frame,
section tag D1/A2/scatter3/B4/C5); COPY (2, reg, centre, reg frame, centre frame, copy rank);
ERASE (3, reg, centre, reg frame, centre frame, 0).  The centre is register id 2v+R.
The lowering below is written from the word semantics alone: lazy nested climbs before each
gate, one ADD per operand, one COPY/ADD.../ERASE episode per retained total, final climbs.
"""
import struct
from collections import Counter

from wordsem import need

TAG = {'D': 1, 'A': 2, 'scatter': 3, 'B': 4, 'C': 5}


def lower(word, geo):
    v, R = word['v'], word['R']
    n = 2 * v + R
    centre = n
    zero = [k for k, d in enumerate(geo.dim) if d == 0]
    need(len(zero) == 1, 'zero frame')
    zero = zero[0]
    cur = list(word['start'])
    out = []

    def move(r, f):
        if cur[r] != f:
            out.append((0, r, cur[r], f, geo.dim[f] - geo.dim[cur[r]], 0))
            cur[r] = f
    for sec in ('D', 'A', 'scatter', 'B', 'C'):
        if sec == 'scatter':
            for k, q in enumerate(word['ret']):
                out.append((2, q, centre, cur[q], zero, geo.dim[cur[q]] - geo.dim[zero]))
                for t, row in enumerate(word['scatter']):
                    if k in row:
                        out.append((1, v + t, centre, 1, zero, TAG[sec]))
                out.append((3, q, centre, cur[q], zero, 0))
            continue
        for f, d, srcs in word[sec]:
            for r in [d] + list(srcs):
                move(r, f)
            for s in srcs:
                out.append((1, d, s, 1, f, TAG[sec]))
    for r in range(n):
        move(r, word['final'][r])
    return out


def pack(records):
    return b''.join(struct.pack('<6i', *r) for r in records)


def replay(word, geo, records, reverse):
    """F2 replay of a record stream.  Reverse orientation: records in reverse order, every MOVE
    undone (a strict climb of the orthogonal complement), coefficients negated, COPY/ERASE
    exchanged around the same centre.  Returns (bad columns, profile, adds, copies, max
    cancellation-free row l1 norm)."""
    v, R = word['v'], word['R']
    n = 2 * v + R
    centre = n
    H = 8
    dim = (lambda f: H - geo.dim[f]) if reverse else (lambda f: geo.dim[f])
    cur = list(word['final'] if reverse else word['start']) + [-1]
    val = [1 << i for i in range(n)] + [0]
    hist, adds, copies, held = Counter(), 0, 0, None
    norm = [1] * n + [0]          # cancellation-free row l1 bound, as in the selected caller
    maxnorm = 1
    for op, x, y, c, f, z in (reversed(records) if reverse else records):
        if op == 0:
            old, new = (c, y) if reverse else (y, c)
            need(cur[x] == old and dim(new) - dim(old) == f > 0, 'MOVE out of order')
            need(geo.nested(old, new) if not reverse else geo.nested(new, old), 'MOVE not nested')
            cur[x] = new
            hist[f] += 1
        elif op == 1:
            need(x != y and x < n and cur[x] == cur[y] == f, 'ADD operands not at the common frame')
            need(y != centre or held is not None, 'ADD from an empty centre')
            need(x != held, 'ADD into the held register')
            need(c in (1, -1), 'coefficient')
            if c & 1:
                val[x] ^= val[y]
            norm[x] += abs(c) * norm[y]
            maxnorm = max(maxnorm, norm[x])
            adds += 1
        elif op == (3 if reverse else 2):
            need(held is None and y == centre and cur[x] == c and val[centre] == 0, 'COPY discipline')
            held, cur[centre], val[centre], norm[centre] = x, f, val[x], norm[x]
            hist[abs(dim(c) - dim(f))] += 1
            copies += 1
        else:
            need(held == x and y == centre and cur[x] == c and cur[centre] == f and val[centre] == val[x],
                 'ERASE discipline')
            held, cur[centre], val[centre], norm[centre] = None, -1, 0, 0
    need(held is None and cur[:n] == list(word['start'] if reverse else word['final']), 'end frames')
    bad = [i for i in range(n) if val[i] != (1 << i) ^ ((1 << (i - v)) if v <= i < 2 * v else 0)]
    return bad, dict(sorted(hist.items())), adds, copies, maxnorm
