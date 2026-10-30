#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact route reduction for the specified 4080-owner block.

OpenAI Codex assistance.  R extraction and the source interpretation are
inherited.  This implementation owns the row-major GF(2) arithmetic, complete
route equivalence relation, subgroup certificate and rational class kernels.
It imports no predecessor group arithmetic and performs no triple census.

Runtime: Python >= 3.10, standard library only.  Executed retained source and all
source-data dependencies are authenticated below before loading.  The --receipt
mode compares the complete independent JSON, including every subgroup element,
route and equivalence-class rank.  Installed default mode compares the primary
package's common fields individually, including the complete partition, every
class rank and attaining repair interface.  Neither comparison uses receipt
hashes as a substitute for the declared exact data comparison.
"""

import argparse
from collections import Counter, deque
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
import types


BASE_COMMIT = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
PREDECESSOR_HEAD = "69e745992b966c647e10696b980cb4c96d7ebeed"
ACTIVE, TOTAL, PORTS = 17, 73, 112
TRIPLE = (0, 6, 85)
EXTRACTOR = "research/centre-block-repair-information/independent.py"
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
OLD_RECEIPT = "research/centre-owner-observation-floor/RESULT.json"
MOORE_MANIFEST = "research/centre-block-moore-bound/SOURCES.json"
MOORE_CHECKER = "research/centre-block-moore-bound/verify.py"
INPUTS = {
    EXTRACTOR: ("executed_inherited_extractor", "b298ff3902c14db11e4ed057259785efc185e8ae3bb39c0d1c432e2340ceb4ea"),
    ARCHIVE: ("source_data", "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"),
    OLD_RECEIPT: ("exact_R_H_reference_receipt", "d238990b46dba2e4b92919602ef17de994f02a3d904adb399efc1dbcd032c86e"),
    MOORE_MANIFEST: ("loader_provenance_not_executed", "5f6b3b33395314c2bc7c58d51916e2d71cd13ab3f9807cc34f298ad90a9e737c"),
    MOORE_CHECKER: ("loader_provenance_not_executed", "661016189cc91ae088d53f073c9d6678a57196f5d6c054cb8f06b4c22d304248"),
}
IDENTITY = tuple(1 << i for i in range(ACTIVE))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def authenticate(root):
    raw = {}
    for name, (_, expected) in INPUTS.items():
        path = root / name
        require(path.is_file() and not path.is_symlink(), "regular source: " + name)
        data = path.read_bytes()
        require(sha256(data).hexdigest() == expected, "source SHA256: " + name)
        raw[name] = data
    manifest = json.loads(raw[MOORE_MANIFEST])
    declared = {r["path"]: r["sha256"] for r in manifest["files"] if r["usage"] == "input"}
    require(declared[EXTRACTOR] == INPUTS[EXTRACTOR][1]
            and declared[ARCHIVE] == INPUTS[ARCHIVE][1], "loader-manifest source binding")
    return raw


def transpose(rows):
    n = len(rows)
    return tuple(sum(((row >> k) & 1) << j for j, row in enumerate(rows)) for k in range(n))


def multiply(left, right):
    """Exact row-major product AB: output row i is XOR of B's selected rows."""
    require(len(left) == len(right), "matching matrix dimensions")
    output = []
    for row in left:
        value = 0
        while row:
            bit = row & -row
            value ^= right[bit.bit_length() - 1]
            row ^= bit
        output.append(value)
    return tuple(output)


def point_action(rows, vector):
    return sum(((row & vector).bit_count() & 1) << i for i, row in enumerate(rows))


def invert(rows):
    """Exact Gauss-Jordan inversion, without relying on route orthogonality."""
    n = len(rows)
    work = [row | (1 << (n + i)) for i, row in enumerate(rows)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if (work[i] >> j) & 1), None)
        require(pivot is not None, "invertible GF(2) matrix")
        work[j], work[pivot] = work[pivot], work[j]
        for i in range(n):
            if i != j and ((work[i] >> j) & 1):
                work[i] ^= work[j]
    require(all((row & ((1 << n) - 1)) == 1 << i for i, row in enumerate(work)),
            "inverse elimination identity")
    return tuple(row >> n for row in work)


