#!/usr/bin/env python3
"""Independent check of #4464: stage-zero commutation and the forced translation, all 112 ports.

For a in F_2^9, T_a e_x = e_(x xor a) and C_a = ((1+i)I + (1-i)T_a)/2, with Fourier character i^(a.xi mod 2).
D0 = F9 Q^-1 with F9 = prod_j C_(2^j), Q = C_q. For the recorded complement B = (b_1..b_8) of q and translation t:
  (1) {q, b_1..b_8} is an orthonormal basis of F_2^9, so M = [q; B] is orthogonal and every column count c_i is odd;
  (2) the character identity |xi| - q.xi == sum_j b_j.xi + 2 t.xi (mod 4) holds for all 512 xi, i.e. D0 = T_t G_B;
  (3) closed form: evaluating (2) at xi = e_i forces t_i = [c_i == 3 (mod 4)]; this equals the recorded
      translation_after at every port (so the translation is determined by q and B, never optional);
  (4) [D0, Q] = 0 by an exact XOR convolution in Q(i) (kernels as dicts of Gaussian rationals);
  (5) port-0 witness: (D0 - G_B)[0, 0] = -1/16 by Fourier inversion;
  (6) the same closed form (with q prepended when a frame meets the nine port bits) reproduces translation_after for
      every one of the 2,016 nonempty recorded idle normalizations (224 empty ones are skipped).
Independent code reading the pinned DATA-PHASES.json only. Ryanson Jonathan with Claude Code (Claude Opus 5.5)
assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PHASES = "research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json"
N = 512
I4 = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # i^k as (re, im)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def dot(a, b):
    return bin(a & b).count("1") & 1


def kernel_from_char(char):
    """char[xi] in Z/4 -> exact kernel K[x] = (1/512) sum_xi i^char(xi) (-1)^(xi.x), as (F re, F im)"""
    K = {}
    for x in range(N):
        re = im = 0
        for xi in range(N):
            s = -1 if dot(xi, x) else 1
            a, b = I4[char[xi] % 4]
            re += s * a
            im += s * b
        if re or im:
            K[x] = (F(re, N), F(im, N))
    return K


def conv(A, B):
    out = {}
    for x, (ar, ai) in A.items():
        for y, (br, bi) in B.items():
            z = x ^ y
            r, i = out.get(z, (0, 0))
            out[z] = (r + ar * br - ai * bi, i + ar * bi + ai * br)
    return {k: v for k, v in out.items() if v != (0, 0)}


def main():
    for row in json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"], row["path"])
    recipes = sorted(json.loads((ROOT / PHASES).read_text(encoding="utf-8"))["recipes"], key=lambda r: r["port"])
    need([r["port"] for r in recipes] == list(range(112)), "112 ports")
    qw, tw, forced_equal = Counter(), Counter(), 0
    for rec in recipes:
        q = rec["q"]
        child = rec["idle_children"][0]
        B, t = child["orthogonal_axes"][:8], child["translation_after"]
        need(child["orthogonal_axes"][8:] == [1 << i for i in range(9, 17)], "remaining axes are D1's fresh axes")
        rows = [q] + B
        need(all(0 < r < N for r in rows) and 0 <= t < N, "nine-bit support")
        need(all(dot(a, b) == int(i == j) for i, a in enumerate(rows) for j, b in enumerate(rows)), "(1) orthonormal")
        c = [sum(r >> i & 1 for r in rows) for i in range(9)]
        need(all(ci % 2 == 1 for ci in c), "(1) odd column counts")
        forced = sum(1 << i for i in range(9) if c[i] % 4 == 3)
        need(forced == t, f"(3) port {rec['port']}: recorded translation is the forced one")
        forced_equal += 1
        need(t != 0, "translation nonzero")
        for xi in range(N):
            lhs = (bin(xi).count("1") - dot(q, xi)) % 4
            rhs = (sum(dot(b, xi) for b in B) + 2 * dot(t, xi)) % 4
            need(lhs == rhs, "(2) character identity")
            if dot(t, xi):
                need(lhs != sum(dot(b, xi) for b in B) % 4, "dropping t changes this character")
        qw[bin(q).count("1")] += 1
        tw[bin(t).count("1")] += 1
    all_idle = 0
    for rec in recipes:
        for ch in rec["idle_children"]:
            ax = ch["orthogonal_axes"]
            if not ax:
                continue
            rows = ([rec["q"]] if any(a & (N - 1) for a in ax) else []) + ax
            need(all(dot(a, b) == int(i == j) for i, a in enumerate(rows) for j, b in enumerate(rows)), "(6) orthonormal")
            width = max(x.bit_length() for x in rows)
            cnt = [sum(x >> i & 1 for x in rows) for i in range(width)]
            need(sum(1 << i for i in range(width) if cnt[i] % 4 == 3) == ch["translation_after"], "(6) forced translation")
            all_idle += 1
    need(all_idle == 2016, "(6) all 2,016 nonempty idle normalizations")
    need(qw == Counter({3: 77, 7: 35}) and tw == Counter({4: 77, 8: 35}), "weight profiles")
    # (4), (5) exact kernels at port 0 and at the first weight-7 port
    witness = None
    for rec in (recipes[0], next(r for r in recipes if bin(r["q"]).count("1") == 7)):
        q, B = rec["q"], rec["idle_children"][0]["orthogonal_axes"][:8]
        t = rec["idle_children"][0]["translation_after"]
        D0 = kernel_from_char([(bin(xi).count("1") - dot(q, xi)) % 4 for xi in range(N)])
        Qk = kernel_from_char([dot(q, xi) for xi in range(N)])
        GB = kernel_from_char([sum(dot(b, xi) for b in B) % 4 for xi in range(N)])
        need(conv(D0, Qk) == conv(Qk, D0), "(4) [D0, Q] = 0")
        need(len(D0) == 256 and all(r * r + i * i == F(1, 256) for r, i in D0.values()), "256 entries of modulus 1/16")
        diff = D0.get(0, (0, 0))[0] - GB.get(0, (0, 0))[0], D0.get(0, (0, 0))[1] - GB.get(0, (0, 0))[1]
        if rec["port"] == 0:
            need(diff == (F(-1, 16), 0) and t == 15 and q == 11, "(5) port-0 witness -1/16")
            witness = {"q": q, "B": B, "t": t, "entry_00_of_D0_minus_GB": str(diff[0])}
    print(json.dumps({"status": "PASS_STAGE_ZERO_FORCED_TRANSLATION", "ports": 112,
                      "forced_translation_matches_recorded": forced_equal,
                      "all_idle_normalizations_forced": all_idle, "q_weights": dict(qw),
                      "t_weights": dict(tw), "port0_witness": witness, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
