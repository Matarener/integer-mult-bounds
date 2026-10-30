#!/usr/bin/env python3
"""Check one smaller selected P104 circuit. Produced by Nick Petalas.

Apache-2.0. The source word and tariff retain the credits in README.md.
No predecessor executable is imported, and no source file is changed.
"""
import gzip
import io
import json
import sys
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CASES = (
    ("selected", "research/p104-helper-subspace-splits/WORD.json.gz",
     9751, 25475, 220232, 220226),
    ("sign_gauge", "research/p104-sign-gauge/WORD.json.gz",
     9627, 25253, 219258, 219252),
)
BEFORE = [
    ["ADD", 225, 234, "-1", 267],
    ["ADD", 229, 234, "1", 267],
    ["ADD", 227, 234, "1", 267],
    ["ADD", 225, 234, "-1", 267],
]
AFTER = [
    ["ADD", 225, 234, "-2", 267],
    ["ADD", 229, 234, "1", 267],
    ["ADD", 227, 234, "1", 267],
]
ROLES = (225, 227, 229, 234)


def need(value, message):
    if not value:
        raise ValueError(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(raw).hexdigest()


def source_word(source, events):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    pin = next(row for row in manifest["files"] if row["path"] == source)
    with (ROOT / source).open("rb") as stream:
        raw = stream.read(262145)
    need(len(raw) <= 262144, "Compressed source bound")
    need(sha256(raw).hexdigest() == pin["sha256"], "Source hash")
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        payload = stream.read(4194305)
    need(len(payload) <= 4194304, "Uncompressed source bound")
    word = json.loads(payload)
    need(word["public"] == 748, "Exact public boundary")
    need(len(word["program"]) == events <= 25475, "Exact source length")
    need(len(word["frames"]) == 1089, "Exact frame inventory")
    return word, sha256(raw).hexdigest(), sha256(payload).hexdigest()


def construct(word, start):
    need(word["program"][start:start + 4] == BEFORE, "Exact source block")
    changed = deepcopy(word)
    changed["program"][start:start + 4] = deepcopy(AFTER)
    return changed


def local_prefixes(program):
    need(0 < len(program) <= 4, "Local length bound")
    rows = {r: tuple(Fraction(r == s) for s in ROLES) for r in ROLES}
    prefixes = [dict(rows)]
    for event in program:
        need(event[0] == "ADD" and len(event) == 5, "Local ADD grammar")
        _, dst, src, coefficient, frame = event
        need(dst in ROLES and src in ROLES and dst != src, "Local ports")
        need(frame == 267, "One local chart")
        q = Fraction(coefficient)
        rows[dst] = tuple(a + q*b for a, b in zip(rows[dst], rows[src], strict=True))
        prefixes.append(dict(rows))
    return prefixes


def local_identity(before, after):
    old, new = local_prefixes(before), local_prefixes(after)
    need(old[-1] == new[-1], "Exact dirty local endpoint")
    for role in ROLES:
        values = {prefix[role] for prefix in old}
        need(all(prefix[role] in values for prefix in new),
             "No new macro-boundary row value")
    return {"roles": len(ROLES), "basis_columns": len(ROLES),
            "before_prefixes": len(old), "after_prefixes": len(new)}


def boundaries(word, changed, start):
    need({k: v for k, v in word.items() if k != "program"} ==
         {k: v for k, v in changed.items() if k != "program"},
         "All boundary metadata unchanged")
    need(word["program"][:start] == changed["program"][:start], "Same prefix")
    need(word["program"][start + 4:] == changed["program"][start + 3:],
         "Same suffix")
    current = word["initial"][:] + [None]*8
    for event in word["program"][:start]:
        if event[0] == "MOVE":
            current[event[1]] = event[3]
        elif event[0] == "INIT":
            current[event[1]] = event[2]
        elif event[0] == "CLEAR":
            current[event[1]] = None
    need(all(current[r] == 267 for r in ROLES), "Actual common-frame cut")
    old = [e for e in word["program"] if e[0] != "ADD"]
    new = [e for e in changed["program"] if e[0] != "ADD"]
    need(old == new, "Every non-ADD occurrence unchanged")
    paid = [e for e in old if e[0] == "MOVE"]
    profile = Counter(abs(len(word["frames"][e[3]]) -
                          len(word["frames"][e[2]])) for e in paid)
    return {"paid_occurrences": len(paid), "paid_profile": dict(profile),
            "public_inputs": word["public"], "owned_role_slots": 8}


def add_row(destination, source, coefficient):
    for column, value in source.items():
        total = destination.get(column, Fraction(0)) + coefficient*value
        if total:
            destination[column] = total
        else:
            destination.pop(column, None)


def normalized_endpoint(word):
    """Compare complete coefficients; MOVE is a chart identification here.

    The separate local context proof covers arbitrary actual native maps.
    This diagnostic is not a replay of their Gaussian action or phases.
    """
    count = word["public"] + 8
    need(count == 756 and len(word["program"]) <= 25475, "Endpoint bounds")
    rows = [{r: Fraction(1)} for r in range(count)]
    for event in word["program"]:
        op, dst = event[:2]
        need(0 <= dst < count, "Endpoint destination bound")
        if op == "MOVE":
            continue
        if op in ("INIT", "CLEAR"):
            rows[dst] = {}
        elif op == "SCALE":
            q = Fraction(event[-2])
            rows[dst] = {c: q*v for c, v in rows[dst].items()}
        else:
            need(op in ("ADD", "COPY"), "Endpoint opcode")
            src, q = event[2], Fraction(event[-2])
            need(0 <= src < count and src != dst, "Endpoint source bound")
            if op == "COPY":
                rows[dst] = {c: q*v for c, v in rows[src].items()}
            else:
                add_row(rows[dst], rows[src], q)
    return rows


def scalar_tariff(program):
    total = 0
    for event in program:
        op = event[0]
        if op == "MOVE":
            continue
        if op in ("INIT", "CLEAR"):
            total += 2
            continue
        q = Fraction(event[-2])
        n, d = abs(q.numerator), q.denominator
        need(n > 0 and d & (d - 1) == 0, "Nonzero dyadic scalar")
        if op == "SCALE":
            need(n & (n - 1) == 0, "Dyadic unit scale")
            total += 2*(abs(n.bit_length() - d.bit_length()) + int(q < 0))
        else:
            need(op in ("ADD", "COPY"), "Tariff opcode")
            total += 2*(3 + n.bit_length() - 1 + n.bit_count()
                        + d.bit_length() - 1)
    return total


def rejects(function, *args):
    try:
        function(*args)
    except ValueError:
        return 1
    raise ValueError("A semantic mutation was accepted")


def controls(word, changed, start):
    count = 0
    for position, replacement in ((3, "-1"), (3, "2"), (1, 229),
                                  (2, 229), (4, 266)):
        wrong = deepcopy(AFTER)
        wrong[0][position] = replacement
        count += rejects(local_identity, BEFORE, wrong)
    count += rejects(local_identity, BEFORE, AFTER[:2])
    wrong = deepcopy(changed)
    wrong["final"][225] = wrong["initial"][225]
    count += rejects(boundaries, word, wrong, start)
    wrong = deepcopy(changed)
    move = next(e for e in wrong["program"] if e[0] == "MOVE")
    move[3] = (move[3] + 1) % len(word["frames"])
    count += rejects(boundaries, word, wrong, start)
    # A source update and a target observation block this shortcut.
    for middle in (("ADD", 234, 229, "1", 267),
                   ("ADD", 229, 225, "1", 267)):
        before = [BEFORE[0], list(middle), BEFORE[-1]]
        after = [AFTER[0], list(middle)]
        count += rejects(local_identity, before, after)
    wrong = deepcopy(word)
    wrong["program"][start][3] = "1"
    count += rejects(construct, wrong, start)
    return count


def run_case(case):
    name, source, start, events, expected_old, expected_new = case
    word, source_hash, payload_hash = source_word(source, events)
    changed = construct(word, start)
    local = local_identity(BEFORE, AFTER)
    boundary = boundaries(word, changed, start)
    old_rows = normalized_endpoint(word)
    new_rows = normalized_endpoint(changed)
    need(old_rows == new_rows, "Complete normalized dirty endpoint equality")
    old_cost = scalar_tariff(word["program"])
    new_cost = scalar_tariff(changed["program"])
    need((old_cost, new_cost) == (expected_old, expected_new),
         "Exact full scalar tariff")
    need(len(changed["program"]) == events - 1, "One removed scalar macro")
    endpoint = [[[c, str(v)] for c, v in sorted(row.items())] for row in new_rows]
    return {"case": name, "local": local,
            "boundary": boundary, "normalized_rows": len(new_rows),
            "normalized_endpoint_sha256": digest(endpoint),
            "source_sha256": source_hash, "source_payload_sha256": payload_hash,
            "candidate_canonical_json_sha256": digest(changed),
            "events_before": len(word["program"]),
            "events_after": len(changed["program"]),
            "scalar_before": old_cost, "scalar_after": new_cost,
            "scalar_saving": old_cost - new_cost,
            "rejecting_controls": controls(word, changed, start)}


def run():
    need(len(sys.argv) == 1, "No command-line arguments accepted")
    files = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    return {"status": "PASS_P104_SELECTED_SCALAR_PAIR",
            "cases": [run_case(case) for case in CASES],
            "package_sha256": {f: sha256((HERE / f).read_bytes()).hexdigest()
                               for f in files}}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
