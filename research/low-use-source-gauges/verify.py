"""Exact finite controls for the low-use source-gauge theorem; no writes."""

from __future__ import annotations

import hashlib
import heapq
import itertools
import json
import platform
from fractions import Fraction
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
MAX_ROLES = 4
MAX_EDGES = 4


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def power(exponent: int) -> Fraction:
    require(type(exponent) is int and abs(exponent) <= 32, "bad exponent")
    return Fraction(2**exponent) if exponent >= 0 else Fraction(1, 2**-exponent)


def tariff(value: Fraction) -> int:
    require(value != 0 and value.denominator.bit_count() == 1, "not dyadic")
    numerator = abs(value.numerator)
    trailing = (numerator & -numerator).bit_length() - 1
    odd = numerator >> trailing
    valuation = trailing - (value.denominator.bit_length() - 1)
    return 2 * (2 + odd.bit_length() + odd.bit_count() + abs(valuation))


def validate(edges: tuple, sources: int, roles: int) -> None:
    require(1 <= sources < roles <= MAX_ROLES, "bad role counts")
    require(len(edges) <= MAX_EDGES, "too many edges")
    for source, target, odd, valuation in edges:
        require(0 <= source < sources <= target < roles, "not bipartite")
        require(type(odd) is int and odd != 0 and odd % 2 != 0, "bad odd part")
        require(type(valuation) is int and abs(valuation) <= 8, "bad valuation")


def identity(size: int) -> list[list[Fraction]]:
    return [[Fraction(i == j) for j in range(size)] for i in range(size)]


def compile_word(edges: tuple, events: list, sources: int, roles: int) -> tuple:
    validate(edges, sources, roles)
    require(len(events) <= 1000, "event capacity")
    gauges = [0] * roles
    used = [0] * len(edges)
    physical = []
    cost = 0
    for kind, index, delta in events:
        if kind == "S":
            require(0 <= index < roles, "scale role")
            coefficient = power(delta)
            gauges[index] += delta
            physical.append(("S", index, index, coefficient))
            cost += 2 * abs(delta)
        else:
            require(kind == "A" and 0 <= index < len(edges), "unknown event")
            source, target, odd, valuation = edges[index]
            coefficient = odd * power(valuation + gauges[target] - gauges[source])
            physical.append(("A", target, source, coefficient))
            used[index] += 1
            cost += tariff(coefficient)
    require(gauges == [0] * roles, "gauge not restored")
    require(used == [1] * len(edges), "contribution multiplicity")
    return physical, cost


def replay(physical: list, roles: int) -> list:
    matrix = identity(roles)
    require(len(physical) <= 1000, "physical word capacity")
    for kind, target, source, coefficient in physical:
        if kind == "S":
            matrix[target] = [coefficient * x for x in matrix[target]]
        else:
            matrix[target] = [x + coefficient * y
                              for x, y in zip(matrix[target], matrix[source])]
    return matrix


def check_endpoint(edges: tuple, events: list, sources: int, roles: int) -> int:
    physical, cost = compile_word(edges, events, sources, roles)
    expected = identity(roles)
    inverse_transpose = identity(roles)
    for source, target, odd, valuation in edges:
        coefficient = odd * power(valuation)
        expected[target][source] += coefficient
        inverse_transpose[source][target] -= coefficient
    require(replay(physical, roles) == expected, "wrong full endpoint")
    dual = [(kind, source if kind == "A" else target,
             target if kind == "A" else source,
             -q if kind == "A" else 1 / q)
            for kind, target, source, q in physical]
    require(replay(dual, roles) == inverse_transpose, "wrong dual endpoint")
    dual_cost = sum(tariff(q) if kind == "A" else 2 * abs(
        q.numerator.bit_length() - q.denominator.bit_length())
        for kind, _, _, q in dual)
    require(dual_cost == cost, "dual tariff differs")
    return cost


