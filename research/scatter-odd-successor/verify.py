#!/usr/bin/env python3
"""Bind an odd-multiplicity scatter exporter and run the even duplicate through it.

The published replay XORs a retained total once per occurrence. This successor
emits one ADD when that count is odd. The frozen membership exporter is not
edited.
"""

import copy
import gzip
import hashlib
import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WORD = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
EXPORT = ROOT / "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
CHECKER = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"
ARCHIVED = ROOT / "research/scatter-duplicate-boundary/RESULT.json"
EXPORT_LINE = "        if k in row: rec.append((1,v+t,temp,1,ZERO,3))"
REPLAY_LINE = "                        val[v + t] ^= copies[k]"
MARKER = "PASS_SCATTER_ODD_SUCCESSOR even_successor=0 disagreements=0 no_new_kappa"


def fail(message):
    raise SystemExit("FAIL_SCATTER_ODD_SUCCESSOR " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_checker():
    spec = importlib.util.spec_from_file_location("xcheck_p", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def coefficients_of(record, dimension, retained_count):
    coefficients = [[0 for _ in range(retained_count)] for _ in range(dimension)]
    retained = 0
    for opcode, destination, _source, _one, _zero, phase in record:
        if opcode == 2:
            retained += 1
        elif opcode == 1 and phase == 3:
            coefficients[destination - dimension][retained - 1] = 1
    require(retained == retained_count, "scatter did not visit every retained total")
    return coefficients


def frozen_coefficients(word, scatter):
    lines = EXPORT.read_text(encoding="utf-8").splitlines()
    loop = "\n".join(lines[58:63])
    require(EXPORT_LINE.strip() in loop, "export loop is not the pinned membership action")
    record = []
    dimension = word["v"]
    namespace = {
        "c": {"ret": word["ret"], "scatter": scatter},
        "rec": record,
        "cur": [0] * (2 * dimension + word["R"]),
        "dim": [0],
        "ZERO": 0,
        "temp": 2 * dimension + word["R"],
        "v": dimension,
    }
    exec(loop, namespace)
    return coefficients_of(record, dimension, len(word["ret"]))


def successor_coefficients(word, scatter):
    """Emit one phase-3 ADD for each odd occurrence count."""
    record = []
    dimension = word["v"]
    temp = 2 * dimension + word["R"]
    for index, retained in enumerate(word["ret"]):
        record.append((2, retained, temp, 0, 0, 0))
        for target, row in enumerate(scatter):
            if row.count(index) % 2 == 1:
                record.append((1, dimension + target, temp, 1, 0, 3))
    return coefficients_of(record, dimension, len(word["ret"]))


def symbolic_coefficients(checker, word):
    values, _frames, stats = checker.Word(word).replay(sections=("scatter",), frames_on=False)
    dimension = word["v"]
    retained = word["ret"]
    coefficients = [
        [(values[dimension + target] >> retained[index]) & 1 for index in range(len(retained))]
        for target in range(dimension)
    ]
    return coefficients, stats["scatter_terms"]


def disagreements(symbolic, exported):
    found = []
    for target, (left, right) in enumerate(zip(symbolic, exported, strict=True)):
        for index, (symbolic_bit, exported_bit) in enumerate(zip(left, right, strict=True)):
            if symbolic_bit != exported_bit:
                found.append([target, index])
    return found


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/e8-bit-carrier-skeleton/code/bit/export_records.py",
        "research/e8-bit-p111-tuned/code/xcheck_p.py",
        "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
        "research/scatter-duplicate-boundary/RESULT.json",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    require(EXPORT_LINE in EXPORT.read_text(encoding="utf-8"), "exporter no longer uses membership")
    require("validate_scatter" not in EXPORT.read_text(encoding="utf-8"), "an unexpected scatter guard is installed")
    require(REPLAY_LINE in CHECKER.read_text(encoding="utf-8"), "symbolic replay no longer XORs once per occurrence")


def case_of(checker, word, scatter):
    trial = copy.deepcopy(word)
    trial["scatter"] = scatter
    symbolic, terms = symbolic_coefficients(checker, trial)
    return {
        "terms": terms,
        "symbolic": symbolic,
        "frozen": frozen_coefficients(trial, scatter),
        "successor": successor_coefficients(trial, scatter),
    }


def evaluate():
    authenticate()
    archived = json.loads(ARCHIVED.read_text(encoding="utf-8"))
    require(
        archived["even_disagreements"] == [[0, 0]]
        and archived["even_symbolic"] == 0
        and archived["even_export"] == 1
        and archived["repair_adopted"] is False,
        "the archived even-duplicate gap moved",
    )
    checker = load_checker()
    with gzip.open(WORD, "rt", encoding="utf-8") as handle:
        selected = json.load(handle)
    require(selected["scatter"][0] == [4, 5, 6, 7, 8], "selected first row changed")
    require(all(len(row) == len(set(row)) for row in selected["scatter"]), "a selected row repeats an index")
    baseline = case_of(checker, selected, selected["scatter"])
    even_rows = copy.deepcopy(selected["scatter"])
    even_rows[0] = list(even_rows[0]) + [0, 0]
    even = case_of(checker, selected, even_rows)
    triple_rows = copy.deepcopy(selected["scatter"])
    triple_rows[0] = list(triple_rows[0]) + [0, 0, 0]
    triple = case_of(checker, selected, triple_rows)
    require(disagreements(baseline["symbolic"], baseline["frozen"]) == [], "selected frozen export moved")
    require(disagreements(baseline["symbolic"], baseline["successor"]) == [], "successor changes the selected word")
    require(disagreements(even["symbolic"], even["frozen"]) == [[0, 0]], "frozen even gap moved")
    require(even["symbolic"][0][0] == 0 and even["frozen"][0][0] == 1, "frozen even coefficient moved")
    require(disagreements(even["symbolic"], even["successor"]) == [], "successor misses the even cancellation")
    require(even["successor"][0][0] == 0, "successor even coefficient moved")
    require(disagreements(triple["symbolic"], triple["successor"]) == [], "successor misses the odd triple")
    require(triple["symbolic"][0][0] == 1 and triple["successor"][0][0] == 1, "triple coefficient moved")
    require(Counter(even_rows[0])[0] == 2 and Counter(triple_rows[0])[0] == 3, "fixture counts moved")
    return {
        "contract": "odd-multiplicity",
        "repair_adopted_upstream": False,
        "v": selected["v"],
        "rows": len(selected["scatter"]),
        "selected_terms": baseline["terms"],
        "selected_successor_disagreements": [],
        "even_appended": [0, 0],
        "even_terms": even["terms"],
        "even_symbolic": 0,
        "even_frozen_export": 1,
        "even_successor": 0,
        "even_successor_disagreements": [],
        "triple_appended": [0, 0, 0],
        "triple_symbolic": 1,
        "triple_successor": 1,
        "triple_successor_disagreements": [],
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
