"""Literal programs and dirty-state controls. Nick Petalas. Apache-2.0."""

import json
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import census
from verify import check_sources, read_json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def skeleton(word, cut, ports):
    result = [("T", 0)]
    for i in range(len(word) + 1):
        if i == cut:
            result.append(("T", 0))
        if i < len(word):
            result.append(("B", word[i], (ports >> i) & 1))
    return result


def observations(word, n):
    roots = [1 << n, 2 << n]
    result = [(0, p, roots[p]) for p in range(2)]
    for i, op in enumerate(word):
        if op[0] == "T":
            roots[op[1]] ^= roots[1 - op[1]]
        else:
            roots[op[2]] ^= 1 << op[1]
        result.extend((i + 1, p, roots[p]) for p in range(2))
    return result


def complete(word, n, three=False):
    available = observations(word, n)
    pairs = {}
    for target in range(1, 1 << n):
        for reads in combinations(available, 2):
            if reads[0][2] ^ reads[1][2] == target:
                pairs[target] = reads
                break
    if three:
        missing = [m for m in range(1, 1 << n) if m not in pairs]
        if len(missing) != 1:
            return None
        target = missing[0]
        for reads in combinations(available, 3):
            if reads[0][2] ^ reads[1][2] ^ reads[2][2] == target:
                pairs[target] = reads
                break
    if len(pairs) != (1 << n) - 1:
        return None
    at = [[] for _ in range(len(word) + 1)]
    for target, reads in sorted(pairs.items()):
        for cut, port, _ in reads:
            at[cut].append(("A", target, port))
    result = []
    for cut, reads in enumerate(at):
        result.extend(reads)
        if cut < len(word):
            result.append(word[cut])
    return result


def positive(three):
    for word in census.source_words(2, not three):
        for cut in range(len(word) + 1):
            for ports in census.restoring_ports(word, cut, 2, not three):
                compiled = complete(skeleton(word, cut, ports), 2, three)
                if compiled is not None:
                    return compiled
    raise ValueError("no small positive control")


def formal(word, n):
    roots = [1 << n, 2 << n]
    outputs = [0] * (1 << n)
    for op in word:
        if op[0] == "T":
            roots[op[1]] ^= roots[1 - op[1]]
        elif op[0] == "B":
            roots[op[2]] ^= 1 << op[1]
        elif op[0] == "A":
            outputs[op[1]] ^= roots[op[2]]
        else:
            raise ValueError("unknown call")
    return roots == [1 << n, 2 << n] and outputs == list(range(1 << n))


def maps_for(n, width):
    from random import Random

    random = Random(20261018 + width)
    maps = {}
    for kind, indices in (("B", range(n)), ("A", range(1, 1 << n))):
        for index in indices:
            maps[kind, index] = tuple(
                random.randrange(1 << width) for _ in range(width)
            )
    if width >= 2:
        maps["B", 0] = (1,) + (0,) * (width - 1)
        maps["A", 1] = (3, 2, *(1 << i for i in range(2, width)))
        a, b = maps["A", 1], maps["B", 0]
        census.require(
            apply(a, apply(b, 2)) != apply(b, apply(a, 2)), "noncommuting fixture"
        )
    return maps


def apply(matrix, value):
    return sum(((row & value).bit_count() & 1) << i for i, row in enumerate(matrix))


def execute(word, state, n, maps):
    rows = list(state)
    for op in word:
        if op[0] == "T":
            rows[n + op[1]] ^= rows[n + 1 - op[1]]
        elif op[0] == "B":
            rows[n + op[2]] ^= apply(maps["B", op[1]], rows[op[1]])
        else:
            rows[n + 1 + op[1]] ^= apply(maps["A", op[1]], rows[n + op[2]])
    return rows


def expected(state, n, maps):
    rows = list(state)
    for target in range(1, 1 << n):
        value = 0
        for source in range(n):
            if target & (1 << source):
                value ^= apply(maps["B", source], state[source])
        rows[n + 1 + target] ^= apply(maps["A", target], value)
    return rows


def dense(word, n):
    count = 0
    rows = n + 1 + (1 << n)
    for width in (1, 2, 3):
        maps = maps_for(n, width)
        for column in range(rows * width + 1):
            state = [0] * rows
            if column < rows * width:
                state[column // width] = 1 << (column % width)
            else:
                state = [(i * 3 + 1) % (1 << width) for i in range(rows)]
            forward = execute(word, state, n, maps)
            census.require(forward == expected(state, n, maps), "dense dirty endpoint")
            census.require(
                execute(reversed(word), forward, n, maps) == state, "literal inverse"
            )
            count += 1
    return count


def run():
    check_sources()
    source = read_json(ROOT / "research/universal-connector-boundary/CERTIFICATE.json")[
        "schedules"
    ]["five_extra_source"]
    old = [
        (kind, source["rows"][index] if kind == "A" else index, 0)
        for kind, index in source["word"]
    ]
    coupled = read_json(
        ROOT / "research/bidirectional-five-source-connector/EVIDENCE.json"
    )["witness"]["complete_word"]
    census.require(len(old) == 74 and len(coupled) == 78, "witness size contract")
    fixtures = [(positive(True), 2), (positive(False), 2), (old, 5), (coupled, 5)]
    rejected = 0
    pairs = 0
    for word, n in fixtures:
        census.require(formal(word, n), "positive formal endpoint")
        pairs += dense(word, n)
        for i in range(len(word)):
            census.require(
                not formal(word[:i] + word[i + 1 :], n), "omitted call accepted"
            )
            changed = [list(op) for op in word]
            changed[i][-1] ^= 1
            census.require(not formal(changed, n), "wrong port/direction accepted")
            rejected += 2
    for bad in (True, 0, 6):
        try:
            census.census(bad, False)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("out-of-domain census accepted")
    return {
        "status": "PASS_DIRTY_CONNECTOR_CONTROLS",
        "fixtures": len(fixtures),
        "dense_forward_inverse_pairs": pairs,
        "rejected": rejected,
        "small_positive_words": [fixtures[0][0], fixtures[1][0]],
    }


if __name__ == "__main__":
    observed = run()
    expected = read_json(HERE / "CHECKS.json")["dirty_controls"]
    census.require(
        json.dumps(observed, sort_keys=True) == json.dumps(expected, sort_keys=True),
        "dirty control receipt mismatch",
    )
    print(json.dumps(observed, indent=2, sort_keys=True))
