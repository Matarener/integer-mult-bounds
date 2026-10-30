#!/usr/bin/env python3
"""This section's polynomial-inverse error is strictly below 2^{-57}."""

import hashlib
import importlib.util
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTES = {
    "research/unconditional-batched-crt/GAUSSIAN.md":
        "2f63c91c58f2d1cf31294812c75970ea390c61866a8da7ed700d4316a033a242",
    "research/unconditional-batched-crt/INVERSE-CONDITIONING.md":
        "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a",
    "research/unconditional-batched-crt/vendor/FINE-PRIME.md":
        "47d1b1b4df28aadda3cd6bdeb1fbc47290595e9208cd09c1a1f338520d33fdce",
    "research/unconditional-batched-crt/vendor/GAUGEFREE-INTERIORS.md":
        "d1423ac0ea0003521797209f4396e6981a66994bbee4f8b48026e5b95f8c5116",
}
PREDECESSOR = ROOT / "research/gaussian-origin-two-power-c2/verify.py"
PREDECESSOR_README = ROOT / "research/gaussian-origin-two-power-c2/README.md"
PREDECESSOR_SHA = "b16f9767bda4ca29b45e5f71ee8f369c4578d4e74d3adcd44537fd1a0050427a"
PREDECESSOR_README_SHA = "3f4d384549d2b62a4e12ff655865dc07cc2ca39cf6b3b1d42d8bfa6e230b73d5"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def predecessor_majorant():
    """Replay the inherited proof that the section error is below (319/100) exp(-361)."""
    assert digest(PREDECESSOR) == PREDECESSOR_SHA
    assert digest(PREDECESSOR_README) == PREDECESSOR_README_SHA
    readme = PREDECESSOR_README.read_text(encoding="utf-8")
    assert "strictly below `(319/100) exp(-361)`" in readme
    assert "strictly below `2^{-38}`" in readme
    spec = importlib.util.spec_from_file_location(
        "gaussian_origin_two_power_c2", PREDECESSOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


def taylor_clears_two_to_the_57():
    """The degree-10 Taylor sum of exp(361) exceeds 2^{57}*(319/100)."""
    assert 3 * 19 == 57
    target = Fraction((1 << 57) * 319, 100)
    assert target == Fraction(11493186249049505792, 25)
    series = Fraction(0)
    power = Fraction(1)
    for index in range(10):
        series += power
        power *= Fraction(361, index + 1)
    assert power > 0
    assert series == Fraction(10678198581212035750165, 36288)
    assert series < target
    series += power
    power *= Fraction(361, 11)
    assert power > 0
    assert series == Fraction(38657793315667161768372101, 3628800)
    assert series > target


def main():
    for name, expected in NOTES.items():
        assert digest(ROOT / name) == expected
    fine = (ROOT / "research/unconditional-batched-crt/vendor/FINE-PRIME.md").read_text(
        encoding="utf-8"
    )
    assert "`2^-Cp` for every fixed C eventually." in fine
    predecessor_majorant()
    taylor_clears_two_to_the_57()


if __name__ == "__main__":
    main()
