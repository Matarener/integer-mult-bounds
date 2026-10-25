"""R19 designed native blocks on F_2^9 (exact replay with nreplay = literal_replay rules).

Conduit block (h300 motif): port x read by helper h at A (dim a), data delivered to consumer m at B (dim b,
off x's flag) and consumer c at G (dim gg), uncompute at the top U (dim 9).  Optional bottom holder y
(h starts at dim 0 and pre-subtracts h_in into y; y reads h at G).  Four words per parameter set:
  BASE      h carries the conduit to U, x jumps A->U directly (no pass-through visits anywhere)
  HAND      successor hand-off at F = B: x lifted A->B->U, h retires at B, s starts at B
  LATE      (only with y) later entrance: h starts at A, y pre-subtracts at A (y lifted 0->A->G)
  LATE+HAND hand-off at B on LATE
Each word is replayed exactly on all arbitrary-input columns (identity/restoration semantics: x, h, s, y
restored; m = m_in + x_in; c = c_in + x_in; y = y_in + x_in), and dM = sum f(targets) - sum f(paid)."""
import sys, itertools
from decimal import Decimal as D, getcontext
from fractions import Fraction as Q
from pathlib import Path
getcontext().prec = 50
sys.path.insert(0, str(Path.home()/'imb-r19/research/helper-handoff-r18'))
from nreplay import replay, v, need
CROOT = D('0.0030272882499395587812724555013848588705741016191552')   # selected #5413 raw root
def f(x): return D(0) if x == 0 else (D(x).ln() * (1 - CROOT)).exp()

FR = [[1 << i for i in range(k)] for k in range(10)]   # flag H_0 < H_1 < ... < H_9 (frame index = dim)
X, M, CC, H, Y, S = range(6)
def climb(i, a, b): return ('climb', 'L', i, a, b, b - a)
def add(t, s, num, fr): return ('scalar', ['add', ['L', t], ['L', s], num, 1], fr)
CLR = ('scalar', ['clear', ['C', 0]], 0)

def word(a, b, gg, holder, late, hand):
    U = 9; hs = a if (late or not holder) else 0
    st = {X: a, M: b, CC: gg, H: hs, Y: 0, S: b}; fi = {X: U, M: U, CC: U, H: U, Y: U, S: U}
    p = [CLR]
    if holder:
        if late: p += [climb(Y, 0, a), add(Y, H, -1, a)]
        else: p += [add(Y, H, -1, 0), climb(H, 0, a)]
    p += [add(H, X, 1, a), climb(H, a, b), add(M, H, 1, b)]
    yfrom = a if late else 0
    if hand:
        p += [climb(X, a, b), add(H, X, -1, b), add(M, H, -1, b)]            # h pure; m recollects h_in
        if holder: p += [climb(Y, yfrom, b), add(Y, H, 1, b), add(Y, S, -1, b)]   # y: h_in -> s_in
        p += [add(S, X, 1, b), climb(S, b, gg), add(CC, S, 1, gg)]
        if holder: p += [climb(Y, b, gg), add(Y, S, 1, gg)]
        p += [climb(S, gg, U), climb(X, b, U), add(S, X, -1, U), climb(CC, gg, U), add(CC, S, -1, U),
              climb(M, b, U)]
        fi[H] = b; helpers = [H, S]
    else:
        p += [climb(H, b, gg), add(CC, H, 1, gg)]
        if holder: p += [climb(Y, yfrom, gg), add(Y, H, 1, gg)]
        p += [climb(H, gg, U), climb(X, a, U), add(H, X, -1, U), climb(M, b, U), add(M, H, -1, U),
              climb(CC, gg, U), add(CC, H, -1, U)]
        helpers = [H]
    if holder: p += [climb(Y, gg, U)]
    regs = [X, M, CC, H] + ([Y] if holder else []) + ([S] if hand else [])
    n = max(regs) + 1
    start = [st[r] if r in regs else 0 for r in range(n)]; final = [fi[r] if r in regs else 0 for r in range(n)]
    return n, regs, start, final, p, helpers

def check(a, b, gg, holder, late, hand):
    n, regs, start, final, prog, helpers = word(a, b, gg, holder, late, hand)
    rows, prof, climbs = replay(n, FR, start, final, prog)
    for r in regs:
        want = v.identity(('L', r))
        if r in (M, CC, Y): v.add(want, v.identity(('L', X)), Q(1))
        need(rows['L', r] == want, 'endpoint row of register %d' % r)
    targets = sorted(final[i] - start[i] for i in helpers)
    dM = sum(f(k) for k in targets) - sum(cnt * f(k) for k, cnt in prof.items())
    return prof, targets, dM

if __name__ == '__main__':
    print('flag frames H_k = <e_0..e_{k-1}>; f(x)=x^(1-C) at the selected raw root C=%s' % str(CROOT)[:14])
    best = {}
    for holder in (False, True):
        for a, b, gg in itertools.product(range(1, 8), range(2, 9), range(3, 9)):
            if not a < b < gg < 9: continue
            res = {}
            for late, hand in [(False, False), (False, True)] + ([(True, False), (True, True)] if holder else []):
                res[(late, hand)] = check(a, b, gg, holder, late, hand)
            base = res[(False, False)][2]
            bestbase = max(res[k][2] for k in res if not k[1]); besthand = max(res[k][2] for k in res if k[1])
            key = 'holder' if holder else 'plain'
            best.setdefault(key, []).append((float(res[(False, True)][2] - base), float(besthand - bestbase), a, b, gg))
            if (a, b, gg) in [(1, 4, 6), (3, 4, 5), (2, 5, 7)]:
                for k, (prof, t, dm) in res.items():
                    print(f'{key:6s} a={a} F=B={b} G={gg} {"LATE" if k[0] else "BASE"}{"+HAND" if k[1] else "     "} '
                          f'exact rows OK; paid {prof}; helper targets {t}; block dM {float(dm):+.6f}')
    for key, rows in best.items():
        rows.sort(reverse=True)
        mx = max(rows, key=lambda r: r[1])
        print(f'{key}: {len(rows)} parameter sets; max dM(HAND - BASE) = {rows[0][0]:+.6f} at a,b,G={rows[0][2:]}; '
              f'max dM(best hand-off word - best non-hand-off word) = {mx[1]:+.6f} at a,b,G={mx[2:]}')
    print('PASS_BLOCK_R19')
