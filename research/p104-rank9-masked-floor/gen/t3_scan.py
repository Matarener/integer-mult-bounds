"""Scan all types: line certificates (rank 7 on O_v cap Z, pivot where rho_v != 0) and pair certificates (rank 6 on
O_v cap O_w cap Z, two pivots with nonzero 2x2 minor of rho_v, rho_w) for the lines outside the reduced Z."""
import sys, json, time
sys.path.insert(0, '.')
from p104lib import ORTH, N as NL
from rank_cert import cert, rootv
DROP = {2: 78, 28: 82, 75: 71, 102: 70, 118: 70, 123: 70, 229: 35}
reps = [r for r in json.load(open('orbitsW.json')) if r['frame']]
T0 = time.time()
out = {}
for k in range(len(reps)):
    m = int(reps[k]['mask']); Z = [i for i in range(NL) if m >> i & 1]
    if k in DROP: Z = [i for i in Z if i != DROP[k]]
    Zs = set(Z); O = [v for v in range(NL) if v not in Zs]
    badl = []; badp = []; maxX = 0; maxD = 0
    for v in O:
        rv = rootv(v); k0 = next(i for i in range(9) if rv[i])
        c = cert([x for x in Z if ORTH[x][v]], [k0])
        if c is None: badl.append(v)
        else: maxX = max(maxX, len(c[0])); maxD = max(maxD, abs(c[3]))
    for a in range(len(O)):
        for b in range(a + 1, len(O)):
            v, w = O[a], O[b]; rv, rw = rootv(v), rootv(w)
            pv = next(((i, j) for i in range(9) for j in range(i + 1, 9) if rv[i] * rw[j] - rv[j] * rw[i]), None)
            c = cert([x for x in Z if ORTH[x][v] and ORTH[x][w]], list(pv))
            if c is None: badp.append((v, w))
            else: maxD = max(maxD, abs(c[3]))
    out[k] = {'O': len(O), 'badl': badl, 'badp': badp}
    print('[%6.1fs] type %d |Z| %d |O| %d bad lines %s bad pairs %d maxX %d maxD %d' % (time.time() - T0, k, len(Z), len(O), badl, len(badp), maxX, maxD), flush=True)
json.dump(out, open(sys.argv[1], 'w'))
