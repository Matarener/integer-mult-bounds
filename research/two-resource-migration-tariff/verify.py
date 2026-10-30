#!/usr/bin/env python3
"""Exact two-resource migration certificates and bounded independent oracles."""

from dataclasses import dataclass, replace
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import random


@dataclass(frozen=True)
class Job:
    start: int
    stop: int
    mask: int
    weight: int = 1


@dataclass(frozen=True)
class Certificate:
    cost: int
    choices: tuple[int, ...]
    potentials: tuple[tuple[int, ...], ...]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def layers(jobs):
    """At most 1023 layers, each with at most two injective assignments."""
    require(1 <= len(jobs) <= 512, "job count")
    events = {}
    for i, job in enumerate(jobs):
        require(all(type(x) is int for x in
                    (job.start, job.stop, job.mask, job.weight)), "integer input")
        require(0 <= job.start < job.stop <= 10**6, "lifetime")
        require(1 <= job.mask <= 3, "resource list")
        require(0 <= job.weight <= 10**12, "migration weight")
        events.setdefault(job.start, [[], []])[1].append(i)
        events.setdefault(job.stop, [[], []])[0].append(i)
    times = sorted(events)
    active = set()
    result = []
    for time in times[:-1]:
        endings, beginnings = events[time]
        active.difference_update(endings)
        active.update(beginnings)
        require(len(active) <= 2, "pointwise Hall shortage")
        ids = tuple(sorted(active))
        options = tuple(tuple(r for r in range(2) if jobs[i].mask & (1 << r))
                        for i in ids)
        states = tuple(tuple(zip(ids, colors)) for colors in product(*options)
                       if len(set(colors)) == len(colors))
        require(bool(states), "pointwise Hall shortage")
        assert 1 <= len(states) <= 2
        result.append(states)
    assert len(result) <= 2 * len(jobs) - 1
    return tuple(result)


def transition(jobs, previous, current):
    old = dict(previous)
    return sum(jobs[i].weight for i, color in current
               if i in old and old[i] != color)


def optimize(jobs):
    states = layers(jobs)
    distances = [(0,) * len(states[0])]
    parents = [(-1,) * len(states[0])]
    for before, after in zip(states, states[1:]):
        entries = tuple(min((distances[-1][p] + transition(jobs, a, b), p)
                            for p, a in enumerate(before)) for b in after)
        distances.append(tuple(x[0] for x in entries))
        parents.append(tuple(x[1] for x in entries))
    final = min(range(len(states[-1])), key=lambda i: distances[-1][i])
    cost = distances[-1][final]
    choices = [0] * len(states)
    for k in range(len(states) - 1, -1, -1):
        choices[k] = final
        final = parents[k][final]
    return Certificate(cost, tuple(choices), tuple(distances))


def check_certificate(jobs, certificate):
    """Check a primal path and dual arc inequalities, without optimization."""
    states = layers(jobs)
    require(type(certificate.cost) is int and certificate.cost >= 0, "cost")
    require(len(certificate.choices) == len(states), "path length")
    require(len(certificate.potentials) == len(states), "potential length")
    path = []
    for k, options in enumerate(states):
        choice = certificate.choices[k]
        require(type(choice) is int and 0 <= choice < len(options), "choice")
        values = certificate.potentials[k]
        require(len(values) == len(options), "potential width")
        require(all(type(x) is int for x in values), "integer potentials")
        path.append(options[choice])
    require(all(x <= 0 for x in certificate.potentials[0]), "initial bound")
    for k in range(1, len(states)):
        for p, before in enumerate(states[k - 1]):
            for q, after in enumerate(states[k]):
                require(certificate.potentials[k][q] <=
                        certificate.potentials[k - 1][p] +
                        transition(jobs, before, after), "dual arc")
    require(all(x >= certificate.cost for x in certificate.potentials[-1]),
            "terminal bound")
    actual = sum(transition(jobs, a, b) for a, b in zip(path, path[1:]))
    require(actual == certificate.cost, "primal cost")
    return actual


def brute(jobs):
    """Enumerate literal assignments on every integer unit cell independently."""
    require(len(jobs) <= 6 and max(j.stop for j in jobs) <= 9, "oracle bound")
    options = []
    for time in range(min(j.start for j in jobs), max(j.stop for j in jobs)):
        active = tuple(i for i, j in enumerate(jobs) if j.start <= time < j.stop)
        cell = []
        for colors in product(range(2), repeat=len(active)):
            if len(set(colors)) != len(colors):
                continue
            if all(jobs[i].mask & (1 << c) for i, c in zip(active, colors)):
                cell.append(dict(zip(active, colors)))
        if not cell:
            return None
        options.append(cell)
    best = None
    for path in product(*options):
        cost = 0
        for before, after in zip(path, path[1:]):
            for i in before.keys() & after.keys():
                if before[i] != after[i]:
                    cost += jobs[i].weight
        best = cost if best is None else min(best, cost)
    return best


