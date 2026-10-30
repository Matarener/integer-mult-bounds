"""Parabolic-pattern proof certificate for the relative 27-deletion bound.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
The scalar support classification is the Weyl/parabolic argument of PR3166.
This scan is distinct from neighbor_audit.py's fixed-root kernel strata.
"""

from collections import Counter
from functools import reduce
from math import gcd

from finite_inputs import SIMPLE, inverse
from vendor.pr3755 import geometry as g


def run(roots, labels):
    inv = inverse(list(zip(*SIMPLE)))
    supports = []
    for root in roots:
        coeff = [sum(x * y for x, y in zip(row, root)) for row in inv]
        g.require(all(x >= 0 for x in coeff) or all(x <= 0 for x in coeff),
                  "positive simple-root pattern")
        supports.append(sum(1 << i for i, x in enumerate(coeff) if x))
    characters = [sum(1 << i for i, u in enumerate(labels) if g.parity(u & z))
                  for z in range(1, 512)]
    stars = [characters[label - 1] for label in labels]
    g.require(all(x.bit_count() == 64 for x in stars), "root character has wrong size")
    full = (1 << 120) - 1
    minimum = 120
    witness = None
    patterns = []
    comparisons = 0
    accepted = 0
    for subset in range(255):
        zero = sum(1 << i for i, support in enumerate(supports) if support & ~subset == 0)
        if subset.bit_count() == 7 and zero.bit_count() == 63:
            # Precisely the rank-seven root-normal (E7) class.
            g.require(sum(all(g.dot(root, roots[i]) == 0
                              for i in range(120) if zero >> i & 1) for root in roots) == 1,
                      "excluded E7 class is not a root-normal class")
            continue
        off = full ^ zero
        best = 120
        valid = 0
        for v, ov in enumerate(stars):
            forced = off & ov
            for z, oz in enumerate(characters, 1):
                comparisons += 1
                if forced & oz:
                    continue
                valid += 1
                deleted = off & oz
                count = deleted.bit_count()
                g.require(deleted & ov == 0, "relative deletion leaves neighbor set")
                best = min(best, count)
                if count < minimum:
                    minimum = count
                    witness = {"simple_subset": subset, "zero_root_lines": zero.bit_count(),
                               "root": v, "character": z, "deletion_count": count,
                               "deleted_root_indices": [i for i in range(120) if deleted >> i & 1]}
        accepted += valid
        patterns.append({"simple_subset": subset, "zero_root_lines": zero.bit_count(),
                         "minimum_neighbor_deletions": best, "admissible_root_character_pairs": valid})
    g.require(len(patterns) == 254 and minimum == 27, "relative nonroot deletion threshold")
    g.require(witness is not None and witness["simple_subset"].bit_count() == 7,
              "minimum needs a concrete one-dimensional normal witness")
    rows = [SIMPLE[i] for i in range(8) if witness["simple_subset"] >> i & 1]
    normal = [(-1) ** j * g.determinant([row[:j] + row[j + 1:] for row in rows]) for j in range(8)]
    divisor = reduce(gcd, (abs(x) for x in normal))
    normal = [x // divisor for x in normal]
    if next(x for x in normal if x) < 0:
        normal = [-x for x in normal]
    g.require(all(sum(a * b for a, b in zip(row, normal)) == 0 for row in rows), "cofactor normal")
    g.require(not any(g.rational_rank([root, normal]) == 1 for root in roots), "nonroot witness is a root")
    oz = characters[witness["character"] - 1]
    actual = [i for i, root in enumerate(roots) if oz >> i & 1 and g.dot(root, normal)]
    g.require(actual == witness["deleted_root_indices"], "relative threshold witness support")
    witness["normal"] = normal
    return {"nonroot_parabolic_patterns": len(patterns), "root_character_comparisons": comparisons,
            "admissible_pairs": accepted, "minimum_nonroot_neighbor_deletions": minimum,
            "witness": witness, "pattern_minima": patterns}


def low_weight_run(roots, labels):
    """All nonroot parabolic zero patterns and all pivots for binary weight seven."""
    inv = inverse(list(zip(*SIMPLE)))
    supports = []
    for root in roots:
        coeff = [sum((x * y for x, y in zip(row, root))) for row in inv]
        supports.append(sum((1 << i for i, x in enumerate(coeff) if x)))
    chars = [0] + [sum((1 << i for i, u in enumerate(labels) if g.parity(u & z))) for z in range(1, 512)]
    full = (1 << 120) - 1
    hist = Counter()
    minimum = 121
    witness = None
    patterns = 0
    admissible = 0
    for subset in range(255):
        zero = sum((1 << i for i, s in enumerate(supports) if not s & ~subset))
        if subset.bit_count() == 7 and zero.bit_count() == 63:
            continue
        patterns += 1
        off = full ^ zero
        for v, label in enumerate(labels):
            forced = off & chars[label]
            rank = g.binary_rank((labels[i] for i in range(120) if forced >> i & 1))
            hist[rank] += 1
            if rank >= 8:
                continue
            g.require(rank == 7, 'nonroot forced binary rank belowseven')
            allowed = [z for z in range(1, 512) if not forced & chars[z]]
            g.require(len(allowed) == 3 and allowed[0] ^ allowed[1] == allowed[2], 'nonroot uniqueannplane')
            deleted = off & (chars[allowed[0]] | chars[allowed[1]])
            count = deleted.bit_count()
            admissible += 1
            g.require(not deleted & chars[label], 'allrequireddeletionsinneighbors')
            if count < minimum:
                minimum = count
                witness = {'subset': subset, 'v': v, 'chars': allowed, 'deleted': [i for i in range(120) if deleted >> i & 1]}
    g.require(patterns == 254 and minimum == 55, 'nonroot neighborweightseven threshold55')
    g.require(dict(hist) == {7: 6, 8: 30474} and admissible == 6, 'all nonroot low-weight pattern pivots')
    rows = [SIMPLE[i] for i in range(8) if witness['subset'] >> i & 1]
    g.require(len(rows) == 7, 'attaining nonroot zero pattern has a one-dimensional kernel')
    normal = [(-1) ** j * g.determinant([row[:j] + row[j + 1:] for row in rows]) for j in range(8)]
    divisor = reduce(gcd, (abs(x) for x in normal))
    normal = [x // divisor for x in normal]
    if next((x for x in normal if x)) < 0:
        normal = [-x for x in normal]
    g.require(not any((g.rational_rank([r, normal]) == 1 for r in roots)), 'nonroot low witness is a root')
    off_normal = {i for i, r in enumerate(roots) if g.dot(r, normal)}
    required = [i for i in off_normal if any((chars[z] >> i & 1 for z in witness['chars']))]
    g.require(sorted(required) == witness['deleted'], 'explicit nonroot low support witness')
    g.require(g.binary_rank((labels[i] for i in off_normal - set(required))) == 7, 'attained nonroot low weight')
    witness['normal'] = normal
    return {'patterns': patterns, 'ordered_pattern_pivots': patterns * 120, 'forced_rank_histogram': dict(hist), 'admissible_planes': admissible, 'minimum': minimum, 'witness': witness}
