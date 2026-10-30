"""Bridge-schedule model for the nine-stage complex template (standard library only).

Exact rule (copied from the eight-wire check in
research/e8-complex-gauge-kernel/code/replay_gk.py, global_check):
  local forward  : row Y_p += row X_p
  local reverse  : row X_p -= row Y_p
  bridge(i<-j,q) : row X_i += q row X_j ; row Y_j -= q row Y_i
  terminal       : (X_p, Y_p) -> (Y_p, -X_p) for every pair
and the final 8x8 matrix must be the identity.

Level model (data_phases.py, global_nine.py): stage s takes its owner pair from level s-1 to s.
A bridge needs both pairs at the same level (an add needs equal labels). Idle children advance an
untouched pair between touches; consecutive idle advances of one pair between two touches form one
idle child, of rank 8 per level (the first level -1 -> 0 also has rank 8 on each side).

Design class ("simple riding"): every pair receives three alternating shears (U L U or L U L). Each of
the nine stages has one owner pair; a pair may additionally ride a stage of another pair through a
bridge pair (+1 before, -1 after the stage). On a forward stage the bridge is (owner <- rider),
on a reverse stage (rider <- owner); only these orientations give the rider the owner's shear.
"""
from fractions import Fraction as Fr
import itertools

IDENTITY = [[int(i == j) for j in range(8)] for i in range(8)]
TERMINAL = {'kind': 'terminal', 'pairs': 4}


def apply(recipe):
    m = [r[:] for r in IDENTITY]
    for e in recipe:
        if e['kind'] == 'local':
            a = 2 * e['pair']; b = a + 1
            dst, src, q = (a, b, -1) if e['reverse'] else (b, a, 1)
            m[dst] = [x + q * y for x, y in zip(m[dst], m[src])]
        elif e['kind'] == 'bridge':
            i, j, q = e['dst'], e['src'], e['coefficient']
            m[2 * i] = [x + q * y for x, y in zip(m[2 * i], m[2 * j])]
            m[2 * j + 1] = [x - q * y for x, y in zip(m[2 * j + 1], m[2 * i + 1])]
        elif e['kind'] == 'terminal':
            old = [r[:] for r in m]
            for i in range(4):
                m[2 * i] = old[2 * i + 1]; m[2 * i + 1] = [-x for x in old[2 * i]]
        else:
            raise ValueError(e)
    return m


def idle_segments(recipe):
    """Idle children per side implied by the touch levels of a recipe (lazy advances)."""
    lvl = {p: -1 for p in range(4)}; pend = {p: 0 for p in range(4)}; seg = []

    def go(p, to):
        if to < lvl[p]:
            raise ValueError(f'pair {p} is past level {to}')
        pend[p] += 8 * (to - lvl[p]); lvl[p] = to

    def touch(p):
        if pend[p]:
            seg.append(pend[p]); pend[p] = 0

    for e in recipe:
        if e['kind'] == 'local':
            p, s = e['pair'], e['stage']
            go(p, s - 1); touch(p); lvl[p] = s
        elif e['kind'] == 'bridge':
            i, j = e['dst'], e['src']; L = max(lvl[i], lvl[j])
            go(i, L); go(j, L); touch(i); touch(j)
    for p in range(4):
        go(p, 8); touch(p)
    return tuple(sorted(seg))


def design_segments(stages_of, owned):
    seg = []
    for p in range(4):
        lvl = -1
        for s in stages_of[p]:
            if s - 1 > lvl:
                seg.append(8 * (s - 1 - lvl))
            if (s, p) not in owned:
                seg.append(8)          # rider: idle s-1 -> s between its two bridges
            lvl = s
        if lvl < 8:
            seg.append(8 * (8 - lvl))
    return tuple(sorted(x for x in seg if x))


