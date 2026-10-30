"""Exact preparation, independent graph distances and dirty operator replay.

Nick Petalas. Apache-2.0. Normal replay is read-only; --emit prints evidence.
"""

import argparse
import hashlib
import json
from itertools import product
from pathlib import Path

from compiler import (
    apply_coupling,
    move_pair,
    permutation_swaps,
    preparation,
    require,
)

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def strict_json(raw):
    require(len(raw) <= 65536, "JSON capacity exceeded")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    return json.loads(raw, object_pairs_hook=unique)


def authenticate():
    sources = strict_json((PACKAGE / "SOURCES.json").read_bytes())
    require(len(sources["files"]) == 3, "source inventory capacity")
    inputs = [row for row in sources["files"] if row["usage"] == "input"]
    require(len(inputs) == 1, "source inventory changed")
    for row in inputs:
        require(
            row["path"] == "research/q8-affine-dirty-compiler/README.md",
            "unexpected source path",
        )
        path = ROOT / row["path"]
        require(path.is_file() and not path.is_symlink(), "source missing or linked")
        require(
            not path.parent.is_symlink() and not path.parent.parent.is_symlink(),
            "source parent linked",
        )
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source drift")
        blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        require(blob == row["git_blob"], "source blob drift")
    return len(inputs)


def local_table():
    rows = []
    for ua, va, ub, vb in product(range(2), repeat=4):
        before = 2 * (ua + va + ub + vb) - ua * va - ub * vb
        after = 2 * ((ua ^ ub) + va + ub + (vb ^ va))
        after -= (ua ^ ub) * va + ub * (vb ^ va)
        change = after - before
        require(change >= -2, "potential drops by more than one")
        rows.append([ua, va, ub, vb, change])
    return rows


def graph_distances(roles):
    """Independent BFS on four coordinate colors; no distance formula used."""
    states = (1 << roles) * (1 << roles)
    distances = [-1] * states
    queue = [0] * states
    tail = 0
    for pivot in range(roles):
        state = (1 << pivot) | ((1 << pivot) << roles)
        distances[state] = 0
        queue[tail] = state
        tail += 1
    # Every reachable state has odd overlap, so there are at most states states.
    for head in range(states):
        if head == tail:
            break
        state = queue[head]
        u, v = state & ((1 << roles) - 1), state >> roles
        for a in range(roles):
            for b in range(roles):
                if a == b:
                    continue
                # Independent arithmetic update of the two colored sites.
                next_u = u ^ (1 << a) if u & (1 << b) else u
                next_v = v ^ (1 << b) if v & (1 << a) else v
                target = next_u | (next_v << roles)
                if distances[target] < 0:
                    distances[target] = distances[state] + 1
                    require(tail < states, "BFS capacity exhausted")
                    queue[tail] = target
                    tail += 1
    return distances, tail


