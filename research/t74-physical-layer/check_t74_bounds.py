# SPDX-License-Identifier: Apache-2.0
"""Check the T74 finite scalar, tape and numerical-height allowances."""
from math import prod
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from binding import T74Binding
from compile_word import need
from predecessor import close_test_imports
from production_native import PRIME
from scalar_program import prefix_guard


def run(prepared):
    binding = T74Binding(prepared)
    passes = {}
    for key, code in binding.codes.items():
        passes[key] = sum(len(binding.catalogue[op[4]].program) if op[0] == "scalar" else 1
                          for op in code if op[0] in ("scalar", "copy", "zero", "release_zero"))
    per_cover = sum(passes[call["provider_id"], call["orientation"]] for call in binding.calls.values())
    guards = [prefix_guard(program) for program in binding.catalogue.values()]
    need(len(binding.catalogue) == 36 and max(g[0] for g in guards) == 3 and
         max(g[1] for g in guards) <= 9, "complete small dyadic vocabulary")
    gamma = (1 << 1296) * prod((1 << (2*i)) - 1 for i in range(1, 37))
    need(binding.cover.size == gamma and gamma.bit_length() == 2628, "complete fixed cover")
    histogram = binding.check_profile()
    mass = sum(rank * count for rank, count in histogram.items())
    need(mass == 4816512, "complete changed paid rank mass")
    # PR3385's constructor inventory changes only at bank/private packets:
    # (632+99) - (704+8) = 19. Release uses the inherited fixed scratch pool.
    tape_delta = (binding.slots + binding.private) - (704 + 8)
    need(tape_delta == 19, "actual changed packet-tape inventory")
    tapes = 2 * PRIME * PRIME + 100696823 + tape_delta
    stock = (binding.families + tapes) * gamma
    s, allowance, guard = mass * gamma, 1 << 100000, 1 << 210000
    B = s + allowance
    # Conservatively include all finite source groups and their packet scans;
    # actual scalar passes, rather than the old 144-call allowance, enter here.
    groups = binding.inventory()["subgroups_per_cover"]
    fixed_passes = per_cover + 32 * (groups + 666 * (binding.slots + binding.private))
    scalar_charge = gamma * fixed_passes + 32 * 73
    literal = 2 * (1 << 30000) * stock**2 + 8 * s + 4 * stock + 4 + 32 * 73
    need(scalar_charge < allowance and literal < allowance and
         32 * 73 * B * B < guard and 2 * B + 18 < guard and
         2 * B * (73 - 48) >= s + allowance, "changed complete numerical-height guard")
    return dict(status="PASS_T74_CHANGED_HEIGHT_AND_INVENTORY_ALLOWANCES",
                scalar_passes={pid+":"+direction: n for (pid, direction), n in passes.items()},
                complete_scalar_passes_per_cover=per_cover, fixed_group_count=groups,
                scalar_charge_bits=scalar_charge.bit_length(), enlarged_literal_bits=literal.bit_length(),
                required_guard_bits=(32 * 73 * B * B).bit_length(),
                owned_tape_formula="2*q^2+100696842", owned_tapes=str(tapes),
                maximum_scalar_prefix_denominator_bits=3,
                maximum_scalar_prefix_l1=str(max(g[1] for g in guards)),
                scope="Finite inequalities under the written inherited height/refinement model; no production-size payload execution.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prepared", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.prepared), indent=2, sort_keys=True))
    finally:
        close_test_imports()
