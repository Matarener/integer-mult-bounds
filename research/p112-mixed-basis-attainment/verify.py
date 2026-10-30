"""Exact overlap criterion and column-span tariff replay. Apache-2.0."""

import hashlib
import itertools
import json
from pathlib import Path

GROUPS = "ABC"
MASKS = {
    "A": {0: 7, 1: 12, -1: 11},
    "B": {0: 7, 1: 10, -1: 13},
    "C": {0: 7, 1: 9, -1: 14},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(vectors):
    pivots = {}
    for original in vectors:
        value = original
        for bit in range(5, -1, -1):
            if value & (1 << bit):
                if bit in pivots:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    return len(pivots)


def load(directory):
    with (directory / "FIXTURES.json").open("rb") as handle:
        raw = handle.read(200_001)
    require(len(raw) <= 200_000, "fixture size")
    document = json.loads(raw)
    require(isinstance(document, list) and 1 <= len(document) <= 64, "case count")
    for case in document:
        validate(case)
    require(len({case["name"] for case in document}) == len(document), "unique names")
    with (directory / "RESULT.json").open("rb") as handle:
        result_raw = handle.read(200_001)
    require(len(result_raw) <= 200_000, "result size")
    result = json.loads(result_raw)
    require(
        result["fixtures_sha256"] == hashlib.sha256(raw).hexdigest(), "fixture hash"
    )
    return document, result


def validate(case):
    blocks, cells = case["blocks"], case["cells"]
    require(1 <= len(blocks) <= 4 and 3 <= len(cells) <= 8, "geometry limit")
    expected = set()
    for h, block in enumerate(blocks):
        d, bases = block["dimension"], block["bases"]
        require(type(d) is int and 1 <= d <= 6, "block dimension")
        require(1 <= len(bases) <= 3 and set(bases) <= set(GROUPS), "block groups")
        for group, basis in bases.items():
            require(len(basis) == d, "full basis")
            require(all(type(v) is int and 0 < v < 2**d for v in basis), "label range")
            for i, left in enumerate(basis):
                for j, right in enumerate(basis):
                    require((left & right).bit_count() % 2 == (i == j), "Gram-I basis")
                expected.add((group, h, i))
    seen = set()
    for cell in cells:
        group, ports = cell["group"], cell["ports"]
        require(group in set(GROUPS) and 1 <= len(ports) <= 24, "cell group/size")
        for h, j in ports:
            require(type(h) is int and type(j) is int, "port type")
            port = (group, h, j)
            require(port in expected and port not in seen, "cell partition")
            seen.add(port)
    require(seen == expected, "cell coverage")
    require({c["group"] for c in cells} == set(GROUPS), "nonempty groups")


def prepare(case):
    ports = [[] for _ in case["blocks"]]
    for cell_id, cell in enumerate(case["cells"]):
        group = cell["group"]
        for h, j in cell["ports"]:
            ports[h].append((group, cell_id, case["blocks"][h]["bases"][group][j]))
    edges = []
    singles = set()
    for block, labels in zip(case["blocks"], ports, strict=True):
        if len(block["bases"]) == 1:
            singles.update(cell for _, cell, _ in labels)
        for g, cell, vector in labels:
            for other_g, other_cell, other_vector in labels:
                if g < other_g and (vector & other_vector).bit_count() % 2:
                    edges.append((cell, other_cell))
    return ports, sorted(set(edges)), singles


def criterion(case, ports, edges, singles, values):
    if any(values[c] != 1 for c in singles):
        return False
    for left, right in edges:
        x, y = values[left], values[right]
        if (x == 0) != (y == 0) or (x == -1 and y == -1):
            return False
    for block, labels in zip(case["blocks"], ports, strict=True):
        if len(block["bases"]) == 3:
            reference = next(iter(block["bases"]))
            zeros = sum(g == reference and values[c] == 0 for g, c, _ in labels)
            negatives = sum(values[c] == -1 for _, c, _ in labels)
            if negatives + zeros != block["dimension"]:
                return False
    return True


def charges(case, ports, values, family):
    totals = [0] * 4
    for block, labels in zip(case["blocks"], ports, strict=True):
        present = set(block["bases"])
        queries = [{"A", "B"}, {"A", "C"}, {"B", "C"}, set(GROUPS)]
        for term in range(4):
            if family == "VVV" and not present & queries[term]:
                continue
            vectors = []
            for group, cell, vector in labels:
                if family == "VVV":
                    mask = MASKS[group][values[cell]]
                else:
                    zero_masks = {"A": 3, "B": 5, "C": 6}
                    mask = (
                        zero_masks[group]
                        if values[cell] == 0
                        else 15 ^ zero_masks[group]
                    )
                if mask & (1 << term):
                    vectors.append(vector)
            totals[term] += rank(vectors)
    return totals


def pinned_region(edges, singles, count):
    active = set(singles)
    for _ in range(count):
        for left, right in edges:
            if left in active or right in active:
                active.update((left, right))
    require(all((a in active) == (b in active) for a, b in edges), "component closure")
    return active


def replay(case):
    ports, edges, singles = prepare(case)
    active = pinned_region(edges, singles, len(case["cells"]))
    floor = sum(
        b["dimension"] * (1 if len(b["bases"]) == 1 else 3) for b in case["blocks"]
    )
    stream = hashlib.sha256()
    hist = {}
    hits = 0
    first = None
    for values in itertools.product((0, 1, -1), repeat=len(case["cells"])):
        costs = charges(case, ports, values, "VVV")
        total = sum(costs)
        hit = criterion(case, ports, edges, singles, values)
        require(total >= floor and hit == (total == floor), "attainment equivalence")
        stream.update(bytes([*costs, int(hit)]))
        hist[str(total)] = hist.get(str(total), 0) + 1
        if hit:
            reduced = [v if c in active else 0 for c, v in enumerate(values)]
            require(
                sum(charges(case, ports, reduced, "VVV")) == floor,
                "unpinned zero reduction",
            )
            hits += 1
            if first is None:
                first = list(values)
    mmm_floor = sum(
        b["dimension"] * (2 if len(b["bases"]) == 1 else 3) for b in case["blocks"]
    )
    mmm_hist = {}
    for values in itertools.product((0, 1), repeat=len(case["cells"])):
        total = sum(charges(case, ports, values, "MMM"))
        require(total >= mmm_floor, "MMM lower bound")
        mmm_hist[str(total)] = mmm_hist.get(str(total), 0) + 1
    require(
        sum(charges(case, ports, [0] * len(case["cells"]), "MMM")) == mmm_floor,
        "MMM attainment",
    )
    return {
        "name": case["name"],
        "floor": floor,
        "assignments": 3 ** len(case["cells"]),
        "stream_sha256": stream.hexdigest(),
        "histogram": hist,
        "attaining": hits,
        "first": first,
        "minimum": min(map(int, hist)),
        "mmm_floor": mmm_floor,
        "mmm_histogram": mmm_hist,
    }


def main():
    directory = Path(__file__).resolve().parent
    cases, expected = load(directory)
    actual = [replay(case) for case in cases]
    require(actual == expected["cases"], "result mismatch")
    print(
        f"PASS_MIXED_BASIS_CRITERION cases={len(cases)} "
        f"assignments={sum(r['assignments'] for r in actual)}"
    )


if __name__ == "__main__":
    main()
