#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound algebra and obligation checks, not physical supplier admission."""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path
import random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from copy_child import (block_diagonal, compile_copy, determinant, eye, factor_sl,
                       independent_columns, inverse, invoice, mul, need,
                       normalize_kernel, projector, reduce_rational, residual,
                       row_add, split_basis, support_bound, word_matrix)

HERE = Path(__file__).resolve().parent
WORD_SHA = "e432182d5b62c8bbefeb871fce30317234d707e5e18d4295e65ac21f7fd8365e"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def authenticate():
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    for row in sources["retained"]:
        path = HERE / row["path"]
        need(path.is_file() and not path.is_symlink(), "missing/linked retained input")
        data = path.read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "retained SHA")
        need(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == row["git_blob"], "retained Git blob")
    data = (HERE / "inputs/r437-word.json.gz").read_bytes()
    need(hashlib.sha256(data).hexdigest() == WORD_SHA, "fixed R437 input binding")
    return json.loads(gzip.decompress(data))


def embed(p, n):
    out = [[0] * n for _ in range(n)]
    for i, row in enumerate(p):
        out[i][:len(p)] = row
    return out


def generated_unit(n, modulus, seed):
    rng = random.Random(seed)
    out = eye(n)
    # Arbitrary high coefficients and nonorthogonal unit matrices; invertible
    # by construction, with no acceptance/rejection conditioning on endpoints.
    for _ in range(3 * n):
        i, j = rng.sample(range(n), 2)
        row_add(out, i, j, rng.randrange(modulus), modulus)
    return out


def reject(fn, name):
    try:
        fn()
    except (ValueError, ZeroDivisionError):
        return name
    raise ValueError("accepted semantic control: " + name)


def geometry_check(n, columns, delta, rank=7):
    parent = n * columns + delta
    width = rank * columns
    # These exponents describe three independent spectators. The external G
    # appears once in the middle, not hidden in an aggregate volume equality.
    before, gap, suffix = 0, 2 * parent - 2 * width, 0
    need(before + 2 * width + gap + suffix == 2 * parent, "projected full volume")
    need(width < parent and gap >= 0, "proper-width child")
    return [parent, width, gap]


def finite_function_check():
    """Complete small address cube with repeated physical prefixes/spectators."""
    modulus, n, rank = 3, 2, 1
    p = [[1, 0], [0, 0]]
    g = [[1, 1], [1, 2]]
    weights = [2, 1]
    result = compile_copy(p, rank, g, weights, 3, modulus)
    matrix = result["matrix"]
    addresses = list(product(range(modulus), repeat=2 * n))
    lookup = {x: i for i, x in enumerate(addresses)}
    rng = random.Random(3936)
    source = tuple(rng.randrange(2) for _ in range(3 * len(addresses) * 2))
    original = source[:]
    output = []
    for physical_prefix in range(3):
        for x in addresses:
            y = tuple(sum(a * b for a, b in zip(row, x)) % modulus for row in matrix)
            for spectator in range(2):
                output.append(source[(physical_prefix * len(addresses) + lookup[y]) * 2 + spectator])
    need(source == original and len(output) == len(source), "borrowed source and full extents")
    need(len({tuple(sum(a * b for a, b in zip(row, x)) % modulus for row in matrix) for x in addresses}) == len(addresses), "full small permutation")
    # Complete inverse on arbitrary payload, including repeated prefix labels.
    recovered = []
    mi = inverse(matrix, modulus)
    for physical_prefix in range(3):
        for x in addresses:
            y = tuple(sum(a * b for a, b in zip(row, x)) % modulus for row in mi)
            for spectator in range(2):
                recovered.append(output[(physical_prefix * len(addresses) + lookup[y]) * 2 + spectator])
    need(tuple(recovered) == source, "all small payload cells return")
    output[:] = [0] * len(output)
    need(source == original and not any(output), "owned disposal does not clear borrowed source")
    return dict(addresses=len(addresses), physical_prefixes=3, spectators=2,
                payload_bits=len(source), scope="finite function/permutation check, not physical execution")


