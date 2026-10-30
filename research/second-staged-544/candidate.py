"""Exact second-entry-544 trial on the two frozen PR4076 words.

The output is a scoped frame rejection, not an admitted supplier.  The one
late-cut rewrite is emitted to separate exact dirty algebra from frame legality.
Prepared with OpenAI GPT-6.1 Sol assistance; Apache-2.0.  See CONSTRUCTION.md
and source4076/NOTICE.md for predecessor credit and exact source boundaries.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
import types
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_COMMIT = "9744f9df268590295a9872b1952c695a678192b9"
SOURCE_MANIFEST_SHA256 = "a53a27d6d9f1e2b2fd5612f77f752dd007293a8d4cb6342c6e7a590dffe07aa1"
OLD_ENTRANCE = (414, 51)
RAISED_ENTRANCE = (392, 37, 22)
RELEASES = ((683, 672, Q(1, 2)), (684, 676, Q(-1, 2)))
LATE_CUT = 1752  # Immediately before this B gate in the frozen source word.
RECOVERY = {544: Q(1), 379: Q(-1), 236: Q(2), 395: Q(1), 283: Q(-1, 2)}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def imported(name, path):
    """Execute authenticated source bytes, independent of any __pycache__."""
    raw = path.read_bytes()
    manifest_raw = (ROOT / "SOURCE-EXPORT.json").read_bytes()
    need(hashlib.sha256(manifest_raw).hexdigest() == SOURCE_MANIFEST_SHA256,
         "source manifest digest")
    manifest = json.loads(manifest_raw)
    entry = next(item for item in manifest["files"]
                 if item["export"] == path.relative_to(ROOT).as_posix())
    need(entry["commit"] == SOURCE_COMMIT
         and len(raw) == entry["bytes"]
         and hashlib.sha256(raw).hexdigest() == entry["sha256"],
         "interpreter source bytes")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(raw, str(path), "exec"), module.__dict__)
    return module


C = imported("second544_audit_core", ROOT / "source4076/vendor/audit_core.py")
V = imported("second544_audit_verify", ROOT / "source4076/vendor/audit_verify.py")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def authenticate():
    manifest_raw = (ROOT / "SOURCE-EXPORT.json").read_bytes()
    need(hashlib.sha256(manifest_raw).hexdigest() == SOURCE_MANIFEST_SHA256,
         "source manifest digest")
    manifest = json.loads(manifest_raw)
    for item in manifest["files"]:
        need(item["commit"] == SOURCE_COMMIT, "unexpected source commit")
        raw = (ROOT / item["export"]).read_bytes()
        need(len(raw) == item["bytes"], "source size: " + item["export"])
        need(hashlib.sha256(raw).hexdigest() == item["sha256"],
             "source digest: " + item["export"])
    return SOURCE_MANIFEST_SHA256


def load(provider):
    return json.loads(gzip.decompress(
        (ROOT / f"source4076/inputs/NEW-{provider}.json.gz").read_bytes()))


def basis(mask):
    """Canonical reduced binary basis, highest pivot first."""
    pivots = {}
    for value in C.points(mask):
        x = value
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    for p in sorted(pivots):
        for q in sorted(pivots, reverse=True):
            if q > p and (pivots[q] >> p) & 1:
                pivots[q] ^= pivots[p]
    return [pivots[p] for p in sorted(pivots, reverse=True)]


def join(a, b):
    return C.span(basis(a) + basis(b))


def qdict(values):
    return {str(r): str(q) for r, q in sorted(values.items()) if q}


def source_contract(w):
    need(C.span(w["start_extra"]["544"]) == C.span(OLD_ENTRANCE),
         "old entrance mismatch")
    need("544" not in w["helper_final"], "544 must have ordinary FULL terminal")
    for i, r, q in RELEASES:
        need(w["B"][i][:-1] == ["add", r, 544, q.numerator, q.denominator],
             "old release mismatch")
    need(w["B"][685][:-1] == ["add", 544, 379, 1, 1], "first producer")
    need(C.span(w["B"][685][-1]) == C.span(RAISED_ENTRANCE),
         "first producer frame")
    need(w["B"][686][:-1] == ["add", 544, 236, -2, 1], "second producer")
    need(not any(544 in C.touched(g) for g in w["A"]), "544 touches A")
    need([i for i, g in enumerate(w["B"]) if 544 in C.touched(g)]
         == [683, 684, 685, 686, 1240], "544 chronological contact list")
    need(not any(rec[1] in (544, 672, 676) for rec in w["warps"]),
         "a release path has a native warp")
    for r in (672, 676):
        for i in range(685, LATE_CUT):
            g = w["B"][i]
            need(not (g[0] == "add" and g[2] == r), "recipient read before cut")
            need(not (g[0] == "scale" and g[1] == r and g[2] != g[3]),
                 "recipient scaled before cut")
    # Only one 3-space containing the old 2-space lies inside the 3-space
    # carried by the unchanged first producer: it is that producer's frame.
    need(C.dim(C.span(OLD_ENTRANCE)) == 2
         and C.dim(C.span(RAISED_ENTRANCE)) == 3
         and C.span(OLD_ENTRANCE) & ~C.span(RAISED_ENTRANCE) == 0,
         "one-dimensional extension premise")


def recovery_at_cut(w):
    """Transport the identity h0 = e544*x through the prefix inverse.

    For x'_t = x_t+q*x_s a linear recovery row updates l_s -= q*l_t.
    Any touched warp is rejected, rather than silently treated as a scalar.
    544 is absent before B, so its original row needs no A/wrapper support.
    """
    row = {544: Q(1)}
    trace = []
    at = {}
    for k, rec in enumerate(w["warps"], 1):
        at.setdefault(rec[0], []).append((k, rec))
    for i in range(LATE_CUT):
        for k, rec in at.get(i, ()):
            need(not row.get(rec[1]), f"recovery sees native warp {k}")
        g = w["B"][i]
        old = dict(row)
        if g[0] == "add" and row.get(g[1]):
            new = row.get(g[2], Q(0)) - Q(g[3], g[4]) * row[g[1]]
            if new:
                row[g[2]] = new
            else:
                row.pop(g[2], None)
        elif g[0] == "scale" and row.get(g[1]):
            row[g[1]] /= Q(g[2], g[3])
        if row != old:
            trace.append({"B": i, "gate": g[:-1], "recovery": qdict(row)})
    need(row == RECOVERY, "unexpected exact late recovery")
    return trace


def late_word(w, recovery=None):
    """Move both releases to one actual cut, with all source corrections."""
    recovery = RECOVERY if recovery is None else recovery
    x = copy.deepcopy(w)
    inserted = []
    for _, r, a in RELEASES:
        for s, q in recovery.items():
            z = a * q
            inserted.append(["add", r, s, z.numerator, z.denominator, []])
    new = []
    before = {}
    removed = {i for i, _, _ in RELEASES}
    for i in range(len(w["B"]) + 1):
        before[i] = len(new)
        if i == LATE_CUT:
            new.extend(inserted)
        if i < len(w["B"]) and i not in removed:
            new.append(copy.deepcopy(w["B"][i]))
    x["B"] = new
    for rec in x["warps"]:
        rec[0] = before[rec[0]]
    x["start_extra"]["544"] = list(RAISED_ENTRANCE)
    x["cleanup"] = C.derive_cleanup(x)
    return x, inserted


def frames(w, inherited=False, observe_B=()):
    """Exact least monotone B/restore assignment, with A and endpoints fixed.

    At a scalar gate the least permissible frame is the join of its current
    input frames.  Native frame maps are updated with the unchanged G.  By
    chronological induction every permissible assignment contains this one.
    inherited=True adds each supplied scalar frame as a further lower bound.
    Terminal failures are returned, never counted as valid paid children.
    """
    x = copy.deepcopy(w)
    live = set(range(C.N)) - set(x["removed"])
    cur = {r: C.span((x["ports"][r],)) if r < C.V else C.ZERO for r in live}
    for r, U in x["start_extra"].items():
        cur[int(r)] = C.span(U)
    for g in x["A"]:
        if g[0] == "warp":
            need(cur[g[1]] == C.span(g[3]), "fixed A warp entry")
            cur[g[1]] = C.span(g[4])
        else:
            F = C.span(g[-1])
            for r in C.touched(g):
                need(cur[r] & ~F == 0, "fixed A frame failure")
                cur[r] = F
    # Centre descents use private copies; the live centre keeps its A frame.
    at = {}
    for k, rec in enumerate(x["warps"], 1):
        at.setdefault(rec[0], []).append((k, rec))
    changes = []
    last = {}
    observations = {}

    def scalar(sec, i, g):
        F = C.ZERO
        for r in C.touched(g):
            F = join(F, cur[r])
        if inherited:
            F = join(F, C.span(g[-1]))
        old = C.span(g[-1])
        if old != F:
            changes.append({"section": sec, "index": i, "registers": list(C.touched(g)),
                            "old_dimension": C.dim(old), "new_frame": basis(F)})
        g[-1] = basis(F)
        for r in C.touched(g):
            cur[r] = F
            last[r] = [sec, i]

    for i in range(len(x["B"]) + 1):
        for k, rec in at.get(i, ()):
            _, r, G, _, _ = rec
            rec[3] = basis(cur[r])
            cur[r] = C.image_mask(C.warp_images(G), cur[r])
            rec[4] = basis(cur[r])
            last[r] = ["warp", k]
        if i in observe_B:
            observations[str(i)] = {str(r): basis(cur[r])
                                     for r in sorted(set(RECOVERY) | {672, 676})}
        if i < len(x["B"]):
            scalar("B", i, x["B"][i])
    for i, g in enumerate(x["restore"]):
        scalar("restore", i, g)
    end = {r: C.hyperplane(x["ports"][r-C.V]) if C.is_target(r) else C.FULL
           for r in live}
    for r, U in x["helper_final"].items():
        end[int(r)] = C.span(U)
    violations = []
    for r in sorted(live):
        if cur[r] & ~end[r]:
            violations.append({"register": r, "current_frame": basis(cur[r]),
                               "terminal_frame": basis(end[r]), "last_contact": last.get(r),
                               "forbidden_vector": min(C.points(cur[r] & ~end[r]))})
    x["cleanup"] = C.derive_cleanup(x)
    try:
        bill, widths, *_ = C.frame_bill(x)
        need(not violations, "frame bill missed a terminal violation")
        status = "PASS"
    except C.AuditFailure as exc:
        need(violations, "unexpected nonterminal frame error: " + str(exc))
        bill = widths = None
        status = str(exc)
    return x, {"valid_frame_bill": not violations, "first_rejection": status,
               "warp_frame_policy": "Same G and lender; entry/exit frames relaxed to current/image. This is a favorable necessary closure, not fixed native-boundary admission.",
               "local_profile": bill, "width_inventory": widths,
               "changed_scalar_frames": len(changes), "terminal_violations": violations,
               "changes": changes, "observed_B_entry_frames": observations}


def original_frames_at(w, cut):
    """Exact original source/current-reader frames at one frozen B boundary."""
    _, _, _, start, _ = C.frame_bill(w)
    cur = dict(start)
    for g in w["A"]:
        if g[0] == "warp":
            cur[g[1]] = C.span(g[4])
        else:
            for r in C.touched(g):
                cur[r] = C.span(g[-1])
    at = {}
    for rec in w["warps"]:
        at.setdefault(rec[0], []).append(rec)
    for i in range(cut + 1):
        for rec in at.get(i, ()):
            cur[rec[1]] = C.span(rec[4])
        if i < cut:
            for r in C.touched(w["B"][i]):
                cur[r] = C.span(w["B"][i][-1])
    return {str(r): {"frame": basis(cur[r]), "dimension": C.dim(cur[r]),
                     "terminal": (basis(C.span(w["helper_final"][str(r)]))
                                  if str(r) in w["helper_final"] else basis(C.FULL))}
            for r in sorted(set(RECOVERY) | {672, 676})}


def path_witness(w, late=False):
    if late:
        # The new ten-gate block is immediately before old B1752.  Its first
        # add reads 544 into 672.  There is no warp before old B1754.
        gate = w["B"][1754]
        need(gate[:3] == ["add", 181, 672], "late target path")
        target, source_path = 181, [544, 672, 181]
        indices = ["late release before old B1752", "old B1754"]
    else:
        for i, pair in ((683, (672, 544)), (1116, (672, 462)), (1738, (116, 462))):
            need(tuple(w["B"][i][1:3]) == pair, "same-slot witness path")
        target, source_path = 116, [544, 672, 462, 116]
        indices = [683, 1116, 1738]
    port = w["ports"][target-C.V]
    vector = 22
    need(C.span(RAISED_ENTRANCE) >> vector & 1, "witness not in raised entrance")
    need((port & vector).bit_count() % 2 == 1, "witness is terminal-admissible")
    need(not any(rec[1] in source_path for rec in w["warps"]), "path crosses a warp")
    return {"direction": vector, "register_path": source_path, "gate_indices": indices,
            "target": target, "port": port, "binary_dot": 1,
            "no_native_warps_on_path": True}


def rejected_semantics(w):
    try:
        V.semantics(C, w)
    except (ValueError, C.AuditFailure) as exc:
        return str(exc)
    raise ValueError("dirty-algebra control was accepted")


def prefix_map_at(w, boundary):
    partial = copy.deepcopy(w)
    need(not any(rec[0] == boundary for rec in partial["warps"]),
         "chosen boundary coincides with a native warp")
    partial["B"] = partial["B"][:boundary]
    partial["restore"] = []
    partial["cleanup"] = []
    return C.forward_rows(partial, symbolic_buffers=True)


def row_map_digest(rows):
    return digest([[r, [[var, list(word), str(q)]
                         for (var, word), q in sorted(rows[r].items())]]
                   for r in sorted(rows)])


def inserted_inverse(x, insertions):
    restored = set(map(int, x["helper_final"]))
    private = lambda r: r + C.N if r in restored else r
    block = [["add", private(g[1]), private(g[2]), -g[3], g[4], basis(C.FULL)]
             for g in reversed(insertions)]
    indices = [i for i in range(len(x["cleanup"]) - len(block) + 1)
               if x["cleanup"][i:i+len(block)] == block]
    need(len(indices) == 1, "inserted literal inverse block")
    return {"first_cleanup_index": indices[0], "gates": block,
            "restored_sources_use_private_buffers": {str(r): private(r)
                                                      for r in RECOVERY if r in restored}}


def run_provider(provider, emit_dir=None):
    w = load(provider)
    source_contract(w)
    baseline_bill, baseline_widths, *_ = C.frame_bill(w)
    C.hygiene(w)
    need(C.same_cleanup(w["cleanup"], C.derive_cleanup(w)), "source inverse cleanup")
    baseline_semantics = V.semantics(C, w)
    trace = recovery_at_cut(w)

    raised = copy.deepcopy(w)
    raised["start_extra"]["544"] = list(RAISED_ENTRANCE)
    same, same_result = frames(raised)
    _, extension_result = frames(raised, inherited=True)
    need(not same_result["valid_frame_bill"], "same-slot trial unexpectedly feasible")
    need([v["register"] for v in same_result["terminal_violations"]] == [116, 117, 180, 181],
         "same-slot covered endpoint set")
    # This is the exact same scalar program and literal inverse as its source.
    same_semantics = V.semantics(C, same)

    late, insertions = late_word(w)
    block_start = LATE_CUT - len(RELEASES)
    late, late_result = frames(late, observe_B=range(block_start, block_start + len(insertions)))
    C.hygiene(late)
    late_semantics = V.semantics(C, late)
    need(not late_result["valid_frame_bill"], "late trial unexpectedly feasible")
    old_prefix = prefix_map_at(w, LATE_CUT)
    new_prefix = prefix_map_at(late, block_start + len(insertions))
    need(new_prefix == old_prefix, "compensated prefix differs at actual late cut")

    # A real missing-source control: using the immediate post-producer formula
    # at the late cut omits source395 and source283/2 and must fail dirty algebra.
    wrong, _ = late_word(w, {544: Q(1), 379: Q(-1), 236: Q(2)})
    wrong["cleanup"] = C.derive_cleanup(wrong)
    wrong_failure = rejected_semantics(wrong)

    # Every source correction in the actual ten-gate release is independently
    # indispensable on this dirty-input domain, even if the clean answer agrees.
    omitted = []
    for source in RECOVERY:
        deficient = {r: q for r, q in RECOVERY.items() if r != source}
        mutant, _ = late_word(w, deficient)
        omitted.append({"source": source, "rejection": rejected_semantics(mutant)})

    # Reverting the raise is a genuine feasible-frame control for the same
    # chronology and A/terminal contract, not a circular profile comparison.
    _, old_minimum = frames(w)
    need(old_minimum["valid_frame_bill"], "unraised minimum control failed")
    artifacts = {}
    if emit_dir is not None:
        emit_dir.mkdir(parents=True, exist_ok=True)
    for label, word in (("same-slot", same), ("late-compensated", late)):
        raw = gzip.compress(canonical(word), mtime=0)
        name = f"{label}-{provider}.json.gz"
        if emit_dir is not None:
            (emit_dir / name).write_bytes(raw)
        # Generated gzip headers/deflate bytes can vary by Python/zlib/platform.
        # Proof-relevant replay binds the canonical word, not that container.
        artifacts[label] = {"file": name, "canonical_word_sha256": digest(word)}
    for result in (same_result, extension_result, late_result, old_minimum):
        # The full exact trace remains reproducible from this program; retain
        # compact local summaries and the complete failed endpoint list.
        result.pop("changes")
    return {"source_word_sha256": digest(w), "baseline_profile": baseline_bill,
            "baseline_width_inventory": baseline_widths, "baseline_semantics": baseline_semantics,
            "same_slots": {"least_frames": same_result, "inherited_frame_extension": extension_result,
                           "semantics": same_semantics, "witness": path_witness(w)},
            "late_cut": {"old_B_position": LATE_CUT, "recovery": qdict(RECOVERY),
                         "recovery_trace": trace, "insertions_without_frames": [g[:-1] for g in insertions],
                         "insertions_with_least_frames": late["B"][block_start:block_start+len(insertions)],
                         "inserted_literal_inverse": inserted_inverse(late, insertions),
                         "original_source_frames_at_cut": original_frames_at(w, LATE_CUT),
                         "old_to_new_B_index": {"old_i_lt_683": "i", "old_683_684": "deleted",
                                                "old_685_le_i_lt_1752": "i-2", "old_i_ge_1752": "i+8",
                                                "inserted_new_indices": list(range(block_start, block_start+len(insertions)))},
                         "chronology": "Cut before old B1752; old B1752 is a commuting recipient write. Latest common boundary before a recipient read is old B1753, one gate later; the same recovery row and target181 witness hold there.",
                         "deleted_scalar_gates": 2, "inserted_scalar_gates": 10,
                         "inverse_cleanup_add_count_delta": len(late["cleanup"]) - len(w["cleanup"]),
                         "prefix_identity_at_cut": {"all_symbolic_rows_equal": True,
                                                    "rows": len(old_prefix),
                                                    "canonical_map_sha256": row_map_digest(old_prefix)},
                         "semantics": late_semantics, "least_frames": late_result,
                         "witness": path_witness(w, late=True)},
            "controls": {"unraised_least_frames": old_minimum,
                         "stale_post_producer_recovery_rejected": wrong_failure,
                         "each_recovery_source_omission_rejected": omitted},
            "diagnostic_words": artifacts,
            "admission": {"paid_profile": "UNDEFINED: fixed target terminal frames are violated",
                          "nominal_544_width_change": "7->6 is not admitted",
                          "native": "NOT RUN: frame contract already fails",
                          "owner_fill": "NOT RUN", "outer_transfer": "NOT ESTABLISHED"}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    result_mode = parser.add_mutually_exclusive_group()
    result_mode.add_argument("--output", type=Path)
    result_mode.add_argument("--check", type=Path, help="Read-only comparison against a frozen result JSON")
    parser.add_argument("--emit-dir", type=Path,
                        help="External owned scratch directory for rejected diagnostic words")
    args = parser.parse_args()
    # Verification consumes an existing fixed certificate.  Missing evidence
    # is an error; generation is available only through explicit --output.
    frozen = None if args.output else json.loads(
        (args.check if args.check is not None else ROOT / "candidate-result.json").read_text())
    source_manifest_sha256 = authenticate()
    result = {"status": "EXACT_SCOPED_FRAME_REJECTION", "source_commit": SOURCE_COMMIT,
              "source_manifest_sha256": source_manifest_sha256,
              "scope": "Two frozen PR4076 words; same-slot raise and one fully compensated late cut; no search",
              "proof_level": "Written monotone-frame witness plus exact finite arbitrary-dirty replay",
              "providers": {provider: run_provider(provider, args.emit_dir)
                            for provider in ("base", "extra")}}
    # JSON objects have string keys. Normalize before comparing a fresh result
    # with its frozen representation (histograms originate with integer keys).
    result = json.loads(canonical(result))
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if not args.output:
        need(frozen == result, "frozen candidate result differs")
    print(json.dumps({"status": result["status"],
                      "providers": {p: {"same_slot_bad_targets": [v["register"] for v in r["same_slots"]["least_frames"]["terminal_violations"]],
                                        "late_violating_registers": [v["register"] for v in r["late_cut"]["least_frames"]["terminal_violations"]],
                                        "dirty_algebra": r["late_cut"]["semantics"]["forward"]}
                                    for p, r in result["providers"].items()}}, sort_keys=True))


if __name__ == "__main__":
    main()
