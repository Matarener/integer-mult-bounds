# SPDX-License-Identifier: Apache-2.0
"""Compile the full selected scalar vocabulary before numerical input.

I use the Horner/shift method already specified in PR2287 and the physical
instruction alphabet of PR3098. This extends their finite lowering domain;
it does not introduce a new arithmetic identity. Jose Manuel/Codex.
"""
from collections import Counter
from fractions import Fraction as Q


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def power_two(value):
    return value > 0 and value & (value - 1) == 0


class ScalarProgram:
    """Three logical words: target T, preserved source S, zero scratch Q."""
    def __init__(self, kind, numerator, denominator):
        require(kind in ("add", "scale") and type(numerator) is int and
                type(denominator) is int and denominator != 0, "fixed scalar literal")
        value = Q(numerator, denominator)
        require(abs(value.numerator) <= 65537 and value.denominator <= 65536 and
                power_two(value.denominator), "selected full-word literal domain")
        self.kind = kind
        self.coefficient = value
        self.key = kind, value.numerator, value.denominator
        a, b = abs(value.numerator), value.denominator
        shift = b.bit_length() - 1
        operations = []
        if not a:
            if kind == "scale":
                operations.append(("clear", 0))
        elif kind == "scale":
            require(power_two(a), "selected SCALE is a signed power of two")
            if value < 0:
                operations.append(("neg", 0))
            exponent = a.bit_length() - 1 - shift
            operations.extend((("double" if exponent > 0 else "half"), 0)
                              for _ in range(abs(exponent)))
        else:
            operations.append(("copy", 2, 1))
            for bit in bin(a)[3:]:
                operations.append(("double", 2))
                if bit == "1":
                    operations.append(("add", 2, 1, 1))
            operations.extend(("half", 2) for _ in range(shift))
            operations.append(("add", 0, 2, -1 if value < 0 else 1))
            operations.append(("clear", 2))
        self.program = tuple(operations)
        require(len(self.program) <= 64, "finite full scalar word")
        self.prefix_rows = self._verify()

    def _verify(self):
        rows = [(Q(1), Q(0)), (Q(0), Q(1)), (Q(0), Q(0))]
        prefixes = [tuple(rows)]
        for op in self.program:
            kind, dst = op[:2]
            require(dst != 1, "source-preserving lowering")
            if kind == "copy":
                require(rows[dst] == (0, 0), "COPY starts at logical zero")
                rows[dst] = rows[op[2]]
            elif kind == "clear":
                rows[dst] = (Q(0), Q(0))
            elif kind == "add":
                rows[dst] = tuple(x + op[3] * y for x, y in zip(rows[dst], rows[op[2]]))
            else:
                factor = {"double": Q(2), "half": Q(1, 2), "neg": Q(-1)}[kind]
                rows[dst] = tuple(factor * x for x in rows[dst])
            prefixes.append(tuple(rows))
        want = (Q(1), self.coefficient) if self.kind == "add" else (self.coefficient, Q(0))
        require(rows == [want, (Q(0), Q(1)), (Q(0), Q(0))], "complete scalar endpoint")
        return tuple(prefixes)


def compile_catalogue(programs):
    catalogue = {}
    counts = {}
    for orientation in ("forward", "backward"):
        current = Counter()
        for event in programs[orientation]:
            if event[0] != "scalar":
                continue
            op = event[1]
            if op[0] not in ("add", "scale"):
                require(op[0] in ("copy", "clear"), "full scalar opcode")
                current[op[0]] += 1
                continue
            offset = 3 if op[0] == "add" else 2
            value = Q(op[offset], op[offset + 1])
            key = op[0], value.numerator, value.denominator
            if key not in catalogue:
                catalogue[key] = ScalarProgram(*key)
            current[op[0]] += 1
        counts[orientation] = dict(current)
    require(len(catalogue) == 349, "full selected scalar catalogue")
    return catalogue, counts


def prefix_guard(program):
    """Exact affine prefix envelope, not a replacement for the caller height proof."""
    denominator_bits = 0
    l1 = Q(0)
    for rows in program.prefix_rows:
        for row in rows:
            l1 = max(l1, sum(abs(x) for x in row))
            for value in row:
                require(power_two(value.denominator), "dyadic prefix")
                denominator_bits = max(denominator_bits, value.denominator.bit_length() - 1)
    return denominator_bits, l1


def inventory(programs):
    catalogue, counts = compile_catalogue(programs)
    histogram = Counter(len(p.program) for p in catalogue.values())
    guards = [prefix_guard(p) for p in catalogue.values()]
    return {
        "literals": len(catalogue),
        "occurrences": counts,
        "maximum_instructions": max(histogram),
        "instruction_histogram": dict(sorted(histogram.items())),
        "maximum_prefix_denominator_bits": max(g[0] for g in guards),
        "maximum_prefix_l1": str(max(g[1] for g in guards)),
        "maximum_numerator": max(abs(p.coefficient.numerator) for p in catalogue.values()),
        "maximum_denominator": max(p.coefficient.denominator for p in catalogue.values()),
    }
