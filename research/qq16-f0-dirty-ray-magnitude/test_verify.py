#!/usr/bin/env python3
"""Failure controls for the F0 dirty-ray magnitude ledger."""
import importlib.util
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("dirty_ray", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def synthetic():
    word = [["phase", 0] for _ in range(verify.WIDTH)]
    word[0] = ["scalar", ["add", ["L", 1], ["L", 2], 3, 1], 4]
    word[1] = ["scalar", ["add", ["L", 400], ["L", 2], -5, 2], 4]
    # Keep the published fault index inside the word without using it.
    while len(word) <= verify.FAULT:
        word.append(["phase", 0])
    word[verify.FAULT] = ["scalar", ["add", ["L", 39], ["L", 359], 4, 1], 1]
    return word


def main():
    word = synthetic()
    summary = verify.project(word, 2, sparse=False)
    other = verify.project(word, 2, sparse=True)
    if summary["peaks"] != other["peaks"]:
        raise SystemExit("synthetic representations disagree")
    if summary["peaks"]["data"] != 3 or summary["peaks"]["helper"] != Q(5, 2):
        raise SystemExit("synthetic peak moved")
    if summary["peaks"]["data"] == 128:
        raise SystemExit("synthetic word reused the F0 constant")
    packet, _receipt = verify.load(verify.ROOT)
    literal = verify.expand(packet)
    tampered = [event[:] for event in literal]
    gate = tampered[24280][1][:]
    gate[3] = 63
    tampered[24280] = ["scalar", gate, 1]
    moved = verify.project(tampered, verify.DIRTY, sparse=True)
    if moved["peaks"]["data"] == 128:
        raise SystemExit("coefficient 63 still reported the published peak")
    result = verify.audit(verify.ROOT)
    if result["dirty_peaks"] != {"data": "128", "helper": "68", "private": "0"}:
        raise SystemExit("published ledger moved")
    if result["data_ray_peaks"]["data"] != "1":
        raise SystemExit("data-ray control moved")
    print("PASS_QQ16_F0_DIRTY_RAY_MAGNITUDE_TESTS groups=3")


if __name__ == "__main__":
    main()
