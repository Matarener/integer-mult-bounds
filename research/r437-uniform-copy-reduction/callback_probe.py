#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Direct, authenticated encoded-component probe; predecessor code is reused.

Actual R437 COPY515 projector/source record plus a declared synthetic rank-26
ancestor. No full R437 Catalogue, payload, stock or physical return is claimed.
"""
from contextlib import contextmanager
from dataclasses import replace
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
VENDOR = ROOT / "research/selected-bit-physical-caller/inputs/pr2753/predecessor/vendor"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    source = json.loads((HERE / "SOURCES.json").read_bytes())
    inputs = {row["path"]: row for row in source["files"] if row["usage"] == "input"}
    for path in sorted(VENDOR.glob("*.py")):
        relative = path.relative_to(ROOT).as_posix()
        need(relative in inputs and not path.is_symlink(), "declared encoded component input")
        data = path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == inputs[relative]["sha256"], "encoded component source SHA")
    return source


def body(tape):
    # Observer only, outside no_decode and outside the component algorithm.
    return bytes(tape.cells[1:]).rstrip(bytes([4]))


def numerical_return(arena, live):
    need(arena.live == live and arena.template.head == 1, "numerical slots/template return")
    for word in arena.words:
        need(word.head == 1, "returned numerical head")
        if word.slot not in live:
            need(word.cells[0] == 2 and all(x == 4 for x in word.cells[1:]),
                 "complete erased numerical scratch")


def main():
    authenticate()
    sys.path.insert(0, str(VENDOR))
    from binding import split_basis
    from children import coefficient, extend
    from controller import Callback
    from numeric import selected_coefficient
    import oracle
    from plan import Request, compile_plan
    from records import Fields, Program
    from sources import Template, compile_specification
    from words import Arena, Ring, Unsigned, Word
    # Import the new independent projector only after the pinned source
    # namespace is established. The predecessor module name does not collide.
    sys.path.insert(0, str(HERE))
    from copy_child import projector

    @contextmanager
    def no_decode():
        original = Word.inspect
        def forbidden(_self):
            raise ValueError("runtime host numerical decoding")
        Word.inspect = forbidden
        try:
            yield
        finally:
            Word.inspect = original

    raw = (HERE / "inputs/r437-word.json.gz").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == "e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e", "R437 target input")
    word = json.loads(gzip.decompress(raw))
    local, rank = projector(word["lines"], word["frames"][515])
    need(rank == 7 and word["ret"][5] == 475, "literal R437 target")
    zero = [[F(0)] * 64 for _ in range(64)]
    base7 = [row[:] for row in zero]
    for i, row in enumerate(local):
        base7[i][:8] = row
    base26 = [[F(i == j and i < 26) for j in range(64)] for i in range(64)]
    identity = tuple(tuple(F(i == j) for j in range(64)) for i in range(64))
    templates = [Template(3, 26, ("DECLARED_SYNTHETIC_ANCESTOR", 26), tuple(map(tuple, base26)), identity,
                          split_basis(base26, 26, 3)),
                 Template(3, 7, ("R437_COPY", 475, 515, 0, 28416, "common"), tuple(map(tuple, base7)), identity,
                          split_basis(base7, 7, 3))]
    fixtures = [oracle.fixture(template, 2, high=1) for template in templates]
    specifications = {code: compile_specification(code, template, fixtures[code][0])
                      for code, template in enumerate(templates)}
    need(all(spec.good for spec in specifications.values()), "actual compiled good low branches")
    pivots = [oracle.good_pivots(oracle.projector(template, low, high, 2), template.rank, 9)
              for template, (low, high) in zip(templates, fixtures)]

    arena, indices = Arena(5), Arena(14)
    modulus = arena.input(9)
    ring = Ring(modulus)
    # ROOT4096 -> GOOD rank26, width1664 -> current COPY7, width182.
    # The ancestor is a legal declared grammar probe, not a claimed actual
    # R437 owner/idle descriptor or a fresh large-prime selected execution.
    program = Program.fixture(indices, arena, 4096, 2, [(0, 0, 26, 0, False, False)], 2)
    fields = Fields.fixture(indices, arena, [(code, high) for code, (_low, high) in enumerate(fixtures)], 2)
    original_program, original_fields = body(program.tape), body(fields.tape)
    protected_arena, protected_indices = set(arena.live), set(indices.live)
    observed = []
    for i in (0, 26, 64, 181):
        coordinate = indices.input(i)
        request = Request("child", coordinate, child_kind="good")
        expected = 2 * pivots[0][i // 64] * pivots[1][i // 26] % 9
        with no_decode():
            result = coefficient(ring, indices, program, fields, specifications, 1, request)
            expected_word = arena.literal(expected)
            need(Unsigned(arena).compare(result, expected_word) == 0, "actual generated two-level unit coefficient")
        need(expected % 3 != 0, "generated value remains a unit")
        observed.append(dict(coordinate=i, value=expected))
        arena.free_many(result, expected_word)
        indices.free(coordinate)
        numerical_return(arena, protected_arena)
        numerical_return(indices, protected_indices)
        need(body(program.tape) == original_program and body(fields.tape) == original_fields
             and program.tape.head == fields.tape.head == 1, "borrowed encoded source/prefixes preserved")

    coordinate = indices.zero()
    with no_decode():
        incoming = Callback(ring, indices, program, fields, specifications, 1, allow_fallback=True)
        child_program = extend(incoming, Request("child", coordinate, child_kind="good"))
        incoming.close()
    level = indices.input(2)
    metadata, parent, child = child_program.step(level)
    expected_parent, expected_child = indices.input(1664), indices.input(182)
    need(metadata == (0, 1, 7, 0, 0, 0) and Unsigned(indices).compare(parent, expected_parent) == 0
         and Unsigned(indices).compare(child, expected_child) == 0, "actual nonterminal descriptor extent and source")
    indices.free_many(level, parent, child, expected_parent, expected_child, coordinate)
    child_program.tape.clear()

    controls = []
    for name, current, table in [
        ("foreign_current_source", 3, specifications),
        ("wrong_ancestor_rank", 1, {0: replace(specifications[0], template=replace(templates[0], rank=25)), 1: specifications[1]}),
        ("wrong_current_prefix_code", 0, specifications),
    ]:
        coordinate = indices.zero()
        try:
            with no_decode():
                value = coefficient(ring, indices, program, fields, table, current,
                                    Request("child", coordinate, child_kind="good"))
        except ValueError as error:
            controls.append(dict(control=name, rejected_by=str(error)))
        else:
            arena.free(value)
            raise ValueError("accepted encoded source mutation: " + name)
        finally:
            indices.free(coordinate)
        numerical_return(arena, protected_arena)
        numerical_return(indices, protected_indices)
        need(body(program.tape) == original_program and body(fields.tape) == original_fields
             and program.tape.head == fields.tape.head == 1, "failed source binding preserves borrowed bytes/heads")
    program.tape.clear()
    fields.tape.clear()
    ring.close()
    arena.free(modulus)
    numerical_return(arena, set())
    numerical_return(indices, set())
    result = dict(status="PASS_ENCODED_R437_COPY_COEFFICIENT_PROBE", q=3, atom_precision=2,
                  actual_R437_center=475, actual_R437_frame=515, copied_projector_rank=7,
                  synthetic_ancestor_rank=26, root_width=4096, parent_width=1664,
                  child_width=182, child_is_nonterminal=True,
                  generated_coefficients=observed, child_metadata=list(metadata), controls=controls,
                  runtime_host_numerical_decoding=False,
                  scope="Authenticated reused numerical components, actual COPY projector and explicit finite new source record, synthetic ancestor; no full R437 catalogue, payload, stock, physical CALL/RETURN or all-size cost proof")
    path = HERE / "CALLBACK-PROBE.json"
    if "--write-result" in sys.argv:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(json.loads(path.read_bytes()) == result, "callback probe receipt differs")
    print(result["status"] + " parent=1664 child=182 controls=3 no_decode=true")


if __name__ == "__main__":
    main()
