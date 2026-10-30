#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Four-role exact minimum for diag([xyx],[xyx],[e],[e]) in M4(F2[S3]).

Model (unchanged from research/s3-three-role-xyx, now with four roles): a paid
call is D_N(g) = I + ([g]+[e]) N with g in {x, y}, x = (1 2), y = (2 3), and N
any rank-one idempotent u v^T of M_m(F2) (v.u = 1).  A word is the ordered
product of its calls; equality is required in M_m(F2[S3]).

Search engine: the algebra isomorphism Phi : F2[S3] -> M2(F2) x F2[C2],
[g] -> (rho(g), c^sign(g)), applied entrywise.  In the C2 block every paid
factor is I + delta N with delta = c + 1 and delta^2 = 0, so a word has image
I + delta * (XOR of its N).  The M2 block is an 2m x 2m binary matrix.  The
pair is a faithful encoding of the word's product.

Lower bound: every word of length <= 5 misses the target, by the involution
meet-in-the-middle ball(I,3) cap T*ball(I,2) = empty.  Upper bound: the direct
six-call word.  An independent engine multiplies in M_m(F2[S3]) directly and
checks the witness, the ball(I,2) set under Phi and the involution property.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PRED_CERT = ROOT / "research/s3-three-role-xyx/CERTIFICATE.json"
EXPECTED_PRED_LAYERS = [1, 56, 1750, 45396]


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit(f"FAIL_S3_XYX_FOUR_ROLE: {message}")


# ---------------------------------------------------------------- group S3 --
def compose(p, q):
    """Permutation product p*q, applying q first (predecessor convention)."""
    return tuple(p[q[i]] for i in range(3))


ELEMENTS = tuple(itertools.permutations(range(3)))
INDEX = {g: i for i, g in enumerate(ELEMENTS)}
MUL = tuple(tuple(INDEX[compose(a, b)] for b in ELEMENTS) for a in ELEMENTS)
E = INDEX[(0, 1, 2)]
X = INDEX[(1, 0, 2)]
Y = INDEX[(0, 2, 1)]
XYX = MUL[MUL[X][Y]][X]
LABELS = (X, Y)
need(XYX == MUL[MUL[Y][X]][Y] == INDEX[(2, 1, 0)], "xyx must be (1 3) = yxy")


def sign(p) -> int:
    return sum(1 for i in range(3) for j in range(i + 1, 3) if p[i] > p[j]) & 1


# rho: S3 permutes the three nonzero vectors of F2^2, which is linear.
POINTS = (0b01, 0b10, 0b11)  # vectors as bitmasks (bit a = coordinate a)


def rho(p):
    """2x2 binary matrix as tuple of column masks: column a = image of e_a."""
    return (POINTS[p[POINTS.index(0b01)]], POINTS[p[POINTS.index(0b10)]])


def mat2_mul(a, b):
    out = []
    for col in b:
        v = 0
        for k in range(2):
            if (col >> k) & 1:
                v ^= a[k]
        out.append(v)
    return tuple(out)


def check_isomorphism() -> None:
    for p in ELEMENTS:
        for q in ELEMENTS:
            need(rho(compose(p, q)) == mat2_mul(rho(p), rho(q)), "rho not a hom")
            need(sign(compose(p, q)) == sign(p) ^ sign(q), "sign not a hom")
    # Phi on the six basis elements: 4 bits of rho(g) and 2 bits of c^sign(g).
    rows = []
    for p in ELEMENTS:
        r = rho(p)
        rows.append(r[0] | (r[1] << 2) | (1 << (4 + sign(p))))
    rank, rows = 0, list(rows)
    for bit in range(6):
        piv = next((i for i in range(rank, 6) if (rows[i] >> bit) & 1), None)
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for i in range(6):
            if i != rank and (rows[i] >> bit) & 1:
                rows[i] ^= rows[rank]
        rank += 1
    need(rank == 6, "Phi must be bijective on F2[S3]")


