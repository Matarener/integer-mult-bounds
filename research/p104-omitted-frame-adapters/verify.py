#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Sharp bank-local native tariff for omitted P104 endpoint charts.

Nick Petalas. PR3446 defines the projection, PR3462 identifies the missing
adapters, PR2586 supplies the word, and the retained compiler supplies synthesis.
"""

import argparse
import gzip
import hashlib
import json
import runpy
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMPILER = (
    "research/gmx-t74-borrow43-handoff/new/fastnative/vendor/native/new/code/"
    "borrow/vendor/clifford/clifford_exact.py"
)
WORD = "research/p104-rounded-collector/inputs/WORD.json"
NATIVE = "research/p104-rounded-collector/inputs/NATIVE.json.gz"
ROLES = {f"Y{i}" for i in (*range(22, 33), *range(63, 104))}
ROLES |= {f"{p}{i}" for p in ("D", "G") for i in range(27, 32)} | {"Q7"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_json(path):
    require(
        path.is_file() and not path.is_symlink(), "missing or linked file: " + str(path)
    )
    require(path.stat().st_size <= 4_000_000, "file capacity")
    return json.loads(path.read_bytes())


def sources():
    pins = read_json(HERE / "SOURCES.json")["files"]
    require(len(pins) == 5, "source pin count")
    loaded = {}
    for pin in pins:
        if pin["usage"] != "input":
            continue
        path = ROOT / pin["path"]
        require(
            path.is_file() and not path.is_symlink(), "missing source: " + pin["path"]
        )
        require(path.stat().st_size <= 4_000_000, "source capacity")
        raw = path.read_bytes()
        require(
            hashlib.sha256(raw).hexdigest() == pin["sha256"],
            "source hash: " + pin["path"],
        )
        loaded[pin["path"]] = raw
    require(set(loaded) == {COMPILER, WORD, NATIVE}, "live source set")
    origin = read_json(HERE / "inputs/ORIGINS.json")
    require(origin["path"] == "inputs/PR3416_verify.py", "checker path")
    path = HERE / origin["path"]
    require(path.is_file() and not path.is_symlink(), "missing frozen checker")
    require(
        hashlib.sha256(path.read_bytes()).hexdigest() == origin["sha256"],
        "checker hash",
    )
    native = gzip.decompress(loaded[NATIVE])
    require(len(native) <= 8_000_000, "native expansion capacity")
    return json.loads(loaded[WORD]), json.loads(native)


def closure(word):
    """Reconstruct PR3446's syntactic terminal-history fixed point."""
    program = word["program"]
    names = sorted(word["initial_frames"])
    require(len(program) == 5398 and len(names) == 358, "word shape")
    state = {name: 1 << (5398 + j) for j, name in enumerate(names)}
    histories, cleanups, allocations = [], [], {}
    for index, op in enumerate(program):
        kind, target = op[:2]
        if kind == "zero":
            require(target not in state, "private alias")
            state[target] = 1 << index
            allocations[target] = index
        elif kind == "add":
            state[target] |= state[op[2]] | (1 << index)
        else:
            require(kind in ("sign", "transport", "erase"), "opcode")
            state[target] |= 1 << index
        histories.append(state[target])
        if kind == "erase":
            cleanups.append((allocations.pop(target), state.pop(target)))
    require(len(cleanups) == 8 and not allocations, "private lifetimes")
    ports = [
        i
        for i, op in enumerate(program)
        if i <= 4516
        and op[0] == "add"
        and op[2] in ROLES
        and op[1] not in ROLES | {"C"}
    ]
    require(len(ports) == 675, "port count")
    mask = 0
    for index in ports:
        mask |= histories[index]
    for name in ROLES | {program[i][1] for i in ports}:
        mask |= state[name]
    for _ in range(367):
        before = mask
        for start, end in cleanups:
            if mask >> start & 1:
                mask |= end
        for j, name in enumerate(names):
            if mask >> (5398 + j) & 1:
                mask |= state[name]
        if before == mask:
            break
    else:
        raise ValueError("closure capacity")
    selected = [i for i in range(5398) if mask >> i & 1]
    retained = {name for j, name in enumerate(names) if mask >> (5398 + j) & 1}
    require(len(selected) == 4027 and len(retained) == 265, "projection size")
    require(
        digest(selected)
        == "66113bcd513a17eac24f43944a8759bdae1bb2a85e2b9900122f281c5c676dc8",
        "projection event hash",
    )
    return selected, sorted(set(names) - retained)


