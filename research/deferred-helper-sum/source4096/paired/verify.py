#!/usr/bin/env python3
"""Exact paired-boundary obstruction for the pinned PR4076 helper pair.

Standard library only; no source interpreter is imported.  The BORROW-WORD
interpretation was read from the pinned PR4076 export's audit_core.py (Sagar
Thakrar, Apache-2.0).  This is a new finite free-operator coefficient check,
not an independent human review, native-phase check or supplier admission.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

V, N = 112, 704
H = (608, 609)
R = (608, 609, 417, 419, 421, 610)
SOURCE_HEAD = "9744f9df268590295a9872b1952c695a678192b9"
SOURCE_FILES = {
    "PROOF.md": (6458, "9ebc183172a290f8b7f1527df9d56c3123f80e1a21485bf44c4cc5ecd56108cc", "5965718abd3157ae497b624dfd12cf599e54b636"),
    "NOTICE.md": (2940, "91f7f723bb616aca757812f940f6b893559e64e441d6158c907155a79b3b15a7", "9ccffcfb7da1e36b158752ffed293dc95797e68e"),
    "inputs/NEW-base.json.gz": (74530, "8159c67d29ab58efe546ebc4ce20872421996cc71b5f17737ff8b36cbc76d148", "dcc0374b5c822d544a4ecf19d00635c7117d82c9"),
    "inputs/NEW-extra.json.gz": (74528, "0147e6b30ef328e227e89113323eb0d02d116e125b0e7c99a00ea4f2652dcc80", "990c54caeeb4fb344de622de98d97e107ec67ed5"),
    "inputs/OLD-base.json.gz": (74428, "08e6c96fbe3dfec96cb8451b3867ef8c1a214109ecd1e5af7fcc28e0f05728d0", "806784bf99d9d15004d2d227d06268556a0726c8"),
    "inputs/OLD-extra.json.gz": (74425, "d83c2ec9cecc0ad092d34ea4080b28a4fd7199579356b6d5a8fc6cd53ff93299", "c531be7383ad3ba941600c7ced14e5e10d6d1c67"),
    "recipe/ENTRIES.json": (788, "00071bc2e54bf5fd05a6aac9292a3861087e72898d86d1f6f7bbda65b07cfbda", "f67031d3e12f7ca91075ba2b2fdeeb99a3de5873"),
    "vendor/audit_core.py": (19364, "888679ca8502cdcb100420fe5382a052529a494bf76cb332928b86e62612b951", "8b5e1d5f2a106402f036b63028ecef31a4e4c462"),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def target(r):
    return V <= r < 2 * V


def left(op, word):
    return word[1:] if word and word[0] == -op else (op,) + word


def right(word, op):
    return word[:-1] if word and word[-1] == -op else word + (op,)


def axpy(dst, src, coefficient):
    for key, value in tuple(src.items()):
        result = dst.get(key, Q(0)) + coefficient * value
        if result:
            dst[key] = result
        else:
            dst.pop(key, None)


def authenticate(source):
    for path, (size, digest, git_blob) in SOURCE_FILES.items():
        raw = (source / path).read_bytes()
        need(len(raw) == size, "source byte length: " + path)
        need(hashlib.sha256(raw).hexdigest() == digest, "source SHA256: " + path)
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == git_blob, "source Git blob: " + path)
    return {path: {"bytes": size, "sha256": digest, "git_blob": blob}
            for path, (size, digest, blob) in SOURCE_FILES.items()}


def load(source, kind, provider):
    return json.loads(gzip.decompress((source / "inputs" / f"{kind}-{provider}.json.gz").read_bytes()))


def events(w):
    """Same literal chronological event convention as source audit_core.program.

    No cleanup is included: M is the complete non-target forward operator at
    the cleanup boundary.  Target shears are retained for their separate check.
    """
    seq = []
    for i, c in enumerate(w["initial_corrections"]):
        need(target(c["target"]), "correction writes a non-target")
        seq.append((["corr", c["target"], c["source"],
                     tuple(c["operator_word"]), Q(c["coefficient"])], ["initial_corrections", i]))
    for name in ("precondition", "compensation", "A", "cut"):
        seq.extend((deepcopy(g), [name, i]) for i, g in enumerate(w[name]))
    at = {}
    for k, warp in enumerate(w["warps"], 1):
        at.setdefault(warp[0], []).append((["warp", warp[1], k], ["warps", k]))
    for pos in range(len(w["B"]) + 1):
        seq.extend(at.get(pos, ()))
        if pos < len(w["B"]):
            seq.append((deepcopy(w["B"][pos]), ["B", pos]))
    seq.extend((deepcopy(g), ["restore", i]) for i, g in enumerate(w["restore"]))
    return seq


def non_target(seq):
    return [(g, where) for g, where in seq if g[0] != "corr" and not target(g[1])]


def operator(g):
    """Remove frame annotations; exact optimized scalar frames may change."""
    return g[:{"add": 5, "scale": 4, "warp": 3, "corr": 5}[g[0]]]


def columns(seq, include_targets=False):
    rows = {r: {} for r in range(N)}
    for h in H:
        rows[h][h, ()] = Q(1)
    for g, _ in seq:
        kind = g[0]
        if kind == "add" and (include_targets or not target(g[1])):
            need(g[1] != g[2], "self add")
            axpy(rows[g[1]], rows[g[2]], Q(g[3], g[4]))
        elif kind == "scale":
            q = Q(g[2], g[3])
            rows[g[1]] = {key: q * value for key, value in rows[g[1]].items()}
        elif kind == "warp":
            rows[g[1]] = {(r, left(g[2], word)): value
                          for (r, word), value in rows[g[1]].items()}
        elif kind == "corr" and include_targets:
            _, t, s, ops, q = g
            moved = {}
            for (r, word), value in rows[s].items():
                for op in reversed(ops):
                    word = left(op, word)
                axpy(moved, {(r, word): value}, q)
            axpy(rows[t], moved, Q(1))
    return {r: row for r, row in rows.items() if row}


def inverse_row(seq, h):
    """e_h^T M^-1: multiply on the right by inverse gates chronologically."""
    row = {(h, ()): Q(1)}
    for g, _ in non_target(seq):
        if g[0] == "add":
            t, s, q = g[1], g[2], Q(g[3], g[4])
            axpy(row, {(s, word): value for (r, word), value in tuple(row.items()) if r == t}, -q)
        elif g[0] == "scale":
            q = Q(g[2], g[3])
            row = {(r, word): value / q if r == g[1] else value
                   for (r, word), value in row.items()}
        else:
            need(g[0] == "warp", "unknown non-target opcode")
            row = {(r, right(word, -g[2])) if r == g[1] else (r, word): value
                   for (r, word), value in row.items()}
    return row


def pullback(seq, reader):
    """alpha M, a reverse-order independent check of each claimed inverse row."""
    row = deepcopy(reader)
    for g, _ in reversed(non_target(seq)):
        if g[0] == "add":
            t, s, q = g[1], g[2], Q(g[3], g[4])
            axpy(row, {(s, word): value for (r, word), value in tuple(row.items()) if r == t}, q)
        elif g[0] == "scale":
            q = Q(g[2], g[3])
            row = {(r, word): value * q if r == g[1] else value
                   for (r, word), value in row.items()}
        else:
            row = {(r, right(word, g[2])) if r == g[1] else (r, word): value
                   for (r, word), value in row.items()}
    return row


def scalar_row(values):
    return {(r, ()): Q(q) for r, q in values.items()}


EXPECTED_COLUMNS = {
    417: scalar_row({608: "1/2", 609: "1/2"}),
    419: scalar_row({609: "-1/2"}),
    421: scalar_row({608: "-1/2"}),
    608: scalar_row({608: "1"}),
    609: scalar_row({609: "1"}),
    610: scalar_row({608: "-1", 609: "-1"}),
}
EXPECTED_INVERSE = {
    608: scalar_row({342: "2", 356: "2", 410: "1/2", 417: "-1", 419: "-1", 421: "-1",
                     608: "1/2", 609: "-1/2", 610: "-1/2", 612: "-1"}),
    609: scalar_row({276: "-1", 292: "-1", 410: "1/2", 417: "1", 419: "-1", 421: "1",
                     608: "1/2", 609: "1/2", 610: "1/2", 612: "-1"}),
}


def serial(row):
    return [{"coordinate": r, "operator_word": list(word), "coefficient": str(value)}
            for (r, word), value in sorted(row.items())]


def rejects(function, message):
    try:
        function()
    except ValueError:
        return message
    raise ValueError("control accepted: " + message)


def run(source):
    source_files = authenticate(source)
    entries = json.loads((source / "recipe" / "ENTRIES.json").read_bytes())
    need([(e["helper"], e["cut"], e["source_word"]) for e in entries[:2]] ==
         [(608, 10535, "PR3945 NEW"), (609, 10535, "after 608")], "sequential staging records differ")
    providers = {}
    for provider in ("base", "extra"):
        w, old = load(source, "NEW", provider), load(source, "OLD", provider)
        seq, oldseq = events(w), events(old)
        live = set(range(N)) - set(w["removed"])
        need(len(live) == 632 and set(H) <= live and len(w["helper_final"]) == 91,
             "live-input geometry differs")
        for g, _ in seq:
            if g[0] == "corr":
                touched = g[1:3]
            elif g[0] == "add":
                touched = g[1:3]
                need(g[1] != g[2] and Q(g[3], g[4]), "noninvertible scalar add")
            elif g[0] == "scale":
                touched = g[1:2]
                need(Q(g[2], g[3]), "zero scale")
            else:
                need(g[0] == "warp" and 0 < abs(g[2]) <= len(w["warps"]), "invalid warp")
                touched = g[1:2]
            need(set(touched) <= live, "forward event touches a non-live coordinate")
        need(all(not target(g[2]) for g, _ in non_target(seq) if g[0] == "add"),
             "non-target reads a target")
        need(all(h not in map(int, w["helper_final"]) for h in H), "pair is already restored")
        need(all(w["start_extra"][str(h)] == [97, 45] for h in H), "pair entrances differ")
        # Source OLD cut10535 maps through exactly twelve removed target reads.
        # No inserted release precedes that cut.  This proves the physical cut
        # correspondence rather than treating a changing index as a fixed event.
        oldcut, newcut = 10535, 10523
        removed = [(i, g) for i, (g, _) in enumerate(oldseq[:oldcut])
                   if g[0] == "add" and g[2] in (600, 608, 609)]
        need(len(removed) == 12 and all(target(g[1]) for _, g in removed), "cut deletion support")
        filtered = [operator(g) for i, (g, _) in enumerate(oldseq[:oldcut]) if i not in {i for i, _ in removed}]
        need(filtered == [operator(g) for g, _ in seq[:newcut]], "source-to-actual cut correspondence")
        # The609 record is explicitly sourced AFTER the608 edit.  Before its
        # cut, that edit has deleted four early reads and has not inserted any
        # release.  Thus intermediate10535 is OLD10539, then NEW10527.
        need(all(r["position"] > 10539 for r in entries[0]["releases"]),
             "an earlier608 release changes sequential cut indexing")
        oldcut609, newcut609 = 10539, 10527
        before609 = [operator(g) for g, _ in oldseq[:oldcut609]
                     if not (g[0] == "add" and g[2] == 608)]
        need(len(before609) == entries[1]["cut"], "after608 cut length differs")
        all_deleted609 = [operator(g) for g, _ in oldseq[:oldcut609]
                          if not (g[0] == "add" and g[2] in (600, 608, 609))]
        need(all_deleted609 == [operator(g) for g, _ in seq[:newcut609]],
             "sequential609 source-to-actual cut correspondence")
        accesses = [(i, g, where) for i, (g, where) in enumerate(seq)
                    if g[0] != "corr" and any(h in g[1:3] for h in H)]
        need(accesses[0][0] == 10609 and accesses[0][1][:3] == ["add", 121, 609],
             "first actual pair access differs")
        need(all(not any(h in g[1:3] for h in H) for g, _ in seq[:10609] if g[0] != "corr"),
             "pair is not idle at the proposed cut")
        need(all(c["source"] not in H for c in w["initial_corrections"]),
             "operator correction reads the pair")
        need(all(g[2] not in H for key in ("precondition", "compensation") for g in w[key]),
             "wrapper target compensation reads pair")
        result_columns = columns(seq)
        need(result_columns == EXPECTED_COLUMNS, "complete forward columns differ")
        result_inverse = {h: inverse_row(seq, h) for h in H}
        need(result_inverse == EXPECTED_INVERSE, "complete inverse rows differ")
        for cut in (newcut, newcut609, 10535):
            need(columns(seq[cut:]) == result_columns, "suffix columns differ")
            need({h: inverse_row(seq[cut:], h) for h in H} == result_inverse, "suffix inverse rows differ")
            for h in H:
                need(pullback(seq[cut:], result_inverse[h]) == {(h, ()): Q(1)},
                     "suffix inverse-row full-input pullback differs")
            need(not any(target(r) for r in columns(seq[cut:], True)), "suffix target dirt leak")
        need(not any(target(r) for r in columns(seq, True)), "complete target dirt leak")
        for h in H:
            need(pullback(seq, result_inverse[h]) == {(h, ()): Q(1)}, "inverse-row pullback differs")
        # Pair-only outward map has an invertible 2x2 scalar minor.
        minor = [[result_columns[r].get((h, ()), Q(0)) for h in H] for r in (421, 419)]
        determinant = minor[0][0] * minor[1][1] - minor[0][1] * minor[1][0]
        need(determinant == Q(1, 4), "pair-only obstruction minor differs")
        # For alpha M=a e608^T+b e609^T, inverse-row coefficients outside R
        # at342 and276 form a unit minor.  Therefore alpha supported on R
        # forces a=b=0, before any normalization or paired S,T can be chosen.
        reader_minor = [[result_inverse[h].get((r, ()), Q(0)) for h in H] for r in (342, 276)]
        reader_det = reader_minor[0][0] * reader_minor[1][1] - reader_minor[0][1] * reader_minor[1][0]
        need(reader_det == -2, "receiver-cone obstruction minor differs")
        difference = {}
        for r, row in result_columns.items():
            value = row.get((608, ()), Q(0)) - row.get((609, ()), Q(0))
            if value:
                difference[r, ()] = value
        need(difference == scalar_row({608: "1", 609: "-1", 419: "1/2", 421: "-1/2"}),
             "difference direction differs")
        controls = []
        bad = deepcopy(result_columns)
        bad[421].clear()
        controls.append(rejects(lambda: need(bad == columns(seq), "missing outward column"),
                                "omitted421 leakage is rejected by complete forward coefficients"))
        badrow = deepcopy(result_inverse[608])
        badrow.pop((342, ()))
        controls.append(rejects(lambda: need(pullback(seq, badrow) == {(608, ()): Q(1)}, "false inverse row"),
                                "omitted342 inverse coefficient is rejected by full pullback"))
        projected_reader = {key: value for key, value in result_inverse[608].items() if key[0] in R}
        controls.append(rejects(lambda: need(all(r in H for r, _ in pullback(seq, projected_reader)),
                                            "receiver-only reader leaks"),
                                "projected receiver-only reader fails eligible-source support"))
        controls.append(rejects(lambda: need(all(r in H for r, _ in difference), "false restored difference"),
                                "defect-canceling difference fails the full forward cone"))
        controls.append(rejects(lambda: need(filtered == [operator(g) for g, _ in seq[:newcut + 1]], "false cut"),
                                "off-by-one mapped cut is rejected by exact prefix identity"))
        old_columns = columns(oldseq)
        delta = deepcopy(result_columns)
        for r, row in old_columns.items():
            axpy(delta.setdefault(r, {}), row, Q(-1))
        delta = {r: row for r, row in delta.items() if row}
        need(delta == {417: scalar_row({608: "1/2", 609: "1/2"}),
                       610: scalar_row({608: "-1", 609: "-1"})}, "rewrite defect differs")
        providers[provider] = {
            "prefix_event_count": len(seq), "non_target_event_count": len(non_target(seq)),
            "source_cut": oldcut, "actual_mapped_cut": newcut,
            "source_cut_event": oldseq[oldcut][1], "actual_cut_event": seq[newcut][1],
            "sequential609_source_old_cut": oldcut609, "sequential609_actual_new_cut": newcut609,
            "sequential609_actual_cut_event": seq[newcut609][1],
            "covered_new_cuts": [newcut, newcut609, 10535],
            "first_pair_access": {"event": accesses[0][0], "locator": accesses[0][2], "gate": accesses[0][1]},
            "all_pair_accesses": [{"event": i, "locator": where, "gate": g} for i, g, where in accesses],
            "pair_entrance_frame_basis": [97, 45], "pair_entrance_dimension": 2,
            "pair_inherited_terminal_dimension": 9, "pair_inherited_widths": [7, 7],
            "forward_columns_by_output": {str(r): serial(row) for r, row in result_columns.items()},
            "inverse_rows": {str(h): serial(row) for h, row in result_inverse.items()},
            "inverse_row_pullbacks": "complete identity, both rows, all input coefficients",
            "rewrite_defect_by_output": {str(r): serial(row) for r, row in delta.items()},
            "difference_direction": serial(difference),
            "pair_minor_rows": [421, 419], "pair_minor_determinant": str(determinant),
            "receiver_reader_minor_rows": [342, 276], "receiver_reader_minor_determinant": str(reader_det),
            "target_pair_columns": "zero at full forward boundary and all three declared suffix boundaries",
            "compensation_and_operator_correction_pair_access": "none",
            "private_buffers": "91 inherited arbitrary dirty inputs, outside this forward word",
            "controls": controls,
        }
    return {
        "status": "PASS_PAIRED_608_609_FIXED_RECEIVER_OBSTRUCTION_NO_NEW_KAPPA",
        "source_pr": 4076, "source_head": SOURCE_HEAD, "authenticated_source_files": source_files,
        "ring": "Z[1/2][F_72], free invertible noncommuting warp operators; scalar changes over Z[1/2] or Q",
        "input_support": list(H), "terminal_support": list(R), "providers": providers,
        "scope": "finite exact full-column and inverse-row certificate plus all-scalar algebraic obstruction; no native phases, owner allocation, all-size or kappa claim",
        "local_change": "none: both pair-only and natural existing-receiver paired extractions fail",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parent / "source4076")
    parser.add_argument("--out", "--output", dest="output", type=Path)
    args = parser.parse_args()
    result = run(args.source)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
