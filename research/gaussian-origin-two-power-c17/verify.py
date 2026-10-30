#!/usr/bin/env python3
"""This section's polynomial-inverse error is strictly below 2^{-323}."""

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
    "research/gaussian-origin-two-power-c14/README.md":
        "140f6340e8b4fd0bed2535ebab4ac7d300cdb097bb8b96438ec2b73523663d53",
    "research/gaussian-origin-two-power-c14/verify.py":
        "c843d061efb7bbe82cac3ac9dfb8dafc46fa4adbc49fc336783fe2753aa36ab5",
    "research/gaussian-origin-two-power-c15/README.md":
        "3417f0d33aa07cb12ca1157eb47542bd9af2a7f71bdc7c1634c6bf3897422d70",
    "research/gaussian-origin-two-power-c15/verify.py":
        "e7b3b8fe2de23c314df1a06e32f915196cc8bd93ed2c618e1dc11244746c2585",
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
PREDECESSOR = ROOT / "research/gaussian-origin-two-power-c16/verify.py"
PREDECESSOR_README = ROOT / "research/gaussian-origin-two-power-c16/README.md"
PREDECESSOR_SHA = "15828ffe60a8cd03c695dcf8987237d7b4078971df40f60006cdfe41468ddf63"
PREDECESSOR_README_SHA = "8452267974318bcd6f68a699f06898925de281b9a1cc32ed43f0d3d86e878d84"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def predecessor_bound():
    """Replay the inherited proof that the section error is below 2^{-304}."""
    assert digest(PREDECESSOR) == PREDECESSOR_SHA
    assert digest(PREDECESSOR_README) == PREDECESSOR_README_SHA
    readme = PREDECESSOR_README.read_text(encoding="utf-8")
    assert "strictly below `(319/100) exp(-361)`" in readme
    assert "therefore strictly below\n`2^{-304}`" in readme
    spec = importlib.util.spec_from_file_location(
        "gaussian_origin_two_power_c16", PREDECESSOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


def taylor_clears():
    """The degree-100 Taylor sum of exp(361) exceeds 2^{323}*(319/100)."""
    assert 17 * 19 == 323
    target = Fraction((1 << 323) * 319, 100)
    assert target == Fraction(1362759728917540632568023848536174249116525485263544467226212545790576185048048670914649811465535488, 25)
    series = Fraction(0)
    power = Fraction(1)
    for index in range(100):
        series += power
        power *= Fraction(361, index + 1)
    assert power > 0
    assert series == Fraction(2969262568355185131865279849448531767194106568087574105573066202167288126037502648944171251000218777297143125238252194316443852981516343220833012784466843598725923346082891803715807048957377133313164516710215134358455389302459868695011043210647, 129078169678523532657923135545433909486219129176803309633464934177557144714312902842003932721896499134508704858680551127646208000000000000000000000)
    assert series < target
    series += power
    power *= Fraction(361, 101)
    assert power > 0
    assert power == Fraction(821219754307572944556380793266707242420628796945676126959387120272108862253574739642528874604857727168517200686461759215150786497520821887524347060009720715994452112732345381748613374039658106540103920521289177085834914077535832365726886577910513801539, 3806773380159016025147469113505936858567574557682283207710147838764515311914516130616379983834171552474930723692206813856541966336000000000000000000000000)
    assert series == Fraction(184815978517684490740844659077199914137867681033228529994468824307473853380387806562332060374008927639068543556147368343235418922601991634205441845143545646638968412007436071787828585087885472530049082378482381428846083359082081154408569441882228347, 2217107385066404208006679739956864798233881512919209788998338869402746250387021625286185197340810455722149518749101231133687808000000000000000000000000)
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
