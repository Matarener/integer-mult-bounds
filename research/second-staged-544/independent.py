#!/usr/bin/env python3
"""Independent fixed-contact obstruction for a second entrance on helper 544.

No constructor, retained frame walker, frame optimizer or semantic interpreter
is imported.  Subspaces are explicit immutable sets of binary vectors.  The
least assignment follows a newly built chronological constraint DAG.  This is
finite exact computation plus the written DAG lemma in INDEPENDENT.md, not a
formal-kernel proof or an assertion about changed contact networks.

Prepared with substantial OpenAI GPT-6.1 Sol assistance.  Apache-2.0; credited
source words and retained audit lineage are in source4076/NOTICE.md.
"""

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_HEAD = "9744f9df268590295a9872b1952c695a678192b9"
CANONICAL_BASE = "bb4bccbf42844d2801487450727c2f63e10d1d0f"
EXPORT_DIGEST = "a53a27d6d9f1e2b2fd5612f77f752dd007293a8d4cb6342c6e7a590dffe07aa1"
E_BASIS = (414, 51)
P_BASIS = (392, 37, 22)
EXTRA = 22


def need(condition, explanation):
    if not condition:
        raise ValueError(explanation)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def span(vectors):
    result = {0}
    for vector in vectors:
        need(type(vector) is int and 0 <= vector < 512, "bad binary vector")
        if vector not in result:
            result.update(point ^ vector for point in tuple(result))
    return frozenset(result)


def join(spaces):
    return span(vector for space in spaces for vector in space)


def dim(space):
    length = len(space)
    need(length > 0 and length & (length - 1) == 0, "bad subspace cardinality")
    return length.bit_length() - 1


def basis(space):
    """Ascending greedy basis, intentionally different from the source RREF."""
    result, sofar = [], frozenset((0,))
    for vector in sorted(space):
        if vector not in sofar:
            result.append(vector)
            sofar = span(result)
    need(sofar == space, "input is not a binary subspace")
    return result


FULL = span(1 << j for j in range(9))


def orthogonal(port):
    return frozenset(x for x in range(512) if (x & port).bit_count() % 2 == 0)


def image(space, columns):
    def apply(vector):
        out = 0
        for j, column in enumerate(columns):
            if vector & (1 << j):
                out ^= column
        return out
    return frozenset(apply(x) for x in space)


def authenticate():
    raw = (HERE / "SOURCE-EXPORT.json").read_bytes()
    need(digest(raw) == EXPORT_DIGEST, "source export manifest digest")
    manifest = json.loads(raw)
    need(len(manifest["files"]) == 9, "source export file count")
    receipts = {}
    for record in manifest["files"]:
        need(record["commit"] == SOURCE_HEAD, "source head")
        relative = record["export"]
        need(relative not in receipts, "duplicate source export")
        payload = (HERE / relative).read_bytes()
        need(len(payload) == record["bytes"], "source byte length: " + relative)
        need(digest(payload) == record["sha256"], "source SHA256: " + relative)
        blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
        need(blob == record["git_blob"], "source Git blob: " + relative)
        receipts[relative] = record["sha256"]
    return receipts


def load_word(provider):
    relative = "source4076/inputs/NEW-" + provider + ".json.gz"
    word = json.loads(gzip.decompress((HERE / relative).read_bytes()))
    pins = json.loads((HERE / "source4076/INPUTS.json").read_bytes())
    need(digest(canonical(word)) == pins["canonical_sha256"]["NEW-" + provider + ".json.gz"],
         "canonical word digest")
    return word


def touched(gate):
    need(gate[0] in ("add", "scale"), "unexpected scalar opcode")
    return tuple(gate[1:3] if gate[0] == "add" else gate[1:2])


