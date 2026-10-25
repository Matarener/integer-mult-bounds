#!/usr/bin/env python3
"""Exact partial sum capture on the two immutable PR3945 words.

Python standard library only.  No assertions are used.  With --output, write a
fresh deterministic result to that path; otherwise compare against RESULT.json.
The imported, source-pinned audit core is credited in DERIVATION.md.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
SOURCE_FREEZE = "f0631e4329ef4124c498fe3d1c500aab34ce6490"
SOURCE_PINS = {
    "predecessor4061/frozen/WORD-base.json.gz":
        "08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0",
    "predecessor4061/frozen/WORD-extra.json.gz":
        "d83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299",
    "source4076/vendor/audit_core.py":
        "888679ca8502cdcb100420fe5382a052529a494bf76cb332928b86e62612b951",
}
OLD_BLOCK = [
    ["add", 183, 600, 1, 4, [45]],
    ["add", 202, 600, -1, 4, [45]],
    ["add", 175, 600, 1, 4, [45]],
    ["add", 123, 600, -1, 4, [45]],
    ["add", 183, 601, 1, 4, [45]],
    ["add", 202, 601, 1, 4, [45]],
    ["add", 175, 601, 1, 4, [45]],
    ["add", 123, 601, 1, 4, [45]],
]
# Indices are zero-based.  The four exception reads remain byte-identical.
NEW_BLOCK = [copy.deepcopy(OLD_BLOCK[i]) for i in (1, 3, 5, 7)] + [
    ["add", 600, 601, 1, 1, [45]],
    copy.deepcopy(OLD_BLOCK[0]),
    copy.deepcopy(OLD_BLOCK[2]),
    ["add", 600, 601, -1, 1, [45]],
]
FULL_BASIS = [256, 128, 64, 32, 16, 8, 4, 2, 1]
INVERSE_PAIR = [
    ["add", 600, 601, 1, 1, FULL_BASIS],
    ["add", 600, 601, -1, 1, FULL_BASIS],
]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_core():
    for name, expected in SOURCE_PINS.items():
        need(file_digest(PACKAGE / name) == expected, "source pin differs: " + name)
    spec = importlib.util.spec_from_file_location("pinned_partial_capture_audit",
                                                PACKAGE / "source4076/vendor/audit_core.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def local_rows(gates):
    """An independent six-coordinate rational check of the changed block."""
    regs = (123, 175, 183, 202, 600, 601)
    rows = {r: {r: Q(1)} for r in regs}
    for kind, dst, src, num, den, frame in gates:
        need(kind == "add" and dst != src and frame == [45], "local gate format")
        for var, coefficient in list(rows[src].items()):
            value = rows[dst].get(var, Q(0)) + Q(num, den) * coefficient
            if value:
                rows[dst][var] = value
            else:
                rows[dst].pop(var, None)
    return rows


def row_digest(rows):
    return digest([[r, [[var, list(word), str(q)] for (var, word), q in sorted(row.items())]]
                   for r, row in sorted(rows.items())])


def first_difference(expected, actual):
    for r in sorted(set(expected) | set(actual)):
        erow, arow = expected.get(r, {}), actual.get(r, {})
        for var, word in sorted(set(erow) | set(arow)):
            if erow.get((var, word), 0) != arow.get((var, word), 0):
                return {"output": r, "input": var, "operator_word": list(word),
                        "expected": str(erow.get((var, word), 0)),
                        "actual": str(arow.get((var, word), 0))}
    return None


def exact_contract(core, word, rows, dual=False):
    regs = sorted(set(range(core.N)) - set(word["removed"]))
    regs += sorted(int(c) + core.N for c in word["helper_final"])
    need(len(regs) == 723 and set(rows) == set(regs), "incomplete 723-coordinate domain")
    for r in regs:
        expected = {(r, ()): Q(1)}
        if not dual and core.is_target(r):
            expected[r - core.V, ()] = Q(1)
        if dual and r < core.V:
            expected[r + core.V, ()] = Q(-1)
        need(rows[r] == expected, "full arbitrary-input contract differs at " + str(r))


def primitive_counts(core, word):
    prefix, cleanup = core.program(word)
    counts = lambda gates: dict(sorted(Counter(g[0] for g in gates).items()))
    return {"prefix": counts(prefix), "cleanup": counts(cleanup),
            "complete": counts(prefix + cleanup),
            "prefix_records": len(prefix), "cleanup_records": len(cleanup),
            "complete_records": len(prefix) + len(cleanup)}


def count_delta(old, new):
    return {k: new.get(k, 0) - old.get(k, 0) for k in sorted(set(old) | set(new))}


def paid_description(core, word):
    bill, widths, chain, start, end = core.frame_bill(word, lagrangian=True)
    local_regs = (123, 175, 183, 202, 600, 601)
    block_events = {r: [(where, d, mask) for where, d, mask in chain[r]
                        if where[0] == "B" and 77 <= where[1] < 85]
                    for r in local_regs}
    need(all(block_events[r] and chain[r][0] == block_events[r][0] for r in local_regs),
         "local frame entrances are not the declared starting frames")
    entrance = {str(r): core.dim(start[r]) for r in local_regs}
    exit_frames = {str(r): core.dim(block_events[r][-1][2]) for r in local_regs}
    need(entrance == {str(r): int(r >= 600) for r in local_regs}
         and all(mask == core.span([45]) for events in block_events.values()
                 for _, _, mask in events), "fixed local boundary frames differ")
    local_bill = dict(sorted(Counter(d for events in block_events.values()
                                    for _, d, _ in events if type(d) is int and d > 0).items()))
    need(local_bill == {1: 4}, "local block does not attain the four-target rank-1 floor")
    # Preserve helper identities as well as the width multiset.
    ordered = [[r, core.dim(end[r]) - core.dim(start[r]), hex(start[r]), hex(end[r])]
               for r in sorted(start) if r >= 2 * core.V]
    positive = [[r, [[d, hex(mask)] for _, d, mask in chain[r]
                     if type(d) is int and d > 0]] for r in sorted(start)]
    return {"profile": bill, "width_inventory": widths,
            "local_block": {"entrance_dimensions": entrance, "exit_dimensions": exit_frames,
                            "paid_profile": local_bill,
                            "helper_positive_climbs": 0, "target_rank1_climbs": 4},
            "ordered_helper_contract_sha256": digest(ordered),
            "positive_frame_transitions_sha256": digest(positive),
            "live_helpers": len(ordered),
            "capture_helpers": {str(r): {"entrance_dimension": core.dim(start[r]),
                                             "terminal_dimension": core.dim(end[r]),
                                             "width": core.dim(end[r]) - core.dim(start[r]),
                                             "positive_climbs": [d for _, d, _ in chain[r]
                                                                 if type(d) is int and d > 0]}
                                for r in (600, 601)}}


def candidate(core, old):
    need(old["B"][77:85] == OLD_BLOCK, "frozen B77..84 context changed")
    need(old["start_extra"]["600"] == old["start_extra"]["601"] == [45],
         "capture entrance differs")
    need(all(600 not in core.touched(g) and 601 not in core.touched(g)
             for g in old["A"] + old["B"][:77]), "capture pullbacks are not original dirt")
    need(min(w[0] for w in old["warps"]) > 84, "operator enters the changed local block")
    need(600 not in map(int, old["helper_final"]) and 601 not in map(int, old["helper_final"]),
         "capture pair would require a private-buffer remap")
    need(core.same_cleanup(old["cleanup"], core.derive_cleanup(old)), "frozen cleanup is stale")
    literal = copy.deepcopy(old)
    literal["B"][77:85] = copy.deepcopy(NEW_BLOCK)
    literal["cleanup"] = core.derive_cleanup(literal)
    locations = [i for i in range(len(literal["cleanup"]) - 1)
                 if literal["cleanup"][i:i + 2] == INVERSE_PAIR
                 and literal["cleanup"][:i] + literal["cleanup"][i + 2:] == old["cleanup"]]
    need(len(locations) == 1, "literal inverse pair has no unique cancellation witness")
    i = locations[0]
    canceled = copy.deepcopy(literal)
    canceled["cleanup"] = literal["cleanup"][:i] + literal["cleanup"][i + 2:]
    need(canceled["cleanup"] == old["cleanup"], "explicit cancellation differs from predecessor")
    need(all(literal[k] == old[k] for k in old if k not in ("B", "cleanup")),
         "unexpected word-field edit")
    return literal, canceled, i


def algebra_checks(core, old, literal, canceled):
    results = {}
    for dual in (False, True):
        orientation = "inverse_transpose" if dual else "forward"
        expected = core.forward_rows(old, dual=dual, symbolic_buffers=True)
        exact_contract(core, old, expected, dual)
        for label, word in (("literal", literal), ("canceled", canceled)):
            got = core.forward_rows(word, dual=dual, symbolic_buffers=True)
            need(got == expected, orientation + " all-column equality failed: " + label)
            exact_contract(core, word, got, dual)
        results[orientation] = {"independent_coordinates": 723,
                                "nonzero_coefficients": sum(map(len, expected.values())),
                                "all_rows_equal": True, "full_contract": True,
                                "matrix_sha256": row_digest(expected)}
    # A separately traversed reverse pullback checks every input column, including
    # private buffers, against the forward traversal.
    for label, word in (("predecessor", old), ("literal", literal), ("canceled", canceled)):
        cols = core.reverse_columns(word)
        need(len(cols) == 723, "reverse pullback has missing input columns")
        need(core.transpose(cols) == core.forward_rows(word, symbolic_buffers=True),
             "reverse-column/forward-row disagreement: " + label)
    results["reverse_column_traversal"] = {"input_columns": 723,
                                            "all_three_words_match_forward": True}
    boundary = {}
    for label, word in (("predecessor", old), ("literal", literal), ("canceled", canceled)):
        def save(rows):
            boundary[label] = copy.deepcopy(rows)
        core.forward_rows(word, symbolic_buffers=True, snapshot=save)
        need(core.boundary_defects(word, boundary[label]) == [], "cleanup-boundary defect: " + label)
    need(boundary["literal"] == boundary["canceled"] == boundary["predecessor"],
         "cleanup-boundary equality failed")
    results["cleanup_boundary"] = {"all_723_rows_equal": True,
                                    "target_and_restored_helper_contract": True}
    return results


def controls(core, old, literal, canceled, pair_index):
    expected = core.forward_rows(old, symbolic_buffers=True)
    results = {}

    def reject_map(label, mutant):
        need(mutant != literal, "no-op control: " + label)
        actual = core.forward_rows(mutant, symbolic_buffers=True)
        witness = first_difference(expected, actual)
        need(witness is not None, "map control unexpectedly passed: " + label)
        results[label] = {"rejected_by": "full arbitrary-dirty forward map", "witness": witness}

    missing = copy.deepcopy(literal)
    missing["B"].pop(84)  # Delete the actual -601 undo, preserving later warp cuts.
    for record in missing["warps"]:
        if record[0] > 84:
            record[0] -= 1
    missing["cleanup"] = core.derive_cleanup(missing)
    reject_map("missing_capture_undo", missing)

    wrong_sign = copy.deepcopy(literal)
    wrong_sign["B"][81][3] = -1
    wrong_sign["B"][84][3] = 1
    wrong_sign["cleanup"] = core.derive_cleanup(wrong_sign)
    reject_map("difference_instead_of_sum", wrong_sign)

    missing_inverse = copy.deepcopy(literal)
    missing_inverse["cleanup"].pop(pair_index + 1)
    reject_map("one_literal_inverse_shear_missing", missing_inverse)

    wrong_frame = copy.deepcopy(literal)
    wrong_frame["B"][81][-1] = [51]
    need(wrong_frame != literal, "no-op frame control")
    try:
        core.frame_bill(wrong_frame)
    except core.AuditFailure as exc:
        results["wrong_capture_frame"] = {"rejected_by": "chronological binary-frame containment",
                                           "witness": str(exc)}
    else:
        raise ValueError("incomparable capture-frame control passed")

    # Frozen cleanup is semantically valid after certified adjacent cancellation.
    # It is only rejected if falsely labelled as the literal reverse-inverse list.
    need(not core.same_cleanup(canceled["cleanup"], core.derive_cleanup(canceled)),
         "literal-format control did not change the actual cleanup list")
    need(core.forward_rows(canceled, symbolic_buffers=True) == expected,
         "certified cancellation was incorrectly treated as a semantic defect")
    results["frozen_cleanup_mislabelled_literal"] = {
        "rejected_by": "literal reverse-inverse representation only",
        "semantic_map_passes": True,
        "valid_with_explicit_adjacent_cancellation_certificate": True,
    }
    return results


def verify_word(core, name):
    path = PACKAGE / "predecessor4061/frozen" / ("WORD-" + name + ".json.gz")
    old = json.loads(gzip.decompress(path.read_bytes()))
    literal, canceled, pair_index = candidate(core, old)
    for word in (old, literal, canceled):
        need(core.hygiene(word), "dyadic/access hygiene failed")
    algebra = algebra_checks(core, old, literal, canceled)
    paid = {label: paid_description(core, word) for label, word in
            (("predecessor", old), ("literal", literal), ("canceled", canceled))}
    need(paid["predecessor"] == paid["literal"] == paid["canceled"],
         "capture unexpectedly changes paid frames or ordered widths")
    need(paid["predecessor"]["profile"] == {int(k): v for k, v in old["report"]["local_profile"].items()},
         "recomputed profile differs from frozen report")
    need(paid["predecessor"]["width_inventory"] ==
         {int(k): v for k, v in old["report"]["width_inventory"].items()},
         "recomputed widths differ from frozen report")
    counts = {label: primitive_counts(core, word) for label, word in
              (("predecessor", old), ("literal", literal), ("canceled", canceled))}
    return {
        "frozen_file_sha256": file_digest(path),
        "word_json_sha256": {label: digest(word) for label, word in
                             (("predecessor", old), ("literal", literal), ("canceled", canceled))},
        "algebra": algebra,
        "cleanup": {"literal_reverse_inverse_verified": True,
                    "adjacent_pair_zero_based_index": pair_index,
                    "pair": INVERSE_PAIR,
                    "deleting_exact_pair_equals_predecessor_cleanup": True},
        "paid": paid["predecessor"],
        "profile_delta": count_delta(paid["predecessor"]["profile"], paid["canceled"]["profile"]),
        "width_delta": count_delta(paid["predecessor"]["width_inventory"],
                                   paid["canceled"]["width_inventory"]),
        "primitive_counts": counts,
        "primitive_delta": {label: count_delta(counts["predecessor"]["complete"],
                                                 counts[label]["complete"])
                            for label in ("literal", "canceled")},
        "rejection_controls": controls(core, old, literal, canceled, pair_index),
    }


def run():
    core = load_core()
    old_local, new_local = local_rows(OLD_BLOCK), local_rows(NEW_BLOCK)
    need(old_local == new_local, "independent rational local-block identity failed")
    result = {
        "schema_version": 1,
        "status": "exact_partial_capture_with_zero_recursive_profile_gain",
        "source_freeze_commit": SOURCE_FREEZE,
        "predecessor4061_head": "f977a8a3dcb2983829d066a80420b7ded42d3e09",
        "audit_core_source4076_head": "9744f9df268590295a9872b1952c695a678192b9",
        "source_sha256": SOURCE_PINS,
        "verifier_sha256": file_digest(Path(__file__).resolve()),
        "edit": {"field": "B", "zero_based_half_open_slice": [77, 85],
                 "old": OLD_BLOCK, "new": NEW_BLOCK,
                 "all_other_forward_fields_unchanged": True,
                 "warp_positions_unchanged": True},
        "local_identity": {str(r): {str(s): str(q) for s, q in sorted(row.items())}
                           for r, row in sorted(old_local.items())},
        "domain": {"live_dirty_inputs": 632, "private_buffer_inputs": 91,
                   "independent_coordinates": 723, "independent_native_operator_symbols": 72,
                   "coefficient_ring": "dyadic rationals over the free group algebra",
                   "phase_claim": False, "formal_kernel_claim": False},
        "words": {name: verify_word(core, name) for name in ("base", "extra")},
        "conclusion": {"complete_paid_rank_moment_delta": "0 for every exponent p",
                       "ordered_helper_width_change": False,
                       "literal_scalar_add_delta": 2,
                       "canceled_scalar_add_delta": 0,
                       "new_kappa_claim": False,
                       "stop_rule": "This concrete partial capture removes no recursive child charge or helper width."},
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="write a fresh deterministic JSON result to this path")
    args = parser.parse_args()
    # Normalize JSON object keys before comparing the checked-in certificate.
    result = json.loads(json.dumps(run()))
    if args.output is not None:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        committed = json.loads((HERE / "RESULT.json").read_text())
        need(result == committed, "fresh result differs from committed RESULT.json")
    print("PASS_PARTIAL_HELPER_CAPTURE", digest(result),
          "python=" + sys.version.split()[0], "optimize=" + str(sys.flags.optimize))


if __name__ == "__main__":
    main()
