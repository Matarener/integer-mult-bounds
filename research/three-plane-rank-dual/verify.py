#!/usr/bin/env python3
"""Three-plane extension of #4365's rank dual: exact certificates for every plane triple. Standard library only.

Contract (#4365 PROOF.md section 1): a scalar message u v^T is charged t(S,U) = rank_F2 of the binary label
pairing on the whole-plane closures S of u and U of v. For a plane triple and a weight vector w >= 0 on the
seven plane unions X, the functional L(M) = sum_X w_X rank(M_XX) is subadditive, and on an atom it equals
sum_X w_X [S meets X][U meets X]. If that is <= t(S,U) for all 49 closure pairs, every finite decomposition of
I_6 over ANY field costs at least L(I_6) = sum_X 2|X| w_X.

The verifier recomputes all 27,720 triples' tariffs from the pinned archive and matching, groups them into
classes, and checks CERTIFICATES.json exactly:
  * classes with value 12: integer weights with every atom inequality, so the three-plane COPY mass is >= 12
    over every field; the coordinate decomposition attains 12, so it is sharp;
  * classes with value < 12: the stored weights attain the value, and an exact dual covering y >= 0 with
    sum_{S,U meet X} y >= 2|X| for every X and sum y t = value proves no principal block-rank functional does
    better; the recorded F2 exact minimum (generate.py, HiGHS ILP; local evidence) is 12.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import io
import itertools
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
MATCHING = ROOT / "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
HASHES = {"archive": "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6",
          "matching": "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1"}
UNIONS = list(range(1, 8))            # bitmask over the three planes
KEYS = sorted((S, U) for S in UNIONS for U in UNIONS)
SINGLES = (1, 2, 4)
OFFDIAG = [(P, Q) for P in SINGLES for Q in SINGLES if P != Q]


def phi_bound(S, U, X, Z):
    """upper bound on rank(Phi_Z(u v^T)_XX): Phi_Z zeroes the plane blocks (P, Q) in Z.

    Restricted to rows X and columns X, Phi_Z(u v^T) = sum over touched row planes P of
    u_P (sum over allowed column planes Q of v_Q)^T, so rows with the same allowed column set combine into one
    rank-one term; columns likewise."""
    Z = {tuple(z) for z in Z}
    rows = [P for P in SINGLES if P & S & X]
    cols = [Q for Q in SINGLES if Q & U & X]
    by_row = {frozenset(Q for Q in cols if (P, Q) not in Z) for P in rows} - {frozenset()}
    by_col = {frozenset(P for P in rows if (P, Q) not in Z) for Q in cols} - {frozenset()}
    return min(len(by_row), len(by_col))


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def pop(x):
    return bin(x).count("1")


def dot(a, b):
    return pop(a & b) & 1


def rank2(rows):
    rank = 0
    rows = list(rows)
    while rows:
        pivot = rows.pop()
        if pivot == 0:
            continue
        rank += 1
        low = pivot & -pivot
        rows = [r ^ pivot if r & low else r for r in rows]
    return rank


def load():
    raw = ARCHIVE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == HASHES["archive"], "archive hash")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
        data = json.loads(tf.extractfile(MEMBER).read())
    cert_raw = MATCHING.read_bytes()
    need(hashlib.sha256(cert_raw).hexdigest() == HASHES["matching"], "matching hash")
    recipes = sorted(data["recipes"], key=lambda r: r["port"])
    labels = [r["q"] for r in recipes]
    planes = json.loads(cert_raw)["matching"]
    need(len(labels) == 112 and len(planes) == 56, "112 labels, 56 planes")
    for u, v in planes:
        need((dot(labels[u], labels[u]), dot(labels[v], labels[v]), dot(labels[u], labels[v])) == (1, 1, 0),
             "plane Gram I_2")
    return labels, planes


def classes_of_triples():
    labels, planes = load()
    out = {}
    for tri in itertools.combinations(range(56), 3):
        ports = [planes[i] for i in tri]
        group = {X: [p for k in range(3) if X >> k & 1 for p in ports[k]] for X in UNIONS}
        tt = tuple(rank2(sum(dot(labels[a], labels[b]) << j for j, b in enumerate(group[U])) for a in group[S])
                   for S, U in KEYS)
        out.setdefault(tt, []).append(tri)
    return out


def main():
    classes = classes_of_triples()
    need(sum(len(v) for v in classes.values()) == 27720, "all triples")
    cert = json.loads((Path(__file__).resolve().parent / "CERTIFICATES.json").read_text(encoding="utf-8"))
    rows = {tuple(r["tariffs"]): r for r in cert["classes"]}
    need(set(rows) == set(classes), "one certificate per tariff class")
    strong = weak = phi_strong = 0
    weak_values = {}
    for tt, triples in classes.items():
        T = dict(zip(KEYS, tt))
        r = rows[tt]
        need(r["triples"] == len(triples), "triple count")
        w = [Q(x) for x in r["weights"]]
        need(all(x >= 0 for x in w), "nonnegative weights")
        for S, U in KEYS:
            need(sum(w[i] for i, X in enumerate(UNIONS) if S & X and U & X) <= T[S, U], "atom inequality")
        value = sum(2 * pop(X) * w[i] for i, X in enumerate(UNIONS))
        need(value == Q(r["value"]) and value <= 12, "functional value")
        # the coordinate decomposition: diagonal atoms on single planes cost the self tariff
        need(sum(2 * T[1 << k, 1 << k] for k in range(3)) == 12, "coordinate decomposition costs 12")
        if value == 12:
            need(all(x.denominator == 1 for x in w), "integer certificate")
            strong += len(triples)
            continue
        # zeroed-block functional: Phi_Z keeps the diagonal plane blocks, so Phi_Z(I)_XX = I_X
        Z = [tuple(z) for z in r["phi_zero_blocks"]]
        need(all(P != Q for P, Q in Z), "only off-diagonal blocks are zeroed")
        pw = [Q(x) for x in r["phi_weights"]]
        need(all(x >= 0 for x in pw), "nonnegative phi weights")
        for S, U in KEYS:
            need(sum(pw[i] * phi_bound(S, U, X, Z) for i, X in enumerate(UNIONS)) <= T[S, U], "phi atom inequality")
        pvalue = sum(2 * pop(X) * pw[i] for i, X in enumerate(UNIONS))
        need(pvalue == Q(r["phi_value"]), "phi value")
        if pvalue == 12:
            phi_strong += len(triples)
        else:
            y = [Q(x) for x in r["covering"]]
            need(all(x >= 0 for x in y), "nonnegative covering")
            for i, X in enumerate(UNIONS):
                need(sum(y[k] for k, (S, U) in enumerate(KEYS) if S & X and U & X) >= 2 * pop(X), "covering")
            need(sum(y[k] * T[key] for k, key in enumerate(KEYS)) == value, "covering value = functional value")
            need(r.get("f2_minimum_mass") == 12, "recorded F2 exact minimum is 12")
            weak += len(triples)
            weak_values[str(value)] = weak_values.get(str(value), 0) + len(triples)
    need(strong == 26977 and phi_strong == 418 and weak == 325, "class split")
    print(json.dumps({"status": "PASS_THREE_PLANE_RANK_DUAL", "triples": 27720, "tariff_classes": len(classes),
                      "floor_12_block_rank": strong, "floor_12_zeroed_block": phi_strong,
                      "floor_12_all_fields_total": strong + phi_strong, "open_below_12_block_rank": weak_values,
                      "f2_exact_minimum_on_those": 12, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
