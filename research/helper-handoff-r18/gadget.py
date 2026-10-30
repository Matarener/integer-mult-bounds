"""Constructive proof of concept: SUCCESSOR HAND-OFF of a productive conduit helper (R18).

Scaled-down native instance on F_2^5 (h = 5 axes).  Registers:
  0 x   port line      start A=<1>      final U (full)
  1 m1  main consumer  start 0          final U     wanted row m1_in + x_in
  2 c   main consumer  start 0          final U     wanted row  c_in + x_in
  3 h   helper (arbitrary dirty input, must be restored)
  4 s   successor helper (hand-off version only; arbitrary dirty input, starts at F)
The helper h is a CONDUIT, the same motif as #4610's helper threads (e.g. h300: read a port line at a
low frame, carry it along a different flag, deliver it to consumers there, uncompute at the top):
x's data must reach m1 at frame B=<1,2> and c at frame G=<1,2,4,8>; x itself travels A -> Xb=<1,4> -> F.

BASELINE: h carries x from A through B, F, G to U; consumers pre-subtract h_in while h is pure at A;
the uncompute h -= x happens at the top.  h climbs 0>A>B>F>G>U: five rank-1 jobs, ONE rank-5 target.

HAND-OFF: identical paid climbs.  At F, where x meets the conduit with unchanged data, two free ADDs
make h pure (h -= x) and load the successor (s += x); h retires at F with a rank-3 target and s (which
sat idle at its start frame F) carries the conduit F>G>U with a rank-2 target.  The consumer above F
(c) pre-subtracts s_in instead of h_in, during its own early pass through F while s is still pure.
Every register ends with its wanted row on ALL arbitrary input columns (exact replay, nreplay.py =
literal_replay rules).  Targets 5 -> 3 + 2 at the same paid profile."""
import sys
from fractions import Fraction as Q
from nreplay import replay, v, need
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))

FR = [[], [1], [1, 2], [1, 4], [1, 2, 4], [1, 2, 4, 8], [1, 2, 4, 8, 16]]
Z, A, B, XB, F, G, U = range(7)
X, M1, CC, H, S = 0, 1, 2, 3, 4
def climb(i, a, b): return ('climb', 'L', i, a, b, len(FR[b]) - len(FR[a]))
def add(t, s, num, frame, den=1): return ('scalar', ['add', ['L', t], ['L', s], num, den], frame)

CLR = ('scalar', ['clear', ['C', 0]], Z)   # owned C0 is unused; cleared as the interpreter requires
def baseline():
    return [CLR, climb(H, Z, A),
            climb(M1, Z, A), add(M1, H, -1, A),          # m1 -= h_in (h pure at A)
            climb(CC, Z, A), add(CC, H, -1, A),          # c  -= h_in
            add(H, X, 1, A),                              # conduit loads x
            climb(CC, A, F), climb(CC, F, G),             # c passes F early (before x arrives there)
            climb(H, A, B), climb(M1, A, B), add(M1, H, 1, B),   # m1 = m1_in + x_in
            climb(X, A, XB), climb(X, XB, F), climb(H, B, F),    # x and h meet at F
            climb(H, F, G), add(CC, H, 1, G),             # c = c_in + x_in
            climb(H, G, U), climb(X, F, U), add(H, X, -1, U),    # uncompute at the top
            climb(M1, B, U), climb(CC, G, U)]

def handoff(presub=True, cancel=True, cancel_frame=F):
    p = [CLR, climb(H, Z, A),
         climb(M1, Z, A), add(M1, H, -1, A),
         climb(CC, Z, A)] + ([] if presub else [add(CC, H, -1, A)]) + [
         add(H, X, 1, A),
         climb(CC, A, F)] + ([add(CC, S, -1, F)] if presub else []) + [   # c -= s_in (s idle & pure at F)
         climb(CC, F, G),
         climb(H, A, B), climb(M1, A, B), add(M1, H, 1, B),
         climb(X, A, XB)]
    if cancel_frame == XB:            # control: try the cancellation before x reaches F
        p += [add(H, X, -1, XB)]
    p += [climb(X, XB, F), climb(H, B, F)]
    if cancel and cancel_frame == F:
        p += [add(H, X, -1, F)]                                   # h pure: retires at F
    p += [add(S, X, 1, F),                                        # successor takes the conduit
          climb(S, F, G), add(CC, S, 1, G),
          climb(S, G, U), climb(X, F, U), add(S, X, -1, U),
          climb(M1, B, U), climb(CC, G, U)]
    return p

def wanted(n):
    out = {}
    for r in range(n):
        row = v.identity(('L', r))
        if r in (M1, CC): v.add(row, v.identity(('L', X)), Q(1))
        out[r] = row
    return out

def run(name, n, start, final, prog, helpers):
    rows, prof, climbs = replay(n, FR, start, final, prog)
    want = wanted(n)
    ok = all(rows['L', r] == want[r] for r in range(n))
    need(ok, name + ': endpoint rows')
    targets = sorted(len(FR[final[i]]) - len(FR[start[i]]) for i in helpers)
    print(f'{name:9s} all {n} arbitrary input columns exact: {ok}; paid profile {prof}; '
          f'helper climbs {[climbs[i] for i in helpers]}; productive helper targets {targets}')
    return prof, targets

if __name__ == '__main__':
    p0, t0 = run('baseline', 4, [A, Z, Z, Z], [U, U, U, U], baseline(), [H])
    p1, t1 = run('hand-off', 5, [A, Z, Z, Z, F], [U, U, U, F, U], handoff(), [H, S])
    need(p0 == p1, 'same paid profile'); need(sum(t0) == sum(t1), 'same target mass (rank-mass invariant)')
    # mutation controls: each must FAIL
    ctl = {'no successor pre-subtraction': dict(presub=False),
           'no co-framed cancellation': dict(cancel=False),
           'cancellation before the frames meet': dict(cancel=False, cancel_frame=XB)}
    for name, kw in ctl.items():
        try:
            run('control', 5, [A, Z, Z, Z, F], [U, U, U, F, U], handoff(**kw), [H, S]); raise SystemExit('control passed: ' + name)
        except AssertionError as e:
            print(f'control rejected ({name}): {str(e)[:60]}')
    print('PASS_HANDOFF_GADGET targets', t0, '->', t1, 'paid', p0)
