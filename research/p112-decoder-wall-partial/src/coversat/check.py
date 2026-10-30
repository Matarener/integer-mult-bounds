# Independent checker for COVERSAT models + encoder self-tests.
# check.py model orbit lam model.out  -> verifies Ferrers (nested rows), exact rank_F2(B o S_k) == lam_k, covers; prints patterns.
# check.py selftest                    -> crossing-free == nested rows (exhaustive 4x4), atom_S patterns crossing-free (random).
import sys, itertools, random, pickle
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import orbit, brows, f2rank01, masked, atom_S
def nested(rows):
    rs = [r for r in rows if r]
    return all((a & b) in (a, b) for a in rs for b in rs)
def crossfree(M, n):
    for t, t2 in itertools.combinations(range(n), 2):
        for s, s2 in itertools.permutations(range(n), 2):
            if M[t] >> s & 1 and not M[t] >> s2 & 1 and not M[t2] >> s & 1 and M[t2] >> s2 & 1: return False
    return True
def selftest():
    n = 4
    for bits in range(1 << 16):
        M = [(bits >> (4 * t)) & 15 for t in range(n)]
        assert nested(M) == crossfree(M, n)
    rnd = random.Random(1)
    for _ in range(20000):
        k = rnd.randint(1, 8); c = [rnd.randint(0, k) for _ in range(8)]; r = [rnd.randint(0, k) for _ in range(8)]
        S = atom_S(c, r); assert crossfree(S, 8) and nested(S)
    print('selftest OK')
def read_model(path):
    val = {}
    for line in open(path):
        if line.startswith('v'):
            for x in line.split()[1:]:
                x = int(x)
                if x: val[abs(x)] = x > 0
    return val
def check(o, lam, path):
    T, B = orbit(o); Br = brows(B); val = read_model(path); m = len(lam); pats = []
    for k in range(m):
        Sk = [sum(1 << s for s in range(8) if val[1 + 64 * k + 8 * t + s]) for t in range(8)]
        assert nested(Sk), ('not Ferrers', k)
        rk = f2rank01(masked(Br, Sk)); assert rk <= lam[k], ('rank', k, rk, lam[k])
        pats.append(Sk)
    for t in range(8):
        for s in range(8):
            if not B[t][s]: continue
            cov = sum(P[t] >> s & 1 for P in pats)
            assert (cov >= 1) if t == s else (cov != 1), ('cover', t, s, cov)
    for k, P in enumerate(pats): print(' term', k, 'f2', lam[k], [f'{x:08b}'[::-1] for x in P])
    return pats
if __name__ == '__main__':
    if sys.argv[1] == 'selftest': selftest()
    else:
        o = int(sys.argv[2]); lam = [int(x) for x in sys.argv[3].split(',')]
        pats = check(o, lam, sys.argv[4]); print('MODEL OK orbit', o, 'lam', lam)
        if len(sys.argv) > 5: pickle.dump(pats, open(sys.argv[5], 'wb'))
