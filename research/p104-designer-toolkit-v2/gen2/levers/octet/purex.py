"""OCTLIFE copy of PUREX/purex.py (Z = birth frame of the 0-born registers).
PUREX end-early pass (DAG level, exact Fractions).  usage: python -B purex.py IN.json.gz OUT.json.gz [--mode y8|xstop] [--max N]
A helper h ends at frame f (its last non-F9 frame) after a cleanup  h -= sum a_R R  at f whose x-part removes h's x-content.
All non-x symbols that the cleanup (or the missing F9 restore) leaves are pre-cancelled at dim 0 (Zh: r -= c*s with s still pure),
Y junk loads (Zy) are re-solved against the post-Zh dim-0 values, F9 ops touching an ender are deleted, and F9 registers' remaining
residue is cancelled at the end of F9 from clean registers (dependency order).  Iterate replay -> residue until exact.
No env vars at import."""
import sys, os, gzip, json, collections
from fractions import Fraction as Q
TK = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
for p in (TK, os.path.join(TK, 'synth'), os.path.join(os.path.dirname(TK), 'infra'), TK + '/gen2'):
    if p not in sys.path: sys.path.insert(0, p)

def dy(q): q = Q(q); return q != 0 and (q.denominator & (q.denominator - 1)) == 0 and abs(q) + 1 < 2 ** 16

def addf(d, s, q):
    for c, v in s.items():
        t = d.get(c, 0) + q * v
        if t: d[c] = t
        else: d.pop(c, None)

def replay(ops, n, no, snap=None):
    F = [{r: Q(1)} for r in range(n)] + [{} for _ in range(no)]; S = {}
    for i, o in enumerate(ops):
        op, r, s, q = o[0], o[1], o[2], o[3]
        if op in ('INIT', 'CLEAR'): F[r] = {}
        elif op == 'SCALE': F[r] = {c: v * Q(q) for c, v in F[r].items()}
        elif op == 'COPY': F[r] = {c: v * Q(q) for c, v in F[s].items()}
        else: addf(F[r], F[s], Q(q))
        if snap is not None and i in snap: S[i] = [dict(x) for x in F]
    return F, S

