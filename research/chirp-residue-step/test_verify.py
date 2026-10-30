#!/usr/bin/env python3
"""Independent residue arithmetic for one chirp axis."""


def main():
    for index in range(128):
        assert (index + 1) ** 2 - index ** 2 == 2 * index + 1
        assert 2 * (index + 1) + 1 == (2 * index + 1) + 2
    radius = 8
    length = radius
    modulus = 2 * radius
    slope = 1
    factor = (-slope * (radius // length)) % modulus
    index = 0
    value = 0
    difference = factor
    total = 0
    for _ in range(length):
        assert value == (factor * index * index) % modulus
        assert total == value
        if index + 1 < length:
            total = (total + difference) % modulus
            value = (value + difference) % modulus
            difference = (difference + 2 * factor) % modulus
            index += 1
        else:
            total = (total - value) % modulus
            index = 0
            value = 0
    assert total == 0 and index == 0 and value == 0
    size = 8
    tail = 1
    visits = 0
    for length in (2, 2, 2):
        visits += size // tail
        tail *= length
    assert visits == 14
    assert visits < 2 * size
    print("PASS_CHIRP_RESIDUE_STEP_TEST")


if __name__ == "__main__":
    main()
