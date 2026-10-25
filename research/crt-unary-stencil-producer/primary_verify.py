"""Observer-only verification of the literal unary producer and consumer."""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
MACHINE_SHA = "1cb27312932914eb631078bd56e85feb1dc6c4191e9d1962b2cc3a7e1cfb8df7"
ADAPTER_SHA = "40794cd2e2936f0f5e42fac1bb51b65c951a2ab56b7e88824e8c2d09a3dbf40e"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name, path, expected=None):
    data = path.read_bytes()
    if expected is not None:
        need(sha256(data).hexdigest() == expected, "authenticated predecessor source: " + name)
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(data, str(path), "exec", dont_inherit=True, optimize=0), module.__dict__)
    return module


def public_inputs(machine, shape):
    return tuple(machine.Tape([machine.LEFT] + ["1"] * n + [machine.END]) for n in shape)


def observed_run(producer, machine, shape, mutant=None):
    inputs = public_inputs(machine, shape)
    before = [t.cells[:] for t in inputs]
    allocated = []

    def fresh():
        t = machine.Tape()
        allocated.append(t)
        return t

    work, stencil = producer.produce(*inputs, fresh, **(mutant or {}))
    need(len(work) == 8 and len(allocated) == 9, "fixed eight private plus one output role")
    protected = all(t.cells[:len(old)] == old and all(x == machine.BLANK for x in t.cells[len(old):])
                    for t, old in zip(inputs, before))
    private_blank = all(t.cells[0] == machine.LEFT and all(x == machine.BLANK for x in t.cells[1:])
                        for t in work)
    heads = all(t.head == 0 for t in inputs + work + (stencil,))
    all_tapes = inputs + work + (stencil,)
    counts = {"reads": sum(t.reads for t in all_tapes),
              "writes": sum(t.writes for t in all_tapes),
              "moves": sum(t.moves for t in all_tapes)}
    counts["actions"] = sum(counts.values())
    counts["visited_cells"] = sum(len(t.cells) for t in all_tapes)
    return stencil, {"geometry_G_H_K_Y_J_B": list(shape), **counts,
                     "protected_input": protected, "private_blank": private_blank,
                     "heads_returned": heads}, inputs, work


def case(producer, machine, adapter, shape, consume=False):
    g, h, k, y, j, b = shape
    stencil, receipt, inputs, work = observed_run(producer, machine, shape)
    expected = adapter.geometry_stencil(g, h, y, (j,), k, b, machine)
    need(stencil.cells == [machine.LEFT] + expected + [machine.END], "actual predecessor stencil equality")
    need(receipt["protected_input"] and receipt["private_blank"] and receipt["heads_returned"],
         "producer complete boundary")
    length = 2*h+y+b
    need(receipt["actions"] == 33*h+25*k+38*y-6*g-j+12*b+335,
         "written exact successful setup action census")
    need(receipt["actions"] <= 63*length+335, "written linear setup bound")
    need(receipt["visited_cells"] == 4*h+2*k+4*y-g+2*b+38,
         "written exact visited-space census")
    need(receipt["visited_cells"] <= 6*length+38, "written visited-space bound")
    receipt["stencil_bits"] = length
    receipt["stencil_canonical_sha256"] = sha256(json.dumps(expected, separators=(",", ":")).encode()).hexdigest()
    if consume:
        original = stencil.cells[:]
        prior_stencil_actions = stencil.actions
        counter, mask = machine.transduce(stencil)
        expected_bits, old_receipt = adapter.audit(expected, machine)
        need(stencil.cells == original and stencil.head == 0 and counter.head == mask.head == 0,
             "unchanged consumer protects retained stencil and returns heads")
        need(all(x == machine.BLANK for x in counter.cells[1:]), "consumer private cleanup")
        bits = "".join(mask.cells[1:-1])
        need(bits == expected_bits, "unchanged consumer complete BAD mask equality")
        need(sum(t.actions for t in (stencil, counter, mask)) - prior_stencil_actions == old_receipt["total_cell_head_actions"],
             "exact unchanged consumer action invoice")
        receipt["consumer"] = {"addresses": len(bits), "good": bits.count("0"),
                               "mask_sha256": sha256(bits.encode()).hexdigest(),
                               "prior_consumer_action_formula": old_receipt["total_cell_head_actions"]}
    return receipt


