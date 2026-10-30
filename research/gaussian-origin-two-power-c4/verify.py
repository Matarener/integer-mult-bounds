#!/usr/bin/env python3
"""This section's polynomial-inverse error is strictly below 2^{-76}."""

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
    "research/gaussian-origin-two-power-c2/README.md":
        "3f4d384549d2b62a4e12ff655865dc07cc2ca39cf6b3b1d42d8bfa6e230b73d5",
    "research/gaussian-origin-two-power-c2/verify.py":
        "b16f9767bda4ca29b45e5f71ee8f369c4578d4e74d3adcd44537fd1a0050427a",
}
PREDECESSOR = ROOT / "research/gaussian-origin-two-power-c3/verify.py"
PREDECESSOR_README = ROOT / "research/gaussian-origin-two-power-c3/README.md"
PREDECESSOR_SHA = "e4d77df768b6d13f8c7e590cb52212d93f8c986ba3ef9b2005226ded65663b38"
PREDECESSOR_README_SHA = "283fa012e6298af89a5c013f6a9f1b9f725760d19023b9dd223f5d6421a735de"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def predecessor_bound():
    """Replay the inherited proof that the section error is below 2^{-57}."""
    assert digest(PREDECESSOR) == PREDECESSOR_SHA
    assert digest(PREDECESSOR_README) == PREDECESSOR_README_SHA
    readme = PREDECESSOR_README.read_text(encoding="utf-8")
    assert "strictly below `(319/100) exp(-361)`" in readme
    assert "therefore strictly below\n`2^{-57}`" in readme
    spec = importlib.util.spec_from_file_location(
        "gaussian_origin_two_power_c3", PREDECESSOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


def taylor_clears_two_to_the_76():
    """The degree-13 Taylor sum of exp(361) exceeds 2^{76}*(319/100)."""
    assert 4 * 19 == 76
    target = Fraction((1 << 76) * 319, 100)
    assert target == Fraction(6025739632141667292676096, 25)
    series = Fraction(0)
    power = Fraction(1)
    for index in range(13):
        series += power
        power *= Fraction(361, index + 1)
    assert power > 0
    assert series == Fraction(1013341104939320794792667371757, 95800320)
    assert series < target
    series += power
    power *= Fraction(361, 14)
    assert power > 0
    assert series == Fraction(917160294948960776428552987246843, 3113510400)
    assert series > target


def main():
    for name, expected in NOTES.items():
        assert digest(ROOT / name) == expected
    fine = (ROOT / "research/unconditional-batched-crt/vendor/FINE-PRIME.md").read_text(
        encoding="utf-8"
    )
    assert "`2^-Cp` for every fixed C eventually." in fine
    predecessor_bound()
    taylor_clears_two_to_the_76()


if __name__ == "__main__":
    main()
