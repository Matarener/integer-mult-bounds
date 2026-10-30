"""PLANBUILD plan.py: load a pm3/pm4 model plan (population = pm2.build({}, dirsel=2, cos='pair'), P1 parameters) and recompute its
exact model R0 from the pick alone (non-hub part EXACT chain tax; hub roles re-solved given the pick, role-only CP-SAT per octet).
usage: plan.py PICK [PICK ...] [--d8sig] [--nX 3] [--late 4] [--enders 4]   (no env, no side effects at import)"""
import os
import sys, collections, pickle, io, contextlib
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
for p in (W + '/ext/HUBCOST', W + '/ext/PAIRMIX'):
    if p not in sys.path: sys.path.insert(0, p)

VMKT = {0: 3.10, 1: 3.10, 2: 3.10, 6: 3.10, 7: 3.10, 8: 3.10, 9: 3.10, 11: 3.10, 3: 9.29, 4: 9.29, 5: 9.29, 10: 9.29, 12: 9.29, 13: 2.00}
_B = {}

def population(dirsel=2, cos='pair'):
    import pm2
    key = (dirsel, cos)
    if key not in _B: _B[key] = pm2.build({}, dirsel=dirsel, cos=cos)
    return _B[key]

def option_regs(B, k, o):
    """registers of option o at arrival k: (piece reg or None, dual reg or None)"""
    if o[0] == 'a': return o[1], None
    if o[0] == 'b': return None, o[1]
    if o[0] == 'd': return o[1], o[2]
    return None, None

def evaluate(B, pick, hubs=True, cfg=None, verbose=True):
    import flagmodel as FM, rt, pmh
    from ortools.sat.python import cp_model
    tax = rt.tax
    N, DN = B['N'], B['DN']; ch, role = FM.regs_of(B)
    A = []
    for (prid, drid, dk) in B['arr']:
        p = ('b', N.rects[prid]['reg']); d = ('d', DN.rects[drid]['reg'])
        dg = len(N.rects[prid]['g']); dH = 9 - len(DN.rects[drid]['g'])
        mt = B['meta'][B['dmeta'][dk][1]]
        A.append((p, d, dg, dH, mt[0]))
    assert set(pick) == set(range(len(A))), ('pick keys', len(pick), len(A))
    fch = {r: list(c) for r, c in ch.items()}; frole = dict(role); alias = {}; ncopy = 0.0; used = set()
    cnt = collections.Counter()
    for k, o in sorted(pick.items()):
        p, d, dg, dH, kind = A[k]
        own = 'own'
        if o[0] == 'a':
            fch[o[1]].append(dH); own = 'own' if o[1] == p else 'alt'; used.add(o[1])
        elif o[0] == 'b':
            fch[o[1]].append(dg); own = 'own' if o[1] == d else 'alt'; used.add(o[1])
        elif o[0] == 'c': ncopy += tax([0, dg, dH, 9])
        else:
            pp, dd = o[1], o[2]; fch[pp] = fch[pp] + fch[dd]; frole[pp] = 'X' if role[pp] == 'X' else ('Y' if role[dd] == 'Y' else 'H'); alias[dd] = pp
            own = 'own' if (pp == p and dd == d) else 'alt'; used |= {pp, dd}
        cnt[(kind, o[0], own)] += 1
    tot = collections.Counter()
    for r, c in fch.items():
        if r in alias: continue
        tot[frole[r]] += FM.ftax(c, frole[r])
    tot['copy'] = ncopy
    if hubs:
        pmh.CFG.update(cfg or dict(d8sig=True, nX=3, late=4, enders=4))
        cX, cXacc, hc = pmh.role_prices(ch, role); htot = 0.0; roles = {}
        for o_, dd_ in sorted(pmh.byoctet(N).items()):
            M = cp_model.CpModel(); v = {}
            xs = [r for r in dd_['X'] if r not in used]; hs = [r for r in dd_['H'] if r not in used]
            for r in xs:
                v[(r, 'X')] = M.NewBoolVar(''); v[(r, 'acc')] = M.NewBoolVar(''); M.Add(v[(r, 'acc')] <= v[(r, 'X')])
            M.Add(sum(v[(r, 'X')] for r in xs) == pmh.CFG['nX']); M.Add(sum(v[(r, 'acc')] for r in xs) == 1)
            for r in hs:
                for kk in ('mate', 'late', 'ender'): v[(r, kk)] = M.NewBoolVar('')
                M.Add(sum(v[(r, kk)] for kk in ('mate', 'late', 'ender')) <= 1)
            for kk, n in (('mate', 1), ('late', pmh.CFG['late']), ('ender', pmh.CFG['enders'])):
                M.Add(sum(v[(r, k2)] for (r, k2) in v if k2 == kk) == n)
            cst = {(r, 'X'): cX for r in xs}; cst.update({(r, 'acc'): cXacc - cX for r in xs})
            cst.update({(r, kk): hc(r, kk) for r in hs for kk in ('mate', 'late', 'ender')})
            M.Minimize(sum(int(round(cst[key] * 1e6)) * b for key, b in v.items()))
            S = cp_model.CpSolver(); S.parameters.num_workers = 1; st = S.Solve(M)
            assert S.StatusName(st) == 'OPTIMAL', ('hub roles', o_, S.StatusName(st))
            htot += S.ObjectiveValue() / 1e6
            roles[o_] = {key: 1 for key, b in v.items() if S.Value(b)}
        tot['hub'] = htot
    R0 = sum(tot.values())
    if verbose:
        print('R0 %.2f' % R0, {k: round(v, 2) for k, v in tot.items()})
        print('options (kind, opt, holder):', sorted(cnt.items()))
    return dict(R0=R0, tot=tot, A=A, fch=fch, frole=frole, alias=alias, cnt=cnt, roles=roles if hubs else None, used=used)

if __name__ == '__main__':
    a = sys.argv[1:]
    g = lambda k, d: a[a.index(k) + 1] if k in a else d
    cfg = dict(d8sig='--d8sig' in a, nX=int(g('--nX', 3)), late=int(g('--late', 4)), enders=int(g('--enders', 4)))
    with contextlib.redirect_stdout(io.StringIO()): B = population()
    print('population: arrivals', len(B['arr']), 'piece regs', len(B['N'].regs), 'dual regs', len(B['DN'].regs))
    for f in [x for x in a if x.endswith('.pick')]:
        pk = pickle.load(open(f, 'rb')); print('==', f)
        r = evaluate(B, pk, hubs=True, cfg=cfg)
        print('R0eq = R0 - 73.3 + 317.4 = %.1f' % (r['R0'] - 73.3 + 317.4))
