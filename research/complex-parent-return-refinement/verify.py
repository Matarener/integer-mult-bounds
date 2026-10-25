#!/usr/bin/env python3
"""Independent executable controls for the source-relative parent return.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar (thakrarsagar), with substantial OpenAI Codex assistance.
Jose Manuel/jmbarrancoml's PR3385 execution bodies are unchanged frozen inputs.
The fixture substitutes only a declared callee endpoint, not the controller.
"""

from contextlib import contextmanager
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FROZEN = "inputs/pr3385/"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(bytes(raw)).hexdigest()


def authenticate(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    result, hashes = {}, {}
    rows = [(root, row) for row in manifest["files"] if row["usage"] == "input"]
    rows += [(HERE, row) for row in manifest["frozen_sources"]]
    for base, row in rows:
        raw = (base / row["path"]).read_bytes()
        require(digest(raw) == row["sha256"], "Input changed: " + row["path"])
        hashes[row["path"]] = row["sha256"]
        if base == HERE:
            result[row["path"]] = raw
    return result, hashes


def execute(name, raw, filename):
    module = ModuleType(name)
    module.__file__ = str(filename)
    sys.modules[name] = module
    exec(compile(raw, str(filename), "exec"), module.__dict__)
    return module


@contextmanager
def runtime(raw):
    """One cold source cohort; only its path anchor is supplied by this loader."""
    before, old_path = set(sys.modules), sys.path[:]
    require("cohort" not in before, "fresh source cohort required")
    try:
        sys.path.insert(0, str(HERE / FROZEN))
        cohort = execute("cohort", raw[FROZEN + "cohort.py"], ROOT / "research/physical-complex-controller/cohort.py")
        cohort.activate()
        machine = importlib.import_module("machine")
        counts = importlib.import_module("cardinal_counts")
        parking = importlib.import_module("parking")
        words = importlib.import_module("words")
        ordinary = importlib.import_module("ordinary")
        code = importlib.import_module("macro_code")
        scalar = importlib.import_module("scalar_program")
        def native_factory():
            return ordinary.Ordinary(2, SimpleNamespace(codes=SimpleNamespace(q=2)),
                                     SimpleNamespace(families=0), (code.Code((("unreachable",),), 0),), capacity=64)
        yield SimpleNamespace(machine=machine, Count=counts.Count, Tape=machine.Tape, parking=parking,
                              words=words, scalar=scalar, native_factory=native_factory, cohort=cohort)
    finally:
        # All inherited archive loaders retain their TemporaryDirectory owners.
        temporary, names = {}, set(sys.modules) - before
        for name in names:
            module = sys.modules.get(name)
            for value in tuple(vars(module).values()) if module is not None else ():
                if isinstance(value, tempfile.TemporaryDirectory):
                    temporary[id(value)] = value
        paths = [Path(value.name) for value in temporary.values()]
        for value in temporary.values():
            value.cleanup()
        require(all(not path.exists() for path in paths), "inherited temporary directory survived cleanup")
        for name in names:
            sys.modules.pop(name, None)
        sys.path[:] = old_path


def body(rt, tape):
    cells = tuple(tape.cells[1:])
    end = next((i for i, value in enumerate(cells) if value == rt.words.BLANK), len(cells))
    require(all(value == rt.words.BLANK for value in cells[end:]), "hidden nonblank tape tail")
    return cells[:end]


def origin(rt, tape):
    require(tape.head == 1, "noncanonical role head")
    require(tape.cells[0] == rt.words.LEFT, "owned origin marker not normalized")


def fill(tape, values):
    tape.clear()
    for value in values:
        tape.append(value)
    tape.rewind()


def count_value(rt, tape):
    symbols = body(rt, tape)
    require(symbols and symbols[-1] == rt.words.RIGHT and all(bit in (0, 1) for bit in symbols[:-1]),
            "observer received a malformed Count")
    return sum(bit << i for i, bit in enumerate(symbols[:-1]))


def signal(size, salt):
    return tuple(((i * 37 + i // 5 + salt * 11) >> (salt % 3)) & 1 for i in range(size))


class Binding:
    """Reduced fixed control, explicitly not the selected O73 numerical payload."""
    dimension, families, slots, private = 3, 2, 3, 2
    events = ("first", "second")
    cover = SimpleNamespace(size=2)

    def __init__(self, target, rank):
        self.code = (("marker", -1, "before"), ("child", 17, target, rank),
                     ("marker", -1, "resume"), ("identity", -1, 0), ("child", 31, target, rank))

    def group_count(self, event):
        require(event in (0, 1), "fixture event range")
        return 2

    def group(self, event, subgroup, cover):
        require(event in (0, 1) and subgroup in (0, 1) and cover in (0, 1), "fixture finite group range")
        keys = ((1, 1), (0, 0)) if (event + subgroup + cover) % 2 else ((0, 1), (1, 0))
        return SimpleNamespace(keys=keys, code=self.code, recipes={})


def setup(rt, machine_type, rank):
    target = 3 if rank == 1 else 1
    binding = Binding(target, rank)
    recipe = rt.scalar.ScalarProgram("scale", -1, 1)
    machine = machine_type(binding, rt.native_factory(), {recipe.key: recipe})
    values = dict(prefixes=2, rows=8 if rank == 1 else 4, front=1, compact_bits=0,
                  before=1 if rank == 1 else 2, width=3, after=2 if rank == 1 else 1,
                  back=1, spacing=rank, guard=1, residue=rank - 1,
                  component_bits=2, coefficients=1, root_width=3)
    address_bits = values["front"] + values["before"] + 3 * values["compact_bits"]
    address_bits += values["width"] * values["spacing"] + values["after"] + values["back"]
    row_bits = (1 << address_bits) * 2 * values["component_bits"] * values["coefficients"]
    unused = values["rows"] // (binding.families * binding.cover.size)
    packet_bits = values["prefixes"] * unused * row_bits
    total = values["prefixes"] * values["rows"] * row_bits
    source = rt.Tape()
    payload = signal(total, 2 + rank)
    fill(source, payload)
    rt.machine.copy_symbols(source, machine.roles["current"])
    borrowed = {name: rt.Count.literal(value) for name, value in values.items()}
    for name, value in borrowed.items():
        rt.machine.copy_symbols(value.tape, machine.roles[name])
    derived = dict(columns=1, unused=unused, row_bits=row_bits, gaussians=packet_bits // (2 * values["component_bits"]))
    for name, value in derived.items():
        encoded = rt.Count.literal(value)
        rt.machine.copy_symbols(encoded.tape, machine.roles[name])
        encoded.close()
    machine.root, machine.closed, machine.mode = True, False, "group"
    machine.event = machine.subgroup = machine.cover_index = machine.pc = 1
    machine.group = binding.group(1, 1, 1)
    machine.bank.select(machine.group.keys)
    machine.bank.gather(machine.roles["current"], *(machine.c(name) for name in ("prefixes", "unused", "row_bits")))
    for i, tape in enumerate(machine.private):
        fill(tape, signal(packet_bits, 11 + i))
    return SimpleNamespace(machine=machine, binding=binding, target=target, rank=rank, values=values,
                           derived=derived, source=source, payload=payload, borrowed=borrowed,
                           packet_bits=packet_bits, row_bits=row_bits, unused=unused)


def expected_header(case):
    values = (1, 1, 1, 1, 2, case.target, case.rank)
    bounds = (2, 2, 2, 2, 65536, 5, 3)
    return tuple((value >> bit) & 1 for value, bound in zip(values, bounds)
                 for bit in range(max(1, (bound - 1).bit_length())))


def validate_gather(rt, case):
    extent = case.unused * case.row_bits
    packets, records = [], []
    for slot, (family, cover) in enumerate(case.machine.group.keys):
        expected = ()
        for prefix in range(case.values["prefixes"]):
            start = ((prefix * 2 + family) * 2 + cover) * extent
            expected += case.payload[start:start + extent]
        require(body(rt, case.machine.bank.packets[slot]) == expected, "oracle gathered owner packet")
        packets.append(expected)
        records.append({"slot": slot, "owner": [family, cover], "sha256": digest(expected)})
    require(len(set(packets)) == len(packets), "selected owner packets must be distinguishable")
    require(not body(rt, case.machine.bank.packets[2]), "unselected slot is not empty")
    return records


def validate_child(rt, case, original_target):
    machine, expected = case.machine, dict(case.values)
    expected["rows"] = case.unused
    expected["width"] = case.rank
    expected["after"] += (3 - case.rank) * case.values["spacing"]
    actual = {name: count_value(rt, machine.capsule[name]) for name in rt.machine.INPUTS}
    require(actual == expected, "oracle child descriptor transition")
    require(body(rt, machine.capsule["current"]) == original_target, "oracle copied child target")
    require(case.values["width"] * case.values["spacing"] + case.values["after"] ==
            expected["width"] * expected["spacing"] + expected["after"], "oracle row extent identity")
    return expected


def expected_scatter(case, returned):
    result = list(case.payload)
    if case.target < case.binding.slots:
        family, cover = case.machine.group.keys[case.target]
        extent = case.unused * case.row_bits
        for prefix in range(case.values["prefixes"]):
            start = ((prefix * case.binding.families + family) * case.binding.cover.size + cover) * extent
            result[start:start + extent] = returned[prefix * extent:(prefix + 1) * extent]
    return tuple(result)


def validate_entry(rt, case, original_target, child, parked_symbols):
    machine = case.machine
    require((machine.mode, machine.root, machine.group, machine.event, machine.subgroup,
             machine.cover_index, machine.pc) == ("node", False, None, 0, 0, 0, 0), "oracle child control state")
    require(machine.bank.state == "closed" and machine.bank.source is None and machine.bank.selection is None,
            "oracle child bank metadata")
    require(machine.parking.stack.head - 1 == 4 * parked_symbols + len(machine.parked) + 1,
            "oracle complete frame extent")
    for name, tape in machine.roles.items():
        if name in rt.machine.INPUTS:
            require(count_value(rt, tape) == child[name], "oracle installed child descriptor")
        else:
            require(body(rt, tape) == (original_target if name == "current" else ()), "oracle child active role")
        origin(rt, tape)
    for tape in (*machine.bank.packets, *machine.private, *machine.capsule.values()):
        require(not body(rt, tape), "oracle child slot or consumed capsule not empty")
        origin(rt, tape)


def one_cut(rt, machine_type, rank, skip_header=False):
    case = setup(rt, machine_type, rank)
    machine = case.machine
    gathered = validate_gather(rt, case)
    borrowed_before = {name: body(rt, value.tape) for name, value in case.borrowed.items()}
    before = [body(rt, tape) for tape in machine.parked]
    target_tape = machine.packet(case.target)
    original_target = body(rt, target_tape)
    try:
        with rt.machine.sealed_constructors(), machine.scope.installed():
            machine.prepare_child(case.target, rank)
        child = validate_child(rt, case, original_target)
        if not skip_header:
            require(body(rt, machine.roles["header"]) == expected_header(case), "oracle saved header")
        parked_symbols = sum(len(body(rt, tape)) for tape in machine.parked)
        machine.enter_child()
        validate_entry(rt, case, original_target, child, parked_symbols)
        returned = original_target[rank:] + original_target[:rank]
        require(returned != original_target, "opaque callee endpoint must be observable")
        fill(machine.roles["current"], returned)
        fill(machine.private[1], (1, 0, 1))  # Child-owned state must be erased before restoration.
        machine.mode = "return"  # Declared callee endpoint, matching the run-loop cut.
        require(machine.return_node() is False, "oracle return mode")
        require((machine.root, machine.event, machine.subgroup, machine.cover_index, machine.pc) ==
                (True, 1, 1, 1, 2), "oracle saved PC and finite state")
        for i, tape in enumerate(machine.parked):
            expected = returned if tape is target_tape else () if tape is machine.roles["header"] else before[i]
            require(body(rt, tape) == expected, "oracle restored target or untouched role")
            origin(rt, tape)
        require(machine.bank.source is machine.roles["current"] and machine.bank.state == "gathered" and
                machine.bank.selection == {key: slot for slot, key in enumerate(machine.group.keys)}, "oracle reconstructed bank metadata")
        require(not body(rt, machine.output), "protected child output not consumed")
        machine.parking.empty()
        expected = expected_scatter(case, returned)
        machine.bank.scatter(machine.roles["current"], *(machine.c(name) for name in ("prefixes", "unused", "row_bits")))
        machine.bank.commit(machine.roles["current"])
        require(body(rt, machine.roles["current"]) == expected, "oracle owner packet scatter")
        require(body(rt, case.source) == case.payload and case.source.head == 1 and
                all(body(rt, value.tape) == borrowed_before[name] and value.tape.head == 1
                    for name, value in case.borrowed.items()), "oracle borrowed inputs preserved")
        return {"rank": rank, "target": case.target, "target_kind": "private" if case.target >= 3 else "bank",
                "parent_descriptors": case.values, "child_descriptors": child, "row_bits": case.row_bits,
                "packet_bits": case.packet_bits, "parked_roles": len(machine.parked),
                "gathered_packets": gathered,
                "parked_body_symbols": parked_symbols, "encoded_frame_symbols": 4 * parked_symbols + len(machine.parked) + 1,
                "empty_unselected_slot": 2, "callee": "cyclic left rotation by rank bits; conditional endpoint only",
                "returned_sha256": digest(returned), "source_sha256": digest(case.payload),
                "replacement_bank_sha256": digest(expected), "saved_next_PC": 2,
                "all_other_role_bodies_preserved": True, "all_return_heads_canonical": True}
    finally:
        machine.discard()
        case.source.clear()
        for value in case.borrowed.values():
            value.close()


def parking_controls(rt):
    roles = tuple(rt.Tape() for _ in range(7))
    parking = rt.parking.Parking(roles)
    saved, prefixes, lengths, symbols = [], [], [], set()
    for depth in range(12):
        words = [tuple(rt.parking.BODY[(depth + i + j) % len(rt.parking.BODY)]
                       for j in range((depth * i + i) % 23)) for i in range(7)]
        symbols.update(value for word in words for value in word)
        for tape, word in zip(roles, words):
            fill(tape, word)
        prefixes.append((body(rt, parking.stack), parking.stack.head))
        saved.append(words)
        start = parking.stack.head
        parking.park()
        length = 4 * sum(map(len, words)) + len(roles) + 1
        require(parking.stack.head - start == length and all(not body(rt, tape) for tape in roles), "opaque frame encoding")
        lengths.append(length)
    require(symbols == set(rt.parking.BODY), "opaque BODY alphabet coverage")
    for depth in reversed(range(12)):
        parking.restore()
        require([body(rt, tape) for tape in roles] == saved[depth], "opaque nested restoration")
        require((body(rt, parking.stack), parking.stack.head) == prefixes[depth], "older frame prefix changed")
        for tape in roles:
            origin(rt, tape)
            tape.clear()
    parking.empty()
    fill(roles[0], (12, 13, 0, 1))
    parking.park()
    parking.stack.step(-1)
    parking.stack.write(rt.parking.ROLE_END)
    parking.stack.step(1)
    rejects(parking.restore, "one parent frame available")
    parking.stack.write(rt.parking.FRAME_END)
    parking.stack.step(1)
    parking.restore()
    require(body(rt, roles[0]) == (12, 13, 0, 1), "controlled delimiter repair changed body")
    for tape in roles:
        tape.clear()
    parking.empty()
    return {"depth": 12, "roles": 7, "frame_lengths": lengths,
            "all_BODY_symbols_exercised": symbols == set(rt.parking.BODY),
            "BODY_symbols_exercised": sorted(symbols), "older_frames_preserved": True,
            "frame_delimiter_mutation_rejected": True}


def rejects(action, message):
    try:
        action()
    except ValueError as error:
        require(message in str(error), "unexpected failure: " + str(error))
        return
    raise ValueError("control accepted: " + message)


def mutant_controls(rt, raw):
    source = raw[FROZEN + "machine.py"].decode()
    changes = [
        ("after", "tail.multiply_small(self.binding.dimension - rank)",
         "tail.multiply_small(self.binding.dimension - rank + 1)", "oracle child descriptor transition", False),
        ("target", "transfer(self.output, self.packet(target))",
         "transfer(self.output, self.packet((target + 1) % self.binding.slots))", "oracle restored target or untouched role", False),
        ("PC", "self.cover_index, self.pc + 1, target, rank))",
         "self.cover_index, self.pc + 4, target, rank))", "oracle saved PC and finite state", True),
    ]
    records = []
    for name, old, new, reason, skip_header in changes:
        require(source.count(old) == 1, "unique frozen mutation site")
        changed = source.replace(old, new, 1).encode()
        module = execute("parent_return_mutant_" + name, changed, HERE / (FROZEN + "machine.py"))
        rejects(lambda: one_cut(rt, module.Machine, 1, skip_header), reason)
        records.append({"mutation": name, "old": old, "new": new, "sha256": digest(changed),
                        "detected_by": reason, "source_return_accepts_matching_alternate_PC": skip_header})
    header = rt.parking.FiniteFields((3,))
    tape = rt.Tape()
    fill(tape, (1, 1))
    rejects(lambda: header.read(tape), "finite header value")
    tape.clear()
    return {"source_mutants": records, "out_of_range_header_rejected": True,
            "limitation": "A header naming another identical child can pass the source guard; the independent expected transition detects it."}


def source_control():
    old_read = Path.read_bytes
    target = HERE / (FROZEN + "machine.py")
    def counterfeit(path):
        return b'raise RuntimeError("counterfeit executed")\n' if path == target else old_read(path)
    with patch.object(Path, "read_bytes", counterfeit):
        rejects(authenticate, "Input changed: " + FROZEN + "machine.py")
    return True


def build():
    raw, hashes = authenticate()
    source_control()
    with runtime(raw) as rt:
        cases = [one_cut(rt, rt.machine.Machine, rank) for rank in (1, 2)]
        parking = parking_controls(rt)
        mutants = mutant_controls(rt, raw)
    result = {"schema_version": 1, "status": "PASS_COMPLEX_PARENT_RETURN_REFINEMENT",
              "scope": "Conditional parent-cut refinement with unchanged source Tape/Count/controller bodies; reduced valid layouts, no selected O73 payload or numerical child implementation.",
              "inputs_sha256": hashes, "cases": cases, "parking": parking, "controls": mutants,
              "source_corruption_before_execution": True, "inherited_temporary_directories_cleaned": True}
    return json.loads(json.dumps(result))


def main():
    require(sys.argv[1:] in ([], ["--emit"]), "usage: verify.py [--emit]")
    result = build()
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "RESULT.json mismatch")
        print("PASS_COMPLEX_PARENT_RETURN_REFINEMENT: exact parent state, private/bank replacement, stack and mutation controls")


if __name__ == "__main__":
    main()
