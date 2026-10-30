"""RETAINOP retain_test.py (~3 s, venv python -B, no env at import): R-RETAIN reproduces swarm PR #6167 from r245g.
1. census on r245g finds the site (s=772, f=737 -> g=595, reader 451 with one stranded operand), model save 1.116 (jl terms)
2. apply(mv='ra') gives a program EQUAL to FRONTIER/W6167.json.gz, LEGAL, exact kappa .003128652015904
3. mv='late' is also legal with the same kappa; W6167 itself has no positive site (fixed point); `rebuild --post retain` pass is wired
usage: tests/retain_test.py"""
import sys, os, gzip, json
W = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')); TK = W
sys.path[:0] = [TK, TK + '/alignbuild']
import retain

def main():
    fails = 0
    def ok(c, m):
        nonlocal fails; print(('PASS ' if c else 'FAIL ') + m, flush=True); fails += (not c)
    a = json.load(gzip.open(W + '/words/6144.json.gz')); b = json.load(gzip.open(W + '/words/6167.json.gz'))
    ss = [x for x in retain.sites(a) if x['save'] > 1e-9]
    S = ss[0] if ss else None
    ok(S and (S['s'], S['f'], S['g']) == (772, 737, 595) and abs(S['save'] - 1.1157) < 1e-3 and [(R['r'], len(R['stranded'])) for R in S['readers']] == [(451, 1)], 'census: 772 f737->g595, reader 451 + 1 retained operand, save 1.116')
    w2 = retain.apply(a, S, 'ra')
    ok(w2 is not None and w2['program'] == b['program'], 'apply == W6167 program (bit-identical)')
    lg, k, v = retain.judge(w2)
    ok(lg and abs(k - 0.003128652015904) < 1e-14, 'LEGAL, exact kappa .003128652015904 (%.15f)' % k)
    w3 = retain.apply(a, S, 'late'); lg3, k3, _ = retain.judge(w3)
    ok(lg3 and abs(k3 - k) < 1e-15, 'mv=late legal, same kappa')
    ok(not [x for x in retain.sites(b) if x['save'] > 1e-9], 'W6167: no positive site left')
    import rebuild
    ok(callable(rebuild.post) and 'retain' in open(TK + '/rebuild.py').read(), 'rebuild --post retain wired')
    print('ALL PASS' if not fails else '%d FAILED' % fails); return 1 if fails else 0

if __name__ == '__main__': sys.exit(main())
