# SPDX-License-Identifier: Apache-2.0
"""Reprice the actual scalar/inventory implementation under retained guards."""
from fractions import Fraction as F
from hashlib import sha256
import json
from math import prod
from pathlib import Path
import sys
import types

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cohort
from production_native import PRIME
from scalar_program import compile_catalogue
from selected_source import load

ENGINE_ROOT = "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r740-replica32/code/engines/"
ENGINE_PINS = {"moment": "81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482",
               "base_two_moment": "aee70c242a2f1d225528fabe2002e1564d1dc884797c07d28a831c7878ee9098"}


def run():
    need = cohort.require
    data = load()
    catalogue, _ = compile_catalogue(data["programs"])
    passes = {}
    for name, events in data["programs"].items():
        total = 0
        for event in events:
            if event[0] != "scalar":
                continue
            op = event[1]
            if op[0] in ("copy", "clear"):
                total += 1
            else:
                offset = 3 if op[0] == "add" else 2
                value = F(op[offset], op[offset + 1])
                total += len(catalogue[op[0], value.numerator, value.denominator].program)
        passes[name] = total
    local = sum(passes[call["orientation"]] for call in data["template"]["calls"])
    need(local == 11581648 and local < 20936640, "complete scalar pass comparison")
    gamma = (1 << 1296) * prod((1 << (2 * i)) - 1 for i in range(1, 37))
    histogram = {1:349604, 2:60192, 3:62585, 4:20448, 5:11808, 7:7, 8:1152, 48:4866}
    mass = sum(rank * count for rank, count in histogram.items())
    need(mass == 1041408, "selected rank mass")
    scalar_charge = gamma * (local + 144 * 224 * 8) + 32 * 73
    tapes = 2 * PRIME * PRIME + 100696823
    expanded_stock = (14336 + tapes) * gamma
    s, E, C0 = gamma * mass, 1 << 100000, 1 << 210000
    B = s + E
    literal = 2 * (1 << 30000) * expanded_stock ** 2 + 8 * s + 4 * expanded_stock + 4 + 32 * 73
    need(literal < E and scalar_charge < E and 32 * 73 * B * B < C0 and
         2 * B + 18 < C0 and 2 * B * (73 - 48) >= s + E, "complete enlarged height guard")
    engines = []
    for name, pin in ENGINE_PINS.items():
        path = cohort.ROOT / (ENGINE_ROOT + name + ".py")
        raw = path.read_bytes()
        need(sha256(raw).hexdigest() == pin, "retained exact moment engine")
        engine = types.ModuleType("controller_retained_" + name)
        engine.__file__ = str(path)
        # The source uses assertions; retain them even in the -O control.
        exec(compile(raw, str(path), "exec", optimize=0), engine.__dict__)
        engines.append(engine)
    a = F(167, 100000)
    first = engines[0].moment(histogram, 73, 14336, a, False)
    second = engines[1].moment(73, 14336, list(histogram.items()), a)
    need(max(first[0], second[0]) <= min(first[1], second[1]), "retained moment interval intersection")
    gap = 1 - max(first[1], second[1])
    need(gap > F(15999, 10**9), "strict coarse moment gap")
    tau, sigma, beta, lam, lamp = F(99830289, 10**8), 1-a, F(1, 1000), F(249583, 250000), F(599, 600)
    chi, leaf, reserve = sigma+beta*(tau-sigma), sigma+beta*(1-sigma), F(499, 500)
    need(tau < sigma and max(chi, leaf, reserve) < lam < lamp, "complete strict time margins")
    return dict(owned_tapes=str(tapes), tape_formula="2*q^2+100696823", scalar_passes_per_cover=local,
                scalar_charge_bits=scalar_charge.bit_length(), enlarged_literal_bits=literal.bit_length(),
                required_C0_bits=(32 * 73 * B * B).bit_length(), internal_exponent=str(chi),
                leaf_exponent=str(leaf), reservation_exponent=str(reserve),
                retained_moment_gap_lower=str(gap),
                scope="Retained moment engines and written constructor inventory; no new selected exponent.")


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
