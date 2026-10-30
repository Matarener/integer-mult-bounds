"""All-position exact root-normal rank-seven correction certificate.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
The self-root branch uses the written union-of-three-cuts argument and the
full remainder24 input recomputed by finite_inputs. The neighbor branch
checks its unique two-dimensional annihilator, independently of the fixed-v
all-plane audit in root_low_audit.py.
"""
from collections import Counter
from vendor.pr3755 import geometry as g

def run(roots, labels):
    cuts = [0] + [sum(1 << i for i, u in enumerate(labels) if g.parity(z & u))
                  for z in range(1, 512)]
    off = [sum(1 << i for i, row in enumerate(roots) if g.dot(row, root)) for root in roots]
    hist = Counter()
    checked = 0
    witness = None
    for v, label in enumerate(labels):
        ov = cuts[label]
        for a, root in enumerate(roots):
            forced = off[a] & ov
            rank = g.binary_rank(labels[i] for i in range(120) if forced >> i & 1)
            expected = 1 if a == v else 7 if g.dot(roots[v], root) else 8
            g.require(rank == expected, "forced outside-neighbor root rank type")
            hist[rank] += 1
            if expected != 7:
                continue
            allowed = [z for z in range(1, 512) if not cuts[z] & forced]
            g.require(len(allowed) == 3 and allowed[0] ^ allowed[1] == allowed[2],
                      "unique two-dimensional annihilator")
            deleted = off[a] & (cuts[allowed[0]] | cuts[allowed[1]])
            g.require(deleted & ov == 0 and deleted.bit_count() == 29,
                      "neighbor root weight-seven correction threshold")
            remaining = off[a] & ~deleted
            g.require(g.binary_rank(labels[i] for i in range(120) if remaining >> i & 1) == 7,
                      "attaining corrected root word has binary weight seven")
            if witness is None:
                witness = {"pivot": v, "root_normal": a, "characters": allowed,
                           "deleted_indices": [i for i in range(120) if deleted >> i & 1]}
            checked += 1
    g.require(dict(hist) == {1: 120, 7: 6720, 8: 7560} and checked == 6720,
              "all ordered root-pivot pairs covered")
    return {"ordered_root_pairs": 14400, "forced_label_rank_histogram": dict(sorted(hist.items())),
            "unique_neighbor_annihilator_planes": checked,
            "minimum_root_weight_seven_neighbor_deletions": 29,
            "self_root_lower_bound_from_three_cuts": 36,
            "witness": witness}
