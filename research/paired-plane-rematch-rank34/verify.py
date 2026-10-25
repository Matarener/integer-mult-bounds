#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""A rematched P112 pairing whose strict plane-port mask has exact fitting rank 34.

Model, label source and checking functions are PR2484's (research/paired-plane-minrank-bracket-audit),
imported unchanged: ports i, j may be matched iff q_i.q_i = q_j.q_j = 1 and q_i.q_j = 0; a fitting K has
K_ii = 1 and K_ij = 0 whenever i != j and the planes at i, j are not orthogonal.

Checks: (1) CERTIFICATE.json's 56 pairs are a perfect matching with Gram I2;
(2) its 34 disjoint supports give a fitting 0/1 matrix of rank 34 (mod 2, 3 and 1000003), so rank <= 34;
(3) its 17 planes are pairwise non-orthogonal, so the 34x34 principal submatrix of every fit is I_34
    and rank >= 34 over every field;
(4) the PR1825 matching still has exact clique number 24 here (positive control of the shared engine);
(5) written: no orthogonal plane set has more than four planes, so colourings need >= 14 classes (28 supports);
(6) rejection controls.
"""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
_SPEC = importlib.util.spec_from_file_location(
    "pr2484_verify", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(_SPEC)  # PR2484's verifier, imported unchanged
_SPEC.loader.exec_module(V)

ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
PR1825 = ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json"


def model():
    labels, pairs0, orth0 = V.load_model(ARCHIVE.read_bytes(), PR1825.read_bytes())
    return labels, pairs0, orth0


def plane_orth(labels, pairs):
    V.need(len(pairs) == 56 and sorted(x for p in pairs for x in p) == list(range(112)), "perfect matching")
    dot = V.parity_dot
    for a, b in pairs:
        V.need(dot(labels[a], labels[a]) == 1 and dot(labels[b], labels[b]) == 1 and dot(labels[a], labels[b]) == 0,
               "matched plane must have Gram I2")
    basis = [(labels[a], labels[b]) for a, b in pairs]
    return [[i != j and all(dot(x, y) == 0 for x in basis[i] for y in basis[j]) for j in range(56)] for i in range(56)]


def check(cert, labels):
    pairs = [tuple(p) for p in cert["pairs"]]
    orth = plane_orth(labels, pairs)
    supports = [list(s) for s in cert["supports"]]
    upper = V.check_fitting_supports(supports, pairs, orth)
    K = V.dense_from_supports(supports)
    required = V.check_mask_entries(K, pairs, orth)
    ranks = {str(p): V.rank_mod_p(K, p) for p in (2, 3, 1000003)}
    V.need(set(ranks.values()) == {upper}, "dense rank equals the support count")
    clique = list(cert["clique_planes"])
    V.need(len(set(clique)) == len(clique) and all(0 <= v < 56 for v in clique), "clique planes")
    V.need(all(not orth[u][v] for u in clique for v in clique if u != v), "clique planes pairwise non-orthogonal")
    ports = [p for v in clique for p in pairs[v]]
    owner = V.owner_map(pairs)
    for i in ports:
        for j in ports:
            V.need(i == j or not orth[owner[i]][owner[j]], "principal submatrix entries are all forced")
    lower = len(ports)
    V.need(lower == upper, "exact rank")
    return dict(pairs=len(pairs), supports=upper, required_mask_entries=required, ranks_mod_p=ranks,
                clique_planes=len(clique), forced_identity_block=lower, exact_fitting_rank=upper), pairs, orth


def bad_matching(labels, pairs):
    """Swap partners between the first two pairs (a,b), (c,d) with q_a.q_c = 1."""
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            (a, b), (c, d) = pairs[i], pairs[j]
            if V.parity_dot(labels[a], labels[c]):
                out = list(pairs)
                out[i], out[j] = (a, c), (b, d)
                return out
    raise AssertionError("no non-orthogonal swap found")


def controls(cert, labels, pairs0, orth0):
    out = {}
    omega, count, _ = V.clique_number_dp(orth0, V.greedy_order(orth0))
    V.need(omega == 24, "PR1825 matching clique number 24 (PR2484's engine)")
    out["pr1825_clique_number"] = omega
    pairs = [tuple(p) for p in cert["pairs"]]
    bad = [list(s) for s in cert["supports"]]
    bad[0], bad[1] = bad[0] + bad[1][:1], bad[1][1:]
    for label, fn in (
        ("merged_support_rejected", lambda: V.check_fitting_supports(bad, pairs, plane_orth(labels, pairs))),
        ("non_orthogonal_pair_rejected", lambda: plane_orth(labels, bad_matching(labels, pairs))),
        ("pr1825_supports_on_new_pairs_rejected", lambda: V.check_fitting_supports(
            json.loads(PR1825_CERT.read_text())["rank49_supports"], pairs, plane_orth(labels, pairs))),
    ):
        try:
            fn()
        except (V.CheckFailure, ValueError, AssertionError, KeyError, TypeError) as error:
            out[label] = "rejected: " + str(error)[:100]
        else:
            raise AssertionError("control accepted: " + label)
    return out


PR1825_CERT = ROOT / "research/paired-plane-minrank-bracket-audit/CERTIFICATE.json"


def main():
    labels, pairs0, orth0 = model()
    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    result, pairs, orth = check(cert, labels)
    result["controls"] = controls(cert, labels, pairs0, orth0)
    result["status"] = "PASS_PAIRED_PLANE_REMATCH_RANK34"
    result["pr1825_matching_exact_rank_cited_from_pr2484"] = 49
    # Pairwise orthogonal Gram-I2 planes have orthonormal, hence independent, spanning labels: 2k <= 9, k <= 4.
    result["colouring_method_floor"] = 2 * -(-56 // 4)
    want = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8")) if (HERE / "RESULT.json").exists() else None
    if "--write" in sys.argv:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return
    V.need(want == json.loads(json.dumps(result)), "recomputed result differs from RESULT.json")
    print("PASS_PAIRED_PLANE_REMATCH_RANK34 exact_rank=34 pr1825=49 clique=17 supports=34 no_new_kappa")


if __name__ == "__main__":
    main()
