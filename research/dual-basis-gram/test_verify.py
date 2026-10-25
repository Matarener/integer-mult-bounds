#!/usr/bin/env python3
"""Independent Gram arithmetic for the stated dual basis."""


def basis(index):
    vector = [0] * 8
    vector[index] = 1
    return vector


def main():
    unit = [basis(index) for index in range(8)]
    primal = [
        [1, 1, 0, 0, 0, 0, 0, 0],
        unit[1],
        [1, 0, -1, 0, 0, 0, 0, 0],
        *unit[3:],
    ]
    dual = [
        [1, 0, 1, 0, 0, 0, 0, 0],
        [-1, 1, -1, 0, 0, 0, 0, 0],
        [0, 0, -1, 0, 0, 0, 0, 0],
        *unit[3:],
    ]
    for row, left in enumerate(primal):
        for column, right in enumerate(dual):
            product = sum(item * other for item, other in zip(left, right))
            assert product == (1 if row == column else 0)
    assert sum((1, 7, 9, 9, 9, 9, 9, 9, 9, 1)) == 72
    print("PASS_DUAL_BASIS_GRAM_TEST")


if __name__ == "__main__":
    main()