class Ctx:
    def __init__(s, w):
        import dag as D
        s.D = D; s.w = w; s.d = D.decompile(w, forms=False); d = s.d
        s.n = d['meta']['npub']; s.no = d['meta']['nowned']; s.live = set(d['meta']['live'])
        fr = d['frames']; s.dim = [len(b) for b in fr]
        s.F9 = max(range(len(fr)), key=lambda f: s.dim[f])
        z0 = collections.Counter(d['regs'][str(r)][1] for r in range(d['meta']['npub']) if s.dim[d['regs'][str(r)][1]] == 0)
        s.Z = z0.most_common(1)[0][0] if z0 else [i for i in range(len(fr)) if s.dim[i] == 0][0]   # OCTLIFE: octet words have 2 empty frames
        s.role = lambda r: 'O' if r >= s.n else ('X' if r in s.live else ('Y' if (r - 112) in s.live else 'H'))
        s.req = D.required(d['meta'])
        ops = d['ops']; s.zy = []; s.body = []; s.f9 = []
        for o in ops:
            if o[0] == 'ADD' and o[4] == s.Z and s.role(o[1]) == 'Y' and not s.body: s.zy.append(o)
            elif o[0] == 'ADD' and o[4] == s.F9: s.f9.append(o)
            else:
                assert not s.f9, 'body op after F9 block'
                s.body.append(o)
        s.init = {r: d['regs'][str(r)][1] for r in range(s.n)}
        s.born0 = {r for r in range(s.n) if s.init[r] == s.Z}

    def census(s, mode='y8', maxn=None, xstops=False, dims=None):
        """sequential joint census on the body.  returns list of enders dict(h, t (body idx), f, use[(R, coef)])."""
        n = s.n; role = s.role; body = s.body
        last = {}; bad = set()
        for i, o in enumerate(body):
            if o[0] in ('ADD', 'COPY'):
                last[o[1]] = i; last[o[2]] = i
                if role(o[1]) in ('X', 'O') and role(o[2]) == 'H': bad.add(o[2])
            elif o[0] == 'SCALE': last[o[1]] = i
        for o in s.f9:
            if role(o[1]) == 'X' and role(o[2]) == 'H': pass
        want = collections.defaultdict(list)
        for h, i in last.items():
            if h < n and role(h) == 'H' and h not in bad and s.init[h] == s.Z: want[i].append(h)
        X = {r: ({r: Q(1)} if role(r) == 'X' else {}) for r in range(n + s.no)}
        J = {r: ({r} if (r < n and role(r) == 'H' and r not in s.born0) else set()) for r in range(n + s.no)}   # non-dim-0 junk symbols carried
        cur = dict(s.init); at = collections.defaultdict(set)
        for r in range(n): at[cur[r]].add(r)
        from ee0 import solve
        acc = []
        SP = []
        for b in s.d['frames']:
            z = {0}
            for v in b: z |= {x ^ v for x in z}
            SP.append(frozenset(z))
        nxt = {}; nexto = [None] * len(body)       # for X mains: frame of the next op after body index i
        for i in range(len(body) - 1, -1, -1):
            o = body[i]
            for x in ([o[1], o[2]] if o[0] in ('ADD', 'COPY') else [o[1]]):
                if x is not None and x < n and role(x) == 'X': nxt[x] = (i, o[4])
            nexto[i] = dict(nxt)
        xs = [r for r in range(n) if role(r) == 'X']
        hist = {x: [(-1, s.init[x], {x: Q(1)})] for x in xs}; XV = {x: {x: Q(1)} for x in xs}
        if xstops:
            XX = {r: ({r: Q(1)} if role(r) == 'X' else {}) for r in range(n + s.no)}
            for i, o in enumerate(body):
                op, r, src, q, f = o[:5]
                if op == 'ADD': addf(XX[r], XX[src], Q(q))
                elif op == 'COPY': XX[r] = {c: v * Q(q) for c, v in XX[src].items()}
                elif op in ('INIT', 'CLEAR'): XX[r] = {}
                elif op == 'SCALE': XX[r] = {c: v * Q(q) for c, v in XX[r].items()}
                for x in ([r, src] if op in ('ADD', 'COPY') else [r]):
                    if x in hist: hist[x].append((i, f, dict(XX[x])))
        for i, o in enumerate(body):
            op, r, src, q, f = o[:5]
            for x in ([r, src] if op in ('ADD', 'COPY') else [r]):
                if x is not None and x < n and cur.get(x) != f:
                    at[cur[x]].discard(x); cur[x] = f; at[f].add(x)
            if op == 'ADD': addf(X[r], X[src], Q(q)); J[r] = J[r] | J[src]
            elif op == 'COPY': X[r] = {c: v * Q(q) for c, v in X[src].items()}; J[r] = set(J[src])
            elif op in ('INIT', 'CLEAR'): X[r] = {}; J[r] = set()
            elif op == 'SCALE': X[r] = {c: v * Q(q) for c, v in X[r].items()}
            for h in want.get(i, []):
                if maxn is not None and len(acc) >= maxn: continue
                f = cur[h]; v = X[h]
                if dims is not None and s.dim[f] not in dims: continue
                oth = sorted(x for x in at[f] if x != h and x < n)
                c = solve(v, [X[x] for x in oth]) if v else {}
                tins = [i] * len(oth)
                if c is None and xstops and s.dim[f] < 8:
                    cand = []; ct = []
                    for x in xs:
                        if x in oth: continue
                        H = hist[x]
                        for k in range(len(H)):
                            ti, fa, val = H[k]; tn, fb = (H[k + 1][0], H[k + 1][1]) if k + 1 < len(H) else (len(body), s.d['regs'][str(x)][2])
                            if tn <= i: continue
                            if SP[fa] <= SP[f] <= SP[fb] and val: cand.append(val); ct.append((x, max(ti, i)))
                    c = solve(v, [X[x] for x in oth] + cand)
                    if c is not None:
                        oth = oth + [x for x, _ in ct]; tins = tins + [t for _, t in ct]
                if c is None: continue
                use = [(oth[k], -a, tins[k]) for k, a in c.items() if a]
                if not all(dy(a) for _, a, _ in use): continue
                if J[h] or any(J[R] for R, _, t in use if t == i): continue
                acc.append(dict(h=h, t=i, f=f, use=use)); X[h] = {}
        return acc

    def build(s, enders, maxit=40, verbose=True):
        n, no, role = s.n, s.no, s.role
        E = {e['h']: e for e in enders}
        ins = collections.defaultdict(list)
        for e in enders:
            for R, a, t in e['use']: ins[t].append(['ADD', e['h'], R, str(a), e['f'], None])
        body = []
        for i, o in enumerate(s.body):
            body.append(list(o)); body += ins.get(i, [])
        f9 = [list(o) for o in s.f9 if o[1] not in E and o[2] not in E]
        Zh = collections.defaultdict(dict)          # r -> {pure source: coef}
        clean_end = lambda r: r < n and r not in E and role(r) in ('X', 'H') and (s.init[r] != s.Z or True)
        for it in range(maxit):
            zh = s.order_zh(Zh)
            if zh is None: raise SystemExit('PUREX: Zh cycle')
            # V0 = values after Zh (sources pure by construction)
            V0 = {r: ({r: Q(1)} if r < n else {}) for r in range(n + no)}
            for o in zh: addf(V0[o[1]], {o[2]: Q(1)}, Q(o[3]))
            # Y loads: solve on the program without Zy
            prog = zh + body + f9
            F, _ = replay(prog, n, no)
            zy = []; fail = []
            for y in range(n):
                if role(y) != 'Y': continue
                rr = {c: F[y].get(c, 0) - s.req[y].get(c, 0) for c in set(F[y]) | set(s.req[y])}; rr = {c: v for c, v in rr.items() if v}
                a = {}
                for _ in range(10000):
                    hs = [c for c in rr if c < n and role(c) == 'H' and c in s.born0]
                    if not hs: break
                    g = max(hs, key=lambda c: (c not in Zh, c))     # pre-cancelled helpers' Zh terms show up after: take leaves first
                    k = rr[g]; a[g] = a.get(g, 0) + k; addf(rr, V0[g], -k)
                if rr: fail.append((y, {c: str(v) for c, v in list(rr.items())[:4]}, len(rr)))
                zy += [['ADD', y, g, str(-k), s.Z, None] for g, k in sorted(a.items()) if k]
            if fail: raise SystemExit('PUREX: Y residue not junk-only %s' % fail[:4])
            prog = zh + zy + body + f9
            F, _ = replay(prog, n, no)
            change = False; xfail = []; todo = {}
            for r in range(n):
                if role(r) == 'Y': continue
                rr = {c: F[r].get(c, 0) - s.req[r].get(c, 0) for c in set(F[r]) | set(s.req[r])}; rr = {c: v for c, v in rr.items() if v}
                if not rr: continue
                if r in E:
                    if any(role(c) == 'X' for c in rr): xfail.append((r, 'ender x-residue'))
                    z0 = {c: v for c, v in rr.items() if role(c) != 'X'}
                else:
                    z0 = {c: v for c, v in rr.items() if c in E or role(c) in ('Y', 'O')}
                    fx = {c: v for c, v in rr.items() if c not in z0}
                    if fx: todo[r] = fx
                if z0:
                    if r not in s.born0: xfail.append((r, 'needs dim-0 precancel, not born at 0', list(z0)[:4])); continue
                    if any(c not in s.born0 for c in z0): xfail.append((r, 'precancel symbol not dim-0', [c for c in z0 if c not in s.born0][:4])); continue
                    for c, v in z0.items():
                        Zh[r][c] = Zh[r].get(c, 0) - v
                        if not Zh[r][c]: del Zh[r][c]
                    change = True
            if xfail: raise SystemExit('PUREX: %s' % xfail[:6])
            if verbose: print('iter', it, 'Zh regs', len(Zh), 'Zh ops', sum(len(v) for v in Zh.values()), 'zy', len(zy), 'F9 residue regs', len(todo), flush=True)
            if not change: break
        else: raise SystemExit('PUREX: no convergence')
        fixes = []
        while todo:
            ready = [r for r, df in todo.items() if not any(c in todo for c in df)]
            if not ready: raise SystemExit('PUREX: cyclic F9 residue (%d)' % len(todo))
            for r in ready:
                fixes += [['ADD', r, c, str(-v), s.F9, None] for c, v in sorted(todo[r].items())]; del todo[r]
        ops = zh + zy + body + f9 + fixes
        bad = [o for o in ops if o[0] == 'ADD' and not dy(o[3])]
        if bad: raise SystemExit('PUREX: non-dyadic %s' % bad[:4])
        dag = dict(s.d); dag['ops'] = ops; dag['regs'] = {k: list(v) for k, v in s.d['regs'].items()}
        for h, e in E.items(): dag['regs'][str(h)][2] = e['f']
        w2, rep = s.D.realise(dag, schedule='lazy', verify=True)
        return w2, rep, dict(zh=len(zh), zy=len(zy), fixes=len(fixes), f9=len(f9), body=len(body))

    def order_zh(s, Zh):
        """ops r += c*src at dim 0, every src still at its pure initial value: r must come before src's own ops"""
        regs = [r for r in Zh if Zh[r]]; srcs = collections.defaultdict(set)
        for r in regs:
            for c in Zh[r]: srcs[r].add(c)
        indeg = {r: 0 for r in regs}
        # edge r -> c (r first) when c has its own Zh
        for r in regs:
            for c in srcs[r]:
                if c in indeg: indeg[c] += 1
        order = []; ready = sorted(r for r in regs if indeg[r] == 0)
        while ready:
            r = ready.pop(); order.append(r)
            for c in srcs[r]:
                if c in indeg:
                    indeg[c] -= 1
                    if indeg[c] == 0: ready.append(c)
        if len(order) != len(regs): return None
        return [['ADD', r, c, str(v), s.Z, None] for r in order for c, v in sorted(Zh[r].items())]

