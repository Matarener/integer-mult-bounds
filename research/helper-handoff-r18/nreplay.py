"""Generalised literal native replay (R18).

Same rules as research/kappa-rebuild/complex/native_extensions.py::literal_replay, but for any number of
persistent registers and any frame lattice F_2^h:
  * scalar add/copy/scale need the target (and source) at the event's exact frame index;
  * clear and copy may only target the owned register ('C',0);
  * a climb is a strictly ascending subspace inclusion, paid at its dimension jump (rank checked);
  * warps change the frame and append a word symbol (verify_buffers.warp);
  * final frames must match and owned C0 must be cleared at return.
Rows are exact (Fraction) formal combinations of (input, warp word)."""
import sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'research/kappa-causal-continuation/buffer-borrowing'))
import verify_buffers as v

def need(ok, msg):
    if not ok: raise AssertionError(msg)

def span(basis):
    pts = {0}
    for x in basis: pts |= {p ^ x for p in tuple(pts)}
    return frozenset(pts)

def replay(n, frames, start, final, program, backward=False):
    rows = {('L', i): v.identity(('L', i)) for i in range(n)}; rows['C', 0] = v.identity(('C', 0))
    cur = {('L', i): f for i, f in enumerate(start)}; cur['C', 0] = None
    sp = [span(f) for f in frames]; profile = Counter(); climbs = Counter()
    for event in program:
        kind = event[0]
        if kind == 'scalar':
            g, frame = event[1:]; t = tuple(g[1])
            if g[0] == 'clear':
                need(t == ('C', 0), 'Only owned C0 can be cleared'); rows[t] = {}; cur[t] = frame
            else:
                need(cur[t] == frame, 'Exact scalar target frame %r' % (event,))
                if g[0] in ('add', 'copy'):
                    s = tuple(g[2]); need(cur[s] == frame, 'Exact scalar source frame %r' % (event,))
                    if g[0] == 'copy':
                        need(t == ('C', 0), 'Only owned field overwritten by copy'); rows[t] = dict(rows[s])
                    else:
                        need(t != s, 'Distinct reversible ADD arguments'); v.add(rows[t], rows[s], Q(g[3], g[4]))
                else:
                    need(g[0] == 'scale', 'Known scalar action'); q = Q(g[2], g[3])
                    rows[t] = {k: q*x for k, x in rows[t].items()}
        elif kind == 'warp':
            _, r, op, old, new = event; t = tuple(r)
            need(cur[t] == old, 'Warp input frame'); rows[t] = v.warp(rows[t], op, backward); cur[t] = new
        elif kind in ('climb', 'center'):
            if kind == 'climb':
                _, part, i, old, new, rank = event; t = ('L', i)
                need(sp[old] < sp[new], 'Ascending borrowed climb %r' % (event,)); climbs[i] += 1
            else:
                _, i, old, new, rank = event; t = ('C', i)
                need(sp[old] < sp[new] or sp[new] < sp[old], 'Nested center transport')
            need(cur[t] == old and rank == abs(len(frames[new]) - len(frames[old])), 'Paid rank and source frame %r' % (event,))
            cur[t] = new; profile[rank] += 1
        else:
            need(kind in ('phase', 'adapter', 'residual_adapter'), 'Known inert native marker')
    need([cur['L', i] for i in range(n)] == list(final), 'Final native frames')
    need(not rows['C', 0], 'Owned C0 cleared at return')
    return rows, dict(sorted(profile.items())), climbs
