#!/usr/bin/env python3
"""Exact phase-sensitive replay of the eight A/B D4 star normalizers.

Standard library only. Apache-2.0; substantial OpenAI Codex assistance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import types

GEOMETRY_SHA = "93716ba2a0297c4b468ca7344a9b744fcdaee4013f490443a58ddc7a6610eedd"
COMPILER_SHA = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--compiler", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), "output exists")
    geometry_raw, compiler_raw = args.geometry.read_bytes(), args.compiler.read_bytes()
    need(sha(geometry_raw) == GEOMETRY_SHA, "geometry SHA256")
    need(sha(compiler_raw) == COMPILER_SHA, "compiler SHA256")
    geometry = json.loads(geometry_raw)
    ce = types.ModuleType("_star_exact_compiler")
    ce.__file__ = str(args.compiler)
    sys.modules[ce.__name__] = ce
    exec(compile(compiler_raw, ce.__file__, "exec", dont_inherit=True, optimize=0),
         ce.__dict__)
    n = 7
    groups = geometry["groups7"]
    need(groups == [[7, 2, 50, 55], [13, 61, 8, 56], [117, 64, 69, 112]],
         "fixed eight-port star geometry")
    identity = ce.ident(n)
    F7 = ce.fourier(n)
    F = F7.then(ce.xgate(n, 33))
    phase_i = ce.Op(n, ce.identity(n), [("phase", 1)])

    def product(*items):
        result = identity
        for item in reversed(items):
            result = result.then(item)
        return result

    def same(left, right, name, phase_guard=True):
        need(left.tab == right.tab, name + ": signed Pauli images")
        if phase_guard:
            need(left.zero_state() == right.zero_state(), name + ": global phase")

    def native_zero(operator, name):
        need(ce.rank([x for x, z, phase in operator.tab[n:]]) == 0,
             name + ": native rank")
        record, literal = ce.lower_child(operator)
        need(record["rank"] == 0 and record["right"] is None,
             name + ": native lowering")
        same(operator, literal, name + ": lowering phase")
        need(all(event[0] in ("P", "X", "D", "phase")
                 for event in literal.circuit), name + ": literal monomial")
        rec = record["left"]
        need(not any(rec["quadratic_rows"]) and
             not any(rec["linear_Z4"]) and rec["phase"] == 0,
             name + ": phase-free address map")
        image = [ce.mv(rec["matrix_rows"], x) ^ rec["offset"]
                 for x in range(1 << n)]
        need(sorted(image) == list(range(1 << n)),
             name + ": address permutation")
        need(all(image[image[x]] == x for x in range(1 << n)),
             name + ": address involution")
        swaps = [[x, image[x]] for x in range(1 << n) if x < image[x]]
        symbols = list(range(1 << n))
        for a, b in swaps:
            symbols[a], symbols[b] = symbols[b], symbols[a]
        need(all(symbols[image[x]] == x for x in range(1 << n)),
             name + ": in-place symbolic arbitrary-input map")
        # Directly check every monomial address against its literal recipe.
        for x in range(1 << n):
            vector, denominator = literal.zero_state(x)
            need(denominator == 0 and
                 vector == [(int(y == image[x]), 0) for y in range(1 << n)],
                 name + ": literal basis address")
        return {"native": record, "literal_events": literal.circuit,
                "basis_address_image": image, "in_place_swaps": swaps,
                "complex_ADDs": 3 * len(swaps), "complex_NEGs": len(swaps),
                "Gaussian_unit_phase_multiplications": 0}

    rows = []
    controls = []

    def reject(name, actual, expected):
        try:
            same(actual, expected, name)
        except ValueError as error:
            need(str(error) in (name + ": signed Pauli images",
                                name + ": global phase"),
                 "unintended mutation rejection")
            controls.append({"name": name, "rejected": True,
                             "reason": str(error)})
        else:
            raise ValueError("mutation survived: " + name)

    for group in range(2):
        for coordinate, p in enumerate(groups[group]):
            q, r = groups[(group + 1) % 3][coordinate], groups[(group + 2) % 3][coordinate]
            dot = lambda x, y: (x & y).bit_count() & 1
            need(dot(p, p) == dot(q, q) == dot(r, r) == 1 and
                 dot(p, q) == dot(p, r) == dot(q, r) == 0,
                 "orthonormal port triple")
            w = q ^ r
            need(w and dot(w, w) == 0, "nonzero isotropic star direction")
            matrix = tuple((1 << j) ^ (w if w >> j & 1 else 0) for j in range(n))
            need(ce.mv(matrix, p) == p and ce.mv(matrix, q) == r and
                 ce.mv(matrix, r) == q, "star action on the actual triple")
            R = ce.perm(n, matrix)
            epsilon = (w.bit_count() // 2 + 1) % 2
            need(dot(w, 33) == epsilon, "actual full-F gauge condition")
            for x in range(1 << n):
                need((ce.mv(matrix, x).bit_count() - x.bit_count() -
                      2 * epsilon * dot(w, x)) % 4 == 0,
                     "complete mod-four character-weight identity")
            same(product(R, F7, R), product(ce.xgate(n, epsilon * w), F7),
                 "native ungauged phase correction")
            same(product(R, F, R), F, "actual invariant F covariance")
            same(product(R, R), identity, "star involution")
            Cp, Cq, Cr = ce.cgate(n, p), ce.cgate(n, q), ce.cgate(n, r)
            S = product(F, Cr.adjoint(), Cp.adjoint())
            T = product(F, Cp.adjoint(), Cq.adjoint())
            J = product(F, ce.xgate(n, p))
            K = product(T.adjoint(), J, R)
            same(K, product(Cq, Cp.adjoint(), R), "physical star K")
            A = product(Cq.adjoint(), K, Cp)
            same(A, R, "logical star A")
            same(product(R, S, R), T, "all-input source normalization")
            EX, EY = product(F, Cq.adjoint()), product(F, Cp.adjoint())
            same(product(T, Cp), EX, "source frame diagonal")
            same(product(T, Cq), EY, "target frame diagonal")
            H = A.adjoint()
            pre_x = product(Cp, H, Cp.adjoint())
            post_y = product(EY, H, EY.adjoint())
            same(pre_x, R, "physical pre-X H both orientations")
            same(post_y, R, "physical post-Y H both orientations")
            same(product(EY.adjoint(), T, K, Cp), R, "forward logical cross")
            same(product(EX.adjoint(), T, K.adjoint(), Cq), R,
                 "backward logical inverse cross")
            AB = product(T, K.adjoint(), T.adjoint(), K.adjoint())
            BB = product(T, AB.adjoint(), T.adjoint())
            T2 = product(T, T)
            same(AB, ce.xgate(n, p ^ q), "exact star AB")
            same(BB, ce.xgate(n, p ^ q), "exact star BB")
            same(T2, ce.xgate(n, 127 ^ p ^ q), "exact star T squared")
            same(product(T2, K, T.adjoint(), AB), product(T, K.adjoint()),
                 "wrapped inverse-B cross")
            same(product(BB, T2, T.adjoint(), AB), T,
                 "wrapped inverse-B Y diagonal")
            recipes = {}
            for name, operator in (
                    ("P", R), ("post", R), ("common_F_P", product(F, R, F.adjoint())),
                    ("pre_X_H", pre_x), ("post_Y_H", post_y),
                    ("AB", AB), ("BB", BB), ("T_squared", T2)):
                recipes[name] = native_zero(operator, name)
            need(len(recipes["P"]["in_place_swaps"]) == 32 and
                 len(recipes["AB"]["in_place_swaps"]) ==
                 len(recipes["BB"]["in_place_swaps"]) ==
                 len(recipes["T_squared"]["in_place_swaps"]) == 64,
                 "exact base involution swap counts")
            phase_wrong = product(phase_i, R, S, R)
            reject(str(p) + ": output phase i", phase_wrong, T)
            same(phase_wrong, T, "phase guard deleted", phase_guard=False)
            controls.append({"name": str(p) + ": delete phase guard",
                             "bad_phase_accepted": True,
                             "scope": "exact-operator equality predicate"})
            reject(str(p) + ": omit AB", product(T2, K, T.adjoint()),
                   product(T, K.adjoint()))
            reject(str(p) + ": physical K substituted for inverse K",
                   K, K.adjoint())
            if epsilon:
                reject(str(p) + ": omit invariant F translation",
                       product(R, F7, R), F7)
            rows.append({"group": group, "coordinate": coordinate, "p": p,
                         "q": q, "r": r, "w": w, "weight_w": w.bit_count(),
                         "epsilon": epsilon, "dot_w_33": dot(w, 33),
                         "R_rows": list(matrix), "logical_A_is_R": True,
                         "AB_BB_translation": p ^ q,
                         "T_squared_translation": 127 ^ p ^ q,
                         "literal_recipes": recipes})
    need(len(rows) == 8 and len(controls) == 36, "complete star/control coverage")
    need(sha(args.geometry.read_bytes()) == GEOMETRY_SHA and
         sha(args.compiler.read_bytes()) == COMPILER_SHA, "inputs changed")
    result = {
        "status": "PASS_EIGHT_AB_STAR_NORMALIZERS_WITH_EXACT_PHASE",
        "checker_sha256": sha(Path(__file__).read_bytes()),
        "input_sha256": {"geometry": GEOMETRY_SHA, "compiler": COMPILER_SHA},
        "rows": rows, "controls": controls, "ports": 8,
        "monomial_recipes": 64, "literal_basis_address_checks": 8192,
        "signed_Pauli_images_per_operator": 14,
        "exact_zero_column_phase_check": True,
        "enumerated_character_weight_checks": 1024,
        "unfused_wrapper_counts_per_port": {
            "forward_common_code": {"R": 4, "nonzero_translations": 0},
            "backward_common_code": {"R": 4, "nonzero_translations": 4}},
        "all_f_literal_cost": {
            "N": "2^(7f)",
            "R_swaps": "(2^(7f)-2^(6f))/2",
            "translation_swaps": "2^(7f-1)",
            "per_swap": "3 complex ADDs and 1 complex NEG; one extra magnitude bit",
            "binary_address_work": "O(49 f N) per monomial, no cycle-discovery search",
            "extra_complex_fields": 0},
        "limits": [
            "Eight fixed A/B h7 ports only; four C ports have a separate checker.",
            "Character-weight proof and tensor lift are written all-parameter arguments.",
            "8192 checks enumerate lowered monomial basis addresses; they are not "
            "independent full-program native-history simulations.",
            "No paid wrapper is omitted because its native rank is zero.",
            "No rounded network, whole caller, physical tape, or kappa claim."]}
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