def lift(rows):
    """Faithful block-diagonal extension fixing all 56 spectator coordinates."""
    require(len(rows) == ACTIVE and all(0 <= r < 1 << ACTIVE for r in rows),
            "complete active block")
    return tuple(rows) + tuple(1 << i for i in range(ACTIVE, TOTAL))


def row_route(record):
    """Form rows directly from the orthonormal-chart swap, rather than composing columns."""
    q = record["q"]
    axes = tuple(record["idle_children"][0]["orthogonal_axes"][:8])
    chart = (q,) + axes
    require(len(chart) == 9 and all(0 < v < 512 for v in chart), "nine-dimensional route chart")
    require(all(((a & b).bit_count() & 1) == int(i == j)
                for i, a in enumerate(chart) for j, b in enumerate(chart)), "orthonormal route chart")
    top = tuple((q if (q >> i) & 1 else 0)
                | sum(1 << (9 + j) for j, axis in enumerate(axes) if (axis >> i) & 1)
                for i in range(9))
    return top + axes


def load(root):
    raw = authenticate(root)
    source = types.ModuleType("authenticated_inherited_query_extractor")
    source.__file__ = str(root / EXTRACTOR)
    exec(compile(raw[EXTRACTOR], source.__file__, "exec"), source.__dict__)
    word, phases = source.sources()
    rows, later = source.query_rows(word)
    reference = json.loads(raw[OLD_RECEIPT])
    require([[str(x) for x in r] for r in rows] == reference["R"], "full exact inherited R receipt")
    require([[str(x) for x in r] for r in later] == reference["H"], "full exact inherited H receipt")
    require(len(rows) == 8 and all(len(r) == PORTS for r in rows), "8 by 112 R")
    require(later == [[x / 4 for x in r] for r in rows], "H=R/4")
    recipes = phases["recipes"]
    require(phases["m"] == TOTAL and len(recipes) == PORTS, "73-dimensional,112-port route data")
    require([r["q"] for r in recipes] == word["ports"], "all route labels match R order")
    routes = [row_route(r) for r in recipes]
    for record, route in zip(recipes, routes):
        full = lift(route)
        inherited_columns = tuple(source.chart_action(record, 1 << i) for i in range(TOTAL))
        require(transpose(full) == inherited_columns, "all 73 route columns match source chart action")
        require(multiply(route, route) == IDENTITY, "involutory active route")
        require(invert(route) == transpose(route), "orthogonal active route")
        require(all(point_action(full, 1 << k) == 1 << k for k in range(ACTIVE, TOTAL)),
                "every spectator is pointwise fixed")
        require(all(point_action(full, 1 << k) < 1 << ACTIVE for k in range(ACTIVE)),
                "active17 subspace invariant")
    require(len(set(routes)) == PORTS, "112 structurally distinct full routes")
    require(all(any(point_action(r, 1 << k) != 1 << k for r in routes)
                for k in range(ACTIVE)), "each of the17 active coordinate basis vectors is moved")
    return rows, routes, source.MEMBER_SHA256


def closure(generators, cap=4080):
    """Enumerate complete right-generator words using structural tuple equality."""
    elements, index = [IDENTITY], {IDENTITY: 0}
    tree = []
    queue = deque([IDENTITY])
    while queue:
        g = queue.popleft()
        for j, generator in enumerate(generators):
            h = multiply(g, generator)
            if h not in index:
                require(len(elements) < cap, "subgroup enumeration exceeds declared cap")
                index[h] = len(elements)
                elements.append(h)
                tree.append([index[g], j, index[h]])
                queue.append(h)
    return elements, index, tree


