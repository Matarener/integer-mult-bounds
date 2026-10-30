#!/usr/bin/env python3
"""Replay new two-clique relay fixtures, not predecessor word results.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

import gzip
import hashlib
import itertools
import json
from pathlib import Path
import random

from model import (annihilator, check_network, dimension, image, in_rows,
                   packet, require, row_basis, row_basis_binary, span, tags_for)


PACKAGE = Path(__file__).resolve().parent
PORTS = (73, 239, 336, 502, 81, 247, 328, 494)


def all_frames():
    universe = span([81, 502, 239, 73])
    frames = {frozenset({0})}
    for _ in range(4):
        fresh = set(frames)
        for frame in frames:
            basis = row_basis_binary(frame)
            for x in universe - frame:
                fresh.add(span([*basis, x]))
        frames = fresh
    result = sorted(frames, key=lambda f: (len(f), tuple(sorted(f))))
    require(len(result) == 67, "all four-dimensional binary subspaces")
    return result


def check_geometry(frames):
    root = PACKAGE.parents[1]
    path = root / "research/p104-helper-subspace-splits/WORD.json.gz"
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        source_ports = json.load(handle)["ports"]
    require(set(PORTS) <= set(source_ports), "fixture ports belong to the source")
    tags = tags_for(PORTS)
    intervals = local_tests = reader_tests = 0
    for gather in frames:
        before = annihilator(image(gather, PORTS, tags))
        for i, port in enumerate(PORTS):
            if port in gather:
                local_tests += 1
                unit = tuple(int(j == i) for j in range(8))
                require(all(not any(packet(unit, tags, z)) for z in before),
                        "all local input generators lie in the rational lift")
            if all(not (port & x).bit_count() % 2 for x in gather):
                reader_tests += 1
                z = (1, 0) if tags[i] == 1 else (0, 1)
                require(in_rows(z, row_basis(list(before), 2)),
                        "all binary readers annihilate the rational lift")
        for landing in frames:
            if landing <= gather:
                intervals += 1
                after = row_basis(list(annihilator(image(landing, PORTS, tags))), 2)
                require(all(in_rows(z, after) for z in before), "lift inclusion")
                require(len(after) - len(before) <=
                        dimension(gather) - dimension(landing), "all gap bounds")
    return {"frames": len(frames), "nested_pairs": intervals,
            "local_generators": local_tests, "reader_tests": reader_tests}


def attaining_network(staged):
    moves = []
    output = [[0] * (8 if staged else 4) for _ in PORTS]
    for i in range(4):
        local = tuple(int(j in (i, i + 4)) for j in range(8))
        gather = span([PORTS[i], PORTS[i + 4]])
        middle = span([PORTS[i] ^ PORTS[i + 4]]) if staged else frozenset({0})
        moves.append((gather, middle, local, (0,) * len(moves)))
        if staged:
            parents = [0] * len(moves)
            parents[-1] = 1
            moves.append((middle, frozenset({0}), (0,) * 8, tuple(parents)))
        output[i][len(moves) - 1] = 1
        output[i + 4][len(moves) - 1] = 1
    return moves, output


def check_attainers():
    results = []
    identity = [tuple(int(i == j) for j in range(8)) for i in range(8)]
    for staged in (False, True):
        moves, output = attaining_network(staged)
        result = check_network(PORTS, moves, output)
        require(result.pop("shadow") == identity, "all eight independent target rows")
        require(result == {"paid": 8, "effective_paid": 8,
                           "shadow_rank": 8, "debt_dimension": 8}, "sharp invoice")
        endpoint = [[int(i % 4 == j % 4) for j in range(8)] for i in range(8)]
        require(literal_endpoint(moves, output) == endpoint, "complete source endpoint")
        require(len(row_basis(endpoint, 8)) == 4, "rank-four completion control")
        results.append({"moves": len(moves), **result, "completion_rank": 4})
    return results


def literal_endpoint(moves, output):
    values = []
    for _, _, local, parents in moves:
        values.append(tuple(local[i] + sum(a * v[i] for a, v in zip(parents, values))
                            for i in range(8)))
    return [[sum(a * v[i] for a, v in zip(row, values)) for i in range(8)]
            for row in output]


def check_networks(frames):
    rng = random.Random(103)
    tags = tags_for(PORTS)
    intervals = [(g, l) for g in frames for l in frames if l < g]
    nonzero_relays = branches = mixed = 0
    for _ in range(512):
        moves, uses = [], [0] * 16
        for count in range(16):
            gather, landing = intervals[rng.randrange(len(intervals))]
            local = tuple(rng.choice((-1, 0, 1)) if p in gather else 0 for p in PORTS)
            parents = tuple(rng.choice((-1, 0, 1)) if old[1] <= gather else 0
                            for old in moves)
            nonzero_relays += sum(bool(x) for x in parents)
            mixed += sum(bool(x) for x in parents) >= 2
            for i, x in enumerate(parents):
                if x:
                    uses[i] += 1
            moves.append((gather, landing, local, parents))
            require(len(moves) == count + 1, "fixed network bound")
        branches += sum(x >= 2 for x in uses)
        output = [[rng.choice((-1, 0, 1))
                   if all(not (p & x).bit_count() % 2 for x in move[1]) else 0
                   for move in moves] for p in PORTS]
        checked = check_network(PORTS, moves, output)
        endpoint = literal_endpoint(moves, output)
        direct = [tuple(endpoint[j][i] * int(tags[i] == tags[j]) for i in range(8))
                  for j in range(8)]
        require(checked["shadow"] == direct, "literal endpoint replay")
    require(min(nonzero_relays, branches, mixed) > 0, "relay coverage is nonvacuous")
    return {"networks": 512, "moves": 8192, "nonzero_parent_edges": nonzero_relays,
            "branching_parents": branches, "mixed_parent_moves": mixed}


def check_rank_oracle():
    for bits in itertools.product((0, 1), repeat=9):
        a, b, c, d, e, f, g, h, i = bits
        determinant = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
        rows = [bits[0:3], bits[3:6], bits[6:9]]
        minors = [rows[r][x] * rows[s][y] - rows[r][y] * rows[s][x]
                  for r, s in itertools.combinations(range(3), 2)
                  for x, y in itertools.combinations(range(3), 2)]
        expected = 3 if determinant else 2 if any(minors) else int(any(bits))
        require(len(row_basis(rows, 3)) == expected, "independent minor rank oracle")
    return 512


def must_reject(moves, output, message):
    try:
        check_network(PORTS, moves, output)
    except ValueError as error:
        require(message in str(error), "control failed for the intended reason")
    else:
        raise ValueError("invalid network accepted: " + message)


def check_controls():
    moves, output = attaining_network(True)
    bad = list(moves)
    g, l, local, parents = bad[1]
    bad[1] = (g, l, (1,) + (0,) * 7, parents)
    must_reject(bad, output, "local source availability")
    bad = list(moves)
    g, l, local, parents = bad[0]
    bad[0] = (g, span([PORTS[0]]), local, parents)
    must_reject(bad, output, "ancestor arrival availability")
    bad_output = [list(row) for row in output]
    bad_output[0][0] = 1
    must_reject(moves, bad_output, "receiver availability")
    bad = list(moves)
    g, _, local, parents = bad[0]
    bad[0] = (g, g, local, parents)
    must_reject(bad, output, "confined strict descent")
    bad = list(moves)
    g, l, local, parents = bad[0]
    bad[0] = (g | {1}, l, local, parents)
    must_reject(bad, output, "confined strict descent")
    pair = [moves[0], moves[1]]
    pair_output = [[int(j == 1 and i in (0, 4)) for j in range(2)] for i in range(8)]
    result = check_network(PORTS, pair, pair_output)
    require(result["shadow_rank"] == 2 and dimension(pair[1][0]) == 1,
            "shared-cost counterexample to per-move rank billing")
    return {"rejected_networks": 5, "per_move_counterexample": True}


def main():
    frames = all_frames()
    result = {"status": "PASS_P104_TWO_CLIQUE_RELAY_FLOOR", "claim_type": "scoped-proof",
              "geometry": check_geometry(frames), "attainers": check_attainers(),
              "relay_fixtures": check_networks(frames), "rank_oracle_cases": check_rank_oracle(),
              "controls": check_controls(), "no_new_kappa": True}
    result["package_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(PACKAGE.iterdir()) if p.is_file()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
