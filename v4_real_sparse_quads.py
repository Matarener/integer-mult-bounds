# Same sparse real-valued escape search as v4_real_sparse.py, on the MOST DEGENERATE plane quadruples
# (smallest tariff(D, D) = pairing rank of the whole group with itself).  Baseline = 16 (4 per plane).
import itertools, sys, time, multiprocessing as mp
from v4_real_sparse import search, tar, NP, ORTH
def _run(a):
    D, st, sd = a
    return D, search(D, st, sd)
if __name__ == '__main__':
    n_groups = int(sys.argv[1]); starts = int(sys.argv[2]); t0 = time.time()
    cand = []
    for D in itertools.combinations(range(NP), 4):
        cand.append((tar(D, D), sum(not ORTH[a][b] for a, b in itertools.combinations(D, 2)), D))
    cand.sort(key=lambda x: (x[0], -x[1]))
    pick = [D for _, _, D in cand[:n_groups]]
    from collections import Counter
    print('quadruples scanned', len(cand), '%.0fs' % (time.time() - t0), '| tariff(D,D) of picked:', dict(Counter(c[0] for c in cand[:n_groups])), flush=True)
    with mp.get_context('spawn').Pool(4) as pool:
        for D, best in pool.imap_unordered(_run, [(D, starts, i) for i, D in enumerate(pick)]):
            tag = 'ESCAPE' if best and best[0] < 16 else 'no escape'
            print('quad', D, 'best exact real decoder cost', best[0] if best else None, '->', tag, '%.0fs' % (time.time() - t0), flush=True)
            if best and best[0] < 16: print('   terms:', best[1], flush=True)
