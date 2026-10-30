"""Finite exact corroboration and source-bound diagnostic demonstration."""

import argparse
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from diagnose import (add_scaled, load_word, localize, need, p104_problem)


def oracle(events, inputs, roles):
    """Replay one scalar basis input at a time; no prefix/suffix tables."""
    matrix = [{} for _ in range(roles)]
    for coordinate in range(inputs):
        values = [Q(int(i == coordinate)) for i in range(roles)]
        for event in events:
            op, destination = event[:2]
            if op == "ADD":
                values[destination] += Q(event[3]) * values[event[2]]
            elif op == "COPY":
                values[destination] = Q(event[3]) * values[event[2]]
            elif op == "SCALE":
                values[destination] *= Q(event[2])
            elif op in ("INIT", "CLEAR"):
                values[destination] = Q(0)
            else:
                need(op == "MOVE", "oracle opcode")
        for row, value in enumerate(values):
            if value:
                matrix[row][coordinate] = value
    return matrix


def flatten(matrix, inputs):
    return tuple(row.get(i, Q(0)) for row in matrix for i in range(inputs))


def brute_repairs(events, inputs, roles, target):
    """Derive each signature by a fresh whole-program unit perturbation."""
    base = flatten(oracle(events, inputs, roles), inputs)
    goal = flatten(target, inputs)
    residual = tuple(t - b for t, b in zip(goal, base))
    if not any(residual):
        return None
    repairs = []
    for index, event in enumerate(events):
        if event[0] != "ADD":
            continue
        altered = [list(e) for e in events]
        altered[index][3] = str(Q(event[3]) + 1)
        image = flatten(oracle(altered, inputs, roles), inputs)
        signature = tuple(a - b for a, b in zip(image, base))
        nonzero = [i for i, value in enumerate(signature) if value]
        if not nonzero:
            continue
        first = nonzero[0]
        delta = residual[first] / signature[first]
        if delta and all(r == delta * s for r, s in zip(residual, signature)):
            repairs.append((index, str(delta), str(Q(event[3]) + delta)))
    return repairs


def compare(events, inputs, roles, target):
    result = localize(events, inputs, roles, target)
    expected = brute_repairs(events, inputs, roles, target)
    if expected is None:
        need(result == {"status": "already_matches", "repairs": []}, "zero residual")
    else:
        actual = [(r["event"], r["delta"], r["replacement"])
                  for r in result["repairs"]]
        need(actual == expected, "complete repair set versus direct replay")
        need((result["status"] == "localized") == bool(expected), "repair status")
        for index, _, coefficient in expected:
            repaired = deepcopy(events)
            repaired[index][3] = coefficient
            need(oracle(repaired, inputs, roles) == target, "direct repaired endpoint")
    return result


def exhaustive_add_words():
    alphabet = [["ADD", d, 1 - d, c, 0]
                for d in range(2) for c in ("-1", "1")]
    words = faults = alternatives = 0
    transcript = hashlib.sha256()
    for length in range(1, 5):
        for letters in itertools.product(alphabet, repeat=length):
            clean = [list(e) for e in letters]
            target = oracle(clean, 2, 2)
            words += 1
            for index in range(length):
                for delta in (Q(-2), Q(1, 2), Q(1)):
                    altered = deepcopy(clean)
                    altered[index][3] = str(Q(altered[index][3]) + delta)
                    result = compare(altered, 2, 2, target)
                    faults += 1
                    alternatives += len(result["repairs"])
                    transcript.update(json.dumps(result, sort_keys=True).encode())
    return dict(words=words, coefficient_faults=faults,
                returned_repairs=alternatives, sha256=transcript.hexdigest())


