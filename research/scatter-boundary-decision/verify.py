"""Independent reproduction and successor-schema decision at the scatter/export
boundary of the selected bit word.  Nick Petalas, Apache-2.0.

The audited claim is research/scatter-export-parity-audit (#2977): a
symbolically accepted word whose unchanged record exporter changes the target
endpoint.  This package re-derives it on a separate route and decides which
boundary a successor checker/exporter must enforce.

Route: the pinned checker and exporter run unchanged as black-box executables;
records are interpreted by a locally written reader whose semantics come from
the exporter's own docstring, not from the audited package's replay.
"""

import argparse
import ast
import copy
import gzip
import hashlib
import itertools
import json
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREFIX = "research/e8-bit-p111-tuned/"
WORD = PREFIX + "tune/bitE8mut-p111-tuned.json.gz"
BASE_WORD = "research/e8-bit-p111/data/bitE8mut-p111.json.gz"
CHECKER = PREFIX + "code/xcheck_p.py"
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
GEN_P3 = PREFIX + "code/gen_p3.py"
PWORDL = PREFIX + "code/pwordl.py"
APPLY = PREFIX + "tune/apply.py"
SELECTED = "research/community-frontier1094-audit/SELECTED-SOURCE.json"
ARCHIVED = "research/scatter-export-parity-audit/RESULT.json"

RECORD = struct.Struct("<6i")
COLUMNS = 661
RETAIN = 9


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(body):
    return hashlib.sha256(body).hexdigest()


def sources(root):
    rows = json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]
    require(0 < len(rows) <= 24, "bounded source inventory")
    result = {}
    for row in rows:
        if row["usage"] != "input":
            continue
        path = row["path"]
        require(not Path(path).is_absolute() and ".." not in Path(path).parts, "contained input")
        require(path not in result, "unique source input")
        target = root / path
        require(target.stat().st_size <= 5 * 1024 * 1024, "bounded source bytes")
        body = target.read_bytes()
        require(sha256(body) == row["sha256"], "source: " + path)
        result[path] = body
    selected = json.loads(result[SELECTED])["files"]
    for path in (WORD, CHECKER, EXPORTER):
        require(sha256(result[path]) == selected[path], "selected source binding: " + path)
    return result


def load_word(body):
    return json.loads(gzip.decompress(body))


def census(word):
    """Row multiplicity facts for one word, measured not assumed."""
    rows = word["scatter"]
    duplicates = [t for t, row in enumerate(rows) if len(set(row)) != len(row)]
    counts = [Counter(row).most_common(1)[0][1] for row in rows if row]
    return {
        "v": word["v"],
        "rows_with_repeats": len(duplicates),
        "first_repeat_row": duplicates[0] if duplicates else None,
        "max_multiplicity": max(counts) if counts else 0,
        "terms": sum(len(row) for row in rows),
    }


def deploy(body, directory, name):
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / name
    target.write_bytes(body)
    return target


def run_checker(checker, word, directory, tag):
    """Run the pinned checker as an unchanged executable on one word."""
    directory.mkdir(parents=True, exist_ok=True)
    word_path = directory / (tag + ".json.gz")
    word_path.write_bytes(gzip.compress(json.dumps(word).encode()))
    out = directory / (tag + ".checker.json")
    run = subprocess.run(
        [sys.executable, "-I", "-B", str(checker), str(word_path), "--json", str(out)],
        check=False, capture_output=True, text=True, timeout=120,
    )
    if run.returncode == 0:
        verdict = "accept"
    elif "REJECT" in run.stdout:
        verdict = "reject"
    else:
        verdict = "error"
    message = None
    if verdict != "accept":
        lines = [ln for ln in run.stdout.splitlines() if ln.strip()]
        message = (lines[-1] if lines else "") or (run.stderr.splitlines()[-1] if run.stderr else "")
    payload = json.loads(out.read_bytes()) if out.exists() else None
    require(verdict != "accept" or (payload is not None and payload["status"].startswith("PASS")), "checker status")
    return {"verdict": verdict, "message": message, "payload": payload}


