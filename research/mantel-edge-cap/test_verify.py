#!/usr/bin/env python3
"""Independent Mantel check through five vertices."""


def edge_bit(order, left, right):
    return left * (2 * order - left - 1) // 2 + (right - left - 1)


def main():
    for order in range(1, 6):
        cap = (order * order) // 4
        assert (order // 2) * ((order + 1) // 2) == cap
        triples = []
        for first in range(order):
            for second in range(first + 1, order):
                for third in range(second + 1, order):
                    triples.append((
                        edge_bit(order, first, second),
                        edge_bit(order, first, third),
                        edge_bit(order, second, third),
                    ))
        edge_count = order * (order - 1) // 2
        for mask in range(1 << edge_count):
            if mask.bit_count() <= cap:
                continue
            assert any(
                (mask >> first) & 1 and (mask >> second) & 1 and (mask >> third) & 1
                for first, second, third in triples
            )
    print("PASS_MANTEL_EDGE_CAP_TEST")


if __name__ == "__main__":
    main()
