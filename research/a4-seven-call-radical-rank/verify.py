#!/usr/bin/env python3
"""Replay the A4 four-role exact minimum: radical-rank lemma, controls and two exact joins.

Standard library only.  Needs a C compiler (cc or gcc) with POSIX threads for the joins.
Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5).  Apache-2.0.
"""

from __future__ import annotations

import itertools
import json
import random
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PRED = ROOT / "research/a4-commutator-four-role-seed-dcbf/RESULT.json"

# ---------------------------------------------------------------- group A4 and F2[A4]
PERMS = sorted(p for p in itertools.permutations(range(4))
               if sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4)) % 2 == 0)
IDX = {p: k for k, p in enumerate(PERMS)}
ONE = IDX[(0, 1, 2, 3)]
MUL = [[IDX[tuple(p[q[t]] for t in range(4))] for q in PERMS] for p in PERMS]  # (p o q)(t)=p(q(t))
INV = [next(j for j in range(12) if MUL[i][j] == ONE) for i in range(12)]
A, B = IDX[(1, 2, 0, 3)], IDX[(1, 3, 2, 0)]          # a=(123), b=(124)
D = MUL[A][B]                                          # d = ab = (13)(24)
C = MUL[MUL[A][B]][MUL[INV[A]][INV[B]]]               # c = a b a^-1 b^-1 = (12)(34)
E = MUL[B][A]                                          # e = ba = (14)(23)
V4 = [ONE, C, D, E]
COSET = {MUL[p][v]: i for i, p in enumerate([ONE, A, MUL[A][A]]) for v in V4}  # k in a^i V4


def amul(x: int, y: int) -> int:
    """Product in F2[A4]; elements are 12-bit masks over PERMS."""
    out = 0
    for i in range(12):
        if x >> i & 1:
            for j in range(12):
                if y >> j & 1:
                    out ^= 1 << MUL[i][j]
    return out


def g(k: int) -> int:
    return 1 << k


def pi(x: int) -> int:
    """Image in F2[A4/V4] = F2[C3], as a 3-bit mask over the cosets V4, aV4, a^2V4."""
    out = 0
    for k in range(12):
        if x >> k & 1:
            out ^= 1 << COSET[k]
    return out


def mat_id() -> list[list[int]]:
    return [[g(ONE) if i == j else 0 for j in range(4)] for i in range(4)]


def mat_mul(X, Y):
    out = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            acc = 0
            for k in range(4):
                if X[i][k] and Y[k][j]:
                    acc ^= amul(X[i][k], Y[k][j])
            out[i][j] = acc
    return out


# paid factors: id = 120*gi + n, (x, y) x-major, y ascending, popcount(x&y) odd
PAIRS = [(x, y) for x in range(1, 16) for y in range(1, 16) if bin(x & y).count("1") % 2]
assert len(PAIRS) == 120


def factor_matrix(x: int, y: int, label: int):
    """D_N(label) = I + ([label]+[1]) x y^T."""
    s = g(label) ^ g(ONE)
    M = mat_id()
    for i in range(4):
        for j in range(4):
            if x >> i & 1 and y >> j & 1:
                M[i][j] ^= s
    return M


FACTORS = [factor_matrix(x, y, A if gi == 0 else B) for gi in range(2) for (x, y) in PAIRS]


def word_product(word):
    M = mat_id()
    for f in word:
        M = mat_mul(M, FACTORS[f])
    return M


def target(labels):
    T = [[0] * 4 for _ in range(4)]
    for i, lab in enumerate(labels):
        T[i][i] = g(lab)
    return T


TARGET = target([A, B, C, D])
THREE = target([A, B, C, ONE])
DIRECT = [0, 128, 24, 144, 144, 24, 56, 176]


def regular_replay(M, T) -> int:
    """Apply both matrices to all 48 role/address basis inputs e_j [h]; count agreements."""
    ok = 0
    for j in range(4):
        for h in range(12):
            if all(amul(M[i][j], g(h)) == amul(T[i][j], g(h)) for i in range(4)):
                ok += 1
    return ok


# ---------------------------------------------------------------- F4 linear algebra
# F4 = {0,1,w,w^2} coded 0,1,2,3; addition is XOR.
F4MUL = [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 3, 1], [0, 3, 1, 2]]
F4INV = {1: 1, 2: 3, 3: 2}
W = 2
WPOW = [1, 2, 3]


