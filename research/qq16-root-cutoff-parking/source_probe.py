# SPDX-License-Identifier: Apache-2.0
"""Execute two unchanged source methods over exact descriptor integers.

This is a Count/record test interpreter, not physical execution or a new
implementation of the source primitives. Physical correctness is inherited.
Prepared for commdata2338 with substantial OpenAI Codex assistance.
"""
import ast
from types import SimpleNamespace


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Count:
    def __init__(self, value):
        self.value = value.value if isinstance(value, Count) else value
        need(type(self.value) is int and self.value >= 0, "natural descriptor")
        self.tape = self

    literal = classmethod(lambda cls, value: cls(value))
    product = classmethod(lambda cls, a, b: cls(a.value * b.value))

    def zero(self):
        return self.value == 0

    def add(self, other):
        self.value += other.value

    def multiply_small(self, factor):
        self.value *= factor

    def divide_small(self, divisor):
        self.value, remainder = divmod(self.value, divisor)
        return remainder

    def close(self):
        pass  # Lifetimes, record cells and their costs are outside this probe.


def methods(source):
    tree = ast.parse(source)
    machine = next(n for n in tree.body if isinstance(n, ast.ClassDef)
                   and n.name == "Machine")
    inputs = next(ast.literal_eval(n.value) for n in tree.body
                  if isinstance(n, ast.Assign) and any(
                      isinstance(t, ast.Name) and t.id == "INPUTS" for t in n.targets))
    functions = [n for n in machine.body if isinstance(n, ast.FunctionDef)
                 and n.name in ("node", "prepare_child")]
    need(len(functions) == 2, "both original descriptor methods")
    env = {
        "Count": Count, "INPUTS": inputs, "BLANK": -1, "need": need,
        "positive": lambda x: need(x.value > 0, "positive descriptor"),
        "compare": lambda a, b: (a.value > b.value) - (a.value < b.value),
        "subtract": lambda a, b: Count(a.value - b.value),
        "divide": lambda a, b: tuple(Count(x) for x in divmod(a.value, b.value)),
        "fixed_power": lambda a, k, cap: Count(min(a.value ** k, cap.value)),
        "skip": lambda tape, extent: None,
        "copy_symbols": lambda source, target: setattr(target, "value", source.value),
    }
    # No imported predecessor module or constructor executes here.
    exec(compile(ast.Module(body=functions, type_ignores=[]),
                 "<authenticated Machine descriptor methods>", "exec"), env)
    return inputs, env["node"], env["prepare_child"]


def fixture(inputs, width, root_width, rows, gamma):
    values = dict.fromkeys(inputs, 0)
    values.update(width=width, root_width=root_width, rows=rows, prefixes=3,
                  spacing=7, guard=1, component_bits=2, coefficients=5,
                  front=11, compact_bits=2, before=13, after=17, back=19)
    state = SimpleNamespace(values=values, leaves=[], mode="node", group=None,
                            binding=SimpleNamespace(dimension=73, families=14336,
                                                    cover=SimpleNamespace(size=gamma)))
    state.roles = {"current": SimpleNamespace(rewind=lambda: None, read=lambda: -1),
                   "header": SimpleNamespace()}
    state.c = lambda key: Count(state.values[key])
    state.save = lambda value, key: state.values.__setitem__(key, value.value)
    state.shape = lambda: state.values.__setitem__("row_bits", 20)
    state.complete_extent = lambda: Count(0)
    state.apply_leaf = lambda w, before, after: state.leaves.append(
        (w.value, before.value, after.value))
    state.capsule = {name: Count(0) for name in ("current", *inputs)}
    state.packet = lambda index: Count(23)
    state.header = SimpleNamespace(write=lambda tape, fields: None)
    state.bank = SimpleNamespace(state="gathered")
    state.root = True
    return state


def rectangle(values):
    return (3 * values["compact_bits"] + values["front"] + values["before"]
            + values["width"] * values["spacing"] + values["after"] + values["back"])


def check_source(source, ranks, cutoffs):
    inputs, node, child = methods(source)
    counts = {"node_cases": 0, "child_cases": 0}
    for threshold in cutoffs:
        root = threshold ** 1000
        for width in sorted({0, 1, 72, 73, threshold-1, threshold, threshold+1,
                             73*(threshold//48), 8192}):
            gamma, rows = 3, (14336*3)**4
            state = fixture(inputs, width, root, rows, gamma)
            before = rectangle(state.values)
            node(state)
            terminal = width < 73 or width ** 1000 < root
            need((state.mode == "return") == terminal, "literal cutoff decision")
            counts["node_cases"] += 1
            if terminal:
                need(state.leaves == [(width, 13, 17)], "terminal source leaf")
                continue
            q, remainder = divmod(width, 73)
            need(state.values["columns"] == q and state.values["width"] == 73*q,
                 "source quotient and reached program width")
            need(state.values["unused"] == rows//(14336*gamma), "source fresh rows")
            need(rectangle(state.values) == before, "remainder spectators preserved")
            need(len(state.leaves) == bool(remainder), "one optional remainder leaf")
            state.group = object()
            for rank in ranks:
                child(state, 0, rank)
                result = {name: value.value for name, value in state.capsule.items()
                          if name != "current"}
                need(result["width"] == rank*q, "literal child width")
                need(result["rows"] == rows//(14336*gamma), "literal child row division")
                need(result["root_width"] == root, "unchanged global cutoff")
                need(rectangle(result) == before, "complete address extent preserved")
                for key in set(inputs)-{"rows", "width", "after", "before"}:
                    need(result[key] == state.values[key], "unchanged spectator descriptor")
                counts["child_cases"] += 1
    return counts
