"""Replay source-bound literal Count selection and independent failure controls.

Hiroki Kumazaki with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    checked = 0
    for row in sources["files"]:
        if row["usage"] == "input":
            require(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "source pin: " + row["path"])
            checked += 1
    predecessor = sources["predecessor"]
    require(sha256((HERE / predecessor["retained_path"]).read_bytes()).hexdigest()
            == predecessor["sha256"], "retained PR3486 proof")
    return checked


@contextmanager
def activate():
    # Direct execution also avoids stale bytecode from an earlier source tree.
    with tempfile.TemporaryDirectory(prefix="body-depth-bytecode-") as cache:
        sys.pycache_prefix = cache
        sys.path.insert(0, str(ROOT / "research/physical-ordinary-interchange"))
        import source
        source.activate()
        sys.path.insert(0, str(HERE))
        yield


def observe(count):
    """Checker only: no observer is called while the selector is running."""
    from words import RIGHT
    tape = count.tape
    cells = tape.cells if hasattr(tape, "cells") else tape.physical.cells
    end = cells.index(RIGHT, 1)
    digits = cells[1:end]
    require(bool(digits) and all(type(bit) is int and bit in (0, 1) for bit in digits),
            "canonical binary observation")
    require(len(digits) == 1 or digits[-1] == 1, "no leading zero")
    return sum(bit << position for position, bit in enumerate(digits))


def run_case(args, implementation=None):
    import encoded
    import selector
    from cardinal_counts import Count
    from check_support import no_decode
    from scratch_pool import ScratchPool
    from session import sealed_constructors
    from independent import specification, slab_specification, padded_guards
    e, q, m, r, w_factor, compatibility, numerator, denominator = args
    profile = encoded.Profile(numerator=numerator, denominator=denominator,
                              dimension=m, child_rank=r, row_factor=w_factor)
    original = Count.literal(e)
    before = bytes(original.tape.cells)
    pool = ScratchPool(24)
    candidate = None
    try:
        with no_decode(), sealed_constructors(), pool.install():
            try:
                candidate = (implementation or selector.select_body_stock)(
                    original, q, profile, compatibility)
                observed = {key: value if key == "fits" else observe(value)
                            for key, value in candidate.items()}
            finally:
                if candidate is not None:
                    selector.close_plan(candidate)
            pool.empty()
        require(bytes(original.tape.cells) == before and original.tape.head == 1,
                "borrowed original restored")
        expected = specification(*args)
        require(expected == slab_specification(*args), "independent inverse-depth agreement")
        require(canonical(observed) == canonical(expected), "literal Count plan equals independent specification")
        guard = padded_guards(observed, q, m, w_factor, compatibility) if observed["fits"] else None
        return dict(args=list(args), plan=observed, guards=guard, peak_roles=pool.peak,
                    tape_steps=sum(t.meter.reads + t.meter.writes + t.meter.moves for t in pool.tapes))
    finally:
        original.close()


def cases():
    # Complete reduced strict-fit/depth-jump range, then changed width, rank,
    # radix, compatibility and live-family factors. No random nomination.
    result = [(e, 2, 2, 1, 1, 1, 0, 1) for e in range(1, 81)]
    for q, m, r, factor, compatibility, a, b in (
            (2, 2, 1, 1, 2, 0, 1), (3, 2, 1, 2, 5, 0, 1),
            (2, 3, 2, 1, 1, 0, 1), (3, 3, 1, 1, 2, 1, 3),
            (2, 2, 1, 1, 1, 1, 3), (2, 2, 1, 1, 9475, 0, 1),
            (2, 2, 1, 1, 1, 1, 1)):
        for e in (1, 2, 8, 9, 12, 13, 24, 32, 61, 64, 65, 80, 127):
            result.append((e, q, m, r, factor, compatibility, a, b))
    return list(dict.fromkeys(result))


def source_boundary():
    tree = ast.parse((HERE / "selector.py").read_text())
    forbidden = {"cells", "physical", "head", "inspect", "inspect_count", "bit_length"}
    bad = [node.attr for node in ast.walk(tree)
           if isinstance(node, ast.Attribute) and node.attr in forbidden]
    require(not bad, "selector has no host tape observation")
    return "source inspection: no cells/head/physical/inspect/bit_length access; literal runtime also seals constructors and Word.inspect"


def controls():
    import encoded
    import selector
    from cardinal_counts import Count
    from check_support import no_decode
    from scratch_pool import ScratchPool
    from session import sealed_constructors
    rejected = []
    base = encoded.Profile(numerator=0, denominator=1, dimension=2, child_rank=1, row_factor=1)
    invalid = [(True, base, 1), (1, base, 1), (2, base, 0),
               (2, encoded.Profile(dimension=2, child_rank=2), 1),
               (2, encoded.Profile(numerator=2, denominator=1), 1)]
    for index, (q, profile, compatibility) in enumerate(invalid):
        original, pool = Count.literal(13), ScratchPool(24)
        try:
            with no_decode(), sealed_constructors(), pool.install():
                try:
                    selector.select_body_stock(original, q, profile, compatibility)
                except ValueError:
                    rejected.append("compiled-contract-" + str(index))
                else:
                    raise ValueError("invalid compiled contract accepted")
                pool.empty()
        finally:
            original.close()
    original, pool = Count.literal(0), ScratchPool(24)
    try:
        with no_decode(), sealed_constructors(), pool.install():
            try:
                selector.select_body_stock(original, 2, base, 1)
            except ValueError:
                rejected.append("zero-original")
            else:
                raise ValueError("zero original accepted")
            pool.empty()
    finally:
        original.close()

    # A semantic failure after all trial fields exist must unwind both scopes.
    original, pool = Count.literal(24), ScratchPool(24)
    snapshot = bytes(original.tape.cells)
    saved = selector._fits
    def injected(_trial):
        raise ValueError("injected completed-trial failure")
    selector._fits = injected
    try:
        with no_decode(), sealed_constructors(), pool.install():
            try:
                selector.select_body_stock(original, 2, base, 1)
            except ValueError as error:
                require(str(error) == "injected completed-trial failure", "failure reached trial boundary")
            else:
                raise ValueError("injected semantic failure accepted")
            pool.empty()
        require(bytes(original.tape.cells) == snapshot and original.tape.head == 1,
                "semantic failure preserves borrowed input")
        rejected.append("completed-trial-failure-cleanup")
    finally:
        selector._fits = saved
        original.close()

    text = (HERE / "selector.py").read_text()
    mutations = (
        ("old-original-depth", 'Count(body)', 'Count(original)', (13, 2, 2, 1, 1, 1, 0, 1)),
        ("missing-Q", 'stock.multiply_small(compatibility)', 'pass',
         (32, 2, 2, 1, 1, 5, 0, 1)),
        ("nonstrict-fit", 'strict.divide_small(2)', 'strict.increment(); strict.divide_small(2)',
         (12, 2, 2, 1, 1, 1, 0, 1)),
        ("wrong-radix-exponent", '_power(radix, borrowed)', '_power(radix, depth)',
         (13, 2, 2, 1, 1, 1, 0, 1)),
        ("false-final-endpoint", '_plan(work, trial, "upper")', '_plan(work, trial, "lower")',
         (24, 2, 2, 1, 1, 1, 0, 1)),
    )
    for name, old, new, args in mutations:
        require(text.count(old) == 1, "unique executed mutation target: " + name)
        module = ModuleType("mutant_" + name.replace("-", "_"))
        exec(compile(text.replace(old, new), name, "exec"), module.__dict__)
        try:
            run_case(args, module.select_body_stock)
        except ValueError as error:
            require(str(error) == "literal Count plan equals independent specification", "mutation reached oracle: " + name)
            rejected.append(name)
        else:
            raise ValueError("algorithm mutation accepted: " + name)
    return rejected


def replay():
    inputs = authenticate()
    with activate():
        from independent import check
        boundary = source_boundary()
        records = [run_case(args) for args in cases()]
        failures = controls()
        arithmetic = check()
    witnesses = [row for row in records if row["args"] in (
        [12, 2, 2, 1, 1, 1, 0, 1], [13, 2, 2, 1, 1, 1, 0, 1],
        [24, 2, 2, 1, 1, 1, 0, 1], [61, 2, 2, 1, 1, 1, 1, 3])]
    return dict(source_inputs=inputs, encoded_cases=len(records),
                fitted=sum(row["plan"]["fits"] for row in records),
                peak_setup_roles=max(row["peak_roles"] for row in records),
                records_sha256=sha256(canonical(records).encode()).hexdigest(),
                independent=arithmetic, rejection_controls=failures,
                runtime_boundary=boundary, witnesses=witnesses)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = replay()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(canonical(result) == canonical(json.loads((HERE / "RESULT.json").read_text())),
                "complete typed retained result")
        print("PASS_ENCODED_BODY_DEPTH", sha256(canonical(result).encode()).hexdigest())


if __name__ == "__main__":
    main()
