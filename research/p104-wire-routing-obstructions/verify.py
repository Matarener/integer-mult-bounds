#!/usr/bin/env python3
"""Verifier for p104-wire-routing-obstructions (standard library only).

Checks, on the 104 P104 ports pinned in research/p104-carrier-code-uniqueness/e8/ports.json:
  V1  ports are odd-weight vectors of F_2^9; their E8 root lines r(q) (A8 coordinates) have norm 2; ports conflict
      (<q,q'> = 1) exactly when the roots are orthogonal, and |r.r'| = 1 on every non-conflicting pair;
  V2  sign lemma: for non-conflicting k, i and every common non-conflicting reader j, G_jk*G_ji = G_ki unless
      r_j = +-(r_k - G_ki r_i) (the third root of their A2); counts of pairs whose third root is a port;
  V3  triangle lemma: for pairwise non-conflicting k, m, i, G_km*G_mi*G_ik = -1 iff r_i = G_ki r_k + G_mi r_m;
  V4  cover lemma: |P(Q_j cap Q_a)| <= 24, and P(Q_j cap Q_a) u P(Q_j cap Q_b) = P(Q_j) iff {j, a, b} is an A2 triangle;
  V5  capacity: every 7-dim frame Q_x cap Q_y (x, y non-conflicting) with 24 ports has at most 16 ports in any 6-dim subframe;
  V6  two-source data: on each 24-port frame P(Q_x cap Q_y), the ratio G_yi/G_xi takes one value on 23 ports and the
      other on exactly one port, the third vertex of the triangle;
  controls: a perturbed port list and a sign-flipped Gram entry must be rejected;
  RESULT.json must equal the recomputed counts.
Apache-2.0.  Prepared for Matarener with Claude (Anthropic), via Claude Code.
"""
import json, sys, hashlib
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PORTS = ROOT / "research/p104-carrier-code-uniqueness/e8/ports.json"
PORTS_SHA = "ba6a0b9cf76b7cccc1ce8b3d1aa78a4aa329b34d45aded694648f0cf43fc9fce"


def fail(msg):
    print("FAIL:", msg); sys.exit(1)


def dot2(a, b):
    return bin(a & b).count("1") & 1


def root(q):
    ones = [b for b in range(9) if q >> b & 1]
    if len(ones) == 7:
        z = [b for b in range(9) if not q >> b & 1]
        r = [F(0)] * 9; r[z[0]] = F(1); r[z[1]] = F(-1); return r
    if len(ones) == 3:
        return [F(2, 3) if b in ones else F(-1, 3) for b in range(9)]
    raise ValueError("port of weight %d" % len(ones))


def ip(a, b):
    return sum(x * y for x, y in zip(a, b))