def entrance_census(word):
    old = span(word["start_extra"]["544"])
    producer = span(word["B"][685][-1])
    need(old == span(E_BASIS) and producer == span(P_BASIS), "entrance/producer source contract")
    need(dim(old) == 2 and dim(producer) == 3 and old < producer, "proper entrance extension")
    extensions = {span(tuple(old) + (vector,)) for vector in range(512) if vector not in old}
    eligible = [space for space in extensions if space <= producer]
    need(len(extensions) == 127 and eligible == [producer], "unique dimension-three entrance")
    need(EXTRA in producer and EXTRA not in old, "extra direction")
    return {"ambient_dimension": 9, "old_basis": list(E_BASIS), "old_points": sorted(old),
            "producer_basis": list(P_BASIS), "producer_points": sorted(producer),
            "dimension_three_extensions_of_old": len(extensions),
            "extensions_contained_in_first_producer": len(eligible), "extra_vector": EXTRA}


def make_graph(word, raised=False):
    """Scalar nodes require common frames; directed edges require containment.

    Exact warp entries and target/centre cuts are fixed by seeding and bounding
    the *previous contact node*, without inventing an extra paid lift.  Warp
    exits start new fixed nodes.  End nodes represent the permitted final climb.
    """
    nodes, last = [], {}

    def node(label, seed=frozenset((0,)), parents=(), upper=None):
        index = len(nodes)
        need(all(parent < index for parent in parents), "nonchronological edge")
        nodes.append({"label": tuple(label), "seed": seed, "parents": tuple(parents),
                      "upper": upper, "fixed_reasons": []})
        return index

    for register in range(704):
        if register in word["removed"]:
            continue
        initial = span((word["ports"][register],)) if register < 112 else span(())
        if str(register) in word["start_extra"]:
            initial = span(word["start_extra"][str(register)])
        if register == 544 and raised:
            initial = span(P_BASIS)
        last[register] = node(("start", register), initial, upper=initial)

    def fix_previous(register, frame, reason):
        entry = nodes[last[register]]
        if entry["upper"] is not None:
            need(entry["upper"] == frame, "inconsistent fixed boundary")
        entry["seed"] = join((entry["seed"], frame))
        entry["upper"] = frame
        entry["fixed_reasons"].append(tuple(reason))

    def scalar(gate, label):
        registers = touched(gate)
        need(all(register in last for register in registers), "dead scalar contact")
        index = node(label, parents=tuple(last[register] for register in registers))
        for register in registers:
            last[register] = index

    def native(register, entry, exit_frame, label, columns):
        need(len(columns) == 9 and image(FULL, columns) == FULL, "noninvertible native map")
        need(image(entry, columns) == exit_frame, "native frame map")
        fix_previous(register, entry, ("native-entry",) + tuple(label))
        last[register] = node(("native-exit",) + tuple(label), exit_frame, upper=exit_frame)

    for i, gate in enumerate(word["A"]):
        if gate[0] != "warp":
            scalar(gate, ("A", i))
            continue
        _, register, op, entry, exit_frame = gate
        columns = word["warps"][abs(op) - 1][2]
        if op < 0:
            inverse = {next(iter(image(frozenset((vector,)), columns))): vector for vector in range(512)}
            columns = [inverse[1 << j] for j in range(9)]
        need(i < word["prelude_events"], "native outside prelude")
        native(register, span(entry), span(exit_frame), ("A", i), columns)

    for register in range(112, 224):
        frame = span(word["target_levels"].get(str(register - 112), ()))
        fix_previous(register, frame, ("target-cut", register))
    for register, vectors in zip(word["centers"], word["center_frames"]):
        fix_previous(register, span(vectors), ("centre-cut", register))

    at = {}
    for k, record in enumerate(word["warps"]):
        at.setdefault(record[0], []).append((k, record))
    for i in range(len(word["B"]) + 1):
        for k, (_, register, columns, entry, exit_frame) in at.get(i, ()):
            native(register, span(entry), span(exit_frame), ("B", k), columns)
        if i < len(word["B"]):
            scalar(word["B"][i], ("B", i))
    for i, gate in enumerate(word["restore"]):
        scalar(gate, ("restore", i))

    for register in last:
        terminal = FULL if register < 112 or register >= 224 else orthogonal(word["ports"][register - 112])
        if str(register) in word["helper_final"]:
            terminal = span(word["helper_final"][str(register)])
        last[register] = node(("end", register), terminal, (last[register],), upper=terminal)
    return nodes


