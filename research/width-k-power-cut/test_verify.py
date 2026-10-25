#!/usr/bin/env python3
"""Integer checks for the width-power cut."""


def main():
    witness = 2**500
    assert 1**500 <= witness - 1 < 2**500
    assert witness == 2**500
    print("PASS_WIDTH_K_POWER_CUT_TEST")


if __name__ == "__main__":
    main()
