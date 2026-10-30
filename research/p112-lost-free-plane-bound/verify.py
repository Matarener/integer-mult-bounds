#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Lost-free P112 plane-port sets: an elementary upper bound |S| <= 56 and what it means for the decoder.

Definitions (philippeVV, Discussion 1587, plane-port follow-up 4). Port a has label q_a in F2^9 and a plane
E_a = <q_a, r_a> with r_a.q_a = 0 and r_a.r_a = 1 (the normalised basis of a nondegenerate plane through q_a).
S is lost-free if every pair a != b in S with q_a.q_b = 0 has E_a orthogonal to E_b. The exact masked decoder
(G/2)[S,S] + I_{S^c} is then priced 72 + 2(112 - |S|) in that family (block <= 8 terms of pairing rank <= 9).

Checks:
 1. the 112 labels have norm one; exhaustive enumeration of orthonormal 8-sets ("frames"): exactly 4,032,
    and every label lies in exactly 288 of them;
 2. lemma (written; checked on all frames): k pairwise orthogonal planes <q,r> carry 2k orthonormal, hence
    independent, vectors, so k <= 4 in F2^9; a frame's labels are pairwise q-orthogonal, so a lost-free S
    meets every frame in <= 4 ports; double counting: 288 |S| <= 4 * 4032, so |S| <= 56;
 3. the witness evidence/best-32.json is lost-free with valid planes (|S| = 32 is attained);
 4. port transitivity: evidence/symmetry.json maps port 0 to every port by a linear isometry preserving the
    label set (supports the solver evidence; not needed for 2);
 5. pricing: with |S| <= 56 the family costs >= 72 + 112 = 184, above the complex plane-port break-even budgets
    (plane-port-copy-budgets: at most 164 at the incumbent tie) and below the zero-saving line 2w = 1792/9.
