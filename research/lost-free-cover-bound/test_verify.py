#!/usr/bin/env python3
"""Fixed block costs of the lost-free sizes."""


def main():
    def cost(size, block=72):
        return block + 2 * (112 - size)

    assert 4 * 14 == 56
    assert cost(32) == 232 and cost(37) == 222 and cost(56) == 184
    assert cost(56, 52) == 164 and cost(56, 48) == 160
    print("PASS_LOST_FREE_COVER_TEST")


if __name__ == "__main__":
    main()