def analyse(P, G=None):
    N = len(P)
    if N != 104 or len(set(P)) != 104 or not all(bin(q).count("1") & 1 for q in P):
        raise ValueError("V1 port list")
    R = [root(q) for q in P]
    if G is None:
        G = [[ip(R[i], R[j]) for j in range(N)] for i in range(N)]
    if not all(G[i][i] == 2 for i in range(N)):
        raise ValueError("V1 norms")
    for i in range(N):
        for j in range(N):
            if i != j and ((dot2(P[i], P[j]) == 1) != (G[i][j] == 0) or (G[i][j] != 0 and abs(G[i][j]) != 1)):
                raise ValueError("V1 conflict <=> orthogonal")
    orth = lambda a, b: a != b and not dot2(P[a], P[b])
    line = {}
    for m, r in enumerate(R):
        line[tuple(r)] = m; line[tuple(-x for x in r)] = m
    res = {}
    # V2
    pairs = third_port = third_missing = 0
    for k in range(N):
        for i in range(N):
            if not orth(k, i): continue
            pairs += 1
            t = tuple(a - G[k][i] * b for a, b in zip(R[k], R[i]))
            if ip(t, t) != 2: raise ValueError("V2 third root norm")
            tj = line.get(t)
            if tj is None: third_missing += 1
            else: third_port += 1
            for j in range(N):
                if j in (k, i) or not (orth(j, k) and orth(j, i)): continue
                if (G[j][k] * G[j][i] != G[k][i]) != (j == tj):
                    raise ValueError("V2 sign lemma at %d %d %d" % (k, i, j))
    res["V2_ordered_pairs"] = pairs; res["V2_third_root_is_port"] = third_port; res["V2_third_root_missing_line"] = third_missing
    # V3
    tri = a2 = 0; triangles = set()
    for k in range(N):
        for m in range(k + 1, N):
            if not orth(k, m): continue
            for i in range(m + 1, N):
                if not (orth(k, i) and orth(m, i)): continue
                tri += 1
                prod = G[k][m] * G[m][i] * G[i][k]
                comb = [G[k][i] * a + G[m][i] * b for a, b in zip(R[k], R[m])]
                if (prod == -1) != (comb == R[i]): raise ValueError("V3 triangle lemma")
                if prod == -1: a2 += 1; triangles.add(frozenset((k, m, i)))
    res["V3_triples"] = tri; res["V3_A2_triangles"] = a2
    # V4
    Qp = [frozenset(i for i in range(N) if orth(i, j)) for j in range(N)]
    if any(len(q) != 48 for q in Qp): raise ValueError("V4 |P(Q_j)| != 48")
    maxint = 0; cover = 0
    for j in range(N):
        H = {a: Qp[j] & Qp[a] for a in range(N) if a != j}
        maxint = max(maxint, max(len(s) for s in H.values()))
        for a in H:
            for b in H:
                if a < b and (H[a] | H[b]) == Qp[j]:
                    cover += 1
                    if frozenset((j, a, b)) not in triangles: raise ValueError("V4 cover pair not an A2 triangle")
        for T in triangles:
            if j in T:
                a, b = sorted(T - {j})
                if (H[a] | H[b]) != Qp[j]: raise ValueError("V4 triangle does not cover")
    res["V4_max_ports_in_Qj_cap_Qa"] = maxint; res["V4_unordered_cover_pairs"] = cover
    # V5, V6
    best6 = 0; frames = 0; split = {}
    for x in range(N):
        for y in range(x + 1, N):
            Fp = Qp[x] & Qp[y]
            if len(Fp) != 24 or not orth(x, y): continue
            frames += 1
            for u in range(1, 512):
                if u in (P[x], P[y], P[x] ^ P[y]): continue      # functionals vanishing on F give no hyperplane
                best6 = max(best6, sum(1 for i in Fp if not dot2(P[i], u)))
            for (s, o) in ((x, y), (y, x)):
                z = [i for i in Fp if G[s][o] * G[o][i] * G[s][i] == -1]
                ratios = {}
                for i in Fp: ratios.setdefault(F(G[o][i], G[s][i]), []).append(i)
                key = tuple(sorted(len(v) for v in ratios.values()))
                if key != (1, 23) or [v for v in ratios.values() if len(v) == 1][0] != z:
                    raise ValueError("V6 split")
                split[key] = split.get(key, 0) + 1
    if best6 > 16: raise ValueError("V5 capacity")
    res["V5_frames_with_24_ports"] = frames; res["V5_max_ports_in_6dim_subframe"] = best6
    res["V6_ordered_frames_with_23_1_split"] = sum(split.values())
    return res


def main():
    raw = PORTS.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    pins = json.loads((HERE / "SOURCES.json").read_text())
    pinned = [f["sha256"] for f in pins["files"] if f["path"].endswith("e8/ports.json")]
    if pinned != [sha]: fail("ports.json does not match its SOURCES.json pin")
    P = json.loads(raw)
    try:
        res = analyse(P)
    except ValueError as e:
        fail(str(e))
    for k, v in res.items(): print("%-40s %s" % (k, v))
    # controls
    bad = list(P); bad[0] = bad[0] ^ 3 if bin(bad[0] ^ 3).count("1") & 1 else bad[0] ^ 6
    try: analyse(bad); fail("control: perturbed port list accepted")
    except ValueError: print("control: perturbed port list rejected")
    R = [root(q) for q in P]; G = [[ip(R[i], R[j]) for j in range(104)] for i in range(104)]
    k, i = next((k, i) for k in range(104) for i in range(104) if k != i and G[k][i] == 1)
    G[k][i] = G[i][k] = -1
    try: analyse(P, G); fail("control: sign-flipped Gram accepted")
    except ValueError: print("control: sign-flipped Gram entry rejected")
    want = json.loads((HERE / "RESULT.json").read_text())
    if want != res: fail("RESULT.json differs from recomputed counts")
    print("PASS p104-wire-routing-obstructions")


if __name__ == "__main__":
    main()
