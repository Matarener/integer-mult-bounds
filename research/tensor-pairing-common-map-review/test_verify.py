#!/usr/bin/env python3
"""Failure controls for the common-map review. Both scanners are imported."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rejects(operation, text):
    try:
        operation()
    except ValueError as error:
        need(text in str(error), "unexpected failure: " + str(error))
    else:
        raise ValueError("control was accepted")


def main():
    primary = load("verify")
    second = load("independent")
    primary.audit()
    gram, pairing = second.pairing_from_formula()
    second.square_identity(pairing)
    matrix = second.witness_and_scalar(gram, pairing)
    need(matrix[0][2] == 0 and gram[0][1] == 8, "scanners disagree on the mismatch")
    second.nine_labels(pairing)

    def bad_square():
        broken = [row[:] for row in pairing]
        broken[0][15] ^= 1
        broken[15][0] ^= 1
        second.square_identity(broken)

    rejects(bad_square, "square")

    def bad_cross():
        changed = [row[:] for row in matrix]
        changed[0][2] = 1
        changed[2][0] = 1
        for i in range(8):
            for j in range(8):
                if i // 2 != j // 2:
                    need(changed[i][j] == 0, "cross")

    rejects(bad_cross, "cross")

    def bad_label():
        labels = list(second.LABELS)
        labels[0] ^= 1
        for i, left in enumerate(second.NINE_INDEX):
            for j, right in enumerate(second.NINE_INDEX):
                bit = (labels[i] & labels[j]).bit_count() & 1
                need(bit == pairing[left][right], "label")

    rejects(bad_label, "label")
    print("PASS_TENSOR_PAIRING_COMMON_MAP_REVIEW_TESTS controls=3")


if __name__ == "__main__":
    main()
