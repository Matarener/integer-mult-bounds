"""Independent local replay of a G20 local word (written from scratch; imports no package code).

Model (as stated in the packages' PROOF.md / native.py contract):
- every wire carries a payload in a frame f; frame f is a subspace span(B_f) of Q^8 with complement basis A_f;
- ADD d s f : x_d += x_s (char 2 / XOR of symbols), only if both wires sit in frame f;
- Q d s t k : paid native query moving wire d from frame s to frame t; frames must be nested and
  k = |dim s - dim t| in 1..7; action on payload = reflection I - 2(P_hi - P_lo), P = orthogonal projector;
- ZERO_Q : free move, only for an identically zero payload; ERASE/INIT only on owned wires.
Checks (exact, over Q, no moduli):
 frames: rank(B)=dim, rank(A)=8-dim, A.B^T=0;  nesting by subspace inclusion (rank of stacked basis);
 GF(2) endpoint rows; full operator endpoint with exact 8x8 rational matrices per input symbol;
 paid histogram; owned fields end at zero.
Usage: python3 audit_local.py FRAMES.json WORD.json.gz [label]
"""
from fractions import Fraction as Fr
from collections import Counter
import gzip, json, sys, time


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def rank(rows):
    m = [[Fr(x) for x in r] for r in rows]
    r = 0
    ncols = len(m[0]) if m else 0
    for c in range(ncols):
        p = next((i for i in range(r, len(m)) if m[i][c] != 0), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        for i in range(len(m)):
            if i != r and m[i][c] != 0:
                f = m[i][c] / m[r][c]
                m[i] = [a - f * b for a, b in zip(m[i], m[r])]
        r += 1
    return r


def inv(m):
    n = len(m)
    a = [[Fr(x) for x in row] + [Fr(int(i == j)) for j in range(n)] for i, row in enumerate(m)]
    for c in range(n):
        p = next(i for i in range(c, n) if a[i][c] != 0)
        a[c], a[p] = a[p], a[c]
        v = a[c][c]
        a[c] = [x / v for x in a[c]]
        for i in range(n):
            if i != c and a[i][c] != 0:
                f = a[i][c]
                a[i] = [x - f * y for x, y in zip(a[i], a[c])]
    return [row[n:] for row in a]


def mul(a, b):
    return tuple(tuple(sum(x * y for x, y in zip(r, c)) for c in zip(*b)) for r in a)


I8 = tuple(tuple(Fr(int(i == j)) for j in range(8)) for i in range(8))


def projector(B):
    if not B:
        return tuple(tuple(Fr(0) for _ in range(8)) for _ in range(8))
    Bt = list(map(list, zip(*B)))
    G = mul(B, Bt)
    return mul(mul(Bt, inv(G)), B)


def main(frames_path, word_path, label):
    frames = json.load(open(frames_path))['frames']
    w = json.loads(gzip.decompress(open(word_path, 'rb').read()))
    rec, owned, start, final = w['records'], set(w['owned']), w['start'], w['final']
    width = len(start)
    log(label, 'records', len(rec), 'width', width, 'owned', len(owned))
    used = set(start) | set(final)
    for e in rec:
        if e[0] == 'ADD': used.add(e[3])
        elif e[0] in ('Q', 'ZERO_Q'): used |= {e[2], e[3]}
        elif e[0] in ('ERASE', 'INIT') and e[2] is not None: used.add(e[2])
    used.discard(None)
    need(all(start[i] is not None and final[i] is not None for i in range(width) if i not in owned), 'non-owned wires have frames')
    dim, P = {}, {}
    for f in sorted(used):
        fr = frames[str(f)]
        A, B = fr['A'], fr['B']
        need(rank(B) == len(B) == fr['dim'] and (not A or rank(A) == len(A)) and len(A) + len(B) == 8, 'frame basis %d' % f)
        need(all(sum(Fr(x) * Fr(y) for x, y in zip(a, b)) == 0 for a in A for b in B), 'frame orthogonality %d' % f)
        dim[f] = fr['dim']
        P[f] = projector(B)
        need(mul(P[f], P[f]) == P[f], 'projector idempotent %d' % f)
    log(label, 'frames used', len(used), 'all bases exact')
    R = {f: tuple(tuple(I8[i][j] - 2 * P[f][i][j] for j in range(8)) for i in range(8)) for f in used}
    nest = {}

    def query(s, t, k):
        key = (s, t, k)
        if key not in nest:
            lo, hi = (s, t) if dim[s] < dim[t] else (t, s)
            need(1 <= k <= 7 and dim[hi] - dim[lo] == k, 'query rank %s' % (key,))
            Bl, Bh = frames[str(lo)]['B'], frames[str(hi)]['B']
            need(rank(Bh + Bl) == rank(Bh), 'nesting span(B_lo) in span(B_hi) %s' % (key,))
            Q = tuple(tuple(I8[i][j] - 2 * (P[hi][i][j] - P[lo][i][j]) for j in range(8)) for i in range(8))
            need(mul(R[s], R[t]) == Q, 'telescoping R_s R_t = residual reflection %s' % (key,))
            nest[key] = Q
        return nest[key]

    st = list(start)
    rows = [1 << i for i in range(width)]
    fld = [{I8: 1 << i} for i in range(width)]
    paid, ops = Counter(), Counter()
    for ix, e in enumerate(rec):
        op, d = e[0], e[1]
        ops[op] += 1
        if op == 'ERASE':
            need(d in owned, 'erase non-owned at %d' % ix)
            rows[d] = 0; fld[d] = {}; st[d] = e[2]
        elif op == 'INIT':
            need(d in owned and rows[d] == 0 and not fld[d], 'INIT of nonzero/non-owned at %d' % ix)
            st[d] = e[2]
        elif op == 'ADD':
            s, f = e[2], e[3]
            need(d != s and st[d] == f and st[s] == f, 'ADD frame mismatch at %d' % ix)
            rows[d] ^= rows[s]
            out = dict(fld[d])
            for m, b in fld[s].items():
                z = out.get(m, 0) ^ b
                if z: out[m] = z
                else: out.pop(m, None)
            fld[d] = out
        elif op in ('Q', 'ZERO_Q'):
            s, t, k = e[2], e[3], e[4]
            need(st[d] == s, 'query from wrong frame at %d' % ix)
            Q = query(s, t, k)
            st[d] = t
            if op == 'ZERO_Q':
                need(rows[d] == 0 and not fld[d], 'free move of nonzero payload at %d' % ix)
            else:
                paid[k] += 1
                new = {}
                for m, b in fld[d].items():
                    mm = mul(Q, m)
                    z = new.get(mm, 0) ^ b
                    if z: new[mm] = z
                    else: new.pop(mm, None)
                fld[d] = new
        else:
            need(False, 'unknown op ' + op)
        if ix % 2000 == 0:
            log(label, 'event', ix, dict(ops))
    need(st == final, 'final frames')
    expected = [0 if i in owned else (1 << i) ^ ((1 << (i - 111)) if 111 <= i < 222 else 0) for i in range(width)]
    need(rows == expected, 'GF(2) endpoint rows')
    for o in range(width):
        want = {}
        r = expected[o]
        while r:
            b = r & -r; i = b.bit_length() - 1; r ^= b
            m = mul(R[final[o]], R[start[i]])
            z = want.get(m, 0) ^ b
            if z: want[m] = z
            else: want.pop(m, None)
        need(fld[o] == want, 'operator endpoint at output %d' % o)
    res = dict(label=label, records=len(rec), ops=dict(ops), paid=dict(sorted(paid.items())),
               frames_used=len(used), distinct_queries=len(nest), width=width, owned=len(owned),
               endpoint='exact rational operator endpoint on all %d columns' % width)
    log('PASS', json.dumps(res))
    return res


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else sys.argv[2])