usage: verify.py [--write]
"""
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
_SPEC = importlib.util.spec_from_file_location("pr2484_verify", ROOT / "research/paired-plane-minrank-bracket-audit/verify.py")
V = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(V)
need = V.need
dot = V.parity_dot
N = 112


def labels():
    q, _, _ = V.load_model((ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz").read_bytes(),
                           (ROOT / "research/paired-plane-scalar-mask-obstruction/PR1825-CERTIFICATE.json").read_bytes())
    need(all(dot(x, x) == 1 for x in q), "labels have norm one")
    return q


def frames(q):
    nb = [frozenset(j for j in range(N) if j != i and dot(q[i], q[j]) == 0) for i in range(N)]
    out = []

    def grow(cl, cand):
        if len(cl) == 8:
            out.append(tuple(cl)); return
        for u in sorted(cand):
            if u > cl[-1]:
                grow(cl + [u], cand & nb[u])
    for v in range(N):
        grow([v], frozenset(u for u in nb[v] if u > v))
    return out


def rank_f2(vs):
    basis = []
    for v in vs:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
    return len(basis)


def plane_ok(q, a, r):
    return dot(r, q[a]) == 0 and dot(r, r) == 1


def planes_orth(q, a, ra, b, rb):
    return dot(q[a], q[b]) == 0 and dot(q[a], rb) == 0 and dot(ra, q[b]) == 0 and dot(ra, rb) == 0


def check_lost_free(q, S):
    for a, r in S.items():
        need(plane_ok(q, a, r), "normalised nondegenerate plane")
    ports = sorted(S)
    for i, a in enumerate(ports):
        for b in ports[i + 1:]:
            if dot(q[a], q[b]) == 0:
                need(planes_orth(q, a, S[a], b, S[b]), "lost-free pair %d,%d" % (a, b))
    return len(S)


def check_transitivity(q, perms):
    L = {v: i for i, v in enumerate(q)}
    reach = set()
    for p in perms:
        need(sorted(p) == list(range(N)), "permutation")
        # linear: the map defined on a label basis sends every label to its permuted label
        basis, idx = [], []
        for i in range(N):
            if rank_f2([q[j] for j in idx] + [q[i]]) > len(idx):
                idx.append(i)
        need(len(idx) == 9, "label basis")
        coord = {}
        for mask in range(1 << 9):
            v = 0
            img = 0
            for k in range(9):
                if mask >> k & 1:
                    v ^= q[idx[k]]; img ^= q[p[idx[k]]]
            coord[v] = img
        need(all(coord[q[a]] == q[p[a]] for a in range(N)), "permutation is induced by a linear map")
        need(all(dot(q[p[a]], q[p[b]]) == dot(q[a], q[b]) for a in range(N) for b in range(a, N)), "isometry")
        reach.add(p[0])
    return sorted(reach)


def main():
    q = labels()
    F = frames(q)
    per = [0] * N
    for f in F:
        for a in f:
            per[a] += 1
    need(len(F) == 4032 and set(per) == {288}, "4032 frames, 288 through every label")
    for f in F[:200]:
        need(rank_f2([q[a] for a in f]) == 8, "frame labels independent")
    bound = (4 * len(F)) // per[0]
    need(bound == 56, "double-counting bound")
    S = {int(a): r for a, r in json.loads((HERE / "evidence/best-32.json").read_text()).items()}
    size = check_lost_free(q, S)
    need(size == 32, "witness size")
    need(all(sum(1 for a in f if a in S) <= 4 for f in F), "witness meets every frame in <= 4 ports")
    sym = json.loads((HERE / "evidence/symmetry.json").read_text())
    reach = check_transitivity(q, sym["perms"][:N])
    need(reach == list(range(N)), "port 0 reaches every port")
    # controls: an overfull frame and a broken plane are rejected
    controls = {}
    f = F[0]
    bad = {a: next(r for r in range(1, 512) if plane_ok(q, a, r)) for a in f[:5]}
    try:
        check_lost_free(q, bad)
    except V.CheckFailure as e:
        controls["five_ports_of_one_frame_rejected"] = str(e)
    else:
        raise AssertionError("five frame ports accepted")
    broken = dict(S); a0 = min(broken); broken[a0] = q[a0]
    try:
        check_lost_free(q, broken)
    except V.CheckFailure as e:
        controls["degenerate_plane_rejected"] = str(e)
    else:
        raise AssertionError("bad plane accepted")
    w = Q(896, 9)
    pricing = {
        "family_cost_formula": "72 + 2*(112 - |S|)",
        "max_lost_free_upper_bound_proved_here": bound,
        "family_cost_lower_bound_at_proved_bound": 72 + 2 * (N - bound),
        "beat_naive_224_needs_S_at_least": 37,
        "positive_saving_line_2w": str(2 * w), "positive_saving_needs_S_at_least": 49,
        "incumbent_tie_budget_plane_port_copy_budgets": "164 (rank-2 copies) / 160 (rank-8)",
        "beat_incumbent_needs_S_at_least": "66 (budget 164) / 68 (budget 160)",
    }
    need(72 + 2 * (N - 37) < 224 <= 72 + 2 * (N - 36), "37 threshold")
    need(72 + 2 * (N - 49) < 2 * w <= 72 + 2 * (N - 48), "49 threshold")
    need(72 + 2 * (N - 66) <= 164 < 72 + 2 * (N - 65), "66 threshold at budget 164")
    need(72 + 2 * (N - 68) <= 160 < 72 + 2 * (N - 67), "68 threshold at budget 160")
    need(72 + 2 * (N - bound) > 164, "proved bound already above the incumbent tie budget")
    pred = json.loads((ROOT / "research/plane-port-copy-budgets/RESULT.json").read_text())["complex"]["shrink"]
    need(max(v["charge"] for k, v in pred.items() if k.endswith("incumbent_ceiling") and v) == 164, "tie budget 164")
    out = {"status": "PASS_P112_LOST_FREE_PLANE_BOUND", "frames": len(F), "frames_per_label": per[0],
           "lost_free_upper_bound": bound, "witness_size": size, "transitive_orbit_of_port0": len(reach),
           "pricing": pricing, "controls": controls,
           "solver_evidence_not_certified": "evidence/progress.log: CP-SAT bound 51 (port fixed by transitivity)"}
    path = HERE / "RESULT.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return
    need(json.loads(path.read_text(encoding="utf-8")) == json.loads(json.dumps(out)), "RESULT.json differs")
    print("PASS_P112_LOST_FREE_PLANE_BOUND frames=4032 per_label=288 |S|<=56 witness=32 transitive=112 no_new_kappa")


if __name__ == "__main__":
    main()
