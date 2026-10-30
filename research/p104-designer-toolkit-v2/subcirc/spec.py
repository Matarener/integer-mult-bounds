"""spec.py [G ...] : implementation-free I/O spec of market columns of #6030 (SUBCIRC sec 2), emitted to subcirc/specs/dual_<G>.json.gz.
Spec = PRINCIPLES pdata.load (members' events stripped): inputs = cone rows (non-member registers at frames containing G, with windows, exact rows mod p
over the non-member symbols), outputs = residual need D_y of each served Y (exact, mod p) and its decomposition over the cone rows, Y chains (frames, dims,
windows), obligations = members end at their unit rows. Round trip: sum_k need[y][k] * row[k] == D_y exactly (mod p) on the non-member symbols, and the
member-only part of D_y is zero (members carry no input of their own into the Ys).  No member event, role or frame is written."""
import sys, os, json, gzip
import numpy as np
sys.path[:0] = [os.path.dirname(os.path.abspath(__file__)), os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'alignbuild')]
import pdata
from pdata import rp, tax
P = rp.P
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')) + '/words/6030.json.gz'
DUALS = [118, 1050, 116, 1048, 114, 1052, 1049, 1051, 1053, 120, 1027, 115, 1031, 117]
def sparse(v): return {int(i): int(v[i]) for i in np.nonzero(v % P)[0]}
def emit(G, outdir):
    d = pdata.load(W, G); M = d['M']; R = d['R']; nonM = np.ones(R, dtype=bool); nonM[M] = False
    rows = {}
    # re-snapshot rows exactly as pdata does
    import collections
    snapt = collections.defaultdict(list)
    for r, f, t0, t1 in d['cone']: snapt[t1].append(r)
    _, snaps = rp.replay(d['w'], d['prog'], snap=snapt)
    for r, f, t0, t1 in d['cone']: rows['%d@%d' % (r, f)] = dict(reg=r, frame=f, dim=d['dim'][f], t0=t0, t1=t1, row=sparse(snaps[t1][r] * nonM))
    ok = True; outs = {}
    for y in d['served']:
        Dy = d['D'][y] % P
        nd = d['need'][y]
        if nd is None: ok = False; outs[y] = dict(D=sparse(Dy), need=None); continue
        acc = np.zeros(R, dtype=object)
        for (r, f), c in nd.items(): acc = (acc + c * snaps[[t1 for rr, ff, t0, t1 in d['cone'] if rr == r and ff == f][0]][r].astype(object)) % P
        rt = all(int(x) == 0 for x in ((acc - Dy.astype(object)) % P)[nonM]) and not (Dy[M] % P).any()
        ok &= rt
        outs[y] = dict(D=sparse(Dy), need={'%d@%d' % k: v for k, v in nd.items()}, roundtrip=rt,
                       chain=[dict(frame=f, dim=x, t0=t0, t1=t1) for f, x, t0, t1 in d['ych'][y]])
    sw = {m: [x for _, x in c] for m, c in d['swarm_chains'].items()}
    J = dict(schema='subcirc-spec/1', slot='dual', G=G, dimG=d['dim'][G], n_members=len(M), member_ids=M,
             current_cost=sum(tax(c) for c in sw.values()), current_chains=sorted(map(tuple, sw.values())),
             inputs=rows, outputs={str(k): v for k, v in outs.items()}, other_residual_rows=d['other'], roundtrip=ok,
             frames={str(f): d['w']['frames'][f] for f in set([G] + [v['frame'] for v in rows.values()] + [c['frame'] for o in outs.values() for c in o.get('chain', [])])})
    os.makedirs(outdir, exist_ok=True)
    json.dump(J, gzip.open('%s/dual_%d.json.gz' % (outdir, G), 'wt'))
    return J
if __name__ == '__main__':
    Gs = [int(x) for x in sys.argv[1:]] or DUALS
    for G in Gs:
        J = emit(G, os.path.dirname(os.path.abspath(__file__)) + '/specs')
        print('dual', G, 'members', J['n_members'], 'inputs', len(J['inputs']), 'served', len(J['outputs']), 'other', len(J['other_residual_rows']),
              'cost %.3f' % J['current_cost'], 'roundtrip', J['roundtrip'], flush=True)
