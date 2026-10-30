#!/usr/bin/env python3
"""Finite checks for the elementary-abelian diagonal minimum.

The uniform statement is PROOF.md. These checks compare two multiplication
engines and exhaust small words. They do not replace the written argument.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_json(text):
    def pairs(items):
        seen = set()
        out = {}
        for key, value in items:
            need(key not in seen, "duplicate JSON key: " + str(key))
            seen.add(key)
            out[key] = value
        return out

    return json.loads(text, object_pairs_hook=pairs)


def bit_mul(left, right):
    out = 0
    rest = left
    while rest:
        i = (rest & -rest).bit_length() - 1
        rest ^= 1 << i
        other = right
        while other:
            j = (other & -other).bit_length() - 1
            other ^= 1 << j
            if (i & j) == 0:
                out ^= 1 << (i | j)
    return out


def set_mul(left, right):
    out = set()
    for i in left:
        for j in right:
            if (i & j) == 0:
                monomial = i | j
                if monomial in out:
                    out.remove(monomial)
                else:
                    out.add(monomial)
    return out


def bits_of(monomials):
    value = 0
    for monomial in monomials:
        value |= 1 << monomial
    return value


def set_of(value):
    monomials = set()
    rest = value
    while rest:
        bit = (rest & -rest).bit_length() - 1
        monomials.add(bit)
        rest ^= 1 << bit
    return monomials


def delta(subset):
    """Group element for subset S, minus 1. Bit position is the subset mask."""
    element = 0
    mask = subset
    while True:
        element ^= 1 << mask
        if mask == 0:
            break
        mask = (mask - 1) & subset
    return element ^ 1


def linear_part(element, rank):
    image = 0
    for generator in range(rank):
        if (element >> (1 << generator)) & 1:
            image |= 1 << generator
    return image


def odd_dot(left, right):
    value = left & right
    parity = 0
    while value:
        parity ^= 1
        value &= value - 1
    return parity


def factors(rank, roles):
    found = []
    width = 1 << roles
    for subset in range(1, 1 << rank):
        step = delta(subset)
        slope = linear_part(step, rank)
        need(slope != 0, "non-identity label in m^2")
        for column in range(width):
            for row in range(width):
                if odd_dot(column, row):
                    found.append((step, column, row, slope))
    return found


def eye(roles):
    return [[1 if i == j else 0 for j in range(roles)] for i in range(roles)]


def zeros(roles):
    return [[0 for _ in range(roles)] for _ in range(roles)]


def matvec(matrix, vector):
    roles = len(matrix)
    image = [0] * roles
    index = 0
    rest = vector
    while rest:
        if rest & 1:
            for row in range(roles):
                image[row] ^= matrix[row][index]
        rest >>= 1
        index += 1
    return image


def apply(matrix, step, column, row, multiply):
    roles = len(matrix)
    image = matvec(matrix, column)
    scaled = [multiply(step, entry) for entry in image]
    updated = [line[:] for line in matrix]
    index = 0
    rest = row
    while rest:
        if rest & 1:
            for source in range(roles):
                updated[source][index] ^= scaled[source]
        rest >>= 1
        index += 1
    return updated


def direct(labels, multiply, roles=None):
    if roles is None:
        roles = len(labels)
    matrix = eye(roles)
    for index, subset in enumerate(labels):
        if subset:
            matrix = apply(matrix, delta(subset), 1 << index, 1 << index, multiply)
    return matrix


def diagonal_count(matrix):
    roles = len(matrix)
    count = 0
    for row in range(roles):
        for column in range(roles):
            if row != column and matrix[row][column]:
                return None
            if row == column and matrix[row][column] != 1:
                count += 1
    return count


def add_update(graded, slope, column, row):
    roles = len(graded)
    updated = [line[:] for line in graded]
    for source in range(roles):
        if (column >> source) & 1:
            for target in range(roles):
                if (row >> target) & 1:
                    updated[source][target] ^= slope
    return updated


def image_dimension(graded, rank):
    roles = len(graded)
    basis = {}
    dimension = 0
    for column in range(roles):
        word = 0
        for row in range(roles):
            bits = graded[row][column]
            generator = 0
            while bits:
                if bits & 1:
                    word |= 1 << (row * rank + generator)
                bits >>= 1
                generator += 1
        while word:
            lead = word.bit_length() - 1
            if lead in basis:
                word ^= basis[lead]
            else:
                basis[lead] = word
                dimension += 1
                break
    return dimension


def linear_matrix(matrix, rank):
    roles = len(matrix)
    graded = zeros(roles)
    for row in range(roles):
        for column in range(roles):
            entry = matrix[row][column]
            if row == column:
                entry ^= 1
            graded[row][column] = linear_part(entry, rank)
    return graded


def higher_term(element, rank):
    rest = element & ~1
    for generator in range(rank):
        rest &= ~(1 << (1 << generator))
    return rest != 0


def rank_rows(rows):
    basis = {}
    for row in rows:
        value = row
        while value:
            lead = value.bit_length() - 1
            if lead in basis:
                value ^= basis[lead]
            else:
                basis[lead] = value
                break
    return len(basis)


def socle_witness():
    """Image of the one-column module map r |-> r*(z1, z2) inside R^2."""
    values = {0}
    for scalar in range(16):
        left = bit_mul(scalar, 2)
        right = bit_mul(scalar, 4)
        values.add(left | (right << 4))
    socle = []
    for vector in values:
        if bit_mul(vector & 15, 2) == bit_mul(vector >> 4, 2) == 0 and (
                bit_mul(vector & 15, 4) == bit_mul(vector >> 4, 4) == 0):
            socle.append(vector)
    dimension = rank_rows(socle)
    need(len(values) == 8 and dimension == 2, "socle witness drifted")
    need(dimension > 1, "socle bound is not the obstruction used here")
    return {"columns": 1, "image_size": len(values), "socle_dimension": dimension}


def chain_ring_rejected():
    """(z1) and (z2) are incomparable, so the ring is not a chain ring."""
    for scalar in range(16):
        need(bit_mul(4, scalar) != 2, "z1 became a multiple of z2")
        need(bit_mul(2, scalar) != 4, "z2 became a multiple of z1")


def pins():
    rows = load_json((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]
    for row in rows:
        payload = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(payload).hexdigest() == row["sha256"], "source SHA: " + row["path"])
        header = b"blob " + str(len(payload)).encode("ascii") + b"\0"
        need(hashlib.sha1(header + payload).hexdigest() == row["git_blob"],
             "source blob: " + row["path"])
    proof = (HERE / "PROOF.md").read_text(encoding="utf-8")
    need("k\\ge 2" in proof or "k\\ge 2" in proof.replace(" ", ""), "proof missing rank hypothesis")
    need("not a chain ring" in proof, "proof missing chain-ring boundary")
    predecessor = (ROOT / "research/bit-cyclic-root-barrier/PROOF.md").read_text(encoding="utf-8")
    need("does not construct a saving" in predecessor, "predecessor sentence moved")
    need("F_2[z]/(z^q)" in predecessor or "F2[z]/(z^q)" in predecessor, "predecessor hypothesis moved")


def agree(left, right):
    need(len(left) == len(right), "shape")
    for row in range(len(left)):
        need(left[row] == right[row], "engines disagree")


def record_product(product, graded, rank, length, stats):
    roles = len(product)
    observed = linear_matrix(product, rank)
    for i in range(roles):
        for j in range(roles):
            if observed[i][j] != graded[i][j]:
                stats["linear_mismatches"] += 1
    dimension = image_dimension(graded, rank)
    if dimension > length:
        stats["over_length"] += 1
    stats["max_image"] = max(stats["max_image"], dimension)
    count = diagonal_count(product)
    if count is not None:
        stats["diagonal_products"] += 1
        stats["max_diagonal"] = max(stats["max_diagonal"], count)
        if count > length:
            stats["over_length"] += 1
    if any(higher_term(product[i][j], rank) for i in range(roles) for j in range(roles)):
        stats["higher_products"] += 1


def census(rank, roles, length):
    found = factors(rank, roles)
    stats = {
        "linear_mismatches": 0,
        "diagonal_products": 0,
        "higher_products": 0,
        "max_diagonal": 0,
        "max_image": 0,
        "over_length": 0,
    }
    identity = eye(roles)
    blank = zeros(roles)
    if length == 1:
        for step, column, row, slope in found:
            product = apply(identity, step, column, row, bit_mul)
            graded = add_update(blank, slope, column, row)
            record_product(product, graded, rank, length, stats)
    else:
        need(length == 2, "census length")
        for step, column, row, slope in found:
            first = apply(identity, step, column, row, bit_mul)
            graded = add_update(blank, slope, column, row)
            for step2, column2, row2, slope2 in found:
                product = apply(first, step2, column2, row2, bit_mul)
                total = add_update(graded, slope2, column2, row2)
                record_product(product, total, rank, length, stats)
    need(stats["linear_mismatches"] == 0 and stats["over_length"] == 0, "census failed")
    need(stats["max_diagonal"] <= length and stats["max_image"] <= length, "short diagonal")
    return {
        "rank": rank,
        "roles": roles,
        "length": length,
        "factors": len(found),
        "products": len(found) if length == 1 else len(found) ** 2,
        "diagonal_products": stats["diagonal_products"],
        "higher_term_products": stats["higher_products"],
        "max_diagonal_nonidentity": stats["max_diagonal"],
        "max_image_dimension": stats["max_image"],
        "linear_mismatches": stats["linear_mismatches"],
    }


def direct_checks():
    words = []
    samples = [
        (2, [1, 2, 3, 0]),
        (3, [1, 2, 4, 3, 0, 7]),
        (4, [1, 2, 4, 8, 3]),
    ]
    for rank, labels in samples:
        roles = len(labels)
        primary = direct(labels, bit_mul)
        secondary = direct(labels, lambda a, b: bits_of(set_mul(set_of(a), set_of(b))))
        agree(primary, secondary)
        count = diagonal_count(primary)
        expected = sum(1 for label in labels if label)
        need(count == expected, "direct word missed the target")
        graded = linear_matrix(primary, rank)
        dimension = image_dimension(graded, rank)
        need(dimension == expected, "graded image dimension")
        need(image_dimension(graded, rank) <= expected, "graded column bound")
        shortened = labels[:-1] + [0]
        if labels[-1] == 0:
            shortened = labels[:]
            shortened[0] = 0
        omitted = direct(shortened, bit_mul)
        need(diagonal_count(omitted) != expected or omitted != primary, "omission still hit")
        need(omitted != primary, "omission did not change the word")
        words.append({
            "rank": rank,
            "labels": labels,
            "nonidentity": expected,
            "image_dimension": dimension,
            "omission_changed": True,
        })
    # Same coordinate, two distinct labels: cross term is nonzero and t stays below 2.
    crossed = apply(apply(eye(1), delta(1), 1, 1, bit_mul), delta(2), 1, 1, bit_mul)
    need(crossed[0][0] == delta(3) ^ 1, "cross term witness")
    need(higher_term(crossed[0][0] ^ 1, 2), "cross term should land in m^2")
    need(diagonal_count(crossed) == 1, "cross term created an extra diagonal")
    return {"words": words, "cross_term_diagonal": 1, "cross_term_has_m2": True}


def engines():
    failures = 0
    for rank, width in ((2, 16), (3, 256)):
        for left in range(width):
            for right in range(width):
                if bits_of(set_mul(set_of(left), set_of(right))) != bit_mul(left, right):
                    failures += 1
    need(failures == 0, "multiplication engines disagree")
    return {"k2_pairs": 256, "k3_pairs": 65536, "disagreements": failures}


def labels_through_rank_6():
    checked = 0
    for rank in range(1, 7):
        for subset in range(1, 1 << rank):
            need(linear_part(delta(subset), rank) != 0, "label vanished")
            checked += 1
    need(checked == 120, "label count")
    return checked


def run():
    pins()
    chain_ring_rejected()
    witness = socle_witness()
    multiplication = engines()
    label_count = labels_through_rank_6()
    one = census(2, 4, 1)
    two_klein = census(2, 4, 2)
    two_rank3 = census(3, 3, 2)
    constructed = direct_checks()
    need(one["max_diagonal_nonidentity"] == 1, "one call set two diagonals")
    need(two_klein["max_diagonal_nonidentity"] == 2, "two calls exceeded t=2")
    need(two_rank3["max_diagonal_nonidentity"] == 2, "rank-3 two calls exceeded t=2")
    need(two_klein["higher_term_products"] > 0, "no m^2 cross term observed")
    return {
        "status": "PASS_ELEMENTARY_ABELIAN_DIAGONAL_MINIMUM",
        "kappa_changed": False,
        "minimum": "t",
        "rank_at_least": 2,
        "labels_checked": label_count,
        "engines": multiplication,
        "socle_control": witness,
        "one_factor": one,
        "two_factor_k2_n4": two_klein,
        "two_factor_k3_n3": two_rank3,
        "direct": constructed,
        "scope": "Finite checks of the graded bound. The uniform minimum is the written proof.",
    }


if __name__ == "__main__":
    result = run()
    receipt = HERE / "RESULT.json"
    if sys.argv[1:] == ["--write-receipt"]:
        need(not receipt.exists(), "will not overwrite receipt")
        receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        need(not sys.argv[1:], "unknown arguments")
        need(result == load_json(receipt.read_text(encoding="utf-8")), "receipt mismatch")
    print(result["status"])
