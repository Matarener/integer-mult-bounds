#!/usr/bin/env python3
"""Independent sign cancellation at two small rings."""


def main():
    ring = 8
    for left in range(ring):
        for right in range(ring):
            exponent = left + right
            degree = left + right
            sign = 1
            if exponent >= ring:
                exponent -= ring
                sign = -sign
            if degree >= ring:
                degree -= ring
                sign = -sign
            assert sign == 1 and exponent == degree
    ring = 4
    limit = 1 << ring
    for left_mask in range(limit):
        left = [(left_mask >> index) & 1 for index in range(ring)]
        for right_mask in range(limit):
            right = [(right_mask >> index) & 1 for index in range(ring)]
            cyclic = [0] * ring
            signed = [0] * ring
            for left_index, left_digit in enumerate(left):
                for right_index, right_digit in enumerate(right):
                    term = left_digit * right_digit
                    cyclic[(left_index + right_index) % ring] += term
                    index = left_index + right_index
                    if index >= ring:
                        index -= ring
                    signed[index] += term
            assert signed == cyclic
    print("PASS_NEGACYCLIC_SIGN_CANCELLATION_TEST")


if __name__ == "__main__":
    main()
