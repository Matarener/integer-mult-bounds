# SPDX-License-Identifier: Apache-2.0
"""Compile both literal selected words to a finite physical instruction tape.

I preserve the native directions from the selected exact-recipe audit and
PR2287. Compilation depends on fixed source geometry, never numerical input.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json

from scalar_program import compile_catalogue


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def slot(role):
    require(type(role) in (tuple, list) and len(role) == 2, "source role")
    kind, index = role
    require(type(index) is int and ((kind == "L" and 0 <= index < 704) or
                                  (kind == "C" and 0 <= index < 8)), "finite native role")
    return index if kind == "L" else 704 + index


def compile_local(data, orientation):
    require(orientation in ("forward", "backward"), "selected orientation")
    edges = {(r["old"], r["new"]): r for r in data["native"]["children"]}
    endpoints = {(r["role"], r["port"]): r for r in data["native"]["endpoint_adapters"]}
    require(len(edges) == 2896 and len(endpoints) == 224, "selected native catalogue")
    scalars, _ = compile_catalogue(data["programs"])
    recipes = {}
    code = []
    ranges = []
    private = set()
    word = data["word"]

    def mono(raw_index, role, literal, inverse):
        require(type(literal) is dict and type(inverse) is bool, "native monomial direction")
        name = sha256(canonical(literal)).hexdigest()
        if name in recipes:
            require(recipes[name] == literal, "monomial content identity")
        recipes[name] = literal
        code.append(("monomial", raw_index, role, name, inverse))

    for raw_index, event in enumerate(data["programs"][orientation]):
        first = len(code)
        kind = event[0]
        if kind == "phase":
            code.append(("marker", raw_index, event[1]))
        elif kind == "scalar":
            op = event[1]
            target = slot(op[1])
            if target >= 704 and target not in private:
                require(op[0] == "clear", "private first instruction is logical CLEAR")
                private.add(target)
            if op[0] == "clear":
                require(target >= 704, "only private logical CLEAR")
                code.append(("zero", raw_index, target))
            elif op[0] == "copy":
                source = slot(op[2])
                require(source != target and target >= 704, "private COPY endpoints")
                code.append(("copy", raw_index, target, source))
            else:
                require(op[0] in ("add", "scale"), "scalar opcode")
                i = 3 if op[0] == "add" else 2
                q = Fraction(op[i], op[i + 1])
                key = op[0], q.numerator, q.denominator
                require(key in scalars, "full scalar lowering exists")
                source = slot(op[2]) if op[0] == "add" else None
                require(source != target, "nonalias scalar operands")
                code.append(("scalar", raw_index, target, source, key))
        elif kind in ("climb", "center"):
            if kind == "climb":
                _, _part, role, old, new, rank = event
            else:
                _, private_index, old, new, rank = event
                role = 704 + private_index
                require(role in private and rank == 8, "initialized native centre")
            record = edges[old, new]
            require(record["rank"] == rank and 0 < rank < 73, "proper directed child")
            mono(raw_index, role, record["right"], False)
            code.append(("child", raw_index, role, rank))
            mono(raw_index, role, record["left"], False)
        elif kind == "adapter":
            _, direction, role, frame = event
            require(direction in ("old_to_new", "new_to_old"), "endpoint adapter direction")
            require(frame == word["start" if direction == "old_to_new" else "final"][role],
                    "endpoint adapter source frame")
            if direction == "old_to_new" and role < 112:
                record = endpoints["source", role]
                require(record["frame"] == frame, "source adapter record")
                mono(raw_index, role, record["left"], False)
            elif direction == "new_to_old" and 112 <= role < 224:
                record = endpoints["target", role - 112]
                require(record["frame"] == frame, "target adapter record")
                mono(raw_index, role, record["left"], True)
            else:
                require(frame == (0 if direction == "old_to_new" else 1), "literal identity adapter")
                code.append(("identity", raw_index, role))
        elif kind == "residual_adapter":
            _, direction, role, entrance, *end = event
            terminal = end[0] if end else 1
            require(direction in ("pre", "post") and 224 <= role < 704,
                    "helper wrapper direction and role")
            require((entrance, terminal) == (word["start"][role], word["final"][role]),
                    "helper wrapper endpoints")
            key = f"{entrance}:{terminal}" if end else str(entrance)
            record = data["residuals"]["recipes"][key]
            require(record["frame"] == entrance, "normalized wrapper source")
            mono(raw_index, role, record["right" if direction == "pre" else "left"], True)
        else:
            raise ValueError("unimplemented selected event: " + str(kind))
        require(first < len(code), "each selected event has a physical instruction or explicit identity")
        ranges.append((first, len(code)))
    require(private == set(range(704, 712)), "all eight private slots")
    require(all(code[j][1] == i for i, (start, end) in enumerate(ranges) for j in range(start, end)),
            "complete ordered source-event refinement")
    return tuple(code), recipes, tuple(ranges)


def check(data):
    result = {}
    for direction in ("forward", "backward"):
        code, recipes, ranges = compile_local(data, direction)
        result[direction] = {
            "source_events": len(ranges), "physical_instructions": len(code),
            "counts": dict(Counter(op[0] for op in code)),
            "monomial_records": len(recipes),
            "sha256": sha256(canonical(code)).hexdigest(),
            "scope": "Complete source instruction compilation; numerical execution and recursive controller remain separate."
        }
    return result
