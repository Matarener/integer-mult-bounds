"""Separate restored-word oracle: even set partitions, no prefix prune.

The even-position-block method is credited to Nick Petalas's PR3005.
This implementation imports neither bounds.py nor a predecessor executable.
Prepared for SHIN09-git with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import combinations


def restored_partitions(n=5, length=12):
    word = [-1] * length

    def partition(positions, label):
        if not positions:
            yield tuple(word)
            return
        if label == n:
            return
        first, rest = positions[0], positions[1:]
        for size in range(2, len(positions) + 1, 2):
            for other in combinations(rest, size - 1):
                block = (first,) + other
                selected = set(block)
                for index in block:
                    word[index] = label
                yield from partition(tuple(i for i in rest if i not in selected), label + 1)

    yield from partition(tuple(range(length)), 0)


def inspect(word, n=5):
    location = 0
    points = []
    for label in word:
        points.append(location)
        location ^= 2 ** label
    if location != 0:
        raise ValueError("oracle restoration")
    simple = len(set(points)) == len(points)
    covered = {left ^ right for left in points for right in points}
    universal = covered == set(range(2 ** n))
    return tuple(points), simple, universal


def census(n=5, length=12):
    restored = 0
    closed, universal = [], []
    for word in restored_partitions(n, length):
        restored += 1
        _, simple, cover = inspect(word, n)
        if simple:
            closed.append(word)
            if cover:
                universal.append(word)
    return {"restored_partitions": restored, "simple_closed": len(closed),
            "simple_universal": len(universal)}, tuple(sorted(closed)), tuple(sorted(universal))

