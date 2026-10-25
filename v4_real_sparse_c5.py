# Sparse real-valued escape search on the 23 induced 5-cycles (C5 holes) of the non-orthogonality graph and on each
# hole extended by its 1 and 2 most degenerate extra planes (groups of 5, 6, 7).  Baseline = 4 per plane.
# Groups with orthogonal pairs have free mask entries; this is where scalar rank savings (C5) live.
import itertools, sys, time, multiprocessing as mp
from v4_real_sparse import search, tar, NP, ORTH
NON = [[i != j and not ORTH[i][j] for j in range(NP)] for i in range(NP)]
def c5_holes():
    out = set()
    for S in itertools.combinations(range(NP), 5):
        if all(sum(NON[a][b] for b in S) == 2 for a in S): out.add(S)
    return sorted(out)
def _run(a):
    D, st, sd = a
    return D, search(D, st, sd)
if __name__ == '__main__':
    starts = int(sys.argv[1]); t0 = time.time()
    holes = c5_holes(); groups = []
    for H in holes:
        groups.append(H); cur = list(H)
        for _ in range(2):
            best = min((x for x in range(NP) if x not in cur), key=lambda x: (tar(cur + [x], cur + [x]), x))
            cur = cur + [best]; groups.append(tuple(cur))
    todo = list(range(len(groups)))
    if len(sys.argv) > 2: todo = [int(x) for x in sys.argv[2].split(',')]   # resume: group indices still to run
    print('C5 holes', len(holes), '| groups (5/6/7 planes)', len(groups), '| running', len(todo), '%.0fs' % (time.time() - t0), flush=True)
    with mp.get_context('spawn').Pool(4) as pool:
        for D, best in pool.imap_unordered(_run, [(groups[i], starts, i) for i in todo]):
            base = 4 * len(D); tag = 'ESCAPE' if best and best[0] < base else 'no escape'
            print('group', D, 'size', len(D), 'baseline', base, 'best exact real decoder cost', best[0] if best else None, '->', tag, '%.0fs' % (time.time() - t0), flush=True)
            if best and best[0] < base: print('   terms:', best[1], flush=True)
