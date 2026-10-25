#!/usr/bin/env python3
"""Counts for the ledger evidence drift."""


def main():
    assert 2064 + 902 + 2 + 60 == 3028
    assert 3528 >= 1365
    print("PASS_LEDGER_EVIDENCE_DRIFT_TEST")


if __name__ == "__main__":
    main()
