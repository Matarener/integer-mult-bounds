"""Export the exact Gram criterion as bounded QF_BV SMT-LIB.

No solver is imported. Nick Petalas, Apache-2.0.
"""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from linear import MAX_DIM, matrix, require
from model import group_product


class Circuit:
    def __init__(self, size):
        require(1 <= size <= MAX_DIM, "circuit dimension")
        self.size = size
        self.mask = (1 << size) - 1
        self.nodes = []
        self.cache = {}
        self.assertions = []

    def node(self, op, *args):
        key = (op, *args)
        if key not in self.cache:
            require(len(self.nodes) < 200_000, "circuit capacity")
            self.cache[key] = len(self.nodes)
            self.nodes.append(key)
        return self.cache[key]

    def const(self, value):
        require(0 <= value <= self.mask, "constant range")
        return self.node("const", value)

    def xor(self, left, right):
        return self.node("xor", left, right)

    def bit(self, value, index):
        return self.node("bit", value, index)

    def mux(self, condition, yes, no):
        return self.node("mux", condition, yes, no)

    def sum_rows(self, terms):
        value = self.const(0)
        for term in terms:
            value = self.xor(value, term)
        return value

    def multiply(self, left, right):
        return tuple(self.sum_rows(tuple(self.node("and", self.bit(row, j), other)
                                        for j, other in enumerate(right))) for row in left)

    def equal(self, left, right):
        require(len(left) == len(right), "equation shape")
        self.assertions.extend(zip(left, right, strict=True))

    def rank(self, rows):
        pivots = [self.const(0)] * self.size
        for original in rows:
            value = original
            for j in range(self.size - 1, -1, -1):
                occupied = self.node("nonzero", pivots[j])
                take = self.node("and", self.bit(value, j),
                                 self.xor(occupied, self.const(self.mask)))
                reduced = self.mux(self.bit(value, j), self.xor(value, pivots[j]), value)
                pivots[j] = self.mux(take, value, pivots[j])
                value = self.mux(take, self.const(0), reduced)
        result = self.const(0)
        for pivot in pivots:
            bit = self.node("and", self.node("nonzero", pivot), self.const(1))
            result = self.node("add", result, bit)
        return result

    def evaluate(self, rows, labels):
        require(len(rows) == len(labels) == self.size, "valuation shape")
        matrix(rows, self.size)
        require(all(label in (2, 4) for label in labels), "valuation labels")
        values = []
        for node in self.nodes:
            op, *args = node
            if op == "const":
                value = args[0]
            elif op == "row":
                value = rows[args[0]]
            elif op == "label":
                value = self.mask if labels[args[0]] == 4 else 0
            else:
                value = self.evaluate_operation(op, args, values)
            values.append(value & self.mask)
        return all(values[left] == values[right] for left, right in self.assertions)

    def evaluate_operation(self, op, args, values):
        a = values[args[0]]
        if op == "bit":
            return self.mask if (a >> args[1]) & 1 else 0
        if op == "nonzero":
            return self.mask if a else 0
        b = values[args[1]]
        if op == "xor":
            return a ^ b
        if op == "and":
            return a & b
        if op == "add":
            return a + b
        require(op == "mux", "unknown operation")
        require(a in (0, self.mask), "nonboolean mask")
        return b if a else values[args[2]]

    def expression(self, node):
        op, *args = node
        n = self.size
        zero, ones = f"(_ bv0 {n})", f"(_ bv{self.mask} {n})"
        if op == "const":
            return f"(_ bv{args[0]} {n})"
        if op == "row":
            return f"m{args[0]}"
        if op == "label":
            return f"(ite j{args[0]} {ones} {zero})"
        a = f"v{args[0]}"
        if op == "nonzero":
            return f"(ite (= {a} {zero}) {zero} {ones})"
        if op == "bit":
            return f"(ite (= ((_ extract {args[1]} {args[1]}) {a}) #b1) {ones} {zero})"
        b = f"v{args[1]}"
        if op in ("xor", "and", "add"):
            return f"(bv{op} {a} {b})"
        require(op == "mux", "unknown operation")
        return f"(ite (= {a} {zero}) v{args[2]} {b})"

    def smt(self, timeout_ms):
        require(1 <= timeout_ms <= 600_000, "solver timeout")
        n = self.size
        lines = ["; Exact formal Q8 Gram candidate system, not a solver certificate.",
                 "(set-logic QF_BV)", f"(set-option :timeout {timeout_ms})"]
        for j in range(n):
            lines.extend((f"(declare-fun m{j} () (_ BitVec {n}))", f"(declare-fun j{j} () Bool)"))
        for j, node in enumerate(self.nodes):
            lines.append(f"(define-fun v{j} () (_ BitVec {n}) {self.expression(node)})")
        for left, right in self.assertions:
            lines.append(f"(assert (= v{left} v{right}))")
        names = " ".join([f"m{j}" for j in range(n)] + [f"j{j}" for j in range(n)])
        lines.extend(("(check-sat)", f"(get-value ({names}))"))
        return "\n".join(lines) + "\n"


