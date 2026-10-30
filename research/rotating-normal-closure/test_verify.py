#!/usr/bin/env python3
"""Arithmetic of the rotating-normal deficit."""


def main():
    path = [1, 8, 15, 22, 29, 36]
    assert path[0] - 0 == 1
    assert all(right - left == 7 for left, right in zip(path, path[1:]))
    assert path[-1] + 7 == 43
    assert 6 * (1 + 6 + 7) == 84
    assert 84 + 2 == 86 == 43 * 2
    print("PASS_ROTATING_NORMAL_CLOSURE_TEST")


if __name__ == "__main__":
    main()
