#!/usr/bin/env python3
"""Exact four-wire ADD distances. Charan ., with Codex assistance. Apache-2.0."""
import argparse
from collections import Counter, deque
from hashlib import sha256
import json
from pathlib import Path


def generate(output):
    identity = (1, 2, 4, 8)
    generators = [(d, s) for d in range(4) for s in range(4) if d != s]
    distance, previous = {identity: 0}, {}
    pending = deque([identity])
    while pending:
        state = pending.popleft()
        for d, s in generators:
            child = list(state)
            child[d] ^= child[s]
            child = tuple(child)
            if child not in distance:
                distance[child] = distance[state] + 1
                previous[child] = (state, [d, s])
                pending.append(child)
    labels = bytearray([255]) * 65536
    for rows, length in distance.items():
        labels[sum(r << (4 * i) for i, r in enumerate(rows))] = length
    gl2 = [(a, b) for a in range(1, 4) for b in range(1, 4) if a != b]
    endpoints = []
    for a, b in gl2:
        for c, d in gl2:
            rows = (a << 2, b << 2, c, d)
            current, reverse_word = rows, []
            while current != identity:
                current, gate = previous[current]
                reverse_word.append(gate)
            endpoints.append(dict(rows=list(rows), distance=distance[rows], word=reverse_word[::-1]))
    result = dict(schema="g20-isolated-exchange-distance/v1", invertible_states=len(distance),
        directed_edges=len(distance) * len(generators), levels=dict(sorted(Counter(distance.values()).items())),
        exchange_histogram=dict(sorted(Counter(x["distance"] for x in endpoints).items())),
        exchange_minimum=min(x["distance"] for x in endpoints),
        distance_table_sha256=sha256(labels).hexdigest(), endpoints=endpoints)
    output.mkdir(parents=True, exist_ok=True)
    (output / "distances.bin").write_bytes(labels)
    (output / "CERTIFICATE.json").write_text(json.dumps(result, indent=2) + "\n")
    print("GENERATED_GL4_EXCHANGE_CERTIFICATE", len(distance), "states")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="fresh output directory")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must not exist")
    generate(args.output)
