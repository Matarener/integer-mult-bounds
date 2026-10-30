#!/usr/bin/env python3
"""Arithmetic checks for the centre columns."""


def main():
    columns = (
        (1, 1, 1, 1, 0, 0, 0, 0),
        (0, 1, 1, 0, 1, 0, 0, 1),
        (1, 0, 0, 1, -1, 0, 0, -1),
    )
    relation = tuple(columns[0][i] - columns[1][i] - columns[2][i] for i in range(8))
    assert relation == (0, 0, 0, 0, 0, 0, 0, 0)
    assert 112 - 8 == 104
    assert 16 * 15 * 17 == 4080
    assert 104 * 4080 == 424320
    print("PASS_CENTRE_COLUMN_RELATION_TEST")


if __name__ == "__main__":
    main()
