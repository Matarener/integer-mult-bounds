"""Exact constructive and exhaustive checks for PROOF.md; standard library only."""

import argparse
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def graph(p):
    require(type(p) is int and 2 <= p <= 20, "fixture p outside [2,20]")
    return tuple((u, v) for u in range(2 * p) for v in range(u + 1, 2 * p)
                 if u // 2 != v // 2)


def components(n, edges):
    adjacency = [[] for _ in range(n)]
    for u, v in edges:
        adjacency[u].append(v)
        adjacency[v].append(u)
    seen = set()
    result = []
    for root in range(n):
        if root in seen:
            continue
        queue = [root]
        seen.add(root)
        for head in range(n):
            if head == len(queue):
                break
            for v in adjacency[queue[head]]:
                if v not in seen:
                    seen.add(v)
                    queue.append(v)
        result.append(tuple(sorted(queue)))
    require(sum(map(len, result)) == n, "component partition")
    return tuple(result), adjacency


def analyze(p, targets):
    available = set(graph(p))
    require(len(targets) == len(set(targets)), "duplicate target")
    require(all(e in available for e in targets), "invalid target edge")
    comps, adjacency = components(2 * p, targets)
    require(len(targets) - 2 * p + len(comps) == 1, "not one cycle in total")
    core = set(range(2 * p))
    for _ in range(2 * p):
        leaves = {v for v in core if sum(w in core for w in adjacency[v]) <= 1}
        if not leaves:
            break
        core.difference_update(leaves)
    cycle = tuple(i for i, (u, v) in enumerate(targets) if u in core and v in core)
    require(len(cycle) >= 3 and len(cycle) % 2 == 1, "cycle is not odd")
    require(len(core) == len(cycle), "cycle core mismatch")
    return comps, cycle


def root_colors(comps):
    roots = [c[0] for c in comps]
    root_set = set(roots)
    adjusted = False
    if len(roots) % 4 == 2 and all((v ^ 1) in root_set for v in roots):
        index = next(i for i, c in enumerate(comps) if len(c) > 1)
        roots[index] = comps[index][1]
        root_set = set(roots)
        adjusted = True
    pairs = tuple((v, v ^ 1) for v in sorted(root_set)
                  if v % 2 == 0 and (v ^ 1) in root_set)
    singles = tuple(v for v in sorted(root_set) if (v ^ 1) not in root_set)
    half = len(roots) // 2
    choices = [j for j in range(len(singles) + 1)
               if 0 <= half - j <= 2 * len(pairs) and (half - j) % 2 == 0]
    require(bool(choices), "balanced root coloring absent")
    j = choices[0]
    left = set(singles[:j])
    for pair in pairs[:(half - j) // 2]:
        left.update(pair)
    require(len(left) == half, "unbalanced root coloring")
    require(all((u in left) == (v in left) for u, v in pairs), "split missing edge")
    return tuple(roots), frozenset(left), adjusted


def construct(p, targets):
    """Return actual vector-valued star coefficients and the retained graph."""
    comps, cycle = analyze(p, targets)
    roots, left, adjusted = root_colors(comps)
    constant = sum(1 << i for i in cycle)
    labels = [None] * (2 * p)
    adjacency = [[] for _ in labels]
    for i, (u, v) in enumerate(targets):
        if i != cycle[0]:
            adjacency[u].append((v, i))
            adjacency[v].append((u, i))
    queue = list(roots)
    for root in roots:
        labels[root] = constant if root in left else 0
    for head in range(2 * p):
        if head == len(queue):
            break
        u = queue[head]
        for v, i in adjacency[u]:
            if labels[v] is None:
                labels[v] = labels[u] ^ constant ^ (1 << i)
                queue.append(v)
    require(all(a is not None for a in labels), "unreached target vertex")
    zero_edges = frozenset((min(u, v), max(u, v)) for u in left
                           for v in roots if v not in left)
    retained = frozenset(targets) | zero_edges
    s = 2 * p - len(targets) + 1
    require(len(zero_edges) == s * s // 4, "wrong zero-edge count")
    require(zero_edges <= set(graph(p)), "unavailable root edge")
    return tuple(labels), constant, retained, adjusted


def endpoint(p, targets, labels, constant, retained):
    """Check every retained input column against the literal unit decoders."""
    require(len(labels) == 2 * p, "wrong coefficient count")
    require(retained <= set(graph(p)), "invalid retained edge")
    require(set(targets) <= retained, "target deleted")
    units = {e: 1 << i for i, e in enumerate(targets)}
    for u, v in retained:
        require(labels[u] ^ labels[v] ^ constant == units.get((u, v), 0),
                "wrong retained input column")
    return True


def binary_basis(rows, width):
    basis = [0] * width
    for row in rows:
        value = row
        for bit in range(width - 1, -1, -1):
            if value & (1 << bit):
                if basis[bit]:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    break
    return basis


def in_span(value, basis):
    for bit in range(len(basis) - 1, -1, -1):
        if value & (1 << bit):
            value ^= basis[bit]
    return value == 0


def all_retained_oracle():
    """Enumerate every p=3 retained graph, then optimize every target set."""
    edges = graph(3)
    width = len(edges)
    rows = [sum(1 << i for i, e in enumerate(edges) if v in e) for v in range(6)]
    rows.append((1 << width) - 1)
    best = [-1] * (1 << width)
    for mask in range(1 << width):
        basis = binary_basis((row & mask for row in rows), width)
        decodable = sum(1 << i for i in range(width)
                        if mask & (1 << i) and in_span(1 << i, basis))
        best[decodable] = max(best[decodable], mask.bit_count())
    for i in range(width):
        for mask in range(1 << width):
            if not mask & (1 << i):
                best[mask] = max(best[mask], best[mask | (1 << i)])
    return edges, best


def exhaustive_check():
    edges, best = all_retained_oracle()
    cases = adjusted = 0
    by_r = {}
    digest = hashlib.sha256()
    for mask in range(1 << len(edges)):
        targets = tuple(e for i, e in enumerate(edges) if mask & (1 << i))
        try:
            analyze(3, targets)
        except ValueError:
            continue
        labels, constant, retained, changed = construct(3, targets)
        endpoint(3, targets, labels, constant, retained)
        expected = len(targets) + (7 - len(targets)) ** 2 // 4
        require(best[mask] == expected == len(retained), "exhaustive optimum differs")
        cases += 1
        adjusted += changed
        by_r[len(targets)] = by_r.get(len(targets), 0) + 1
        digest.update(f"{mask}:{best[mask]}:{labels}:{constant}\n".encode())
    require(cases > 0 and adjusted > 0, "exhaustive coverage absent")
    return {"retained_graphs": len(best), "target_sets": cases,
            "targets_by_r": by_r, "root_adjustments": adjusted,
            "sha256": digest.hexdigest()}


def cycle_fixture(p, length, attached, mode):
    vertices = tuple(range(0, 2 * p, 2)) + tuple(range(1, 2 * p, 2))
    cycle = list(vertices[:length])
    if cycle[-1] // 2 == cycle[0] // 2:
        cycle[-1], cycle[-2] = cycle[-2], cycle[-1]
    edges = {(min(u, v), max(u, v))
             for u, v in zip(cycle, cycle[1:] + cycle[:1])}
    rest = vertices[length:]
    active = list(cycle)
    for v in rest[:attached]:
        parent = next(u for u in reversed(active) if u // 2 != v // 2)
        edges.add((min(parent, v), max(parent, v)))
        active.append(v)
    if mode:
        remaining = rest[attached:]
        for u, v in zip(remaining[::2], remaining[1::2]):
            if u // 2 != v // 2:
                edges.add((min(u, v), max(u, v)))
    return tuple(sorted(edges))


def fixture_check():
    cases = columns = adjusted = 0
    cycle_lengths = set()
    digest = hashlib.sha256()
    for p in range(4, 17):
        for length in range(3, 2 * p, 2):
            for attached in range(2 * p - length + 1):
                for mode in (0, 1):
                    targets = cycle_fixture(p, length, attached, mode)
                    labels, constant, retained, changed = construct(p, targets)
                    endpoint(p, targets, labels, constant, retained)
                    s = 2 * p - len(targets) + 1
                    require(len(retained) == len(targets) + s * s // 4, "fixture size")
                    cases += 1
                    columns += len(retained)
                    adjusted += changed
                    cycle_lengths.add(length)
                    digest.update(f"{p}:{targets}:{labels}:{constant}\n".encode())
    return {"cases": cases, "retained_columns": columns,
            "cycle_lengths": sorted(cycle_lengths), "root_adjustments": adjusted,
            "sha256": digest.hexdigest()}


def expect_rejection(operation):
    try:
        operation()
    except ValueError:
        return
    raise ValueError("control unexpectedly accepted")


def controls():
    triangle = ((0, 2), (0, 4), (2, 4))
    invalid = [(), ((0, 1),), triangle + (triangle[0],),
               ((0, 2), (0, 3), (1, 2), (1, 3)),
               triangle + ((1, 3), (1, 5), (3, 5))]
    for targets in invalid:
        expect_rejection(lambda: analyze(3, targets))
    labels, constant, retained, _ = construct(4, triangle)
    expect_rejection(lambda: endpoint(4, triangle, labels, 0, retained))
    bad_labels = list(labels)
    bad_labels[0] ^= 1
    expect_rejection(lambda: endpoint(4, triangle, bad_labels, constant, retained))
    expect_rejection(lambda: endpoint(4, triangle, labels, constant,
                                      retained - {triangle[0]}))
    deleted = set(graph(4)) - retained
    require(bool(deleted), "no deletion-restoration control")
    for edge in sorted(deleted):
        expect_rejection(lambda: endpoint(4, triangle, labels, constant, retained | {edge}))
    for a in range(1, 41):
        for b in range(1, 41):
            require(a * a // 4 + b * b // 4 <= (a + b - 1) ** 2 // 4,
                    "component concentration inequality")
    require(12 - 3 - 4 == 5 and 24 - 3 - 9 == 12, "triangle specialization")
    return {"invalid_inputs": len(invalid), "decoder_mutants": 3,
            "restored_deleted_edges": len(deleted), "concentration_pairs": 1600}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new source-bound JSON receipt")
    args = parser.parse_args()
    result = {"claim_type": "scoped proof with finite corroboration",
              "exhaustive_p3": exhaustive_check(), "constructive": fixture_check(),
              "controls": controls()}
    package = Path(__file__).resolve().parent
    result["source_sha256"] = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest()
        for name in ("verify.py", "PROOF.md", "README.md", "TASK.json", "SOURCES.json", "VERIFY.json")}
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.receipt:
        require(args.receipt.resolve().parent != package, "receipt must be outside package")
        with args.receipt.open("x", encoding="utf-8") as output:
            require(output.write(encoded) == len(encoded), "incomplete receipt write")
    print("PASS_ODD_UNICYCLIC_STAR_BUDGETS")
    print(encoded, end="")


if __name__ == "__main__":
    main()
