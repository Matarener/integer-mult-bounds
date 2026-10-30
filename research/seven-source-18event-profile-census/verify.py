from __future__ import annotations
import hashlib, itertools as it, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
IS_T = [0 < m < 128 and m.bit_count() <= 3 for m in range(128)]
T5 = sum(1 << m for m in range(64) if not (m & 1) and IS_T[m])
T6 = sum(1 << m for m in range(64) if IS_T[m])
T6_0 = sum(1 << m for m in range(128) if not (m & 1) and IS_T[m])
T7 = sum(1 << m for m in range(128) if IS_T[m])

def req(ok):
    if not ok: raise AssertionError()

def seen(w):
    ps, cur, sm = [0], 0, 0
    for x in w[:-1]:
        cur ^= 1 << x
        for p in ps: sm |= 1 << (cur ^ p)
        ps.append(cur)
    return sm

def enum_dbl(n, k):
    out = []
    def dfs(p, w, c, nl):
        if p == n: out.append(w[:]); return
        for l in range(1, nl):
            if c[l] < 2: c[l] += 1; w.append(l); dfs(p+1, w, c, nl); w.pop(); c[l] -= 1
        if nl <= k: c[nl] += 1; w.append(nl); dfs(p+1, w, c, nl+1); w.pop(); c[nl] -= 1
    dfs(0, [], [0]*(k+1), 1)
    return out

res = json.loads((HERE / "RESULT.json").read_text())
all12 = enum_dbl(12, 6)
w12_max = [w for w in all12 if (seen(w) & T6_0).bit_count() == 39]
req(len(all12) == 10395 and len(w12_max) == 2 and all((seen(w) & T6_0).bit_count() <= 39 for w in all12))
h61 = []
for w12 in w12_max:
    for c in it.combinations(range(18), 6):
        sc, i12 = set(c), iter(w12)
        w18 = [0 if k in sc else next(i12) for k in range(18)]
        cov = (seen(w18) & T7).bit_count()
        req(cov <= 61)
        if cov == 61: h61.append(" ".join(map(str, w18)))
req(len(h61) == 105 and hashlib.sha256(("\n".join(h61)+"\n").encode()).hexdigest() == res["canonical_62_sha256"])

w5 = [w for w in enum_dbl(10, 5) if (seen(w) & T5) == T5]
c63, ord63 = set(), 0
for w10 in w5:
    lifts = [tuple(c[k]-k for k in range(4)) for c in it.combinations(range(14), 4)
             if (seen([0 if k in set(c) else w10[k - sum(x < k for x in c)] for k in range(14)]) & T6) == T6]
    for g0 in lifts:
        for g6 in lifts:
            gopts = [[tuple(0 if p in p0 else 6 for p in range(g0.count(i)+g6.count(i)))
                      for p0 in it.combinations(range(g0.count(i)+g6.count(i)), g0.count(i))] for i in range(11)]
            for pr in it.product(*gopts):
                w18 = [x for i in range(10) for x in (*pr[i], w10[i])] + list(pr[10])
                if (seen(w18) & T7) == T7:
                    ord63 += 1
                    mp, n4, n2 = {}, 0, 2
                    for x in w18:
                        if x not in mp:
                            mp[x] = n4 if w18.count(x) == 4 else n2
                            if w18.count(x) == 4: n4 += 1
                            else: n2 += 1
                    c63.add(" ".join(str(mp[x]) for x in w18))
c63_s = sorted(c63)
req(ord63 == 108 and len(c63_s) == 54 and c63_s[1] == res["pr2397_witness"])
req(hashlib.sha256(("\n".join(c63_s)+"\n").encode()).hexdigest() == res["canonical_44_sha256"])
print(res["primary_result_marker"])