def subgroup_certificate(routes):
    generators = [multiply(routes[0], routes[6]), multiply(routes[6], routes[85])]
    elements, index, tree = closure(generators)
    require(len(elements) == 4080 and len(tree) == 4079, "complete subgroup order4080")
    inverse = []
    right, left = [], []
    for g in elements:
        inv = invert(g)
        require(inv in index and multiply(g, inv) == IDENTITY and multiply(inv, g) == IDENTITY,
                "every enumerated element has a two-sided inverse in the set")
        require(inv == transpose(g), "every subgroup element remains orthogonal")
        inverse.append(index[inv])
        right.append([index[multiply(g, s)] for s in generators])
        left.append([index[multiply(s, g)] for s in generators])
    require(all(sorted(row[j] for row in right) == list(range(4080)) for j in range(2)),
            "right-generator edges are complete permutations")
    require(all(sorted(row[j] for row in left) == list(range(4080)) for j in range(2)),
            "left-generator edges are complete permutations")
    require(all(right[parent][label] == child and parent < child for parent, label, child in tree),
            "4079-edge generating spanning tree")
    # The product and point-action checks use different code paths.  A basis is
    # sufficient for exact equality of binary linear maps; no sample assumption.
    for g in elements:
        for s in generators:
            product = multiply(g, s)
            require(all(point_action(product, 1 << k) == point_action(g, point_action(s, 1 << k))
                        for k in range(ACTIVE)), "all basis points of every right-generator product")
    # Verify the full73 embedding on every element/generator product, without
    # doing arithmetic on an unfaithful small representation.
    for g in elements:
        for s in generators:
            require(lift(multiply(g, s)) == multiply(lift(g), lift(s)), "faithful full73 product lift")
    return generators, elements, index, tree, inverse, right, left


def equivalence(routes, index):
    table = [[multiply(a, b) in index for b in routes] for a in routes]
    require(all(table[p][p] for p in range(PORTS)), "route equivalence reflexive")
    require(all(table[p][q] == table[q][p] for p in range(PORTS) for q in range(PORTS)),
            "route equivalence symmetric")
    classes = []
    remaining = set(range(PORTS))
    while remaining:
        p = min(remaining)
        part = [q for q in range(PORTS) if table[p][q]]
        require(set(part) <= remaining, "disjoint complete equivalence classes")
        require(all(table[q] == table[p] for q in part), "route equivalence transitive")
        classes.append(part)
        remaining.difference_update(part)
    require(sum(map(len, classes)) == PORTS, "all112 routes covered once")
    return table, classes


