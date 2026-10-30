# SPDX-License-Identifier: Apache-2.0
"""Execute each actual compiled local program against its intrinsic endpoint.

I use exact arithmetic modulo 65537 with i=256. These complete-input probes
complement the rational native proofs; they do not prove equality over C.
"""
from hashlib import sha256
from pathlib import Path
import random

import numpy as np
from bundles import authenticate_prepared
from compile_word import Compiler, need, read_native

MODULUS, IMAGINARY = 65537, 256
LABELS = np.arange(512, dtype=np.int64)
INV2 = pow(2, -1, MODULUS)
A = (1 + IMAGINARY) * INV2 % MODULUS
B = (1 - IMAGINARY) * INV2 % MODULUS
UNITS = np.array([pow(IMAGINARY, j, MODULUS) for j in range(4)], dtype=np.int64)


def cgate(vector, mask, inverse=False):
    a, b = (B, A) if inverse else (A, B)
    return (a * vector + b * vector[LABELS ^ mask]) % MODULUS


def fourier(vector, rank=9):
    for axis in range(rank):
        vector = cgate(vector, 1 << axis)
    return vector


def monomial(record):
    need(len(record["matrix_rows"]) == 9, "intrinsic nine-axis recipe")
    destination = np.full(512, record["offset"], dtype=np.int64)
    phases = np.full(512, record["phase"], dtype=np.int64)
    bits = [(LABELS >> i) & 1 for i in range(9)]
    for i, row in enumerate(record["matrix_rows"]):
        destination ^= np.fromiter(((int(x) & row).bit_count() & 1 for x in LABELS), dtype=np.int64) << i
        phases += record["linear_Z4"][i] * bits[i]
        for j in range(i + 1, 9):
            if record["quadratic_rows"][i] >> j & 1:
                phases += 2 * bits[i] * bits[j]
    need(len(set(map(int, destination))) == 512, "exact monomial permutation")
    return destination, phases % 4


def execute(code, recipes, initial, cache):
    state = np.zeros((731, 512), dtype=np.int64)
    state[:632] = initial
    for op in code:
        kind = op[0]
        if kind in ("marker", "identity"):
            continue
        target = op[2]
        if kind == "zero":
            need(target >= 632, "owned scratch clear")
            state[target] = 0
        elif kind == "release_zero":
            need(target >= 640 and not np.any(state[target]), "complete private-zero release")
        elif kind == "copy":
            need(not np.any(state[target]), "copy into zero scratch")
            state[target] = state[op[3]]
        elif kind == "scalar":
            _, numerator, denominator = op[4]
            coefficient = numerator * pow(denominator, -1, MODULUS) % MODULUS
            state[target] = (coefficient * state[target] if op[3] is None else
                             state[target] + coefficient * state[op[3]]) % MODULUS
        elif kind == "child":
            state[target] = fourier(state[target], op[3])
        else:
            need(kind == "monomial", "complete compiled modular alphabet")
            key = op[3]
            if key not in cache:
                cache[key] = monomial(recipes[key])
            destination, phases = cache[key]
            if op[4]:
                state[target] = UNITS[(-phases) % 4] * state[target][destination] % MODULUS
            else:
                value = np.empty(512, dtype=np.int64)
                value[destination] = UNITS[phases] * state[target] % MODULUS
                state[target] = value
    need(not np.any(state[632:]), "all C and Z scratch return zero")
    return state[:632]


def endpoint(word, orientation, initial):
    expected = np.zeros_like(initial)
    for i, mask in enumerate(word["ports"]):
        fx, fy = fourier(initial[i]), fourier(initial[112+i])
        expected[i] = cgate(fx, mask, True)
        expected[112+i] = cgate(fy, mask, True)
        if orientation == "forward":
            expected[112+i] = (expected[112+i] + fx[LABELS ^ mask]) % MODULUS
        else:
            expected[i] = (expected[i] - fy) % MODULUS
    for role in range(224, 632):
        width = len(word["frames"][word["final"][role]]) - len(word["frames"][word["start"][role]])
        expected[role] = fourier(initial[role], width)
    return expected


def run(prepared):
    authenticate_prepared(prepared)
    need(IMAGINARY * IMAGINARY % MODULUS == MODULUS - 1, "exact Gaussian modular image")
    cache, results = {}, []
    for index, provider in enumerate(("gauge44", "extra")):
        data = read_native(Path(prepared) / "bound/base/providers" / provider)
        rng = random.Random(20261018 + index)
        initial = np.array([rng.randrange(MODULUS) for _ in range(632 * 512)], dtype=np.int64).reshape(632, 512)
        saved = initial.copy()
        for direction in ("forward", "backward"):
            code, recipes, _ = Compiler(data, direction).run()
            actual = execute(code, recipes, initial, cache)
            expected = endpoint(data["word"], direction, initial)
            need(np.array_equal(actual, expected) and np.array_equal(initial, saved), "complete compiled intrinsic endpoint")
            results.append(dict(provider=provider, orientation=direction, role_vectors=632, addresses=512,
                                sha256=sha256(actual.astype("<i8").tobytes()).hexdigest()))
    return dict(status="PASS_T74_COMPILED_MODULAR_ENDPOINTS", modulus=MODULUS, imaginary=IMAGINARY,
                cases=results, monomial_literals=len(cache),
                scope="Four actual compiled programs on deterministic complete input arrays; modular probes complement the exact rational source proofs and do not establish universal complex equality.")