def solve_graph(nodes, ignore_upper=()):
    values, violations = [], []
    ignored = set(tuple(label) for label in ignore_upper)
    for index, node in enumerate(nodes):
        value = join((node["seed"],) + tuple(values[parent] for parent in node["parents"]))
        values.append(value)
        if node["upper"] is not None and node["label"] not in ignored and not value <= node["upper"]:
            violations.append({"node": index, "label": list(node["label"]),
                               "required_basis": basis(value), "allowed_basis": basis(node["upper"]),
                               "outside_points": sorted(value - node["upper"]),
                               "fixed_reasons": [list(reason) for reason in node["fixed_reasons"]]})
    return values, violations


def short_witness(word):
    expected = ((683, 544, 672), (1116, 672, 462), (1738, 462, 116))
    path = []
    previous = -1
    for index, source, destination in expected:
        gate = word["B"][index]
        need(gate[0] == "add" and {source, destination} == set(gate[1:3]), "short path contact")
        need(index > previous, "short path chronology")
        need(not any(previous < record[0] <= index and record[1] == source for record in word["warps"]),
             "short path crosses native warp")
        path.append({"B_index": index, "gate": gate[:-1], "from": source, "to": destination})
        previous = index
    port = word["ports"][116 - 112]
    need(port == 131 and (port & EXTRA).bit_count() % 2 == 1, "target separating character")
    need(not any(record[1] in (544, 672, 462) for record in word["warps"]), "short path warp-free registers")
    return {"extra_vector": EXTRA, "path": path, "target": 116, "target_port": port,
            "binary_pairing": 1, "native_warps_on_path_registers": 0}


def provider_result(word):
    old_nodes = make_graph(word)
    nodes = make_graph(word, raised=True)
    old_values, old_bad = solve_graph(old_nodes)
    values, bad = solve_graph(nodes)
    need(not old_bad, "baseline least constraints are infeasible")
    need([entry["label"] for entry in bad] == [["end", r] for r in (116, 117, 180, 181)],
         "affected terminal census differs")
    need(len(nodes) == len(old_nodes) == 7491, "contact node count")
    cone = []
    for index, (old, new, node) in enumerate(zip(old_values, values, nodes)):
        need(old <= new, "raising one seed decreased a least frame")
        if old != new:
            cone.append({"node": index, "label": list(node["label"]), "old_basis": basis(old),
                         "raised_basis": basis(new), "dimension_delta": dim(new) - dim(old)})
    kinds = Counter(entry["label"][0] for entry in cone)
    contacts = [entry["label"][1] for entry in cone if entry["label"][0] == "B"]
    return {"entrance_census": entrance_census(word), "short_witness": short_witness(word),
            "constraint_nodes": len(nodes), "constraint_edges": sum(len(node["parents"]) for node in nodes),
            "baseline_feasible": True, "raised_feasible": False, "violations": bad,
            "least_frame_cone": cone, "cone_counts_by_kind": dict(sorted(kinds.items())),
            "affected_B_contacts": contacts,
            "target_cut_centre_or_native_violations": 0,
            "admissible_profile_or_width_delta": None}


def local_matrix(variant="source"):
    """All coefficients on independent h,u,v,a,b; no clean-input premise."""
    rows = [[Fraction(i == j) for j in range(5)] for i in range(5)]

    def add(destination, source, coefficient):
        rows[destination] = [x + coefficient * y for x, y in zip(rows[destination], rows[source])]

    if variant != "omit_first_release" and variant != "late_uncorrected_releases":
        add(1, 0, Fraction(-1 if variant == "wrong_first_sign" else 1, 2))
    if variant != "late_uncorrected_releases":
        add(2, 0, Fraction(-1, 2))
    add(0, 3, Fraction(1))
    add(0, 4, Fraction(-2))
    if variant == "late_uncorrected_releases":
        add(1, 0, Fraction(1, 2))
        add(2, 0, Fraction(-1, 2))
    return [[str(coefficient) for coefficient in row] for row in rows]


def add_row(destination, source, coefficient):
    result = dict(destination)
    for column, value in source.items():
        total = result.get(column, 0) + coefficient * value
        if total:
            result[column] = total
        else:
            result.pop(column, None)
    return result


