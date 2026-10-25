#!/usr/bin/env python3
"""Independent annihilator of frame A."""


def dot(left, right):
    return (left & right).bit_count() & 1


def main():
    generators = (256, 128, 64, 38, 20, 10, 1)
    reached = {0}
    for vector in generators:
        reached |= {item ^ vector for item in reached}
    assert len(reached) == 128
    annihilator = [
        normal for normal in range(512)
        if all(dot(normal, point) == 0 for point in reached)
    ]
    assert annihilator == [0, 30, 42, 52]
    assert 30 ^ 42 == 52
    print("PASS_RANK7_FRAME_LINES_TEST")


if __name__ == "__main__":
    main()
