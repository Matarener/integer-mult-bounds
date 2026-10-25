#!/usr/bin/env python3
"""Independent residue check at width 4."""


def main():
    modulus = 1 << 4
    assert (modulus - 1).bit_length() == 4
    pairs = 0
    for left in range(modulus):
        for right in range(modulus):
            total = left + right
            assert total < 2 * modulus
            if total >= modulus:
                total -= modulus
            assert total == (left + right) % modulus
            pairs += 1
    assert pairs == 256
    assert 5 * 4 == 20
    print("PASS_CHIRP_FIELD_WIDTH_TEST")


if __name__ == "__main__":
    main()