def interval_cost(edges: tuple, roles: int) -> int:
    total = sum(tariff(odd * power(v)) - 2 * abs(v)
                for _, _, odd, v in edges)
    for target in range(roles):
        values = [-v for _, t, _, v in edges if t == target]
        points = sorted({0, *values})
        candidates = [4 * (high - low) + 2 * sum(
            max(low - s, 0, s - high) for s in values)
            for low in points for high in points if low <= 0 <= high]
        total += min(candidates)
    return total


def relax(state: tuple, value: int, event: tuple, previous: tuple,
          distances: dict, parents: dict, heap: list) -> None:
    if value < distances.get(state, 10**9):
        distances[state] = value
        parents[state] = (previous, event)
        heapq.heappush(heap, (value, state))


def shortest(edges: tuple, sources: int, roles: int, coupled: bool) -> tuple:
    """Independent bounded gauge-state oracle, gauges in {-1,0,1}."""
    validate(edges, sources, roles)
    require(all(abs(edge[3]) <= 1 for edge in edges), "oracle valuation")
    start = (0, (0,) * roles)
    goal = ((1 << len(edges)) - 1, start[1])
    distances, parents, heap = {start: 0}, {}, [(0, start)]
    capacity = (1 << len(edges)) * 3**roles
    pop_limit = 1 + capacity * (2 * roles + len(edges))
    for _ in range(pop_limit):
        require(bool(heap), "oracle exhausted")
        value, state = heapq.heappop(heap)
        if value != distances[state]:
            continue
        if state == goal:
            return value, reconstruct(parents, start, goal, capacity)
        mask, gauges = state
        for role in range(0 if coupled else sources, roles):
            for delta in (-1, 1):
                if abs(gauges[role] + delta) <= 1:
                    changed = list(gauges)
                    changed[role] += delta
                    relax((mask, tuple(changed)), value + 2,
                          ("S", role, delta), state, distances, parents, heap)
        for index, (source, target, odd, valuation) in enumerate(edges):
            if not (mask >> index) & 1:
                cost = tariff(odd * power(valuation + gauges[target] - gauges[source]))
                relax((mask | (1 << index), gauges), value + cost,
                      ("A", index, 0), state, distances, parents, heap)
    raise ValueError("oracle pop bound")


def reconstruct(parents: dict, start: tuple, goal: tuple, capacity: int) -> list:
    events = []
    state = goal
    for _ in range(capacity):
        if state == start:
            return list(reversed(events))
        state, event = parents[state]
        events.append(event)
    raise ValueError("parent path bound")


def matrix_census() -> dict:
    count = 0
    pairs = tuple(itertools.product(range(2), range(2, 4)))
    for options in itertools.product((None, -1, 0, 1), repeat=4):
        edges = tuple((source, target, (-3 if i % 2 else 1), v)
                      for i, ((source, target), v) in enumerate(zip(pairs, options))
                      if v is not None)
        coupled, events = shortest(edges, 2, 4, True)
        fixed, _ = shortest(edges, 2, 4, False)
        expected = interval_cost(edges, 4)
        require(coupled == fixed == expected, "low-use optimum differs")
        require(check_endpoint(edges, events, 2, 4) == coupled, "cost mismatch")
        normalized = [e for e in events if e[0] != "S" or e[1] >= 2]
        require(check_endpoint(edges, normalized, 2, 4) <= coupled,
                "source erasure increased cost")
        count += 1
    return {"matrix_instances": count}


def path_controls() -> int:
    edges = ((0, 2, 1, -1), (1, 2, -3, 1), (0, 3, 3, 1), (1, 3, 1, -1))
    count = 0
    for gauges in itertools.product((-2, 0, 2), repeat=4):
        events = [("S", r, g) for r, g in enumerate(gauges) if g]
        events += [("A", index, 0) for index in (3, 0, 2, 1)]
        events += [("S", r, -g) for r, g in enumerate(gauges) if g]
        cost = check_endpoint(edges, events, 2, 4)
        reduced = [e for e in events if e[0] != "S" or e[1] >= 2]
        require(check_endpoint(edges, reduced, 2, 4) <= cost, "path removal")
        count += 1
    return count


