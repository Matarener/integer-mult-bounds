#!/usr/bin/env python3
"""This section's polynomial-inverse error is strictly below 2^{-209}."""

import hashlib
import importlib.util
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTES = {
    "research/gaussian-origin-two-power-c2/README.md":
        "3f4d384549d2b62a4e12ff655865dc07cc2ca39cf6b3b1d42d8bfa6e230b73d5",
    "research/gaussian-origin-two-power-c2/verify.py":
        "b16f9767bda4ca29b45e5f71ee8f369c4578d4e74d3adcd44537fd1a0050427a",
    "research/gaussian-origin-two-power-c3/README.md":
        "283fa012e6298af89a5c013f6a9f1b9f725760d19023b9dd223f5d6421a735de",
    "research/gaussian-origin-two-power-c3/verify.py":
        "e4d77df768b6d13f8c7e590cb52212d93f8c986ba3ef9b2005226ded65663b38",
    "research/gaussian-origin-two-power-c4/README.md":
        "65f2afe861d0f9bf2538e444a992d6542a44bf24eef42504cc9256446936056d",
    "research/gaussian-origin-two-power-c4/verify.py":
        "52db9fc3982288c69c9a4a0e7b7b77e580bcf0668c59d43cd494693639b8f73b",
    "research/gaussian-origin-two-power-c5/README.md":
        "8c1766ed3fddf06fc3cfb914bd531a858af5c3d5ddaff37757370cf2583ee597",
    "research/gaussian-origin-two-power-c5/verify.py":
        "e2701421524be2265cd03e6eb6020a2d84e99f65f98e69b3cfcae113e545c19c",
    "research/gaussian-origin-two-power-c6/README.md":
        "8adad29d437b6c17efb1bc99eb49d32891728ce7972f4ce01e906bcfcacf4b7c",
    "research/gaussian-origin-two-power-c6/verify.py":
        "c26553c443efbfa0efcf2da6665519677b27dc322501f10be75944c3cffe341b",
    "research/gaussian-origin-two-power-c7/README.md":
        "e28feaef932d125f2fa76faadf6a6e60dc9f195f217005a509eccb2c68fe35f4",
    "research/gaussian-origin-two-power-c7/verify.py":
        "83dde59d69988234a2906db2ed5a79ac07b0fdaeed4d62ee6e28a646ed3dbb50",
    "research/gaussian-origin-two-power-c8/README.md":
        "19af097db78c4e857ed8674ae13868698f009cbc092a913f0874185302e01730",
    "research/gaussian-origin-two-power-c8/verify.py":
        "e89bd8cbdaa5aea36ffc97b492d8047f9a738f13e38a0538d9027da11e26da9e",
    "research/gaussian-origin-two-power-c9/README.md":
        "37cde6035b9f60cb4d7eb140d668277bc5da6dd9c66082c39997d01fc7e950de",
    "research/gaussian-origin-two-power-c9/verify.py":
        "9fd41844bed4c6411ad93b7d9928127ced5dbe20e858680b0d8cc5744440c0eb",
    "research/unconditional-batched-crt/GAUSSIAN.md":
        "2f63c91c58f2d1cf31294812c75970ea390c61866a8da7ed700d4316a033a242",
    "research/unconditional-batched-crt/INVERSE-CONDITIONING.md":
        "be3e4b729481b15a5ccc286b297908e4f9cef94c0c9144a28ee1cf58950d142a",
    "research/unconditional-batched-crt/vendor/FINE-PRIME.md":
        "47d1b1b4df28aadda3cd6bdeb1fbc47290595e9208cd09c1a1f338520d33fdce",
    "research/unconditional-batched-crt/vendor/GAUGEFREE-INTERIORS.md":
        "d1423ac0ea0003521797209f4396e6981a66994bbee4f8b48026e5b95f8c5116",
}
PREDECESSOR = ROOT / "research/gaussian-origin-two-power-c10/verify.py"
PREDECESSOR_README = ROOT / "research/gaussian-origin-two-power-c10/README.md"
PREDECESSOR_SHA = "da3977d0d093ddfec0082795b0ddbf992922872cf7d230becc18d24f01fad1d7"
PREDECESSOR_README_SHA = "1910fe57002d60f8eedf19b9cf49ab483010ad71b66a26d6d3e4d3a046b77507"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def predecessor_bound():
    """Replay the inherited proof that the section error is below 2^{-190}."""
    assert digest(PREDECESSOR) == PREDECESSOR_SHA
    assert digest(PREDECESSOR_README) == PREDECESSOR_README_SHA
    readme = PREDECESSOR_README.read_text(encoding="utf-8")
    assert "strictly below `(319/100) exp(-361)`" in readme
    assert "therefore strictly below\n`2^{-190}`" in readme
    spec = importlib.util.spec_from_file_location(
        "gaussian_origin_two_power_c10", PREDECESSOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


def taylor_clears():
    """The degree-50 Taylor sum of exp(361) exceeds 2^{209}*(319/100)."""
    assert 11 * 19 == 209
    target = Fraction((1 << 209) * 319, 100)
    assert target == Fraction(65614494223183090930929396154474351386186592642138997051025784832, 25)
    series = Fraction(0)
    power = Fraction(1)
    for index in range(50):
        series += power
        power *= Fraction(361, index + 1)
    assert power > 0
    assert series == Fraction(95553932919539766603649325382907512119460349657123358726477401559258607594012287578008819769371178124380192330496583593, 241749112354994917224294130889922134389787983872000000000)
    assert series < target
    series += power
    power *= Fraction(361, 51)
    assert power > 0
    assert power == Fraction(75051624198251984443456989853061891539043939434909537798332873934101480896578056472849915762891214746171016655874432115640378001, 4296727848441502161285991735372031055576896731348992000000000000)
    assert series == Fraction(241199781628697792715269268713289227915581902589328924860589767612657804515427566079246089653313431050504437902176486295291741, 84249565655715728652666504615137863834841112379392000000000000)
    assert series > target


def main():
    for name, expected in NOTES.items():
        assert digest(ROOT / name) == expected
    fine = (ROOT / "research/unconditional-batched-crt/vendor/FINE-PRIME.md").read_text(
        encoding="utf-8"
    )
    assert "`2^-Cp` for every fixed C eventually." in fine
    predecessor_bound()
    taylor_clears()


if __name__ == "__main__":
    main()