def check_preparations():
    rows, transitions, improved = [], 0, 0
    digest = hashlib.sha256()
    for roles in range(1, 9):
        exact, reached = graph_distances(roles)
        count, maximum = 0, 0
        for u in range(1, 1 << roles):
            for v in range(1, 1 << roles):
                if (u & v).bit_count() % 2 != 1:
                    continue
                pivot, program = preparation(roles, u, v)
                require(exact[u | (v << roles)] == len(program), "BFS minimum mismatch")
                old_round_trip = 2 * (u.bit_count() + v.bit_count() - 2)
                require(
                    old_round_trip - 2 * len(program) == (u & v).bit_count() - 1,
                    "old/new scalar invoice mismatch",
                )
                a, b = u, v
                for destination, source in program:
                    a, b = move_pair(a, b, destination, source)
                    transitions += 1
                require(a == b == 1 << pivot, "conjugation endpoint mismatch")
                require(2 * len(program) <= 3 * (roles - 1), "uniform bound")
                count += 1
                maximum = max(maximum, len(program))
                improved += (u & v).bit_count() >= 3
                digest.update(f"{roles},{u},{v},{len(program)}\n".encode())
        require(
            count == reached == ((1 << roles) - 1) * (1 << (roles - 1)),
            "incomplete idempotent graph",
        )
        require(maximum == (3 * (roles - 1)) // 2, "maximum is not sharp")
        rows.append([roles, count, maximum])
    # Capacity endpoint and a large odd shared support, without a large BFS.
    for roles in (63, 64, 255, 256):
        u, v = (1 << roles) - 1, (1 << (roles - (roles % 2 == 0))) - 1
        pivot, program = preparation(roles, u, v)
        for destination, source in program:
            u, v = move_pair(u, v, destination, source)
        require(u == v == 1 << pivot, "large preparation endpoint")
    return {
        "rows": rows,
        "transitions": transitions,
        "improved_cases": improved,
        "distance_sha256": digest.hexdigest(),
        "large_cases": 4,
    }


def hamilton(label, point):
    left, right = [0] * 4, [0] * 4
    left[label & 3] = -1 if label & 4 else 1
    right[point & 3] = -1 if point & 4 else 1
    a, b, c, d = left
    e, f, g, h = right
    value = (
        a * e - b * f - c * g - d * h,
        a * f + b * e + c * h - d * g,
        a * g - b * h + c * e + d * f,
        a * h + b * g - c * f + d * e,
    )
    require(sum(abs(x) for x in value) == 1, "Hamilton unit")
    index = next(k for k in range(4) if value[k])
    return index | (4 if value[index] < 0 else 0)


def dirty_fixture(roles, u, v, label, payload=1):
    original = [
        [1 << (role * 8 * payload + cell) for cell in range(8 * payload)]
        for role in range(roles)
    ]
    expected = [row[:] for row in original]
    for point in range(8):
        for cell in range(payload):
            source, target = (
                point * payload + cell,
                hamilton(label, point) * payload + cell,
            )
            packet = 0
            for role in range(roles):
                if v >> role & 1:
                    packet ^= original[role][source]
            for role in range(roles):
                if u >> role & 1:
                    expected[role][source] ^= packet
                    expected[role][target] ^= packet
    actual = apply_coupling([row[:] for row in original], u, v, label, payload)
    require(actual == expected, "dirty Q8 operator mismatch")
    inverse = label if label in (0, 4) else label ^ 4
    require(
        apply_coupling(actual, u, v, inverse, payload) == original,
        "dirty Q8 inverse mismatch",
    )
    return 8 * roles * payload


def check_operators():
    cases, columns = 0, 0
    for roles in range(1, 7):
        for u in range(1, 1 << roles):
            for v in range(1, 1 << roles):
                if (u & v).bit_count() % 2 != 1:
                    continue
                for label in range(8):
                    columns += dirty_fixture(roles, u, v, label)
                    cases += 1
    for payload in (2, 3, 7):
        for label in range(8):
            columns += dirty_fixture(4, 7, 7, label, payload)
            cases += 1
    return {"cases": cases, "dirty_columns": columns, "inverse_checked": True}


def compute():
    _, program = preparation(3, 7, 7)
    swaps = permutation_swaps(1)
    old_program = ((1, 0), (2, 0), (0, 1), (0, 2))
    invoice = {
        "old": 8 * 2 * len(old_program) + 3 * len(swaps),
        "new": 8 * 2 * len(program) + 3 * len(swaps),
        "payload": 1,
    }
    require(invoice == {"old": 82, "new": 66, "payload": 1}, "sample invoice")
    return {
        "status": "PASS_OPTIMAL_DIRTY_PREPARATION",
        "source_inputs": authenticate(),
        "local_transition_table": local_table(),
        "preparations": check_preparations(),
        "operators": check_operators(),
        "three_role_noncentral_bit_xors": invoice,
        "claim": "local compiler only",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--receipt", type=Path, default=PACKAGE / "RESULT.json")
    args = parser.parse_args()
    result = compute()
    if not args.emit:
        expected = strict_json(args.receipt.read_bytes())
        require(
            json.dumps(expected, sort_keys=True) == json.dumps(result, sort_keys=True),
            "typed receipt mismatch",
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
