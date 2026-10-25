"""Exact finite inputs for the sharp P112 six/seven-flat theorem.

conorholds, with OpenAI Codex assistance. Apache-2.0.
The primary engine uses the declared simple-root coordinates and polar equations.
The mathematical argument, including the characteristic-zero transfer, is separate.
"""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
from types import ModuleType


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
CONSUMED_INPUTS = {"research/p112-root-simplex-exclusion/geometry.py",
                   "research/one-sided-decoders-all-m/data/data.json"}
RETAINED_INPUTS = {"inputs/pr3154/land_e2_k8.out", "inputs/pr3154/land_e3_k8.out"}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    def constant(_):
        raise ValueError("nonfinite JSON number")

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return sha256(canonical_json(value).encode()).hexdigest()


def regular_bytes(root, name):
    relative = Path(name)
    need(not relative.is_absolute() and all(x not in (".", "..") for x in relative.parts),
         "noncanonical source path")
    path = root
    for part in relative.parts:
        path /= part
        need(not path.is_symlink(), "linked source input")
    need(path.is_file(), "missing source input")
    return path.read_bytes()


def authenticate():
    sources = strict_json(regular_bytes(PACKAGE, "SOURCES.json"))
    live = [row["path"] for row in sources["files"] if row["usage"] == "input"]
    retained = [row["retained_path"] for row in sources["retained_pr_sources"]]
    need(len(live) == len(CONSUMED_INPUTS) and set(live) == CONSUMED_INPUTS,
         "source inventory differs from consumed inputs")
    need(len(retained) == len(RETAINED_INPUTS) and set(retained) == RETAINED_INPUTS,
         "retained source inventory differs from consumed inputs")
    need(len({row["path"] for row in sources["files"]}) == len(sources["files"]),
         "duplicate source row")
    checked = []
    for row in sources["files"]:
        if row["usage"] == "input":
            raw = regular_bytes(ROOT, row["path"])
            need(sha256(raw).hexdigest() == row["sha256"], "live source hash differs")
            checked.append(row["path"])
    for row in sources["retained_pr_sources"]:
        raw = regular_bytes(PACKAGE, row["retained_path"])
        need(sha256(raw).hexdigest() == row["sha256"], "retained PR source hash differs")
        checked.append(row["retained_path"])
    return checked


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def span_coordinates(rows):
    """Coordinates in an incrementally selected basis, not row positions."""
    pivots, coordinates = {}, []
    for value in rows:
        coordinate = 0
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot][0]
                coordinate ^= pivots[pivot][1]
            else:
                bit = 1 << len(pivots)
                pivots[pivot] = (value, coordinate ^ bit)
                coordinate = bit
                break
        coordinates.append(coordinate)
    return len(pivots), coordinates