def formal_product(circuit, rows, labels):
    n = circuit.size
    zero = circuit.const(0)
    result = [tuple(circuit.const((1 << a) if g == 0 else 0) for a in range(n)) for g in range(8)]
    for call_index in range(n):
        updated = []
        for g in range(8):
            # Multiplication by i^-1 or j^-1 identifies the input coefficient.
            moved = circuit.mux(labels[call_index], result[group_product(5, g)][call_index],
                                result[group_product(3, g)][call_index])
            delta = circuit.xor(result[g][call_index], moved)
            updated.append(tuple(circuit.xor(result[g][a], circuit.mux(
                circuit.bit(rows[a], call_index), delta, zero)) for a in range(n)))
        result = updated
    return result


def build(calls, i_targets, j_targets):
    c = Circuit(calls)
    require(0 <= i_targets <= calls and 0 <= j_targets <= calls, "target count")
    rows = tuple(c.node("row", a) for a in range(calls))
    labels = tuple(c.node("label", a) for a in range(calls))
    zero = tuple(c.const(0) for _ in rows)
    for j, row in enumerate(rows):
        c.equal((c.bit(row, j),), (c.const(c.mask),))
    selector = c.sum_rows(tuple(c.mux(label, c.const(0), c.const(1 << j))
                                for j, label in enumerate(labels)))
    pi = tuple(c.node("and", row, selector) for row in rows)
    pj = tuple(c.xor(row, other) for row, other in zip(rows, pi, strict=True))
    pim, pjm = c.multiply(pi, rows), c.multiply(pj, rows)
    c.equal(c.multiply(pi, pim), pim)
    c.equal(c.multiply(pj, pjm), pjm)
    c.equal(c.multiply(pi, pjm), zero)
    c.equal(c.multiply(pj, pim), zero)
    c.equal((c.rank(pim), c.rank(pjm)), (c.const(i_targets), c.const(j_targets)))
    expected = [zero] * 8
    expected[0] = tuple(c.xor(c.xor(a, b), d) for a, b, d in zip(rows, pim, pjm, strict=True))
    expected[3], expected[5] = pim, pjm
    for actual, wanted in zip(formal_product(c, rows, labels), expected, strict=True):
        c.equal(c.multiply(actual, rows), wanted)
    return c


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--calls", type=int, required=True)
    parser.add_argument("--i-targets", type=int, required=True)
    parser.add_argument("--j-targets", type=int, required=True)
    parser.add_argument("--timeout-ms", type=int, default=60_000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    c = build(args.calls, args.i_targets, args.j_targets)
    with args.output.open("x", encoding="utf-8") as stream:
        written = stream.write(c.smt(args.timeout_ms))
        require(written > 0, "empty SMT system")
    print(f"EXPORTED nodes={len(c.nodes)} equations={len(c.assertions)}")


if __name__ == "__main__":
    main()
