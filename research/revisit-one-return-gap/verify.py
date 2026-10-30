#!/usr/bin/env python3
"""No restored (11,10) word has both a length-4 and a length-6 return.

Revisit 1 leaves two extra prefix visits. The resulting return-length sets
are enumerated exhaustively. Odd distances are excluded by weight parity.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_REVISIT_ONE_RETURN_GAP split=11,10 incompatible=4+6 patterns=231 no_new_kappa"
LABELS = 7
LENGTH = 22
SPLIT = (11, 10)
KAPPA = Fraction(836330098538459, 500000000000000000)
WITNESS_TWO = (5, 5, 4, 0, 4, 1, 4, 0, 4, 2, 0, 1, 0, 3, 0, 1, 0, 2, 0, 1, 0, 3)
WITNESS_FOUR = (0, 1, 0, 1, 2, 3, 2, 4, 2, 3, 2, 5, 2, 3, 2, 4, 2, 3, 2, 6, 5, 6)


def fail(message):
    raise SystemExit("FAIL_REVISIT_ONE_RETURN_GAP " + message)


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
    require(set(pinned) == {"certificates/selected-result.json"}, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def positive_domain():
    half = 1 << (LABELS - 1)
    rows = []
    for small in range(1, LENGTH):
        for large in range(small, LENGTH):
            budget = large * (large - 1) // 2 + small * (small - 1) // 2 - (half - 1)
            excess = large * small - half
            need = -((-excess) // 2) if excess > 0 else 0
            upper = budget + budget * budget // 4 if budget > 0 else budget
            if (
                large <= LENGTH // 2
                and small <= LENGTH // 2
                and large * small >= half
                and budget >= 0
                and upper >= need
            ):
                rows.append((large, small))
    return rows


def prefixes(word):
    state = 0
    states = [0]
    for label in word:
        state ^= 1 << label
        states.append(state)
    return states


def split_of(states):
    unique = set(states)
    even = sum(state.bit_count() % 2 == 0 for state in unique)
    odd = len(unique) - even
    return tuple(sorted((even, odd), reverse=True)), len(unique)


def return_lengths(states):
    return {
        right - left
        for left, earlier in enumerate(states)
        for right in range(left + 1, len(states))
        if states[right] == earlier
    }


def coincidence_patterns():
    """Partitions of 23 prefix positions with exactly two extra visits and a closed origin."""
    patterns = []
    for middle in range(1, LENGTH):
        patterns.append(frozenset({middle, LENGTH - middle, LENGTH}))
    for left in range(1, LENGTH):
        for right in range(left + 1, LENGTH):
            patterns.append(frozenset({LENGTH, right - left}))
    return patterns


def evaluate():
    authenticate()
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    require(Fraction(selected["kappa"]) == KAPPA, "the selected kappa moved")
    for state in range(1 << LABELS):
        for label in range(LABELS):
            require((state ^ (1 << label)).bit_count() % 2 != state.bit_count() % 2, "a step kept the weight parity")
    require(SPLIT in positive_domain(), "split (11,10) left the positive domain")
    require(LENGTH - sum(SPLIT) == 1, "the split is no longer revisit 1")
    patterns = coincidence_patterns()
    require(len(patterns) == 231, "the coincidence inventory moved")
    require(all(4 not in pattern or 6 not in pattern for pattern in patterns), "a pattern carries both 4 and 6")
    for pattern in patterns:
        interior = {distance for distance in pattern if 4 <= distance <= 18}
        if len(interior) == 2:
            left, right = sorted(interior)
            require(left + right == LENGTH, "two interior distances do not complement")
        require(len(interior) <= 2, "a revisit-1 pattern has three interior distances")
    require(frozenset({4, 6, LENGTH}) not in patterns, "the forbidden pair was enumerated")
    for word, expected in (
        (WITNESS_TWO, frozenset({2, 20, 22})),
        (WITNESS_FOUR, frozenset({4, 18, 22})),
    ):
        states = prefixes(word)
        observed_split, unique = split_of(states)
        lengths = return_lengths(states)
        require(states[-1] == 0 and len(word) == LENGTH, "a witness is not restored")
        require(observed_split == SPLIT and unique == sum(SPLIT), "a witness missed the split")
        require(lengths == expected, "a witness return set moved")
        broken = list(word)
        broken[-1] = (broken[-1] + 1) % LABELS
        require(prefixes(broken)[-1] != 0, "a broken closure stayed closed")
    return {
        "split": [11, 10],
        "revisit": 1,
        "patterns": len(patterns),
        "incompatible_pair": [4, 6],
        "attained_sets": ["2,20,22", "4,18,22"],
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    stored = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == stored, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