def rejections(producer, machine):
    shapes = ((0, 1, 5, 5, 0, 0), (2, 1, 6, 6, 0, 0),
              (2, 2, 5, 5, 0, 0), (1, 1, 5, 5, 1, 0))
    rows = []
    for shape in shapes:
        inputs = public_inputs(machine, shape)
        before = [t.cells[:] for t in inputs]
        allocated = []

        def fresh():
            t = machine.Tape()
            allocated.append(t)
            return t

        rejected = False
        try:
            producer.produce(*inputs, fresh)
        except ValueError:
            rejected = True
        need(rejected, "invalid arithmetic geometry rejected")
        need(all(t.head == 0 for t in inputs + tuple(allocated)), "rejected geometry heads returned")
        need(all(all(x == machine.BLANK for x in t.cells[1:]) for t in allocated),
             "rejected geometry private and output data erased")
        need(all(t.cells[:len(old)] == old for t, old in zip(inputs, before)), "reject input protected")
        rows.append({"shape": list(shape), "actions": sum(t.actions for t in inputs + tuple(allocated))})
    # Unique LEFT and initially blank tail are infrastructure. These defects
    # occur inside that contract: bad data symbol, missing END, END followed
    # immediately by a nonblank symbol.
    for defect in ("bad_symbol", "missing_end", "nonblank_after_end"):
        inputs = public_inputs(machine, (1, 1, 5, 5, 0, 0))
        if defect == "bad_symbol":
            inputs[0].cells[1] = "0"
        elif defect == "missing_end":
            inputs[0].cells[-1] = machine.BLANK
        else:
            inputs[0].cells.append("1")
        before = [t.cells[:] for t in inputs]
        allocated = []

        def fresh():
            t = machine.Tape()
            allocated.append(t)
            return t

        rejected = False
        try:
            producer.produce(*inputs, fresh)
        except ValueError:
            rejected = True
        need(rejected and all(t.head == 0 for t in inputs + tuple(allocated)), "grammar defect rejected and heads returned")
        need(all(all(x == machine.BLANK for x in t.cells[1:]) for t in allocated), "grammar rejection cleanup")
        need(all(t.cells[:len(old)] == old for t, old in zip(inputs, before)), "grammar rejection input protected")
        rows.append({"defect": defect, "actions": sum(t.actions for t in inputs + tuple(allocated))})
    return rows


def authentication_controls(machine_path, adapter_path):
    rows = []
    with tempfile.TemporaryDirectory(prefix="unary-stencil-auth-") as directory:
        for name, path, expected in (("machine", machine_path, MACHINE_SHA),
                                     ("adapter", adapter_path, ADAPTER_SHA)):
            corrupted = Path(directory) / (name + ".py")
            corrupted.write_bytes(path.read_bytes() + b"\nraise RuntimeError('UNAUTHENTICATED_BYTES_EXECUTED')\n")
            rejected = False
            try:
                load("damaged_" + name, corrupted, expected)
            except ValueError as exc:
                rejected = "authenticated predecessor source" in str(exc)
            need(rejected, "damaged source must reject before compile/exec")
            rows.append({"source": name, "damaged_bytes_rejected_before_exec": True})
    return rows