def run_export(exporter, word, directory, tag):
    """Run the pinned exporter as an unchanged executable; return record bytes."""
    directory.mkdir(parents=True, exist_ok=True)
    word_path = directory / (tag + ".json.gz")
    word_path.write_bytes(gzip.compress(json.dumps(word).encode()))
    out = directory / (tag + ".records")
    run = subprocess.run(
        [sys.executable, "-I", "-B", str(exporter), str(word_path), str(out)],
        check=False, capture_output=True, text=True, timeout=120,
    )
    require(run.returncode == 0, "export failed: " + run.stderr)
    body = (out / "249-records.bin").read_bytes()
    require(0 < len(body) <= 30000 * RECORD.size and len(body) % RECORD.size == 0, "bounded records")
    return body


def interpret(records, word):
    """F2 operator of the record stream, read from the exporter's own docstring.

    Registers 0..n-1 start as identity columns e_i; the temporary register
    starts at zero.  MOVE is frame movement only; ADD XORs its source when the
    integer coefficient is odd; COPY loads the temporary register; ERASE closes
    it.  Required endpoint: target v+t holds e_{v+t} + e_t.
    """
    v = word["v"]
    n = 2 * v + word["R"]
    require(n == COLUMNS, "selected column count")
    values = [1 << i for i in range(n)]
    temp = 0
    opened = None
    for op, first, second, coefficient, _frame, _phase in RECORD.iter_unpack(records):
        require(0 <= first <= n and 0 <= second <= n, "record register")
        if op == 0:
            continue
        if op == 1:
            require(first != n and (second != n or opened is not None), "ADD shape")
            if coefficient % 2:
                values[first] ^= values[second] if second != n else temp
        elif op == 2:
            require(opened is None and second == n and first < n, "COPY shape")
            temp, opened = values[first], first
        elif op == 3:
            require(opened == first and second == n, "ERASE source binding")
            temp, opened = 0, None
        else:
            raise ValueError("record opcode")
    require(opened is None and temp == 0, "temporary closes")
    expected = [1 << i for i in range(n)]
    for t in range(v):
        expected[v + t] ^= 1 << t
    return [(i, values[i] ^ expected[i]) for i in range(n) if values[i] != expected[i]]


def difference_digest(differences):
    return sha256(json.dumps([(i, "%x" % mask) for i, mask in differences]).encode())


def simple_support(rows):
    """Sufficient successor boundary: every row is a strictly simple support."""
    if type(rows) is not list:
        return False
    for row in rows:
        if type(row) is not list or len(row) > RETAIN:
            return False
        if not all(type(k) is int and 0 <= k < RETAIN for k in row):
            return False
        if len(row) != len(set(row)):
            return False
    return True


def multiplicity_agrees(rows):
    """Exact set of words on which the two lowering semantics coincide.

    The checker XORs a copied total once per occurrence (multiplicity parity);
    the exporter emits one ADD when the index occurs at all (membership).
    """
    return all((count % 2) == (1 if count else 0) for row in rows for count in Counter(row).values())


def producer_checks(gen_text, pwordl_text, apply_text):
    tree = ast.parse(gen_text)
    decoder = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "decoder_rows")
    uses_combinations = any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "combinations"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "itertools"
        for node in ast.walk(decoder)
    )
    monotone = all(
        len(row) == len(set(row)) and list(row) == sorted(row)
        for size in range(6)
        for row in itertools.combinations(range(5), size)
    )
    return {
        "decoder_rows_uses_itertools_combinations": uses_combinations,
        "combinations_are_simple_supports": monotone,
        "pwordl_build_copies_rows": "scatter=[list(scatter_rows[t]) for t in ports]" in pwordl_text,
        "tune_apply_mentions_scatter": "scatter" in apply_text,
    }


