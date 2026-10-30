#!/usr/bin/env python3
"""Price one adjacent F0 ADD after the first rank-positive climb.

The retained local contract is the nested-frame rule used by the selected
word: a climb replaces a register's frame only by a strict rank increase, and
a scalar ADD may read only registers that already sit in its annotated frame.
This note does not admit a physical tape layout or a new kappa.
"""
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = "research/joint-query/certificate.json.gz"
ARCHIVE = "research/community-frontier1042-audit/selected-replay.tar.gz"
CERTIFICATE_SHA = "a5ed85fac5ebf3c091482a113ab0d351eb5a7892fe2841a35e16017ec1ff49f7"
ARCHIVE_SHA = "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754"
WORD_MEMBER = "slots/local/CANONICAL-WORD.json.gz"
WORD_SHA = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"
RECIPE_MEMBER = "slots/local/CLIFFORD-RECIPES.json"
RECIPE_SHA = "d0768f2164d5f64a2fdbec422f1cfde4e400818792f1904ca541958377243731"
CLIMB = ["climb", "A", 546, 0, 4, 1]
ADD = ["scalar", ["add", ["L", 546], ["L", 561], -1, 1], 4]
INVERSE = ["scalar", ["add", ["L", 546], ["L", 561], 1, 1], 4]
PREFIX_SHA = "15115954461f2cb93e2266822d82bfac1ab8de7d460ff78fcf594d21c61d2b53"
CLIMB_INDEX = 9894
ADD_INDEX = 9895


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(obj):
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def load_bytes(path, sha, cap):
    file = ROOT / path
    need(file.is_file() and not file.is_symlink(), "source file: " + path)
    raw = file.read_bytes()
    need(len(raw) <= cap, "source cap: " + path)
    need(hashlib.sha256(raw).hexdigest() == sha, "source sha: " + path)
    return raw


def contained(old, new):
    """True when every old axis lies in the F2-span of the new axes."""
    span = list(new)
    for vector in old:
        reduced = vector
        for axis in span:
            pivot = axis.bit_length() - 1
            if pivot >= 0 and (reduced >> pivot) & 1:
                reduced ^= axis
        if reduced:
            return False
    return True


def scalar_work(numerator, denominator):
    """Retained coefficient bill: clear, bit doubles, bit adds, halvings, +2.

    The sign is inside the final +2, so +1 and -1 have the same count.
    """
    need(numerator > 0 and denominator > 0, "positive coefficient parts")
    need(denominator & (denominator - 1) == 0, "dyadic denominator")
    count = 1
    for index, bit in enumerate(bin(numerator)[2:]):
        if index:
            count += 1
        if bit == "1":
            count += 1
    count += denominator.bit_length() - 1
    return count + 2


def replay(events, start, frames):
    current = list(start)
    climbs = 0
    scalars = 0
    for index, event in enumerate(events):
        kind = event[0]
        if kind == "climb":
            _, _part, register, old, new, rank = event
            need(current[register] == old, "climb leaves its recorded frame")
            need(contained(frames[old], frames[new]), "climb is not nested")
            need(rank == len(frames[new]) - len(frames[old]) > 0, "climb rank")
            current[register] = new
            climbs += 1
        elif kind == "scalar":
            _gate, operation, frame = event
            operands = [operation[1]]
            if operation[0] in ("add", "copy"):
                operands.append(operation[2])
            for token in operands:
                if token[0] == "L":
                    need(current[token[1]] == frame,
                         "scalar operand leaves the annotated frame at " + str(index))
            scalars += 1
    return current, climbs, scalars