def controls(producer, machine, adapter):
    shape = (1, 2, 5, 7, 1, 1)
    g, h, k, y, j, b = shape
    expected = [machine.LEFT] + adapter.geometry_stencil(g, h, y, (j,), k, b, machine) + [machine.END]
    expected_bits, _ = adapter.audit(expected[1:-1], machine)
    rows = []
    for name in ("include_parity", "wrong_lower_pivot", "wrong_upper_pivot", "omit_cleanup", "omit_output_return"):
        stencil, receipt, inputs, work = observed_run(producer, machine, shape, {name: True})
        if name in ("include_parity", "wrong_lower_pivot", "wrong_upper_pivot"):
            detected = stencil.cells != expected
            counter, mask = machine.transduce(stencil)
            need("".join(mask.cells[1:-1]) != expected_bits, "semantic mutant must alter actual consumer mask")
        elif name == "omit_cleanup":
            detected = not receipt["private_blank"]
        else:
            detected = not receipt["heads_returned"]
        need(detected, "named faulty producer unexpectedly accepted: " + name)
        rows.append({"mutant": name, "detected": True})
    return rows


def guardrail(path):
    tree = ast.parse(path.read_text())
    forbidden = {"len", "range", "enumerate", "int", "str", "format", "sum", "min", "max", "pow"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            need(node.func.id not in forbidden, "host arithmetic/coordinate primitive")
        if isinstance(node, ast.Attribute):
            need(node.attr not in ("head", "cells", "reads", "writes", "moves", "actions"),
                 "producer inspects emulator observer")
        need(not isinstance(node, (ast.BinOp, ast.Subscript)), "host arithmetic or indexed geometry")
    return "PASS_AST_SCOPE_GUARDRAIL_NOT_A_FORMAL_MACHINE_CERTIFICATE"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, default=HERE / "source")
    parser.add_argument("--consumer-path", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    producer = load("unary_producer", HERE / "producer.py")
    machine_path = args.consumer_path or args.source_dir / "predecessor_machine.py"
    adapter_path = args.source_dir / "predecessor_adapter.py"
    machine = load("predecessor_machine", machine_path, MACHINE_SHA)
    adapter = load("predecessor_adapter", adapter_path, ADAPTER_SHA)
    rows = []
    for g in (1, 2, 3):
        for h in (g, g+1):
            for k in (g+4, g+5):
                for j in (0, 1, 2):
                    for padding in (0, 1):
                        for b in (0, 1):
                            rows.append(case(producer, machine, adapter, (g, h, k, j+k+padding, j, b)))
    rows.append(case(producer, machine, adapter, (1, 100, 5, 200, 50, 100)))
    consumer_rows = [case(producer, machine, adapter, shape, True) for shape in
                     ((1, 1, 5, 5, 0, 0), (1, 2, 5, 7, 1, 1), (2, 2, 6, 6, 0, 0), (1, 1, 6, 7, 1, 0))]
    result = {"status": "PASS_LITERAL_UNARY_ONE_TARGET_STENCIL_PRODUCER_NO_NEW_KAPPA",
              "producer_sha256": sha256((HERE / "producer.py").read_bytes()).hexdigest(),
              "predecessor_head": "4f49743a9df0cf7501cdc62bd5707a122fa071e9",
              "predecessor_source_sha256": {"machine": MACHINE_SHA, "adapter": ADAPTER_SHA},
              "setup_action_formula": "33H+25K+38Y-6G-J+12B+335 <= 63L+335; L=2H+Y+B",
              "setup_visited_space_formula": "4H+2K+4Y-G+2B+38 <= 6L+38",
              "cases": rows, "producer_cases": len(rows),
              "total_producer_actions": sum(x["actions"] for x in rows),
              "consumer_cases": consumer_rows,
              "rejections": rejections(producer, machine),
              "controls": controls(producer, machine, adapter),
              "authentication_controls": authentication_controls(machine_path, adapter_path),
              "guardrail": guardrail(HERE / "producer.py"),
              "scope": "Canonical unary six-field one-target family only; input encoding and general descriptor production remain unpriced; no complete E evaluator, CRT supplier, precision or kappa claim"}
    if args.output is not None:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