def decision_table(checker, exporter, word, directory, archived):
    base = run_export(exporter, word, directory, "m0")
    base_sha = sha256(base)
    base_count = len(base) // RECORD.size
    require(
        (base_count, base_sha) == (archived["baseline"]["records"], archived["baseline"]["records_sha256"]),
        "archived baseline record receipt",
    )
    rows = []
    exports = {}
    for m in range(7):
        mutant = copy.deepcopy(word)
        if m:
            mutant["scatter"][0] = mutant["scatter"][0] + [0] * m
        verdict = run_checker(checker, mutant, directory, "m%d" % m)
        records = run_export(exporter, mutant, directory, "m%d" % m)
        exports[m] = records
        differences = interpret(records, mutant)
        normalised = copy.deepcopy(mutant)
        normalised["scatter"][0] = mutant["scatter"][0][:-m] + ([0] if m % 2 else []) if m else mutant["scatter"][0]
        rebuilt = run_export(exporter, normalised, directory, "m%d.parity" % m)
        rows.append({
            "appended_occurrences": m,
            "checker": verdict["verdict"],
            "checker_message": verdict["message"],
            "export_records": len(records) // RECORD.size,
            "export_delta": len(records) // RECORD.size - base_count,
            "checker_accepts": verdict["verdict"] == "accept",
            "operator_parity": m % 2,
            "operator_membership": 1 if m else 0,
            "operator_agrees": multiplicity_agrees(mutant["scatter"]),
            "normalised_export_matches_mutant_export": sha256(rebuilt) == sha256(records),
            "difference_registers": len(differences),
            "difference_digest": difference_digest(differences),
        })
    require(all(r["export_delta"] == 1 for r in rows[1:]), "presence semantics adds one record")
    require(
        [r["appended_occurrences"] for r in rows if r["checker_accepts"] and not r["operator_agrees"]] == [2, 4, 6],
        "hazard class: checker-accepted words whose rows do not agree",
    )
    require(
        all(
            (not r["normalised_export_matches_mutant_export"]) == (r["appended_occurrences"] in (2, 4, 6))
            for r in rows
        ),
        "normalisation changes exactly the even-multiplicity exports",
    )
    mutant_word = copy.deepcopy(word)
    mutant_word["scatter"][0] = mutant_word["scatter"][0] + [0, 0]
    differences = interpret(exports[2], mutant_word)
    require(len(differences) == 1 and differences[0][0] == word["v"], "single changed target")
    support = [i for i in range(COLUMNS) if differences[0][1] >> i & 1]
    witness = archived["mutant"]["witness"]
    require(
        (rows[2]["export_records"], sha256(exports[2]))
        == (archived["mutant"]["records"], archived["mutant"]["records_sha256"]),
        "pair mutant record bytes",
    )
    return {
        "baseline": {"records": base_count, "records_sha256": base_sha},
        "table": rows,
        "hazard_class": [r["appended_occurrences"] for r in rows if r["checker_accepts"] and not r["operator_agrees"]],
        "archived_mutant_records": archived["mutant"]["records"],
        "archived_mutant_records_sha256": archived["mutant"]["records_sha256"],
        "witness_support_matches_archive": support == witness["difference_support"],
        "witness_support_size": len(support),
        "witness_input_column": witness["input_column"],
        "witness_present": bool(differences[0][1] >> witness["input_column"] & 1),
    }


def type_probes(checker, exporter, word, directory, base_sha, base_count):
    probes = [("float_one", [1.0]), ("bool_true", [True]), ("string_one", ["1"]), ("out_of_range", [9])]
    rows = []
    for tag, extra in probes:
        mutant = copy.deepcopy(word)
        mutant["scatter"][0] = mutant["scatter"][0] + extra
        verdict = run_checker(checker, mutant, directory, tag)
        records = run_export(exporter, mutant, directory, tag)
        rows.append({
            "probe": tag,
            "appended": [repr(k) for k in extra],
            "checker": verdict["verdict"],
            "checker_message": verdict["message"],
            "export_delta": len(records) // RECORD.size - base_count,
            "export_changed": sha256(records) != base_sha,
        })
    return rows