def calculate():
    word = authenticate()
    selected = json.loads(gzip.decompress((HERE / "inputs/selected589-word.json.gz").read_bytes()))
    need(word["lines"] == selected["lines"] and word["frames"] == selected["frames"],
         "complete source root/frame equality with the selected predecessor")
    need(word["R"] == 437 and word["ret"] == list(range(470, 479)), "actual R437 source labels")
    # R437's nine retained centres end section A at their capture frames.
    current = word["start"][:]
    for section in ("D", "A"):
        for frame, target, sources in word[section]:
            for role in [target] + sources:
                current[role] = frame
    centres = {centre: current[centre] for centre in word["ret"]}
    need([centres[c] for c in word["ret"]] == list(range(510, 519)), "actual capture-frame source correspondence")
    frame_rows, algebra_cases, support_hashes = [], 0, set()
    last = None
    for centre in word["ret"]:
        frame = centres[centre]
        rational, rank = projector(word["lines"], word["frames"][frame])
        need(rank == 7, "literal rank seven")
        frame_rows.append(dict(center=centre, frame=frame, rank=rank,
                               projector_sha256=hashlib.sha256(canonical([[str(x) for x in row] for row in rational])).hexdigest()))
        for q, w in [(3, 1), (3, 2), (5, 2), (7, 2), (11, 1)]:
            modulus = q ** w
            p = reduce_rational(rational, modulus)
            g = generated_unit(8, modulus, centre * q + w)
            weights = [a for a in range(1, modulus) if a % q][:8]
            weights = (weights * 8)[:8]
            result = compile_copy(p, rank, g, weights, q, modulus)
            support_hashes.add(hashlib.sha256(canonical([(i, j) for i, j, _c in result["head"]])).hexdigest())
            last = p, g, weights, q, modulus, result
            algebra_cases += 1
    need(len(support_hashes) == 1, "one fixed factor support over all tested contexts")

    # Full ambient-64 binding and a deliberately bad leading rank-seven minor.
    rational, _rank = projector(word["lines"], word["frames"][515])
    q, modulus = 3, 9
    p = embed(reduce_rational(rational, modulus), 64)
    basis = split_basis(p, 7, q, modulus)
    permutation = eye(64)
    for i in range(7):
        permutation[i], permutation[57 + i] = permutation[57 + i], permutation[i]
    bad_g = mul(permutation, inverse(basis, modulus), modulus)
    bad_p = mul(mul(bad_g, p, modulus), inverse(bad_g, modulus), modulus)
    need(all(bad_p[i][j] == 0 for i in range(7) for j in range(7)), "bad leading-minor control really is bad")
    ambient = compile_copy(p, 7, bad_g, [1 + 3 * (i % 3) for i in range(64)], q, modulus)
    need(len(ambient["head"]) == 10458, "ambient fixed-support bound")
    # Every pair of head/tail words has complementary physical order because
    # the second bank is reflected. Include both inverse words as well.
    support = [(i, j) for i, j, _c in ambient["head"]]
    need(support == [(i, j) for i, j, _c in ambient["tail"]], "same head/tail factor support")
    reverse_slots = 2 * (sum(i < j for i, j in support) + sum(i > j for i, j in support))
    need(reverse_slots == 20916, "all reverse-order factors separately billed")

    controls = []
    controls.append(reject(lambda: factor_sl([[2, 0], [0, 1]], 9), "omit kernel determinant normalization"))
    controls.append(reject(lambda: compile_copy(p, 7, bad_g, [3] + [1] * 63, 3, 9), "nonunit incoming weight"))
    wrong_rank = [[int(i == j and i < 6) for j in range(64)] for i in range(64)]
    controls.append(reject(lambda: split_basis(wrong_rank, 7, 3, 9), "same label with rank six"))
    p0, g0, weights0, q0, m0, case = last
    expected = case["matrix"]
    transpose = [list(row) for row in zip(*g0)]
    wrong = residual(mul(mul(g0, p0, m0), transpose, m0), weights0, m0)
    controls.append(reject(lambda: need(wrong == expected, "inverse is not transpose"), "transpose high-chart inverse"))
    controls.append(reject(lambda: need(residual(eye(8), weights0, m0) == expected, "full swap differs"), "full swap priced as rank seven"))
    removed = next(i for i, (_a, _b, c) in enumerate(case["head"]) if c)
    damaged = case["head"][:removed] + case["head"][removed + 1:]
    controls.append(reject(lambda: need(word_matrix(damaged, 8, m0) == word_matrix(case["head"], 8, m0), "omitted factor differs"), "omit a nonzero factor"))
    controls.append(reject(lambda: need(invoice(columns=2, prefixes=7)["coarse_calls"] == 7, "one whole-packet call"), "multiply core calls by repeated prefixes"))
    controls.append(reject(lambda: need(reverse_slots == 0, "reverse-order adapters cost is nonzero"), "free reverse-order adapters"))

    # A power-counting rejection of an implication from THIS bound, not a
    # lower bound on any algorithm or an impossibility result for R437.
    c = Q(17, 10000)
    a1, a2 = c * (1 - c), c * (1 - c * c)
    target = Q(1736646042038446578551, 10 ** 24)
    deltas = {"B1": (1 + target) * (1 - a1) - 1,
              "B2": (1 + target) * (1 - a2) - 1}
    need(all(v > 0 for v in deltas.values()), "reverse-adapter bound cannot be silently absorbed")
    return dict(status="PASS_UNIFORM_COPY_REDUCTION_WITH_EXPLICIT_BACKEND_PREMISES",
                claim="uniform local-ring algebra and conditional caller/cost reduction; inherited cheap tariff NOT proved",
                captures=frame_rows, algebra_cases=algebra_cases,
                selected_root_and_frame_tables_unchanged=True,
                full_ambient_cases=1, bad_leading_minor_passes=True,
                dimension=64, fixed_word_length=10458,
                physical_reverse_factor_slots=reverse_slots,
                invoice=invoice(columns=10, prefixes=11),
                projected_geometry=[geometry_check(64, f, d) for f in (1, 2, 9, 10, 63, 64, 1000) for d in (0, 1, 63)],
                small_function_check=finite_function_check(), controls=controls,
                nonabsorption_deltas={k: str(v) for k, v in deltas.items()},
                physical_backend_implemented=False, supplier_admitted=False,
                inherited_dependencies=["completed same-q ordinary B1/B2 with source/spectator preservation and restored owned work",
                                       "proper-width reversed child with the specified compatible stock and successful return contract",
                                       "encoded scalar coefficient preparation and complete ordered shear",
                                       "canonical root-coupling absorption if simplified asymptotic costs are used"],
                remaining=["eliminate, share, or otherwise fully pay reverse-order interchanges inside the intended rank-seven tariff",
                           "bind an encoded physical implementation of this new factor schedule; this algebra compiler is not that implementation",
                           "independent universal review of the inherited C0/B1 source-refinement and complete-cost arguments",
                           "all-source hosting, outer transfer and integer recovery remain outside this local reduction"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = json.loads(canonical(calculate()))
    receipt = HERE / "RESULT.json"
    if args.write_result:
        receipt.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(json.loads(receipt.read_bytes()) == result, "recomputed result differs")
    print(result["status"] + " cases=" + str(result["algebra_cases"]) + " controls=" + str(len(result["controls"])))


if __name__ == "__main__":
    main()