def rational_rank(rows):
    matrix = [[Fraction(x) for x in row] for row in rows]
    if not matrix:
        return 0
    row = 0
    for col in range(len(matrix[0])):
        pivot = next((i for i in range(row, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[row], matrix[pivot] = matrix[pivot], matrix[row]
        scale = matrix[row][col]
        matrix[row] = [x / scale for x in matrix[row]]
        for i in range(row + 1, len(matrix)):
            scale = matrix[i][col]
            if scale:
                matrix[i] = [x - scale * y for x, y in zip(matrix[i], matrix[row])]
        row += 1
    return row


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


class Geometry:
    def __init__(self):
        authenticate()
        path = ROOT / "research/p112-root-simplex-exclusion/geometry.py"
        module = ModuleType("six_seven_frozen_geometry")
        module.__file__ = str(path)
        exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
        self.source = module
        roots, points, _, coordinates = module.root_data()
        self.roots, self.points = roots, points
        self.index = {r: i for i, r in enumerate(roots)}
        self.residues = tuple(sum((int(x) % 2) << j for j, x in enumerate(c))
                              for c in coordinates)
        self.labels = tuple(1 | (r << 1) for r in self.residues)
        self.by_residue = {x: i for i, x in enumerate(self.residues)}
        self.all = (1 << 120) - 1
        self.live = sum(1 << self.index[r] for r in points)
        self.frame = self.all ^ self.live
        self.dots = tuple(tuple(module.dot(a, b) for b in roots) for a in roots)
        self.neighbors = tuple(sum(1 << j for j, value in enumerate(row) if abs(value) == 4)
                               for row in self.dots)
        self.off = tuple(self.neighbors[i] | (1 << i) for i in range(120))
        gram = [[module.dot(a, b) // 4 for b in module.SIMPLE] for a in module.SIMPLE]
        edges = [(i, j) for i in range(8) for j in range(i + 1, 8) if gram[i][j] % 2]
        self.q = tuple((x.bit_count() + sum(((x >> i) & 1) * ((x >> j) & 1)
                                          for i, j in edges)) % 2 for x in range(256))
        need(len(set(self.residues)) == 120 and rank(self.labels) == 9,
             "declared root-label embedding")
        need({x for x in range(256) if self.q[x]} == set(self.residues),
             "quadratic anisotropic points differ from roots")
        need(sum((-1) ** y for y in self.q) == 16, "ambient Gauss sign")
        polar_rows = [sum(self.b(1 << i, 1 << j) << j for j in range(8))
                      for i in range(8)]
        need(rank(polar_rows) == 8, "degenerate polar model")
        need(all(self.b(self.residues[i], self.residues[j]) == (self.dots[i][j] // 4) % 2
                 for i in range(120) for j in range(120)), "polar/root pairing binding")
        need(Counter((x & self.live).bit_count() for x in self.off) == {53: 112, 56: 8},
             "root off-support convention")
        need(all((self.neighbors[i] & self.frame).bit_count()
                 == (0 if self.frame >> i & 1 else 4) for i in range(120)),
             "fixed-frame incidence")
        self.polar_masks = tuple(sum(1 << i for i, r in enumerate(self.residues) if self.b(x, r))
                                 for x in range(256))

    def b(self, a, b):
        return self.q[a ^ b] ^ self.q[a] ^ self.q[b]

    def affine_sections(self):
        """Every polar two-plane, with all four affine right-hand sides."""
        for a in range(1, 256):
            for b in range(a + 1, 256):
                if (a ^ b) < b:
                    continue
                for alpha in range(2):
                    for beta in range(2):
                        ma = self.polar_masks[a] if alpha else self.all ^ self.polar_masks[a]
                        mb = self.polar_masks[b] if beta else self.all ^ self.polar_masks[b]
                        yield a, b, ma & mb


def completion_checks(g):
    counts, qualifiers, maximum, total = Counter(), [], 0, 0
    for a, b, section in g.affine_sections():
        total += 1
        counts[section.bit_count()] += 1
        for v in range(120):
            full_intersection = section & g.off[v]
            maximum = max(maximum, full_intersection.bit_count())
            if (full_intersection & g.live).bit_count() < 29:
                continue
            need(section.bit_count() == 32, "large residual has no32 completion")
            need(section & ~g.neighbors[v] == 0, "completion contains self or orthogonal root")
            rv = g.residues[v]
            need(rv in (a, b, a ^ b), "normal not in affine annihilator")
            mates = [g.by_residue[x] for x in (a, b, a ^ b)
                     if x in g.by_residue and x != rv and not g.b(rv, x)]
            need(len(mates) == 1, "completion mate is not unique")
            w = mates[0]
            need(not g.dots[v][w] and section == g.neighbors[v] & ~g.neighbors[w],
                 "wrong orthogonal completion orientation")
            qualifiers.append((v, w))
    expected = []
    full_count = 0
    for v in range(120):
        for w in range(120):
            if g.dots[v][w]:
                continue
            full_count += 1
            section = g.neighbors[v] & ~g.neighbors[w]
            need(section.bit_count() == 32, "orthogonal completion size")
            need(rank(g.labels[i] for i in indices(section)) == 7, "completion rank")
            if (section & g.live).bit_count() >= 29:
                expected.append((v, w))
    need(total == 43180 and full_count == 7560 and maximum == 32,
         "incomplete affine/root domain or wrong cap")
    need(len(qualifiers) == len(set(qualifiers)) and sorted(qualifiers) == sorted(expected),
         "large completion classification is incomplete")
    return {"count": total, "cardinality_histogram": {str(k): v for k, v in sorted(counts.items())},
            "qualifying29": len(qualifiers), "completion_digest": digest(sorted(qualifiers))}, full_count


def core_checks(g):
    aggregate, pairs = Counter(), 0
    optimal, per_word = [], Counter()
    small_flat_count = 0
    for v, w in combinations(range(120), 2):
        if g.dots[v][w]:
            continue
        core = g.neighbors[v] & g.neighbors[w]
        ids = list(indices(core))
        dim, coordinates = span_coordinates(g.labels[i] for i in ids)
        need(len(ids) == 24 and dim == 7, "common core cardinality/rank")
        sections = Counter()
        for f in range(1, 128):
            low = sum(1 << i for i, x in zip(ids, coordinates) if not ((f & x).bit_count() % 2))
            sections[low.bit_count()] += 1
            if low.bit_count() != 16 or low & g.frame:
                continue
            for normal, mate in ((v, w), (w, v)):
                high = g.neighbors[normal] & ~g.neighbors[mate] & g.live
                target = g.off[normal] & g.live
                sparse = target & ~(low | high)
                floor = 5 if g.live >> normal & 1 else 8
                if sparse.bit_count() != floor:
                    continue
                need(high.bit_count() == 32 and not high & low,
                     "uniform cover partition changed")
                need([rank(g.labels[i] for i in indices(part)) for part in (high, low, sparse)]
                     == [7, 6, 4], "uniform cover support ranks")
                if floor == 5:
                    need(sparse >> normal & 1
                         and rank(g.labels[i] for i in indices(sparse ^ (1 << normal))) == 3,
                         "uniform four-plus-self boundary")
                    four = list(indices(sparse ^ (1 << normal)))
                    closure = {g.labels[i] for i in four}
                    closure.update(g.labels[normal] ^ g.labels[four[0]] ^ g.labels[i]
                                   for i in four)
                    roots = {i for i, label in enumerate(g.labels) if label in closure}
                    need(len(closure) == len(roots) == 8
                         and all(g.live >> i & 1 for i in roots), "small flat root closure")
                    need(sum(1 << i for i in roots if g.dots[normal][i]) == sparse,
                         "small flat contains extra nonorthogonal roots")
                    small_flat_count += 1
                if not per_word[normal]:
                    for i in indices(g.live):
                        coefficient = g.dots[normal][i] // 4
                        need(sum(coefficient for part in (high, low, sparse) if part >> i & 1)
                             == coefficient, "uniform coefficient partition")
                optimal.append((normal, mate, low))
                per_word[normal] += 1
        need(sections == {0: 1, 8: 15, 12: 96, 16: 15}, "core hyperplane capacity")
        aggregate.update(sections)
        pairs += 1
    need(pairs == 3780, "incomplete orthogonal-pair domain")
    need(all(per_word[i] == (3 if g.live >> i & 1 else 945) for i in range(120)),
         "uniform optimal-cover count")
    need(small_flat_count == 336, "nonframe small-flat inventory")
    return {"pairs": pairs, "forms_per_pair": 127,
            "aggregate_histogram": {str(k): v for k, v in sorted(aggregate.items())},
            "uniform_sharpness": {"nonframe_words": 112, "frame_words": 8,
                                  "five_site_covers": sum(per_word[i] for i in indices(g.live)),
                                  "eight_site_covers": sum(per_word[i] for i in indices(g.frame)),
                                  "covers_per_nonframe_word": 3, "covers_per_frame_word": 945,
                                  "partition_ranks": [7, 6, 4],
                                  "nonframe_small_flats": small_flat_count,
                                  "nonframe_small_flat_roots": 8,
                                  "extra_orthogonal_roots": 3,
                                  "cover_digest": digest(sorted(optimal))}}


def root764_checks(g):
    """Complementary 28-sections, using ambient dual masks rather than local bases."""
    polar_one = [sum(1 << i for i, residue in enumerate(g.residues) if g.b(a, residue))
                 for a in range(256)]
    sections, pairs = set(), 0
    for v, residue in enumerate(g.residues):
        local = set()
        for a in range(256):
            if not g.b(residue, a):
                continue
            for offset in (0, 1):
                section = g.neighbors[v] & (polar_one[a] if offset else g.all ^ polar_one[a])
                need(section.bit_count() == 28, "root764 complementary section28")
                local.add(section)
        need(len(local) == 128, "root764 complementary multiplicity")
        pairs += len(local)
        sections.update(local)
    dual_masks = [sum(1 << i for i, label in enumerate(g.labels)
                      if not ((label & a).bit_count() & 1)) for a in range(512)]
    for section in sections:
        need(rank(g.labels[i] for i in indices(section)) == 7, "root764 complementary rank7")
        need(Counter((section & cut).bit_count() for cut in dual_masks)
             == {0: 4, 12: 252, 16: 252, 28: 4}, "root764 complementary cut capacities")
    return {"root_high_pairs": pairs, "c28_sections": len(sections),
            "c28_section_histogram": {"0": 1, "12": 63, "16": 63},
            "c28_digest": sha256(json.dumps(sorted(sections), separators=(",", ":")).encode()).hexdigest()}


def quotient6_checks():
    """All affine codimension-one/two sections of the split six-quadric."""
    roots = [x for x in range(64)
             if sum(((x >> (2*j)) & 1) * ((x >> (2*j+1)) & 1) for j in range(3)) & 1]
    hist = {4: Counter(), 5: Counter()}
    for a in range(1, 64):
        for offset in (0, 1):
            hist[5][sum(((a & x).bit_count() & 1) == offset for x in roots)] += 1
        for b in range(a + 1, 64):
            if b > (a ^ b):
                continue
            for first in (0, 1):
                for second in (0, 1):
                    count = sum(((a & x).bit_count() & 1) == first
                                and ((b & x).bit_count() & 1) == second for x in roots)
                    hist[4][count] += 1
    need(len(roots) == 28 and sum(hist[4].values()) == 2604
         and sum(hist[5].values()) == 126 and max(hist[4]) == 10 and max(hist[5]) == 16,
         "six-quadric affine capacities")
    return {str(d): {str(k): v for k, v in sorted(counts.items())}
            for d, counts in hist.items()}


def witness_checks(g):
    vroot, wroot = (2, 0, 2, 0, 0, 0, 0, 0), (2, 0, -2, 0, 0, 0, 0, 0)
    v, w = g.index[vroot], g.index[wroot]
    x = g.neighbors[v] & ~g.neighbors[w] & g.live
    yr = {tuple(2 if j == center else sign * 2 if j == other else 0 for j in range(8))
          for center in (0, 2) for other in range(4, 8) for sign in (-1, 1)}
    y = sum(1 << g.index[r] for r in yr)
    target = g.off[v] & g.live
    sparse = target & ~(x | y)
    supports = [sparse, y, x]
    sizes = [m.bit_count() for m in supports]
    ranks = [rank(g.labels[i] for i in indices(m)) for m in supports]
    need(sizes == [5, 16, 32] and ranks == [4, 6, 7], "sharp witness changed")
    need(not x & y and (sparse | y | x) == target, "witness is not a disjoint partition")
    old = strict_json(regular_bytes(ROOT, "research/one-sided-decoders-all-m/data/data.json"))
    old_roots = [tuple(int(2 * Fraction(str(z))) for z in r) for r in old["L"]]
    old_frame = [tuple(int(2 * Fraction(str(z))) for z in r) for r in old["F0"]]
    need(set(old_roots) == set(g.points) and set(old_roots + old_frame) == set(g.roots),
         "old/new root or frame binding")
    graph = [old_label | (g.labels[g.index[r]] << 9)
             for r, old_label in zip(old_roots + old_frame, old["LAB"] + old["Z"])]
    need(rank(graph) == 9 and rank(old["LAB"] + old["Z"]) == 9, "old/new label map")
    for i, r in enumerate(old_roots):
        need(old["FC"][i] == [g.source.dot(r, f) // 4 for f in old_frame],
             "historical frame coefficient row")
    small_four = sparse ^ (1 << v)
    four_supports = [x, y, small_four, 1 << v]
    qrows = [[Fraction(g.dots[v][g.index[r]], 4) if (m >> g.index[r]) & 1 else Fraction(0)
              for m in four_supports] for r in old_roots]
    need(all(sum(qrows[i]) == Fraction(g.source.dot(vroot, r), 4)
             for i, r in enumerate(old_roots)), "coefficient identity")
    c_rank = rational_rank(old["FC"])
    q_rank = rational_rank(qrows)
    joint = rational_rank([old["FC"][i] + qrows[i] for i in range(112)])
    need((c_rank, q_rank, joint) == (8, 4, 11), "slack-nine intersection")
    sranks = [rank(g.labels[i] for i in indices(m)) for m in four_supports]
    need(sranks == [7, 6, 3, 1], "slack-nine support ranks")
    return {"sizes": sizes, "ranks": ranks,
            "sparse_indices": [i for i, r in enumerate(old_roots) if sparse >> g.index[r] & 1],
            "slack9": {"sizes": [m.bit_count() for m in four_supports], "ranks": sranks,
                       "code_rank": c_rank, "pieces_rank": q_rank, "joint_rank": joint, "cost": 17}}


def frame_plane_checks(g):
    """All G4 cuts, by the ambient dual no-coloop criterion."""
    phases = [(normal, sum(1 << i for i in indices(g.live)
                            if (normal & g.labels[i]).bit_count() % 2))
              for normal in range(1, 512)]
    masks = [mask for _, mask in phases]
    records, minimum = [], 112
    for i in indices(g.frame):
        matched = [mask for normal, mask in phases
                   if not (normal & g.labels[i]).bit_count() % 2]
        need(len(matched) == 255, "matched frame hyperplane inventory")
        for j in indices(g.frame):
            if i == j:
                continue
            for coefficient in (1, -1, 2):
                off = sum(1 << k for k in indices(g.live)
                          if g.dots[i][k] + coefficient * g.dots[j][k])
                for outside in matched:
                    deleted = off & outside
                    counts = [(deleted & mask).bit_count() for mask in masks]
                    need(counts.count(0) == 1 and 1 not in counts,
                         "frame-plane rank or one-point deletion failed")
                    minimum = min(minimum, deleted.bit_count())
                    records.append((i, j, coefficient, deleted))
    need(len(records) == 42840, "frame-plane case inventory")
    return {"cases": len(records), "minimum_deleted": minimum,
            "rank": 8, "all_one_point_deletions_preserve_rank": True,
            "case_digest": digest(sorted(records))}


def invoice_profile_checks():
    capacity = {1: 1, 2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}
    answer = {}
    for length, budget in ((3, 16), (4, 16), (4, 17)):
        kept, examined = [], 0
        for ascending in combinations_with_replacement(range(1, 8), length):
            if sum(ascending) > budget:
                continue
            examined += 1
            weights = list(reversed(ascending))
            bound = sum(capacity[w] for w in weights)
            if bound < 53:
                continue
            if bound < 70 and sum(32 if w == 7 else capacity[w] for w in weights) < 53:
                continue
            remaining = weights.copy()
            if 7 in remaining and 6 in remaining:
                remaining.remove(7)
                remaining.remove(6)
                if all(w <= 3 for w in remaining) and sum(1 << (w - 1) for w in remaining) <= 4:
                    continue
            kept.append(weights)
        answer[str(length) + ":" + str(budget)] = {"examined": examined, "survivors": sorted(kept)}
    need(answer["3:16"]["survivors"] == [[7, 7, 1], [7, 7, 2]]
         and answer["4:16"]["survivors"] == [[7, 7, 1, 1]]
         and answer["4:17"]["survivors"] == [[7, 5, 4, 1], [7, 6, 3, 1],
                                              [7, 7, 1, 1], [7, 7, 2, 1]],
         "actual-invoice profile exhaustion")
    return answer


def d2_profile_checks():
    cap = (0, 1, 2, 4, 8, 12, 20, 36)
    answer = {}
    for length, budget in ((4, 24), (5, 25)):
        candidates, examined = [], 0
        for ascending in combinations_with_replacement(range(1, 8), length):
            if sum(ascending) > budget:
                continue
            examined += 1
            weights = list(reversed(ascending))
            if weights[0] <= 6:
                # Four-six-plus-nine, or the sole 55555 boundary and distance53.
                continue
            remaining = weights[1:]
            crude = sum(cap[w] for w in remaining)
            if crude < 53 or (crude < 70 and sum(32 if w == 7 else cap[w]
                                                for w in remaining) < 53):
                continue
            sparse = remaining.copy()
            if 7 in sparse and 6 in sparse:
                sparse.remove(7)
                sparse.remove(6)
                if sum(cap[w] for w in sparse) <= 4:
                    continue
            candidates.append(weights)
        intrinsic = [[7, 7, 5, 5], [7, 7, 6, 4]] if length == 4 else [[7, 6, 6, 5, 1]]
        need(all(row in candidates for row in intrinsic), "intrinsic d2 profile boundary")
        actual = [row for row in sorted(candidates) if row not in intrinsic]
        expected = ([[7, 7, 7, k] for k in (1, 2, 3)] if length == 4 else
                    [[7, 7, 5, 4, 1], [7, 7, 5, 4, 2], [7, 7, 5, 5, 1],
                     [7, 7, 6, 3, 1], [7, 7, 6, 3, 2], [7, 7, 6, 4, 1],
                     [7, 7, 7, 1, 1], [7, 7, 7, 2, 1], [7, 7, 7, 2, 2],
                     [7, 7, 7, 3, 1]])
        need(actual == expected, "complete d2 minimum-profile exhaustion")
        answer[str(length) + ":" + str(budget)] = {
            "examined": examined, "intrinsic_exclusions": intrinsic, "actual_profiles": actual}
    return answer


def root_plane_checks(g):
    planes = set()
    for i, j in combinations(range(120), 2):
        ab = g.dots[i][j]
        mask = 0
        for k in range(120):
            ac, bc = g.dots[i][k], g.dots[j][k]
            if 512 + 2 * ab * ac * bc - 8 * (ab * ab + ac * ac + bc * bc) == 0:
                mask |= 1 << k
        need(mask.bit_count() in (2, 3), "root plane has more than three root lines")
        planes.add(mask)
    histogram = Counter(mask.bit_count() for mask in planes)
    need(histogram == {2: 3780, 3: 1120}, "root-plane inventory")
    active_histogram = Counter()
    for plane in planes:
        if plane.bit_count() != 3:
            continue
        active = sum(any(g.dots[i][f] for i in indices(plane)) for f in indices(g.frame))
        need((active, (plane & g.frame).bit_count()) in ((4, 1), (6, 0)),
             "A2 active-frame geometry")
        active_histogram[active] += 1
    need(active_histogram == {4: 224, 6: 896}, "A2 active-frame inventory")
    return {"root_pairs": 7140, "distinct_planes": len(planes),
            "root_line_histogram": {str(k): v for k, v in sorted(histogram.items())},
            "a2_active_axes": {str(k): v for k, v in sorted(active_histogram.items())},
            "plane_digest": digest(sorted(planes))}


def four_axis_checks(g):
    def canonical(form):
        first = next((x for x in form if x), 1)
        return tuple(x if first > 0 else -x for x in form)

    counts = Counter()
    for axes in combinations(list(indices(g.frame)), 4):
        forms = Counter(canonical(tuple(g.dots[i][a] // 4 for a in axes))
                        for i in indices(g.live))
        block = forms[(0, 0, 0, 0)] == 8
        expected = Counter({(0, 0, 0, 0): 8}) if block else Counter()
        sizes = (2, 4) if block else (1, 2, 3)
        for size in sizes:
            multiplicity = {2: 8, 4: 1}[size] if block else {1: 8, 2: 4, 3: 2}[size]
            for support in combinations(range(4), size):
                for signs in product((-1, 1), repeat=size - 1):
                    form = [0] * 4
                    for axis, sign in zip(support, (1,) + signs):
                        form[axis] = sign
                    expected[tuple(form)] = multiplicity
        need(forms == expected, "four-axis restricted-form inventory")
        counts["block" if block else "nonblock"] += 1
    need(counts == {"block": 14, "nonblock": 56}, "four-axis block inventory")
    return {"sets": 70, "block_sets": counts["block"], "nonblock_sets": counts["nonblock"],
            "block_multiplicities": {"zero": 8, "pair": 8, "four": 1},
            "nonblock_multiplicities": {"singleton": 8, "pair": 4, "triple": 2}}


def pencil_callers():
    import ast
    import re
    rows, shared = [], []
    for t in (2, 3):
        for line in regular_bytes(PACKAGE, f"inputs/pr3154/land_e{t}_k8.out").decode().splitlines():
            match = re.fullmatch(r"d (\d+) slack (\d+) (\{.*\}) (\[.*\])", line)
            d, slack = int(match[1]), int(match[2])
            if d < 2:
                continue
            for weights in ast.literal_eval(match[4]):
                remaining = sorted(weights, reverse=True)[d - 2:]
                if t == 2 and all(w <= cap for w, cap in zip(remaining, (7, 7, 5, 5))):
                    shared.append((t, d, slack, weights))
                if max(remaining) <= 6 and (t == 2 or min(remaining) <= 4):
                    rows.append((t, d, slack, weights))
    need(Counter(row[0] for row in rows) == {2: 2, 3: 83}, "literal root-pencil applications")
    need(shared == [(2, 2, 8, [7, 7, 5, 5]), (2, 3, 7, [7, 7, 7, 5, 5])],
         "shared-frame profile applications")
    return {"t2": 2, "t3": 83, "total": len(rows), "application_digest": digest(sorted(rows)),
            "shared_frame_7755": shared}


def frame_sign_checks(g):
    records = []
    for a, b in combinations(list(indices(g.frame)), 2):
        common = g.neighbors[a] & g.neighbors[b]
        positive = sum(1 << site for site in indices(common)
                       if g.dots[a][site] * g.dots[b][site] > 0)
        negative = common ^ positive
        need(common.bit_count() == 24 and positive.bit_count() == negative.bit_count() == 12,
             "frame sign-half partition")
        need(rank(g.labels[i] for i in indices(positive)) == 7
             and rank(g.labels[i] for i in indices(negative)) == 7,
             "frame sign-half label rank")
        radical = (0, g.residues[a], g.residues[b], g.residues[a] ^ g.residues[b])
        fibers = {tuple(sorted(g.by_residue[g.residues[i] ^ r] for r in radical))
                  for i in indices(common)}
        need(len(fibers) == 6 and all(len(set(fiber)) == 4 for fiber in fibers),
             "frame sign-half radical fibers")
        need(all(sum((positive >> i) & 1 for i in fiber) == 2 for fiber in fibers),
             "frame sign halves must meet every radical fiber twice")
        records.append((a, b, positive, negative))
    return {"frame_pairs": 28, "sign_halves": 56, "half_size": 12,
            "binary_rank": 7, "radical_fibers_per_pair": 6, "half_points_per_fiber": 2,
            "case_digest": digest(records)}


def caller_checks():
    import ast
    import re
    parsed = {}
    for t in (2, 3):
        raw = regular_bytes(PACKAGE, f"inputs/pr3154/land_e{t}_k8.out").decode()
        entries = []
        for line in raw.splitlines():
            match = re.fullmatch(r"d (\d+) slack (\d+) (\{.*\}) (\[.*\])", line)
            need(match is not None, "malformed historical caller line")
            d, slack = int(match[1]), int(match[2])
            counters, rows = ast.literal_eval(match[3]), ast.literal_eval(match[4])
            need(counters["SURV"] == len(rows), "historical survivor counter")
            for weights in rows:
                need(len(weights) == d + t and sum(weights) - 8 * d == slack,
                     "historical caller dimensions/ledger")
                entries.append((d, slack, weights))
        parsed[t] = entries
    selected = []
    capacity = {1: 1, 2: 2, 3: 4}
    for t, entries in parsed.items():
        for d, slack, weights in entries:
            low = [w for w in weights if w != 7]
            if weights.count(7) == d and low.count(6) == 1:
                extras = [w for w in low if w != 6]
                if all(w in capacity for w in extras) and sum(capacity[w] for w in extras) <= 4:
                    selected.append({"t": t, "d": d, "slack": slack, "weights": weights})
    selected.sort(key=lambda row: (row["t"], row["d"], row["slack"], row["weights"]))
    need(len(parsed[2]) == 35 and len(parsed[3]) == 280 and len(selected) == 9,
         "historical or new caller count")
    return selected


def run():
    g = Geometry()
    affine, full_count = completion_checks(g)
    stable = {"root_inventory": {"full": 120, "live": 112, "frame": 8},
              "affine6_sections": affine, "core_sections": core_checks(g),
              "witness": witness_checks(g), "callers": caller_checks(),
              "frame_plane": frame_plane_checks(g), "invoice_profiles": invoice_profile_checks(),
              "root_planes": root_plane_checks(g), "pencil_callers": pencil_callers(),
              "frame_sign_halves": frame_sign_checks(g),
              "root764": root764_checks(g), "quotient6": quotient6_checks(),
              "d2_profiles": d2_profile_checks(), "four_axes": four_axis_checks(g)}
    return stable, {"full_ordered_completions": full_count,
                    "chamber_receipt": g.source.chamber_receipt(g.roots, g.points,
                                                               g.source.root_data()[3]),
                    "ambient_gauss_sum": 16, "polar_rank": 8}
