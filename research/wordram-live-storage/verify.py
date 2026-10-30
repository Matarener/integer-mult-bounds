"""Check the new storage refinement, without invoking predecessor verifiers."""

import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compact import check_allocation, compact, operands, require

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = "research/wordram-ntt-kernel/"


def load_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    captured = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (ROOT / row["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row["sha256"],
                    "source hash: " + row["path"])
            captured[row["path"]] = data
    for name in ("ram", "ntt"):
        module = types.ModuleType(name)
        module.__path__ = []
        sys.modules[name] = module
    for name, path in (("ram.wordram_kernel", "ram/wordram_kernel.py"),
                       ("ntt.exact_ntt", "ntt/exact_ntt.py"),
                       ("ram_multiplier", "ram_multiplier.py")):
        module = types.ModuleType(name)
        module.__file__ = str(ROOT / (SOURCE + path))
        sys.modules[name] = module
        exec(compile(captured[SOURCE + path], module.__file__, "exec"),
             module.__dict__)
    return sys.modules["ram_multiplier"], sys.modules["ram.wordram_kernel"]


def peak_certificate(intervals):
    """Independent closed-interval overlap count, before each instruction."""
    events = {}
    for start, finish, _ in intervals:
        events[start] = events.get(start, 0) + 1
        events[finish + 1] = events.get(finish + 1, 0) - 1
    live = peak = witness = 0
    for pc, delta in sorted(events.items()):
        live += delta
        if live > peak:
            peak, witness = live, pc
    require(live == 0, "unclosed interval sweep")
    clique = [x for start, finish, x in intervals if start <= witness <= finish]
    require(len(clique) == peak, "peak witness")
    return peak, witness


def check_structure(plan, result, kernel):
    peak, witness = peak_certificate(result.intervals)
    require(result.capacity == peak, "nonminimal closed-interval allocation")
    check_allocation(result.intervals, result.mapping, sorted(plan.temporaries))
    for old, new in zip(plan.program, result.program, strict=True):
        require(old[0] == new[0] and len(old) == len(new), "opcode change")
        positions = (1,) if old[0] == "bltz" else range(1, len(old))
        for i in positions:
            require(new[i] == result.mapping.get(old[i], old[i]), "address change")
        if old[0] == "bltz":
            require(old[2] == new[2], "branch target change")
    protected = set(plan.left + plan.right + plan.output) | kernel.SCRATCH
    require(not plan.temporaries & protected, "ABI collision")
    allowed = set(result.mapping.values()) | kernel.SCRATCH | set(plan.output)
    for ins in result.program:
        dst, _ = operands(ins)
        require(dst is None or dst in allowed, "static destination outside ABI")
    encoded = json.dumps(result.program, separators=(",", ":")).encode()
    return {"n": plan.n, "original_temporaries": len(plan.temporaries),
            "compact_temporaries": result.capacity, "peak_pc": witness,
            "static_instructions": len(result.program),
            "program_sha256": hashlib.sha256(encoded).hexdigest()}


def execute_pair(plan, result, kernel, left, right, seed):
    rng = random.Random(seed)
    fixed = set(plan.left + plan.right + plan.output) | kernel.SCRATCH
    # Include the old abandoned cells in exterior memory of the compact ABI.
    addresses = fixed | plan.temporaries | {-19, 777777}
    initial = {x: rng.getrandbits(64) for x in sorted(addresses)}
    initial.update(zip(plan.left, left))
    initial.update(zip(plan.right, right))
    old = kernel.run(plan.program, initial)
    new = kernel.run(result.program, initial)
    require(old is not None and new is not None, "execution budget")
    require(old.accepted and new.accepted, "execution rejected")
    require(old.steps == new.steps and old.counts == new.counts, "path or cost change")
    for cell in fixed:
        require(old.memory[cell] == new.memory[cell], "visible endpoint change")
    owned = set(result.mapping.values()) | kernel.SCRATCH
    require(all(new.memory[x] == 0 for x in owned), "dirty compact return")
    allowed = owned | set(plan.output)
    require(new.writes <= allowed, "write outside compact ABI")
    require(all(new.memory[x] == value for x, value in initial.items()
                if x not in allowed), "exterior or input change")
    digits = [new.memory[x] for x in plan.output]
    require(all(0 <= x < 16 for x in digits), "output digit")
    def value(digits):
        return sum(x << (4 * i) for i, x in enumerate(digits))
    require(value(digits) == value(left) * value(right), "integer endpoint")
    return new.steps


def must_reject(action, message):
    try:
        action()
    except ValueError as error:
        require(str(error) == message, "wrong rejection: " + str(error))
        return
    raise ValueError("missing rejection: " + message)


def controls(plan, result, kernel):
    broken = dict(result.mapping)
    peak, witness = peak_certificate(result.intervals)
    clique = [x for a, b, x in result.intervals if a <= witness <= b]
    require(peak >= 2, "control needs an overlap")
    broken[clique[1]] = broken[clique[0]]
    must_reject(lambda: check_allocation(result.intervals, broken,
                                        sorted(plan.temporaries)), "overlapping aliases")
    prefix = [("one", 100), ("add", 101, 100, 100)]
    suffix = [("sub", 100, 100, 100), ("sub", 101, 101, 101), ("accept",)]
    good = prefix + suffix
    compact(good, {100, 101}, {10}, 10)
    bad = [("add", 100, 100, 100)] + good[1:]
    must_reject(lambda: compact(bad, {100, 101}, {10}, 10),
                "read before initialization")
    bad = [("bltz", 10, 2), ("one", 100), ("one", 101)] + suffix
    must_reject(lambda: compact(bad, {100, 101}, {10}, 10),
                "branch skips initialization")
    bad = [("bltz", 10, 0)] + good
    must_reject(lambda: compact(bad, {100, 101}, {10}, 10),
                "nonforward or escaping branch")
    must_reject(lambda: compact(good[:-1], {100, 101}, {10}, 10), "cleanup suffix")
    bad = [("load", 100, 10)] + good[1:]
    must_reject(lambda: compact(bad, {100, 101}, {10}, 10), "unsupported opcode")
    must_reject(lambda: compact(good, {100, 101, 102}, {10}, 10), "cleanup suffix")
    must_reject(lambda: compact(good, {10, 100}, {10}, 10), "temporary/scratch overlap")
    return 8


def verify():
    source, kernel = load_sources()
    rows, executions = [], 0
    maximal = None
    for size in (1, 2, 4, 8, 16, 32, 64, 128, 256):
        plan = source.build_multiplier(size, size)
        result = compact(plan.program, plan.temporaries, kernel.SCRATCH, kernel.ZERO)
        row = check_structure(plan, result, kernel)
        cases = [(15, 15), (0, 15), (1, 15)]
        if size == 1:
            cases = [(a, b) for a in range(16) for b in range(16)]
        steps = []
        for a, b in cases:
            left = [a] * size
            right = [b] * size
            steps.append(execute_pair(plan, result, kernel, left, right, executions))
            executions += 1
        row["dynamic_steps_maximal_digits"] = steps[-1] if size == 1 else steps[0]
        rows.append(row)
        if size == 256:
            maximal = plan, result
    require(maximal is not None, "missing maximal plan")
    count = controls(*maximal, kernel)
    require(rows[-1]["original_temporaries"] == 17920, "source template changed")
    require(rows[-1]["compact_temporaries"] == 1282, "storage result changed")
    return {"claim_type": "scoped program-refinement proof and finite certificate",
            "templates": rows, "paired_dirty_executions": executions,
            "rejection_controls": count}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = verify()
    hashes = {}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name != "RESULT.json":
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result["package_sha256"] = hashes
    target = HERE / "RESULT.json"
    if args.write_result:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads(target.read_text()), "receipt mismatch")
    print("PASS_WORDRAM_LIVE_STORAGE " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