def main():
    os.environ['TK_FREE_BOUNDS'] = '1'
    a = sys.argv[1:]; inp, out = a[0], a[1]
    maxn = int(a[a.index('--max') + 1]) if '--max' in a else None
    import kernel2net as KN, incr
    from tkcommon import profile_of
    w = json.load(gzip.open(inp)); c = Ctx(w)
    dims = set(int(x) for x in a[a.index('--dims') + 1].split(',')) if '--dims' in a else None
    en = c.census(maxn=maxn, xstops='--xstops' in a, dims=dims)
    print('enders', len(en), collections.Counter(c.dim[e['f']] for e in en), flush=True)
    w2, rep, info = c.build(en)
    print(info, 'undelivered', rep['undelivered'][:3], 'value_errors', len(rep['value_errors']))
    vp = dict(w.get('verifier_profile') or {}); w2['verifier_profile'] = vp
    print('R0', {k: round(v, 1) for k, v in KN.r0(w2)[0].items()}, round(KN.r0(w2)[1], 1), 'events', len(w2['program']))
    iw = incr.IncrWord(w2, profile=profile_of(w)[0])
    print('legal', iw.legal_all, 'viol', len(iw.viol), iw.viol[:3], 'kappa %.13f' % iw.kappa, flush=True)
    c.D.save(w2, out); print('wrote', out)

if __name__ == '__main__': sys.exit(main())
