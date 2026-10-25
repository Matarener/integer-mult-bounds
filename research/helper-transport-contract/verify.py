#!/usr/bin/env python3
"""Exact native warp and specified formal exit-shear discriminants.

This is a bounded operator test, not a source-word replacement or kappa claim.
The exact Clifford compiler is the attributed repository implementation.
OpenAI Codex assisted this audit; Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True

COMPILER = "research/t74-native-fast/vendor/native/new/code/borrow/vendor/clifford/clifford_exact.py"
COMPILER_SHA = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"
CANONICAL = "research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz"
PROVIDER = (
    "research/coupled-helper-neutral-completion/capsule/workspace/"
    "swarm-provider-audit-sol-high-20261024/repository/research/"
    "native-rank8-helper-provider/WORD.json.gz"
)
PINS = {
    COMPILER: COMPILER_SHA,
    CANONICAL: "7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05",
    PROVIDER: "7dc356001ed597ad6fc9fd3e0bc6ff7e3ec3a580a579a956827aa17fccfdd2dc",
}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(root):
    for name, pin in PINS.items():
        need(sha256((root / name).read_bytes()).hexdigest() == pin, "source pin: " + name)
    payload = gzip.decompress((root / CANONICAL).read_bytes())
    source_word = json.loads(payload)
    canonical = source_word["canonical"]
    provider = json.loads(gzip.decompress((root / PROVIDER).read_bytes()))
    need(provider["source_sha256"] == sha256(payload).hexdigest(), "canonical payload link")
    need(provider["direction"] == "backward", "selected provider direction")
    need(provider["word"][:9044] == source_word["programs"]["backward"][:9044],
         "selected prefix equals inherited backward prefix")
    need(canonical["frames"][21] == [273] and canonical["frames"][57] == [324],
         "actual source fixture frame bases")
    need(provider["word"][9044] == ["climb", "warp_retimed", 300, 0, 21, 1],
         "selected helper300 enters line273")
    need(provider["word"][9105] == ["climb", "warp_retimed", 295, 57, 430, 1],
         "selected helper295 leaves line324")
    spec = importlib.util.spec_from_file_location("transport_exact_clifford", root / COMPILER)
    ce = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = ce
    spec.loader.exec_module(ce)
    return ce, canonical, provider["word"]


def equal(a, b):
    # Full Pauli action fixes a Clifford operator up to phase. One exactly
    # normalized nonzero state fixes the remaining absolute phase.
    return a.tab == b.tab and a.zero_state() == b.zero_state()


def lower(ce, op):
    recipe, decoded = ce.lower_child(op)
    need(equal(op, decoded), "exact lowering: tableau and absolute phase")
    need(recipe["rank"] == ce.rank([x for x, z, p in op.tab[op.n:]]),
         "binary B-block rank")
    return recipe


def run_fixture(ce, n, u, v, swaps):
    columns = [1 << i for i in range(n)]
    for a, b in swaps:
        columns[a], columns[b] = columns[b], columns[a]
    rows = ce.transpose(columns, n)
    need(ce.mv(rows, u) == v, "binary map carries source line to target line")
    need(ce.inv(rows, n) == rows, "fixture coordinate permutation is involutive")
    # An orthogonal permutation has Q=I+G^-T G^-1=0. Its native K_G lift
    # is exactly this permutation, without an omitted quadratic phase.
    operator = ce.perm(n, rows)
    source_frame = ce.canonical_frame(n, [u])
    target_frame = ce.canonical_frame(n, [v])
    warp = source_frame.adjoint().then(operator).then(target_frame)
    unchanged = source_frame.adjoint().then(target_frame)
    correction = target_frame.adjoint().then(operator.adjoint()).then(target_frame)
    warp_recipe = lower(ce, warp)
    identity_recipe = lower(ce, unchanged)
    repair_recipe = lower(ce, correction)
    need(warp_recipe["rank"] == 0, "legal native warp has zero recursive rank")
    need(identity_recipe["rank"] == repair_recipe["rank"] == 2,
         "distinct-line identity transport and correction have rank two")
    need(equal(warp.then(correction), unchanged), "warp plus repair is exact")
    need(not equal(warp, unchanged), "warp does not retain logical value")
    need(not equal(warp.then(operator.adjoint()), unchanged),
         "inverse logical warp in the wrong physical gauge is not a repair")
    need(equal(operator.then(operator.adjoint()), ce.ident(n)), "exact operator inverse")
    witness = next(j for j in range(1 << n) if ce.mv(rows, j) != j)
    need(operator.zero_state(witness) != ce.ident(n).zero_state(witness),
         "warp-ADD-inverse-warp has the wrong transferred coefficient")
    if n == 2:
        need(all(warp.then(correction).zero_state(j) == unchanged.zero_state(j)
                 for j in range(1 << n)), "all four minimal input columns")
    phased = ce.Op(n, operator.tab, operator.circuit + [("phase", 1)])
    need(phased.tab == operator.tab and not equal(phased, operator),
         "phase-only mutation rejected despite identical tableau")
    need(ce.rank([x for x, z, p in phased.tab[n:]]) == 0,
         "phase mutation retains rank zero")
    return {
        "dimension": n,
        "source_line": [u],
        "target_line": [v],
        "binary_columns": columns,
        "native_warp": warp_recipe,
        "logical_identity_transport": identity_recipe,
        "post_warp_identity_correction": repair_recipe,
        "warp_then_correction_exact": True,
        "logical_transfer_witness": {
            "input_basis": witness,
            "wrong_transferred_basis": ce.mv(rows, witness),
            "required_transferred_basis": witness,
            "coefficient": [1, 0],
        },
        "global_phase_only_mutation_rejected": True,
        "ungauged_inverse_repair_mutation_rejected": True,
        "all_minimal_input_columns_checked": 4 if n == 2 else None,
        "recursive_invoice": {"free_warp": {}, "value_preserving_repair": {2: 1}},
        "physical_adapter_allowance": (
            "Warp: one exact monomial recipe. Rank-two repair: two monomial "
            "adapters. Rank zero does not mean zero movement/scalar cost."
        ),
    }


def prefix_row(program, field, stop):
    """Reverse-substitute one row; retain exact free warp words."""
    need(not any(event[0] == "center" for event in program[:stop]),
         "targeted prefix has no center operators")
    terms = {(("L", field), ()): Q(1)}

    def add(key, value):
        value += terms.get(key, Q(0))
        if value:
            terms[key] = value
        else:
            terms.pop(key, None)

    for event in reversed(program[:stop]):
        if event[0] == "scalar":
            op = event[1]
            target = tuple(op[1])
            old = [(key, value) for key, value in terms.items() if key[0] == target]
            if op[0] == "add":
                for (_, word), value in old:
                    add((tuple(op[2]), word), value * Q(op[3], op[4]))
            elif op[0] == "scale":
                for key, value in old:
                    terms[key] = value * Q(op[2], op[3])
            elif op[0] in ("copy", "clear"):
                for (_, word), value in old:
                    del terms[target, word]
                    if op[0] == "copy":
                        add((tuple(op[2]), word), value)
            else:
                raise ValueError("unknown scalar opcode")
        elif event[0] == "warp":
            target = tuple(event[1])
            symbol = (1 if event[2] > 0 else -1) * (abs(event[2]) + 10**6)
            old = [(key, value) for key, value in terms.items() if key[0] == target]
            for key, value in old:
                del terms[key]
            for (_, word), value in old:
                new_word = word[:-1] if word and word[-1] == -symbol else word + (symbol,)
                add((target, new_word), value)
        else:
            need(event[0] in ("climb", "phase", "adapter", "residual_adapter"),
                 "known coordinate-preserving prefix event")
    return terms


def final_frames(canonical, program):
    """Check frame chronology only; do not certify logical zero-retag values."""
    current = {("L", i): frame for i, frame in enumerate(canonical["start"])}
    current[("C", 0)] = None
    for event in program:
        kind = event[0]
        if kind == "climb":
            _, _, field, old, new, _ = event
            role = ("L", field)
        elif kind == "warp":
            _, field, _, old, new = event
            role = tuple(field)
        elif kind == "center":
            _, field, old, new, _ = event
            role = ("C", field)
        elif kind == "zero_retag":
            _, field, old, new = event
            role = ("L", field)
        elif kind == "scalar":
            operation, frame = event[1:]
            target = tuple(operation[1])
            if operation[0] in ("copy", "clear"):
                current[target] = frame
            else:
                need(current[target] == frame, "scalar target frame history")
            if operation[0] in ("add", "copy"):
                need(current[tuple(operation[2])] == frame, "scalar source frame history")
            continue
        else:
            need(kind in ("phase", "adapter", "residual_adapter"), "known frame-history marker")
            continue
        need(current[role] == old, "chronological source frame")
        current[role] = new
    need([current[("L", i)] for i in range(len(canonical["start"]))] == canonical["final"],
         "actual selected-provider final frames agree on all original roles")
    return current


def rebase_exit_test(ce, canonical, program):
    actual_frames = final_frames(canonical, program)
    row = prefix_row(program, 300, 9044)
    coefficients = {
        113: 1, 123: -1, 128: 1, 135: -1, 140: -1, 145: -1,
        162: -1, 163: 1, 174: -1, 183: -1, 190: 1, 194: 1,
        203: -1, 205: -1, 216: 1, 221: -1,
    }
    expected = {(("L", i), ()): Q(sign, 2) for i, sign in coefficients.items()}
    expected[(("L", 300), ())] = Q(1)
    need(row == expected, "exact selected-backward cutoff row")
    need(prefix_row(program, 19, 9044) == {(("L", 19), ()): Q(1)}, "pure x19 cutoff row")
    need(all(canonical["start"][i] == 0 for i in [300, *coefficients]),
         "entrance rebasing is a legal common-frame scalar shear")
    need(canonical["final"][300] == 1, "original helper300 has rank-nine target")
    target = ce.canonical_frame(9, canonical["frames"][21])
    exits = []
    for field, sign in coefficients.items():
        frame = actual_frames[("L", field)]
        basis = canonical["frames"][frame]
        points = {0}
        for vector in basis:
            points |= {x ^ vector for x in tuple(points)}
        need(len(basis) == 8 and 273 in points, "Y exit hyperplane contains retired line")
        coefficient = ce.canonical_frame(9, basis).adjoint().then(target)
        rank = ce.rank([x for x, z, p in coefficient.tab[9:]])
        distance = 1 + len(basis) - 2
        need(rank == distance == 7, "same-label formal exit coefficient has rank seven")
        exits.append({
            "field": field, "prefix_coefficient": str(Q(sign, 2)),
            "final_frame": frame, "final_basis": basis,
            "contains_line273": True, "formal_exit_shear_coefficient_rank": rank,
        })
    # Lower one concrete coefficient including phase; all sixteen ranks above
    # are independently compared with exact subspace distances.
    first = canonical["frames"][exits[0]["final_frame"]]
    need(lower(ce, ce.canonical_frame(9, first).adjoint().then(target))["rank"] == 7,
         "concrete rank-seven coefficient lowering")
    climbs = [[i, e] for i, e in enumerate(program) if e[0] == "climb" and e[2] == 300]
    profile = Counter(e[-1] for i, e in climbs)
    need(profile == {1: 6, 3: 1}, "complete helper300 paid profile")
    all_y_dimensions = Counter()
    plain_scalar_ranks = Counter()
    for field in range(112, 224):
        basis = canonical["frames"][actual_frames[("L", field)]]
        points = {0}
        for vector in basis:
            points |= {x ^ vector for x in tuple(points)}
        all_y_dimensions[len(basis)] += 1
        plain_scalar_ranks[1 + len(basis) - 2 * int(273 in points)] += 1
    need(all_y_dimensions == {8: 112}, "all actual selected Y exits are rank eight")
    need(plain_scalar_ranks == {7: 52, 9: 60}, "conditional plain-scalar cross-frame ranks")
    return {
        "cut_before_event": 9044,
        "helper300_prefix_row": [
            {"input": list(role), "operator_word": list(word), "coefficient": str(value)}
            for (role, word), value in sorted(row.items())
        ],
        "entrance_basis_shear_is_invertible_and_coframed": True,
        "actual_selected_final_frame_history_checked_on_original_roles": len(canonical["start"]),
        "targeted_prefix_has_no_center_operators": True,
        "original_productive_target": 9,
        "proposed_line21_targets": [1, 8],
        "unchanged_helper_paid_profile_if_handoff_legal": dict(profile),
        "helper300_paid_events": climbs,
        "specified_same_label_formal_exit_shear": exits,
        "minimum_and_maximum_cross_coefficient_rank": [7, 7],
        "one_concrete_cross_coefficient_lowered_with_absolute_phase": True,
        "specified_same_label_exit_shear_is_not_rank_zero": True,
        "all_sixteen_formal_exit_shear_coefficients_are_non_monomial": True,
        "plain_scalar_Y_exit_coefficient_class": {
            "fields": [112, 223],
            "indexing": "inclusive",
            "actual_terminal_dimensions": dict(all_y_dimensions),
            "rank_histogram_by_exact_frame_distance": dict(plain_scalar_ranks),
            "minimum_nonzero_cross_coefficient_rank": 7,
            "scope": (
                "A nonzero plain-scalar Y-output coefficient mapped to retired "
                "line21 has rank at least seven. This neither derives the true "
                "decoder coefficients nor bounds arbitrary joint decoder circuits."
            ),
        },
        "scope": (
            "Specified same-label formal exit shear only. No claim that mixed input "
            "coordinates are dependent, no sum of sixteen H7 charges, and no "
            "lower bound on every coordinated joint decoder. If the selected main "
            "output is H Y, a true inverse wrapper may require R H^-1 rather than "
            "these sixteen same-label R coefficients. The true decoder is unconstructed."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    ce, canonical, program = load(args.repo)
    report = {
        "status": "PASS_NATIVE_WARP_DISCRIMINANT_NO_SOURCE_REPLACEMENT",
        "source_inputs": [{"path": path, "sha256": pin} for path, pin in PINS.items()],
        "selected_source_binding": {
            "direction": "backward", "frame21": [273], "frame57": [324],
            "helper300_line_entry_event": 9044, "helper295_line_exit_event": 9105,
            "new_permutation_is_existing_registered_warp": False,
        },
        "fixtures": [
            run_fixture(ce, 2, 1, 2, [(0, 1)]),
            run_fixture(ce, 9, 273, 324, [(0, 2), (4, 6)]),
        ],
        "entrance_rebasing_exit_test": rebase_exit_test(ce, canonical, program),
        "no_new_kappa_claimed": True,
        "scope": (
            "Two exact warp examples and a specified same-label formal exit shear. "
            "No global impossibility claim, new native word, productive-target "
            "admission or caller replay."
        ),
    }
    serialized = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    elif args.json:
        print(serialized, end="")
    else:
        print(report["status"] + " warp_rank=0 repair_rank=2 formal_exit_rank=7")


if __name__ == "__main__":
    main()
