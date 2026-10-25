#!/usr/bin/env python3
"""Source-relative root address partition; mocked endpoints are not C arithmetic.

SPDX-License-Identifier: Apache-2.0
Sagar Thakrar (thakrarsagar), with substantial OpenAI Codex assistance.
Authenticated-cohort loading/cleanup adapted from complex-parent-return-refinement.
Jose Manuel/jmbarrancoml's PR3385 execution methods remain unchanged.
"""
from contextlib import contextmanager
import hashlib
import importlib
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType, SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/physical-complex-controller"


def require(value, why):
    if not value:
        raise ValueError(why)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def authenticate(corrupt=False):
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    hashes = {}
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        raw = (ROOT / row["path"]).read_bytes()
        if corrupt and row["path"].endswith("/root_layer.py"):
            raw += b"\n# altered source\n"
        require(sha(raw) == row["sha256"], "input changed: " + row["path"])
        hashes[row["path"]] = row["sha256"]
    return hashes


@contextmanager
def runtime(hashes):
    before, old_path = set(sys.modules), sys.path[:]
    try:
        sys.path.insert(0, str(SOURCE))
        layer = importlib.import_module("root_layer")
        rt = SimpleNamespace(layer=layer, Count=layer.Count, Tape=layer.Tape,
                             words=importlib.import_module("words"),
                             session=importlib.import_module("session"))
        for name in set(sys.modules) - before:
            path = getattr(sys.modules[name], "__file__", None)
            if path and Path(path).is_relative_to(ROOT):
                require(str(Path(path).relative_to(ROOT)) in hashes,
                        "unmanifested live module: " + str(path))
        yield rt
    finally:
        temporary = {}
        names = set(sys.modules) - before
        for name in names:
            for value in tuple(vars(sys.modules[name]).values()):
                if isinstance(value, tempfile.TemporaryDirectory):
                    temporary[id(value)] = value
        for value in temporary.values():
            value.cleanup()
            require(not Path(value.name).exists(), "temporary source survived cleanup")
        for name in names:
            sys.modules.pop(name, None)
        sys.path[:] = old_path


def body(rt, tape):
    values = tape.cells[1:]
    end = next((i for i, x in enumerate(values) if x == rt.words.BLANK), len(values))
    require(all(x == rt.words.BLANK for x in values[end:]), "nonblank hidden tail")
    return tuple(values[:end])


def number(rt, count):
    values = body(rt, count.tape)
    require(values[-1] == rt.words.RIGHT and all(x in (0, 1) for x in values[:-1]), "Count encoding")
    return sum(x << i for i, x in enumerate(values[:-1]))


def fill(tape, values):
    tape.clear()
    for x in values:
        tape.append(x)
    tape.rewind()


