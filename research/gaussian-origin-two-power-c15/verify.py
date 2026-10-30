#!/usr/bin/env python3
"""This section's polynomial-inverse error is strictly below 2^{-285}."""

import hashlib
import importlib.util
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NOTES = {
    "research/gaussian-origin-two-power-c10/README.md":
        "1910fe57002d60f8eedf19b9cf49ab483010ad71b66a26d6d3e4d3a046b77507",
    "research/gaussian-origin-two-power-c10/verify.py":
        "da3977d0d093ddfec0082795b0ddbf992922872cf7d230becc18d24f01fad1d7",
    "research/gaussian-origin-two-power-c11/README.md":
        "86c313a73889b97f2b32258de1fa3f165fc8101799f712de03f4b0401554c57f",
    "research/gaussian-origin-two-power-c11/verify.py":
        "bd0a23d1265c072459e798f8c21b069e08620329cdec76bf464159187d626569",
    "research/gaussian-origin-two-power-c12/README.md":
        "ae12309e45940d03b51b20d38b7551777aafad6536bf592c95929b19151622df",
    "research/gaussian-origin-two-power-c12/verify.py":
        "6ab06d3e41833aa3a7ac49af56de7421e8ab843275daa723dcd20555c49751aa",
    "research/gaussian-origin-two-power-c13/README.md":
        "03053d946b080e73fe606c7fdf7288c70ec71f61194dcaf02a76022fd598ead1",
    "research/gaussian-origin-two-power-c13/verify.py":
        "1ea4b18631422ac1d9e9c27ec3331b4d03fb26a9e77449f329aec71d8a1279dc",
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
PREDECESSOR = ROOT / "research/gaussian-origin-two-power-c14/verify.py"
PREDECESSOR_README = ROOT / "research/gaussian-origin-two-power-c14/README.md"
PREDECESSOR_SHA = "c843d061efb7bbe82cac3ac9dfb8dafc46fa4adbc49fc336783fe2753aa36ab5"
PREDECESSOR_README_SHA = "140f6340e8b4fd0bed2535ebab4ac7d300cdb097bb8b96438ec2b73523663d53"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def predecessor_bound():
    """Replay the inherited proof that the section error is below 2^{-266}."""
    assert digest(PREDECESSOR) == PREDECESSOR_SHA
    assert digest(PREDECESSOR_README) == PREDECESSOR_README_SHA
    readme = PREDECESSOR_README.read_text(encoding="utf-8")
    assert "strictly below `(319/100) exp(-361)`" in readme
    assert "therefore strictly below\n`2^{-266}`" in readme
    spec = importlib.util.spec_from_file_location(
        "gaussian_origin_two_power_c14", PREDECESSOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


def taylor_clears():
    """The degree-81 Taylor sum of exp(361) exceeds 2^{285}*(319/100)."""
    assert 15 * 19 == 285
    target = Fraction((1 << 285) * 319, 100)
    assert target == Fraction(4957691012960060588986466786213620249751422253261060058234625269653683735843692087345152, 25)
    series = Fraction(0)
    power = Fraction(1)
    for index in range(81):
        series += power
        power *= Fraction(361, index + 1)
    assert power > 0
    assert series == Fraction(39257876249149424504993772103581491699185300801313870952206202602966016238463670481776345651632263928828262873231347537968478567856957211896692856659926231641788111722630498793690848628436562100367281, 549178237170247330014437686352825194447438688640861814881020288811680690414285869834247319060480000000000000000000)
    assert series < target
    series += power
    power *= Fraction(361, 82)
    assert power > 0
    assert power == Fraction(3986356659537090126650719323733600114910507086983688582259902701249190699229421168777053936446329694022912798484074085852619335644853714823871346164737896385726476519803647927298744105729376465805480924801, 3647641851284782765955895112755464941519887769952604174439736758287183145731686747439070693199708160000000000000000000)
    assert series == Fraction(245214262056474756356922447884918641402540093022968167101603031405221128095249658865922058441384502988145001106133915331471755537661620052390034482105778934242239120005974130410022839357793962087225169, 766955813979138512606369872320324840521422996205341500092459368857691998682019921665069531791360000000000000000000)
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
