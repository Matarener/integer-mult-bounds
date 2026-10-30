#!/usr/bin/env python3
"""Replay four exact common-F normalizers, without repeating their search.

Standard library only. The pinned compiler is a producer; every rank-zero
lowering is independently interpreted on every computational basis vector.
Apache-2.0. Substantial OpenAI Codex assistance.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import types

COMPILER_SHA = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"
GEOMETRY_SHA = "93716ba2a0297c4b468ca7344a9b744fcdaee4013f490443a58ddc7a6610eedd"
WITNESS_SHA = "bc45cf6f3ab114c565fd330d01174092bf4a32d94d3e3e2c49f80ccaa602bb99"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(
                          ValueError("nonfinite JSON constant " + value)))


def load_compiler(raw, path):
    """Execute the authenticated bytes, with producer assertions retained."""
    name = "_carrier_exact_compiler"
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(raw, str(path), "exec", dont_inherit=True, optimize=0),
         module.__dict__)
    return module


def mv(rows, value):
    return sum(((row & value).bit_count() & 1) << j
               for j, row in enumerate(rows))


def phase_value(rows, linear, value):
    result = sum(linear[j] for j in range(len(rows)) if value >> j & 1)
    for j, row in enumerate(rows):
        if value >> j & 1:
            result += 2 * (((row >> (j + 1)) &
                            (value >> (j + 1))).bit_count() & 1)
    return result % 4


def times_i(pair, phase):
    a, b = pair
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def interpret(events, basis, n=7):
    """Independent sparse Gaussian-integer circuit interpreter."""
    state = {basis: (1, 0)}
    denominator = 0
    for event in events:
        kind = event[0]
        if kind == "P":
            state = {mv(event[1], x): value for x, value in state.items()}
            need(len(state) > 0, "permutation erased state")
        elif kind == "X":
            state = {x ^ event[1]: value for x, value in state.items()}
        elif kind == "D":
            state = {x: times_i(value, phase_value(event[1], event[2], x))
                     for x, value in state.items()}
        elif kind == "phase":
            state = {x: times_i(value, event[1])
                     for x, value in state.items()}
        elif kind == "C":
            q, sign = event[1:]
            need(sign in (-1, 1), "native sign")
            result = {}
            for x, (a, b) in state.items():
                for y, pair in ((x, (a - sign * b, b + sign * a)),
                                (x ^ q, (a + sign * b, b - sign * a))):
                    old = result.get(y, (0, 0))
                    result[y] = (old[0] + pair[0], old[1] + pair[1])
            state = {x: value for x, value in result.items()
                     if value != (0, 0)}
            denominator += 1
        else:
            raise ValueError("unknown circuit event " + repr(event))
        need(all(0 <= x < 1 << n for x in state), "address outside chart")
    while denominator and all(a % 2 == b % 2 == 0
                              for a, b in state.values()):
        state = {x: (a // 2, b // 2) for x, (a, b) in state.items()}
        denominator -= 1
    return state, denominator


def normalize_json(value):
    return json.loads(json.dumps(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry", type=pathlib.Path, required=True)
    parser.add_argument("--compiler", type=pathlib.Path, required=True)
    parser.add_argument("--witness", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), "output already exists")
    paths = {"geometry": args.geometry, "compiler": args.compiler,
             "witness": args.witness}
    raw = {key: path.read_bytes() for key, path in paths.items()}
    expected = {"geometry": GEOMETRY_SHA, "compiler": COMPILER_SHA,
                "witness": WITNESS_SHA}
    need({key: digest(value) for key, value in raw.items()} == expected,
         "source SHA256 binding")
    geometry, witness = strict_json(raw["geometry"]), strict_json(raw["witness"])
    ce = load_compiler(raw["compiler"], args.compiler)
    n = 7
    core = [group[0] for group in geometry["groups7"]]
    need(core == [7, 13, 117], "actual D4 core")
    need([(row["p"], row["q"]) for row in witness["rows"]] ==
         [(117, 7), (64, 2), (69, 50), (112, 55)], "four C-port coverage")
    identity = ce.ident(n)
    phase_i = ce.Op(n, ce.identity(n), [("phase", 1)])

    def product(*operators):
        # Conventional matrix order: product(A,B) means A B.
        result = identity
        for operator in reversed(operators):
            result = result.then(operator)
        return result

    def same(left, right, label, phase_guard=True):
        need(left.tab == right.tab, label + ": signed Pauli images")
        if phase_guard:
            need(left.zero_state() == right.zero_state(), label + ": global phase")

    def brank(operator):
        return ce.rank([x for x, z, phase in operator.tab[n:]])

    def zero_native(operator, label):
        need(brank(operator) == 0, label + ": zero native rank")

    def lower(operator, label, reference=None):
        zero_native(operator, label)
        record, literal = ce.lower_child(operator)
        need(record["rank"] == 0 and record["right"] is None,
             label + ": zero native rank")
        need(all(event[0] in ("P", "X", "D", "phase")
                 for event in literal.circuit), label + ": literal monomial")
        same(operator, literal, label + ": exact lowering")
        if reference is not None:
            need(normalize_json(record) == reference,
                 label + ": frozen native recipe")
        monomial = record["left"]
        columns = []
        for basis in range(1 << n):
            actual, denominator = interpret(operator.circuit, basis, n)
            lowered, lower_denominator = interpret(literal.circuit, basis, n)
            address = mv(monomial["matrix_rows"], basis) ^ monomial["offset"]
            phase = (phase_value(monomial["quadratic_rows"],
                                 monomial["linear_Z4"], basis) +
                     monomial["phase"]) % 4
            target = {address: times_i((1, 0), phase)}
            need(denominator == lower_denominator == 0 and
                 actual == lowered == target,
                 label + ": independent full-basis literal implementation")
            columns.append([address, phase])
        need(len({row[0] for row in columns}) == 1 << n,
             label + ": address bijection")
        # A literal in-place implementation: phase each old coordinate, then
        # rotate every address cycle with its smallest address as pivot.
        symbols = [[x, columns[x][1]] for x in range(1 << n)]
        cycles = []
        swaps = []
        for leader in range(1 << n):
            current = columns[leader][0]
            while current > leader:
                current = columns[current][0]
            if current < leader:
                continue
            cycle = [leader]
            current = columns[leader][0]
            while current != leader:
                cycle.append(current)
                swaps.append([leader, current])
                symbols[leader], symbols[current] = symbols[current], symbols[leader]
                current = columns[current][0]
            cycles.append(cycle)
        need(sorted(x for cycle in cycles for x in cycle) ==
             list(range(1 << n)), label + ": complete disjoint cycles")
        need(len(swaps) == (1 << n) - len(cycles),
             label + ": literal swap count")
        need(all(symbols[address] == [basis, phase]
                 for basis, (address, phase) in enumerate(columns)),
             label + ": in-place symbolic arbitrary-input map")
        return {"native": record, "literal_events": literal.circuit,
                "basis_image_address_phase": columns,
                "in_place_cycles": cycles,
                "in_place_pivot_swaps": swaps,
                "in_place_complex_ADDs": 3 * len(swaps),
                "in_place_swap_negations": len(swaps),
                "literal_cost_models": {
                    "out_of_place": "N=2^(7f) complex coordinate writes, at "
                                    "most N Gaussian-unit multiplications, "
                                    "O(49 f N) binary address/phase operations; "
                                    "requires a destination array",
                    "in_place_cycle_enumeration": "at most N Gaussian-unit "
                                                 "multiplications and N-1 "
                                                 "whole-coordinate swaps; "
                                                 "each swap is 3 complex ADDs "
                                                 "and 1 negation; O(49 f N^2) "
                                                 "binary address work and "
                                                 "O(f) address-counter bits",
                },
                "storage_scope": "The in-place algorithm uses no extra complex "
                                 "field. Its address counters and physical "
                                 "tape/controller are not an admitted supplier."}

    chart = ce.perm(n, ce.inv(ce.transpose(core + [5, 53, 30, 96], n), n))
    D = chart.then(ce.hadamard(n, [3, 4])).then(chart.adjoint()).then(
        ce.Op(n, ce.identity(n), [("phase", 3)]))
    VC = D.then(ce.cgate(n, core[0])).then(ce.cgate(n, core[1]))
    F = ce.fourier(n).then(ce.xgate(n, 33))
    rows = []
    total_controls = 0
    for row in witness["rows"]:
        p, q = row["p"], row["q"]
        Cp, Cq = ce.cgate(n, p), ce.cgate(n, q)
        S = product(VC, Cp.adjoint())
        T = product(F, Cp.adjoint(), Cq.adjoint())
        J = product(F, ce.xgate(n, p))
        G = tuple(row["G"])
        Gi = ce.inv(G, n)
        Git = ce.transpose(Gi, n)
        Q = tuple((1 << j) ^ sum((sum(((Git[j] >> k) & 1) *
                                                   ((Gi[k] >> i) & 1)
                                                   for k in range(n)) % 2) << i
                                  for i in range(n)) for j in range(n))
        need(list(Q) == row["Q"] and ce.transpose(Q, n) == Q,
             "quadratic common-pair formula")
        P = ce.perm(n, G).then(ce.diag(n, Q))
        post = product(T, P.adjoint(), S.adjoint())
        K = product(T.adjoint(), J, P)
        A = product(Cq.adjoint(), K, Cp)
        H = A.adjoint()
        same(A, product(Cp.adjoint(), P, Cp), "physical/logical kernel bridge")
        same(product(post, S, P), T, "arbitrary-input source normalization")
        # Actual frames are identical for the two normalized orientations.
        DX, DY = Cp, product(F, Cp.adjoint())
        EX, EY = product(F, Cq.adjoint()), DY
        same(product(T, Cp), EX, "source diagonal front")
        same(product(T, Cq), EY, "target diagonal front")
        same(product(EY.adjoint(), T, K, Cp), A, "forward logical cross")
        same(product(EX.adjoint(), T, K.adjoint(), Cq), H,
             "backward logical cross")
        pre_x = product(DX, H, DX.adjoint())
        post_y = product(DY, H, DY.adjoint())
        same(pre_x, P.adjoint(), "pre-X physical implementation")
        same(post_y, product(F, Cp.adjoint(), H, Cp, F.adjoint()),
             "post-Y physical implementation")
        # Nonzero blocks of both common-code identities, signs handled
        # explicitly by the scalar block alphabet.
        same(product(H, A, H), H, "F common-code lower-left")
        same(product(H, H.adjoint()), identity, "H inverse")
        same(product(H, identity), H, "F and B common-code diagonal")
        same(product(identity, H), H, "B common-code upper-right magnitude")
        AB = product(T, K.adjoint(), T.adjoint(), K.adjoint())
        BB = product(T, AB.adjoint(), T.adjoint())
        T2 = product(T, T)
        same(T2, ce.xgate(n, ((1 << n) - 1) ^ p ^ q),
             "T squared is its explicit translation")
        inverse_cross = product(T2, K, T.adjoint(), AB)
        inverse_y = product(BB, T2, T.adjoint(), AB)
        same(inverse_cross, product(T, K.adjoint()), "corrected inverse-B cross")
        same(inverse_y, T, "corrected inverse-B Y diagonal")
        same(product(T2, T.adjoint()), T, "corrected inverse-B X diagonal")
        same(product(product(F, P, F.adjoint()), F, P.adjoint()),
             F, "common-F conjugation cancellation")
        ranks = {label: brank(operator) for label, operator in
                 (("S", S), ("T", T), ("S_F_inverse", product(S, F.adjoint())),
                  ("T_F_inverse", product(T, F.adjoint())), ("logical_A", A),
                  ("physical_K", K))}
        need([ranks[key] for key in ("S", "T", "S_F_inverse", "T_F_inverse")] ==
             [5, 5, 2, 2], "split-Lagrangian rank hypotheses")
        recipes = {}
        for label, operator, reference in (
                ("P", P, row["pre_native"]),
                ("post", post, row["post_native"]),
                ("common_F_P", product(F, P, F.adjoint()), row["fullcut_native"]),
                ("pre_X_H_both_orientations", pre_x, row["forward_entry_native"]),
                ("post_Y_H_both_orientations", post_y, row["forward_exit_native"]),
                ("AB", AB, row["inverse_input"]),
                ("BB", BB, row["inverse_output"]),
                ("T_squared", T2, None)):
            recipes[label] = lower(operator, label, reference)
        controls = []

        def rejected(name, candidate, target):
            # Execute the changed boundary, retaining the signed-Pauli and
            # independent exact phase tests. Record the actual rejection.
            try:
                same(candidate, target, name)
            except ValueError as error:
                need(str(error) in (name + ": signed Pauli images",
                                    name + ": global phase"),
                     "mutation rejected by an unintended predicate")
                controls.append({"name": name, "rejected": True,
                                 "reason": str(error),
                                 "tableau_equal": candidate.tab == target.tab,
                                 "zero_state_equal":
                                     candidate.zero_state() == target.zero_state()})
            else:
                raise ValueError("mutation survived: " + name)

        phase_wrong = product(phase_i, post, S, P)
        rejected("multiply_output_normalizer_by_i", phase_wrong, T)
        need(phase_wrong.tab == T.tab, "phase-only defect must preserve tableau")
        same(phase_wrong, T, "phase_guard_deleted", phase_guard=False)
        controls.append({"name": "delete_global_phase_comparison",
                         "bad_phase_accepted_by_remaining_tableau_check":
                             True,
                         "scope": "the exact operator equality guard only"})
        rejected("omit_output_normalizer", product(S, P), T)
        rejected("omit_F_gauge_X33", product(post, S, P),
                 product(ce.fourier(n), Cp.adjoint(), Cq.adjoint()))
        no_chirp_cut = product(F, ce.perm(n, G), F.adjoint())
        need(brank(no_chirp_cut) > 0, "omitted chirp must cost positive rank")
        try:
            zero_native(no_chirp_cut, "omit_common_quadratic_chirp")
        except ValueError as error:
            need(str(error) == "omit_common_quadratic_chirp: zero native rank",
                 "chirp control rejected by unintended predicate")
            controls.append({"name": "omit_common_quadratic_chirp",
                             "rejected": True, "reason": str(error),
                             "actual_rank": brank(no_chirp_cut)})
        else:
            raise ValueError("mutation survived: omit_common_quadratic_chirp")
        rejected("omit_AB", product(T2, K, T.adjoint()),
                 product(T, K.adjoint()))
        rejected("omit_BB", product(T2, T.adjoint(), AB), T)
        rejected("omit_T_squared_on_both_outputs",
                 product(K, T.adjoint(), AB), product(T, K.adjoint()))
        rejected("replace_backward_inverse_kernel_by_forward_kernel", K,
                 K.adjoint())
        rejected("execute_logical_H_directly_at_X_entry", H, pre_x)
        need(len(controls) == 10, "complete per-port control coverage")
        total_controls += len(controls)
        rows.append({"p": p, "q": q, "G": list(G), "Q": list(Q),
                     "rank_hypotheses_and_kernels": ranks,
                     "normalization_all_arbitrary_inputs": True,
                     "both_orientations_pre_X_post_Y": True,
                     "swapped_inverse_full_AB_BB_T_squared_wrapper": True,
                     "monomial_recipes": recipes, "controls": controls,
                     "witness_search_trial_provenance": row["winning_trial"],
                     "search_replayed": False})
    need(len(rows) == 4 and total_controls == 40,
         "complete four-port control coverage")
    need({key: digest(path.read_bytes()) for key, path in paths.items()} ==
         expected, "inputs changed during replay")
    result = {
        "status": "PASS_FOUR_EXACT_COMMON_F_NORMALIZERS_AND_INVERSE_WRAPPERS",
        "checker_sha256": digest(pathlib.Path(__file__).read_bytes()),
        "input_sha256": expected, "dimension": 7, "ports": len(rows),
        "signed_Pauli_images_per_operator": 14,
        "independent_basis_columns_per_monomial": 128,
        "monomial_recipes": 32, "independent_basis_columns": 4096,
        "executed_controls_including_phase_check_deletions": total_controls,
        "rows": rows,
        "limits": [
            "Finite exact replay covers four named h7 ports, not all gauges.",
            "All-dimension existence and all-f tensor lift are written proofs.",
            "No full routed caller, physical tape, rounding, ownership or kappa claim.",
            "Each literal rank-zero recipe remains a paid array scan.",
            "Native source-carrier histogram and dirty bus restoration are "
            "separate proof obligations.",
            "The old finite gauge census is provenance, not an optimality bound."
        ]
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
