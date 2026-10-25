#!/usr/bin/env python3
"""Independent count for one 7-dimensional subspace and the Gaussian number."""


def dot(left, right):
    return (left & right).bit_count() & 1


def main():
    assert (512 - 1) * (512 - 2) // 6 == 43435
    orthogonal = [point for point in range(512) if dot(point, 1) == 0 and dot(point, 2) == 0]
    assert len(orthogonal) == 128
    span = {0}
    basis = []
    for point in orthogonal:
        if point not in span:
            span = span | {item ^ point for item in span}
            basis.append(point)
    assert len(basis) == 7
    annihilator = [
        normal for normal in range(512)
        if all(dot(normal, vector) == 0 for vector in basis)
    ]
    assert annihilator == [0, 1, 2, 3]
    print("PASS_RANK7_HYPERPLANE_COUNT_TEST")


if __name__ == "__main__":
    main()
