#!/usr/bin/env python3
"""This section's polynomial-inverse error is strictly below 2^{-399}."""

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
    "research/gaussian-origin-two-power-c16/README.md":
        "8452267974318bcd6f68a699f06898925de281b9a1cc32ed43f0d3d86e878d84",
    "research/gaussian-origin-two-power-c16/verify.py":
        "15828ffe60a8cd03c695dcf8987237d7b4078971df40f60006cdfe41468ddf63",
    "research/gaussian-origin-two-power-c17/README.md":
        "65083c4b532f92b4eff3c7282050aa420e30875f7690e367088c35eb7c71d76d",
    "research/gaussian-origin-two-power-c17/verify.py":
        "b78165b9194d451a0c1bd000fb8c1517ccb81ec0c7eada0c756f84d10b05a50b",
    "research/gaussian-origin-two-power-c18/README.md":
        "874e22e45f8912d3358e7dad4c6574ad139dab6c99964a78ba68fee33bc19f4b",
    "research/gaussian-origin-two-power-c18/verify.py":
        "5828041d770ea59397c2f0f589fca730e56468407395c8285b0db4462f150372",
    "research/gaussian-origin-two-power-c19/README.md":
        "ddf983166558979c63d9e2c24c3c4b26dad4e83e99f84b41f46bbdafb8ad8067",
    "research/gaussian-origin-two-power-c19/verify.py":
        "6017bd954e4e41214046f3ccc889bffef9ca150cfb0d2db8d6b68b1b0d2642ce",
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
PREDECESSOR = ROOT / "research/gaussian-origin-two-power-c20/verify.py"
PREDECESSOR_README = ROOT / "research/gaussian-origin-two-power-c20/README.md"
PREDECESSOR_SHA = "35aae5955a796185076b7e66b243801a973967d7b8ca980074f4a1171a53c688"
PREDECESSOR_README_SHA = "995b7ade5e09412735cb63dd89df8f23de153db2b2810c4b2caf932d39448e45"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def predecessor_bound():
    """Replay the inherited proof that the section error is below 2^{-380}."""
    assert digest(PREDECESSOR) == PREDECESSOR_SHA
    assert digest(PREDECESSOR_README) == PREDECESSOR_README_SHA
    readme = PREDECESSOR_README.read_text(encoding="utf-8")
    assert "strictly below `(319/100) exp(-361)`" in readme
    assert "therefore strictly below\n`2^{-380}`" in readme
    spec = importlib.util.spec_from_file_location(
        "gaussian_origin_two_power_c20", PREDECESSOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()


def taylor_clears():
    """The degree-149 Taylor sum of exp(361) exceeds 2^{399}*(319/100)."""
    assert 21 * 19 == 399
    target = Fraction((1 << 399) * 319, 100)
    assert target == Fraction(102967213888715480012529776983620098488897018489065287574122541842058323927921542635857108462045496028506638982413306298368, 25)
    series = Fraction(0)
    power = Fraction(1)
    for index in range(149):
        series += power
        power *= Fraction(361, index + 1)
    assert power > 0
    assert series == Fraction(213494455561961148499157134235878141864498137504528246371531130505290185161352109441942801038849086182286386045865245363275941166070948989488319581081366179144800762372554878263622342093108625394308759040068377253864660597106484390576174913255395445549088173906306092353681606733412358630734717479960294257121720290212719865086822503685586195573195399343403321480287, 99586761270198339110293558169527407516433450487794677912201483440905449982227217006922566801549692328222847284897243684927230915229784412673113017954571781026853935905118989028239617039310806529909153822303846400000000000000000000000000000000000)
    assert series < target
    series += power
    power *= Fraction(361, 150)
    assert power > 0
    assert power == Fraction(472938946021537518458750783321233651295893254317495409466895013391492089775196580912612742322477554039066782310302418047586380150525443534199096091240763203162841257971853382448956671625236794473218723073121756737148588015667115095967498920121038943488582010620945061291401560950820451995823979399799034030779980066937076645022566274123986840431684323226655987734161110622659, 63917268072906985489547207457479019852864523537656294761264821499384968389570484444107226091276291201077012547486809183216235735805810619174700129093042135628971476069606199877100440794274806435518616156542475100487680000000000000000000000000000000000000)
    assert series == Fraction(5171133266652786947468019866487105716247763755628016763378800549360488738504557286755390437381699713345508953020226676041057868298475261656836786342115605448188988238224974729301779509636176576331835394811446832301112213681475415825996795658654929541432056481676093619084574711199029311194157768129956229137968869514675275449701160574157071248704133389640909665218234123, 990965396479178069605383061356263873687822070351260383895578627897441370380937743319491877384128545753131977480415646251414507531873032855421707427799102877968550016583041858559696756500384595899513428783604265123840000000000000000000000000000000000)
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