# ------------------------------------------------- fast engine (image of Phi)
# State: M2 block as a 2m x 2m binary matrix stored column-major, one byte per
# column (bit r = row r, index r = 2*role + component), packed with the C2 block
# delta-part V (m*m bits, row-major) as  state = (A << 16) | V.
class Fast:
    def __init__(self, m: int):
        self.m = m
        self.n = 2 * m
        self.idem = tuple(
            (u, v)
            for u in range(1, 1 << m)
            for v in range(1, 1 << m)
            if (u & v).bit_count() & 1
        )
        self.calls = tuple((g, u, v) for g in LABELS for u, v in self.idem)
        self.ops = tuple(self._op(c) for c in self.calls)

    def _kron(self, w: int, vec: int) -> int:
        out = 0
        for i in range(self.m):
            if (w >> i) & 1:
                out |= vec << (2 * i)
        return out

    def _op(self, call):
        g, u, v = call
        r = rho(ELEMENTS[g])
        # rho(g) + I = p q^T has rank one for a transposition.
        diff = (r[0] ^ 0b01, r[1] ^ 0b10)
        cols = [a for a in range(2) if diff[a]]
        need(len(cols) >= 1 and len({diff[a] for a in cols}) == 1, "rank one")
        p, q = diff[cols[0]], sum(1 << a for a in cols)
        umask = self._kron(u, p)  # column vector u (x) p
        vmask = self._kron(v, q)  # row vector v (x) q
        ulist = tuple(j for j in range(self.n) if (umask >> j) & 1)
        spread = sum(1 << (8 * j) for j in range(self.n) if (vmask >> j) & 1)
        nmat = 0
        for i in range(self.m):
            for j in range(self.m):
                if (u >> i) & 1 and (v >> j) & 1:
                    nmat |= 1 << (i * self.m + j)
        return ulist, spread, nmat

    def identity(self) -> int:
        a = sum(1 << (8 * j + j) for j in range(self.n))
        return a << 16

    def step(self, state: int, op) -> int:
        """Right-multiply by D_N(g): A += (A (u(x)p)) (v(x)q)^T, V ^= N."""
        ulist, spread, nmat = op
        a = state >> 16
        c = 0
        for j in ulist:
            c ^= (a >> (8 * j)) & 0xFF
        return ((a ^ (c * spread)) << 16) | ((state & 0xFFFF) ^ nmat)

    def diag_target(self, labels) -> int:
        """Image of diag([g_0], ..., [g_{m-1}])."""
        a, vbits = 0, 0
        for i, g in enumerate(labels):
            r = rho(ELEMENTS[g])
            for k in range(2):
                a |= r[k] << (2 * i) << (8 * (2 * i + k))
            if sign(ELEMENTS[g]):
                vbits |= 1 << (i * self.m + i)
        return (a << 16) | vbits

    def left_mul(self, t: int, s: int) -> int:
        """t * s for arbitrary encoded t, s (A part product, V parts add)."""
        ta, sa = t >> 16, s >> 16
        out = 0
        for j in range(self.n):
            col = (sa >> (8 * j)) & 0xFF
            v = 0
            for k in range(self.n):
                if (col >> k) & 1:
                    v ^= (ta >> (8 * k)) & 0xFF
            out |= v << (8 * j)
        return (out << 16) | ((t ^ s) & 0xFFFF)

    def layers(self, depth: int):
        seen = {self.identity()}
        frontier = [self.identity()]
        sizes = [1]
        for _ in range(depth):
            nxt = []
            for s in frontier:
                for op in self.ops:
                    w = self.step(s, op)
                    if w not in seen:
                        seen.add(w)
                        nxt.append(w)
            frontier = nxt
            sizes.append(len(nxt))
        return seen, sizes

    def short_hits(self, target: int, ball2: set) -> int:
        """Number of (X, call) with X*call in target*ball2, plus X in it."""
        shifted = {self.left_mul(target, b) for b in ball2}
        hits = sum(1 for x in ball2 if x in shifted)
        for x in ball2:
            for op in self.ops:
                if self.step(x, op) in shifted:
                    hits += 1
        return hits


# ----------------------------------------- independent engine: M_m(F2[S3]) --
class Exact:
    """Matrices over F2[S3] as tuples of 6-bit group masks, row-major."""

    def __init__(self, m: int):
        self.m = m

    def conv(self, a: int, b: int) -> int:
        out = 0
        for i in range(6):
            if (a >> i) & 1:
                for j in range(6):
                    if (b >> j) & 1:
                        out ^= 1 << MUL[i][j]
        return out

    def factor(self, call):
        g, u, v = call
        m = self.m
        cells = [0] * (m * m)
        for i in range(m):
            cells[i * m + i] = 1 << E
        for i in range(m):
            for j in range(m):
                if (u >> i) & 1 and (v >> j) & 1:
                    cells[i * m + j] ^= (1 << g) | (1 << E)
        return tuple(cells)

    def mul(self, a, b):
        m = self.m
        out = []
        for i in range(m):
            for j in range(m):
                acc = 0
                for k in range(m):
                    acc ^= self.conv(a[i * m + k], b[k * m + j])
                out.append(acc)
        return tuple(out)

    def identity(self):
        return self.diag([E] * self.m)

    def diag(self, labels):
        m = self.m
        cells = [0] * (m * m)
        for i, g in enumerate(labels):
            cells[i * m + i] = 1 << g
        return tuple(cells)

    def word(self, calls):
        state = self.identity()
        for c in calls:
            state = self.mul(state, self.factor(c))
        return state

    def phi(self, mat, fast: Fast) -> int:
        """Entrywise Phi into the fast encoding."""
        m = self.m
        a, vbits = 0, 0
        for i in range(m):
            for j in range(m):
                cell = mat[i * m + j]
                block = (0, 0)
                c2 = [0, 0]
                for g in range(6):
                    if (cell >> g) & 1:
                        r = rho(ELEMENTS[g])
                        block = (block[0] ^ r[0], block[1] ^ r[1])
                        c2[sign(ELEMENTS[g])] ^= 1
                for k in range(2):
                    a |= block[k] << (2 * i) << (8 * (2 * j + k))
                # p + q c = (p + q) + q delta; the delta part is q.
                if c2[1]:
                    vbits |= 1 << (i * m + j)
                need(c2[0] ^ c2[1] == (1 if i == j else 0),
                     "augmentation of a word must be the identity")
        return (a << 16) | vbits


