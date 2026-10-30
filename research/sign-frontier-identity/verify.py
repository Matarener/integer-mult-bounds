"""Exact finite corroboration. Produced by Nick Petalas. Apache-2.0."""

import hashlib
import importlib.util
import itertools
import json
from fractions import Fraction as F
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def load_solver():
    spec = importlib.util.spec_from_file_location("sign_frontier_solver", PACKAGE / "solver.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def literal(roles, word, witness):
    """Separate column-vector interpreter, without the solver's row updates."""
    columns = []
    for column in range(roles):
        values = [F(row == column) for row in range(roles)]
        for gate in word:
            sign = -1 if gate.sign is not None and (witness >> gate.sign) & 1 else 1
            if gate.kind == "ADD":
                values[gate.dst] += gate.coefficient * values[gate.src]
            elif gate.kind == "QUERY":
                values[gate.dst] += gate.coefficient * sign * values[gate.src]
            elif gate.kind == "APPLY":
                values[gate.dst] *= sign
            else:
                values[gate.dst], values[gate.src] = values[gate.src], values[gate.dst]
        columns.append(values)
    return tuple(columns[j][i] for i in range(roles) for j in range(roles))


def exhaustive_check(solver, roles, word):
    labels = sorted({gate.sign for gate in word if gate.sign is not None})
    require(len(labels) <= 8, "exhaustive sign limit")
    good, count = True, 0
    for signs in itertools.product((0, 1), repeat=len(labels)):
        witness = sum(bit << label for bit, label in zip(signs, labels))
        good &= literal(roles, word, witness) == solver.identity(roles)
        count += 1
    result = solver.decide(roles, word)
    require(result["identity"] == good, "identity verdict differs from exhaustive columns")
    if not good:
        require(literal(roles, word, result["witness"]) != solver.identity(roles), "invalid witness")
    dimension = roles * roles + 1
    require(result["max_basis"] <= dimension, "basis capacity")
    require(result["max_states"] <= 2 ** result["frontier"], "state capacity")
    require(result["candidates"] <= len(word) * 2 ** (result["frontier"] + 1) * dimension,
            "candidate bound")
    return count


def small_words(solver):
    gate = solver.Gate
    alphabet = (gate("ADD", 0, 1, F(1, 2)), gate("ADD", 1, 0, F(-2)),
                gate("QUERY", 0, 1, F(1), 0), gate("QUERY", 1, 0, F(-1, 2), 1),
                gate("APPLY", 0, sign=0), gate("SWAP", 0, 1))
    words, assignments = 0, 0
    for length in range(5):
        for word in itertools.product(alphabet, repeat=length):
            assignments += exhaustive_check(solver, 2, word)
            words += 1
    return words, assignments


def structured_words(solver):
    gate = solver.Gate
    words, assignments = 0, 0
    for roles in (2, 3, 5):
        for seed in range(24):
            prefix = tuple(gate("QUERY", (seed + j) % roles, (seed + j + 1) % roles,
                                F((-1) ** j, 1 + (j % 3)), (j * 3 + seed) % 5)
                           for j in range(8))
            for word in (prefix, prefix + solver.inverse(prefix),
                         prefix + solver.inverse(prefix) + (gate("APPLY", 0, sign=5),)):
                assignments += exhaustive_check(solver, roles, word)
                words += 1
    return words, assignments


def large_frontiers(solver):
    gate = solver.Gate
    once = tuple(gate("QUERY", 1, 0, F(1), j) for j in range(128))
    once += (gate("ADD", 1, 0, F(-128)),)
    negative = solver.decide(5, once, frontier_limit=0)
    require(not negative["identity"], "lost non-all-plus branch")
    require(literal(5, once, 0) == solver.identity(5), "all-plus control")
    require(literal(5, once, negative["witness"]) != solver.identity(5), "large witness")
    require(negative["max_basis"] == 2, "rank-two affine prefix family")
    paired = tuple(gate("QUERY", 1, 0, F(sign, 3), j)
                   for j in range(128) for sign in (1, -1))
    positive = solver.decide(5, paired, frontier_limit=1)
    require(positive["identity"] and positive["frontier"] == 1, "repeated-sign cancellation")
    crossing = tuple(gate("QUERY", 1, 0, F(1), j) for j in range(8))
    crossing += tuple(gate("QUERY", 1, 0, F(-1), j) for j in range(8))
    crossed = solver.decide(5, crossing)
    require(crossed["identity"] and crossed["max_states"] == 256, "full frontier occupancy")
    return {"once_128": negative, "paired_128": positive, "crossing_8": crossed}


def expect_rejection(callback):
    try:
        callback()
    except ValueError:
        return 1
    raise RuntimeError("invalid input accepted")


def controls(solver):
    gate = solver.Gate
    cases = ((0, ()), (True, ()), (6, ()), (2, []),
             (2, (gate("BAD", 0, 1),)), (2, (gate("ADD", 0, 0),)),
             (2, (gate("QUERY", 0, 1),)), (2, (gate("ADD", 0, 1, F(1), 0),)),
             (2, (gate("APPLY", 0, 1, sign=0),)),
             (2, (gate("SWAP", 0, 1, F(2)),)),
             (2, (gate("QUERY", 0, 1, F(1), -1),)),
             (2, (gate("ADD", 0, 1, 0.5),)),
             (2, (gate("ADD", 0, 1, F(1 << 65)),)),
             (2, (gate("ADD", 2, 0),)), (2, (gate("APPLY", True, sign=0),)),
             (2, (gate("ADD", 0, 1),) * 4097))
    count = sum(expect_rejection(lambda r=r, w=w: solver.decide(r, w)) for r, w in cases)
    repeated = (gate("APPLY", 0, sign=0),) * 2
    count += expect_rejection(lambda: solver.decide(2, repeated, frontier_limit=0))
    count += expect_rejection(lambda: solver.decide(2, (), frontier_limit=9))
    scalar = tuple(gate("APPLY", j, sign=0) for j in range(5))
    result = solver.decide(5, scalar)
    require(not result["identity"] and result["witness"] == 1, "homogeneous scalar control")
    require(solver.decide(2, repeated)["identity"], "repeated signs must agree")
    require(not solver.decide(2, (repeated[0], gate("APPLY", 0, sign=1)))["identity"],
            "independent signs must branch")
    return count, 3


def boundary_fixtures(solver):
    gate = solver.Gate
    fixtures = ((1, ()), (1, (gate("APPLY", 0, sign=4095),) * 2),
                (5, (gate("SWAP", 0, 4),) * 4096),
                (2, (gate("ADD", 0, 1, F((1 << 64) - 1)),
                     gate("ADD", 0, 1, F(-((1 << 64) - 1))))))
    for roles, word in fixtures:
        require(solver.decide(roles, word)["identity"], "accepted capacity boundary")
    mixed = (gate("ADD", 0, 1, F(2, 3)), gate("QUERY", 2, 0, F(-7, 5), 3),
             gate("APPLY", 1, sign=1), gate("SWAP", 1, 4))
    exhaustive_check(solver, 5, mixed + solver.inverse(mixed))
    require(solver.decide(5, mixed + solver.inverse(mixed))["identity"], "mixed inverse")
    return len(fixtures) + 1


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            require(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "source input hash mismatch: " + row["path"])


def main():
    authenticate()
    solver = load_solver()
    small, small_assignments = small_words(solver)
    structured, structured_assignments = structured_words(solver)
    large = large_frontiers(solver)
    rejected, semantic = controls(solver)
    boundaries = boundary_fixtures(solver)
    result = {"status": "PASS_SIGN_FRONTIER_IDENTITY", "small_words": small,
              "small_assignments": small_assignments, "structured_words": structured,
              "structured_assignments": structured_assignments, "large_fixtures": large,
              "input_rejections": rejected, "semantic_controls": semantic,
              "capacity_and_inverse_fixtures": boundaries,
              "package_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(PACKAGE.iterdir()) if p.is_file()}}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
