"""Independent stdlib semantics of a bitE8/1+mut word (format of selected #589).

Written from scratch for this audit from the format description in the selected
#589 package on main (research/e8-bit-p111-tuned/code/xcheck_p.py docstring,
code/pwordl.py builder); no code is imported from any audited package.

Registers: sources 0..v-1, targets v..2v-1, helpers 2v..2v+R-1.  A gate
[f, d, srcs] first moves every operand to frame f (a strict, nested climb when
it is elsewhere) and then sets d <- d + sum(srcs) over F2.  The scatter
snapshots the retained helpers `ret` and adds the listed snapshots to targets.
Frames are spans over Q of their listed E8 lines (ham coordinates, form dot/2).
"""
import gzip
import json
import math
from collections import Counter
from fractions import Fraction


class Reject(Exception):
    pass


def need(ok, msg):
    if not ok:
        raise Reject(msg)


def load(path):
    with open(path, 'rb') as fh:
        return json.loads(gzip.decompress(fh.read()))


def canonical(word):
    return json.dumps(word, sort_keys=True, separators=(',', ':')).encode()


def perp_basis(vectors, dim=8):
    """Integer basis of {u : u.x = 0 for all x in vectors} (Euclidean dot)."""
    rows = [[Fraction(a) for a in x] for x in vectors]
    piv, r = [], 0
    for col in range(dim):
        p = next((i for i in range(r, len(rows)) if rows[i][col]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        inv = 1 / rows[r][col]
        rows[r] = [a * inv for a in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][col]:
                f = rows[i][col]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        piv.append(col)
        r += 1
    out = []
    for free in (c for c in range(dim) if c not in piv):
        vec = [Fraction(0)] * dim
        vec[free] = Fraction(1)
        for row, pc in zip(rows[:r], piv):
            vec[pc] = -row[free]
        den = 1
        for a in vec:
            den = den * a.denominator // math.gcd(den, a.denominator)
        out.append([int(a * den) for a in vec])
    return r, out


class Geometry:
    """Rational frame dimensions, nesting and closure computed from the lines."""

    def __init__(self, word):
        self.lines = [list(map(int, x)) for x in word['lines']]
        self.frames = [list(f) for f in word['frames']]
        self.dim, self.perp = [], []
        for f in self.frames:
            d, pb = perp_basis([self.lines[i] for i in f])
            self.dim.append(d)
            self.perp.append(pb)
        self._nest = {}

    def inside(self, line, k):
        x = self.lines[line]
        return all(sum(a * b for a, b in zip(x, u)) == 0 for u in self.perp[k])

    def nested(self, a, b):
        key = (a, b)
        if key not in self._nest:
            self._nest[key] = all(self.inside(i, b) for i in self.frames[a])
        return self._nest[key]

    def closure_checks(self):
        v = len(self.lines)
        n = 0
        for k, f in enumerate(self.frames):
            inside = [i for i in range(v) if self.inside(i, k)]
            need(inside == sorted(f), 'frame %d is not closed in the live lines' % k)
            n += v
        return n


def bits(mask):
    while mask:
        b = mask & -mask
        yield b.bit_length() - 1
        mask ^= b


def forward(word, geo, sections=('D', 'A', 'scatter', 'B', 'C'), frames_on=True, trace=None):
    """Forward symbolic replay over F2.  Register r starts as the column bitset 1 << r, so one
    pass covers every input column, including arbitrary (dirty) helper contents.  Returns final
    values, final frames, every frame climb (register, old, new, position) and the COPY frames.
    trace(event, values, frames) is called after every gate when given."""
    v, R = word['v'], word['R']
    n = 2 * v + R
    need(len(word['start']) == n and len(word['final']) == n, 'start/final length')
    cur = list(word['start'])
    val = [1 << r for r in range(n)]
    climbs = []          # (register, old frame, new frame, position)
    copies = []
    pos = 0
    if frames_on:
        for s in range(v):
            need(geo.frames[cur[s]] == [s] and geo.dim[cur[s]] == 1, 'source %d does not start at its line' % s)
        for r in range(v, n):
            need(geo.dim[cur[r]] == 0, 'register %d does not start at the zero frame' % r)

    def move(r, f, where):
        if cur[r] == f:
            return
        need(geo.nested(cur[r], f) and geo.dim[cur[r]] < geo.dim[f],
             'illegal climb of register %d from frame %d to %d at %s' % (r, cur[r], f, where))
        climbs.append((r, cur[r], f, where))
        cur[r] = f

    for sec in sections:
        if sec == 'scatter':
            need(len(word['scatter']) == v, 'scatter rows')
            if frames_on:
                need(all(geo.dim[cur[v + t]] == 0 for t in range(v)), 'a target left the zero frame before the scatter')
            snap = [val[q] for q in word['ret']]
            for k, q in enumerate(word['ret']):
                need(2 * v <= q < n, 'retained register is not a helper')
                copies.append((q, cur[q], geo.dim[cur[q]]))
            for t, row in enumerate(word['scatter']):
                for k in row:
                    val[v + t] ^= snap[k]
            if trace:
                trace(('scatter', None, None, None), val, cur)
            continue
        for i, g in enumerate(word[sec]):
            need(len(g) == 3, 'malformed gate')
            f, d, srcs = g
            regs = [d] + list(srcs)
            need(srcs and len(set(regs)) == len(regs) and all(0 <= r < n for r in regs), 'bad operands %s[%d]' % (sec, i))
            need(0 <= f < len(word['frames']), 'frame id')
            if frames_on:
                for r in regs:
                    move(r, f, (sec, i))
            acc = 0
            for s in srcs:
                acc ^= val[s]
            val[d] ^= acc
            if trace:
                trace((sec, i, f, d, tuple(srcs)), val, cur)
    if frames_on:
        for r in range(n):
            move(r, word['final'][r], ('final', r))
    return val, cur, climbs, copies


def check_identity(word, val):
    v, R = word['v'], word['R']
    n = 2 * v + R
    bad = [r for r in range(n) if val[r] != ((1 << r) | ((1 << (r - v)) if v <= r < 2 * v else 0))]
    return bad


def check_final_frames(word, geo):
    v, R = word['v'], word['R']
    n = 2 * v + R
    full = [k for k, d in enumerate(geo.dim) if d == 8]
    need(len(full) == 1, 'exactly one full frame')
    for r in list(range(v)) + list(range(2 * v, n)):
        need(geo.dim[word['final'][r]] == 8, 'final frame of %d is not full' % r)
    for t in range(v):
        lt = geo.lines[t]
        perp = [i for i in range(v) if sum(a * b for a, b in zip(geo.lines[i], lt)) == 0]
        need(geo.frames[word['final'][v + t]] == perp, 'target %d final frame is not t-perp' % t)
    return full[0]


def pullback(word, sections=('D', 'A', 'scatter', 'B', 'C')):
    """Second method: transpose action in reverse order.  col[j] = set of outputs
    depending on input j (bitset over registers)."""
    v, R = word['v'], word['R']
    n = 2 * v + R
    col = [1 << r for r in range(n)]
    for sec in reversed(sections):
        if sec == 'scatter':
            for t, row in enumerate(word['scatter']):
                for k in row:
                    q = word['ret'][k]
                    col[q] ^= col[v + t]
            continue
        for f, d, srcs in reversed(word[sec]):
            cd = col[d]
            for s in srcs:
                col[s] ^= cd
    return col


def check_pullback(word, col):
    v, R = word['v'], word['R']
    n = 2 * v + R
    return [j for j in range(n) if col[j] != ((1 << j) | ((1 << (v + j)) if j < v else 0))]


def reverse_orientation(word, geo):
    """Literal reverse orientation: gates in reverse order, starting at the final frames;
    every move is a nested strict descent (a climb of the orthogonal complement)."""
    v, R = word['v'], word['R']
    n = 2 * v + R
    cur = list(word['final'])
    val = [1 << r for r in range(n)]

    def move(r, f, where):
        if cur[r] == f:
            return
        need(geo.nested(f, cur[r]) and geo.dim[f] < geo.dim[cur[r]],
             'illegal reverse move of %d from %d to %d at %s' % (r, cur[r], f, where))
        cur[r] = f

    for sec in ('C', 'B', 'scatter', 'A', 'D'):
        if sec == 'scatter':
            # mirror of the forward scatter: targets descend to the zero frame, each retained
            # helper to the frame of its last A gate (where the forward COPY reads it)
            zero = [k for k, d in enumerate(geo.dim) if d == 0][0]
            for t in range(v):
                move(v + t, zero, ('scatter', t))
            for q in word['ret']:
                last = [g[0] for g in word['A'] if q == g[1] or q in g[2]]
                need(last, 'retained helper %d is never written in A' % q)
                move(q, last[-1], ('scatter', q))
            snap = [val[q] for q in word['ret']]
            for t, row in enumerate(word['scatter']):
                for k in row:
                    val[v + t] ^= snap[k]
            continue
        for i in range(len(word[sec]) - 1, -1, -1):
            f, d, srcs = word[sec][i]
            for r in [d] + list(srcs):
                move(r, f, (sec, i))
            acc = 0
            for s in srcs:
                acc ^= val[s]
            val[d] ^= acc
    for r in range(n):
        move(r, word['start'][r], ('start', r))
    return val


def profile(geo, climbs, copies):
    h = Counter()
    for r, a, b, _ in climbs:
        h[geo.dim[b] - geo.dim[a]] += 1
    for q, f, d in copies:
        h[d] += 1
    return dict(sorted(h.items()))


def paths(word, climbs):
    n = 2 * word['v'] + word['R']
    p = {r: [word['start'][r]] for r in range(n)}
    for r, a, b, where in climbs:
        p[r].append(b)
    return p


def rebuild_DC(word):
    """D0 from the raw word's helper part of each target; C as the literal reverse of the
    source/helper-destination A/B gates at the full frame (pwordl.build convention)."""
    v, R = word['v'], word['R']
    n = 2 * v + R
    val = [1 << r for r in range(n)]
    for sec in ('A', 'scatter', 'B'):
        if sec == 'scatter':
            snap = [val[q] for q in word['ret']]
            for t, row in enumerate(word['scatter']):
                for k in row:
                    val[v + t] ^= snap[k]
            continue
        for f, d, srcs in word[sec]:
            acc = 0
            for s in srcs:
                acc ^= val[s]
            val[d] ^= acc
    hmask = ((1 << R) - 1) << (2 * v)
    zero = [k for k, f in enumerate(word['frames']) if not f]
    full = [k for k, f in enumerate(word['frames']) if len(f) == v]
    need(len(zero) == 1 and len(full) == 1, 'zero/full frame ids')
    D = []
    for t in range(v):
        m = val[v + t] & hmask
        if m:
            D.append([zero[0], v + t, list(bits(m))])
    # literal reverse of A then B, restricted to source/helper destinations
    C = [[full[0], d, list(s)] for f, d, s in reversed(word['A'] + word['B']) if not (v <= d < 2 * v)]
    return D, C
