# SPDX-License-Identifier: Apache-2.0
"""Certify the full T74 affine/phase vocabulary in the retained compiler."""
from itertools import combinations
from hashlib import sha256

from binding import T74Binding
from compile_word import canonical, need
import cohort
cohort.monomial_api()
from cardinal_counts import Count
from phase_recipe import Recipe


def literal_phase(record, address):
    value = record["phase"]
    for i, coefficient in enumerate(record["linear_Z4"]):
        if address >> i & 1:
            value += coefficient
            value += 2 * ((record["quadratic_rows"][i] >> (i + 1)) & (address >> (i + 1))).bit_count()
    return value % 4


def encoded_phase(recipe, record, addresses, spacing, residue):
    state = {name: Count.literal(sum(((x >> i) & 1) << (residue + j*spacing)
                                   for j, x in enumerate(addresses)))
             for i, name in enumerate(recipe.vectors)}
    arguments = tuple(Count.literal(v) for v in (len(addresses), spacing, residue))
    before = {name: bytes(value.tape.cells) for name, value in state.items()}
    try:
        expected = sum(literal_phase(record, x) for x in addresses) % 4
        need(recipe.phase(state, *arguments) == expected and
             recipe.phase(state, *arguments, True) == (-expected) % 4,
             "encoded forward/inverse phase at the original or recovered source address")
        need(all(bytes(value.tape.cells) == before[name] for name, value in state.items()),
             "phase scan preserves address controls")
    finally:
        for value in (*state.values(), *arguments):
            value.close()


def run(prepared):
    binding = T74Binding(prepared)
    vectors = tuple("v" + str(i) for i in range(73))
    constant = 1 << 73
    signatures = {}
    counts = []
    digest = sha256()
    points = (0, *(1 << i for i in range(9)), *((1 << i) | (1 << j) for i, j in combinations(range(9), 2)))
    for key, record in sorted(binding.recipes.items()):
        recipe = Recipe(record, vectors)
        forms = [1 << i for i in range(73)]
        for operation, target, source in recipe.word:
            need(operation in ("add", "flip"), "retained finite monomial alphabet")
            forms[target] ^= forms[source] if operation == "add" else constant
        expected = [row ^ (constant if record["offset"] >> i & 1 else 0)
                    for i, row in enumerate(record["matrix_rows"])]
        need(forms == expected, "complete affine form identity on 2^73 columns")
        for operation, target, source in reversed(recipe.word):
            forms[target] ^= forms[source] if operation == "add" else constant
        need(forms == [1 << i for i in range(73)], "complete inverse affine form identity")
        need(not any(recipe.linear[9:]) and all(j < 9 for i, j in recipe.quadratic), "native nine-coordinate phase support")
        for address in points:
            compiled = recipe.constant + sum(a for i, a in enumerate(recipe.linear) if address >> i & 1)
            compiled += 2 * sum((address >> i & 1) * (address >> j & 1) for i, j in recipe.quadratic)
            need(compiled % 4 == literal_phase(record, address), "complete quadratic coefficient polarization")
        signature = (recipe.constant, recipe.linear, recipe.quadratic)
        signatures.setdefault(signature, (recipe, record))
        counts.append((len(recipe.word), len(recipe.quadratic)))
        digest.update(canonical([key, expected, signature]))
    need(len(counts) == 3782 and len(signatures) == 2248, "complete changed monomial/phase census")
    for index, (recipe, record) in enumerate(signatures.values()):
        # Include nonzero high spectators while phases remain on the native nine axes.
        address = ((index * 197 + 31) % 512) | (1 << (9 + index % 64))
        encoded_phase(recipe, record, (address,), 1, 0)
    spaced = 0
    for phase in range(4):
        recipe, record = next(pair for signature, pair in signatures.items() if signature[0] == phase)
        for columns in (2, 3):
            addresses = tuple(((j*113+29) % 512) | (1 << (13+j)) for j in range(columns))
            encoded_phase(recipe, record, addresses, 3, 2)
            spaced += 1
    return dict(status="PASS_T74_COMPLETE_MONOMIAL_COMPILATION", literals=len(counts),
                phase_signatures=len(signatures), affine_columns="2^73 per literal, by symbolic forms",
                polarization_points_per_literal=len(points), encoded_phase_addresses=len(signatures),
                spaced_tensor_cases=spaced, maximum_affine_gates=max(n for n, _ in counts),
                maximum_quadratic_terms=max(n for _, n in counts), sha256=digest.hexdigest(),
                scope="Complete affine and phase polynomial identities; encoded phase probes and separate physical packet/root fixtures. No O73 payload enumeration.")
