"""Independent exact semantics and binary-frame bill for the BORROW-WORD format.

Standard library only. Nothing is imported from the audited authors' code
(PR3133/PR3605 producers, cleanup generator, evaluator or frame solver); the word
format and its semantic contract were read from those pinned sources and are
credited there.  The frame-bill and free-word structure (point-set spans, warp
frame and lifted-frame checks, target levels keyed by register, dual symbol
naming) re-implements, without importing, Arham Tahir's
research/coupled-carrier-independent-audit/verify.py (Apache-2.0) and shares its
reading of the contract, so this module is not independent of that audit.

Sagar Thakrar (thakrarsagar), with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as Q

V, N, H = 112, 704, 9          # sources 0..111, targets 112..223, helpers 224..703
DUAL = 10 ** 6                  # offset naming the independent dual symbols D_k = K_k^(-T)


class AuditFailure(Exception):
    """Explicit failure; never disabled by python -O."""


def need(ok, *why):
    if not ok:
        raise AuditFailure(' '.join(map(str, why)))


def is_target(r):
    return V <= r < 2 * V


def touched(g):
    return g[1:3] if g[0] == 'add' else g[1:2]


# ----------------------------------------------------------------------------
# Binary frames: a subspace of F_2^9 is stored as a 512-bit point-set mask
# (bit x set iff x lies in the subspace).  Containment is mask inclusion.
# ----------------------------------------------------------------------------
_SPAN = {}


def span(vectors):
    key = tuple(vectors)
    mask = _SPAN.get(key)
    if mask is None:
        points = {0}
        for u in key:
            need(type(u) is int and 0 <= u < 512, 'frame vector out of range', u)
            if u not in points:
                points |= {p ^ u for p in points}
        mask = sum(1 << p for p in points)
        _SPAN[key] = mask
    return mask


def points(mask):
    return [x for x in range(512) if mask >> x & 1]


def dim(mask):
    size = bin(mask).count('1')
    need(size and size & (size - 1) == 0, 'not a subspace point set')
    return size.bit_length() - 1


FULL = (1 << 512) - 1
ZERO = 1


def hyperplane(port):
    return sum(1 << x for x in range(512) if bin(x & port).count('1') % 2 == 0)


def warp_images(columns):
    """Images of all 512 vectors under the F_2-linear map with columns G e_i."""
    need(len(columns) == H and all(type(c) is int and 0 <= c < 512 for c in columns), 'warp columns')
    images = [0] * 512
    for x in range(1, 512):
        low = x & -x
        images[x] = images[x ^ low] ^ columns[low.bit_length() - 1]
    need(len(set(images)) == 512, 'singular warp')
    return images


def image_mask(images, mask):
    return sum(1 << images[x] for x in points(mask))


def lagrangian_action_ok(images, U, E):
    """K_G(x,z)=(Gx, Gx+G^{-T}(x+z)) is symplectic and maps L_U to L_E, L_0 and L_FULL to themselves.

    L_U={(x,x+p): x in U, p in U^perp}.  This is the binary frame action only; it
    is not a Clifford phase or Gaussian-product certificate.  For invertible G with
    G(U)=E it is implied by the frame-map check (<G^-T p, Gu> = <p, u>), so it is a
    consistency check of the implementation, not extra evidence.
    """
    inverse = [0] * 512
    for x, y in enumerate(images):
        inverse[y] = x
    # G^{-T} z: bit j of the result is <G^{-1} e_j, z>.
    git = lambda z: sum((bin(inverse[1 << j] & z).count('1') & 1) << j for j in range(H))
    lift = lambda x, z: (images[x], images[x] ^ git(x ^ z))
    pair = lambda a, b: (bin(a[0] & b[1]).count('1') + bin(a[1] & b[0]).count('1')) & 1
    basis = [(1 << i, 0) for i in range(H)] + [(0, 1 << i) for i in range(H)]
    lifted = [lift(*b) for b in basis]
    if any(pair(lifted[i], lifted[j]) != pair(basis[i], basis[j]) for i in range(18) for j in range(i + 1, 18)):
        return False

    def frame(mask):
        us = points(mask)
        perp = [p for p in range(512) if all(bin(p & u).count('1') % 2 == 0 for u in us)]
        return {(u, u ^ p) for u in us for p in perp}
    return all({lift(*pt) for pt in frame(a)} == frame(b) for a, b in ((ZERO, ZERO), (FULL, FULL), (U, E)))


# ----------------------------------------------------------------------------
# Chronological binary-frame bill (BORROW-WORD contract)
# ----------------------------------------------------------------------------
def frame_bill(w, lagrangian=False):
    rep = w['report']
    need((rep['v'], 2 * rep['v'] + rep['R'], rep['h']) == (V, N, H), 'word geometry')
    removed = set(w['removed'])
    need(len(removed) == len(w['removed']) and all(2 * V <= r < N for r in removed), 'removed helpers')
    live = [r for r in range(N) if r not in removed]
    liveset = set(live)
    B, warps = w['B'], w['warps']
    for k, (pos, lender, cols, U, E) in enumerate(warps, 1):
        need(0 <= pos <= len(B), 'warp position', k)
        need(lender in liveset and not is_target(lender), 'warp lender', k)
        images = warp_images(cols)
        su, se = span(U), span(E)
        need(dim(su) == len(U) == len(E) == dim(se), 'warp frame bases', k)
        need(image_mask(images, su) == se, 'warp does not map its frame', k)
        if lagrangian:
            need(lagrangian_action_ok(images, su, se), 'lifted frame action', k)
    for name in ('A', 'B', 'restore'):
        for g in w[name]:
            if g[0] != 'warp':
                need(all(r in liveset for r in touched(g)), 'removed/out-of-range register', name, g)
                if g[0] == 'add' and not is_target(g[1]):
                    need(not is_target(g[2]), 'non-target reads a target', name, g)
    need(all(g[-1] is None and is_target(g[1]) and g[0] == 'add' for g in w['cut']), 'cut gates')
    need(all(g[-1] == [] and is_target(g[1]) for g in w['precondition'] + w['compensation']), 'zero-frame wrapper writes')
    need(all(not is_target(g[1]) for g in w['restore']), 'restore writes a target')

    ports = w['ports']
    start, end = {}, {}
    for r in live:
        if r < V:
            start[r], end[r] = span((ports[r],)), FULL
        elif r < 2 * V:
            start[r], end[r] = ZERO, hyperplane(ports[r - V])
        else:
            start[r], end[r] = ZERO, FULL
    for q, U in w['start_extra'].items():
        need(int(q) in liveset and int(q) >= 2 * V, 'entrance names a live helper', q)
        start[int(q)] = span(U)
    for q, U in w['helper_final'].items():
        need(int(q) in liveset and int(q) >= 2 * V, 'terminal names a live helper', q)
        end[int(q)] = span(U)

    current, bill, chain = dict(start), Counter(), {}

    def climb(r, mask, where):
        need(current[r] & ~mask == 0, 'frame containment fails', where, r)
        d = dim(mask) - dim(current[r])
        if d:
            bill[d] += 1
        chain.setdefault(r, []).append((where, d, mask))
        current[r] = mask

    npre = w['prelude_events']
    for i, g in enumerate(w['A']):
        if g[0] == 'warp':
            need(i < npre and len(g) == 5, 'warp outside the prelude', i)
            _, r, op, fr, to = g
            need(op != 0 and abs(op) <= len(warps) and warps[abs(op) - 1][1] == r, 'prelude warp lender', i)
            images = warp_images(warps[abs(op) - 1][2])
            if op < 0:
                inverse = [0] * 512
                for x, y in enumerate(images):
                    inverse[y] = x
                images = inverse
            need(image_mask(images, span(fr)) == span(to), 'prelude warp frame action', i)
            need(current[r] == span(fr), 'prelude warp entry frame', i, r)
            current[r] = span(to)
            chain.setdefault(r, []).append((('A', i), 'warp', span(to)))
        else:
            if i < npre:
                need(is_target(g[1]), 'prelude scalar writes a non-target', i)
            for r in touched(g):
                climb(r, span(g[-1]), ('A', i))
    levels = {V + int(t): span(U) for t, U in w['target_levels'].items()}
    need(all(current[t] == levels.get(t, ZERO) for t in range(V, 2 * V)), 'target cut levels')
    for q, U in zip(w['centers'], w['center_frames']):
        U = span(U)
        need(current[q] == U, 'centre entry frame', q)
        served = {levels.get(g[1], ZERO) for g in w['cut'] if g[2] == q}
        for T in sorted(served, key=lambda m: -dim(m)):
            need(T & ~U == 0, 'centre descent not nested', q)
            d = dim(U) - dim(T)
            if d:
                bill[d] += 1
                chain.setdefault(q, []).append((('centre',), d, T))
            U = T
    at = {}
    for k, rec in enumerate(warps, 1):
        at.setdefault(rec[0], []).append(k)
    for p in range(len(B) + 1):
        for k in at.get(p, ()):
            _, lender, _, U, E = warps[k - 1]
            need(current[lender] == span(U), 'native warp entry frame', k, lender)
            current[lender] = span(E)
            chain.setdefault(lender, []).append((('warp', k), 'warp', span(E)))
        if p < len(B):
            for r in touched(B[p]):
                climb(r, span(B[p][-1]), ('B', p))
    for i, g in enumerate(w['restore']):
        for r in touched(g):
            climb(r, span(g[-1]), ('restore', i))
    for r in live:
        climb(r, end[r], ('end',))
    restored = set(map(int, w['helper_final']))
    need(all(end[r] == FULL for r in live if r not in restored and not is_target(r)), 'a FULL-cleanup register ends low')
    widths = Counter(dim(end[r]) - dim(start[r]) for r in live if r >= 2 * V)
    return dict(sorted(bill.items())), dict(sorted(widths.items())), chain, start, end


def hygiene(w):
    """Inherited structural contract: dyadic scalars, power-of-two scales, wrapper and correction access."""
    entering = set(map(int, w['start_extra']))
    restored = set(map(int, w['helper_final']))
    live = set(range(N)) - set(w['removed'])
    for name in ('precondition', 'compensation', 'A', 'cut', 'B', 'restore', 'cleanup'):
        for g in w[name]:
            if g[0] == 'warp':
                continue
            q = Q(g[3], g[4]) if g[0] == 'add' else Q(g[2], g[3])
            need(q != 0 and q.denominator & (q.denominator - 1) == 0, 'non-dyadic scalar', name, g)
            if g[0] == 'scale':
                need(abs(q.numerator) & (abs(q.numerator) - 1) == 0, 'non power-of-two scale', name, g)
    for g in w['precondition'] + w['compensation']:
        need(not any(r in entering | restored for r in touched(g)), 'wrapper touches an entering or restored helper', g)
    for c in w['initial_corrections']:
        word = c['operator_word']
        need(is_target(c['target']) and c['source'] in live and c['source'] >= 2 * V
             and c['source'] not in entering, 'correction access', c)
        need(word and all(w['warps'][abs(o) - 1][1] == c['source'] for o in word), 'correction operator lender', c)
        q = Q(c['coefficient'])
        need(q != 0 and q.denominator & (q.denominator - 1) == 0, 'correction coefficient', c)
    return True


# ----------------------------------------------------------------------------
# Literal inverse cleanup, derived from the contract
# ----------------------------------------------------------------------------
def ordinary_forward(w):
    """Chronological non-wrapper actions whose inverse forms cleanup."""
    out = [g for g in w['A'][w['prelude_events']:]]
    at = {}
    for k, rec in enumerate(w['warps'], 1):
        at.setdefault(rec[0], []).append(['warp', rec[1], k])
    for p in range(len(w['B']) + 1):
        out += at.get(p, [])
        if p < len(w['B']):
            out.append(w['B'][p])
    return out + list(w['restore'])


def derive_cleanup(w):
    restored = set(map(int, w['helper_final']))
    buf = lambda r: r + N if r in restored else r
    full = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    out = []
    for g in reversed(ordinary_forward(w)):
        if g[0] == 'warp':
            out.append(['warp', buf(g[1]), -g[2], full])
        elif is_target(g[1]):
            continue
        elif g[0] == 'add':
            out.append(['add', buf(g[1]), buf(g[2]), -g[3], g[4], full])
        else:
            need(g[0] == 'scale', 'unknown primitive', g)
            out.append(['scale', buf(g[1]), g[3], g[2], full])
    return out


def same_cleanup(a, b):
    norm = lambda c: [(g[:-1], span(g[-1])) for g in c]
    return len(a) == len(b) and norm(a) == norm(b)


# ----------------------------------------------------------------------------
# Exact free-operator semantics.  A value is a dict {(input, word): Fraction};
# word is a reduced tuple of signed operator ids (leftmost = applied last).
# ----------------------------------------------------------------------------
def program(w, cleanup=None):
    """Literal executed sequence: corrections, wrapper, A, cut, B+warps, restore | cleanup."""
    items = [('corr', c['target'], c['source'], tuple(c['operator_word']), Q(c['coefficient']))
             for c in w['initial_corrections']]
    items += w['precondition'] + w['compensation'] + w['A'] + w['cut']
    at = {}
    for k, rec in enumerate(w['warps'], 1):
        at.setdefault(rec[0], []).append(['warp', rec[1], k])
    for p in range(len(w['B']) + 1):
        items += at.get(p, [])
        if p < len(w['B']):
            items.append(w['B'][p])
    items += w['restore']
    return items, list(w['cleanup'] if cleanup is None else cleanup)


def dual_op(op):
    return (1 if op > 0 else -1) * (abs(op) + DUAL)


def _left(op, word):
    return word[1:] if word and word[0] == -op else (op,) + word


def _right(word, op):
    return word[:-1] if word and word[-1] == -op else word + (op,)


def _axpy(dst, src, q):
    for key, x in src.items():
        y = dst.get(key, 0) + q * x
        if y:
            dst[key] = y
        else:
            dst.pop(key, None)


def forward_rows(w, cleanup=None, dual=False, symbolic_buffers=True, snapshot=None):
    """Schrodinger pass: every register's value as a combination of initial inputs.

    Live inputs are independent symbols.  Private buffers are independent symbols
    when symbolic_buffers is set (dirty), otherwise zero.  The optional snapshot
    callback sees the rows at the cleanup boundary.
    """
    removed = set(w['removed'])
    live = [r for r in range(N) if r not in removed]
    restored = sorted(map(int, w['helper_final']))
    rows = {r: {(r, ()): Q(1)} for r in live}
    for c in restored:
        rows[c + N] = {(c + N, ()): Q(1)} if symbolic_buffers else {}
    prefix, tail = program(w, cleanup)

    def apply(g):
        kind = g[0]
        if kind == 'add':
            t, s, q = g[1], g[2], Q(g[3], g[4])
            need(t != s and q, 'add gate', g)
            if dual:
                t, s, q = s, t, -q
            _axpy(rows[t], rows[s], q)
        elif kind == 'scale':
            q = Q(g[2], g[3])
            need(q != 0, 'zero scale', g)
            if dual:
                q = 1 / q
            rows[g[1]] = {k: q * x for k, x in rows[g[1]].items()}
        elif kind == 'warp':
            op = dual_op(g[2]) if dual else g[2]
            rows[g[1]] = {(var, _left(op, word)): x for (var, word), x in rows[g[1]].items()}
        elif kind == 'corr':
            _, t, s, word, c = g
            if dual:
                src, ops, dst, c = rows[t], [-dual_op(o) for o in word], s, -c
            else:
                src, ops, dst = rows[s], list(reversed(word)), t
            moved = {}
            for (var, wd), x in src.items():
                for o in ops:
                    wd = _left(o, wd)
                moved[var, wd] = x
            _axpy(rows[dst], moved, c)
        else:
            raise AuditFailure('unknown primitive ' + repr(g))

    for g in prefix:
        apply(g)
    if snapshot is not None:
        snapshot(rows)
    for g in tail:
        apply(g)
    return rows


def reverse_columns(w, cleanup=None, upto_cleanup=False):
    """Heisenberg pull-back: process the forward program backwards.

    cols[s] = {(output, word): coefficient}: the final output register 'output'
    contains coefficient*word*x_s.  Words grow on the right.  Every live input and
    every private buffer is an independent symbol.
    """
    removed = set(w['removed'])
    live = [r for r in range(N) if r not in removed]
    restored = sorted(map(int, w['helper_final']))
    regs = live + [c + N for c in restored]
    cols = {r: {(r, ()): Q(1)} for r in regs}
    prefix, tail = program(w, cleanup)
    seq = prefix if upto_cleanup else prefix + tail
    for g in reversed(seq):
        kind = g[0]
        if kind == 'add':
            t, s, q = g[1], g[2], Q(g[3], g[4])
            need(t != s and q, 'add gate', g)
            _axpy(cols[s], cols[t], q)
        elif kind == 'scale':
            q = Q(g[2], g[3])
            need(q != 0, 'zero scale', g)
            cols[g[1]] = {k: q * x for k, x in cols[g[1]].items()}
        elif kind == 'warp':
            op = g[2]
            cols[g[1]] = {(out, _right(word, op)): x for (out, word), x in cols[g[1]].items()}
        elif kind == 'corr':
            _, t, s, word, c = g
            moved = {}
            for (out, wd), x in cols[t].items():
                for o in word:
                    wd = _right(wd, o)
                moved[out, wd] = x
            _axpy(cols[s], moved, c)
        else:
            raise AuditFailure('unknown primitive ' + repr(g))
    return cols


def transpose(cols):
    rows = {}
    for s, col in cols.items():
        for (r, word), x in col.items():
            rows.setdefault(r, {})[s, word] = x
    return rows


def endpoint_defects(w, rows, dual=False):
    """Compare final rows with the contract on the zero-buffer (live-input) domain.

    Returns (bad live registers, dirty buffers, buffer->live leaks, buffer self-map identity).
    """
    removed = set(w['removed'])
    live = [r for r in range(N) if r not in removed]
    restored = sorted(map(int, w['helper_final']))
    bad = []
    for r in live:
        expect = {(r, ()): Q(1)}
        if dual and r < V:
            expect[r + V, ()] = Q(-1)
        if not dual and is_target(r):
            expect[r - V, ()] = Q(1)
        got = {k: x for k, x in rows.get(r, {}).items() if k[0] < N}
        if got != expect:
            bad.append(r)
    dirty = [c for c in restored if any(k[0] < N for k in rows.get(c + N, {}))]
    leaks = sorted({r for r in live for k in rows.get(r, {}) if k[0] >= N})
    buffer_identity = all({k: x for k, x in rows.get(c + N, {}).items() if k[0] >= N} == {(c + N, ()): Q(1)}
                          for c in restored)
    return bad, dirty, leaks, buffer_identity


def boundary_defects(w, rows):
    """Contract at the cleanup boundary (forward): targets sheared, restored helpers clean and isolated."""
    restored = set(map(int, w['helper_final']))
    out = []
    for t in range(V, 2 * V):
        if {k: x for k, x in rows[t].items() if k[0] < N} != {(t, ()): Q(1), (t - V, ()): Q(1)}:
            out.append(('target', t))
    for c in restored:
        if rows[c] != {(c, ()): Q(1)}:
            out.append(('restored', c))
    for r, row in rows.items():
        if r < N and r not in restored and any(k[0] in restored for k in row):
            out.append(('restored input read', r))
    return out
