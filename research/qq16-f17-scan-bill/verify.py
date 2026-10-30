#!/usr/bin/env python3
"""Price one F17 block-scale scan term at the exact F0/B_1_2 entry width.

Wentao Li, with substantial AI assistance. Apache-2.0.
Predecessor verifiers are not imported. Admission uses need(), including under -O.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
MAX_BYTES = 1_048_576
LINES = 336
PARAMETERS = {"h": 73, "lambda": 1, "f": 64, "e": 0, "beta": 64}
INPUTS = {
    "research/qq16-producer-entry-contract/README.md":
        "83029c16c55be649e223bd583a14529d26a9c2e44afcf2766a3f70504b641ffe",
    "research/qq16-block-scale-scan/README.md":
        "86b082070985c89efc43448bd0a8d3426f74720ff0d901a48b81b205432f17ec",
}
EXPECTED = {
    "schema_version": 1,
    "status": "PASS_QQ16_F17_SCAN_BILL",
    "producer": "F_0_then_B_1_2",
    "consumer": "PR2707_zero_retention_decoder_in_F17",
    "priced_term": "block_scale_scan",
    "physical_bill": "F17 direct Boolean block-scale scan gate evaluations",
    "parameters": PARAMETERS,
    "Q0": 80,
    "b": 79,
    "k": 137,
    "Qmax": 497,
    "E": 15,
    "W": 532,
    "w": 529,
    "p": 137,
    "popcount_span": 392,
    "popcount_sum": 1628,
    "lines": 336,
    "scan_per_line_nd": 4232,
    "scan_per_line_const": 2415,
    "scan_nd_coefficient": 1421952,
    "scan_owner_coefficient": 811440,
    "control_W": 456,
    "control_w": 453,
    "control_p": 122,
    "control_scan_per_line_nd": 3624,
    "control_scan_per_line_const": 1984,
    "control_scan_nd_coefficient": 1217664,
    "control_scan_owner_coefficient": 666624,
    "selected_kappa": "0.001672660197076918",
    "kappa_changed": False,
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def root_dir():
    marker = "research/qq16-block-scale-scan/README.md"
    for candidate in (Path.cwd(), *PACKAGE.parents):
        if (candidate / marker).is_file():
            return candidate
    need(False, "repository root")
    return None


def read_bytes(path):
    need(path.is_file() and not path.is_symlink(), "expected plain file: " + path.name)
    with path.open("rb") as source:
        raw = source.read(MAX_BYTES + 1)
    need(len(raw) <= MAX_BYTES, "file byte capacity: " + path.name)
    return raw


def normalized(text):
    return re.sub(r"\s+", " ", text)


def load_sources(root):
    texts = {}
    for name, digest in INPUTS.items():
        raw = read_bytes(root / name)
        need(hashlib.sha256(raw).hexdigest() == digest, "source hash: " + name)
        texts[name] = normalized(raw.decode("utf-8"))
    return texts


def require_phrases(texts):
    entry = texts["research/qq16-producer-entry-contract/README.md"]
    scan = texts["research/qq16-block-scale-scan/README.md"]
    for phrase in (
        "norm <= B = 17628*H",
        "Q0 = f + ceil(lambda/2) + 6 + 9*lambda",
        "B < 2^(e+15)",
        "k = beta+37 + ceil_log2(lambda) + floor(73*lambda/2)",
        "Qmax = Q0 + 3*k + 6",
        "W = Qmax + e + 35",
        "W=532",
        "Q0=80",
        "k=137",
        "X is in F17 and Y in F17",
    ):
        need(phrase in entry, "missing entry phrase: " + phrase)
    for phrase in (
        "G_scan(w,q,p) = w*(4q+2) - 2p + S(w-p) + 3",
        "S(n) = sum_{0 <= i < n} popcount(i)",
        "one scan costs `3624D + 1984` gates",
        "supplies `p=k`",
        "With `w=W-3`",
        "one scan per line per owner, not per factor",
        "unchanged 336-line decoder, multiply by 336",
        "1,217,664*N*D + 666,624*N",
    ):
        need(phrase in scan, "missing scan phrase: " + phrase)


def ceil_log2(value):
    need(type(value) is int and value >= 1, "ceil_log2 domain")
    if value == 1:
        return 0
    return (value - 1).bit_length()


def popcount_sum(limit):
    """S(limit) = sum of popcount(i) for 0 <= i < limit."""
    need(type(limit) is int and limit >= 0, "popcount span")
    total = 0
    bit = 0
    while (1 << bit) < limit or (bit == 0 and limit > 0):
        period = 1 << (bit + 1)
        half = 1 << bit
        total += (limit // period) * half + max(0, (limit % period) - half)
        bit += 1
        need(bit <= limit.bit_length() + 2, "popcount bit walk")
        if (1 << bit) >= limit and bit > 0:
            break
    return total


def scan_formula(width, components, reserve):
    """Stated polynomial G_scan(w,q,p) = w*(4q+2) - 2p + S(w-p) + 3."""
    need(type(width) is int and width >= 1, "scan width")
    need(type(components) is int and components >= 0, "component count")
    need(type(reserve) is int and 0 <= reserve < width, "scan reserve")
    return width * (4 * components + 2) - 2 * reserve + popcount_sum(width - reserve) + 3


def scan_breakdown(width, components, reserve):
    """Gate roles stated in the scan proof, summed separately from the polynomial."""
    need(type(components) is int and components >= 1, "breakdown components")
    absolute = 3 * width * components
    magnitude_or = (components - 1) * width
    leading = 3 * (width - reserve)
    exponent_or = popcount_sum(width - reserve)
    low_or = reserve
    flags = 3
    return absolute + magnitude_or + leading + exponent_or + low_or + flags


def check_popcount_table():
    for limit in range(0, 513):
        direct = sum(value.bit_count() for value in range(limit))
        need(popcount_sum(limit) == direct, "popcount table: " + str(limit))


def scan_invoice(component_bits, reserve):
    need(scan_formula(component_bits, 1, reserve) == scan_breakdown(component_bits, 1, reserve),
         "one-component identity")
    need(scan_formula(component_bits, 2, reserve) == scan_breakdown(component_bits, 2, reserve),
         "two-component identity")
    need(scan_formula(component_bits, 4, reserve) == scan_breakdown(component_bits, 4, reserve),
         "four-component identity")
    # q = 2D real components. The D coefficient is 8w; the rest is independent of D.
    per_line_nd = 8 * component_bits
    per_line_const = scan_formula(component_bits, 0, reserve)
    need(per_line_const == 2 * component_bits - 2 * reserve + popcount_sum(component_bits - reserve) + 3,
         "constant term")
    need(0 <= component_bits - 1 - reserve <= component_bits, "exponent fits the signed kernel range")
    return {
        "popcount_span": component_bits - reserve,
        "popcount_sum": popcount_sum(component_bits - reserve),
        "scan_per_line_nd": per_line_nd,
        "scan_per_line_const": per_line_const,
        "scan_nd_coefficient": LINES * per_line_nd,
        "scan_owner_coefficient": LINES * per_line_const,
    }


def derive():
    h = PARAMETERS["h"]
    lam = PARAMETERS["lambda"]
    fractional = PARAMETERS["f"]
    exponent = PARAMETERS["e"]
    beta = PARAMETERS["beta"]
    need(17628 < 2 ** 15, "post-B1 norm does not fit E=e+15")
    q0 = fractional + (lam + 1) // 2 + 6 + 9 * lam
    relative = beta + 15
    precision = relative + 22 + ceil_log2(lam) + (h * lam) // 2
    qmax = q0 + 3 * precision + 6
    entry_exponent = exponent + 15
    width = qmax + exponent + 35
    need(width == qmax + entry_exponent + 20, "format width identity")
    component_bits = width - 3
    reserve = precision
    check_popcount_table()
    invoice = scan_invoice(component_bits, reserve)
    control = scan_invoice(453, 122)
    bill = {
        "Q0": q0,
        "b": relative,
        "k": precision,
        "Qmax": qmax,
        "E": entry_exponent,
        "W": width,
        "w": component_bits,
        "p": reserve,
        "lines": LINES,
        "control_W": 456,
        "control_w": 453,
        "control_p": 122,
        "control_scan_per_line_nd": control["scan_per_line_nd"],
        "control_scan_per_line_const": control["scan_per_line_const"],
        "control_scan_nd_coefficient": control["scan_nd_coefficient"],
        "control_scan_owner_coefficient": control["scan_owner_coefficient"],
    }
    bill.update(invoice)
    for key, value in bill.items():
        need(value == EXPECTED[key], "recomputed bill mismatch: " + key)
    return bill


def certificate_matches(bill):
    raw = read_bytes(PACKAGE / "CERTIFICATE.json")
    data = json.loads(raw, object_pairs_hook=unique)
    need(type(data) is dict, "certificate object")
    need(set(data) == set(EXPECTED), "certificate keys")
    for key, value in EXPECTED.items():
        if key == "parameters":
            need(type(data[key]) is dict and set(data[key]) == set(PARAMETERS), "parameters")
            for name, item in PARAMETERS.items():
                need(type(data[key][name]) is int and data[key][name] == item, name)
        elif type(value) is int:
            need(type(data[key]) is int and not type(data[key]) is bool and data[key] == bill.get(key, value), key)
        elif type(value) is bool:
            need(type(data[key]) is bool and data[key] is value, key)
        else:
            need(type(data[key]) is str and data[key] == value, key)


def canonical_certificate():
    return json.dumps(EXPECTED, indent=2, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = root_dir()
    texts = load_sources(root)
    require_phrases(texts)
    bill = derive()
    destination = PACKAGE / "CERTIFICATE.json"
    if args.write:
        need(not destination.exists(), "certificate already exists")
        destination.write_text(canonical_certificate(), encoding="utf-8")
    certificate_matches(bill)
    print(
        "PASS_QQ16_F17_SCAN_BILL "
        f"W={bill['W']} scan={bill['scan_nd_coefficient']}*N*D+"
        f"{bill['scan_owner_coefficient']}*N "
        f"control={bill['control_scan_nd_coefficient']}*N*D+"
        f"{bill['control_scan_owner_coefficient']}*N no_new_kappa"
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise SystemExit("FAIL_QQ16_F17_SCAN_BILL " + str(exc))