def f4_rank(M) -> int:
    M = [row[:] for row in M]
    rank = 0
    for col in range(len(M[0])):
        piv = next((r for r in range(rank, len(M)) if M[r][col]), None)
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        inv = F4INV[M[rank][col]]
        M[rank] = [F4MUL[inv][v] for v in M[rank]]
        for r in range(len(M)):
            if r != rank and M[r][col]:
                fac = M[r][col]
                M[r] = [v ^ F4MUL[fac][w] for v, w in zip(M[r], M[rank])]
        rank += 1
    return rank


def f4_matmul(X, Y):
    out = [[0] * len(Y[0]) for _ in range(len(X))]
    for i in range(len(X)):
        for k in range(len(Y)):
            if X[i][k]:
                for j in range(len(Y[0])):
                    out[i][j] ^= F4MUL[X[i][k]][Y[k][j]]
    return out


def f4_inverse(M):
    n = len(M)
    aug = [row[:] + [1 if i == j else 0 for j in range(n)] for i, row in enumerate(M)]
    for col in range(n):
        piv = next(r for r in range(col, n) if aug[r][col])
        aug[col], aug[piv] = aug[piv], aug[col]
        inv = F4INV[aug[col][col]]
        aug[col] = [F4MUL[inv][v] for v in aug[col]]
        for r in range(n):
            if r != col and aug[r][col]:
                fac = aug[r][col]
                aug[r] = [v ^ F4MUL[fac][w] for v, w in zip(aug[r], aug[col])]
    return [row[n:] for row in aug]


# ---------------------------------------------------------------- the radical-rank lemma
class Base:
    """Lemma data for a base generator s in {a, b}; the other generator is s^2 v, v in V4."""

    def __init__(self, s: int, other: int):
        self.s = s
        self.powers = [ONE, s, MUL[s][s]]
        self.v_other = MUL[INV[MUL[s][s]]][other]
        assert self.v_other in V4 and self.v_other != ONE

        def conj(v):
            return MUL[MUL[INV[s]][v]][s]

        # mu: V4 -> F4 is F2-linear and conjugation-equivariant: mu(s^-1 v s) = w mu(v)
        self.mu = {ONE: 0, C: 1, conj(C): W, conj(conj(C)): F4MUL[W][W]}
        assert sorted(self.mu) == sorted(V4)
        self.vpart = {}
        for p in self.powers:
            for v in V4:
                self.vpart[MUL[p][v]] = v                 # g = s^i v
        assert len(self.vpart) == 12

    def phi(self, x: int) -> int:
        out = 0
        for k in range(12):
            if x >> k & 1:
                out ^= self.mu[self.vpart[k]]
        return out

    def aug(self, r: int) -> int:                         # trivial character of F2[<s>]
        return sum(r >> p & 1 for p in self.powers) % 2

    def psi(self, r: int) -> int:                         # character s -> w of F2[<s>]
        out = 0
        for i, p in enumerate(self.powers):
            if r >> p & 1:
                out ^= WPOW[i]
        return out

    def in_sub(self, r: int) -> bool:
        return all(not (r >> k & 1) or k in self.powers for k in range(12))


def sub_inverse(word, is_other, base):
    """Inverse of the F2[<s>]-part product P1...Pn, using D_N(t)^-1 = D_N(t^-1)."""
    inv = mat_id()
    for f, o in zip(word, is_other):
        x, y = PAIRS[f % 120]
        t = MUL[base.s][base.s] if o else base.s
        inv = mat_mul(factor_matrix(x, y, INV[t]), inv)
    return inv