def rref(rows):
    work = [list(map(Q, row)) for row in rows]
    pivots = []
    for column in range(len(work[0])):
        pivot = next((i for i in range(len(pivots), len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        i = len(pivots)
        work[i], work[pivot] = work[pivot], work[i]
        scale = work[i][column]
        work[i] = [x / scale for x in work[i]]
        for j in range(len(work)):
            if j != i:
                scale = work[j][column]
                work[j] = [x - scale * y for x, y in zip(work[j], work[i])]
        pivots.append(column)
    return work, pivots


def scalar_certificate(rows, ports):
    selected = [[r[p] for p in ports] for r in rows]
    reduced, pivots = rref(selected)
    basis = []
    for free in range(len(ports)):
        if free in pivots:
            continue
        vector = [Q(int(j == free)) for j in range(len(ports))]
        for i, pivot in enumerate(pivots):
            vector[pivot] = -reduced[i][free]
        first = next(x for x in vector if x)
        vector = [x / first for x in vector]
        require(all(sum(a * b for a, b in zip(row, vector)) == 0 for row in selected),
                "exact rational class-kernel vector")
        basis.append(vector)
    require(len(pivots) + len(basis) == len(ports), "complete class rank-nullity")
    return {"ports": ports, "rank": len(pivots), "pivot_columns": pivots,
            "rref": [[str(x) for x in row] for row in reduced],
            "kernel_basis": [[str(x) for x in vector] for vector in basis]}


def expected_partition(classes):
    expected = [list(TRIPLE)] + [[p] for p in range(PORTS) if p not in TRIPLE]
    require(classes == expected, "one triple class and109 singleton classes")


def expected_scalars(certificates):
    require(certificates[0]["ports"] == list(TRIPLE) and certificates[0]["rank"] == 2
            and certificates[0]["kernel_basis"] == [["1", "-1", "-1"]], "unique triple kernel")
    require(all(c["rank"] == 1 and c["kernel_basis"] == [] and len(c["ports"]) == 1
                for c in certificates[1:]), "all109 singleton classes have full column rank")


def rejected(operation):
    try:
        operation()
    except ValueError:
        return True
    return False


def attainment(rows, pivots, owners):
    """Reduce the proposed repair rowspace to one scalar amplitude per owner."""
    require(pivots == [0, 1, 2, 3, 4, 5, 6, 12], "independently reconstructed pivot interface")
    complement = [p for p in range(PORTS) if p not in pivots]
    ordinary = [p for p in complement if p != 85]
    require(len(ordinary) == 103 and 85 in complement, "103 raw coordinates and one amplitude")
    local = list(rows) + [[Q(int(p == q)) for p in range(PORTS)] for q in ordinary]
    certificate = scalar_certificate(local, list(range(PORTS)))
    u = ["0"] * PORTS
    for p, value in zip(TRIPLE, ("1", "-1", "-1")):
        u[p] = value
    require(certificate["rank"] == 111 and certificate["kernel_basis"] == [u],
            "R plus103 raw reads leave precisely the local u-amplitude")
    # Small exact algebraic model after the112-dimensional local elimination:
    # x85(g)-x85(anchor) = -(lambda(g)-lambda(anchor)).
    small = scalar_certificate([[Q(1), Q(-1), Q(0)], [Q(1), Q(0), Q(-1)]], [0, 1, 2])
    require(small["rank"] == 2 and small["kernel_basis"] == [["1", "1", "1"]],
            "three-owner reduced star-difference rowspace")
    # All4079 rows have a different nonanchor pivot, and the common constant
    # vector is in the kernel.  This certifies this specific full star without
    # allocating a4080-square rational matrix.
    sparse_rows = [((0, Q(1)), (g, Q(-1))) for g in range(1, owners)]
    require([row[1][0] for row in sparse_rows] == list(range(1, owners)), "all nonanchor pivots once")
    require(all(sum(value for _, value in row) == 0 for row in sparse_rows), "constant amplitude in star kernel")
    ordinary_reads = len(ordinary) * owners
    difference_reads = len(sparse_rows)
    minimum = ordinary_reads + difference_reads
    require(minimum == 104 * owners - 1, "independently reconstructed exact repair dimension")
    return {"pivot_ports": pivots, "ordinary_nonpivot_ports": ordinary,
            "local_observation_plus_raw_read_rank": certificate["rank"],
            "local_kernel_basis": [u], "difference_port": 85,
            "three_owner_reduced_model": small,
            "full_star_nonanchor_pivots": list(range(1, owners)),
            "full_star_rank": difference_reads,
            "ordinary_coordinate_reads": ordinary_reads,
            "difference_reads_to_one_fixed_anchor": difference_reads,
            "additional_scalar_observation_minimum": minimum,
            "physical_acquisition_and_dirty_restoration_not_implemented": True}


def controls(rows, routes, generators, index):
    smaller, smaller_index, _ = closure(generators[:1])
    require(len(smaller) < 4080, "one-generator subgroup cannot replace L")
    _, smaller_classes = equivalence(routes, smaller_index)
    require(rejected(lambda: expected_partition(smaller_classes)), "proper subgroup loses the triple class")

    # Pair-order reversal alone cannot test coset orientation: for involutions,
    # rho_p rho_q and rho_q rho_p are inverses and have identical membership.
    # Use an actual output at a route that does not normalize L instead.
    g, p = generators[0], 1
    output = multiply(g, routes[p])
    correct_source = multiply(output, routes[p])
    reversed_source = multiply(routes[p], output)
    require(correct_source == g and correct_source in index and reversed_source not in index,
            "wrong left-output orientation must change an actual source owner")

    changed = [list(row) for row in rows]
    changed[5][85] += 1
    changed_cert = scalar_certificate(changed, list(TRIPLE))
    require(changed_cert["rank"] == 3, "changed source coefficient breaks triple dependence")
    require(rejected(lambda: expected_scalars([changed_cert])), "changed coefficient is rejected")
    skew = [Q(1), Q(-1), Q(-2)]
    require(any(sum(row[p] * v for p, v in zip(TRIPLE, skew)) for row in rows),
            "changed witness coefficient has nonzero old observation")

    changed_routes = list(routes)
    changed_routes[85] = multiply(multiply(routes[1], routes[85]), routes[1])
    require(multiply(changed_routes[85], changed_routes[85]) == IDENTITY,
            "changed route remains a valid involution")
    require(invert(changed_routes[85]) == transpose(changed_routes[85]),
            "changed route remains orthogonal")
    require(len(set(changed_routes)) == PORTS, "changed route remains distinct")
    _, wrong_classes = equivalence(changed_routes, index)
    require(rejected(lambda: expected_partition(wrong_classes)), "changed route is rejected")
    return {"wrong_subgroup_order": len(smaller), "wrong_subgroup_rejected": True,
            "orientation_witness": {"port": p, "owner_active_rows": list(g),
                                    "output_active_rows": list(output),
                                    "right_source_in_L": True, "left_source_in_L": False,
                                    "wrong_source_active_rows": list(reversed_source)},
            "changed_R_entry": [5, 85, "plus1"], "changed_R_triple_rank": changed_cert["rank"],
            "changed_witness_coefficients_rejected": True,
            "changed_involutory_route": "rho85 replaced by rho1 rho85 rho1",
            "changed_route_partition_rejected": True}


def build(root):
    rows, routes, members = load(root)
    _, pivots = rref(rows)
    require(len(pivots) == 8, "exact full R rank8")
    generators, elements, index, tree, inverse, right, left = subgroup_certificate(routes)
    table, classes = equivalence(routes, index)
    expected_partition(classes)
    scalars = [scalar_certificate(rows, part) for part in classes]
    expected_scalars(scalars)
    repair = attainment(rows, pivots, len(elements))
    negative = controls(rows, routes, generators, index)
    # JSON's booleans retain the complete112x112 membership relation.  Python
    # dictionaries/sets accelerate exact tuple equality; hashes never decide
    # equality on their own.  Full active matrices determine full73 matrices.
    return {"schema_version": 1, "claim": "full_selected_L_block_joint_kernel_dimension_one",
            "source_base_commit": BASE_COMMIT, "reviewed_predecessor_head": PREDECESSOR_HEAD,
            "input_files": [{"path": p, "role": v[0], "sha256": v[1]} for p, v in INPUTS.items()],
            "archive_members_sha256": members,
            "source_extraction": "inherited exact reverse adjoints for R/H; direct row-chart routes compared on all73 source columns",
            "runtime": "Python>=3.10 standard library only; inherited source imports collections,fractions,itertools,pathlib,gzip,hashlib,json,tarfile",
            "coefficient_field": "Q; identical ranks and kernel over C",
            "active_dimension": ACTIVE, "full_dimension": TOTAL, "fixed_spectators": TOTAL - ACTIVE,
            "R": [[str(x) for x in row] for row in rows], "R_rank": len(pivots),
            "routes_active_rows": [list(r) for r in routes],
            "subgroup": {"generators": [[0, 6], [6, 85]],
                         "generator_active_rows": [list(g) for g in generators],
                         "order": len(elements), "elements_active_rows": [list(g) for g in elements],
                         "generating_spanning_tree": tree, "inverse_indices": inverse,
                         "right_generator_indices": right, "left_generator_indices": left,
                         "exact_equality": "all17 integer rows; faithful identity extension by56 spectators"},
            "coset_orientation": "outputs L rho_p; L rho_p=L rho_q iff rho_p rho_q in L",
            "relative_route_membership": table,
            "route_classes": classes, "class_size_histogram": {str(k): v for k, v in sorted(Counter(map(len, classes)).items())},
            "scalar_class_certificates": scalars,
            "attaining_repair_rowspace": repair,
            "joint_kernel": {"source_owners": 4080, "source_coordinates": 456960,
                             "old_rank": 32640, "old_kernel_dimension": 424320,
                             "joint_kernel_dimension": 1,
                             "basis": {"every_g_in_L": {"0": "1", "6": "-1", "85": "-1"}, "all_other_coordinates": "0"},
                             "conditional_abstract_repair_dimension": 424319,
                             "written_proof_required": True},
            "controls": negative, "proof_level": "finite exact route/rational certificate plus written all-coefficient implication",
            "no_formal_kernel_proof": True, "no_general_minimum_support_claim": True,
            "no_physical_supplier_or_kappa_claim": True,
            "receipt_binding": "--receipt requires complete independent JSON equality; installed default compares all declared primary common fields and repair-interface fields individually"}


def compare_primary(result, path):
    """Compare common mathematical fields with the primary package receipt.

    This checks actual classes, ranks and coefficients in addition to source
    digests.  Primary implementation code is never imported or executed.
    """
    primary = json.loads(path.read_bytes())
    pairs = {
        "source_ports": PORTS,
        "old_rank_per_owner": result["R_rank"],
        "route_dimension": result["full_dimension"],
        "active_dimension": result["active_dimension"],
        "fixed_spectators": result["fixed_spectators"],
        "subgroup_order": result["subgroup"]["order"],
        "coset_classes": result["route_classes"],
        "class_size_histogram": result["class_size_histogram"],
        "triple": list(TRIPLE), "triple_coefficients": [1, -1, -1],
        "common_kernel_dimension": result["joint_kernel"]["joint_kernel_dimension"],
        "old_kernel_dimension": result["joint_kernel"]["old_kernel_dimension"],
        "additional_scalar_observation_minimum": result["attaining_repair_rowspace"]["additional_scalar_observation_minimum"],
    }
    for key, value in pairs.items():
        require(primary[key] == value, "exact primary receipt field: " + key)
    ranks = primary["class_ranks"]
    expected_ranks = [c["rank"] for c in result["scalar_class_certificates"]]
    # Compare the ordered rank of every class, rather than only a histogram.
    require(ranks == expected_ranks, "exact primary class-rank receipt")
    expected_interface = result["attaining_repair_rowspace"]
    interface = primary["attaining_observation_interface"]
    for key in ("pivot_ports", "ordinary_nonpivot_ports", "ordinary_coordinate_reads",
                "difference_port", "difference_reads_to_one_fixed_anchor"):
        require(interface[key] == expected_interface[key], "exact primary repair interface: " + key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    installed = Path(__file__).parent.name == "centre-coset-full-kernel"
    default_root = Path(__file__).resolve().parents[2] if installed else Path.cwd()
    parser.add_argument("--root", type=Path, default=default_root, help="pinned source checkout root")
    parser.add_argument("--receipt", type=Path, help="optional complete independent receipt to compare")
    parser.add_argument("--primary-receipt", type=Path, help="package RESULT.json to compare")
    parser.add_argument("--emit", action="store_true", help="emit the complete exact receipt")
    args = parser.parse_args()
    require(sys.version_info >= (3, 10), "Python>=3.10")
    result = build(args.root.resolve())
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        receipt = args.receipt
        if receipt is None and not installed:
            receipt = Path(__file__).with_name("route-receipt.json")
        if receipt is not None:
            expected = json.loads(receipt.read_bytes())
            require(result == expected, "complete exact independent route receipt")
        primary = args.primary_receipt
        if primary is None and installed:
            primary = Path(__file__).with_name("RESULT.json")
        if primary is not None:
            compare_primary(result, primary)
        require(receipt is not None or primary is not None, "at least one exact receipt comparison")
        print("PASS_INDEPENDENT_ROUTES order4080 classes3:1,1:109 joint_kernel1 repair424319 no_new_kappa")


if __name__ == "__main__":
    main()