def binary_rank(columns):
    require(
        len(columns) <= 18
        and all(type(x) is int and 0 <= x < 1 << 18 for x in columns),
        "binary matrix capacity",
    )
    pivots = {}
    for original in columns:
        column = original
        for bit in reversed(range(18)):
            if not column >> bit & 1:
                continue
            if bit in pivots:
                column ^= pivots[bit]
            else:
                pivots[bit] = column
                break
    return len(pivots)


def check_recipe(kernel, old, new, recipe, cache):
    actual = kernel["recipe_program"](recipe)
    expected = kernel["adjoint"](kernel["chart"](old)) + kernel["chart"](new)
    tableau, anchor = kernel["equal_certificate"](actual, expected, cache)
    table = kernel["program_table"](expected, cache)
    rank = binary_rank([x for _, x, _ in table[9:]])
    require(recipe["rank"] == rank, "nonminimal native rank")
    dirty = tuple(((17 * x + 3) % 29 - 14, (11 * x + 5) % 23 - 11) for x in range(512))
    result = kernel["canonical_vector"](kernel["apply"](actual, dirty))
    reference = kernel["canonical_vector"](kernel["apply"](expected, dirty))
    require(result == reference, "dense Gaussian payload mismatch")
    restored = kernel["canonical_vector"](
        kernel["apply"](kernel["adjoint"](actual), *result)
    )
    require(restored == (dirty, 0), "adapter inverse restoration")
    return {
        "signed_pauli_sha256": tableau,
        "exact_anchor_sha256": anchor,
        "rank": rank,
        "dirty_endpoint_sha256": digest(result),
    }


def certify(word, archive, compiler, kernel):
    kernel["bind"](word, archive)
    selected, omitted = closure(word)
    require(len(omitted) == 93, "omitted bank count")
    require(
        all(word["program"][i][1] not in omitted for i in selected),
        "projection touches omitted bank",
    )
    cache, records, recipes = {}, [], {}
    full = [256, 128, 64, 32, 16, 8, 4, 2, 1]
    for name in omitted:
        old, new = word["initial_frames"][name], word["final_frames"][name]
        require(new == full and len(old) in (0, 1), "adapter endpoint shape")
        key = tuple(old)
        if key not in recipes:
            forward_old = compiler["canonical_frame"](9, old)
            forward_new = compiler["canonical_frame"](9, new)
            operation = forward_old.then(forward_new.adjoint())
            # Discard its execution object; the separate checker validates the recipe.
            recipe, _compiled = compiler["lower_child"](operation)
            certificate = check_recipe(kernel, old, new, recipe, cache)
            require(certificate["rank"] == 9 - len(old), "endpoint rank")
            recipes[key] = {
                "old": old,
                "new": new,
                "recipe": recipe,
                "certificate": certificate,
            }
        records.append(
            {
                "bank": name,
                "recipe_key": list(key),
                "rank": recipes[key]["recipe"]["rank"],
            }
        )
    profile = Counter(row["rank"] for row in records)
    require(profile == {8: 52, 9: 41} and len(recipes) == 53, "adapter profile")
    omitted_events = [
        op
        for i, op in enumerate(word["program"])
        if i not in selected and op[0] == "transport"
    ]
    old_profile = Counter(op[4] for op in omitted_events)
    return {
        "schema_version": 1,
        "projection_event_sha256": digest(selected),
        "omitted_banks": records,
        "recipes": list(recipes.values()),
        "profile": {str(k): v for k, v in sorted(profile.items())},
        "rank_mass": sum(k * v for k, v in profile.items()),
        "omitted_original_transport_profile": {
            str(k): v for k, v in sorted(old_profile.items())
        },
        "omitted_original_transport_count": len(omitted_events),
        "scope": "Exact endpoint adapters only; sharp bank-local monomial/native-C tariff.",
    }


def engines():
    return (
        runpy.run_path(str(ROOT / COMPILER)),
        runpy.run_path(str(HERE / "inputs/PR3416_verify.py")),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    word, archive = sources()
    compiler, kernel = engines()
    receipt = certify(word, archive, compiler, kernel)
    if args.write_receipt is not None:
        args.write_receipt.write_bytes(json.dumps(receipt, indent=2).encode() + b"\n")
    else:
        require(
            canonical(receipt) == canonical(read_json(HERE / "ADAPTERS.json")),
            "adapter receipt mismatch",
        )
    print(
        "PASS_P104_OMITTED_FRAME_ADAPTERS",
        receipt["profile"],
        "rank_mass=" + str(receipt["rank_mass"]),
    )


if __name__ == "__main__":
    main()
