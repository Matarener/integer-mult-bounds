#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent binding of PR3335's all-field, all-block rank theorem.

Arham Tahir, with substantial OpenAI Codex assistance. Standard library only;
no predecessor executable imports, floating point, network or default writes.
The arbitrary-field/dimension proof is in README, not inferred from samples.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
PAYLOAD_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
PREDECESSOR = "1d46df8b5aeac49d165cae58c1dd1036666bb789"


class Rejected(ValueError):
    """A checked mathematical or input-contract failure."""


def need(condition, message):
    if not condition:
        raise Rejected(message)


def unique_object(items):
    out = {}
    for key, value in items:
        need(key not in out, "duplicate JSON key: " + key)
        out[key] = value
    return out


def decode(raw):
    return json.loads(raw, object_pairs_hook=unique_object)


def dot(x, y):
    return (x & y).bit_count() % 2


def authenticate():
    sources = decode((HERE / "SOURCES.json").read_bytes())
    observed = {}
    rows = [r for r in sources["files"] if r["usage"] == "input"]
    need(len(sources["remote_sources"]) == 1, "one remote certificate")
    remote = sources["remote_sources"][0]
    need(remote["commit"] == PREDECESSOR
         and remote["git_blob"] == "a99dfa5e83d5f70b4ef8d9cf2fa7a275aeddf8bb"
         and remote["sha256"] == "cd5edbe9bf46aa544ee47450adcf0c2dc9eee5a57acda8bc6f4b726ab7f2ae47"
         and remote["source_path"] == "research/paired-plane-rematch-rank34/CERTIFICATE.json"
         and remote["path"] == "research/rematch-block-rank-audit/PR3335-CERTIFICATE.json",
         "exact remote source binding")
    for row in rows + [remote]:
        raw = (ROOT / row["path"]).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(digest == row["sha256"] and blob == row["git_blob"],
             "source bytes: " + row["path"])
        observed[row["path"]] = digest
    need(len(observed) == 2, "archive and vendored certificate pins")
    return observed


def load_model():
    archive = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
    with tarfile.open(archive, "r:gz") as tf:
        members = [m for m in tf.getmembers() if m.name == MEMBER]
        need(len(members) == 1 and members[0].isfile(), "unique regular phase payload")
        stream = tf.extractfile(members[0])
        need(stream is not None, "phase stream")
        payload = stream.read()
    need(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA, "selected phase hash")
    rows = sorted(decode(payload)["recipes"], key=lambda r: r["port"])
    need([r["port"] for r in rows] == list(range(112)), "selected port order")
    labels = [r["q"] for r in rows]
    need(len(set(labels)) == 112
         and all(type(q) is int and 0 < q < 512 and dot(q, q) == 1 for q in labels),
         "112 distinct odd nine-bit labels")
    return labels, decode((HERE / "PR3335-CERTIFICATE.json").read_bytes())


def model(labels, cert):
    """Reconstruct each plane as all four vectors, rather than a borrowed graph."""
    pairs = cert["pairs"]
    need(len(pairs) == 56 and all(isinstance(p, list) and len(p) == 2 for p in pairs),
         "56 plane pairs")
    flat = [p for pair in pairs for p in pair]
    need(all(type(i) is int for i in flat) and sorted(flat) == list(range(112)),
         "perfect matching")
    spaces, owner = [None] * 112, [None] * 112
    for k, (i, j) in enumerate(pairs):
        need(dot(labels[i], labels[j]) == 0, "Gram-I2 pair")
        E = frozenset((0, labels[i], labels[j], labels[i] ^ labels[j]))
        need(len(E) == 4, "plane dimension two")
        spaces[i] = spaces[j] = E
        owner[i] = owner[j] = k
    forbidden = [[any(dot(x, y) for x in spaces[i] for y in spaces[j])
                  for j in range(112)] for i in range(112)]
    for i in range(112):
        for j in range(112):
            a, b = pairs[owner[i]], pairs[owner[j]]
            need(forbidden[i][j] == any(dot(labels[u], labels[v]) for u in a for v in b),
                 "basis/full-plane mask agreement")
    return pairs, owner, forbidden


