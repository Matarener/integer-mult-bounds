#!/usr/bin/env python3
"""Second evaluation of the F17 block-scale scan at the exact entry width.

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
    "research/qq16-block-scale-scan/README.md":
        "86b082070985c89efc43448bd0a8d3426f74720ff0d901a48b81b205432f17ec",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def locate():
    marker = Path("research/qq16-block-scale-scan/README.md")
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


def ones_below(limit):
    """Count set bits in 0..limit-1 by complete dyadic blocks."""
    need(type(limit) is int and 0 <= limit <= 10000, "span")
    total = 0
    shift = 0
    remaining = limit
    while remaining:
        block = 1 << shift
        if block > remaining:
            break
        # Numbers with this bit set come in the upper half of each 2^(shift+1) window.
        window = block << 1
        total += (limit // window) * block
        tail = limit % window
        if tail > block:
            total += tail - block
        shift += 1
    direct = 0
    for value in range(limit):
        direct += value.bit_count()
    need(total == direct, "ones table")
    return total


def polynomial(width, reserve):
    """Return (coefficient of D, constant) for q=2D in G_scan."""
    need(0 <= reserve < width, "reserve")
    span = width - reserve
    ones = ones_below(span)
    constant = width * 2 - 2 * reserve + ones + 3
    return 8 * width, constant, ones


def roles(width, reserve):
    """Same roles as the scan proof, evaluated at q=2 and doubled into the D slope."""
    ones = ones_below(width - reserve)
    at_two = 3 * width * 2 + width + 3 * (width - reserve) + ones + reserve + 3
    at_four = 3 * width * 4 + 3 * width + 3 * (width - reserve) + ones + reserve + 3
    slope = at_four - at_two
    need(slope == 8 * width, "two extra complex coordinates add 8w gates")
    stated = width * (4 * 2 + 2) - 2 * reserve + ones + 3
    need(at_two == stated, "role sum matches the polynomial at q=2")
    return at_two


def main():
    root = locate()
    entry = text_of(root, "research/qq16-producer-entry-contract/README.md")
    scan = text_of(root, "research/qq16-block-scale-scan/README.md")
    need("W=532" in entry and "k=137" in entry and "Q0=80" in entry, "published width")
    need("W = Qmax + e + 35" in entry and "B < 2^(e+15)" in entry, "width formula")
    need("X is in F17 and Y in F17" in entry, "F17 charts")
    need("G_scan(w,q,p) = w*(4q+2) - 2p + S(w-p) + 3" in scan, "scan polynomial")
    need("one scan per line per owner, not per factor" in scan, "scan multiplicity")
    need("multiply by 336" in scan and "1,217,664*N*D + 666,624*N" in scan, "published control")
    need("With `w=W-3`" in scan and "supplies `p=k`" in scan, "width binding")
    q0 = 64 + (1 + 1) // 2 + 6 + 9 * 1
    relative = 64 + 15
    precision = relative + 22 + 0 + 73 // 2
    qmax = q0 + 3 * precision + 6
    width = qmax + 0 + 35
    need(q0 == 80 and relative == 79 and precision == 137 and qmax == 497 and width == 532, "chain")
    need(17628 < 2 ** 15, "entry exponent slack")
    component = width - 3
    need(component == 529 and precision < component, "scan domain")
    per_nd, per_const, ones = polynomial(component, precision)
    roles(component, precision)
    need(ones == 1628 and per_nd == 4232 and per_const == 2415, "one line")
    need(336 * per_nd == 1421952 and 336 * per_const == 811440, "decoder scans")
    control_nd, control_const, _control_ones = polynomial(453, 122)
    roles(453, 122)
    need(control_nd == 3624 and control_const == 1984, "W=456 line")
    need(336 * control_nd == 1217664 and 336 * control_const == 666624, "W=456 decoder")
    print(
        "PASS_QQ16_F17_SCAN_BILL_INDEPENDENT "
        f"W={width} scan={336 * per_nd}*N*D+{336 * per_const}*N "
        f"control={336 * control_nd}*N*D+{336 * control_const}*N no_new_kappa"
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, UnicodeError, ValueError) as exc:
        raise SystemExit("FAIL_QQ16_F17_SCAN_BILL_INDEPENDENT " + str(exc))
