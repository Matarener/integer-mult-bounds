"""Separate explicit-coordinate clique enumeration and bounded cover search."""

import json
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAX_STATES = 500_000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_json(path):
    require(path.stat().st_size <= 65536, "independent metadata byte bound")
    return json.loads(path.read_bytes())


def load():
    metadata = bounded_json(HERE / "SOURCES.json")
    rows = [row for row in metadata["files"] if row["usage"] == "input"]
    require(len(rows) == 1, "one independent source")
    path = HERE.parents[1] / rows[0]["path"]
    require(path.stat().st_size <= 1_048_576, "source byte bound")
    raw = path.read_bytes()
    require(sha256(raw).hexdigest() == rows[0]["sha256"], "independent source binding")
    data = json.loads(raw)["recipes"]
    require(len(data) == 112, "112 independent source ports")
    by_port = {row["port"]: row["q"] for row in data}
    require(set(by_port) == set(range(112)), "independent port inventory")
    coordinates = [
        tuple((by_port[i] // (2**k)) % 2 for k in range(9)) for i in range(112)
    ]
    export = bounded_json(HERE / "SOURCE-EXPORT.json")
    require(
        len(export["files"]) == 2
        and {row["local_path"] for row in export["files"]}
        == {"PREDECESSOR13.json", "UPPER16.json"},
        "independent retained certificate names",
    )
    for row in export["files"]:
        raw = (HERE / row["local_path"]).read_bytes()
        require(sha256(raw).hexdigest() == row["sha256"], "independent export binding")
    old = bounded_json(HERE / "PREDECESSOR13.json")["orthonormal_groups"]
    return coordinates, old


def enumerate_groups(vectors):
    n = len(vectors)
    require(n <= 24 and all(len(v) == 9 for v in vectors), "coordinate domain")
    require(
        all(all(bit in (0, 1) for bit in v) and sum(v) % 2 for v in vectors),
        "binary unit coordinate vectors",
    )
    require(len(set(vectors)) == n, "distinct coordinate vectors")
    orthogonal = [
        [sum(a * b for a, b in zip(x, y, strict=True)) % 2 == 0 for y in vectors]
        for x in vectors
    ]
    level = [(i,) for i in range(n)]
    groups = []
    for length in range(2, min(8, n) + 1):
        following = []
        for prefix in level:
            for vertex in range(prefix[-1] + 1, n):
                if all(orthogonal[previous][vertex] for previous in prefix):
                    following.append((*prefix, vertex))
        level = following
        require(len(level) <= 100_000, "independent clique layer capacity")
        if length % 2 == 0:
            groups.extend(sum(2**v for v in group) for group in level)
    require(len(groups) <= 4096, "independent group capacity")
    return groups


def cover_exists(groups, n, bound):
    require(n <= 24 and 0 <= bound <= 4, "independent cover domain")
    require(len(groups) <= 4096, "independent cover group capacity")
    by_vertex = [
        [group for group in groups if group & (2**vertex)] for vertex in range(n)
    ]
    group_set = set(groups)
    stack = [((2**n) - 1, bound)]
    seen = set()
    for _ in range(MAX_STATES):
        if not stack:
            return False, len(seen)
        remaining, slots = stack.pop()
        if remaining == 0:
            return True, len(seen)
        if slots == 0 or remaining.bit_count() > 8 * slots:
            continue
        key = (remaining, slots)
        if key in seen:
            continue
        seen.add(key)
        if slots == 1:
            if remaining in group_set:
                return True, len(seen)
            continue
        choices = None
        for vertex in range(n):
            if remaining & (2**vertex):
                candidates = [
                    g
                    for g in by_vertex[vertex]
                    if g & remaining == g
                    and (remaining ^ g).bit_count() <= 8 * (slots - 1)
                ]
                if choices is None or len(candidates) < len(choices):
                    choices = candidates
        require(choices is not None, "nonempty remaining domain")
        stack.extend((remaining ^ group, slots - 1) for group in choices)
        require(len(stack) <= MAX_STATES, "independent worklist capacity")
    raise ValueError("independent search bound exhausted; result unknown")


def run():
    vectors, old = load()
    expected = bounded_json(HERE / "RESULT.json")["cases"]
    require(len(expected) == 78, "independent expected case inventory")
    states = []
    tail = [v for group in old[13:] for v in group]
    for index, removed in enumerate(combinations(range(13), 2)):
        vertices = sorted(tail + [v for k in removed for v in old[k]])
        groups = enumerate_groups([vectors[v] for v in vertices])
        histogram = {
            str(k): v for k, v in Counter(g.bit_count() for g in groups).items()
        }
        require(expected[index]["removed"] == list(removed), "independent case order")
        require(expected[index]["groups"] == histogram, "independent clique counts")
        exists, count = cover_exists(groups, 24, 4)
        require(not exists, "independent four-group cover found")
        states.append(count)
    print(
        "PASS_P112_INDEPENDENT_REPAIR cases=78 states="
        + str(sum(states))
        + " max_states="
        + str(max(states))
    )


if __name__ == "__main__":
    run()
