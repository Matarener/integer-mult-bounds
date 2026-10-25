#!/usr/bin/env python3
"""Bind the exact F0/B_1_2 entry width to one F17 decoder arithmetic bill.

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
PARAMETERS = {"h": 73, "lambda": 1, "f": 64, "e": 0, "beta": 64}
INPUTS = {
    "research/qq16-producer-entry-contract/README.md":
        "83029c16c55be649e223bd583a14529d26a9c2e44afcf2766a3f70504b641ffe",
    "research/qq16-finite-dyadic-format/README.md":
        "916cb7e48b28bf6940822c0aca375bb1558ae5282cb4246fd3e9b19e4f41a9e6",
    "research/qq16-rounded-pair-bit-circuit/README.md":
        "7357e10ce43ab8eaea5f39f00a9166877bd6e13803c1ab0a1aeec890b02d6646",
    "research/qq16-rounded-producer-envelope/README.md":
        "7e45a72f4d5a160d4b62478259c6d6b664d22799e98b0dd997be75367636edac",
}
EXPECTED = {
    "schema_version": 1,
    "status": "PASS_QQ16_F17_PAIR_BILL",
    "producer": "F_0_then_B_1_2",
    "consumer": "PR2707_zero_retention_decoder_in_F17",
    "parameters": PARAMETERS,
    "Q0": 80,
    "b": 79,
    "k": 137,
    "Qmax": 497,
    "E": 15,
    "W": 532,
    "w": 529,
    "L": 531,
    "exponent_bits": 10,
    "gates_per_pair": 159192,
    "pair_kernel_coefficient": 26744256,
    "field_bit_coefficient": 493696,
    "control_gates_per_pair": 124028,
    "control_pair_kernel_coefficient": 20836704,
    "dirty_width_supplied": False,
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
    candidates = [Path.cwd(), *PACKAGE.parents]
    marker = "research/qq16-finite-dyadic-format/README.md"
    for candidate in candidates:
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
        path = root / name
        raw = read_bytes(path)
        need(hashlib.sha256(raw).hexdigest() == digest, "source hash: " + name)
        texts[name] = normalized(raw.decode("utf-8"))
    return texts


def require_phrases(texts):
    entry = texts["research/qq16-producer-entry-contract/README.md"]
    finite = texts["research/qq16-finite-dyadic-format/README.md"]
    pair = texts["research/qq16-rounded-pair-bit-circuit/README.md"]
    dirty = texts["research/qq16-rounded-producer-envelope/README.md"]
    for phrase in (
        "norm <= B = 17628*H",
        "B < 2^(e+15)",
        "ceil(lambda/2) + 6 + 9*lambda",
        "k = beta+37 + ceil_log2(lambda) + floor(73*lambda/2)",
        "W = Qmax + e + 35",
        "W=532",
        "X is in F17 and Y in F17",
        "physical endpoint adapter or consumer still needs its own invoice",
    ):
        need(phrase in entry, "missing entry phrase: " + phrase)
    for phrase in (
        "Qmax = Q0 + 3*k + 6",
        "W = Qmax + E + 20",
        "2*464*N*D*W",
        "32369*B < 2^(E+15)",
        "less than `2^(E+16)`",
        "smaller than `2^(Qmax+E+16)`",
        "smaller than `2^(Qmax+E+18)`",
        "W=456",
        "A norm bound alone would not bound PR2771's adaptive exponent",
    ):
        need(phrase in finite, "missing format phrase: " + phrase)
    for phrase in (
        "24Lk+52L+4*2^k+4k+4",
        "124,028",
        "w=453",
        "L=455",
        "20836704*lambda*N*D",
    ):
        need(phrase in pair, "missing pair phrase: " + phrase)
    for phrase in (
        "B1 is below `2^(delta+80) H`",
        "component representation/grid",
        "subsequent F17 consumption are unknown",
        "a paid F17 consumer",
    ):
        need(phrase in dirty, "missing dirty-ledger phrase: " + phrase)


def ceil_log2(value):
    need(type(value) is int and value >= 1, "ceil_log2 domain")
    if value == 1:
        return 0
    return (value - 1).bit_length()


def runtime_gates(length):
    """PR2811 runtime-exponent pair count: 24*L*k+52*L+4*2^k+4*k+4."""
    need(type(length) is int and length >= 3, "pair length")
    bits = (length - 2).bit_length()
    gates = 24 * length * bits + 52 * length + 4 * (1 << bits) + 4 * bits + 4
    return gates, bits


def derive():
    h = PARAMETERS["h"]
    lam = PARAMETERS["lambda"]
    fractional = PARAMETERS["f"]
    exponent = PARAMETERS["e"]
    beta = PARAMETERS["beta"]
    need(17628 < 2 ** 15, "post-B1 norm does not fit E=e+15")
    need(32369 < 2 ** 15, "completed-field majorant does not fit E")
    # Q0 uses ceil(lambda/2), which is not ceil_log2(lambda) except at lambda=1.
    q0 = fractional + (lam + 1) // 2 + 6 + 9 * lam
    relative = beta + 15
    precision = relative + 22 + ceil_log2(lam) + (h * lam) // 2
    qmax = q0 + 3 * precision + 6
    entry_exponent = exponent + 15
    width = qmax + entry_exponent + 20
    need(width == qmax + exponent + 35, "entry-contract width identity")
    component_bits = width - 3
    length = component_bits + 2
    gates, bits = runtime_gates(length)
    # Strict component bound abs < 2^(W-4) fits in signed (W-3) bits.
    need(component_bits - 1 == width - 4, "component width slack")
    need(length - 1 == width - 2, "numerator width slack")
    coefficient = gates * 168
    field_bits = 2 * 464 * width
    control_gates, control_bits = runtime_gates(455)
    need(control_bits == 9 and control_gates == 124028, "published pair control")
    need(control_gates * 168 == 20836704, "published kernel coefficient")
    bill = {
        "Q0": q0,
        "b": relative,
        "k": precision,
        "Qmax": qmax,
        "E": entry_exponent,
        "W": width,
        "w": component_bits,
        "L": length,
        "exponent_bits": bits,
        "gates_per_pair": gates,
        "pair_kernel_coefficient": coefficient,
        "field_bit_coefficient": field_bits,
        "control_gates_per_pair": control_gates,
        "control_pair_kernel_coefficient": control_gates * 168,
        "dirty_width_supplied": False,
    }
    for key, value in bill.items():
        need(value == EXPECTED[key], "recomputed bill mismatch: " + key)
    return bill


def certificate_matches(root, bill):
    path = PACKAGE / "CERTIFICATE.json"
    raw = read_bytes(path)
    data = json.loads(raw, object_pairs_hook=unique)
    need(type(data) is dict, "certificate object")
    need(set(data) == set(EXPECTED), "certificate keys")
    for key, value in EXPECTED.items():
        if key == "parameters":
            need(type(data[key]) is dict and set(data[key]) == set(PARAMETERS), "parameters")
            for name, item in PARAMETERS.items():
                need(type(data[key][name]) is int and data[key][name] == item, name)
        elif type(value) is int:
            need(type(data[key]) is int and data[key] == bill.get(key, value), key)
        elif type(value) is bool:
            need(type(data[key]) is bool and data[key] is value, key)
        else:
            need(type(data[key]) is str and data[key] == value, key)
    need(root.is_dir(), "root")


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
    certificate_matches(root, bill)
    print(
        "PASS_QQ16_F17_PAIR_BILL "
        f"W={bill['W']} gates_per_pair={bill['gates_per_pair']} "
        f"pair_kernel={bill['pair_kernel_coefficient']}*lambda*N*D "
        f"field_bits={bill['field_bit_coefficient']}*N*D "
        "dirty_width=unsupplied control_gates=124028"
    )


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise SystemExit("FAIL_QQ16_F17_PAIR_BILL " + str(exc))
