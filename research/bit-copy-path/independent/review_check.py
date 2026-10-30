#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact audit of the frozen COPY-path question.

Set-valued binary rows, primitive integer elimination, scalar dual propagation,
and a short rational analytic bound. No producer module or receipt is executed.
Substantial OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import gzip
from hashlib import sha256
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PINS = {
    "inputs/WORD.json.gz":
        "c46ccd7d3eedabc6a7efbb1a91ec13f2928bad8ee0bac57c6e593a092d13d96c",
    "inputs/GEOMETRY.json.gz":
        "a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022",
    "inputs/global_k.py.txt":
        "6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8",
    "composition/inputs/CODED-WORD.json.gz":
        "1a6841fccba51fa922993c77b4b296e659c2c538252e5e06113d0438c5edb870",
    "composition/inputs/FULL-E8-GEOMETRY.json.gz":
        "1fb726ea3818fe0837cceb0dd22a71a0814f064e5e781628104610d6468e0e55",
    "bounds/inputs/SELECTED-ASSEMBLY.json":
        "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045",
}
SEPARATORS = [
    [104, 107], [104, 107], [100, 108], [110], [98, 108],
    [106, 108], [106, 108], [106, 108], [107],
]
LATE_SEPARATORS = [
    [108, 110], [106, 109], [102, 108, 110], [101, 102], [109],
    [109], [110], [102], [108],
]


def need(condition, label):
    if not condition:
        raise ValueError(label)


def reject(label, operation, intended):
    try:
        operation()
    except ValueError as error:
        need(str(error) == intended, "wrong rejection: " + label)
        return label
    raise ValueError("unexpected acceptance: " + label)


def read(relative):
    data = (ROOT / relative).read_bytes()
    need(sha256(data).hexdigest() == PINS[relative], "immutable input " + relative)
    if relative.endswith(".gz"):
        return json.loads(gzip.decompress(data))
    if relative.endswith(".json"):
        return json.loads(data)
    return data.decode()


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sxor(rows):
    answer = set()
    for row in rows:
        answer.symmetric_difference_update(row)
    return answer


def matmul(left, right):
    return [sxor(right[j] for j in row) for row in left]


def rank2(rows):
    pivots = {}
    for original in rows:
        row = set(original)
        while row:
            p = min(row)
            if p in pivots:
                row.symmetric_difference_update(pivots[p])
            else:
                pivots[p] = row
                break
    return len(pivots)


def bits(row):
    return sum(1 << j for j in row)