def lemma_checks() -> dict:
    out = {}
    J_basis = [g(MUL[p][v]) ^ g(p) for p in [ONE, A, MUL[A][A]] for v in [C, D, E]]
    J_all = {0}
    for y in J_basis:
        J_all |= {z ^ y for z in J_all}
    assert len(J_all) == 512 and all(pi(y) == 0 for y in J_all)
    assert sum(1 for x in range(4096) if pi(x) == 0) == 512          # J = ker pi exactly
    for name, s, other in (("a", A, B), ("b", B, A)):
        base = Base(s, other)
        sub = [r for r in range(1 << 12) if base.in_sub(r)]
        assert len(sub) == 8
        # (1) F2[<s>] meets J only in 0, so a lift mod J into M4(F2[<s>]) is unique
        assert [r for r in sub if pi(r) == 0] == [0]
        # (2) D_N(other) = D_N(s^2) D_N(v_other) for all 120 rank-one idempotents N
        for (x, y) in PAIRS:
            rhs = mat_mul(factor_matrix(x, y, MUL[s][s]), factor_matrix(x, y, base.v_other))
            assert factor_matrix(x, y, other) == rhs
        # (3) Phi(r y t) = aug(r) Phi(y) psi(t) on J, Phi(J^2) = 0, Phi(v+1) != 0 for v != 1
        for y in J_all:
            py = base.phi(y)
            for r in sub:
                ry = amul(r, y)
                for t in sub:
                    assert base.phi(amul(ry, t)) == F4MUL[F4MUL[base.aug(r)][py]][base.psi(t)]
        for y1 in J_basis:
            for y2 in J_basis:
                assert base.phi(amul(y1, y2)) == 0
        assert all(base.phi(g(v) ^ g(ONE)) for v in (C, D, E))
        # (4) unique lift of T mod J and the radical defect U - I = lift^-1 T - I
        def defect_rank(labels):
            lift = []
            for lab in labels:
                cands = [r for r in sub if pi(r) == pi(g(lab))]
                assert len(cands) == 1
                lift.append(cands[0])
            lift_inv = [next(r for r in sub if amul(r, l) == g(ONE)) for l in lift]
            defect = [amul(lift_inv[i], g(lab)) ^ g(ONE) for i, lab in enumerate(labels)]
            assert all(pi(x) == 0 for x in defect)
            return f4_rank([[base.phi(defect[i]) if i == j else 0 for j in range(4)] for i in range(4)])

        rank = defect_rank([A, B, C, D])
        rank3 = defect_rank([A, B, C, ONE])
        assert rank == 3 and rank3 == 2
        out[f"base_{name}"] = {
            "other_label_split": f"{'b' if name == 'a' else 'a'} = {name}^2 * {''.join(map(str, PERMS[base.v_other]))}",
            "defect_rank_target": rank, "defect_rank_three_output_control": rank3,
            "bound": f"n_{'b' if name == 'a' else 'a'} >= {rank}"}
        # (5) random words: Phi(A^-1 W - I) = sum_k aug(C_k)^-1 mu(v) N_k psi(C_k); rank <= #other
        rng = random.Random(20261019 + s)
        for _ in range(60):
            word = [rng.randrange(240) for _ in range(rng.randrange(1, 9))]
            is_other = [(f >= 120) == (name == "a") for f in word]
            parts = []
            for f, o in zip(word, is_other):
                x, y = PAIRS[f % 120]
                parts.append(factor_matrix(x, y, MUL[s][s] if o else s))
            Wm = word_product(word)
            Am = mat_id()
            for P in parts:
                Am = mat_mul(Am, P)
            assert all(base.in_sub(Am[i][j]) for i in range(4) for j in range(4))
            assert all(pi(Wm[i][j]) == pi(Am[i][j]) for i in range(4) for j in range(4))
            Ainv = sub_inverse(word, is_other, base)
            assert mat_mul(Ainv, Am) == mat_id()
            U = mat_mul(Ainv, Wm)
            lhs = [[base.phi(U[i][j] ^ (g(ONE) if i == j else 0)) for j in range(4)] for i in range(4)]
            rhs = [[0] * 4 for _ in range(4)]
            for k, (f, o) in enumerate(zip(word, is_other)):
                if not o:
                    continue
                Ck = mat_id()
                for P in parts[k + 1:]:
                    Ck = mat_mul(Ck, P)
                aug_inv = f4_inverse([[base.aug(Ck[i][j]) for j in range(4)] for i in range(4)])
                psiC = [[base.psi(Ck[i][j]) for j in range(4)] for i in range(4)]
                x, y = PAIRS[f % 120]
                Nk = [[base.mu[base.v_other] if (x >> i & 1 and y >> j & 1) else 0 for j in range(4)]
                      for i in range(4)]
                term = f4_matmul(f4_matmul(aug_inv, Nk), psiC)
                rhs = [[rhs[i][j] ^ term[i][j] for j in range(4)] for i in range(4)]
            assert lhs == rhs
            assert f4_rank(lhs) <= sum(is_other)
        out[f"base_{name}"]["random_word_identity_checks"] = 60
    return out


def det_check() -> None:
    """C3 determinant: det over F2[C3] of a word is t^(n_a - n_b); the target has det 1."""
    def cm(x, y):
        out = 0
        for i in range(3):
            if x >> i & 1:
                for j in range(3):
                    if y >> j & 1:
                        out ^= 1 << ((i + j) % 3)
        return out

    def det(M):
        total = 0
        for p in itertools.permutations(range(4)):
            term = 1
            for i in range(4):
                term = cm(term, M[i][p[i]])
            total ^= term
        return total

    assert COSET[A] == 1 and COSET[B] == 2
    rng = random.Random(7)
    for _ in range(200):
        word = [rng.randrange(240) for _ in range(rng.randrange(0, 9))]
        Wm = word_product(word)
        na = sum(f < 120 for f in word)
        assert det([[pi(Wm[i][j]) for j in range(4)] for i in range(4)]) == 1 << ((2 * na - len(word)) % 3)
    assert det([[pi(TARGET[i][j]) for j in range(4)] for i in range(4)]) == 1