def forward_prefix(word, omitted=()):
    """632 independent columns, with free noncommuting native operator words.

    A term (r, (k,...)) denotes native-operator composition applied to the
    independent B-entry value in register r.  No native operator is replaced
    by a scalar or commuting sample.  Exact prefix equality in this free
    module is stronger than equality for the actual native linear maps.
    """
    rows = {r: {(r, ()): Fraction(1)} for r in range(704) if r not in word["removed"]}
    at = {}
    for k, record in enumerate(word["warps"], 1):
        at.setdefault(record[0], []).append((k, record[1]))
    for index, gate in enumerate(word["B"][:1752]):
        for k, register in at.get(index, ()):
            need(not any(origin == 544 for origin, _ in rows[register]),
                 "native acts on an h0 carrier")
            rows[register] = {(r, (k,) + letters): q for (r, letters), q in rows[register].items()}
        if index in omitted:
            continue
        if gate[0] == "add":
            _, destination, source, numerator, denominator, _ = gate
            need(destination != source, "unexpected self-add")
            rows[destination] = add_row(rows[destination], rows[source], Fraction(numerator, denominator))
        else:
            _, destination, numerator, denominator, _ = gate
            q = Fraction(numerator, denominator)
            need(q != 0, "noninvertible scalar")
            rows[destination] = {column: q * value for column, value in rows[destination].items()}
    return rows


def combine_rows(rows, coefficients):
    result = {}
    for register, coefficient in coefficients.items():
        result = add_row(result, rows[register], coefficient)
    return result


def matrix_digest(rows):
    serial = [[register, [[origin, list(letters), str(value)]
                         for (origin, letters), value in sorted(row.items())]]
              for register, row in sorted(rows.items())]
    return digest(canonical(serial))


def recovery_coefficients(word):
    coefficients = {544: Fraction(1)}
    trace, touched_native = [], []
    at = {}
    for k, record in enumerate(word["warps"], 1):
        at.setdefault(record[0], []).append((k, record[1]))
    for index, gate in enumerate(word["B"][:1752]):
        for k, register in at.get(index, ()):
            if coefficients.get(register):
                touched_native.append([index, k, register])
        if index in (683, 684):
            continue
        before = dict(coefficients)
        if gate[0] == "add":
            _, destination, source, numerator, denominator, _ = gate
            if coefficients.get(destination):
                coefficients[source] = coefficients.get(source, 0) - Fraction(numerator, denominator) * coefficients[destination]
        else:
            _, destination, numerator, denominator, _ = gate
            if coefficients.get(destination):
                coefficients[destination] /= Fraction(numerator, denominator)
        coefficients = {r: q for r, q in coefficients.items() if q}
        if coefficients != before:
            trace.append({"B_index": index, "gate": gate[:-1],
                          "recovery_coefficients": {str(r): str(q) for r, q in sorted(coefficients.items())}})
    need(not touched_native, "native map touches the scalar recovery row")
    expected = {544: Fraction(1), 379: Fraction(-1), 236: Fraction(2),
                395: Fraction(1), 283: Fraction(-1, 2)}
    need(coefficients == expected, "late recovery row differs")
    need([entry["B_index"] for entry in trace] == [685, 686, 801, 1417], "late recovery update census")
    return coefficients, trace


def recovered_prefix(rows, coefficients, wrong_sign=False):
    restored = {register: dict(row) for register, row in rows.items()}
    for destination, sign in ((672, 1), (676, -1)):
        if wrong_sign and destination == 672:
            sign = -sign
        for source, q in coefficients.items():
            restored[destination] = add_row(restored[destination], restored[source], sign * q / 2)
    return restored