def singular_and_boundary_controls():
    fixtures = [
        [["ADD", 0, 1, "1", 0], ["COPY", 0, 1, "2", 0]],
        [["INIT", 2, 0], ["ADD", 0, 2, "3", 0]],
        [["COPY", 2, 0, "-1/2", 0], ["ADD", 1, 2, "2", 0],
         ["SCALE", 1, "-2", 0], ["CLEAR", 2, 0]],
        [["ADD", 2, 1, "1", 0], ["SCALE", 2, "0", 0],
         ["ADD", 0, 2, "-1", 0]],
        [["MOVE", 0, 0, 1, 0], ["ADD", 0, 1, "1/2", 1],
         ["COPY", 2, 0, "3", 1], ["ADD", 1, 2, "-2/3", 1]],
    ]
    cases = invisible = 0
    for clean in fixtures:
        target = oracle(clean, 2, 3)
        for index, event in enumerate(clean):
            if event[0] != "ADD":
                continue
            for delta in (Q(-2), Q(1, 2), Q(3)):
                changed = deepcopy(clean)
                changed[index][3] = str(Q(event[3]) + delta)
                result = compare(changed, 2, 3, target)
                cases += 1
                invisible += result["status"] == "already_matches"
    ambiguous = [["ADD", 0, 1, "1", 0], ["ADD", 0, 1, "1", 0]]
    result = compare(ambiguous, 2, 2, [{0: Q(1), 1: Q(1)}, {1: Q(1)}])
    need([r["event"] for r in result["repairs"]] == [0, 1], "ambiguous repairs")
    rank_two = [{0: Q(2)}, {1: Q(2)}]
    need(compare([], 2, 2, rank_two)["status"] == "rank_exceeds_one", "rank two")
    rank_one = [{0: Q(2)}, {1: Q(1)}]
    need(compare([], 2, 2, rank_one)["status"] == "no_single_add_repair", "rank one")
    result = compare([["ADD", 0, 1, "1", 0]], 2, 2,
                     [{0: Q(1), 1: Q(1, 3)}, {1: Q(1)}])
    need(not result["repairs"][0]["p104_coefficient_rule"], "nondyadic repair")
    zero_entries = localize([], 2, 2, [{0: Q(1), 1: Q(0)}, {1: Q(1)}])
    need(zero_entries["status"] == "already_matches", "explicit target zeros")
    return dict(singular_fault_cases=cases, invisible_cases=invisible,
                explicit_ambiguity_events=[0, 1], rank_rejection_controls=2,
                nondyadic_repair_reported=True, explicit_target_zeros=True)


def rejected_inputs():
    target = [{0: Q(1)}, {1: Q(1)}]
    invalid = [
        ([["WHAT", 0]], 2),
        ([["ADD", 0, 0, "1", 0]], 2),
        ([["ADD", 0, 2, "1", 0]], 2),
        ([["ADD", 0, 1, "1/0", 0]], 2),
        ([["ADD", 0, 1, str(1 << 257), 0]], 2),
        ([], 1025),
        ([["CLEAR", 0, 0]] * 26001, 2),
    ]
    count = 0
    for events, roles in invalid:
        try:
            localize(events, 2, roles, target)
        except (ValueError, ZeroDivisionError):
            count += 1
        else:
            raise ValueError("invalid input accepted")
    try:
        add_scaled({}, {0: Q(1 << 4096)}, Q(1))
    except ValueError:
        count += 1
    else:
        raise ValueError("intermediate fraction bound")
    return count


def p104_demo():
    sources = json.loads((ROOT / "SOURCES.json").read_text())
    repository = ROOT.parent.parent
    inputs = [row for row in sources["files"] if row["usage"] == "input"]
    need(len(inputs) == 1, "one live word input")
    source = inputs[0]
    path = repository / source["path"]
    need(hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"], "source hash")
    word = load_word(path)
    public, roles, target = p104_problem(word)
    need(word["program"][0] == ["ADD", 112, 704, "-2", 3], "guarded fault site")
    word["program"][0][3] = "-1"
    result = localize(word["program"], public, roles, target)
    need(result == {"status": "localized", "repairs": [
        {"event": 0, "old": "-1", "delta": "-1", "replacement": "-2",
         "p104_coefficient_rule": True}]}, "unique P104 repair")
    word["program"][0][3] = result["repairs"][0]["replacement"]
    repaired = localize(word["program"], public, roles, target)
    need(repaired["status"] == "already_matches", "complete repaired P104 endpoint")
    return dict(source_sha256=source["sha256"], public_inputs=public,
                observed_outputs=roles, events=len(word["program"]), result=result,
                repaired_endpoint="exactly_matches")


def compute():
    local_files = ["README.md", "PROOF.md", "diagnose.py", "verify.py",
                   "TASK.json", "SOURCES.json", "VERIFY.json"]
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
              for name in local_files}
    return dict(schema_version=1, claim_type="scoped diagnostic proof with finite evidence",
                package_sha256=hashes, exhaustive=exhaustive_add_words(),
                controls=singular_and_boundary_controls(),
                rejected_inputs=rejected_inputs(), p104=p104_demo(),
                kappa_improvement=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        need(result == json.loads((ROOT / "RESULT.json").read_text()), "exact receipt")
        print("PASS_P104_ADD_FAULT_LOCALIZATION", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
