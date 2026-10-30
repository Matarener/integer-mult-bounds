"""Separate scalar-factor and raw binary rectangular-matrix replay."""

import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def demand(ok, message):
    if not ok:
        raise ValueError(message)


def fixtures():
    demand((ROOT / "FIXTURES.json").stat().st_size <= 2_000_000, "fixture byte bound")
    raw = (ROOT / "FIXTURES.json").read_bytes()
    demand(len(raw) <= 2_000_000, "fixture byte bound")
    data = json.loads(raw)
    demand(isinstance(data, list) and 1 <= len(data) <= 256, "fixture count")
    for f in data:
        g, lines = f["groups"], f["lines"]
        demand(3 <= len(g) <= 9 and set(g) == {0, 1, 2}, "group contract")
        demand(all(type(x) is int and x in (0, 1, 2) for x in g), "group index")
        demand(1 <= len(lines) <= 64, "line count")
        occurrences = [0] * len(g)
        for line in lines:
            demand(isinstance(line, list) and 1 <= len(line) <= 3, "line arity")
            seen = []
            for c in line:
                demand(type(c) is int and 0 <= c < len(g), "cell index")
                demand(g[c] not in seen, "one occurrence per group")
                seen.append(g[c])
                occurrences[c] += 1
        demand(all(occurrences), "nonempty cells")
    return data, hashlib.sha256(raw).hexdigest()


def factors(group, value, family):
    a, b, c = [int(group == i) for i in range(3)]
    if family == "VVV":
        return (a + b, a + c, b + c, a + b + c), (
            a + b - c - value,
            a - b + c - value,
            -a + b + c - value,
            2 * value,
        )
    return (a + b - c, a - b + c, -a + b + c, a + b + c), (
        a + b - value,
        a + c - value,
        b + c - value,
        value,
    )


def rank(rows):
    pivots = {}
    for original in rows:
        row = original
        for _ in range(192):
            if not row:
                break
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
        else:
            raise ValueError("binary elimination bound")
    return len(pivots)


def charges(f, values, family):
    q, u = zip(
        *(factors(g, x, family) for g, x in zip(f["groups"], values, strict=True)),
        strict=True,
    )
    labels = [(h, c) for h, line in enumerate(f["lines"]) for c in line]
    result = []
    for term in range(4):
        left = [h for h, c in labels if q[c][term] != 0]
        right = [h for h, c in labels if u[c][term] != 0]
        rows = [sum(int(a == b) << j for j, b in enumerate(right)) for a in left]
        result.append(rank(rows))
    return result


def check_operator(groups):
    entries = 0
    extended = list(groups) + [0, 0]
    for family in ("VVV", "MMM"):
        for modulus in (0, 3, 5, 7):
            values = [2 - (j % 4) for j in range(len(extended))]
            queries, readers = zip(
                *(factors(g, x, family) for g, x in zip(extended, values, strict=True)),
                strict=True,
            )
            queries = list(queries)
            queries[-2:] = [(0, 0, 0, 0)] * 2
            readers = list(readers)
            for j in range(len(groups), len(extended)):
                x = values[j]
                readers[j] = (-x, -x, -x, (2 if family == "VVV" else 1) * x)
            for i in range(len(extended)):
                for j in range(len(extended)):
                    got = sum(readers[i][t] * queries[j][t] for t in range(4))
                    want = 2 * int(
                        i < len(groups) and j < len(groups) and groups[i] == groups[j]
                    )
                    demand(
                        (got - want) % modulus == 0 if modulus else got == want,
                        "operator identity",
                    )
                    entries += 1
    return entries


def evaluate(f, expected):
    best, witness, histogram = None, None, {}
    stream = hashlib.sha256()
    for x in itertools.product((-1, 0, 1), repeat=len(f["groups"])):
        total = sum(charges(f, x, "VVV"))
        stream.update((str(total) + "\n").encode())
        histogram[str(total)] = histogram.get(str(total), 0) + 1
        if best is None or total < best:
            best, witness = total, list(x)
    demand(
        best == expected["vvv_min"] and witness == expected["witness"],
        "VVV minimum/witness",
    )
    demand(histogram == expected["histogram"], "VVV histogram")
    demand(stream.hexdigest() == expected["stream_sha256"], "VVV stream")
    demand(sum(histogram.values()) == expected["assignments"], "assignment count")
    mmm = min(
        sum(charges(f, x, "MMM"))
        for x in itertools.product((0, 1), repeat=len(f["groups"]))
    )
    demand(mmm == expected["mmm_min"], "MMM minimum")
    return check_operator(f["groups"])


def main():
    data, digest = fixtures()
    demand((ROOT / "RESULT.json").stat().st_size <= 8_000_000, "record byte bound")
    expected = json.loads((ROOT / "RESULT.json").read_text())
    demand(expected["fixtures_sha256"] == digest, "fixture hash")
    demand(len(expected["rows"]) == len(data), "result count")
    entries = 0
    for f, row in zip(data, expected["rows"], strict=True):
        demand(f["name"] == row["name"], "fixture order")
        counts = [sum(len(line) == k for line in f["lines"]) for k in (1, 2, 3)]
        demand(
            row["vvv_base"] == counts[0] + 3 * counts[1] + 3 * counts[2], "VVV baseline"
        )
        entries += evaluate(f, row)
    print("PASS_CROSSING_RAW_GRAM", len(data), "operator_entries", entries)


if __name__ == "__main__":
    main()
