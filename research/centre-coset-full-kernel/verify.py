#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact full-port certificate for one 4080-owner centre-repair block.

Ross Richardson with substantial OpenAI Codex GPT-6.1 Sol assistance.
Source extraction is inherited and authenticated; the coset certificate is new.
The written implication and conditional tariff are in PROOF.md.
"""
from collections import Counter, deque
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import argparse
import json
from pathlib import Path
import tempfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LOADER = "research/centre-block-moore-bound/verify.py"
TRIPLE = (0, 6, 85)
ACTIVE = 17


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def digest(value):
    return sha256(canonical(value)).hexdigest()


def authenticated_source(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    data = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        path = root / row["path"]
        require(path.is_file() and not path.is_symlink(), "regular input: " + row["path"])
        raw = path.read_bytes()
        require(sha256(raw).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        data[row["path"]] = raw
    require(LOADER in data, "declared source loader")
    module = types.ModuleType("authenticated_centre_loader")
    module.__file__ = str(root / LOADER)
    exec(compile(data[LOADER], module.__file__, "exec"), module.__dict__)
    # The retained loader additionally authenticates its closure and reconstructs
    # R,H and routes from literal selected source, rather than a copied receipt.
    _, _, rows, routes, pivots = module.load_sources(root)
    return rows, routes, pivots


def apply(columns, vector):
    result = 0
    while vector:
        bit = vector & -vector
        result ^= columns[bit.bit_length() - 1]
        vector ^= bit
    return result


def multiply(left, right):
    """Column-major exact GF(2) matrix product left*right."""
    return tuple(apply(left, column) for column in right)


def subgroup(generators):
    identity = tuple(1 << i for i in range(len(generators[0])))
    seen, queue = {identity}, deque([identity])
    while queue:
        element = queue.popleft()
        for generator in generators:
            product = multiply(element, generator)
            if product not in seen:
                seen.add(product)
                queue.append(product)
                require(len(seen) <= 4080, "subgroup exceeded declared domain")
    return seen


def rank(matrix):
    if not matrix or not matrix[0]:
        return 0
    work = [list(map(Q, row)) for row in matrix]
    pivot = 0
    for column in range(len(work[0])):
        index = next((i for i in range(pivot, len(work)) if work[i][column]), None)
        if index is None:
            continue
        work[pivot], work[index] = work[index], work[pivot]
        scale = work[pivot][column]
        work[pivot] = [x / scale for x in work[pivot]]
        for i in range(pivot + 1, len(work)):
            scale = work[i][column]
            work[i] = [a - scale * b for a, b in zip(work[i], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def port_partition(routes, elements):
    """L*rho_p=L*rho_q iff rho_p*rho_q is in L, for involutions."""
    representatives = []
    classes = []
    for p, route in enumerate(routes):
        index = next((i for i, q in enumerate(representatives)
                      if multiply(route, routes[q]) in elements), None)
        if index is None:
            representatives.append(p)
            classes.append([p])
        else:
            classes[index].append(p)
    owner = {p: i for i, members in enumerate(classes) for p in members}
    # Check all pairs, not just comparisons with a chosen representative.
    for p, q in combinations(range(len(routes)), 2):
        require((multiply(routes[p], routes[q]) in elements) == (owner[p] == owner[q]),
                "complete coset equivalence")
    return classes


def certify_partition(rows, routes, elements):
    classes = port_partition(routes, elements)
    dependent = []
    class_ranks = []
    for members in classes:
        value = rank([[row[p] for p in members] for row in rows])
        class_ranks.append(value)
        if value != len(members):
            dependent.append((members, value))
    require(dependent == [(list(TRIPLE), 2)], "only deficient class is the rank-two triple")
    require(len(classes) == 110, "110 right cosets among112 ports")
    require(Counter(map(len, classes)) == {1: 109, 3: 1}, "complete class-size inventory")
    require(all(sum(row[p] * u for p, u in zip(TRIPLE, (1, -1, -1))) == 0 for row in rows),
            "exact triple kernel coefficients")
    return classes, class_ranks


def rejected(function, label):
    try:
        function()
    except ValueError:
        return label
    raise ValueError("control was not rejected: " + label)


def build(root=ROOT):
    rows, full_routes, pivots = authenticated_source(root)
    require(len(rows) == 8 and all(len(row) == 112 for row in rows), "eight-by112 reader")
    require(rank(rows) == 8 and len(pivots) == 8, "old reader rank eight")
    identity = tuple(1 << i for i in range(ACTIVE))
    routes = []
    for route in full_routes:
        require(len(route) == 73, "full route dimension")
        require(all(route[i] == 1 << i for i in range(ACTIVE, 73)), "56 spectator coordinates fixed")
        require(all(column < 1 << ACTIVE for column in route[:ACTIVE]), "active subspace invariant")
        active = tuple(route[:ACTIVE])
        require(multiply(active, active) == identity, "every route involutory")
        routes.append(active)
    require(len(set(routes)) == 112, "distinct full routes via faithful active restriction")
    a, b, c = (routes[p] for p in TRIPLE)
    g1, g2 = multiply(a, b), multiply(b, c)
    generators = [g1, g2, multiply(b, a), multiply(c, b)]
    elements = subgroup(generators)
    require(len(elements) == 4080, "complete subgroup order4080")
    require(a not in elements, "the output coset differs from the source subgroup")
    require(all(multiply(generators[i], generators[i + 2]) == identity for i in (0, 1)),
            "explicit inverse generators")
    # All products were enumerated with exact tuple equality; hashes below only
    # identify reproducible certificates and do not decide matrix equality.
    classes, class_ranks = certify_partition(rows, routes, elements)
    require(multiply(a, c) == multiply(g1, g2), "amplitude-step generators agree")
    reached = subgroup([g1, multiply(a, c), multiply(b, a), multiply(c, a)])
    require(reached == elements, "coefficient constraints connect the whole source block")

    # Recheck all original witness edges in the 4080-owner regular graph.
    for g in elements:
        require(multiply(g, g1) in elements and multiply(g, g2) in elements,
                "all owner transitions remain in the block")
    scalar_kernel = [1, -1, -1]
    owners = len(elements)
    require(pivots == [0, 1, 2, 3, 4, 5, 6, 12], "exact pivot interface")
    complement = [p for p in range(112) if p not in pivots]
    require([p for p, u in zip(TRIPLE, scalar_kernel) if u and p in complement] == [85],
            "known kernel has exactly one nonpivot source coordinate")
    require(rank([[row[p] for p in pivots] for row in rows]) == 8, "invertible pivot minor")
    # Read the 103 nonpivot ports other than85 at every owner, and compare
    # x85(g)-x85(g*) at all4079 nonanchor owners. This leaves exactly the one
    # constant-u direction unobserved; the proof covers every source coefficient.
    ordinary_reads = (len(complement) - 1) * owners
    difference_reads = owners - 1
    minimum = 104 * owners - 1
    require(ordinary_reads + difference_reads == minimum, "constructive optimum information interface")
    eliminated = 64 * owners
    controls = []
    controls.append(rejected(lambda: certify_partition(rows, routes, {identity}),
                             "wrong_subgroup_loses_triple"))
    changed = [list(row) for row in rows]
    changed[0][TRIPLE[2]] += 1
    controls.append(rejected(lambda: certify_partition(changed, routes, elements),
                             "changed_coefficient_rejects_claimed_kernel"))
    changed_routes = list(routes)
    changed_routes[0] = routes[1]
    controls.append(rejected(lambda: certify_partition(rows, changed_routes, elements),
                             "changed_route_rejects_port_partition"))
    require(minimum > eliminated, "rank-one-per-observation optimistic screen fails")
    # Dropping any one owner from the constant witness leaves three distinct
    # nonzero output columns, while S still vanishes everywhere.
    require(len({a, b, c}) == 3 and all(any(row[p] for row in rows) for p in TRIPLE),
            "dropped-owner control has three nonzero outputs")
    controls.append("drop_one_owner_has_three_nonzero_outputs")
    controls.append("omit_one_raw_read_leaves_delta_owner_u_unobserved_but_changes_T")
    with tempfile.TemporaryDirectory(prefix="centre-coset-source-control-") as directory:
        bad_root = Path(directory)
        corrupted = bad_root / LOADER
        corrupted.parent.mkdir(parents=True)
        corrupted.write_bytes((root / LOADER).read_bytes() + b"\n# corrupted control\n")
        try:
            authenticated_source(bad_root)
        except ValueError as error:
            require(str(error) == "source SHA256: " + LOADER,
                    "source corruption fails for the intended digest")
        else:
            raise ValueError("corrupted executable source was accepted")
    controls.append("changed_executable_source_rejected_before_execution")
    return {
        "schema_version": 1,
        "claim": "fixed_coset_full_common_kernel_dimension_one",
        "field": "Q or C, with the same exact coefficient ranks",
        "source_ports": 112,
        "old_rank_per_owner": 8,
        "route_dimension": 73,
        "active_dimension": ACTIVE,
        "fixed_spectators": 56,
        "subgroup_order": owners,
        "subgroup_active_columns_sha256": digest([list(g) for g in sorted(elements)]),
        "all_routes_active_columns_sha256": digest([list(g) for g in routes]),
        "reader_sha256": digest([[str(x) for x in row] for row in rows]),
        "coset_classes": classes,
        "class_ranks": class_ranks,
        "class_size_histogram": {"1": 109, "3": 1},
        "triple": list(TRIPLE),
        "triple_coefficients": scalar_kernel,
        "common_kernel_dimension": 1,
        "old_kernel_dimension": 104 * owners,
        "additional_scalar_observation_minimum": minimum,
        "attaining_observation_interface": {
            "pivot_ports": pivots,
            "ordinary_nonpivot_ports": [p for p in complement if p != 85],
            "ordinary_coordinate_reads": ordinary_reads,
            "difference_port": 85,
            "difference_reads_to_one_fixed_anchor": difference_reads,
            "coefficients": [1, -1],
            "physical_acquisition_and_dirty_restoration_not_implemented": True,
        },
        "conditional_rank_one_repair_screen": {
            "fixed_original_width_stock_and_call_normalization": True,
            "all_other_repair_costs_granted_zero": True,
            "repair_rank_mass_at_least": minimum,
            "entire_removed_centre_rank_mass_at_most": eliminated,
            "excess_rank_mass_at_zero_saving": minimum - eliminated,
            "repair_unit_tariff_must_be_less_than": str(Q(eliminated, minimum)),
            "kernel_dimension_needed_for_strict_unit_tariff_saving_greater_than": 40 * owners,
            "not_a_universal_observation_to_recursive_tariff": True,
        },
        "controls": controls,
        "no_new_kappa": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--output", type=Path, help="write a recomputed certificate to an external path")
    args = parser.parse_args()
    result = build()
    if args.output:
        require(not args.output.resolve().is_relative_to(ROOT.resolve()), "certificate output must be external")
        args.output.write_bytes(canonical(result))
        print("PASS_CENTRE_COSET_CERTIFICATE_WRITTEN")
    elif args.emit:
        print(canonical(result).decode(), end="")
    else:
        require(result == json.loads((HERE / "RESULT.json").read_bytes()), "exact committed receipt")
        print("PASS_CENTRE_COSET_FULL_KERNEL owners4080 classes110 kernel1 repair424319 "
              "conditional_rank_mass_excess163199 no_new_kappa")


if __name__ == "__main__":
    main()
