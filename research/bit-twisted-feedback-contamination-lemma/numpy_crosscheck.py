"""numpy cross-check (pinned numpy==2.5.4): dense BFS + row-major left-multiplication MITM for 3+3,
dense five-register census for 2+3, 3+2, 4+1 (and the settled 1+4), and the contamination-charge
construction run on one greedy (first-gate) optimal unrestricted word for every five-register exit
[[T,0],[K,I]] (T=I shears included and counted separately; twisted means T != I)."""
import itertools, os, sys, time
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lemma import simulate, apply, identity


def bfs_dense(nbits, start, step, gates):
    dist = np.full(1 << nbits, 255, np.uint8); dist[start] = 0
    front = np.array([start], np.int64); d = 0
    while front.size:
        d += 1
        for g in gates:
            y = step(front, g); y = y[dist[y] == 255]; dist[y] = d
        front = np.nonzero(dist == d)[0].astype(np.int64)
    return dist


def three_plus_three():
    def step(x, g):
        k, p, q = g
        if k == 'h': return x ^ (((x >> (3 * q)) & 7) << (3 * p))
        if k == 't': return x ^ (((x >> (9 + 6 * q)) & 63) << (9 + 6 * p))
        return x ^ (((x >> (3 * q)) & 7) << (9 + 6 * p))
    gates = [('h', a, b) for a in range(3) for b in range(3) if a != b] + \
            [('t', i, j) for i in range(3) for j in range(3) if i != j] + [('r', i, a) for i in range(3) for a in range(3)]
    ident = (1 | 2 << 3 | 4 << 6) | (8 << 9) | (16 << 15) | (32 << 21)
    dist = bfs_dense(27, ident, step, gates)
    assert int((dist < 255).sum()) == 168 * 168 * 512
    idx = np.nonzero(dist < 255)[0]; ok = np.ones(idx.size, bool)
    for i in range(3): ok &= ((idx >> (9 + 6 * i + 3)) & 7) == (1 << i)
    ex = idx[ok]; dP = dist[ex].astype(np.int64)
    E = np.zeros_like(ex)
    for a in range(3): E |= ((ex >> (3 * a)) & 7) << (6 * a)
    for i in range(3): E |= ((ex >> (9 + 6 * i)) & 63) << (6 * (3 + i))
    def conj(x, p):
        y = np.zeros_like(x)
        for r in range(6):
            for k in range(6): y |= ((x >> (6 * r + k)) & 1) << (6 * p[r] + p[k])
        return y
    canon = E.copy()
    for a in itertools.permutations(range(3)):
        for b in itertools.permutations(range(3)): canon = np.minimum(canon, conj(E, a + tuple(3 + q for q in b)))
    reps, inv = np.unique(canon, return_inverse=True)
    full = [(d, s) for d in range(6) for s in range(6) if d != s]
    sph = [np.array([sum(1 << (7 * r) for r in range(6))], np.int64)]; seen = sph[0]
    for k in range(1, 5):
        y = np.unique(np.concatenate([sph[-1] ^ (((sph[-1] >> (6 * s)) & 63) << (6 * d)) for d, s in full]))
        y = y[~np.isin(y, seen, assume_unique=True)]; sph.append(y); seen = np.union1d(seen, y)
    B = np.concatenate(sph); Bd = np.concatenate([np.full(s.size, k) for k, s in enumerate(sph)])
    o = np.argsort(B); B, Bd = B[o], Bd[o]
    rd = np.full(reps.size, 9)
    for n_, M in enumerate(reps.tolist()):
        rows = [(M >> (6 * k)) & 63 for k in range(6)]
        T = np.array([np.bitwise_xor.reduce([rows[k] for k in range(6) if p >> k & 1] or [0]) for p in range(64)], np.int64)
        uM = np.zeros_like(B)
        for r in range(6): uM |= T[(B >> (6 * r)) & 63] << (6 * r)
        pos = np.searchsorted(B, uM); pos[pos >= B.size] = 0; hit = B[pos] == uM
        if hit.any(): rd[n_] = min(9, int((Bd[hit] + Bd[pos[hit]]).min()))
    dF = np.minimum(rd[inv], dP)
    tw = (ex & 511) != (1 | 2 << 3 | 4 << 6)
    assert (rd[inv] >= dF).all() and int(dP.max()) == 9
    return dict(exits=int(ex.size), classes=int(reps.size), twisted=int(tw.sum()),
                strict_advantage=int((dF[tw] < dP[tw]).sum()), t_eq_i_advantage=int((dF[~tw] < dP[~tw]).sum()),
                dP_hist=np.bincount(dP[tw]).tolist(), dfull_hist=np.bincount(dF[tw]).tolist(),
                sphere_sizes=[int(s.size) for s in sph])