def permute(values, record_bits, address_mask):
    require(len(values) % record_bits == 0, "whole records")
    result = [0] * len(values)
    for source in range(len(values) // record_bits):
        target = source ^ address_mask
        result[target * record_bits:(target + 1) * record_bits] = values[source * record_bits:(source + 1) * record_bits]
    return tuple(result)


def layout_mask(rt, widths, active, width, spacing, residue):
    """Use the inherited backend's left-counted position to check LSB convention."""
    Layout = importlib.import_module("compact_layout").Layout
    names = tuple("field" + str(i) for i in range(len(widths)))
    counts = [rt.Count.literal(x) for x in widths]
    record = rt.Count.literal(1)
    plan = Layout(names, tuple(counts), record)
    mask = 0
    try:
        for j in range(width):
            low = rt.Count.literal(residue + j * spacing)
            position = plan.bit_position(names[active], low)
            try:
                mask |= 1 << (sum(widths) - number(rt, position) - 1)
            finally:
                position.close()
                low.close()
        return mask
    finally:
        plan.close()
        record.close()
        for count in counts:
            count.close()


def reject(call, phrase):
    try:
        call()
    except ValueError as error:
        require(phrase in str(error), "unexpected rejection: " + str(error))
        return
    raise ValueError("accepted negative control: " + phrase)


def layer_class(rt, replacement=None):
    if replacement is None:
        return rt.layer.RootLayer
    raw = (SOURCE / "root_layer.py").read_text()
    old, new = replacement
    require(raw.count(old) == 1, "unique source mutation")
    module = ModuleType("root_address_mutant")
    module.__file__ = str(SOURCE / "root_layer.py")
    exec(compile(raw.replace(old, new), module.__file__, "exec"), module.__dict__)
    return module.RootLayer


def fixture(rt, selected, replacement=None, corrupt_padding=False):
    # A small algebraically consistent *manual* root plan; compute() is not run.
    # Sixteen-bit tags are unique across every complete two-coefficient record.
    v = dict(left=1, right=1, selected=selected, K=2, residue=1, q0=2, qF=1, qB=1,
             H=1, G=1, work_bits=4, coefficients=2, outer_rows=2, d=selected,
             prefixes=4, original_rows=16, padded_rows=18, core_front=0,
             core_back=2, core_width=selected-4, zero=0)
    record_bits = 2 * v["work_bits"] * v["coefficients"]
    row_axes = (selected - 2) * 2 + 1
    v["row_bits"] = (1 << row_axes) * record_bits
    addresses = 2 * (1 << (1 + 2 * selected + 1))
    require(addresses <= 65536, "distinct coordinate tag capacity")
    payload = tuple((i >> b) & 1 for i in range(addresses) for b in range(record_bits))
    counts = {name: rt.Count.literal(value) for name, value in v.items()}
    layer = object.__new__(layer_class(rt, replacement))
    layer.plan = SimpleNamespace(count=counts.__getitem__)
    layer.current = rt.Tape()
    layer.pool = rt.layer.ScratchPool(32)
    layer.scope = rt.layer.OuterScope(layer.pool)
    layer.padding = rt.layer.RowPadding()
    fill(layer.current, payload)
    leaf_output, core_output = rt.Tape(), rt.Tape()
    calls, descriptors = [], []
    leaf_masks = [layout_mask(rt, (1, 6, 2*(selected-3)+1), 1, 3, 2, 1),
                  layout_mask(rt, (1+2*(selected-1), 2, 1), 1, 1, 2, 1)]
    core_mask = layout_mask(rt, (0, 1, 1, 0, 2*(selected-4), 0, 1, 2), 4, selected-4, 2, 1)
    whole_mask = layout_mask(rt, (1, 2*selected, 1), 1, selected, 2, 1)
    require(whole_mask != layout_mask(rt, (1, 2*selected, 1), 1, selected, 2, 0),
            "opposite residue is distinguishable")

    def leaf_run(source, axes, width, spacing, residue, component_bits, coefficients, outer_rows):
        a = tuple(number(rt, x) for x in axes)
        scalar = tuple(number(rt, x) for x in (width, spacing, residue, component_bits, coefficients, outer_rows))
        expected = [(1, 6, 2 * (selected - 3) + 1), (1 + 2 * (selected - 1), 2, 1)]
        require(len(calls) < 2 and a == expected[len(calls)], "reserved leaf axes")
        require(scalar == ((3 if not calls else 1), 2, 1, 4, 2, 2), "reserved leaf scalar descriptors")
        # rho+jK counts from the low end of the active field, as in run_leaf.
        mask = sum(1 << (a[2] + scalar[2] + scalar[1]*j) for j in range(scalar[0]))
        require(mask == leaf_masks[len(calls)], "leaf backend bit convention")
        rt.layer.origin(leaf_output)
        fill(leaf_output, permute(body(rt, source), record_bits, mask))
        calls.append({"axes": list(a), "scalar": list(scalar), "xor_mask": mask})
        return leaf_output

    expected_machine = dict(prefixes=4, rows=18, front=0, compact_bits=1, before=0,
                            width=selected-4, after=0, back=2, spacing=2, guard=1,
                            residue=1, component_bits=4, coefficients=2, root_width=selected)

    def machine_run(source, supplied):
        actual = {name: number(rt, value) for name, value in supplied.items()}
        require(actual == expected_machine, "all machine descriptors")
        descriptors.append(actual)
        current = body(rt, source)
        expected_extent = 4 * 18 * v["row_bits"]
        require(len(current) == expected_extent, "padded full extent")
        result = []
        mask = sum(1 << (actual["back"] + actual["compact_bits"] + actual["residue"] + actual["spacing"]*j)
                   for j in range(actual["width"]))
        require(mask == core_mask, "core backend bit convention")
        for prefix in range(4):
            start = prefix * 18 * v["row_bits"]
            kept = current[start:start + 16 * v["row_bits"]]
            padding = current[start + 16*v["row_bits"]:start + 18*v["row_bits"]]
            require(not any(padding), "added rows zero")
            for row in range(16):
                values = kept[row*v["row_bits"]:(row+1)*v["row_bits"]]
                result.extend(permute(values, record_bits, mask))
            result.extend(padding)
        if corrupt_padding:
            result[16 * v["row_bits"]] = 1
        fill(core_output, result)
        return core_output

    layer.leaf = SimpleNamespace(run_leaf=leaf_run)
    layer.machine = SimpleNamespace(run=machine_run)
    try:
        with rt.session.sealed_constructors(), layer.scope.installed():
            layer.reserved_leaves()
        require(len(calls) == 2, "both reserved leaves")
        layer.fast_core()
        # Independent original-address positions, without any partition descriptors.
        expected_mask = sum(1 << bit for bit in range(2, 2*selected+1, 2))
        require(expected_mask == whole_mask, "whole backend bit convention")
        expected = permute(payload, record_bits, expected_mask)
        require(body(rt, layer.current) == expected, "complete root address permutation")
        require(layer.current.head == 1, "returned canonical head")
        require(not body(rt, leaf_output) and not body(rt, core_output) and not body(rt, layer.padding.output),
                "all returned endpoints consumed")
        require(not layer.pool.live and not layer.padding.pool.live, "closed physical scratch")
        require(all(number(rt, counts[k]) == x and counts[k].tape.head == 1 for k, x in v.items()),
                "borrowed descriptors preserved")
        return dict(selected=selected, plan=v, address_records=addresses, record_bits=record_bits,
                    input_sha256=sha(bytes(payload)), output_sha256=sha(bytes(expected)),
                    leaf_calls=calls, machine=descriptors[0], selected_xor_mask=expected_mask)
    finally:
        layer.pool.empty()
        for count in counts.values():
            count.close()
        for tape in (layer.current, leaf_output, core_output, layer.padding.output):
            rt.layer.origin(tape)
            tape.clear()


def main():
    hashes = authenticate()
    reject(lambda: authenticate(True), "input changed:")
    with runtime(hashes) as rt:
        cases = [fixture(rt, d) for d in (5, 6)]
        controls = [
            (('residue="residue"', 'residue="zero"'), "all machine descriptors"),
            (('width="core_width"', 'width="selected"'), "all machine descriptors"),
            (('prefixes="prefixes"', 'prefixes="original_rows"'), "all machine descriptors"),
            (('self.apply_leaf(left, self.c("qB"), self.c("right"))', 'pass'), "both reserved leaves"),
        ]
        for replacement, reason in controls:
            reject(lambda: fixture(rt, 5, replacement), reason)
        reject(lambda: fixture(rt, 5, corrupt_padding=True), "nonzero padded row returned")
    result = {"schema_version": 1, "scope": "root address partition with declared permutation endpoints; no C arithmetic",
              "input_hashes": hashes, "fixtures": cases,
              "controls": ["source corruption", "wrong residue", "wrong core width", "wrong prefix count",
                           "omitted right leaf", "nonzero padded output"],
              "limitations": ["manual plans, not RootPlan.compute", "leaf and recursive endpoints are mocks",
                              "no phases, expansion, normalization, truncation or full RootLayer.run",
                              "finite tags establish tested address behavior, not universal C arithmetic"]}
    if "--emit" in sys.argv:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "frozen receipt differs")
        print("PASS: 2 complete address fixtures; all 14 machine descriptors; 6 rejection controls")


if __name__ == "__main__":
    main()
