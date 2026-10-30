"""Realize a frame assignment as an actual native program and replay it exactly.
Order = stable topological sort (priority = original position) of conflict edges plus
per-register-segment frame-order edges; climbs synthesized (warp_merge.synthesize)."""
import sys, json, heapq, gzip, time
from copy import deepcopy
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from lift import *
ROOTP = __import__('pathlib').Path.home()/'imb-r13'
sys.path.insert(0, str(ROOTP/'research/warp-interface-20261022'))
from warp_merge import J, F, synthesize

def realize(w, side, frames):
    """frames: {op index in poset list p: basis list}. Returns new program (with climbs) and new canonical."""
    c = deepcopy(w['canonical']); orig = w['programs'][side]
    labels = {span(b): i for i, b in enumerate(c['frames'])}
    def lab(b):
        s = span(b)
        if s not in labels:
            labels[s] = len(c['frames']); c['frames'].append(sorted(join(b), reverse=True))
        return labels[s]
    events = [e for e in orig if e[0] != 'climb']
    pidx = [k for k, e in enumerate(events) if e[0] not in ('phase', 'adapter', 'residual_adapter')]
    p, groups = build(w, side)
    assert len(p) == len(pidx)
    seg, nseg = segments(p, groups)
    newev = [deepcopy(e) for e in events]
    fdim = {}
    for i, e in enumerate(p):
        k = pidx[i]
        if i in frames:
            assert newev[k][0] == 'scalar'
            newev[k][2] = lab(frames[i])
        if newev[k][0] == 'scalar': fdim[i] = len(c['frames'][newev[k][2]])
    # graph over poset ops
    succ = defaultdict(set); indeg = [0]*len(p)
    def edge(a, b):
        if b not in succ[a]: succ[a].add(b); indeg[b] += 1
    hub = len(p); extra = 0
    nodes = list(range(len(p)))
    for r, gl in groups.items():
        for (t0, A), (t1, B) in zip(gl, gl[1:]):
            for a in A:
                for b in B: edge(a, b)
    # frame-order edges within register segments
    members = defaultdict(list)
    for i in range(len(p)):
        for R, k in seg[i].items():
            if isinstance(k, int) and i in fdim: members[R, k].append(i)
    for key, m in members.items():
        bylev = defaultdict(list)
        for i in m: bylev[fdim[i]].append(i)
        ls = sorted(bylev)
        for l1, l2 in zip(ls, ls[1:]):
            for a in bylev[l1]:
                for b in bylev[l2]: edge(a, b)
    heap = [(pidx[i], i) for i in range(len(p)) if indeg[i] == 0]; heapq.heapify(heap); order = []
    while heap:
        _, i = heapq.heappop(heap); order.append(i)
        for j in succ[i]:
            indeg[j] -= 1
            if indeg[j] == 0: heapq.heappush(heap, (pidx[j], j))
    assert len(order) == len(p), 'cycle'
    # place markers: keep each marker before the first op that originally followed it
    pos_of = {pidx[i]: n for n, i in enumerate(order)}
    out = []; markers = defaultdict(list); nxt = None
    for k in range(len(events)-1, -1, -1):
        if k in pos_of: nxt = pos_of[k]
        else: markers[nxt if nxt is not None else len(order)].append(events[k])
    for n, i in enumerate(order):
        out += list(reversed(markers.get(n, []))); out.append(newev[pidx[i]])
    out += list(reversed(markers.get(len(order), [])))
    prog = synthesize(c, out)
    return c, prog

def replay(c, prog, backward):
    V = F.load(ROOTP/'research/kappa-causal-continuation/buffer-borrowing/verify_buffers.py', 'r13_rows')
    X = F.load(ROOTP/'research/kappa-rebuild/complex/native_extensions.py', 'r13_literal')
    rows, rec = X.literal_replay(V, c, prog, backward)
    ok = all(rows['L', r] == V.expected(('L', r), [], backward, False) for r in range(632))
    F.need(ok, 'All632 arbitrary persistent endpoints')
    prof = Counter({int(k): v for k, v in rec['paid_profile'].items()})
    rebound = deepcopy(c); rebound['R'] = len(c['start'])-2*c['v']; rebound['local_profile'] = dict(prof)
    second = V.replay(prog, rebound, [], backward, False)
    return prof, rec, second

if __name__ == '__main__':
    side = sys.argv[1]; sol = json.load(open(sys.argv[2]))
    frames = {int(k): v for k, v in sol['frames'].items()}
    w = load(); t = time.time(); c, prog = realize(w, side, frames)
    print('program', len(prog), 'climbs', sum(e[0] == 'climb' for e in prog), 't', time.time()-t, flush=True)
    prof, rec, second = replay(c, prog, side == 'backward')
    print('PASS replay', dict(sorted(prof.items())), 'mass', sum(k*v for k, v in prof.items()))
    from price import root
    pp = dict(prof); pp.pop(8, None) if pp.get(8) == 8 else None
    print('root', root({k: v for k, v in prof.items() if k != 8} | ({8: prof[8]-8} if prof.get(8, 0) > 8 else {})))
    if len(sys.argv) > 3:
        open(sys.argv[3], 'wb').write(gzip.compress(json.dumps(dict(canonical=c, program=prog)).encode(), mtime=0))
