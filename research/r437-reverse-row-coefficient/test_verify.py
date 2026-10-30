#!/usr/bin/env python3
"""Failure controls for the reverse-row coefficient."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


def synthetic(records, reverse):
    """Cancellation-free stack on two registers. No copy buffer."""
    norm = [1, 1]
    high = 1
    order = list(reversed(records)) if reverse else records
    for destination, source in order:
        norm[destination] += norm[source]
        high = max(high, norm[destination])
    return high


def main():
    adds = [(0, 1), (0, 1), (1, 0)]
    if synthetic(adds, False) != 4 or synthetic(adds, True) != 5:
        raise SystemExit("FAIL synthetic orientation")
    old, new = verify.load_words()
    gap = verify.report(old, new)["delta"]
    if gap != 9652:
        raise SystemExit("FAIL published gap")
    unchanged = verify.coefficient(old)["reverse"]["l1"]
    if unchanged != 1113998:
        raise SystemExit("FAIL old control")
    try:
        verify.report(old, old)
        raise SystemExit("FAIL unchanged word looked like the candidate")
    except verify.Reject:
        pass
    records = verify.operation_records(new, verify.frame_dimensions(new))
    duplicated = list(records)
    for index, record in enumerate(duplicated):
        if record[:3] == ("add", 158, 223):
            duplicated.insert(index, record)
            break
    else:
        raise SystemExit("FAIL peak add missing")
    moved = verify.walk(duplicated, True)["l1"]
    if moved == 1123650:
        raise SystemExit("FAIL duplicated peak add was invisible")
    try:
        verify.need(False, "control")
        raise SystemExit("FAIL need did not reject")
    except verify.Reject:
        pass
    print("PASS_R437_REVERSE_ROW_COEFFICIENT_CONTROLS " + json.dumps(
        {"groups": 4, "mutated_reverse": moved}, sort_keys=True))


if __name__ == "__main__":
    main()
