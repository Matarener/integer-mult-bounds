#!/usr/bin/env python3
"""Four-plane COPY floor under #4365's contract: exact certificates for plane quadruples. Standard library only.

For a plane quadruple and functionals L(M) = sum_{(Z, X)} w rank(Phi_Z(M)_XX) (Phi_Z zeroes the off-diagonal plane
blocks in Z; Z empty gives the plain block-rank functional), subadditivity and the combinatorial atom bound
    rank(Phi_Z(u v^T)_XX) <= min(#distinct allowed column-plane sets, #distinct allowed row-plane sets)
show that every decomposition of I_8, over any field, costs at least L(I_8) = sum w 2|X| whenever
sum w bound(S, T, X, Z) <= t(S, T) for all 225 closure pairs. Separate coordinate messages cost 16.

The verifier recomputes the tariffs of all 367,290 quadruples from the pinned selected archive and matching,
reads one certificate index per quadruple from CERT-INDEX (0 = no certificate), and checks every referenced
certificate exactly on its class. It reports the certified count; quadruples with index 0 are open.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import gzip
import hashlib
import io
import itertools
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
MATCHING = ROOT / "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
HASHES = {"archive": "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6",
          "matching": "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1"}
K = 4
UNIONS = list(range(1, 1 << K))
KEYS = [(S, T) for S in UNIONS for T in UNIONS]
SINGLES = [1 << k for k in range(K)]
OFF = [(P, Q2) for P in SINGLES for Q2 in SINGLES if P != Q2]


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
        p = rows.pop()
        if not p:
            continue
        rank += 1
        low = p & -p
        rows = [r ^ p if r & low else r for r in rows]
    return rank


def load():
    raw = ARCHIVE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == HASHES["archive"], "archive hash")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tf:
        data = json.loads(tf.extractfile(MEMBER).read())
    cert = MATCHING.read_bytes()
    need(hashlib.sha256(cert).hexdigest() == HASHES["matching"], "matching hash")
    labels = [r["q"] for r in sorted(data["recipes"], key=lambda r: r["port"])]
    planes = json.loads(cert)["matching"]
    need(len(labels) == 112 and len(planes) == 56, "112 labels, 56 planes")
    return labels, planes


def tariffs_all(labels, planes):
    G = {}
    for p in range(56):
        for q in range(56):
            G[p, q] = [sum(dot(labels[a], labels[b]) << j for j, b in enumerate(planes[q])) for a in planes[p]]
    for quad in itertools.combinations(range(56), K):
        out = []
        for S in UNIONS:
            rp = [quad[k] for k in range(K) if S >> k & 1]
            for T in UNIONS:
                cq = [quad[k] for k in range(K) if T >> k & 1]
                rows = []
                for p in rp:
                    for r in range(2):
                        v = 0
                        for jj, q in enumerate(cq):
                            v |= G[p, q][r] << (2 * jj)
                        rows.append(v)
                out.append(rank2(rows))
        yield quad, tuple(out)


def bound(S, T, X, Z):
    rows = [P for P in SINGLES if P & S & X]
    cols = [Q2 for Q2 in SINGLES if Q2 & T & X]
    br = {frozenset(Q2 for Q2 in cols if (P, Q2) not in Z) for P in rows} - {frozenset()}
    bc = {frozenset(P for P in rows if (P, Q2) not in Z) for Q2 in cols} - {frozenset()}
    return min(len(br), len(bc))



def build_table():
    """bound(S, T, X, Z) for every zero mask Z (12 off-diagonal pairs), as a flat bytearray"""
    tab = bytearray(4096 * 15 * 15 * 15)
    for S in UNIONS:
        for T in UNIONS:
            for X in UNIONS:
                rows = [P for P in SINGLES if P & S & X]
                cols = [Q2 for Q2 in SINGLES if Q2 & T & X]
                if not rows or not cols:
                    continue
                rel = [i for i, (P, Q2) in enumerate(OFF) if P in rows and Q2 in cols]
                base = ((S - 1) * 15 + T - 1) * 15 + X - 1
                for m in range(4096):
                    Z = {OFF[i] for i in rel if m >> i & 1}
                    br = {frozenset(Q2 for Q2 in cols if (P, Q2) not in Z) for P in rows} - {frozenset()}
                    bc = {frozenset(P for P in rows if (P, Q2) not in Z) for Q2 in cols} - {frozenset()}
                    tab[m * 3375 + base] = min(len(br), len(bc))
    return tab


def cert_ok(tt, cert, tab):
    """exact: integer-scaled weights; tt is the 225 tariffs in KEYS order"""
    den = 1
    for _, _, w in cert:
        den = den * w.denominator // __import__("math").gcd(den, w.denominator)
    iw = [(m * 3375, X - 1, int(w * den)) for m, X, w in cert]
    for k, (S, T) in enumerate(KEYS):
        base = ((S - 1) * 15 + T - 1) * 15
        if sum(w * tab[m + base + x] for m, x, w in iw) > tt[k] * den:
            return False
    return True


def main():
    certs_raw = json.loads(gzip.decompress((HERE / "CERTIFICATES.json.gz").read_bytes()))
    certs = [None] + [[(mask, X, Q(w)) for mask, X, w in c] for c in certs_raw["certificates"]]
    for c in certs[1:]:
        need(sum(2 * pop(X) * w for m, X, w in c) == 16 and all(w > 0 and 0 <= m < 4096 for m, X, w in c),
             "certificate value 16")
    tab = build_table()
    index = gzip.decompress((HERE / "CERT-INDEX.bin.gz").read_bytes())
    need(len(index) == 2 * 367290, "one index per quadruple")
    labels, planes = load()
    checked = {}
    certified = open_ = 0
    for n, (quad, tt) in enumerate(tariffs_all(labels, planes)):
        ci = index[2 * n] | index[2 * n + 1] << 8
        need(ci < len(certs), "index range")
        if ci == 0:
            open_ += 1
            continue
        key = (tt, ci)
        if key not in checked:
            need(cert_ok(tt, certs[ci], tab), f"atom inequalities, quad {quad}")
            checked[key] = True
        certified += 1
    need(certified + open_ == 367290, "all quadruples")
    print(json.dumps({"status": "PASS_FOUR_PLANE_RANK_DUAL", "quadruples": 367290, "certified_floor_16": certified,
                      "open": open_, "distinct_certificates": len(certs) - 1, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
