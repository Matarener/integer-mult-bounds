"""Construct sparse bases for the complete G20 port interface.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Source interfaces, route joins and tariffs retain the credits in NOTICE.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(test, message):
    if not test:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def right(word, n=8):
    """Execute the serialized row operations on a basis of all row inputs."""
    out = identity(n)
    for op in word:
        kind, i = op[:2]
        need(type(i) is int and 0 <= i < n, "coordinate")
        a = Q(op[-1])
        if kind == "ADD":
            j = op[2]
            need(len(op) == 4 and type(j) is int and 0 <= j < n and i != j,
                 "ADD coordinates")
            need(a in (-1, 1, Q(-1, 4), Q(1, 4)), "dyadic ADD alphabet")
            for row in out:
                row[j] += a * row[i]
        else:
            need(kind == "SCALE" and len(op) == 3 and a in (Q(1, 2), 2),
                 "power-two SCALE alphabet")
            for row in out:
                row[i] *= a
    return out


def invert(word):
    return [op[:-1] + [str(-Q(op[-1]) if op[0] == "ADD" else 1 / Q(op[-1]))]
            for op in reversed(word)]


def construct(line):
    """Build column updates, then reverse their order for a RIGHT product."""
    support = [i for i, x in enumerate(line) if x]
    need(len(support) in (1, 4), "source support")
    need(len({abs(line[i]) for i in support}) == 1, "equal source magnitudes")
    pivot = support[0]
    left = []
    if pivot:
        # This signed swap sends e_0 to -e_pivot. Its sign is free for a line.
        left += [["ADD", 0, pivot, "1"], ["ADD", pivot, 0, "-1"],
                 ["ADD", 0, pivot, "1"]]
    if len(support) == 4:
        a, b, c, d = support
        signs = {i: line[i] / line[pivot] for i in support}

        def butterfly(i, j, s):
            # (x,y) -> (x-s*y, s*x+y). The two rows are orthogonal.
            left.extend([["ADD", i, j, str(-s)], ["SCALE", j, "2"],
                         ["ADD", j, i, str(s)]])

        butterfly(a, c, signs[c])
        butterfly(a, b, signs[b])
        butterfly(c, d, signs[d] / signs[c])
    return list(reversed(left))


def shear_construct(line):
    """Use determinant-one shears on a four-coordinate support."""
    support = [i for i, x in enumerate(line) if x]
    pivot = support[0]
    word = []
    if len(support) == 4:
        for j in support[1:]:
            word.append(["ADD", j, pivot, str(line[j] / line[pivot])])
        for j in support[1:]:
            word.append(["ADD", pivot, j, str(-line[j] / (4 * line[pivot]))])
    if pivot:
        word += [["ADD", 0, pivot, "1"], ["ADD", pivot, 0, "-1"],
                 ["ADD", 0, pivot, "1"]]
    return word


def projector(source):
    w = [[Q(x) for x in row] for row in source["normalizer"]]
    v = [[Q(x) for x in row] for row in source["inverse"]]
    need(multiply(w, v) == identity(8), "source inverse")
    return [[w[i][0] * v[0][j] for j in range(8)] for i in range(8)]


def paired(p):
    """Build the literal x_i / x_(15-i) native address action."""
    h = identity(16)
    for i in range(8):
        for j in range(8):
            h[i][j] -= p[i][j]
            h[i][15-j] += p[i][j]
            h[15-i][j] += p[i][j]
            h[15-i][15-j] -= p[i][j]
    return h


def reflected(w):
    out = [[Q(0) for _ in range(16)] for _ in range(16)]
    for i in range(8):
        for j in range(8):
            out[i][j] = out[15-i][15-j] = w[i][j]
    return out


def check_port(record, source):
    w, v = right(record["forward"]), right(record["inverse"])
    need(multiply(w, v) == multiply(v, w) == identity(8), "both inverse products")
    p = projector(source)
    q = [[Q(i == j == 0) for j in range(8)] for i in range(8)]
    need(multiply(v, multiply(p, w)) == q, "entry projector")
    need(multiply(p, w) == multiply(w, q), "line and all complement columns")
    d, di = reflected(w), reflected(v)
    need(multiply(di, multiply(paired(p), d)) == paired(q), "physical paired action")
    dense = identity(8)
    for op in record["forward"]:
        e = identity(8)
        if op[0] == "ADD":
            e[op[1]][op[2]] = Q(op[3])
        else:
            e[op[1]][op[1]] = Q(op[2])
        dense = multiply(dense, e)
    need(dense == w, "independent dense elementary product")


def route_counts(events, calls):
    expected = {}
    for call in calls:
        if call["stage"] == 0:
            continue
        for phase, start in (("ENTRY", call["core_begin"] - 222),
                             ("RETURN", call["core_end"])):
            for k, bank in enumerate((call["source_bank"], call["target_bank"])):
                for port in range(111):
                    index = start + k * 111 + port
                    need(index not in expected, "disjoint route intervals")
                    expected[index] = ["PAID_PORT_ROUTE", call["stage"],
                                       111 * bank + port, port, phase]
    actual = {i: e for i, e in enumerate(events) if e[0] == "PAID_PORT_ROUTE"}
    need(actual == expected and len(actual) == 7548, "exact route-event join")
    counts = Counter((e[3], "inverse" if e[4] == "ENTRY" else "forward")
                     for e in actual.values())
    need(len(counts) == 222 and set(counts.values()) == {34}, "direction incidence")
    return counts, sha256(canonical(expected)).hexdigest()


def histogram(records, counts, suffix=""):
    h = {kind: Counter() for kind in ("ADD", "SCALE")}
    for r in records:
        for direction in ("forward", "inverse"):
            for op in r[direction + suffix]:
                h[op[0]][str(Q(op[-1]))] += counts[r["port"], direction]
    return {kind: dict(sorted(counter.items())) for kind, counter in h.items()}


def run():
    raw = {}
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["vendored_inputs"]:
        content = (HERE / row["path"]).read_bytes()
        need(sha256(content).hexdigest() == row["sha256"], "source hash: " + row["path"])
        raw[Path(row["path"]).name] = content
    ports = json.loads(raw["PORTS.json"])
    old = json.loads(raw["WORDS.json"])
    calls = json.loads(raw["CALLS.json"])
    controller = json.loads(raw["CONTROLLER.json"])
    need([c["stage"] for c in calls] == controller["invoice"]["thick_stages"],
         "all source stage ordinals")
    decoded = gzip.decompress(raw["GLOBAL.jsonl.gz"])
    need(sha256(decoded).hexdigest() == ports["stream_sha256"], "source stream")
    events = [json.loads(line) for line in decoded.splitlines()]
    need(len(events) == 317004, "source event count")
    counts, join = route_counts(events, calls)
    records, shear_records = [], []
    for source in ports["port_interfaces"]["ports"]:
        line = [Q(row[0]) for row in source["normalizer"]]
        word = construct(line)
        record = {"port": source["port"], "line": source["line"],
                  "complement": source["complement"], "forward": word,
                  "inverse": invert(word)}
        check_port(record, source)
        records.append(record)
        shear = shear_construct(line)
        alternative = {"port": source["port"], "line": source["line"],
                       "complement": source["complement"], "forward": shear,
                       "inverse": invert(shear)}
        check_port(alternative, source)
        shear_records.append(alternative)
    need([r["port"] for r in records] == list(range(111)), "complete port domain")
    new_h, old_h = histogram(records, counts), histogram(old["ports"], counts, "_word")
    delta = {k: {a: old_h[k].get(a, 0) - new_h[k].get(a, 0)
                 for a in sorted(set(old_h[k]) | set(new_h[k]))} for k in old_h}
    need(all(v >= 0 for terms in delta.values() for v in terms.values()),
         "coefficientwise tariff dominance")
    need(any(v > 0 for terms in delta.values() for v in terms.values()), "strict gain")
    controls = []

    def reject(name, operation):
        try:
            operation()
        except ValueError as error:
            controls.append([name, str(error)])
        else:
            raise ValueError("control accepted: " + name)

    def bad_word():
        i = next(i for i, r in enumerate(records) if len(r["forward"]) >= 12)
        r = deepcopy(records[i]); r["forward"].pop()
        r["inverse"] = invert(r["forward"])
        check_port(r, ports["port_interfaces"]["ports"][i])

    reject("coherent wrong basis and inverse", bad_word)
    reject("odd nonunit", lambda: right([["SCALE", 0, "3"]]))
    reject("wrong route owner", lambda: route_counts(
        [e if e[0] != "PAID_PORT_ROUTE" else [*e[:2], e[2]+1, *e[3:]] for e in events], calls))
    return {"schema": "g20-sparse-port-construction/1", "ports": records,
            "scale_free_ports": shear_records,
            "scale_free_histogram": histogram(shear_records, counts),
            "source_events": len(events), "route_markers": sum(counts.values()),
            "route_join_sha256": join, "old_histogram": old_h, "new_histogram": new_h,
            "saved_histogram": delta,
            "old_operations": {k: sum(v.values()) for k, v in old_h.items()},
            "new_operations": {k: sum(v.values()) for k, v in new_h.items()},
            "saved_calls_times_f_squared": {k: {a: 127*v for a, v in row.items()}
                                           for k, row in delta.items()},
            "controls": controls}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=1))
    else:
        need(canonical(result) == canonical(json.loads((HERE / "RESULT.json").read_text())),
             "complete result receipt")
        print("PASS_G20_SPARSE_PORT_CONSTRUCTION", result["new_operations"])
