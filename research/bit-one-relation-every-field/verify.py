"""Replay the F_p one-relation register census and its controls.

Apache-2.0. Prepared for Josie Elliston with Claude (Anthropic) assistance.

Default: the registered domain (about one minute on CPython 3.12) and exact
comparison with CERTIFICATE.json.  ``--long`` adds the W=3, k=6 run over F3
(about ten minutes), whose counts are also recorded in the certificate.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from census import (coeffs_extend, disjoint_ok, evaluate, identity, idempotents,
                    matmul, neg, offdiag, relations)

HERE = os.path.dirname(os.path.abspath(__file__))


def coord_projectors(W):
    return [tuple(1 if (i == a and j == a) else 0 for i in range(W) for j in range(W))
            for a in range(W)]


def sub(A, B, p):
    return tuple((a - b) % p for a, b in zip(A, B))


def product_coeffs(word, p, W):
    I = identity(W)
    cs = [I]
    for N in word:
        cs = coeffs_extend(cs, N, sub(I, N, p), p, W)
    return cs


def structure_ok(word, r, p, W):
    """Lemmas A-C of the README on one diagonal pair (step 1 is built into
    the enumeration).  A: one projector per relation sign.  B: with both signs,
    N N' = N' N = 0 and N + N' is diagonal.  C: an outside factor commutes with
    every relation factor unless the relation factors before it are none or all."""
    k = len(word)
    S = [j for j in range(k) if r[j]]
    if not any(offdiag(word[S[0]], W)):
        return True  # M = 0: coordinate projectors only
    plus = set(word[j] for j in S if r[j] == 1)
    minus = set(word[j] for j in S if r[j] == -1)
    if len(plus) != 1 or len(minus) > 1:
        return False
    if minus:
        (N,), (Np,) = plus, minus
        if any(matmul(N, Np, p, W)) or any(matmul(Np, N, p, W)):
            return False
        if any(offdiag(tuple((a + b) % p for a, b in zip(N, Np)), W)):
            return False
    for j in range(k):
        if r[j] == 0 and S[0] < j < S[-1]:
            E = word[j]
            if any(matmul(E, word[l], p, W) != matmul(word[l], E, p, W) for l in S):
                return False
    return True


def pruned(p, W, k):
    """All diagonal (word, r) pairs, enumerated through the step-1 reduction:
    coordinate projectors off the relation support, and offdiag(N_j) = r_j M
    on it.  Returns (pairs, violations)."""
    idem = idempotents(p, W)
    I = identity(W)
    cls = {}
    for N in idem:
        cls.setdefault(offdiag(N, W), []).append(N)
    coords = coord_projectors(W)
    found, viol, bad = [], [], []
    for r in relations(k):
        for M in cls:
            choice = []
            for j in range(k):
                if r[j] == 0:
                    choice.append(coords)
                else:
                    choice.append(cls.get(M if r[j] == 1 else neg(M, p), []))
            if any(not c for c in choice):
                continue
            stack = [(0, [I], ())]
            while stack:
                i, cs, word = stack.pop()
                if i == k:
                    d = evaluate(cs, r, k, p, W)
                    if d is not None:
                        found.append((word, r))
                        if not disjoint_ok(d, r, k):
                            viol.append((word, r))
                        if not structure_ok(word, r, p, W):
                            bad.append((word, r))
                    continue
                for N in choice[i]:
                    stack.append((i + 1, coeffs_extend(cs, N, sub(I, N, p), p, W), word + (N,)))
    return found, viol, bad


def unpruned(p, W, k):
    """Every word over all rank-one idempotents and every relation r."""
    idem = idempotents(p, W)
    I = identity(W)
    rels = list(relations(k))
    found, viol, step1 = [], [], []
    stack = [(0, [I], ())]
    while stack:
        i, cs, word = stack.pop()
        if i == k:
            for r in rels:
                d = evaluate(cs, r, k, p, W)
                if d is None:
                    continue
                found.append((word, r))
                if not disjoint_ok(d, r, k):
                    viol.append((word, r))
                offs, good = set(), True
                for j in range(k):
                    o = offdiag(word[j], W)
                    if r[j] == 0:
                        good = good and not any(o)
                    else:
                        offs.add(o if r[j] == 1 else neg(o, p))
                if len(offs) > 1 or not good:
                    step1.append((word, r))
            continue
        for N in idem:
            stack.append((i + 1, coeffs_extend(cs, N, sub(I, N, p), p, W), word + (N,)))
    return found, viol, step1


def digest(pairs):
    h = hashlib.sha256()
    for word, r in sorted(pairs):
        h.update(repr((word, r)).encode())
    return h.hexdigest()


def summary(p, W, k, pairs, viol):
    coords = set(coord_projectors(W))
    words = set(w for w, _ in pairs)
    return {"p": p, "W": W, "k": k, "diagonal_pairs": len(pairs), "diagonal_words": len(words),
            "noncoordinate_words": sum(1 for w in words if any(N not in coords for N in w)),
            "mixed_projector_words": sum(1 for w in words
                                         if len(set(N for N in w if N not in coords)) > 1),
            "violations": len(viol), "structure_failures": 0, "pairs_sha256": digest(pairs)}


def controls():
    out = []
    p, W = 3, 2
    N1, N2 = (2, 2, 2, 2), (2, 1, 1, 2)
    # petalas's complementary pair: diagonal under r=(1,-1), disjoint.
    cs = product_coeffs((N1, N2), p, W)
    d = evaluate(cs, (1, -1), 2, p, W)
    assert d is not None and disjoint_ok(d, (1, -1), 2), "complementary pair"
    out.append("complementary_pair_diagonal_and_disjoint")
    # wrong relation sign: same word is not diagonal when r=(1,1).
    assert evaluate(cs, (1, 1), 2, p, W) is None, "wrong sign accepted"
    out.append("wrong_relation_sign_rejected")
    # the characteristic-free cyclic block of seed04: one N, r = 1_S, product U(1) = I.
    N = (2, 2, 2, 2)
    cs = product_coeffs((N, N), p, W)
    d = evaluate(cs, (1, 1), 2, p, W)
    assert d is not None and disjoint_ok(d, (1, 1), 2)
    out.append("shared_cyclic_block_all_plus_diagonal")
    # step-1 reduction is sharp: same off-diagonal sign on an r=-1 index fails.
    cs = product_coeffs((N1, N1), p, W)
    assert evaluate(cs, (1, -1), 2, p, W) is None
    out.append("unsigned_shared_pattern_rejected_for_mixed_signs")
    # disjointness detector: two registers claiming the same frame.
    assert not disjoint_ok([(1, 0), (1, 0)], (1, 1), 2)
    out.append("overlapping_assignment_rejected")
    # disjointness detector accepts the alternative representative a+r.
    assert disjoint_ok([(1, 0, 0), (0, 1, 1)], (1, -1, -1), 3)
    out.append("alternative_class_representative_used")
    # a diagonal entry with two distinct monomials is rejected.
    I = (1, 0, 0, 1)
    assert evaluate([I, I, (0,) * 4, (0,) * 4], (1, 1), 2, p, W) is None
    out.append("non_monomial_diagonal_rejected")
    # a coefficient other than one is rejected.
    assert evaluate([(2, 0, 0, 2), (0,) * 4, (0,) * 4, (0,) * 4], (1, 1), 2, p, W) is None
    out.append("non_unit_coefficient_rejected")
    # structure lemma detector: two different same-sign projectors are flagged.
    assert not structure_ok((N1, (1, 1, 0, 0)), (1, 1), p, W)
    out.append("structure_detector_rejects_unequal_projectors")
    return out


def pair_lemmas(p, W):
    """Lemmas A and B as finite statements: every ordered pair of rank-one
    idempotents with nonzero offdiag(N_l) = +-offdiag(N_i) that passes the
    pair-slice condition has the claimed structure.  Returns the number of
    (same-sign, opposite-sign) pairs that pass the slice condition."""
    idem = idempotents(p, W)
    cls = {}
    for N in idem:
        cls.setdefault(offdiag(N, W), []).append(N)
    same = opp = 0
    for m, members in cls.items():
        if not any(m):
            continue
        for Ni in members:
            for Nl in members:
                if offdiag(matmul(Ni, Nl, p, W), W) == m:
                    assert Ni == Nl, ("Lemma A", p, W, Ni, Nl)
                    same += 1
            for Nl in cls.get(neg(m, p), []):
                if not any(offdiag(matmul(Ni, Nl, p, W), W)):
                    assert not any(matmul(Ni, Nl, p, W)), ("Lemma B", p, W, Ni, Nl)
                    assert not any(matmul(Nl, Ni, p, W)), ("Lemma B", p, W, Ni, Nl)
                    sm = tuple((a + b) % p for a, b in zip(Ni, Nl))
                    assert not any(offdiag(sm, W)), ("Lemma B", p, W, Ni, Nl)
                    assert sorted(sm[i * W + i] for i in range(W)) == [0] * (W - 2) + [1, 1]
                    opp += 1
    return same, opp


PAIR_LEMMA_DOMAIN = [(2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (3, 4), (5, 2), (5, 3), (7, 2), (7, 3)]

REGISTERED_UNPRUNED = [(3, 2, 1), (3, 2, 2), (3, 2, 3), (3, 2, 4), (3, 3, 2), (5, 2, 2), (5, 2, 3)]
REGISTERED_PRUNED = [(3, 3, k) for k in range(2, 6)] + [(3, 2, k) for k in range(2, 7)] + \
    [(5, 2, k) for k in range(2, 5)] + [(3, 4, k) for k in range(2, 4)]
LONG_PRUNED = [(3, 3, 6)]


def main():
    long = "--long" in sys.argv
    write = "--write" in sys.argv
    cert = {"model": "research/bit-one-relation-seed04 with F_p register coefficients; "
                     "one primitive relation r in {-1,0,1}^k, |supp r| >= 2",
            "unpruned_crosscheck": [], "pruned": [], "long_pruned": []}
    for p, W, k in REGISTERED_UNPRUNED:
        f, v, s = unpruned(p, W, k)
        f2, v2, b2 = pruned(p, W, k)
        assert not b2, ("structure lemma fails", p, W, k, b2[:2])
        assert not s, ("step-1 structure fails", p, W, k, s[:2])
        assert set(f) == set(f2) and len(f) == len(f2), ("pruned != unpruned", p, W, k)
        assert not v and not v2, ("disjoint assignment fails", p, W, k, v[:2])
        row = summary(p, W, k, f, v)
        row["step1_failures"] = 0
        cert["unpruned_crosscheck"].append(row)
    for p, W, k in REGISTERED_PRUNED:
        f, v, b = pruned(p, W, k)
        assert not v, ("disjoint assignment fails", p, W, k, v[:2])
        assert not b, ("structure lemma fails", p, W, k, b[:2])
        cert["pruned"].append(summary(p, W, k, f, v))
    cert["controls"] = controls()
    cert["pair_lemmas"] = []
    for p, W in PAIR_LEMMA_DOMAIN:
        same, opp = pair_lemmas(p, W)
        cert["pair_lemmas"].append({"p": p, "W": W, "same_sign_pairs": same, "opposite_sign_pairs": opp})
    path = os.path.join(HERE, "CERTIFICATE.json")
    old = json.load(open(path)) if os.path.exists(path) else None
    if long:
        for p, W, k in LONG_PRUNED:
            f, v, b = pruned(p, W, k)
            assert not v, ("disjoint assignment fails", p, W, k, v[:2])
            assert not b, ("structure lemma fails", p, W, k, b[:2])
            cert["long_pruned"].append(summary(p, W, k, f, v))
    elif old is not None:
        cert["long_pruned"] = old.get("long_pruned", [])
    if write:
        with open(path, "w") as fh:
            json.dump(cert, fh, indent=1, sort_keys=True)
            fh.write("\n")
    else:
        assert old == cert, "CERTIFICATE.json mismatch"
    n = sum(r["diagonal_pairs"] for r in cert["pruned"] + cert["long_pruned"])
    print(f"PASS_ONE_RELATION_FP_CENSUS unpruned={len(cert['unpruned_crosscheck'])} "
          f"pruned={len(cert['pruned'])} pair_lemma_domains={len(cert['pair_lemmas'])} long={len(cert['long_pruned'])} diagonal_pairs={n} "
          f"violations=0 controls={len(cert['controls'])} no_new_kappa")


if __name__ == "__main__":
    main()