# ---------------------------------------------------------------- C joins
def compile_join(src: Path, out: Path) -> None:
    cc = shutil.which("cc") or shutil.which("gcc")
    assert cc, "a C compiler is required"
    subprocess.run([cc, "-std=c11", "-O3", "-Wall", "-Wextra", "-Werror", "-pthread",
                    "-o", str(out), str(src)], check=True)


def run_join(exe: Path, *args: str) -> dict:
    proc = subprocess.run([str(exe), *args], check=True, capture_output=True, text=True, timeout=500)
    text = proc.stdout
    s3 = re.search(r"S3 distinct by minimal length: (\d+) (\d+) (\d+) (\d+) total (\d+)", text)
    stats = re.search(r"processed_len3=(\d+) children=(\d+).*short_hits=(\d+) long_hits=(\d+)", text)
    best = re.search(r"best_word (none|len=(\d+):([\d ]+))", text)
    planted = re.search(r"planted word:([\d ]+)", text)
    return {
        "p_le3": [int(v) for v in s3.groups()],
        "processed_len3": int(stats.group(1)), "children": int(stats.group(2)),
        "short_hits": int(stats.group(3)), "long_hits": int(stats.group(4)),
        "best": None if best.group(1) == "none" else [int(v) for v in best.group(3).split()],
        "planted": None if not planted else [int(v) for v in planted.group(1).split()],
    }


def main() -> None:
    pred = json.loads(PRED.read_text())
    report: dict = {}
    assert (PERMS[C], PERMS[D], PERMS[E]) == ((1, 0, 3, 2), (2, 3, 0, 1), (3, 2, 1, 0))
    assert C == MUL[MUL[A][B]][MUL[B][A]]  # c = abba in this presentation
    assert DIRECT == pred["direct_word"]["factor_ids_in_search_alphabet"]
    M = word_product(DIRECT)
    assert M == TARGET and regular_replay(M, TARGET) == 48
    omissions = sum(word_product(DIRECT[:k] + DIRECT[k + 1:]) != TARGET for k in range(8))
    assert omissions == 8
    mutated = DIRECT[:7] + [56]  # last call b -> a on role 4
    assert regular_replay(word_product(mutated), TARGET) < 48
    report["direct_word"] = {"paid_calls": 8, "regular_inputs_checked": 48,
                             "single_omissions_rejected": omissions, "mutated_label_rejected": True}
    det_check()
    report["c3_determinant"] = "det formula t^(n_a-n_b) checked on 200 random words; target det = 1, so n_a = n_b mod 3 for any target word"
    report["radical_rank_lemma"] = lemma_checks()
    threads = "2"
    with tempfile.TemporaryDirectory() as tmp:
        exe_a, exe_b = Path(tmp) / "join_a", Path(tmp) / "join_b"
        compile_join(PACKAGE / "join_a.c", exe_a)
        compile_join(PACKAGE / "join_b.c", exe_b)
        expected_s3 = [1, 240, 41920, 6655830, 6697991]
        joins = {}
        for name, exe in (("join_a", exe_a), ("join_b", exe_b)):
            res = run_join(exe, "target", threads, "1")
            assert res["p_le3"] == expected_s3, res
            assert res["p_le3"][4] == pred["exact_join"]["right_distinct_exact_states"]
            assert res["processed_len3"] == 6655830 and res["children"] == 6655830 * 240
            assert res["short_hits"] == 0 and res["long_hits"] == 0 and res["best"] is None
            three = run_join(exe, "three", threads, "64")
            assert three["short_hits"] >= 1 and len(three["best"]) == 6
            assert word_product(three["best"]) == THREE
            planted_found = 0
            for seed in ("1", "2"):
                pl = run_join(exe, "planted", threads, "64", seed)
                assert pl["long_hits"] >= 1 and len(pl["best"]) == 7
                assert word_product(pl["best"]) == word_product(pl["planted"])
                planted_found += 1
            joins[name] = {"no_word_through_length": 7, "len3_classes_expanded": res["processed_len3"],
                           "children_checked": res["children"], "three_output_6word": three["best"],
                           "planted_7words_found": planted_found}
        report["joins"] = joins
    report["result"] = "PASS_A4_FOUR_ROLE_EXACT_MINIMUM_EIGHT"
    print(json.dumps(report, indent=1, sort_keys=True))
    print("PASS_A4_FOUR_ROLE_EXACT_MINIMUM_EIGHT")


if __name__ == "__main__":
    main()
