"""pdata.py WORD G: principle-solver input for the market column over frame G (members = H registers visiting G). Strips every member event
(as ALIGNLAW fullbuild) and returns geometry only: the cone over G (every non-member register visiting a frame containing G, with its windows),
served Ys (nonzero residual), their needs as combinations of cone rows, Y chains. No pairing / proxy / birth information is read."""
import sys, json, gzip, math, collections, pickle
import numpy as np
import os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(os.path.dirname(HERE), 'alignbuild'), HERE]
import rp
from rp import P
from life import rref, tax
S = rp.S

def load(word, G):
    path, w0 = S.load_word(word); w = json.loads(json.dumps(w0)); n = len(w['initial']); R = rp.nreg(w)
    fr = w['frames']; dim = [len(b) for b in fr]; span = [rref(b) for b in fr]; SG = span[G]
    live = w['live']; Ys = [r + 112 for r in live]; Yset = set(Ys); F0 = w['initial'][Ys[0]]
    role = S.roles_of(w); prog0 = w['program']; tl0 = rp.timelines(w)
    inside = lambda big, small: rref(list(big) + list(small)) == big
    M = sorted(r for r in range(n) if role(r) == 'H' and any(f == G for _, _, f in tl0[r]))
    Mset = set(M)
    swarm_chains = {m: [(f, dim[f]) for _, _, f in tl0[m]] for m in M}
    prog = [e for e in prog0 if not any(x in Mset for x in S.regfields(e))]
    F9 = {m: w['final'][m] for m in M}
    w['program'] = prog
    tl = rp.timelines(w, prog)
    # cone over G: non-member, non-Y registers with a window at a frame containing G (dims 5..8)
    cone = []
    for r in range(R):
        if r in Mset or r in Yset or r not in tl: continue
        for t0, t1, f in tl[r]:
            if 5 <= dim[f] <= 8 and inside(span[f], SG): cone.append((r, f, t0, min(t1, len(prog) - 1)))
    snapt = collections.defaultdict(list)
    for r, f, t0, t1 in cone: snapt[t1].append(r)
    A_end, snaps = rp.replay(w, prog, snap=snapt)
    D = (rp.target(w) - A_end) % P
    served = [y for y in Ys if D[y].any()]
    other = [r for r in range(R) if D[r].any() and r not in Yset and r not in Mset]
    nonM = np.ones(R, dtype=bool); nonM[M] = False
    rows = {(r, f): snaps[t1][r] for r, f, t0, t1 in cone}
    keys = list(rows)
    Aeq = np.array([rows[k][nonM] for k in keys]).T % P
    need = {}
    for y in served:
        x = rp.solve(Aeq, D[y][nonM])
        need[y] = None if x is None else {keys[i]: int(v) for i, v in enumerate(x) if v}
    ych = {y: [(f, dim[f], t0, t1) for t0, t1, f in tl[y]] for y in served}
    return dict(w=w, w0=w0, prog=prog, G=G, M=M, F9=F9, F0=F0, dim=dim, span=span, cone=cone, served=served, other=other, need=need,
                ych=ych, swarm_chains=swarm_chains, tl=tl, D=D, n=n, R=R)

if __name__ == '__main__':
    d = load(sys.argv[1], int(sys.argv[2]))
    dim = d['dim']
    print('G', d['G'], 'dim', dim[d['G']], 'members', d['M'])
    for m, c in d['swarm_chains'].items(): print('  swarm member', m, c, 'tax %.3f' % tax([x for _, x in c]))
    print('swarm column tax %.3f' % sum(tax([x for _, x in c]) for c in d['swarm_chains'].values()))
    print('cone over G:', len(d['cone']))
    for r, f, t0, t1 in d['cone']: print('  ', r, 'f', f, 'dim', dim[f], 'win', t0, t1)
    print('served Ys', d['served'], 'other residual rows', d['other'][:10])
    for y in d['served']:
        print('  Y', y, 'chain', [(f, x) for f, x, _, _ in d['ych'][y]], 'needs', None if d['need'][y] is None else {k: str(rp.ratrec(v)) for k, v in d['need'][y].items()})
    pickle.dump({k: v for k, v in d.items() if k not in ('w', 'w0', 'prog', 'tl', 'D')}, open('pdata_%d.pkl' % d['G'], 'wb'))
