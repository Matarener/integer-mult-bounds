#!/usr/bin/env python3
"""Second arithmetic check of the F17 pair-kernel bill.

This program is separate from the primary checker and from predecessor checkers.
Wentao Li, with substantial AI assistance. Apache-2.0.
"""

import hashlib
import re
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
MAX_BYTES = 1_048_576
DIGESTS = {
    "research/qq16-producer-entry-contract/README.md":
        "83029c16c55be649e223bd583a14529d26a9c2e44afcf2766a3f70504b641ffe",
    "research/qq16-finite-dyadic-format/README.md":
        "916cb7e48b28bf6940822c0aca375bb1558ae5282cb4246fd3e9b19e4f41a9e6",
    "research/qq16-rounded-pair-bit-circuit/README.md":
        "7357e10ce43ab8eaea5f39f00a9166877bd6e13803c1ab0a1aeec890b02d6646",
    "research/qq16-rounded-producer-envelope/README.md":
        "7e45a72f4d5a160d4b62478259c6d6b664d22799e98b0dd997be75367636edac",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def locate():
    marker = Path("research/qq16-finite-dyadic-format/README.md")
    for candidate in (Path.cwd(), *PACKAGE.parents):
        if (candidate / marker).is_file():
            return candidate
    need(False, "repository root")
    return None


def text_of(root, name):
    path = root / name
    need(path.is_file() and not path.is_symlink(), "plain source")
    raw = path.read_bytes()
    need(len(raw) <= MAX_BYTES, "source capacity")
    need(hashlib.sha256(raw).hexdigest() == DIGESTS[name], "source hash")
    return re.sub(r"\s+", " ", raw.decode("utf-8"))


def pair_gates(length):
    exponent_bits = (length - 2).bit_length()
    total = (24 * length * exponent_bits) + (52 * length)
    total += 4 * (2 ** exponent_bits) + 4 * exponent_bits + 4
    return total, exponent_bits


def main():
    root = locate()
    entry = text_of(root, "research/qq16-producer-entry-contract/README.md")
    finite = text_of(root, "research/qq16-finite-dyadic-format/README.md")
    pair = text_of(root, "research/qq16-rounded-pair-bit-circuit/README.md")
    dirty = text_of(root, "research/qq16-rounded-producer-envelope/README.md")
    need("17628*H" in entry and "W=532" in entry and "X is in F17 and Y in F17" in entry, "entry contract")
    need("2^(e+15)" in entry, "entry exponent")
    need("A norm bound alone would not bound PR2771's adaptive exponent" in finite, "format obstruction")
    need("2*464*N*D*W" in finite and "W = Qmax + E + 20" in finite, "storage formula")
    need("24Lk+52L+4*2^k+4k+4" in pair and "20836704*lambda*N*D" in pair, "pair formula")
    need("B1 is below `2^(delta+80) H`" in dirty, "dirty norm")
    need("component representation/grid" in dirty and "subsequent F17 consumption are unknown" in dirty,
         "dirty grid gap")
    # lambda=1, f=64, e=0, beta=64, h=73. ceil(lambda/2)=1 and ceil_log2(1)=0.
    q0 = 64 + 1 + 6 + 9
    relative_b = 64 + 15
    k = relative_b + 22 + 0 + (73 // 2)
    qmax = q0 + 3 * k + 6
    width = qmax + 0 + 35
    need(q0 == 80 and relative_b == 79 and k == 137 and qmax == 497 and width == 532, "width chain")
    need(17628 < 32768 and 32369 < 32768, "power-of-two slack")
    component_width = width - 3
    length = component_width + 2
    gates, exponent_bits = pair_gates(length)
    need(component_width == 529 and length == 531 and exponent_bits == 10, "pair shape")
    need(gates == 159192 and gates * 168 == 26744256, "kernel coefficient")
    need(2 * 464 * width == 493696, "field bits")
    control, control_bits = pair_gates(455)
    need(control_bits == 9 and control == 124028 and control * 168 == 20836704, "control")
    # The dirty all-cut norm is not an entry exponent. The format proof blocks that substitution.
    need("dirty_width_supplied" not in dirty, "ledger must not already claim this flag")
    print(
        "PASS_QQ16_F17_PAIR_BILL_INDEPENDENT "
        f"W={width} gates_per_pair={gates} "
        f"pair_kernel={gates * 168}*lambda*N*D "
        f"field_bits={2 * 464 * width}*N*D dirty_width=unsupplied"
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit("FAIL_QQ16_F17_PAIR_BILL_INDEPENDENT " + str(exc))
