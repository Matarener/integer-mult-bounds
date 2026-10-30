"""Exact F3 minimum for the one-source one-output additive connector."""

from itertools import product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
WITNESSES = ("BBAABA", "BABBAA", "BAABAB", "ABBAAB", "ABABBA", "AABABB")
LEMMA = (
    "Over F3, with arbitrary dirty x, y and z, every correct word in the "
    "additive alphabet {B, A} for the one-source one-output identity has "
    "length at least 6, and length 6 is attained by exactly six words."
)


def require(ok, why):
    if not ok:
        raise SystemExit(why)


def run(word, mod):
    # z = zx*x + zz*z0; y = yx*x + yy*y0 + yz*z0
    zx, zz, yx, yy, yz = 0, 1, 0, 1, 0
    for op in word:
        if op == "B":
            zx = (zx + 1) % mod
        elif op == "A":
            yx = (yx + zx) % mod
            yz = (yz + zz) % mod
        else:
            require(False, "unknown operator")
    return zx, zz, yx, yy, yz


def correct(word, mod):
    return run(word, mod) == (0, 1, 1, 1, 0)


def main():
    require(LEMMA in (PACKAGE / "README.md").read_text(encoding="utf-8"), "README dropped the lemma")
    require(correct("BABA", 2), "F2 control BABA failed")
    require(not correct("BABA", 3), "F2 witness must fail over F3")

    # Lower bound: B adds 1 to zx; A adds zz=1 to yz. Both finals need 0 mod 3.
    require(min(b + a for b in range(3, 10, 3) for a in range(3, 10, 3)) == 6,
            "count lower bound is not 6")
    for length in range(1, 6):
        for word in product("BA", repeat=length):
            text = "".join(word)
            require(not correct(text, 3), "unexpected short witness " + text)

    found = []
    for word in product("BA", repeat=6):
        text = "".join(word)
        if correct(text, 3):
            found.append(text)
            require(text.count("B") == 3 and text.count("A") == 3, "length-6 witness must use 3+3")
    require(tuple(found) == WITNESSES, "witness list changed: " + repr(found))
    for text in WITNESSES:
        require(correct(text, 3), "listed witness failed: " + text)
    print("PASS_F3_ADDITIVE_CONNECTOR_1X1")


if __name__ == "__main__":
    main()