def scalar_certificate(cert, pairs, owner, forbidden):
    supports = cert["supports"]
    need(len(supports) == 34 and all(isinstance(s, list) and s for s in supports),
         "34 nonempty supports")
    flat = [i for support in supports for i in support]
    need(all(type(i) is int for i in flat) and sorted(flat) == list(range(112)),
         "disjoint support partition")
    channel = [None] * 112
    for k, support in enumerate(supports):
        for i in support:
            channel[i] = k
        need(all(i == j or not forbidden[i][j] for i in support for j in support),
             "support fits full plane mask")
    K = [[int(channel[i] == channel[j]) for j in range(112)] for i in range(112)]
    forced = sum(i == j or forbidden[i][j] for i in range(112) for j in range(112))
    need(forced == 11440, "full forced-entry count")
    clique = cert["clique_planes"]
    need(len(clique) == 17 and all(type(k) is int and 0 <= k < 56 for k in clique)
         and len(set(clique)) == 17, "17 distinct clique planes")
    principal = [i for k in clique for i in pairs[k]]
    need(len(set(principal)) == 34
         and all(i == j or forbidden[i][j] for i in principal for j in principal),
         "every entry of the 34-port identity block is forced")
    for selected in ([s[0] for s in supports], principal):
        need(all(K[i][j] == int(i == j) for i in selected for j in selected),
             "support/clique identity minor")
    need(all(owner[i] != owner[j] for s in supports for i in s for j in s if i != j),
         "same-plane ports cannot share a support")
    return supports, channel, K, principal, forced


def rank_mod(matrix, prime):
    """Modular row elimination independent of the support certificate."""
    pivots = {}
    for original in matrix:
        row = [v % prime for v in original]
        for col, pivot in sorted(pivots.items()):
            if row[col]:
                q = row[col]
                row = [(a - q * b) % prime for a, b in zip(row, pivot)]
        col = next((k for k, value in enumerate(row) if value), None)
        if col is not None:
            inverse = pow(row[col], -1, prime)
            pivots[col] = [v * inverse % prime for v in row]
    return len(pivots)


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def eye(d):
    return [[int(i == j) for j in range(d)] for i in range(d)]


def charts(d, supports):
    direct = [eye(d) for _ in range(112)]
    inverse = [eye(d) for _ in range(112)]
    if d >= 2:
        chosen = next(s for s in supports if len(s) >= 3)
        a, b = chosen[0], chosen[2]
        direct[a][0][1], inverse[a][0][1] = 1, -1
        direct[b][1][0], inverse[b][1][0] = 1, -1
    need(all(multiply(a, b) == eye(d) == multiply(b, a)
             for a, b in zip(direct, inverse)), "unimodular chart inverses")
    return direct, inverse


def block_matrix(channel, direct, inverse):
    d = len(direct[0])
    M = [[0] * (112 * d) for _ in range(112 * d)]
    for i in range(112):
        for j in range(112):
            if channel[i] != channel[j]:
                continue
            block = multiply(direct[i], inverse[j])
            for u in range(d):
                for v in range(d):
                    M[i * d + u][j * d + v] = block[u][v]
    return M


def require_block_fit(M, d, forbidden):
    need(len(M) == 112 * d and all(len(row) == 112 * d for row in M), "block shape")
    for i in range(112):
        for j in range(112):
            if i != j and not forbidden[i][j]:
                continue
            for u in range(d):
                for v in range(d):
                    need(M[i * d + u][j * d + v] == int(i == j and u == v),
                         f"block contract at ({i},{j},{u},{v})")


