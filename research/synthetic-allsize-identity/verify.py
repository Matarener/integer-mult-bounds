# SPDX-License-Identifier: Apache-2.0
"""Finite exact controls for the separately written all-size algebra proof."""

import argparse
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_engine():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            raw = (ROOT / row["path"]).read_bytes()
            need(sha256(raw).hexdigest() == row["sha256"], "source bytes: " + row["path"])
    path = ROOT / "research/synthetic-layout-independent/physical.py"
    spec = spec_from_file_location("retained_synthetic_physical", path)
    need(spec is not None and spec.loader is not None, "retained module loader")
    engine = module_from_spec(spec)
    spec.loader.exec_module(engine)
    return engine


def reverse_bits(value, width):
    return sum(((value >> h) & 1) << (width - 1 - h) for h in range(width))


def path_checks():
    cases, wrong_branch = 0, 0
    digest = sha256()
    for a in range(1, 10):
        r = 1 << (a + 2)
        for x in range(1 << a):
            for k in range(1 << a):
                path = -sum((r >> h) * ((x >> h) & 1) * (k % (2 << h))
                            for h in range(a))
                fourier = -(2 * r >> a) * reverse_bits(x, a) * k
                need((path - fourier) % (2 * r) == 0, "coefficient path congruence")
                bad = -sum((r >> h) * ((x >> h) & 1)
                           * ((k % (1 << h)) + (1 << h) * ((x >> h) & 1))
                           for h in range(a))
                wrong_branch += (bad - fourier) % (2 * r) != 0
                digest.update((path % (2 * r)).to_bytes(2, "big"))
                cases += 1
    need(wrong_branch > 0, "new branch must not replace original input bit")
    return {"pairs": cases, "branch_fault_witnesses": wrong_branch,
            "sha256": digest.hexdigest(), "axis_bit_lengths": [1, 9]}


def expected_slots(ell, width, flags):
    q, b = divmod(ell - 1, width)
    return ([(i, ell - 1) for i, long in enumerate(flags) if long]
            + [(i, h) for h in reversed(range(b)) for i in range(len(flags))]
            + [(i, ell - 2 - j * width - o) for j in range(q)
               for i in range(len(flags)) for o in range(width)])


def layout_checks(engine):
    cases, groups = 0, 0
    for ell in range(2, 13):
        for d in range(1, 5):
            for flags in product((False, True), repeat=d):
                for width in range(1, ell):
                    plan = engine.plan(ell, width, flags)
                    slots = expected_slots(ell, width, flags)
                    need(plan["slots"] == slots, "universal slot formula fixture")
                    need(set(slots) == set(plan["original"]) and len(set(slots)) == len(slots),
                         "each named bit occurs once")
                    q, b = divmod(ell - 1, width)
                    prefix = sum(flags) + d * b
                    for h in range(b, ell - 1):
                        j, o = divmod(ell - 2 - h, width)
                        need([slots.index((i, h)) for i in range(d)]
                             == [prefix + (j * d + i) * width + o for i in range(d)],
                             "complete consecutive chunks, common offset")
                        groups += 1
                    need(plan["prefix_moves"] <= d * width and plan["swaps"] <= d * q - 1,
                         "finite layout operation bounds")
                    cases += 1
    return {"layouts": cases, "chunk_rounds": groups, "ell_range": [2, 12],
            "axes_range": [1, 4], "K": "every integer 1..ell-1"}


def coordinates(index, lengths):
    result = []
    for a in reversed(lengths):
        result.append(index % (1 << a))
        index >>= a
    return list(reversed(result))


def character_column(plan, basis, opposite):
    lengths, r = plan["lengths"], 1 << plan["ell"]
    slots = expected_slots(plan["ell"], plan["width"], plan["long_axes"])
    size = 1 << sum(lengths)
    out = [[0] * r for _ in range(size)]
    for address in range(size):
        physical, logical = (basis, address) if opposite else (address, basis)
        x = [0] * len(lengths)
        for position, (i, h) in enumerate(slots):
            x[i] += ((physical >> (len(slots) - 1 - position)) & 1) << h
        k = coordinates(logical, lengths)
        exponent = sum((2 * r >> a) * reverse_bits(v, a) * w
                       for a, v, w in zip(lengths, x, k))
        quotient, coefficient = divmod(exponent if opposite else -exponent, r)
        out[address][coefficient] = (-1) ** (quotient % 2)
    return out


def reduce_rows(rows, modulus, scale=1):
    return [[(scale * value) % modulus for value in row] for row in rows]


