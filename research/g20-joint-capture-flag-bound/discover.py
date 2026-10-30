#!/usr/bin/env python3
"""Optional deterministic flag-constrained matroid partition search.

Outputs to the requested scratch path. Verification never calls this search.
Jerry Chen (@CubeJerry), with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import deque
import gzip
import importlib.util
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("g20_flag_model", HERE / "model.py")
model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(model)


def discover(data, seconds):
    vectors = data["vectors"]
    colors = [set() for _ in range(108)]
    bases = [{} for _ in colors]
    partial = sum(1 << h for h in data["partial"])
    two = sum(1 << h for h in data["free_two"])
    deadline = time.monotonic() + seconds

    def limit(x):
        return 64 if vectors[x] & partial else 92 if vectors[x] & two else 108

    def reduce(index, value):
        combination = 0
        basis = bases[index]
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                return value, combination
            row, support = basis[pivot]
            value ^= row
            combination ^= support
        return value, combination

    def add(index, x):
        value, combination = reduce(index, vectors[x])
        model.require(value != 0, "discovery inserted dependence")
        bases[index][value.bit_length() - 1] = (value, combination ^ (1 << x))
        colors[index].add(x)

    def rebuild(index):
        members = sorted(colors[index])
        colors[index], bases[index] = set(), {}
        for x in members:
            add(index, x)

    remaining = data["multiplicities"].copy()
    for index in range(108):
        for x in sorted(remaining, key=lambda x: (limit(x), -remaining[x], vectors[x])):
            if index < limit(x) and reduce(index, vectors[x])[0]:
                add(index, x)
                remaining[x] -= 1
        remaining = +remaining
    print("Greedy remainder:", sum(remaining.values()), flush=True)
    steps = 0
    for root in sorted(remaining, key=lambda x: (limit(x), -remaining[x], vectors[x])):
        for _ in range(remaining[root]):
            previous, queue, found = {root: None}, deque([root]), None
            while queue and found is None:
                if time.monotonic() > deadline:
                    raise TimeoutError("search stopped; no impossibility conclusion")
                x = queue.popleft()
                for index in range(limit(x)):
                    if x in colors[index]:
                        continue
                    value, support = reduce(index, vectors[x])
                    if value:
                        found = (x, index)
                        break
                    while support:
                        bit = support & -support
                        y = bit.bit_length() - 1
                        if y not in previous:
                            previous[y] = (x, index)
                            queue.append(y)
                        support ^= bit
            model.require(found is not None, "search exhausted; no mathematical obstruction claimed")
            x, index = found
            colors[index].add(x)
            changed = {index}
            while previous[x] is not None:
                y, index = previous[x]
                colors[index].remove(x)
                colors[index].add(y)
                changed.add(index)
                x = y
            for index in sorted(changed):
                rebuild(index)
            steps += 1
            if steps % 200 == 0:
                print("Augmentations:", steps, flush=True)
    certificate = {"schema": "g20-first-read-flag-partition/v1",
                   "limits": [64, 92, 108], "groups": [sorted(c) for c in colors]}
    model.check_partition(data, certificate)
    return certificate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--seconds", type=int, default=1200)
    args = parser.parse_args()
    model.require(not args.output.exists(), "refuse to overwrite an existing artifact")
    data = model.census(*model.inputs())
    certificate = discover(data, args.seconds)
    raw = (json.dumps(certificate, separators=(",", ":")) + "\n").encode()
    args.output.write_bytes(gzip.compress(raw, mtime=0))
    print("WROTE_VERIFIED_FLAG_PARTITION", args.output)


if __name__ == "__main__":
    main()