def five_registers():
    n = 5
    step = lambda x, g: x ^ (((x >> (n * g[1])) & 31) << (n * g[0]))
    full = [(d, s) for d in range(n) for s in range(n) if d != s]
    ident = sum(1 << (n * i + i) for i in range(n))
    Df = bfs_dense(25, ident, step, full)
    assert int((Df < 255).sum()) == 9999360
    def greedy(xs):  # one optimal unrestricted word per element, by vectorized greedy (first-gate) descent on Df
        cur = xs.copy(); words = [[] for _ in range(xs.size)]
        while True:
            live = np.nonzero(Df[cur] > 0)[0]
            if not live.size: break
            choice = np.full(live.size, -1)
            for gi, g in enumerate(full):
                nb = step(cur[live], g)
                take = (choice < 0) & (Df[nb] == Df[cur[live]] - 1)
                choice[take] = gi
            assert (choice >= 0).all()
            for li, gi in zip(live.tolist(), choice.tolist()): words[li].append(full[gi])
            cur[live] = np.array([step(np.array([c]), full[g])[0] for c, g in zip(cur[live].tolist(), choice.tolist())])
        return [wd[::-1] for wd in words]  # descent g1..gk from M to I: M = g1...gk, apply gk first

    def lemma_run(x, w, H, Y, Dr):
        rows = [(x >> (n * r)) & 31 for r in range(n)]
        assert apply(w, identity(n)) == rows
        out, led = simulate(w, H, Y)
        assert apply(out, identity(n)) == rows and int(Dr[x]) <= len(out)
        return out, led

    res = {}
    for H in range(1, n):
        Y = n - H
        Dr = bfs_dense(25, ident, step, [(d, s) for d, s in full if not (d < H <= s)])
        idx = np.nonzero(Dr < 255)[0]; ok = np.ones(idx.size, bool)
        for j in range(Y): ok &= (((idx >> (n * (H + j))) & 31) >> H) == (1 << j)
        tg = idx[ok]
        ti = np.ones(tg.size, bool)
        for r in range(H): ti &= ((tg >> (n * r)) & 31) == (1 << r)  # helper block T = I (an untwisted shear)
        words = greedy(tg)
        lem = dict(words=0, non_clean=0, singular=0, swaps=0, certified_by_lemma=0, max_charge_minus_fv=0)
        for x, w in zip(tg.tolist(), words):
            out, led = lemma_run(x, w, H, Y, Dr)
            lem['words'] += 1; lem['non_clean'] += led['contaminated_reads'] + led['singular_reads'] > 0  # contaminated or singular
            lem['singular'] += led['singular_reads'] > 0; lem['swaps'] += led['relabel_swaps'] > 0
            lem['certified_by_lemma'] += led['charge'] <= led['virtual_feedback']
            lem['max_charge_minus_fv'] = max(lem['max_charge_minus_fv'], led['charge'] - led['virtual_feedback'])
        # positive control: feedback DOES help at some non-exit elements of P (target block D != I);
        # Corollary 2 must then hold: f_v >= 1 and charge >= f_v + 1 on a minimum unrestricted word
        gap = Dr[idx].astype(int) - Df[idx].astype(int)
        pa = idx[gap > 0]
        assert not np.isin(pa, tg).any() and (gap[gap > 0] == 1).all()
        for x, w in zip(pa.tolist(), greedy(pa)):
            out, led = lemma_run(x, w, H, Y, Dr)
            assert len(w) == int(Dr[x]) - 1 and led['virtual_feedback'] >= 1
            assert led['contaminated_reads'] + led['singular_reads'] > 0 and led['charge'] >= led['virtual_feedback'] + 1
        adv = Dr[tg].astype(int) - Df[tg].astype(int)
        tw = tg[~ti]
        res[f"{H}+{Y}"] = dict(exits=int(tg.size), strict_advantage=int((adv > 0).sum()),
                               max_min=int(Dr[tg].max()), dP_hist=np.bincount(Dr[tg]).tolist(), lemma=lem,
                               t_eq_i=int(ti.sum()), twisted=int(tw.size),
                               twisted_max_min=int(Dr[tw].max()) if tw.size else 0,
                               nonexit_feedback_advantage=int(pa.size))
    return res


if __name__ == "__main__":
    t = time.time()
    r33 = three_plus_three()
    print("3+3", r33, round(time.time() - t, 1), flush=True)
    assert (r33["exits"], r33["classes"], r33["twisted"], r33["strict_advantage"], r33["t_eq_i_advantage"]) == (86016, 3478, 85504, 0, 0)
    assert r33["dP_hist"] == r33["dfull_hist"] == [0, 6, 96, 744, 3594, 11463, 23948, 29259, 15438, 956]
    r5 = five_registers()
    print("five", r5, round(time.time() - t, 1), flush=True)
    assert {k: (v["exits"], v["strict_advantage"], v["max_min"]) for k, v in r5.items()} == {
        "1+4": (16, 0, 4), "2+3": (384, 0, 6), "3+2": (10752, 0, 8), "4+1": (322560, 0, 10)}
    assert {k: (v["t_eq_i"], v["twisted"], v["twisted_max_min"]) for k, v in r5.items()} == {
        "1+4": (16, 0, 0), "2+3": (64, 320, 6), "3+2": (64, 10688, 8), "4+1": (16, 322544, 10)}
    # greedy words with a non-clean read: only 35 in 4+1, each with charge = f_v + 1 (lemma not tight there)
    assert {k: (v["lemma"]["non_clean"], v["lemma"]["words"] - v["lemma"]["certified_by_lemma"],
                v["lemma"]["max_charge_minus_fv"]) for k, v in r5.items()} == {
        "1+4": (0, 0, 0), "2+3": (0, 0, 0), "3+2": (0, 0, 0), "4+1": (35, 35, 1)}
    # feedback gains exactly 1 at 60 + 60 non-exit elements of P_{2,3}, P_{3,2} (D != I): the exit condition D = I is load-bearing
    assert {k: v["nonexit_feedback_advantage"] for k, v in r5.items()} == {"1+4": 0, "2+3": 60, "3+2": 60, "4+1": 0}
    words = sum(v["lemma"]["words"] for v in r5.values())
    twisted5 = sum(v["twisted"] for v in r5.values())
    assert (words, twisted5) == (333712, 333552)
    print(f"PASS_TWISTED_FEEDBACK_NUMPY_CROSSCHECK twisted33={r33['twisted']} classes={r33['classes']} "
          f"five_register_exits={words} twisted5={twisted5} strict_feedback_advantage=0 lemma_words={words} "
          f"nonexit_advantage_controls=120")