def matrix_fixture(engine, plan, basis, digest):
    size, r = 1 << sum(plan["lengths"]), 1 << plan["ell"]
    data = [[0] * r for _ in range(size)]
    data[basis][0] = 1
    forward = engine.execute(data, plan)
    need(forward == character_column(plan, basis, False), "integral forward character")
    opposite = engine.execute(data, plan, opposite=True)
    need(opposite == character_column(plan, basis, True), "integral opposite character")
    back = engine.execute(forward, plan, opposite=True)
    other = engine.execute(opposite, plan)
    expected = [[size * value for value in row] for row in data]
    need(back == other == expected, "both integral scaled inverse identities")
    for modulus in (2, 4, 9, 15):
        reduced = reduce_rows(forward, modulus)
        actual = reduce_rows(engine.execute(reduced, plan, opposite=True), modulus)
        need(actual == reduce_rows(expected, modulus), "integral base change")
        if modulus % 2:
            normalized = reduce_rows(reduced, modulus, pow(size, -1, modulus))
            actual = reduce_rows(engine.execute(normalized, plan, opposite=True),
                                 modulus, pow(size, -1, modulus))
            need(actual == reduce_rows(data, modulus, pow(size, -1, modulus)),
                 "normalized composite over a ring with zero divisors")
    digest.update(json.dumps(forward, separators=(",", ":")).encode())


def matrix_checks(engine):
    configurations, columns, kernels = 0, 0, 0
    digest = sha256()
    for ell in range(2, 5):
        for d in range(1, 4):
            for flags in product((False, True), repeat=d):
                if sum(ell if flag else ell - 1 for flag in flags) > 5:
                    continue
                for width in range(1, ell):
                    plan = engine.plan(ell, width, flags)
                    for basis in range(1 << sum(plan["lengths"])):
                        matrix_fixture(engine, plan, basis, digest)
                        columns += 1
                    kernels += residue_kernels(engine, plan)
                    configurations += 1
    return {"configurations": configurations, "ring_module_columns": columns,
            "residue_rings": [2, 4, 9, 15], "nonunit_two_kernel_fixtures": kernels,
            "sha256": digest.hexdigest()}


def residue_kernels(engine, plan):
    lengths, r = plan["lengths"], 1 << plan["ell"]
    size = 1 << sum(lengths)
    first_axis = lengths.index(max(lengths))
    bit = sum(lengths[first_axis + 1:]) + lengths[first_axis] - 1
    for modulus in (2, 4, 6, 10):
        data = [[0] * r for _ in range(size)]
        data[0][0] = data[1 << bit][0] = modulus // 2
        image = reduce_rows(engine.execute(data, plan), modulus)
        need(any(any(row) for row in data) and not any(any(row) for row in image),
             "explicit nonzero kernel over a nonunit-two residue ring")
    return 4


def fault_checks(engine):
    plan = engine.plan(3, 2, (False, True))
    size, r = 1 << sum(plan["lengths"]), 1 << plan["ell"]
    data = [[(7 * j + 3 * k) % 13 - 6 for k in range(r)] for j in range(size)]
    forward = engine.execute(data, plan)
    good = engine.execute(forward, plan, opposite=True)
    detected = []
    for fault in ("wrong_inverse_sign", "inverse_twiddle_after_butterfly",
                  "omit_layout_restoration", "physical_low_bits",
                  "cyclic_instead_of_negacyclic"):
        bad = engine.execute(forward, plan, opposite=True, fault=fault)
        need(bad != good, "fault detected: " + fault)
        detected.append(fault)
    need(good != data, "opposite is not the unscaled integral inverse")
    tiny = engine.plan(2, 1, (False,))
    unit = [[1, 0, 0, 0], [0, 0, 0, 0]]
    image = reduce_rows(engine.execute(unit, tiny), 2)
    square = reduce_rows(engine.execute(image, tiny, opposite=True), 2)
    need(any(any(row) for row in image) and not any(any(row) for row in square),
         "nonzero characteristic-two operator with zero composite")
    return {"detected": detected + ["unscaled_inverse"],
            "characteristic_two_noninverse": True}


def compute():
    engine = authenticated_engine()
    return {"paths": path_checks(), "layouts": layout_checks(engine),
            "matrices": matrix_checks(engine), "faults": fault_checks(engine),
            "scope": "Finite evidence for PROOF.md; no formal kernel or physical tape claim"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    result = compute()
    if args.write_receipt:
        args.write_receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        need(result == expected, "exact finite receipt")
    print("PASS_SYNTHETIC_ALLSIZE_EVIDENCE " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
