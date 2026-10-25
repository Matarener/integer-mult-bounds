#!/usr/bin/env python3
"""Reconcile one P104 row/column fiber-tag pair.

The 104 labels are the physical_labels array in PR #3966's retained
RESULT.json (SHA-256 ce05a27ebc98677bec4febaa488fa03f5b6fc60216aa43b34298444d12f7ab6c),
itself the PR #3954 export at f1e2839819959cd0534d008be91ed5b79ec55a6a.
That file is not a Git object on this base, so labels.json is the vendored
array and this checker authenticates its bytes.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LABEL_SHA256 = "7227a7d6bdb49f36b6e401478034cc542eb887979890c8deda924b8ac0844209"
Z = 420
J = 511
ROW_LABEL = 386
COLUMN_LABEL = 405


def fail(message):
    raise SystemExit("FAIL_P104_FIBER_TAG_SEAM " + message)


def require(condition, message):
    if not condition:
        fail(message)


def dot(left, right):
    return (left & right).bit_count() & 1


def weight_mod4(value):
    return value.bit_count() % 4


def apply_o(value):
    if dot(value, Z):
        return value ^ Z
    return value


def tensor(left, right):
    """Bit 9*alpha+beta of left⊗right is left_alpha * right_beta."""
    out = 0
    for alpha in range(9):
        if (left >> alpha) & 1:
            out |= right << (9 * alpha)
    return out


def load_labels():
    raw = (ROOT / "labels.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == LABEL_SHA256, "label bytes drifted")
    labels = json.loads(raw.decode("utf-8"))
    require(isinstance(labels, list) and len(labels) == 104, "expected 104 labels")
    require(all(isinstance(item, int) and 0 <= item < 512 for item in labels), "label out of F2^9")
    require(len(set(labels)) == 104, "labels are not distinct")
    return labels


def check_gauge():
    """O is an orthogonal involution on every vector, with the weight law."""
    for left in range(512):
        image = apply_o(left)
        require(apply_o(image) == left, "O is not an involution")
        require(weight_mod4(image) == (weight_mod4(left) + 2 * dot(left, Z)) % 4,
                "weight law failed")
        for right in range(left, 512):
            require(dot(apply_o(left), apply_o(right)) == dot(left, right), "O is not orthogonal")
    require(dot(Z, Z) == 0 and Z.bit_count() == 4, "z is not the stated even weight-4 vector")
    require(apply_o(Z) == Z and apply_o(J) == J, "O does not fix z and the all-ones vector")


def tags(row_image, column_image):
    return tensor(Z, column_image), tensor(row_image, Z)


def shared_flips(row_image, column_image):
    row_tag, column_tag = tags(row_image, column_image)
    shared = tensor(row_image, column_image)
    return dot(row_tag, shared), dot(column_tag, shared), row_tag, column_tag, shared


def check_labels(labels):
    images = []
    class_counts = {1: 0, 3: 0}
    for label in labels:
        require(weight_mod4(label) in (1, 3), "label is not an odd published class")
        image = apply_o(label)
        require(weight_mod4(image) == 3, "image is not weight 3 mod 4")
        require(dot(Z, image) == dot(Z, label), "O is not self-adjoint on z")
        require((dot(Z, label) == 1) == (weight_mod4(label) == 1), "class does not match z·p")
        class_counts[weight_mod4(label)] += 1
        images.append(image)
    require(class_counts == {1: 56, 3: 48}, "class split is not 56/48")
    require(Z not in images, "some image equals z")
    return images


def marginals(value):
    """Return (row-sum, column-sum) in F2^9 for an 81-bit tensor."""
    row_sum = 0
    column_sum = 0
    for alpha in range(9):
        stripe = (value >> (9 * alpha)) & 511
        column_sum ^= stripe
        if stripe.bit_count() & 1:
            row_sum |= 1 << alpha
    return row_sum, column_sum


def check_marginals(images):
    uniform = tensor(Z, J) ^ tensor(J, Z)
    require(marginals(uniform) == (Z, Z), "uniform tag marginals are not both z")
    for image in images:
        row_tag, column_tag = tags(image, image)
        # tags(row_image, column_image) = (z⊗column_image, row_image⊗z).
        # Using the same odd image for both factors checks each shape.
        require(marginals(tensor(Z, image)) == (Z, 0), "row-tag marginals failed")
        require(marginals(tensor(image, Z)) == (0, Z), "column-tag marginals failed")
        require(row_tag != uniform and column_tag != uniform, "marginal witness collided with a")


def check_pairs(labels, images):
    full_equal = 0
    mixed_disagree = 0
    same_agree = 0
    min_hamming = 81
    min_pairs = []
    uniform = tensor(Z, J) ^ tensor(J, Z)
    require(uniform.bit_count() == 40, "uniform completion tag does not have weight 40")
    helper_row_matches = 0
    for row_index, row_image in enumerate(images):
        for column_index, column_image in enumerate(images):
            row_flip, column_flip, row_tag, column_tag, shared = shared_flips(row_image, column_image)
            require(dot(shared, shared) == 1, "shared line is degenerate")
            require(row_flip == dot(Z, labels[row_index]), "row shared flip is not z·p_row")
            require(column_flip == dot(Z, labels[column_index]), "column shared flip is not z·p_column")
            same_class = weight_mod4(labels[row_index]) == weight_mod4(labels[column_index])
            require((row_flip == column_flip) == same_class, "shared-bit rule failed")
            if same_class:
                same_agree += 1
            else:
                mixed_disagree += 1
            if row_tag == column_tag:
                full_equal += 1
            hamming = (row_tag ^ column_tag).bit_count()
            if hamming < min_hamming:
                min_hamming = hamming
                min_pairs = [(row_index, column_index)]
            elif hamming == min_hamming:
                min_pairs.append((row_index, column_index))
            require(row_tag != uniform and column_tag != uniform, "a fiber tag equals the uniform tag")
            uniform_flip = dot(uniform, shared)
            # The uniform tag matches the row tag on the shared line exactly
            # when the column label is class 3.
            require((row_flip == uniform_flip) == (dot(Z, labels[column_index]) == 0),
                    "helper/row shared-bit comparison is inconsistent")
            if row_flip == uniform_flip:
                helper_row_matches += 1
    require(full_equal == 0, "some full-address tags agree")
    require(mixed_disagree == 5376 and same_agree == 5440, "pair census changed")
    require(min_hamming == 6, "minimum Hamming distance is not 6")
    require(sorted(min_pairs) == [(19, 19), (19, 75), (75, 19), (75, 75)],
            "minimum pairs are not labels 32 and 4")
    require(helper_row_matches == 104 * 48, "helper match count is not the class-3 columns")
    return min_hamming


def check_witness(labels, images):
    row_index = labels.index(ROW_LABEL)
    column_index = labels.index(COLUMN_LABEL)
    require((row_index, column_index) == (0, 8), "published witness labels moved")
    require(weight_mod4(labels[row_index]) == 3 and weight_mod4(labels[column_index]) == 1,
            "witness classes changed")
    row_flip, column_flip, row_tag, column_tag, shared = shared_flips(
        images[row_index], images[column_index])
    require((images[row_index], images[column_index]) == (386, 49), "witness images changed")
    require((row_flip, column_flip) == (0, 1), "witness shared flips changed")
    difference = row_tag ^ column_tag
    require(difference.bit_count() == 20, "witness Hamming distance is not 20")
    require((difference >> 11) & 1 == 1, "separating bit 11 disappeared")
    frequency = 1 << 11
    require(dot(row_tag, frequency) == 0 and dot(column_tag, frequency) == 1,
            "character e_11 does not separate the witness tags")
    uniform = tensor(Z, J) ^ tensor(J, Z)
    require(dot(uniform, shared) == 1 and row_flip == 0,
            "uniform helper tag agrees with the witness row tag")


def check_controls():
    """The odd-image hypothesis is necessary, and a forced agreement is rejected."""
    require(tensor(Z, 0) == tensor(0, Z) == 0, "zero tags should agree")
    row_tag, column_tag = tags(386, 49)
    require(row_tag != column_tag, "control lost the witness mismatch")
    try:
        require(row_tag == column_tag, "forced equality")
    except SystemExit as exc:
        require(str(exc).startswith("FAIL_P104_FIBER_TAG_SEAM"), "control raised the wrong failure")
    else:
        fail("forced tag equality was accepted")


def main():
    labels = load_labels()
    check_gauge()
    images = check_labels(labels)
    check_marginals(images)
    min_hamming = check_pairs(labels, images)
    check_witness(labels, images)
    check_controls()
    print(
        "PASS_P104_FIBER_TAG_SEAM pairs=10816 full_equal=0 "
        "mixed_shared_disagree=5376 same_shared_agree=5440 "
        f"min_hamming={min_hamming} witness=386/405 shared_flips=0/1 ham=20 "
        "helper_disagrees_on_witness=true no_new_kappa"
    )


if __name__ == "__main__":
    main()
