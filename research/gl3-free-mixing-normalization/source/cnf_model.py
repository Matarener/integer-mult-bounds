"""Independent direct Boolean/CNF encoding; no Z3 or model.py imports.

Group elements are row tuples; gates use direct row XOR and set coefficients.
Brian Ross with substantial OpenAI Codex assistance, Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import time

from exact_checker import IDENTITY, TARGET, column, group, product

PAIRS = [(i, j) for i in range(3) for j in range(3) if i != j]


class CNF:
    def __init__(self):
        self.variables = 1
        self.clauses = [(1,)]  # Literal 1 is true; -1 is false.
        self.operations = []
        self.cache = {}

    def variable(self):
        self.variables += 1
        return self.variables

    def add(self, *literals):
        values = set(literals)
        if 1 in values or any(-x in values for x in values):
            return
        values.discard(-1)
        self.clauses.append(tuple(sorted(values, key=lambda x: (abs(x), x))))

    def both(self, a, b):
        if -1 in (a, b) or a == -b:
            return -1
        if a == 1:
            return b
        if b == 1 or a == b:
            return a
        key = ("and", *sorted((a, b)))
        if key not in self.cache:
            x = self.variable()
            self.add(-x, a)
            self.add(-x, b)
            self.add(x, -a, -b)
            self.operations.append((x, "and", a, b))
            self.cache[key] = x
        return self.cache[key]

    def xor(self, a, b):
        if a == -1:
            return b
        if b == -1:
            return a
        if a == 1:
            return -b
        if b == 1:
            return -a
        if a == b:
            return -1
        if a == -b:
            return 1
        # XOR of signed literals differs only by parity of the signs.
        sign = -1 if (a < 0) != (b < 0) else 1
        key = ("xor", *sorted((abs(a), abs(b))))
        if key not in self.cache:
            aa, bb = key[1:]
            x = self.variable()
            self.add(-aa, -bb, -x)
            self.add(aa, bb, -x)
            self.add(aa, -bb, x)
            self.add(-aa, bb, x)
            self.operations.append((x, "xor", aa, bb))
            self.cache[key] = x
        return sign * self.cache[key]

    def xors(self, items):
        result = -1
        for x in items:
            result = self.xor(result, x)
        return result

    def either(self, a, b):
        return -self.both(-a, -b)

    def ors(self, items):
        result = -1
        for x in items:
            result = self.either(result, x)
        return result

    def equal(self, a, b):
        self.add(-a, b)
        self.add(a, -b)

    def evaluate(self, assignments):
        values = {1: True, **assignments}
        def truth(lit):
            return values[abs(lit)] == (lit > 0)
        for x, operation, a, b in self.operations:
            values[x] = (truth(a) and truth(b)) if operation == "and" else (truth(a) != truth(b))
        return values

    def failed_clauses(self, assignments):
        values = self.evaluate(assignments)
        return sum(not any(values[abs(x)] == (x > 0) for x in clause)
                   for clause in self.clauses)

    def write(self, path):
        with Path(path).open("w", encoding="ascii", newline="\n") as stream:
            stream.write(f"p cnf {self.variables} {len(self.clauses)}\n")
            for clause in self.clauses:
                stream.write(" ".join(map(str, clause)) + " 0\n")


def address_data():
    elements = sorted(group())
    index = {x: k for k, x in enumerate(elements)}
    distance = {IDENTITY: 0}
    paths = {IDENTITY: []}
    queue = [IDENTITY]
    for x in queue:
        for label, (i, j) in enumerate(PAIRS):
            y = list(x)
            y[i] ^= y[j]
            y = tuple(y)
            if y not in distance:
                distance[y] = distance[x] + 1
                paths[y] = paths[x] + [label]
                queue.append(y)
    assert len(distance) == 168
    perms = []
    for i, j in PAIRS:
        p = []
        for x in elements:
            y = list(x)
            y[i] ^= y[j]
            p.append(index[tuple(y)])
        assert all(p[p[k]] == k for k in range(168))
        perms.append(p)
    return elements, index, distance, paths, perms


def build(length=8, target=TARGET, support_bounds=True, endpoint_columns=None):
    start = time.perf_counter()
    elements, index, distance, paths, perms = address_data()
    if endpoint_columns is not None and support_bounds:
        raise ValueError("custom control endpoints require unpruned encoding")
    cnf = CNF()
    allowed = []
    for t in range(length + 1):
        columns = []
        for c in range(3):
            if support_bounds:
                backward = {product(x, target[c]) for x in elements
                            if distance[x] <= length - t}
                columns.append({index[x] for x in elements
                                if distance[x] <= t and x in backward})
            else:
                columns.append(set(range(168)))
        allowed.append(columns)
    states = []
    state_variables = {}
    for t in range(length + 1):
        state = []
        for r in range(3):
            row = []
            for c in range(3):
                polynomial = []
                for k, x in enumerate(elements):
                    if t == 0:
                        literal = 1 if r == c and x == IDENTITY else -1
                    elif t == length:
                        expected = (r == c and x == target[c]) if endpoint_columns is None else (
                            x in endpoint_columns[c][r])
                        literal = 1 if expected else -1
                    elif k in allowed[t][c]:
                        literal = cnf.variable()
                        state_variables[t, r, c, k] = literal
                    else:
                        literal = -1
                    polynomial.append(literal)
                row.append(polynomial)
            state.append(row)
        states.append(state)
    selectors = []
    for t in range(length):
        u = [cnf.variable() for _ in range(3)]
        v = [cnf.variable() for _ in range(3)]
        labels = [cnf.variable() for _ in range(6)]
        selectors.append((u, v, labels))
        cnf.add(cnf.xors(cnf.both(u[k], v[k]) for k in range(3)))
        cnf.add(*labels)
        for a, b in itertools.combinations(labels, 2):
            cnf.add(-a, -b)
        for c in range(3):
            q = [cnf.xors(cnf.both(v[r], states[t][r][c][k]) for r in range(3))
                 for k in range(168)]
            for k in range(168):
                # One-hot labels make this precisely the selected translation.
                shifted = cnf.ors(cnf.both(labels[g], q[perms[g][k]])
                                  for g in range(6))
                delta = cnf.xor(q[k], shifted)
                for r in range(3):
                    value = cnf.xor(states[t][r][c][k], cnf.both(u[r], delta))
                    cnf.equal(states[t + 1][r][c][k], value)
    metadata = {
        "length": length, "target_row_masks": target, "group_order": 168,
        "alphabet": 168, "selector_bits_per_step": 12,
        "support_bounds": support_bounds, "symmetry_reductions": [],
        "variables": cnf.variables, "clauses": len(cnf.clauses),
        "state_variables": len(state_variables),
        "support_counts": [[len(x) for x in row] for row in allowed],
        "build_seconds": time.perf_counter() - start,
        "encoding": "independent row-tuple Boolean gates with direct Tseitin CNF",
    }
    return cnf, selectors, state_variables, elements, metadata


def word_assignments(word, selectors, state_variables, elements):
    assignments = {}
    for gate, (u, v, labels) in zip(word, selectors):
        uu, vv, i, j = gate
        for k in range(3):
            assignments[u[k]] = bool(uu & (1 << k))
            assignments[v[k]] = bool(vv & (1 << k))
        for k, variable in enumerate(labels):
            assignments[variable] = PAIRS[k] == (i, j)
    prefixes = {}
    for t, _, c, _ in state_variables:
        if (t, c) not in prefixes:
            prefixes[t, c] = column(word[:t], c)
    for (t, r, c, k), variable in state_variables.items():
        assignments[variable] = elements[k] in prefixes[t, c][r]
    return assignments


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", type=int, default=8)
    parser.add_argument("--out", required=True)
    parser.add_argument("--no-support", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.length <= 9:
        parser.error("bounded instance lengths 1..9 only")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    cnf, selectors, states, elements, metadata = build(args.length, support_bounds=not args.no_support)
    path = out / "instance.cnf"
    cnf.write(path)
    metadata["cnf_sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    metadata["cnf_bytes"] = path.stat().st_size
    metadata["source_sha256"] = {
        name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
        for name in ("cnf_model.py", "exact_checker.py")}
    (out / "ENCODING.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    (out / "SELECTORS.json").write_text(json.dumps(selectors), encoding="utf-8")
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