def guard_battery(word):
    cases = [
        ("pinned row 0", word["scatter"][0], True),
        ("duplicate pair", [4, 4], False),
        ("duplicate with odd count", [4, 4, 4], False),
        ("bool", [True], False),
        ("negative", [-1], False),
        ("out of range", [9], False),
        ("float", [1.0], False),
        ("string", ["1"], False),
        ("full range row", list(range(10)), False),
        ("empty row", [], True),
    ]
    return [
        {"case": name, "row": [repr(k) for k in row], "guard_accepts": simple_support([row]), "expected": expected}
        for name, row, expected in cases
    ]


def audit(root, directory):
    data = sources(root)
    checker = deploy(data[CHECKER], directory, "xcheck_p.py")
    exporter = deploy(data[EXPORTER], directory, "export_records.py")
    word = load_word(data[WORD])
    base = load_word(data[BASE_WORD])
    archived = json.loads(data[ARCHIVED])
    require(word["v"] == 111 and word["R"] == 439 and len(word["ret"]) == RETAIN, "selected word shape")
    require(len(word["scatter"]) == word["v"] and len(base["scatter"]) == base["v"], "row inventories")
    tuned_census, base_census = census(word), census(base)
    require(tuned_census["max_multiplicity"] <= 1 and base_census["max_multiplicity"] <= 1, "producer rows are simple")
    require(simple_support(word["scatter"]) and multiplicity_agrees(word["scatter"]), "pinned predicates")
    verdict = run_checker(checker, word, directory, "baseline")
    require(verdict["verdict"] == "accept", "selected word checker")
    baseline = run_export(exporter, word, directory, "baseline")
    require(not interpret(baseline, word), "positive control endpoint")
    table = decision_table(checker, exporter, word, directory, archived)
    require(table["hazard_class"] == [2, 4, 6], "hazard class")
    require(table["witness_support_matches_archive"] and table["witness_present"], "witness reproduction")
    producer = producer_checks(data[GEN_P3].decode(), data[PWORDL].decode(), data[APPLY].decode())
    require(
        producer["decoder_rows_uses_itertools_combinations"]
        and producer["combinations_are_simple_supports"]
        and producer["pwordl_build_copies_rows"]
        and not producer["tune_apply_mentions_scatter"],
        "producer guarantee",
    )
    return {
        "status": "PASS_SCATTER_BOUNDARY_DECISION",
        "columns": COLUMNS,
        "tuned_census": tuned_census,
        "base_census": base_census,
        "tuned_rows_equal_base_rows": word["scatter"] == base["scatter"],
        "checker_baseline": {"columns": verdict["payload"]["columns"], "v": verdict["payload"]["v"]},
        "decision": table,
        "type_probes": type_probes(checker, exporter, word, directory, sha256(baseline), len(baseline) // RECORD.size),
        "guard_battery": guard_battery(word),
        "exact_condition": {
            "checker_semantics": "XOR once per occurrence (multiplicity parity)",
            "exporter_semantics": "one ADD when the index occurs (membership)",
            "agreeing_words": "every positive multiplicity is odd",
            "hazard_from_checker_accepted_words": "some positive multiplicity is even",
        },
        "producer": producer,
        "recommendation": (
            "successor exporter: enforce simple supports (reject duplicates) while the retained "
            "generator is the only producer, because decoder_rows emits strictly increasing "
            "combinations; if multiplicity is ever meaningful, canonicalise rows to parity in the "
            "exporter instead of lowering by membership; additionally declare index types and range "
            "explicitly, because bool is accepted as int by both stages while float and string "
            "behave differently (float crashes the checker; string never matches the exporter)"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="scatter-boundary-decision-") as temporary:
        result = audit(args.root, Path(temporary))
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_bytes())
        require(
            json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "typed deterministic receipt",
        )
        print(result["status"], "columns=661 hazard=[2,4,6] no_new_kappa")


if __name__ == "__main__":
    main()
