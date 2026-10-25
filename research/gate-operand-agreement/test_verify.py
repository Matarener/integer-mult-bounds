#!/usr/bin/env python3
"""Witnesses for the gate-operand contract."""


def predicted(destination, sources):
    multiplicity = sources.count(destination)
    if multiplicity == 0:
        return True
    last = len(sources) - 1 - sources[::-1].index(destination)
    if multiplicity % 2 == 0:
        return False
    earlier = {}
    for source in sources[:last]:
        earlier[source] = earlier.get(source, 0) + 1
    return all(count % 2 == 0 for count in earlier.values())


def main():
    assert predicted(0, []) and predicted(0, [0]) and predicted(0, [1, 1])
    assert predicted(0, [0, 0, 0]) and not predicted(0, [1, 0])
    assert 6 * (5 + 20 + 60 + 120) == 1230
    print("PASS_GATE_OPERAND_AGREEMENT_TEST")


if __name__ == "__main__":
    main()
