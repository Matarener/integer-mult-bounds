"""exact symbolic check of a model net's ops: replay contents (sorted by (dim, seq)), Y_j must receive exactly -RES[j,i] x_i."""
import rt, geo, collections
from fractions import Fraction as Fr
def check(N, I):
    cont = {}
    for r, Rg in N.regs.items():
        cont[r] = {Rg['tag']: Fr(1)} if Rg['role'] == 'X' else {}
    for j in range(geo.m): cont[('Y', j)] = {}
    order = sorted(range(len(N.ops)), key=lambda t: (N.ops[t][4], t))
    for t in order:
        d, s, q, fk, dim = N.ops[t]
        dd = dict(cont[d])
        for c, v in cont[s].items():
            dd[c] = dd.get(c, 0) + q * v
            if dd[c] == 0: del dd[c]
        cont[d] = dd
    bad = 0
    for j in range(geo.m):
        want = {i: -Fr(geo.RES[j, i]).limit_denominator(8) for i in range(geo.m) if geo.ORTH[j, i]}
        if cont[('Y', j)] != want: bad += 1
    return bad
if __name__ == '__main__':
    import grp
    I = rt.bottom_inst(); N, _ = rt.build(I, lam=4.0); print('bottom-only bad Y', check(N, I), 'ops', len(N.ops), 'R0', round(rt.r0(N)[1]))
    M = grp.swarm_matching(); I = grp.inst(M); N, _ = rt.build(I, lam=4.0); print('grp swarm bad Y', check(N, I), 'ops', len(N.ops), 'R0', round(rt.r0(N)[1]))
