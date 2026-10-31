"""P104 = #968's unit in A8 coordinates (lines = 9-bit labels of weight 3 or 7), frames, label classes. Apache-2.0."""
import itertools
P = [11, 19, 35, 131, 259, 13, 21, 37, 69, 133, 261, 41, 73, 265, 49, 81, 145, 273, 161, 193, 321, 385, 14, 22, 38, 70, 134, 262, 26, 74, 138, 50, 146, 274, 98, 290, 194, 322, 386, 28, 44, 140, 268, 84, 148, 276, 100, 164, 292, 196, 324, 388, 56, 88, 152, 280, 168, 296, 200, 328, 392, 112, 176, 304, 208, 336, 400, 224, 352, 416, 508, 506, 502, 494, 478, 446, 382, 254, 505, 501, 493, 477, 445, 381, 253, 499, 475, 443, 379, 251, 487, 471, 439, 375, 247, 463, 431, 367, 239, 415, 351, 223, 319, 191]
LINES = [q for q in range(512) if bin(q).count('1') in (3, 7)]
def root(q):
    c = [(q >> k) & 1 for k in range(9)]
    if sum(c) == 7:
        i, j = [k for k in range(9) if not c[k]]; r = [0] * 9; r[i] = 3; r[j] = -3; return tuple(r)
    return tuple(2 if c[k] else -1 for k in range(9))
RT = {q: root(q) for q in LINES}
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def orth(p, q): return dot(RT[p], RT[q]) == 0
def ldot(a, b): return bin(a & b).count('1') & 1
N = len(P); IDX = {q: i for i, q in enumerate(P)}
ORTH = [[orth(P[i], P[j]) for j in range(N)] for i in range(N)]
def frames(lines=P):
    L = list(lines); out = []
    def rec(cur, cand):
        if len(cur) == 8: out.append(tuple(cur)); return
        for k, q in enumerate(cand):
            rec(cur + [q], [r for r in cand[k + 1:] if orth(q, r)])
    rec([], L); return out
def rank_q(vecs):
    import fractions
    M = [list(map(fractions.Fraction, v)) for v in vecs]; r = 0
    if not M: return 0
    for c in range(len(M[0])):
        p = next((i for i in range(r, len(M)) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        for i in range(len(M)):
            if i != r and M[i][c] != 0:
                f = M[i][c] / M[r][c]; M[i] = [a - f * b for a, b in zip(M[i], M[r])]
        r += 1
    return r
