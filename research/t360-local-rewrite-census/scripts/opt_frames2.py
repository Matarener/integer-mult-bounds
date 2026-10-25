"""opt_frames with a fallback domain for wide quotients (>4 dims): {lo, hi} plus the
original gate frames seen for that (lo,hi).  Any assignment found is legal (checked
by containment), so savings are valid upper-bound witnesses; optimality not claimed."""
import opt_frames as O
from opt_frames import contains
_orig_domain = O.domain.__wrapped__ if hasattr(O.domain, '__wrapped__') else O.domain
EXTRA = {}
def domain(lo, hi):
    try:
        return _orig_domain(lo, hi)
    except ValueError:
        ch = {lo, hi} | {f for f in EXTRA.get((lo, hi), ()) if contains(lo, f) and contains(f, hi)}
        return tuple(sorted(ch, key=lambda f: (len(f), f)))
_graph = O.graph
def graph(w):
    r = _graph(w)
    sec, nodes, frames, edges, lo, hi, comps = r
    EXTRA.clear()
    for i in range(len(nodes)):
        EXTRA.setdefault((lo[i], hi[i]), set()).add(frames[i])
    return r
O.domain = domain
O.graph = graph
optimize = O.optimize