def primitive(row):
    common = 0
    for x in row:
        common = gcd(common, x)
    if common:
        first = next(x for x in row if x)
        common *= 1 if first > 0 else -1
        row = [x // common for x in row]
    return tuple(row)


def reduceq(row, basis):
    """Fraction-free exact reduction; no finite-field rank proxy."""
    row = primitive(row)
    for p, old in basis:
        if row[p]:
            row = primitive([old[p]*x - row[p]*y for x, y in zip(row, old)])
    return row


def basisq(rows):
    basis = []
    for row in rows:
        row = reduceq(row, basis)
        if any(row):
            pivot = next(j for j, x in enumerate(row) if x)
            basis.append((pivot, row))
            basis.sort()
    return basis


def normal(basis):
    need(len(basis) == 7, "hyperplane normal dimension")
    free = next(j for j in range(8) if all(j != p for p, _ in basis))
    vector = [Q(int(j == free)) for j in range(8)]
    for p, row in reversed(basis):
        vector[p] = -sum((row[j]*vector[j] for j in range(p+1, 8)), Q(0))/row[p]
    den = 1
    for x in vector:
        den = den*x.denominator // gcd(den, x.denominator)
    return primitive([int(x*den) for x in vector])


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def frame_audit(geometry):
    roots = geometry["lines"]
    need(len(roots) == 111 and all(dot(x, x) == 4 for x in roots), "actual root lines")
    frames = [set(f) for f in geometry["frames"]]
    bases = [basisq(roots[p] for p in f) for f in frames]
    for f, basis in zip(frames, bases):
        closure = {p for p, root in enumerate(roots) if not any(reduceq(root, basis))}
        need(f == closure, "exact rational frame closure")
    dimensions = [len(b) for b in bases]
    need(dimensions[0] == 0 and dimensions[1] == 8, "zero/full frame dimensions")
    need(all(dimensions[510+j] == 7 for j in range(9)), "nine centre hyperplanes")
    return frames, bases, dimensions


def frame_word(word, frames, dimensions):
    n = len(word["start"])
    current = word["start"][:] + [None]
    live = None
    histogram = Counter()
    nesting = 0
    for op, dst, src, coefficient, frame, phase in word["records"]:
        if op == 0:
            need(current[dst] == src and frames[src] <= frames[coefficient],
                 "literal monotone MOVE")
            move_rank = dimensions[coefficient]-dimensions[src]
            need(frame == move_rank, "literal MOVE child rank")
            histogram[move_rank] += 1
            current[dst] = coefficient
            nesting += 1
        elif op == 1:
            need(coefficient in (-1, 1), "literal ADD coefficient")
            need(dst != src and dst != live, "immutable live COPY source")
            need(current[dst] == current[src] == frame, "literal common-frame ADD")
        elif op == 2:
            need(live is None and src == n and current[dst] == coefficient,
                 "literal COPY source")
            need(frames[frame] <= frames[coefficient], "literal nested COPY")
            copy_rank = dimensions[coefficient]-dimensions[frame]
            if "copy_schema" in word:
                need(phase == copy_rank, "literal coded COPY child rank")
            histogram[copy_rank] += 1
            current[n] = frame
            live = dst
        elif op == 3:
            need(live == dst and current[dst] == coefficient and current[n] == frame,
                 "literal ERASE frame return")
            current[n] = None
            live = None
        else:
            raise ValueError("unknown literal operation")
    need(current[:-1] == word["final"] and live is None, "literal final frames")
    need(0 not in histogram, "only positive literal children")
    return dict(sorted(histogram.items())), nesting


def literal(word, inverse=False, omitted_scatter=(), corrupt_scatter=None):
    n = len(word["start"])
    rows = [{j} for j in range(n)] + [set()]
    snapshots, episodes = [], []
    live, episode = None, -1
    records = list(enumerate(word["records"]))
    if inverse:
        records.reverse()
    for index, (op, dst, src, coefficient, _frame, _phase) in records:
        if op == 1:
            if src == n:
                need(live is not None and 111 <= dst < 222, "private target-only scatter")
                if not inverse:
                    episodes[-1]["targets"].symmetric_difference_update({dst-111})
                if episode in omitted_scatter or index == corrupt_scatter:
                    continue
            rows[dst].symmetric_difference_update(rows[src])
        elif op == (3 if inverse else 2):
            need(live is None and not rows[n], "empty private at COPY")
            live = dst
            episode += 1
            rows[n] = set(rows[dst])
            snapshots.append(set(rows[dst]))
            if not inverse:
                episodes.append(dict(begin=index, source=dst, targets=set()))
        elif op == (2 if inverse else 3):
            need(live == dst and rows[n] == rows[dst], "complete private snapshot return")
            if not inverse:
                episodes[-1]["end"] = index
            rows[n] = set()
            live = None
        else:
            need(op == 0, "known operation in scalar replay")
    need(live is None and not rows[n], "empty final private")
    return rows, snapshots, episodes


def require_original_endpoint(rows):
    n = len(rows)-1
    expected = [{p} for p in range(n)] + [set()]
    for p in range(111):
        expected[111+p].add(p)
    need(rows == expected, "complete original binary endpoint")


def source_audit(word, geometry, coded):
    rows, snapshots, episodes = literal(word)
    reverse, _, _ = literal(word, inverse=True)
    require_original_endpoint(rows)
    require_original_endpoint(reverse)
    need(len(snapshots) == 9 and [e["source"] for e in episodes] == list(range(471, 480)),
         "actual nine snapshot sources")
    R = []
    for j, snapshot in enumerate(snapshots):
        need(snapshot - set(range(111)) == {471+j}, "one independent snapshot dirt")
        R.append(snapshot & set(range(111)))
    K = [{j for j, e in enumerate(episodes) if p in e["targets"]} for p in range(111)]
    need(K == [set(row) for row in geometry["scatter"]], "literal K equals actual scatter")
    erased, _, _ = literal(word, omitted_scatter=range(9))
    for p in range(660):
        expected = sxor(snapshots[j] for j in K[p-111]) if 111 <= p < 222 else set()
        need(rows[p] ^ erased[p] == expected, "all-column omitted-scatter defect")
    need(rank2(R) == rank2(K) == rank2(snapshots) == 9, "full transfer rank")
    M = matmul(R, K)
    need([bits(row) for row in M] == [507,135,238,349,185,437,205,503,425],
         "actual retained pairing")
    forward, _, _ = literal(coded)
    backward, _, _ = literal(coded, inverse=True)
    A, Ainv = forward[:111], backward[:111]
    identity = [{p} for p in range(111)]
    need(matmul(A, Ainv) == matmul(Ainv, A) == identity, "actual coded inverse")
    for p in range(111):
        need(forward[111+p] == {111+p} ^ A[p], "complete coded forward target")
        need(backward[111+p] == {111+p, p}, "complete coded inverse target")
    need(all(forward[p] == backward[p] == {p} for p in range(222, 651)),
         "arbitrary coded helper return")
    W = [set() if p < 3 else set(K[p]) for p in range(111)]
    need(matmul(W, R) == [A[p] ^ {p} for p in range(111)], "actual A-I factorization")
    power = identity
    orders = []
    for exponent in range(1, 29):
        power = matmul(A, power)
        if power == identity:
            orders.append(exponent)
    need(orders == [28], "coded order twenty-eight")
    defect = [A[p] ^ Ainv[p] for p in range(111)]
    need(rank2(defect) == 8, "nonzero coded last-pair residual")
    bad_index = next(i for i, r in enumerate(word["records"]) if r[0] == 1 and r[2] == 660)
    controls = [reject("omitted actual private read", lambda: require_original_endpoint(
        literal(word, corrupt_scatter=bad_index)[0]), "complete original binary endpoint")]
    # Set symmetric difference also accepts an equivalent presentation of signs.
    sign_changed = dict(word)
    sign_changed["records"] = [
        [op, d, s, -c if op == 1 else c, f, ph]
        for op, d, s, c, f, ph in word["records"]]
    require_original_endpoint(literal(sign_changed)[0])
    controls.append("all ADD signs reversed is the same binary operator")
    return R, K, M, A, Ainv, W, snapshots, episodes, {
        "original_columns": 660, "coded_columns": 651,
        "R": [sorted(row) for row in R], "K": [sorted(row) for row in K],
        "A_sha256": digest([sorted(row) for row in A]),
        "A_inverse_sha256": digest([sorted(row) for row in Ainv]),
        "M": [bits(row) for row in M],
        "coded_order": 28, "last_pair_scalar_residual_rank": 8,
        "controls": controls,
    }


def geometry_census(geometry, frames, bases, R, K, M, W):
    roots = geometry["lines"]
    source_seven, target_seven = {}, {}
    hist = {name: Counter() for name in ("source", "target", "coded_defect")}
    coded_seven = []
    for mask in range(1, 512):
        coefficients = {j for j in range(9) if mask >> j & 1}
        source = sxor(R[j] for j in coefficients)
        target = {p for p, row in enumerate(K) if len(row & coefficients) % 2}
        coded_target = {p for p, row in enumerate(W) if len(row & coefficients) % 2}
        sb = basisq(roots[p] for p in sorted(source))
        tb = basisq(roots[p] for p in sorted(target))
        cb = basisq(roots[p] for p in sorted(coded_target))
        for name, basis in (("source", sb), ("target", tb), ("coded_defect", cb)):
            hist[name][len(basis)] += 1
        if len(sb) == 7:
            source_seven[mask] = normal(sb)
        if len(tb) == 7:
            target_seven[mask] = normal(tb)
        if len(cb) == 7:
            coded_seven.append(mask)
    need(hist["source"] == hist["target"] == {7: 9, 8: 502}, "complete direct support census")
    need(hist["coded_defect"] == {7: 12, 8: 499}, "complete coded support census")
    need(set(source_seven) == {1 << j for j in range(9)}, "source special directions")
    need(set(target_seven) == set(map(bits, M)), "target special directions")
    low_cells = set()
    for j in range(9):
        need(source_seven[1 << j] == target_seven[bits(M[j])], "matching support normals")
        for k in range(9):
            orthogonal = dot(source_seven[1 << j], target_seven[bits(M[k])]) == 0
            need(orthogonal == (j != k and j in M[k]), "rank-six incidence")
            if orthogonal:
                low_cells.add((k, j))
    projections = []
    for j in range(9):
        support = [p for p, row in enumerate(K) if j in row]
        need(len(basisq(roots[p] for p in support)) == 8, "each K column spans all eight")
        n = normal(bases[510+j])
        norm = dot(n, n)
        projected = [[norm*x - dot(root, n)*y for x, y in zip(root, n)]
                     for root in (roots[p] for p in support)]
        need(len(basisq(projected)) == 7, "projected K column spans centre hyperplane")
        need(all(dot(v, n) == 0 for v in projected), "projected roots stay in F")
        projections.append(dict(centre=j, target_count=len(support), root_rank=8,
                                projected_rank=7, source_normal=list(n)))
    return low_cells, {
        "support_histograms": {k: dict(sorted(v.items())) for k, v in hist.items()},
        "coded_rank7_directions": coded_seven,
        "same_total_branch_theorem_finite_premises": projections,
    }


def old_direct_floor(M, low_cells):
    histogram = Counter()
    equality = []
    for mask in range(512):
        J = {j for j in range(9) if mask >> j & 1}
        r = rank2(row for row in M if not row & J)
        benefits = sum(any(row & J == {j} and k != j for k, row in enumerate(M)) for j in J)
        lower = 63-benefits+9-len(J)-r
        need(lower >= 63, "minimum-basis direct cost floor")
        histogram[lower] += 1
        if lower == 63:
            equality.append(mask)
    need(equality == [0, 511], "direct equality subsets")
    # Solve M X = I with sets, retaining a different representation than producer.
    augmented = [set(row) | {9+p} for p, row in enumerate(M)]
    for p in range(9):
        q = next(j for j in range(p, 9) if p in augmented[j])
        augmented[p], augmented[q] = augmented[q], augmented[p]
        for j in range(9):
            if j != p and p in augmented[j]:
                augmented[j].symmetric_difference_update(augmented[p])
    inverse = [{j-9 for j in row if j >= 9} for row in augmented]
    need(matmul(M, inverse) == [{j} for j in range(9)], "direct pairing inverse")
    selected = [1, 4, 8]
    minor = [{k for k, col in enumerate(selected) if col in inverse[row]} for row in selected]
    need(rank2(minor) == 3 and not any((r, c) in low_cells for r in selected for c in selected),
         "all-count direct forced minor")
    return {"prior_result": "63 direct scatter floor; not a new lower bound",
            "unit_subset_cases": 512, "lower_bound_histogram": dict(sorted(histogram.items())),
            "forced_minor_rows": [bits(row) for row in minor],
            "ten_or_more_floor": "6*n+3"}


def newcut_duals(word, geometry, frames, dimensions, K, episodes):
    records = word["records"]
    begin = episodes[-1]["end"]+1
    end = max(i for i, r in enumerate(records) if r[0] == 1 and 111 <= r[1] < 222)+1
    need((begin, end) == (24069, 25768), "actual B cut range")
    need(all(r[0] in (0, 1) for r in records[begin:]), "no public COPY after B starts")
    need(not any(r[0] == 1 and 471 <= r[1] < 480 for r in records[begin:end]),
         "immutable source centres during B")
    need(not any(r[0] == 0 and 471 <= r[1] < 480 for r in records[begin:end]),
         "unchanged source centre frames during B")
    for p, root in enumerate(geometry["lines"]):
        cap = frames[word["final"][111+p]]
        need(cap == {q for q, line in enumerate(geometry["lines"]) if dot(root, line) == 0},
             "actual final target caps")
    for j, separator in enumerate(SEPARATORS):
        need(sum(j in K[p] for p in separator) % 2 == 1, "dual detects actual deleted column")
    # Nine scalar terminal observables, packed into nine bits per register.
    # This checks only supplied duals, not a reconstructed 111-vector span.
    dual = [0]*660
    for j, separator in enumerate(SEPARATORS):
        for p in separator:
            dual[111+p] |= 1 << j
    current = word["final"][:]
    next_move = [None]*660
    compatibility = {}
    eligible = [0]*9
    checked = 0
    for index in range(len(records)-1, begin-1, -1):
        op, dst, src, coefficient, frame, phase = records[index]
        if op == 0:
            need(current[dst] == coefficient, "reverse frame state")
            current[dst] = src
            next_move[dst] = coefficient
        else:
            need(op == 1, "only MOVE/ADD in B suffix")
            dual[src] ^= dual[dst]
            next_move[dst] = next_move[src] = None
        if index > end:
            continue
        for d in range(660):
            old = current[d]
            new = old if next_move[d] is None else next_move[d]
            pair = old, new
            if pair not in compatibility:
                need(frames[old] <= frames[new], "legal early MOVE splitting")
                allow = 0
                for j in range(9):
                    F = frames[510+j]
                    intersection = dimensions[new] - int(not frames[new] <= F)
                    if (dimensions[old] < 7 and frames[old] <= F and
                            intersection >= max(3, dimensions[old])):
                        allow |= 1 << j
                compatibility[pair] = allow
            allowed = compatibility[pair]
            need(dual[d] & allowed == 0, "every permitted B insertion annihilated")
            for j in range(9):
                eligible[j] += (allowed >> j) & 1
            checked += 1
    need(checked == 1700*660, "every B cut and persistent receiver checked")
    # If the desired missing vector itself is granted, the dual must reject.
    def verify_added_vector(j, vector):
        need(sum(p in vector for p in SEPARATORS[j]) % 2 == 0,
             "every permitted B insertion annihilated")
    controls = [reject("granting missing output invalidates dual",
                       lambda: verify_added_vector(0, {p for p, row in enumerate(K) if 0 in row}),
                       "every permitted B insertion annihilated")]
    # A zero vector is a harmless equivalent null insertion.
    verify_added_vector(0, set())
    return {"cuts": 1700, "cut_receiver_pairs": checked,
            "per_centre_eligible_cut_receiver_counts_including_zero_influences": eligible,
            "dual_target_ports": SEPARATORS, "controls": controls,
            "scope": "arbitrary real G subset of original F, dim G >= 3, original B gates, early MOVE splitting"}


def late_factory_duals(word, frames, dimensions, K, episodes):
    """Verify fixed duals without constructing or solving influence spans."""
    records = word["records"]
    end = episodes[0]["begin"]
    cases = []
    for j, separator in enumerate(LATE_SEPARATORS):
        begin = 1+max(i for i, r in enumerate(records)
                      if r[0] == 1 and r[1] == 471+j and r[-1] == 2)
        lo, hi = episodes[j]["begin"], episodes[j]["end"]
        need(all(r[0] != 0 for r in records[lo:hi+1]),
             "removed original COPY episode has no ordinary MOVE")
        need(sum(j in K[p] for p in separator) % 2 == 1, "late dual detects missing column")
        current = word["final"][:] + [None]
        dual = [0]*661
        next_move = [None]*661
        for p in separator:
            dual[111+p] = 1
        eligible = checked = 0
        compatibility = {}
        for index in range(len(records)-1, begin-1, -1):
            op, dst, src, coefficient, frame, phase = records[index]
            if lo <= index <= hi:
                continue_event = True
            else:
                continue_event = False
                if op == 0:
                    need(current[dst] == coefficient, "late reverse frame state")
                    current[dst] = src
                    next_move[dst] = coefficient
                elif op == 1:
                    dual[src] ^= dual[dst]
                    next_move[dst] = next_move[src] = None
                elif op == 2:
                    dual[dst] ^= dual[660]
                    dual[660] = 0
                    next_move[dst] = None
                else:
                    need(op == 3, "late known operation")
                    dual[660] = 0
                    next_move[dst] = None
            if index > end:
                continue
            # The cut at a removed COPY still exists in the changed word.
            need(not continue_event or index == end == lo,
                 "only the first removed COPY can meet the late cut range")
            need(current[471+j] == 510+j, "completed late source has its actual frame")
            for d in range(660):
                old = current[d]
                new = old if next_move[d] is None else next_move[d]
                pair = old, new
                if pair not in compatibility:
                    F = frames[510+j]
                    need(frames[old] <= frames[new], "late legal early MOVE splitting")
                    intersection = dimensions[new]-int(not frames[new] <= F)
                    compatibility[pair] = (
                        dimensions[old] < 7 and frames[old] <= F
                        and intersection >= max(3, dimensions[old]))
                allowed = compatibility[pair] and d != 471+j
                need(not allowed or dual[d] == 0, "every late factory insertion annihilated")
                eligible += int(allowed)
                checked += 1
        need(checked == (end-begin+1)*660, "complete late cut-receiver census")
        cases.append({"centre": j, "cuts": end-begin+1, "completed_cut": begin,
                      "dual_target_ports": separator, "cut_receiver_pairs": checked,
                      "eligible_pairs_including_zero_influences": eligible})
    need(sum(row["cuts"] for row in cases) == 254, "all 254 late cuts")
    return {"cases": cases, "cuts": 254,
            "scope": "completed unchanged centre, before first original COPY, dim G>=3 in F, other gates fixed"}


def native_witness(geometry, full, A, Ainv, R, K):
    roots = geometry["lines"]
    need(geometry["ports_geom"][0] == 0 and full["lines"][0] == roots[0],
         "actual identity root-zero chart")
    need(roots[0] == [2,0,0,0,0,0,0,0] and roots[3] == [0,0,0,2,0,0,0,0],
         "actual root-zero and root-three axes")
    need(0 in A[3], "native witness code edge")
    head = [Q(int(j == 59)) for j in range(64)]
    need(59 not in list(range(8))+list(range(50, 57)), "stage-seven fresh-block exclusion")
    # Identity cap chart at port zero sends fresh coordinate 59 to core e3.
    routed = [Q(int(j == 3)) for j in range(64)]
    root = roots[3]
    tail = [Q(root[i]*dot(root, routed[:8]), 4) if i < 8 else Q(0) for i in range(64)]
    need(tail == routed, "destination rho fixes root and N produces TAIL")
    need(head != tail and tail[3] == 1 and head[3] == 0, "uncancelled native impulse")
    # The inverse stage-seven branch, whatever A^-1[3,0], remains at e59.
    residual_addresses = {(tuple([Q(0)]*64), tuple(tail))}
    if 0 in Ainv[3]:
        residual_addresses.add((tuple(head), tuple([Q(0)]*64)))
    need(any(any(t) for _, t in residual_addresses), "nonzero quotient by TAIL-zero support")
    clean = [row ^ {p} for p, row in enumerate(matmul(K, R))]
    edge_witnesses = []
    for p, row in enumerate(clean):
        q = next((q for q in sorted(row) if q != p), None)
        need(q is not None, "off-diagonal clean-map entry on every row")
        entries = [(i, j) for i in range(8) for j in range(8)
                   if roots[p][i]*roots[p][j] != roots[q][i]*roots[q][j]]
        need(entries, "distinct actual root projector")
        edge_witnesses.append([p, q, *entries[0]])
    mutant = [set(row) for row in A]
    mutant[3].remove(0)
    def require_edge(matrix):
        need(0 in matrix[3], "native witness code edge")
    controls = [reject("delete native witness edge", lambda: require_edge(mutant),
                       "native witness code edge")]
    return {"input_last_target_port": 0, "HEAD_axis": 59, "TAIL": 0,
            "output_source_ports": 3, "output_TAIL_axis": 3,
            "coefficient": 1, "all_four_source_banks": True,
            "integral_witness_all_odd_ADDRESS_fields": True,
            "restricted_row_repair_obstructions": edge_witnesses, "controls": controls,
            "scope": "native two-stage identity is a written operator proof; this is its exact integral witness"}


@lru_cache(None)
def log_interval(x):
    """atanh series after binary range reduction, with the entire tail."""
    x = Q(x)
    need(x >= 1, "logarithm domain")
    exponent = 0
    while x >= 2:
        x /= 2
        exponent += 1
    def small(y):
        z = (y-1)/(y+1)
        s = sum((2*z**(2*n+1)/Q(2*n+1) for n in range(24)), Q(0))
        tail = 2*z**49/(49*(1-z*z))
        return s, s+tail
    a, b = small(x)
    c, d = small(Q(2))
    return a+exponent*c, b+exponent*d


@lru_cache(None)
def power_interval(r, b):
    lo, hi = log_interval(Q(64, r))
    lo, hi = b*lo, b*hi
    need(0 <= lo <= hi < 1, "exponential domain")
    def polynomial(x):
        term = Q(1)
        total = term
        for n in range(1, 17):
            term *= x/n
            total += term
        return total, term
    lower, _ = polynomial(lo)
    upper, term = polynomial(hi)
    tail = term*hi/17/(1-hi/18)
    return lower, upper+tail


def bill(hist, b, surcharge=True, free_bad=False):
    lo = hi = Q(0)
    for r, count in hist.items():
        a, z = power_interval(r, b)
        lo += r*count*a
        hi += r*count*z
    if free_bad:
        lo *= 1-Q(1, 10**16)
        hi *= 1-Q(1, 10**16)
    if surcharge:
        a, z = power_interval(1, b)
        c = Q(32*64**2, 10**16)*sum(hist.values())
        lo += c*a
        hi += c*z
    return lo-64*28416, hi-64*28416


def compact(interval):
    grid = 10**18
    a, b = interval
    lower = a.numerator*grid//a.denominator
    upper = -((-b.numerator*grid)//b.denominator)
    return [str(Q(lower, grid)), str(Q(upper, grid))]


def complete_hist(local, full, partial):
    F, D = 288*full, 288*partial
    t = Q(F-56832, 5)
    need(0 <= D <= 14208 and 0 <= t <= 14208, "owner LP resource regime")
    hist = {r: Q(288*n) for r, n in local.items()}
    for r, n in ((7,21312), (6,14208), (4,14208-D), (2,t), (42,14208-t)):
        hist[r] = hist.get(r, 0)+n
    return hist


def budgets(original_hist, coded_hist, selected):
    K = Q(11, 10)*Q(selected["kappa"])
    b = K/(1-K)
    need(b == Q(9199631083923049, 4990800368916076951), "exact target primitive")
    G = complete_hist(original_hist, 433, 5)
    C = complete_hist(coded_hist, 429, 0)
    need(sum(r*n for r, n in G.items()) == 1808352 and
         sum(r*n for r, n in C.items()) == 1791072, "complete returned owner mass")
    one = G.copy()
    one[7] -= 288
    one_bill = bill(one, b)
    allowance = -one_bill[1]/288, -one_bill[0]/288
    coded_bill = bill(C, b)
    coded_allowance = -coded_bill[1]/288, -coded_bill[0]/288
    need(Q(49779,10000) < allowance[0] <= allowance[1] < 5,
         "one-copy allowance below five")
    need(Q(583826,10000) < coded_allowance[0] <= coded_allowance[1] < Q(583827,10000),
         "coded allowance")
    five = one.copy()
    five[5] = five.get(5,0)+288
    five_excess = bill(five, b, surcharge=False, free_bad=True)
    need(five_excess[0] > 0, "rank-five replacement fails raw LP with free bad packets")
    repair = C.copy()
    repair[7] = repair.get(7,0)+9*288
    repair_excess = bill(repair, b, surcharge=False, free_bad=True)
    need(repair_excess[0] > 0, "nine common-cap repairs fail favorable raw LP")
    direct = G.copy()
    for r, n in ((6,4), (7,-8), (8,4)):
        direct[r] = direct.get(r,0)+288*n
    direct_excess = bill(direct, b, surcharge=False, free_bad=True)
    need(direct_excess[0] > 0, "direct relaxed histogram target rejected")
    return {"target": str(b), "one_COPY7_allowance_per_call": compact(allowance),
            "coded429_allowance_per_call": compact(coded_allowance),
            "free_bad_rank5_replacement_excess": compact(five_excess),
            "free_bad_nine_rank7_repair_excess": compact(repair_excess),
            "free_bad_direct_histogram_excess": compact(direct_excess),
            "arithmetic": "24-term atanh after binary range reduction; 16-term exp; rational entire tails",
            "scope": "fixed-stock raw owner LP premise; charged displayed-primal allowances"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE/"review-result.json")
    args = parser.parse_args()
    word = read("inputs/WORD.json.gz")
    geometry = read("inputs/GEOMETRY.json.gz")
    coded = read("composition/inputs/CODED-WORD.json.gz")
    full = read("composition/inputs/FULL-E8-GEOMETRY.json.gz")
    selected = read("bounds/inputs/SELECTED-ASSEMBLY.json")
    read("inputs/global_k.py.txt")  # Identity derivation reviewed against these exact bytes.
    frames, bases, dimensions = frame_audit(geometry)
    ordinary_hist, ordinary_moves = frame_word(word, frames, dimensions)
    coded_hist, coded_moves = frame_word(coded, frames, dimensions)
    R, K, M, A, Ainv, W, snapshots, episodes, source = source_audit(word, geometry, coded)
    low_cells, census = geometry_census(geometry, frames, bases, R, K, M, W)
    output = {
        "status": "PASS_INDEPENDENT_COPY_PATH_REVIEW",
        "no_new_kappa": True,
        "input_pins": PINS,
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_operators": source,
        "exact_geometry": {
            "rational_closed_frames": len(frames),
            "frame_dimension_histogram": dict(sorted(Counter(dimensions).items())),
            "ordinary_monotone_moves": ordinary_moves, "coded_monotone_moves": coded_moves,
            **census,
        },
        "ordinary_local_histogram": ordinary_hist,
        "coded_local_histogram": coded_hist,
        "credited_direct_floor": old_direct_floor(M, low_cells),
        "newcut_separators": newcut_duals(word, geometry, frames, dimensions, K, episodes),
        "late_factory_separators": late_factory_duals(word, frames, dimensions, K, episodes),
        "native_counterexample": native_witness(geometry, full, A, Ainv, R, K),
        "caller_budget": budgets(ordinary_hist, coded_hist, selected),
        "limits": [
            "The finite-branch dimension theorem and native stage composition are written proofs.",
            "The 63 direct factorization floor is credited prior work.",
            "No new physical private-MOVE ABI, dirty-owner schedule, rounded precision contract, or supplier admission.",
            "No general changed-total, changed-factory, changed-caller, or routed-decoder lower bound.",
        ],
    }
    args.output.write_text(json.dumps(output, sort_keys=True, indent=2)+"\n")
    print("PASS_INDEPENDENT_COPY_PATH_REVIEW no_new_kappa")


if __name__ == "__main__":
    main()