def main():
    certificate = json.loads(gzip.decompress(load_bytes(CERTIFICATE, CERTIFICATE_SHA, 8 * 1024**2)))
    events = certificate["core_words"]["forward"]
    need(events[CLIMB_INDEX] == CLIMB, "climb event changed")
    need(events[ADD_INDEX] == ADD, "adjacent ADD changed")
    need(digest(events[:CLIMB_INDEX]) == PREFIX_SHA, "prefix before the climb changed")
    archive = load_bytes(ARCHIVE, ARCHIVE_SHA, 64 * 1024**2)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        word_info = tar.getmember(WORD_MEMBER)
        recipe_info = tar.getmember(RECIPE_MEMBER)
        need(word_info.isfile() and recipe_info.isfile(), "word members")
        word_raw = tar.extractfile(word_info).read()
        recipe_raw = tar.extractfile(recipe_info).read()
    need(hashlib.sha256(word_raw).hexdigest() == WORD_SHA, "word sha")
    need(hashlib.sha256(recipe_raw).hexdigest() == RECIPE_SHA, "recipe sha")
    word = json.loads(gzip.decompress(word_raw))
    recipes = json.loads(recipe_raw)
    frames = word["frames"]
    start = word["start"]
    need(frames[0] == [] and frames[4] == [459], "frame 0 and frame 4")
    need(start[546] == 0 and start[561] == 4, "entrance frames")
    children = {(child["old"], child["new"]): child for child in recipes["children"]}
    need(children[(0, 4)]["rank"] == 1, "forward child rank")
    need((4, 0) not in children, "reverse child unexpectedly present")

    moved_561 = [index for index, event in enumerate(events[:ADD_INDEX])
                 if event[0] == "climb" and event[2] == 561]
    need(moved_561 == [], "L561 climbs before the ADD")
    writes_561 = [index for index, event in enumerate(events[:ADD_INDEX])
                  if event[0] == "scalar" and event[1][1] == ["L", 561]]
    need(writes_561 == [], "L561 is written before the ADD")
    need(events[7963] == ["residual_adapter", "pre", 561, 4], "entrance wrapper")

    current, climbs, scalars = replay(events, start, frames)
    need(current == word["final"], "replay misses the published final frames")
    need(word["final"][546] == 1 and word["final"][561] == 1, "published endpoints")
    climbs_before = sum(1 for event in events[:CLIMB_INDEX] if event[0] == "climb")
    need(climbs_before == 0, "an earlier climb already moved a register")
    before = replay(events[:CLIMB_INDEX], start, frames)[0]
    need(before == list(start), "frames move before the first climb")
    at_add = replay(events[:ADD_INDEX], start, frames)[0]
    need(at_add[546] == 4 and at_add[561] == 4, "pair frames")
    after = replay(events[:ADD_INDEX + 1], start, frames)[0]
    need(after[546] == 4 and after[561] == 4, "the ADD does not change frames")

    work = scalar_work(1, 1)
    real_steps = 2 * work
    need(work == 4 and real_steps == 8, "unit coefficient work")
    need(scalar_work(3, 1) == 6 and scalar_work(1, 2) == 5, "work controls")

    # Dropping the climb leaves L546 in frame 0, so the frame-4 ADD is illegal.
    try:
        replay([ADD], start, frames)
    except ValueError as exc:
        need("annotated frame" in str(exc), "missing-climb control")
    else:
        raise ValueError("ADD without the climb was accepted")

    # An entrance for L561 in frame 0 is also illegal: the source would move.
    moved_start = list(start)
    moved_start[561] = 0
    try:
        replay(events[CLIMB_INDEX:ADD_INDEX + 1], moved_start, frames)
    except ValueError as exc:
        need("annotated frame" in str(exc), "moved-source control")
    else:
        raise ValueError("ADD with relocated L561 was accepted")

    _restored, _climbs, inverse_scalars = replay([INVERSE], at_add, frames)
    need(inverse_scalars == 1 and scalar_work(1, 1) == work, "inverse work")

    print(
        "PASS_QQ16_ADJACENT_ADD_BILL"
        " climb=9894 add=9895 frame=4 axis=459"
        " rank_child=1 scalar_work=%d real_steps=%d"
        " climbs_before_pair=%d reverse_child=absent"
        " word_climbs=%d word_scalars=%d"
        " no_new_kappa"
        % (work, real_steps, climbs_before, climbs, scalars)
    )


if __name__ == "__main__":
    main()