def query_action(x, y, supports, direct, inverse):
    """34 vector queries, separately from the dense block assembler."""
    d = len(direct[0])
    out = list(y)
    for support in supports:
        total = [sum(inverse[j][u][v] * x[j * d + v]
                     for j in support for v in range(d)) for u in range(d)]
        for i in support:
            for u in range(d):
                out[i * d + u] += sum(direct[i][u][v] * total[v] for v in range(d))
    return out


def rejected(name, fn, names):
    try:
        fn()
    except Rejected:
        names.append(name)
    else:
        raise Rejected("control accepted: " + name)


def colouring_rank_control():
    """Classical 27-line Gram fixture: support counting need not bound rank.

    This is not a P112 counterexample, nor a new graph-theory result. The
    explicit seven-dimensional factorization makes the logical control small
    and independently checkable without importing a graph catalogue.
    """
    vectors = []
    for i in range(6):
        vectors.append([0] + [int(i == j) for j in range(6)])
    for i in range(6):
        vectors.append([2] + [-int(i != j) for j in range(6)])
    for a, b in combinations(range(6), 2):
        vectors.append([1] + [-int(j in (a, b)) for j in range(6)])
    gram = [[x[0] * y[0] - sum(a * b for a, b in zip(x[1:], y[1:]))
             for y in vectors] for x in vectors]
    need(all(gram[i][i] == -1 for i in range(27)), "27-line Gram diagonal")
    need(all(gram[i][j] in (0, 1) for i in range(27) for j in range(27) if i != j),
         "27-line Gram off-diagonal")
    allowed = [[i != j and gram[i][j] == 1 for j in range(27)] for i in range(27)]
    need(all(sum(row) == 10 for row in allowed), "27-line degree ten")
    # Every edge has exactly one common neighbour: no permitted K4 can exist.
    need(all(sum(allowed[i][k] and allowed[j][k] for k in range(27)) == 1
             for i in range(27) for j in range(i) if allowed[i][j]),
         "permitted cliques have size at most three")
    # Directly verify a triangle, making the size-three support bound sharp.
    triangle = next((i, j, k) for i, j, k in combinations(range(27), 3)
                    if allowed[i][j] and allowed[i][k] and allowed[j][k])
    fitting = [[-x for x in row] for row in gram]
    need(all(fitting[i][j] == int(i == j)
             for i in range(27) for j in range(27) if i == j or not allowed[i][j]),
         "rank-seven control fits its own strict scalar mask")
    # Rational elimination is separate from the modular rank implementation.
    work = [[Fraction(x) for x in row] for row in fitting]
    rank = 0
    for col in range(27):
        pivot = next((r for r in range(rank, 27) if work[r][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        denominator = work[rank][col]
        work[rank] = [x / denominator for x in work[rank]]
        for r in range(rank + 1, 27):
            coefficient = work[r][col]
            if coefficient:
                work[r] = [a - coefficient * b for a, b in zip(work[r], work[rank])]
        rank += 1
    need(rank == 7 < 9, "support floor nine is not a general rank lower bound")
    return {"ports": 27, "max_permitted_clique": 3, "triangle": list(triangle),
            "disjoint_support_count_lower_bound": 9, "exhibited_rational_fitting_rank": rank,
            "is_P112_counterexample": False}


def run():
    source_hashes = authenticate()
    labels, cert = load_model()
    pairs, owner, forbidden = model(labels, cert)
    supports, channel, K, principal, forced = scalar_certificate(cert, pairs, owner, forbidden)
    ranks, matrices = {}, {}
    for d in (1, 2, 3):
        direct, inverse = charts(d, supports)
        M = block_matrix(channel, direct, inverse)
        require_block_fit(M, d, forbidden)
        measured = {str(p): rank_mod(M, p) for p in (2, 3, 101)}
        need(set(measured.values()) == {34 * d}, "finite block ranks")
        ranks[str(d)], matrices[d] = measured, M
    direct, inverse = charts(2, supports)
    M = matrices[2]
    s = next(s for s in supports if len(s) >= 3)
    a, middle, b = s[:3]
    A, B = multiply(direct[a], inverse[middle]), multiply(direct[middle], inverse[b])
    AB, BA = multiply(A, B), multiply(B, A)
    need(AB != BA and any(abs(x - y) == 1 for r, t in zip(AB, BA) for x, y in zip(r, t)),
         "noncommuting blocks over every field")
    zero = [0] * 224
    for j in range(224):
        x = [int(i == j) for i in range(224)]
        need(query_action(x, zero, supports, direct, inverse) == [row[j] for row in M],
             "independent source-coordinate query action")
        need(query_action(zero, x, supports, direct, inverse) == x, "dirty target identity")

    controls = []
    i, j = pairs[0]
    need(dot(labels[i], labels[j]) == 0 and forbidden[i][j], "line-only escape witness")
    bad = [row[:] for row in K]
    bad[i][j] = 1
    rejected("line-only mask misses matched-partner coupling",
             lambda: require_block_fit(bad, 1, forbidden), controls)
    N = [[1, -1], [1, -1]]
    need(N[0][0] + N[1][1] == 0 and all(sum(row) == 0 for row in N), "hidden fault fixture")
    for target, source in ((i, j), (j, i)):
        bad = [row[:] for row in M]
        for u in range(2):
            for v in range(2):
                bad[2 * target + u][2 * source + v] = N[u][v]
        rejected(f"directed hidden block {target}<-{source}",
                 lambda bad=bad: require_block_fit(bad, 2, forbidden), controls)
    bad = [row[:] for row in M]
    bad[2 * i][2 * i + 1] = 1
    rejected("diagonal trace does not imply identity",
             lambda: require_block_fit(bad, 2, forbidden), controls)
    badcert = decode(json.dumps(cert))
    badcert["clique_planes"] = cert["clique_planes"][:-1]
    rejected("missing clique plane",
             lambda: scalar_certificate(badcert, pairs, owner, forbidden), controls)
    badcert = decode(json.dumps(cert))
    badcert["supports"][0].append(badcert["supports"][1].pop())
    rejected("cross-plane support reassignment",
             lambda: scalar_certificate(badcert, pairs, owner, forbidden), controls)
    badcert = decode(json.dumps(cert))
    badcert["pairs"][0][0] = badcert["pairs"][1][0]
    rejected("duplicate matching port", lambda: model(labels, badcert), controls)
    rejected("duplicate JSON key", lambda: decode('{"pairs":[],"pairs":[]}'), controls)
    need(authenticate() == source_hashes, "source pins stable through replay")
    return {
        "status": "PASS_REMATCH_BLOCK_RANK_AUDIT",
        "predecessor_head": PREDECESSOR,
        "source_sha256": source_hashes,
        "phase_payload_sha256": PAYLOAD_SHA,
        "ports": 112, "planes": 56, "channels": 34,
        "forced_port_entries": forced,
        "support_size_histogram": dict(sorted(Counter(map(len, supports)).items())),
        "forced_identity_ports": principal,
        "exact_theorem": "min rank M = 34*d for every field and every integer d>=1",
        "finite_rank_checks": ranks,
        "noncommuting_witness": {"ports": [a, middle, b], "A": A, "B": B, "AB": AB, "BA": BA},
        "source_coordinate_columns": 224, "dirty_target_columns": 224,
        "line_mask_counterexample_ports": [i, j],
        "colouring_vs_rank_logical_control": colouring_rank_control(),
        "rejected_controls": controls,
        "global_matching_lower_bound_claimed": False,
        "native_tariff_or_supplier_admission_claimed": False,
    }


def main():
    result = run()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
        return
    need(not sys.argv[1:], "usage: verify.py [--emit]")
    expected = decode((HERE / "RESULT.json").read_bytes())
    need(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
         "exact typed result receipt")
    print("PASS_REMATCH_BLOCK_RANK_AUDIT min_rank=34*d fields=all d>=1 "
          "finite_dimensions=1,2,3 source_columns=224 dirty_columns=224 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
