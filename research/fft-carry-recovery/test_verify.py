#!/usr/bin/env python3
"""Independent carry recovery for one FFT width."""


def main():
    width = 5
    beta = 3
    base = 8
    digit_count = 2
    ring = 4
    room = base - 1
    assert digit_count * room * room + digit_count * room == digit_count * room * base
    cap = digit_count * room
    limit = 1 << width
    for left in range(limit):
        for right in range(limit):
            left_digits = [(left >> (beta * index)) & (base - 1) for index in range(digit_count)]
            right_digits = [(right >> (beta * index)) & (base - 1) for index in range(digit_count)]
            coefficients = [0] * (2 * digit_count - 1)
            for left_index, left_digit in enumerate(left_digits):
                for right_index, right_digit in enumerate(right_digits):
                    coefficients[left_index + right_index] += left_digit * right_digit
            carry = 0
            total = 0
            place = 1
            for index in range(ring):
                coefficient = coefficients[index] if index < len(coefficients) else 0
                mixed = coefficient + carry
                digit = mixed % base
                carry = mixed // base
                assert carry <= cap
                total += digit * place
                place *= base
            assert carry == 0
            assert total == left * right
    print("PASS_FFT_CARRY_RECOVERY_TEST")


if __name__ == "__main__":
    main()
