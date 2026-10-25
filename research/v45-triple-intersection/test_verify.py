#!/usr/bin/env python3
"""Independent check of the V45 generators."""


def dot(left, right):
    return (left & right).bit_count() & 1


def main():
    generators = (256, 128, 64, 35, 16, 11, 5)
    assert 7 ^ 42 == 45
    reached = {0}
    for vector in generators:
        assert dot(vector, 7) == dot(vector, 42) == dot(vector, 45) == 0
        reached |= {item ^ vector for item in reached}
    intersection = {
        point for point in range(512)
        if dot(point, 7) == 0 and dot(point, 42) == 0
    }
    assert reached == intersection and len(reached) == 128
    print("PASS_V45_TRIPLE_INTERSECTION_TEST")


if __name__ == "__main__":
    main()
