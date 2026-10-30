#!/usr/bin/env python3
"""Failure controls for the codimension-one substitution argument."""

import importlib.util
from pathlib import Path


def load():
    path = Path(__file__).with_name("verify.py")
    spec = importlib.util.spec_from_file_location("codim_one", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def main():
    module = load()
    missed = {left ^ right for left, right in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))}
    require(1 not in missed or missed != set(range(1, 8)), "control setup")
    require(len(missed) < 7, "a 4-subset of F_2^3 need not cover every direction")

    wide = module.kernel_count(8, (0, 1, 2, 3))
    require(abs(wide - 4) >= 2, "four preserving steps can unbalance by more than two")

    witness = (0, 1, 0, 2, 1, 3, 2, 3)
    states = module.prefix_states(witness)
    require(module.restored(witness, 4) and module.universal(states, 4), "fixture")
    bit0, _ = module.falsely_pruned(4, 8, states, 0b0001)
    high, _ = module.falsely_pruned(4, 8, states, 0b1110)
    require(bit0 and not high, "bit 0 fires on the fixture and a weight-3 mask does not")

    module.two_stay_lemma()
    module.five_point_cover()
    print("PASS_F7_CODIM_ONE_SUBSTITUTION_TESTS groups=4")


if __name__ == "__main__":
    main()