def compare(jobs):
    expected = brute(jobs)
    if expected is None:
        try:
            optimize(jobs)
        except ValueError as error:
            require(str(error) == "pointwise Hall shortage", "wrong rejection")
            return False
        raise ValueError("accepted infeasible timeline")
    certificate = optimize(jobs)
    require(check_certificate(jobs, certificate) == expected, "oracle mismatch")
    if all(j.weight == 1 for j in jobs):
        require(expected <= max(0, len(jobs) - 2), "count bound")
    return True


def exhaustive():
    intervals = tuple((a, b) for a in range(4) for b in range(a + 1, 5))
    counts = {"instances": 0, "feasible": 0, "infeasible": 0}
    for n in range(1, 4):
        for lifetimes in product(intervals, repeat=n):
            for masks in product(range(1, 4), repeat=n):
                for weighted in range(2):
                    jobs = tuple(Job(a, b, mask, i + 1 if weighted else 1)
                                 for i, ((a, b), mask) in
                                 enumerate(zip(lifetimes, masks)))
                    feasible = compare(jobs)
                    counts["instances"] += 1
                    counts["feasible" if feasible else "infeasible"] += 1
    return counts


def alternating(n, weight=1):
    require(1 <= n <= 512, "family bound")
    return (Job(0, 2 * n - 1, 3, weight),) + tuple(
        Job(2 * i - 1, 2 * i, 1 << ((i - 1) % 2)) for i in range(1, n))


def controls():
    jobs = alternating(3, 7)
    certificate = optimize(jobs)
    rejected = 0
    corruptions = [replace(certificate, cost=0),
                   replace(certificate, choices=()),
                   replace(certificate, choices=(9,) + certificate.choices[1:]),
                   replace(certificate, potentials=()),
                   replace(certificate, potentials=((1, 1),) +
                           certificate.potentials[1:])]
    potentials = list(certificate.potentials)
    potentials[-1] = tuple(x + 1 for x in potentials[-1])
    corruptions.append(replace(certificate, potentials=tuple(potentials)))
    for bad in corruptions:
        try:
            check_certificate(jobs, bad)
        except ValueError:
            rejected += 1
    require(rejected == len(corruptions), "accepted forged certificate")
    invalid = [(), (Job(0, 0, 3),), (Job(0, 1, 0),), (Job(0, 1, 4),),
               (Job(0, 1, True),), (Job(0, 1, 3, -1),),
               (Job(0, 1, 3, 10**12 + 1),), (Job(0, 10**6 + 1, 3),),
               (Job(0, 1, 3),) * 513]
    for bad in invalid:
        try:
            optimize(bad)
        except ValueError:
            rejected += 1
    require(rejected == len(corruptions) + len(invalid), "accepted bad input")
    return rejected


def corroborate():
    rng = random.Random(5781)
    random_cases = 400
    for _ in range(random_cases):
        jobs = []
        for _ in range(rng.randint(1, 6)):
            a = rng.randrange(6)
            jobs.append(Job(a, rng.randrange(a + 1, 8), rng.randrange(1, 4),
                            rng.randrange(8)))
        compare(tuple(jobs))
    for n in range(1, 513):
        jobs = alternating(n, 7)
        require(check_certificate(jobs, optimize(jobs)) == 7 * max(0, n - 2),
                "sharp family")
    # Touching half-open jobs need neither simultaneous capacity nor migration.
    require(check_certificate((Job(0, 1, 1), Job(1, 2, 1)),
                              optimize((Job(0, 1, 1), Job(1, 2, 1)))) == 0,
            "half-open boundary")
    return {"random_weighted_cases": random_cases, "sharp_family_sizes": 512,
            "rejection_controls": controls(), "half_open_controls": 1}


def main():
    counts = exhaustive()
    counts.update(corroborate())
    root = Path(__file__).resolve().parent
    names = ("verify.py", "PROOF.md", "README.md", "TASK.json",
             "SOURCES.json", "VERIFY.json")
    hashes = {name: sha256((root / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"status": "PASS_TWO_RESOURCE_MIGRATION_TARIFF",
                      "counts": counts, "sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
