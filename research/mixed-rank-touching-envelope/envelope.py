"""Check a synchronized-factor lower envelope for signed power invoices.

New work produced by Nick Petalas. Apache-2.0.
"""

import argparse
import hashlib
import json
from pathlib import Path


MAX_RANK = 10**9
MAX_COUNT = 10**60
MAX_BYTES = 1024**2


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high):
    require(type(value) is int and low <= value <= high, "integer outside capacity")
    return value


def fields(value, names):
    require(type(value) is dict and set(value) == set(names), "unexpected fields")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def reject_number(value):
    raise ValueError("noninteger JSON number: " + value)


def load(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    return decode(raw), hashlib.sha256(raw).hexdigest()


def decode(raw):
    require(len(raw) <= MAX_BYTES, "input exceeds one MiB")
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_float=reject_number, parse_constant=reject_number)


def histogram(value):
    require(type(value) is dict and len(value) <= 4096, "invalid histogram")
    result = {}
    for text, count in value.items():
        require(type(text) is str and text.isascii() and text.isdecimal(), "invalid rank")
        require(len(text) <= 10, "rank spelling exceeds capacity")
        rank = integer(int(text), 1, MAX_RANK)
        require(str(rank) == text, "noncanonical rank")
        count = integer(count, 0, MAX_COUNT)
        if count:
            result[rank] = count
    return result


def invoice(value):
    fields(value, ("schema", "contract", "paid", "targets"))
    require(value["schema"] == "integer-mult-recursive-invoice/v1", "wrong invoice schema")
    require(type(value["contract"]) is dict and bool(value["contract"]), "missing contract")
    return histogram(value["paid"]), histogram(value["targets"])


def difference(old, new):
    old_paid, old_targets = invoice(old)
    new_paid, new_targets = invoice(new)
    # Canonical JSON distinguishes numeric values from Boolean aliases.
    old_contract = json.dumps(old["contract"], sort_keys=True, separators=(",", ":"))
    new_contract = json.dumps(new["contract"], sort_keys=True, separators=(",", ":"))
    require(old_contract == new_contract, "accounting contracts differ")
    result = {}
    for values, sign in ((new_paid, 1), (new_targets, -1),
                         (old_paid, -1), (old_targets, 1)):
        for rank, count in values.items():
            result[rank] = result.get(rank, 0) + sign * count
    return {rank: count for rank, count in result.items() if count}


def expand(certificate):
    fields(certificate, ("bases", "p", "q", "scale", "offset"))
    bases = certificate["bases"]
    require(type(bases) is list and 2 <= len(bases) <= 8, "factor count outside capacity")
    require(len(bases) % 2 == 0, "odd number of synchronized factors")
    q = integer(certificate["q"], 2, 16)
    p = integer(certificate["p"], 1, q - 1)
    scale = integer(certificate["scale"], 1, MAX_COUNT)
    offset = integer(certificate["offset"], 0, MAX_COUNT)
    result = {1: scale}
    for value in bases:
        base = integer(value, 2, 64)
        rank_factor, constant = base**q, base**p
        next_result = {}
        for rank, count in result.items():
            require(rank * rank_factor <= MAX_RANK, "expanded rank outside capacity")
            next_result[rank] = next_result.get(rank, 0) - constant * count
            high_rank = rank * rank_factor
            next_result[high_rank] = next_result.get(high_rank, 0) + count
        result = {rank: count for rank, count in next_result.items() if count}
        require(len(result) <= 256, "expanded support outside capacity")
    result[1] = result.get(1, 0) + offset
    require(all(abs(count) <= MAX_COUNT for count in result.values()), "coefficient outside capacity")
    return {rank: count for rank, count in result.items() if count}


def check(document):
    fields(document, ("schema", "old", "new", "certificate"))
    require(document["schema"] == "synchronized-invoice-envelope/v1", "wrong envelope schema")
    expected = expand(document["certificate"])
    actual = difference(document["old"], document["new"])
    require(actual == expected, "signed invoice does not match factor certificate")
    cert = document["certificate"]
    return {
        "claim_type": "scoped algebraic proof certificate",
        "difference": "new paid-minus-target cost minus old paid-minus-target cost",
        "domain": "every real t; in particular 0<t<1",
        "minimum": cert["offset"],
        "unique_minimizer": {"numerator": cert["p"], "denominator": cert["q"]},
        "root_multiplicity": len(cert["bases"]) if cert["offset"] == 0 else 0,
        "order": "nonnegative with one equality" if cert["offset"] == 0 else "strictly positive",
        "support_size": len(expected),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        document, digest = load(args.input)
        result = check(document)
    except (OSError, ValueError, TypeError, RecursionError) as error:
        parser.error(str(error))
    result["input_sha256"] = digest
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
