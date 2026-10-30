"""Five-percent screen of the strongest legal rank-1 surcharge on rank-16 delivery."""

import hashlib
import sys
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research" / "complex-local-word-ceiling"))
import ceiling as C  # noqa: E402

PACKAGE = Path(__file__).resolve().parent
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
M, FAMILIES, STAGES, CENTRE = 73, 896, 9, 64
GRID = Q(1, 10 ** 15)
CEILING_SHA = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
BASE_HI = Q(1690054109089, 1000000000000000)
FULL_HI = Q(285077936577, 125000000000000)
LEMMA = (
    "Delivering the selected local mass as rank-16 children and spending all "
    "1646 idle-mass units on extra rank-1 children still clears the five-percent ceiling gate."
)


def require(ok, why):
    if not ok:
        raise SystemExit(why)


def main():
    ceiling_path = ROOT / "research" / "complex-local-word-ceiling" / "ceiling.py"
    digest = hashlib.sha256(ceiling_path.read_bytes()).hexdigest()
    require(digest == CEILING_SHA, "ceiling.py hash changed")
    require(LEMMA in (PACKAGE / "README.md").read_text(encoding="utf-8"), "README dropped the lemma")
    mass = sum(rank * Q(count) for rank, count in WORD.items())
    require(mass == 5586, "selected local mass changed")
    idle = C.model(WORD, M, FAMILIES, STAGES, CENTRE)["idle_mass"]
    require(idle == 1646, "idle mass is not 1646")
    base_hi = C.ceiling(WORD, M, FAMILIES, STAGES, CENTRE, grid=GRID)[1]
    full = {16: mass / 16, 1: idle}
    full_hi = C.ceiling(full, M, FAMILIES, STAGES, CENTRE, grid=GRID)[1]
    require(base_hi == BASE_HI, "selected ceiling moved")
    require(full_hi == FULL_HI, "surcharge ceiling moved")
    require(full_hi > base_hi * Q(21, 20), "five-percent gate failed")
    try:
        C.model({16: mass / 16, 1: idle + 1}, M, FAMILIES, STAGES, CENTRE)
    except ValueError as exc:
        require("coverage law" in str(exc), "unexpected rejection")
    else:
        require(False, "one extra rank-1 child was accepted")
    print("PASS_RANK16_RANK1_SURCHARGE")


if __name__ == "__main__":
    main()