def build(design):
    owners, dirs = design['owners'], design['dirs']
    riders = {s: [] for s in range(9)}
    for p, ss in enumerate(design['riders']):
        for s in ss:
            riders[s].append(p)
    rec = []
    for s in range(9):
        o = owners[s]; rev = bool(dirs[s])

        def br(r, q):
            return ({'kind': 'bridge', 'dst': r, 'src': o, 'coefficient': q} if rev
                    else {'kind': 'bridge', 'dst': o, 'src': r, 'coefficient': q})
        for r in riders[s]:
            rec.append(br(r, 1))
        rec.append({'kind': 'local', 'stage': s, 'pair': o, 'reverse': rev})
        for r in reversed(riders[s]):
            rec.append(br(r, -1))
    return rec


def designs(dir_filter=None):
    """All simple-riding designs, pairs labelled by first appearance; yields (segments, design)."""
    for owners in itertools.product(range(4), repeat=9):
        seen = []
        for o in owners:
            if o not in seen:
                seen.append(o)
        if seen != [0, 1, 2, 3]:
            continue
        own = [owners.count(p) for p in range(4)]
        if max(own) > 3:
            continue
        need = [3 - c for c in own]
        for dirs in (dir_filter or itertools.product((0, 1), repeat=9)):
            bad = False
            for p in range(4):
                ds = [dirs[s] for s in range(9) if owners[s] == p]
                if need[p] == 0 and any(ds[i] == ds[i + 1] for i in range(len(ds) - 1)):
                    bad = True; break
            if bad:
                continue
            choices = [list(itertools.combinations([s for s in range(9) if owners[s] != p], need[p]))
                       for p in range(4)]
            for pick in itertools.product(*choices):
                stages_of = []; good = True
                for p in range(4):
                    st = sorted([s for s in range(9) if owners[s] == p] + list(pick[p]))
                    ds = [dirs[s] for s in st]
                    if ds not in ([0, 1, 0], [1, 0, 1]):
                        good = False; break
                    stages_of.append(st)
                if not good:
                    continue
                seg = design_segments(stages_of, {(s, owners[s]) for s in range(9)})
                if max(seg) > 51:          # halving guard 2 r^2 < 73^2
                    continue
                yield seg, dict(owners=tuple(owners), dirs=tuple(dirs),
                                riders=[list(x) for x in pick], stages_of=stages_of)


def _pair_part(st, p, owners):
    seg = []; lvl = -1
    for s in st:
        if s - 1 > lvl:
            seg.append(8 * (s - 1 - lvl))
        if owners[s] != p:
            seg.append(8)
        lvl = s
    if lvl < 8:
        seg.append(8 * (8 - lvl))
    return tuple(x for x in seg if x)


def census(keep):
    """Fast equivalent of iterating designs(): idle segments are a union of independent per-pair parts.
    keep(segments, dirs) returns a truthy tag to keep a design (stored as design['tag']).
    Returns (number of designs, set of alphabets, kept list of (segments, design))."""
    total = 0; alphabets = set(); kept = []
    for owners in itertools.product(range(4), repeat=9):
        seen = []
        for o in owners:
            if o not in seen:
                seen.append(o)
        if seen != [0, 1, 2, 3]:
            continue
        own = [owners.count(p) for p in range(4)]
        if max(own) > 3:
            continue
        need = [3 - c for c in own]
        cand = []
        for p in range(4):
            mine = [s for s in range(9) if owners[s] == p]
            cand.append([(pick, sorted(mine + list(pick)))
                         for pick in itertools.combinations([s for s in range(9) if owners[s] != p], need[p])])
        for dirs in itertools.product((0, 1), repeat=9):
            opts = []
            for p in range(4):
                o = [(pick, st, _pair_part(st, p, owners)) for pick, st in cand[p]
                     if [dirs[s] for s in st] in ([0, 1, 0], [1, 0, 1])]
                o = [x for x in o if max(x[2]) <= 51]
                if not o:
                    break
                opts.append(o)
            else:
                for combo in itertools.product(*opts):
                    seg = tuple(sorted(x for c in combo for x in c[2]))
                    total += 1; alphabets.add(seg)
                    tag = keep(seg, dirs)
                    if tag:
                        kept.append((seg, dict(tag=tag, owners=tuple(owners), dirs=tuple(dirs),
                                               riders=[list(c[0]) for c in combo],
                                               stages_of=[c[1] for c in combo])))
    return total, alphabets, kept