def star_controls() -> dict:
    oracle_count = 0
    witnesses = 0
    sharp = {}
    for degree, valuation, odd in itertools.product(range(1, 4), range(-1, 2), (-3, 1)):
        edges = tuple((0, target, odd, valuation) for target in range(1, degree + 1))
        base = degree * tariff(Fraction(odd))
        expected = base + 2 * min(degree, 2) * abs(valuation)
        coupled, events = shortest(edges, 1, degree + 1, True)
        fixed, _ = shortest(edges, 1, degree + 1, False)
        require(coupled == expected, "star coupled optimum")
        require(fixed == base + 2 * degree * abs(valuation), "star fixed optimum")
        require(check_endpoint(edges, events, 1, degree + 1) == expected, "star word")
        if degree == 3 and valuation == -1 and odd == 1:
            sharp = {"sharp_star_target_only_cost": fixed, "sharp_star_coupled_cost": coupled}
        reverse = tuple((source, degree, odd, valuation) for source in range(degree))
        reverse_coupled, reverse_events = shortest(reverse, degree, degree + 1, True)
        reverse_fixed, _ = shortest(reverse, degree, degree + 1, False)
        require(reverse_coupled == reverse_fixed == interval_cost(reverse, degree + 1)
                == expected, "reversed star source elimination")
        require(check_endpoint(reverse, reverse_events, degree, degree + 1) == expected,
                "reversed star endpoint")
        oracle_count += 1
    for valuation, odd in itertools.product(range(-8, 9), (-3, 1, 5)):
        edges = tuple((0, target, odd, valuation) for target in range(1, 4))
        events = [("S", 0, valuation)] + [("A", i, 0) for i in range(3)]
        events += [("S", 0, -valuation)]
        cost = check_endpoint(edges, events, 1, 4)
        require(cost == 3 * tariff(Fraction(odd)) + 4 * abs(valuation), "star family")
        witnesses += 1
    require(bool(sharp), "missing sharpness fixture")
    return {"star_oracle_instances": oracle_count, "reversed_star_oracle_instances": oracle_count,
            "star_witnesses": witnesses, **sharp}


def rejection_controls() -> int:
    failures = 0
    invalid_edges = [((0, 0, 1, 0),), ((0, 1, 2, 0),), ((0, 1, 1, 9),)]
    for edges in invalid_edges:
        try:
            validate(edges, 1, 2)
        except ValueError:
            failures += 1
    try:
        tariff(Fraction(1, 3))
    except ValueError:
        failures += 1
    for events in ([], [("A", 0, 0), ("S", 0, 1)]):
        try:
            compile_word(((0, 1, 1, 0),), events, 1, 2)
        except ValueError:
            failures += 1
    require(failures == 6, "invalid contract accepted")
    edges = tuple((0, target, 1, -1) for target in range(1, 4))
    events = [("S", 0, -1)] + [("A", i, 0) for i in range(3)] + [("S", 0, 1)]
    normalized = [e for e in events if e[0] != "S"]
    require(check_endpoint(edges, normalized, 1, 4) > check_endpoint(edges, events, 1, 4),
            "degree-three premise control")
    physical, _ = compile_word(edges, events, 1, 4)
    broken = [(kind, t, s, q / 2 if kind == "A" else q)
              for kind, t, s, q in physical]
    require(replay(broken, 4) != replay(physical, 4), "wrong compensation survived")
    return failures + 2


def authenticate_sources() -> None:
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (PACKAGE.parent.parent / row["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row["sha256"], "source drift")


def main() -> None:
    authenticate_sources()
    result = matrix_census()
    result["gauge_path_fixtures"] = path_controls()
    result.update(star_controls())
    result["rejection_controls"] = rejection_controls()
    result["python"] = platform.python_version()
    result["package_sha256"] = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(PACKAGE.iterdir()) if path.is_file()}
    print(json.dumps(result, sort_keys=True, indent=2))
    print("PASS_LOW_USE_SOURCE_GAUGES no_new_kappa")


if __name__ == "__main__":
    main()