def late_boundary(word):
    need(not any(544 in (gate[1:3] if gate[0] == "add" else gate[1:2]) for gate in word["A"]),
         "A touches the h0 source")
    need(not any(544 in (gate[1:3] if gate[0] == "add" else gate[1:2])
                 for section in ("precondition", "compensation", "cut") for gate in word[section]),
         "wrapper or cut touches the h0 source")
    need(not any(correction["source"] == 544 for correction in word["initial_corrections"]),
         "initial correction reads the h0 source")
    need(not any(record[0] == 1752 for record in word["warps"]), "native at late cut")
    coefficients, trace = recovery_coefficients(word)
    omitted = forward_prefix(word, omitted=(683, 684))
    original = forward_prefix(word)
    need(len(omitted) == 632, "late prefix independent column count")
    need(combine_rows(omitted, coefficients) == {(544, ()): Fraction(1)},
         "all-coefficient late recovery identity")
    restored = recovered_prefix(omitted, coefficients)
    need(restored == original, "all-coefficient late block prefix equality")
    carriers = {}
    for register, row in omitted.items():
        h_terms = {letters: q for (origin, letters), q in row.items() if origin == 544}
        if h_terms:
            need(set(h_terms) == {()}, "native map acts on an h0 carrier")
            carriers[str(register)] = str(h_terms[()])
    need(carriers == {"177": "-1/2", "208": "-1/2", "544": "1"}, "late omitted-prefix h0 carrier census")
    original_carriers = {str(r): str(row[(544, ())]) for r, row in original.items() if (544, ()) in row}
    need(original_carriers.get("672") == "1/2" and original_carriers.get("676") == "-1/2",
         "late restored donor h0 coefficients")
    need(word["B"][1754][:-1] == ["add", 181, 672, 1, 1], "late target contact")
    need(word["B"][1752][:-1] == ["add", 672, 227, 1, 1]
         and word["B"][1753][:-1] == ["add", 227, 672, -1, 2], "late adjacent contacts")
    need(word["ports"][181 - 112] == 304 and (EXTRA & 304).bit_count() % 2 == 1,
         "late target separating character")
    need(not any(1752 <= record[0] <= 1754 and record[1] == 672 for record in word["warps"]),
         "native reset before late target consumer")
    return {"cut_before_original_B_index": 1752, "omitted_original_B_indices": [683, 684],
            "recovery_coefficients": {str(r): str(q) for r, q in sorted(coefficients.items())},
            "recovery_updates": trace, "native_maps_touching_recovery_support": 0,
            "independent_B_entry_input_columns": len(omitted),
            "original_prefix_nonzero_formal_coefficients": sum(len(row) for row in original.values()),
            "omitted_prefix_nonzero_formal_coefficients": sum(len(row) for row in omitted.values()),
            "omitted_prefix_h0_column": carriers,
            "original_prefix_h0_column": original_carriers,
            "recovery_all_coefficient_identity": "h0",
            "ten_scalar_releases_restore_complete_original_prefix": True,
            "original_prefix_matrix_sha256": matrix_digest(original),
            "restored_prefix_matrix_sha256": matrix_digest(restored),
            "late_frame_witness": {"donor": 672, "required_h0_coefficient": "1/2",
                                   "consumer_original_B_index": 1754, "target": 181,
                                   "target_port": 304, "extra_vector": EXTRA, "binary_pairing": 1},
            "universal_scalar_block_statement": "At this cut, any scalar-only block whose entry h0 carriers all contain P, whose new dirty inputs are independent of h0, and whose exit gives 672 a nonzero h0 coefficient forces P into 672; unchanged B1754 then violates target 181's terminal hyperplane. No changed-consumer or global-retiming obstruction is claimed."}


