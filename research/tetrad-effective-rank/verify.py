#!/usr/bin/env python3
"""Bound the tetrad-local alphabet and screen its two ideal ranks.

Twenty-eight four-frames each demand four double-meetings. A paid term has
rank at most four, and its rank is at least the number of frames it meets.
The note's completed identities use ranks two and one.
"""

import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
import ceiling as ceiling_mod  # noqa: E402

MARKER = "PASS_TETRAD_EFFECTIVE_RANK rank2_above_five_percent=false no_new_kappa"
FRAMES = 28
MEETINGS = 4
CAP = 4
FLOOR = FRAMES * MEETINGS
WORD = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
MARGIN = Fraction(21, 20)
README_SENTENCES = (
    "total copied\nrank at least **112**, and each paid term has rank at most **four**.",
    "COPY profile\n`{2: 56}`",
    "profile `{1: 112}`",
    "sum_k beta_k >= 112,              1 <= beta_k <= 4 for every paid term.",
)
WORD_SENTENCE = "`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`, local mass 5,586"


def fail(message):
    raise SystemExit("FAIL_TETRAD_EFFECTIVE_RANK " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p112-tetrad-local-decoder/README.md",
        "research/complex-local-word-ceiling/ceiling.py",
        "research/complex-local-word-ceiling/README.md",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def pair_design():
    terms = []
    for pair in range(FRAMES // 2):
        frames = {2 * pair, 2 * pair + 1}
        terms.extend({frame for frame in frames} for _ in range(MEETINGS))
    return terms


def single_design():
    return [{frame} for frame in range(FRAMES) for _ in range(MEETINGS)]


def frame_counts(terms):
    counts = [0] * FRAMES
    for term in terms:
        for frame in term:
            counts[frame] += 1
    return counts


def effective(terms):
    return Fraction(sum(len(term) for term in terms), len(terms))


def screen(local):
    hi = ceiling_mod.ceiling(local, 73, 896, 9, 64, grid=Fraction(1, 10**12), unpaid=1)[1]
    require(hi.denominator != 0, "ceiling vanished")
    return hi


def evaluate():
    authenticate()
    note = (ROOT / "research/p112-tetrad-local-decoder/README.md").read_text(encoding="utf-8")
    ceiling_readme = (ROOT / "research/complex-local-word-ceiling/README.md").read_text(encoding="utf-8")
    for sentence in README_SENTENCES:
        require(sentence in note, "the tetrad sentence moved")
    require(WORD_SENTENCE in ceiling_readme, "the selected local word moved")
    require("| Local mass as rank-16 children | 2.31 |" in ceiling_readme, "the rank-16 lever moved")
    paired = pair_design()
    singles = single_design()
    require(frame_counts(paired) == [MEETINGS] * FRAMES, "the rank-2 design missed a frame")
    require(frame_counts(singles) == [MEETINGS] * FRAMES, "the rank-1 design missed a frame")
    require(all(1 <= len(term) <= CAP for term in paired + singles), "a sharp term left the cap")
    require(effective(paired) == 2 and effective(singles) == 1, "the exhibited effective ranks moved")
    require(sum(len(term) for term in paired) == FLOOR, "the rank-2 copy mass moved")
    require(sum(len(term) for term in singles) == FLOOR, "the rank-1 copy mass moved")
    require(27 * CAP < FLOOR and 28 * CAP == FLOOR, "the rank-4 count window moved")
    mass = sum(rank * count for rank, count in WORD.items())
    require(mass == 5586, "the selected local mass moved")
    baseline = screen(WORD)
    rank2 = screen({2: Fraction(mass, 2)})
    rank4 = screen({4: Fraction(mass, 4)})
    require(rank2 / baseline < MARGIN, "the rank-2 screen cleared five percent")
    require(rank4 / baseline >= MARGIN, "the rank-4 cap screen missed five percent")
    return {
        "frames": FRAMES,
        "copy_floor": FLOOR,
        "term_rank_cap": CAP,
        "exhibited_effective_ranks": [2, 1],
        "best_exhibited_effective_rank": 2,
        "rank4_count_meeting_floor": 28,
        "baseline_ceiling": str(baseline),
        "rank2_ceiling": str(rank2),
        "rank4_ceiling": str(rank4),
        "rank2_above_five_percent": bool(rank2 / baseline >= MARGIN),
        "rank4_above_five_percent": bool(rank4 / baseline >= MARGIN),
        "rank16_inside_cap": 16 <= CAP,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
