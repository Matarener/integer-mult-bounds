"""Exact local identity and complete modified-word replay; no native replay.

Produced by Nick Petalas. The scalar tariff and logical endpoint convention
retain Ali Romman's PR5827 lineage, cited in README.md. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from patch import START, STOP
from patch import check_window, need, rewrite

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/p104-helper468-rung-removal/WORD.json.gz"
MAX_EVENTS = 26000
MAX_FIELDS = 799


def authenticated_word():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    pins = {row["path"]: row["sha256"] for row in manifest["files"]}
    raw = (ROOT / SOURCE).read_bytes()
    need(len(raw) < 2**20 and sha256(raw).hexdigest() == pins[SOURCE],
         "Pinned source bytes")
    payload = gzip.decompress(raw)
    need(len(payload) < 2**23, "Bounded source payload")
    word = json.loads(payload)
    need(word["public"] == 770 and word["owned_fields"] == 29,
         "Pinned field domain")
    need(len(word["program"]) < MAX_EVENTS, "Bounded program")
    need(len(word["frames"]) <= 2048, "Bounded frame inventory")
    return word


def add_row(destination, source, coefficient):
    need(destination is not source, "Distinct ADD rows")
    for column, value in source.items():
        new = destination.get(column, 0) + coefficient * value
        if new:
            destination[column] = new
        else:
            destination.pop(column, None)


def local_matrix(events):
    roles = sorted({role for event in events for role in event[1:3]})
    need(len(roles) <= MAX_FIELDS and len(events) <= MAX_EVENTS,
         "Bounded local matrix")
    rows = {role: {role: Fraction(1)} for role in roles}
    maximum = Fraction(1)
    for event in events:
        need(event[0] == "ADD", "Local ADD alphabet")
        _, destination, source, coefficient, _ = event
        add_row(rows[destination], rows[source], Fraction(coefficient))
        maximum = max(maximum, sum(abs(v) for v in rows[destination].values()))
    return rows, maximum


def scalar_cost(program):
    """The exact integer allowance formula of PR5827 local.replay."""
    total = 0
    for event in program:
        op = event[0]
        if op in ("INIT", "CLEAR"):
            total += 2
        elif op in ("ADD", "COPY", "SCALE"):
            q = Fraction(event[-2])
            n, d = abs(q.numerator), q.denominator
            need(n > 0 and d & (d - 1) == 0, "Nonzero dyadic coefficient")
            if op == "SCALE":
                total += 2 * (abs(n.bit_length() - d.bit_length()) + int(q < 0))
            else:
                total += 2 * (3 + n.bit_length() - 1 + n.bit_count()
                              + d.bit_length() - 1)
    return total


def scalar_event(event, rows, frames, live, public):
    op, destination = event[:2]
    coefficient, frame = Fraction(event[-2]), event[-1]
    need(frames[destination] == frame and coefficient != 0,
         "Scalar destination frame")
    need(destination < public or destination in live, "Live destination")
    if op == "SCALE":
        rows[destination] = {k: coefficient * v
                             for k, v in rows[destination].items()}
        return
    need(op in ("ADD", "COPY"), "Scalar alphabet")
    source = event[2]
    need(source != destination and 0 <= source < len(rows), "Scalar source")
    need(frames[source] == frame and (source < public or source in live),
         "Available common-frame source")
    if op == "COPY":
        need(destination in live and not rows[destination], "COPY into owned zero")
        rows[destination] = {k: coefficient * v for k, v in rows[source].items()}
    else:
        add_row(rows[destination], rows[source], coefficient)


def replay_candidate(word):
    """Only the new word is executed, on every independent input column."""
    public, owned = word["public"], word["owned_fields"]
    need(public + owned == MAX_FIELDS, "Complete column domain")
    rows = [{i: Fraction(1)} for i in range(MAX_FIELDS)]
    frames = list(word["initial"]) + [None] * owned
    live, paid = set(), Counter()
    peak = lifetimes = 0
    for event in word["program"]:
        op, destination = event[:2]
        need(0 <= destination < MAX_FIELDS, "Destination range")
        if op == "MOVE":
            _, _, start, end, private = event
            need(frames[destination] == start, "MOVE source frame")
            need((destination in live) == private, "MOVE ownership")
            paid[abs(len(word["frames"][start]) - len(word["frames"][end]))] += 1
            frames[destination] = end
        elif op == "INIT":
            need(destination >= public and destination not in live, "Owned INIT")
            rows[destination], frames[destination] = {}, event[2]
            live.add(destination)
            peak = max(peak, len(live))
            lifetimes += 1
        elif op == "CLEAR":
            need(destination in live and frames[destination] == event[2],
                 "Owned CLEAR")
            rows[destination], frames[destination] = {}, None
            live.remove(destination)
        else:
            scalar_event(event, rows, frames, live, public)
    need(not live and frames[:public] == word["final"], "All terminal frames")
    for i, row in enumerate(rows):
        expected = {i: Fraction(1)} if i < public else {}
        if i - 112 in word["live"]:
            expected[i - 112] = Fraction(1)
        need(row == expected, "Complete modified-word endpoint")
    return {"columns": MAX_FIELDS, "endpoint_entries": MAX_FIELDS**2,
            "owned_lifetimes": lifetimes, "peak_owned_fields": peak,
            "paid_moves": dict(sorted(paid.items()))}


def check_context(source, candidate):
    need({k: v for k, v in source.items() if k != "program"}
         == {k: v for k, v in candidate.items() if k != "program"},
         "Every boundary and inventory field retained")
    old, new = source["program"], candidate["program"]
    need(old[:START] == new[:START] and old[STOP:] == new[STOP - 2:],
         "Identical surrounding context")
    need([e for e in old if e[0] != "ADD"]
         == [e for e in new if e[0] != "ADD"], "All non-ADD events retained")
    old_matrix, old_maximum = local_matrix(old[START:STOP])
    new_matrix, new_maximum = local_matrix(new[START:STOP - 2])
    need(old_matrix == new_matrix, "Exact arbitrary-input local equality")
    need(len(new) == 25996, "Two-event saving")
    need((scalar_cost(old), scalar_cost(new)) == (228664, 228644),
         "Complete scalar allowance and twenty-unit saving")
    return {"local_roles": len(old_matrix), "old_local_events": STOP - START,
            "new_local_events": STOP - START - 2,
            "old_local_prefix_l1": str(old_maximum),
            "new_local_prefix_l1": str(new_maximum)}


def rejection_controls(word, candidate):
    baseline, _ = local_matrix(word["program"][START:STOP])
    altered = candidate["program"][START:STOP - 2]
    anchor_indices = [i for i, e in enumerate(altered)
                      if e[1:3] == [158, 159]]
    need(len(anchor_indices) == 2, "Two anchor operations")
    bad_minus = [list(e) for e in altered]
    bad_minus[anchor_indices[0]][3] = "1"
    bad_source = [list(e) for e in altered]
    bad_source[anchor_indices[1]][2] = 157
    variants = [bad_minus, bad_source,
                altered[:anchor_indices[0]] + altered[anchor_indices[0] + 1:],
                altered[:anchor_indices[1]] + altered[anchor_indices[1] + 1:]]
    for variant in variants:
        rows, _ = local_matrix(variant)
        need(rows != baseline, "Reject wrong anchor identity")
    for index, replacement in [
            (666, ["ADD", 250, 158, "1", 3]),
            (666, ["ADD", 250, 159, "1", 3]),
            (666, ["ADD", 133, 250, "1", 3]),
            (666, ["ADD", 250, 251, "1", 4]),
            (509, ["ADD", 158, 711, "2", 3])]:
        program = list(word["program"])
        program[index] = replacement
        try:
            check_window(program)
        except ValueError:
            continue
        raise ValueError("Unsafe source window accepted")
    return {"matrix_mutants_rejected": len(variants),
            "premise_mutants_rejected": 5}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-word", type=Path)
    args = parser.parse_args()
    source = authenticated_word()
    candidate = rewrite(source)
    context = check_context(source, candidate)
    controls = rejection_controls(source, candidate)
    replay = replay_candidate(candidate)
    payload = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
    if args.emit_word is not None:
        target = args.emit_word.resolve()
        need(not target.is_relative_to(ROOT), "Emit only outside the checkout")
        with target.open("xb") as output:
            need(output.write(payload + b"\n") == len(payload) + 1, "Complete export")
    hashes = {p.name: sha256(p.read_bytes()).hexdigest()
              for p in sorted(HERE.iterdir()) if p.is_file()}
    result = {"status": "PASS_P104_DIRTY_ANCHOR_WINDOW",
              "candidate_payload_sha256": sha256(payload).hexdigest(),
              "old_events": 25998, "new_events": 25996,
              "old_scalar_allowance": 228664, "new_scalar_allowance": 228644,
              "local": context, "candidate_replay": replay, "controls": controls,
              "package_sha256": hashes, "new_kappa_claimed": False}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