def controls(words):
    outcomes = []
    for provider, word in words.items():
        nodes = make_graph(word, raised=True)
        _, bad = solve_graph(nodes)
        _, relaxed = solve_graph(nodes, ignore_upper=[entry["label"] for entry in bad])
        need(len(bad) == 4 and not relaxed, "terminal-bound sensitivity control")
        outcomes.append(provider + ": accepting after removal of exactly the four violated terminal bounds")
        _, baseline_bad = solve_graph(make_graph(word))
        need(not baseline_bad, "old entrance positive control")
        outcomes.append(provider + ": old entrance admits the fixed contact graph")
        changed = deepcopy(word)
        changed["start_extra"]["544"] = list(reversed(changed["start_extra"]["544"]))
        need(provider_result(changed) == provider_result(word), "basis-order positive control")
        outcomes.append(provider + ": entrance basis order leaves the exact result unchanged")
        corrupted = deepcopy(word)
        corrupted["B"][1116][2] = 463
        try:
            short_witness(corrupted)
        except ValueError as exc:
            need(str(exc) == "short path contact", "wrong short-path mutation rejection")
        else:
            raise ValueError("short-path contact mutant was accepted")
        outcomes.append(provider + ": broken B1116 witness contact rejected by the named path check")
        wrong_port = deepcopy(word)
        wrong_port["ports"][4] = 129
        try:
            short_witness(wrong_port)
        except ValueError as exc:
            need(str(exc) == "target separating character", "wrong port mutation rejection")
        else:
            raise ValueError("wrong-port witness mutant was accepted")
        outcomes.append(provider + ": wrong target character rejected by the named separation check")
        coefficients, _ = recovery_coefficients(word)
        prefix = forward_prefix(word, omitted=(683, 684))
        for register in sorted(coefficients):
            incomplete = dict(coefficients)
            incomplete.pop(register)
            need(combine_rows(prefix, incomplete) != {(544, ()): Fraction(1)},
                 "omitted recovery source was accepted")
            outcomes.append(provider + ": all-column late recovery rejects missing source " + str(register))
        need(recovered_prefix(prefix, coefficients, wrong_sign=True) != forward_prefix(word),
             "wrong late release sign was accepted")
        outcomes.append(provider + ": complete prefix rejects the wrong late release sign")
    expected = [["1", "0", "0", "1", "-2"], ["1/2", "1", "0", "0", "0"],
                ["-1/2", "0", "1", "0", "0"], ["0", "0", "0", "1", "0"],
                ["0", "0", "0", "0", "1"]]
    need(local_matrix() == expected, "complete five-column local semantics")
    for mutant in ("omit_first_release", "wrong_first_sign", "late_uncorrected_releases"):
        need(local_matrix(mutant) != expected, "semantic mutation accepted: " + mutant)
        outcomes.append("all-column local semantics rejects " + mutant)
    return outcomes


def compute(with_controls=True):
    receipts = authenticate()
    words = {provider: load_word(provider) for provider in ("base", "extra")}
    providers = {provider: {**provider_result(word), "late_boundary": late_boundary(word)}
                 for provider, word in words.items()}
    need(providers["base"] == providers["extra"], "providers have different decisive constraints")
    return {"schema": "second-staged-544-independent-fixed-contact-v1",
            "status": "PASS_FIXED_CONTACT_OBSTRUCTION",
            "source_head": SOURCE_HEAD, "canonical_base": CANONICAL_BASE,
            "checker_sha256": digest(Path(__file__).read_bytes()),
            "source_export_sha256": EXPORT_DIGEST, "source_files_sha256": receipts,
            "providers": providers,
            "controls": controls(words) if with_controls else [],
            "local_all_coefficient_matrix": local_matrix(),
            "local_matrix_columns_and_rows": ["h544", "h672", "h676", "r379", "r236"],
            "coverage": "Two pinned finite words; exact least monotone fixed-contact constraints, all-column formal-operator prefix recovery at original B1752, and written fixed-word/local scalar-block implications. No formal-kernel proof, changed-consumer/global-retiming obstruction, complete supplier or kappa claim."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", "--write", dest="output", type=Path, help="explicitly generate a new result certificate")
    parser.add_argument("--check", type=Path, help="consume an existing certificate; never generate if missing")
    args = parser.parse_args()
    need(not (args.output and args.check), "choose generation or verification")
    result = compute()
    check = args.check if args.check else None if args.output else HERE / "independent-result.json"
    if check:
        need(json.loads(check.read_bytes()) == result, "fixed result certificate differs")
    if args.output:
        args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf8")
    brief = {key: result[key] for key in ("status", "source_head", "checker_sha256")}
    brief["providers"] = {provider: {key: row[key] for key in
                         ("constraint_nodes", "raised_feasible", "affected_B_contacts", "cone_counts_by_kind")}
                          for provider, row in result["providers"].items()}
    brief["controls"] = len(result["controls"])
    brief["certificate"] = "verified" if check else "generated"
    print(json.dumps(brief, sort_keys=True))


if __name__ == "__main__":
    main()
