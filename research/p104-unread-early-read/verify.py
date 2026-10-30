#!/usr/bin/env python3
"""Independent check of the PR #5827 early source observation.

The vendored words are PR #5811 at the bytes pinned by PR #5827 head
05cd36e5af06d7a3790e30ce3f449fa89b853768 and the published replacement word
from that same head. This verifier does not import that package.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
START = 13815
A, C, B = 3, 597, 1031
# Proof names: a=695, b=733, c=773, d=709.
A_ROLE, B_ROLE, C_ROLE, D_ROLE = 695, 733, 773, 709
ROLES = (A_ROLE, D_ROLE, B_ROLE, C_ROLE)
OLD = (
    ["MOVE", 773, 1031, 597, True],
    ["ADD", 709, 773, "1", 597],
    ["MOVE", 733, 3, 597, False],
    ["ADD", 733, 773, "1", 597],
    ["MOVE", 695, 3, 597, False],
    ["ADD", 695, 733, "1", 597],
    ["MOVE", 695, 597, 1031, False],
)
NEW = (
    ["ADD", 695, 733, "1", 3],
    ["MOVE", 695, 3, 1031, False],
    ["ADD", 695, 773, "1", 1031],
    ["MOVE", 773, 1031, 597, True],
    ["ADD", 709, 773, "1", 597],
    ["MOVE", 733, 3, 597, False],
    ["ADD", 733, 773, "1", 597],
)
SOURCE_GZ_SHA256 = "690656bfca9c6f0366527d158ca4edb14f83c410604d647953c20c7c94bea2e8"
NEW_GZ_SHA256 = "5d50e5654910c9535e9025de0f644bb2dece2396e799b4a766110363448fd0b0"
SOURCE_CANON_SHA256 = "a06445539ad73fe16deae66fef8c52ffc39f5f14c765eab3dc3d98e0e2d8074c"
NEW_CANON_SHA256 = "d1e5ee3b9811ce7be0ad80aecf19b41cd9277e838b3a9fe52d25baa610d58782"
PASS = "PASS_P104_UNREAD_EARLY_READ"


class Rejected(Exception):
    """An expected illegal schedule or a failed local predicate."""


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL_P104_UNREAD_EARLY_READ " + message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def span(basis):
    out = {0}
    for vector in basis:
        if type(vector) is not int or not 0 < vector < 512 or vector in out:
            raise Rejected("frame basis is not independent in F_2^9")
        out |= {point ^ vector for point in tuple(out)}
    return frozenset(out)


def load_word(name, gz_sha, canon_sha):
    raw = (HERE / "inputs" / name).read_bytes()
    require(sha256(raw) == gz_sha, "gzip pin mismatch for " + name)
    word = json.loads(gzip.decompress(raw))
    require(canonical(word) == canon_sha, "canonical word pin mismatch for " + name)
    require(word["public"] == 770, "public width")
    require(word["owned_fields"] == 29, "owned width")
    require(len(word["program"]) == 25984, "event count")
    require(len(word["initial"]) == len(word["final"]) == 770, "public boundary width")
    return word


def hits(program, block):
    width = len(block)
    return [index for index in range(len(program) - width + 1)
            if program[index:index + width] == list(block)]


def entry_frames(word, charts):
    current = list(word["initial"]) + [None] * word["owned_fields"]
    for index, event in enumerate(word["program"]):
        if index == START:
            return {role: current[role] for role in ROLES}
        op, role = event[0], event[1]
        if op == "MOVE":
            _, role, source, dest, private = event
            if current[role] != source:
                raise Rejected("transport does not start at the occupied frame")
            nested = charts[dest] < charts[source] if private else charts[source] < charts[dest]
            if not nested:
                raise Rejected("transport is not a strict frame nesting")
            current[role] = dest
        elif op == "INIT":
            current[role] = event[2]
        elif op == "CLEAR":
            if current[role] != event[2]:
                raise Rejected("clear does not name the occupied frame")
            current[role] = None
        elif op not in ("ADD", "SCALE", "COPY"):
            raise Rejected("unknown opcode before the cut")
    raise Rejected("cut index is past the program")


def simulate(events, frames, charts, occupied):
    current = dict(occupied)
    image = {role: {role: Fraction(1)} for role in ROLES}
    ranks = []

    def absorb(destination, source, coefficient):
        row = image[destination]
        for key, value in image[source].items():
            total = row.get(key, 0) + coefficient * value
            if total:
                row[key] = total
            else:
                row.pop(key, None)

    for event in events:
        op = event[0]
        if op == "MOVE":
            _, role, source, dest, private = event
            if current[role] != source:
                raise Rejected("move leaves a frame the role does not occupy")
            nested = charts[dest] < charts[source] if private else charts[source] < charts[dest]
            if not nested:
                raise Rejected("move is not a strict frame nesting")
            ranks.append(abs(len(frames[source]) - len(frames[dest])))
            current[role] = dest
        elif op == "ADD":
            _, role, source, coefficient, frame = event
            if current[role] != frame or current[source] != frame:
                raise Rejected("ADD operands are not together in the named frame")
            absorb(role, source, Fraction(coefficient))
        else:
            raise Rejected("interval opcode is not ADD or MOVE")
    return current, image, ranks


def expect_rejected(action, label):
    try:
        action()
    except Rejected:
        return
    raise SystemExit("FAIL_P104_UNREAD_EARLY_READ control accepted " + label)


def unit_add_charge():
    numerator, denominator = 1, 1
    return 2 * (3 + numerator.bit_length() - 1 + numerator.bit_count()
                + denominator.bit_length() - 1)


def strict_drop_hypotheses():
    """Hypotheses of the written proof that 1^t + 4^t > 5^t for 0<t<1.

    For v in (0,1) and t in (0,1), v^t > v because t-1<0. The weights 1/5
    and 4/5 lie in (0,1) and sum to 1, so each strict comparison adds.
    Equality holds at t=1. At t=2 the inequality reverses.
    """
    one, four = Fraction(1, 5), Fraction(4, 5)
    require(0 < one < 1 and 0 < four < 1, "weights leave the open unit interval")
    require(one + four == 1, "weights do not recover the rank-5 base")
    require(5 < (1 + 2) ** 2, "square-root spot check 5^(1/2) < 1 + 2")
    require(1 + 4 == 5, "the paid-power gap must vanish at exponent 1")
    require(1 + 16 < 25, "the paid-power gap must reverse at exponent 2")


def main():
    source = load_word("pr5811-WORD.json.gz", SOURCE_GZ_SHA256, SOURCE_CANON_SHA256)
    edited = load_word("pr5827-WORD.json.gz", NEW_GZ_SHA256, NEW_CANON_SHA256)
    for key in ("final", "frames", "initial", "live", "owned_fields", "ports", "public", "schema"):
        require(source[key] == edited[key], "boundary field changed: " + key)
    require(hits(source["program"], OLD) == [START], "source interval is not the unique cut")
    require(edited["program"][START:START + 7] == list(NEW), "replacement block mismatch")
    require(
        [index for index, (left, right) in enumerate(zip(source["program"], edited["program"]))
         if left != right] == list(range(START, START + 7)),
        "words differ outside the seven-event interval",
    )
    frames = source["frames"]
    charts = [span(basis) for basis in frames]
    require(len(frames[A]) == 0 and len(charts[A]) == 1, "frame 3 is not dimension 0")
    require(len(frames[C]) == 1 and len(charts[C]) == 2, "frame 597 is not dimension 1")
    require(len(frames[B]) == 5 and len(charts[B]) == 32, "frame 1031 is not dimension 5")
    require(charts[A] < charts[C] < charts[B], "frames 3, 597, 1031 are not strictly nested")
    require(not (len(frames[A]) == 0 and len(frames[C]) == 4 and len(frames[B]) == 5),
            "the published dimensions 0, 4, 5 were accepted")
    rank_ac = abs(len(frames[A]) - len(frames[C]))
    rank_cb = abs(len(frames[C]) - len(frames[B]))
    rank_ab = abs(len(frames[A]) - len(frames[B]))
    require((rank_ac, rank_cb, rank_ab) == (1, 4, 5), "role-695 leg ranks are not 1, 4, 5")
    require((rank_ac, rank_cb) != (4, 1), "swapped prose ranks were accepted")

    try:
        occupied = entry_frames(source, charts)
    except Rejected as exc:
        raise SystemExit("FAIL_P104_UNREAD_EARLY_READ " + str(exc)) from exc
    require(occupied == {A_ROLE: A, B_ROLE: A, C_ROLE: B, D_ROLE: C},
            "entry frames are not a in 3, b in 3, c in 1031, d in 597")
    try:
        old_exit, old_image, old_ranks = simulate(OLD, frames, charts, occupied)
        new_exit, new_image, new_ranks = simulate(NEW, frames, charts, occupied)
    except Rejected as exc:
        raise SystemExit("FAIL_P104_UNREAD_EARLY_READ " + str(exc)) from exc
    expected = {
        A_ROLE: {A_ROLE: Fraction(1), B_ROLE: Fraction(1), C_ROLE: Fraction(1)},
        B_ROLE: {B_ROLE: Fraction(1), C_ROLE: Fraction(1)},
        C_ROLE: {C_ROLE: Fraction(1)},
        D_ROLE: {D_ROLE: Fraction(1), C_ROLE: Fraction(1)},
    }
    require(old_exit == new_exit == {A_ROLE: B, B_ROLE: C, C_ROLE: C, D_ROLE: C},
            "exit frames differ")
    require(old_image == new_image == expected, "four-field images differ")
    require(NEW[0] == ["ADD", A_ROLE, B_ROLE, "1", A], "first new event is not the early read of b")
    require(all(event[1] != B_ROLE or event[0] != "ADD" for event in NEW[:-1]),
            "b is written before the early read")
    require(Counter(new_ranks) - Counter(old_ranks) == Counter({5: 1}),
            "the only added transport rank is not 5")
    delta = Counter(new_ranks)
    delta.subtract(Counter(old_ranks))
    require(dict(delta) == {1: -1, 4: -1, 5: 1}, "paid rank multiset is not -H1-H4+H5")
    require(sum(1 for event in NEW if event[0] == "ADD")
            == sum(1 for event in OLD if event[0] == "ADD") + 1,
            "the schedules do not differ by one ADD")
    require(unit_add_charge() == 8, "one coefficient-+1 ADD is not charged at 8")
    strict_drop_hypotheses()

    omitted = list(NEW[1:])
    _, omitted_image, _ = simulate(omitted, frames, charts, occupied)
    require(omitted_image[A_ROLE] == {A_ROLE: Fraction(1), C_ROLE: Fraction(1)},
            "omitting the early read did not drop b from a")
    doubled = [list(event) for event in NEW]
    doubled[0][3] = "2"
    _, doubled_image, _ = simulate(doubled, frames, charts, occupied)
    require(doubled_image[A_ROLE][B_ROLE] == 2, "a doubled early coefficient was not visible")
    expect_rejected(
        lambda: simulate(list(NEW[1:]) + [list(NEW[0])], frames, charts, occupied),
        "deferred early ADD",
    )
    post_update = {B_ROLE: Fraction(1), C_ROLE: Fraction(1)}
    late_value = {A_ROLE: Fraction(1)}
    for key, value in post_update.items():
        late_value[key] = late_value.get(key, 0) + value
    late_value[C_ROLE] = late_value.get(C_ROLE, 0) + 1
    require(late_value[C_ROLE] == 2, "reading b after b += c and still adding c does not double c")
    extended = list(source["program"]) + list(OLD)
    require(hits(extended, OLD) == [START, 25984], "a second copy of the interval was not found")
    expect_rejected(lambda: span([82, 82]), "dependent basis")
    print(PASS)


if __name__ == "__main__":
    main()