# ---------- exact closure: can final bridges (at level 8, no idle cost) finish the recipe? ----------

def _inv(M):
    n = len(M)
    A = [[Fr(x) for x in r] + [Fr(int(i == j)) for j in range(n)] for i, r in enumerate(M)]
    for c in range(n):
        p = next(r for r in range(c, n) if A[r][c] != 0); A[c], A[p] = A[p], A[c]
        piv = A[c][c]; A[c] = [x / piv for x in A[c]]
        for r in range(n):
            if r != c and A[r][c] != 0:
                f = A[r][c]; A[r] = [x - f * y for x, y in zip(A[r], A[c])]
    return [r[n:] for r in A]


def _mul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def _det(M):
    M = [[Fr(x) for x in r] for r in M]; n = len(M); d = Fr(1)
    for c in range(n):
        p = next((r for r in range(c, n) if M[r][c] != 0), None)
        if p is None:
            return Fr(0)
        if p != c:
            M[c], M[p] = M[p], M[c]; d = -d
        d *= M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / M[c][c]; M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return d


_TINV = _inv(apply([TERMINAL]))


def _reduce(A):
    """Integer row operations r_i += q r_j taking A (det 1) to I; returns the operations in order."""
    n = len(A); A = [r[:] for r in A]; ops = []

    def op(i, j, q):
        if q:
            A[i] = [x + q * y for x, y in zip(A[i], A[j])]; ops.append((i, j, q))
    for c in range(n):
        while True:
            nz = [r for r in range(c, n) if A[r][c] != 0]
            if len(nz) <= 1:
                break
            p = min(nz, key=lambda r: abs(A[r][c]))
            for r in nz:
                if r != p:
                    op(r, p, -(A[r][c] // A[p][c]))
        p = next(r for r in range(c, n) if A[r][c] != 0)
        if p != c:
            op(c, p, 1); op(p, c, -1)
        if A[c][c] == -1:
            k = c + 1 if c + 1 < n else c - 1
            for _ in range(2):
                if A[c][c] == -1:
                    op(k, c, 1); op(c, k, -1); op(k, c, 1)
        for r in range(n):
            if r != c and A[r][c] != 0:
                op(r, c, -A[r][c] * A[c][c])
    return ops if A == [[int(i == j) for j in range(n)] for i in range(n)] else None


def closure(rec):
    """Bridges generate exactly {diag(A, A^-T): A in SL(4,Z)} on (X rows, Y rows). Return explicit final
    bridges completing rec (re-checked with apply), or None if no bridge sequence can complete it."""
    C = _mul(_TINV, _inv(apply(rec)))
    X, Y = [0, 2, 4, 6], [1, 3, 5, 7]
    if any(C[i][j] != 0 for i in X for j in Y) or any(C[i][j] != 0 for i in Y for j in X):
        return None
    A = [[C[i][j] for j in X] for i in X]; B = [[C[i][j] for j in Y] for i in Y]
    if any(x.denominator != 1 for r in A for x in r) or _det(A) != 1:
        return None
    if B != [list(r) for r in zip(*_inv(A))]:
        return None
    ops = _reduce([[int(x) for x in r] for r in A])
    if ops is None:
        return None
    seq = [{'kind': 'bridge', 'dst': i, 'src': j, 'coefficient': -q} for (i, j, q) in reversed(ops)]
    return seq if apply(rec + seq + [TERMINAL]) == IDENTITY else None
