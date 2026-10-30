"""Core of the length-8 index-code enumeration over GF(3) for the 104 P104 ports (standard library only).

Model (see PROOF.md).  Ports q_0..q_103 in F_2^9; i, j conflict iff <q_i, q_j> = 1 (each q_i has odd weight).
A code is an 8-dimensional space W of vectors over the 104 ports such that for every port l some w_l in W has
w_l[l] = 1 and w_l[m] = 0 for every m conflicting with l.  Fix a conflict clique T of size 8: then (w_t)_{t in T}
restricted to T is the identity, so they are a basis and every w_j = sum_{t in T_j} c_{j,t} w_t, where T_j are the
four members of T orthogonal to q_j.  Unknowns: w_t[m] for m not conflicting with t (8 x 48 = 384 trits).
Gauge: rescaling coordinates by signs (diagonal D) maps codes to codes with the same zero pattern and weights;
it normalises c_j (first nonzero = 1) and is tracked on T by sign classes (canonical()).
Search: depth-first over the 96 non-clique ports, choosing at every node the port with the fewest consistent canonical
options (first port with one option, else the minimum); equations kept in incremental Gaussian elimination over
GF(3) on (ones, twos) bitmasks.  Apache-2.0."""
import itertools

T_INDEX = [1, 5, 18, 20, 80, 85, 100, 103]


def dot(a, b):
    return bin(a & b).count('1') & 1


class Model:
    def __init__(self, ports, T=T_INDEX):
        self.P = list(ports); self.N = N = len(self.P)
        P = self.P
        assert N == 104 and len(set(P)) == 104 and all(bin(q).count('1') & 1 for q in P), 'ports'
        self.T = list(T)
        assert all(dot(P[a], P[b]) for a in T for b in T if a != b), 'T is not a conflict clique'
        self.conf = [[m for m in range(N) if m != j and dot(P[j], P[m])] for j in range(N)]
        self.nonconf = [[m for m in range(N) if m != j and not dot(P[j], P[m])] for j in range(N)]
        self.var = {}
        for t in T:
            for m in self.nonconf[t]:
                self.var[t, m] = len(self.var)
        self.NV = len(self.var); self.RHS = 1 << self.NV
        self.others = [j for j in range(N) if j not in T]
        self.Tj = {j: [t for t in T if not dot(P[t], P[j])] for j in self.others}
        assert all(len(v) == 4 for v in self.Tj.values()), 'T_j size'
        self.OPT = [c for c in itertools.product((0, 1, 2), repeat=4)
                    if any(c) and [x for x in c if x][0] == 1]
        assert len(self.OPT) == 40
        self.EQS = {(j, c): self.equations(j, c) for j in self.others for c in self.OPT}
        self.pivots = {}; self.stack = []

    # ---- GF(3) rows as (ones, twos) bitmasks; bit NV is the right-hand side
    @staticmethod
    def add(x, y):
        x1, x2 = x; y1, y2 = y
        return ((x1 & ~y1 & ~y2) | (y1 & ~x1 & ~x2) | (x2 & y2), (x2 & ~y1 & ~y2) | (y2 & ~x1 & ~x2) | (x1 & y1))

    def equations(self, j, c):
        eqs = []; cd = {t: k for t, k in zip(self.Tj[j], c) if k}
        for m in self.conf[j]:
            r1 = r2 = 0
            for t, k in cd.items():
                v = self.var.get((t, m))
                if v is None:
                    continue
                if k == 1: r1 |= 1 << v
                else: r2 |= 1 << v
            if r1 | r2:
                eqs.append((r1, r2))
        r1 = r2 = 0
        for t, k in cd.items():
            v = self.var[t, j]
            if k == 1: r1 |= 1 << v
            else: r2 |= 1 << v
        eqs.append((r1 | self.RHS, r2))
        return eqs

    def push(self, row):
        r1, r2 = row; piv = self.pivots; RHS = self.RHS
        while True:
            bits = (r1 | r2) & ~RHS
            if not bits:
                return not (r1 | r2)
            c = (bits & -bits).bit_length() - 1
            p = piv.get(c)
            if p is None:
                if r2 >> c & 1:
                    r1, r2 = r2, r1
                piv[c] = (r1, r2); self.stack.append(c); return True
            if r1 >> c & 1:
                r1, r2 = self.add((r1, r2), (p[1], p[0]))
            else:
                r1, r2 = self.add((r1, r2), p)

    def mark(self):
        return len(self.stack)

    def undo(self, k):
        while len(self.stack) > k:
            self.pivots.pop(self.stack.pop())

    def apply(self, j, c):
        """push the equations of (j, c); on inconsistency undo and return False"""
        mk = self.mark()
        for eq in self.EQS[j, c]:
            if not self.push(eq):
                self.undo(mk); return False
        return True

    def consistent(self, j, c):
        mk = self.mark(); ok = self.apply(j, c)
        if ok:
            self.undo(mk)
        return ok

    # ---- sign gauge on T
    def canonical(self, j, c, cls):
        sup = [(t, k) for t, k in zip(self.Tj[j], c) if k]
        seen = {cls[sup[0][0]]}
        for t, k in sup[1:]:
            q = cls[t]
            if q in seen:
                continue
            if k != 1:
                return False
            seen.add(q)
        return True

    def merged(self, j, c, cls):
        ids = {cls[t] for t, k in zip(self.Tj[j], c) if k}; new = min(ids)
        return {t: (new if q in ids else q) for t, q in cls.items()}

    def options(self, j, cls):
        return [c for c in self.OPT if self.canonical(j, c, cls) and self.consistent(j, c)]

    def choose(self, rest, cls):
        """MRV choice: (port, options) or (port, []) for a dead node"""
        best = None
        for j in sorted(rest):
            ok = self.options(j, cls)
            if not ok:
                return j, []
            if best is None or len(ok) < len(best[1]):
                best = (j, ok)
            if len(ok) == 1:
                break
        return best

    def solution(self):
        """back-substitute the unique solution (requires no free variables); returns the 104 x 104 matrix w (rows w_l)"""
        assert len(self.pivots) == self.NV, 'free variables'
        x = [0] * self.NV
        for c in sorted(self.pivots, reverse=True):
            r1, r2 = self.pivots[c]
            s = 1 if r1 >> self.NV & 1 else (2 if r2 >> self.NV & 1 else 0)
            for cc in range(c + 1, self.NV):
                if r1 >> cc & 1: s -= x[cc]
                elif r2 >> cc & 1: s -= 2 * x[cc]
            x[c] = s % 3
        return x
