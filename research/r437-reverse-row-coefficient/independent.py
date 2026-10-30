#!/usr/bin/env python3
"""Separate reverse-row walk. Does not import verify.py."""
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
N = 659


def load():
    old = json.loads(gzip.decompress(
        (HERE / "inputs" / "R437-COMPOSED-WORD.json.gz").read_bytes()))
    phases = json.loads(gzip.decompress(
        (HERE / "inputs" / "CANDIDATE-PHASES.json.gz").read_bytes()))
    new = {key: (phases[key] if key in phases else value) for key, value in old.items()}
    return old, new


def records(word):
    frames = [set(frame) for frame in word["frames"]]
    cursor = word["start"][:]
    out = []

    def move(register, frame):
        previous = cursor[register]
        if previous != frame:
            if not frames[previous].issubset(frames[frame]):
                raise RuntimeError("frame")
            out.append((0, register))
            cursor[register] = frame

    for name in ("D", "A", "B", "C"):
        if name == "B":
            for slot, register in enumerate(word["ret"]):
                out.append((2, register))
                for target, group in enumerate(word["scatter"]):
                    if slot in group:
                        out.append((1, 111 + target, N))
                out.append((3, register))
        for frame, destination, sources in word[name]:
            move(destination, frame)
            for source in sources:
                move(source, frame)
                out.append((1, destination, source))
    for register, frame in enumerate(word["final"]):
        move(register, frame)
    return out


def bound(records_in, reverse):
    order = range(len(records_in) - 1, -1, -1) if reverse else range(len(records_in))
    norm = {N: 0}
    high = 1
    peak = None
    adds = 0
    for index in order:
        op = records_in[index]
        code = op[0]
        if code == 1:
            destination, source = op[1], op[2]
            total = norm.get(destination, 1) + norm.get(source, 1)
            norm[destination] = total
            adds += 1
            if total > high:
                high = total
                peak = (destination, source, norm.get(source, 1), total)
        elif code == (3 if reverse else 2):
            norm[N] = norm.get(op[1], 1)
        elif code == (2 if reverse else 3):
            norm[N] = 0
    return high, adds, peak


def main():
    old, new = load()
    old_records, new_records = records(old), records(new)
    old_forward = bound(old_records, False)
    new_forward = bound(new_records, False)
    old_reverse = bound(old_records, True)
    new_reverse = bound(new_records, True)
    if (old_forward[0], new_forward[0], old_reverse[0], new_reverse[0]) != (
            49347, 49347, 1113998, 1123650):
        raise SystemExit("FAIL independent coefficients")
    if (old_forward[1], new_forward[1]) != (24208, 24211):
        raise SystemExit("FAIL independent adds")
    if new_reverse[2][:3] != (158, 223, 8689) or old_reverse[2][:3] != (158, 223, 8689):
        raise SystemExit("FAIL independent peak")
    if 1123650 - 1113998 != 9652 or (1113998).bit_length() != 21 or (1123650).bit_length() != 21:
        raise SystemExit("FAIL independent delta")
    print("PASS_R437_REVERSE_ROW_COEFFICIENT_INDEPENDENT "
          '{"delta":9652,"new_reverse":1123650,"old_reverse":1113998,"peak":[158,223,8689]}')


if __name__ == "__main__":
    main()