def digest(states) -> str:
    h = hashlib.sha256()
    for s in sorted(states):
        h.update(s.to_bytes(16, "big"))
    return h.hexdigest()


def main() -> int:
    check_isomorphism()

    # Calibration: three roles reproduce the predecessor's layer sizes.
    pred = json.loads(PRED_CERT.read_text())
    need(pred["layers_from_identity"] == EXPECTED_PRED_LAYERS,
         "pinned predecessor certificate layers changed")
    f3 = Fast(3)
    _, sizes3 = f3.layers(3)
    need(sizes3 == EXPECTED_PRED_LAYERS, f"m=3 layers {sizes3}")

    m = 4
    fast = Fast(m)
    need(len(fast.idem) == 120 and len(fast.calls) == 240, "120 / 240")
    exact = Exact(m)

    # Involutions: D_N(g)^2 = I, so word inverses are reversed words.
    for call, op in zip(fast.calls, fast.ops):
        f = exact.factor(call)
        need(exact.mul(f, f) == exact.identity(), "factor not an involution")
        need(fast.step(fast.step(fast.identity(), op), op) == fast.identity(),
             "fast factor not an involution")

    target_labels = [XYX, XYX, E, E]
    target = fast.diag_target(target_labels)
    need(exact.phi(exact.diag(target_labels), fast) == target, "target image")

    # Direct six-call witness: x y x on role 0, then on role 1.
    e00, e11 = (0b0001, 0b0001), (0b0010, 0b0010)
    direct = [(g, *e) for e in (e00, e11) for g in (X, Y, X)]
    need(exact.word(direct) == exact.diag(target_labels), "direct word")
    for drop in range(6):
        short = direct[:drop] + direct[drop + 1:]
        need(exact.word(short) != exact.diag(target_labels), "omission hit")

    ball2, sizes2 = fast.layers(2)
    # Independent engine: ball(I,2) built in M4(F2[S3]) and mapped by Phi.
    ex_ball = {exact.identity()}
    ex_front = [exact.identity()]
    factors = [exact.factor(c) for c in fast.calls]
    for _ in range(2):
        nxt = []
        for s in ex_front:
            for f in factors:
                w = exact.mul(s, f)
                if w not in ex_ball:
                    ex_ball.add(w)
                    nxt.append(w)
        ex_front = nxt
    need(len(ex_ball) == len(ball2), "independent ball(I,2) size differs")
    need({exact.phi(s, fast) for s in ex_ball} == ball2, "Phi(ball) differs")

    # Lower bound: no word of length <= 5 reaches the target.
    hits = fast.short_hits(target, ball2)
    need(hits == 0, f"short word reaches target ({hits} hits)")

    # Positive controls: the same search finds length-5 and length-4 targets.
    ctrl5 = fast.diag_target([XYX, MUL[X][Y], E, E])
    need(fast.short_hits(ctrl5, ball2) > 0, "length-5 control missed")
    ctrl4 = fast.diag_target([X, Y, MUL[X][Y], E])
    need(fast.short_hits(ctrl4, ball2) > 0, "length-4 control missed")
    # The rho quotient alone (C2 block dropped) already has no short hit.
    mask = ~0xFFFF
    rshift = {fast.left_mul(target, b) & mask for b in ball2}
    rho_hits = sum(1 for x in ball2 if x & mask in rshift)
    rho_hits += sum(1 for x in ball2 for op in fast.ops
                    if fast.step(x, op) & mask in rshift)
    need(rho_hits == 0, f"rho quotient reaches target ({rho_hits} hits)")

    print(
        "PASS_S3_XYX_FOUR_ROLE roles=4 idempotents=120 calls=240 "
        f"m3_layers={sizes3} ball_i2_layers={sizes2} ball_i2={len(ball2)} "
        f"ball_i2_digest={digest(ball2)[:16]} short_hits=0 "
        f"rho_quotient_hits={rho_hits} direct=6 target_minimum=6 "
        "dirty_lowers=false no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
