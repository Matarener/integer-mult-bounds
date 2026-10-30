"""Positive endpoints, full dirty columns, and small independent comparisons."""

from itertools import product

import algebra
import oracle


def direct_gram(kinds, deleted=None):
    calls = [(role, kind) for role, kind in enumerate(kinds) for _ in range(3)]
    if deleted is not None:
        calls.pop(deleted)
    a = tuple(sum((other == role) << j for j, (other, _) in enumerate(calls))
              for role, _ in calls)
    mask = sum((kind == 1) << j for j, (_, kind) in enumerate(calls))
    return a, mask


def dirty_columns(kinds):
    """Five real roles, including two independent restored spectators."""
    count = 0
    for column in range(40):
        state = [0] * 5
        state[column // 8] = 1 << (column % 8)
        for role, kind in enumerate(kinds):
            permutation = oracle.LEFT_I if kind == 1 else oracle.LEFT_J
            for _ in range(3):
                packet = state[role]
                state[role] = sum(((packet >> h) & 1) << permutation[h] for h in range(8))
        expected = [0] * 5
        role, h = divmod(column, 8)
        if role < 3:
            permutation = oracle.LEFT_I if kinds[role] == 1 else oracle.LEFT_J
            h = permutation[h] ^ 4
        expected[role] = 1 << h
        algebra.require(state == expected, "positive dirty column mismatch")
        count += 1
    return count


def small_replay():
    generic = valuations = positives = omissions = dirty = 0
    for n in range(1, 4):
        for a in algebra.grams(n):
            for mask in range(1 << n):
                actual = algebra.endpoint(a, mask)
                algebra.require(actual == oracle.action(a, mask), "independent action mismatch")
                for si in range(n + 1):
                    for sj in range(n + 1 - si):
                        pair = oracle.projections(a, mask, si, sj)
                        independent = pair is not None and actual == oracle.wanted(a, *pair)
                        algebra.require(algebra.accepts(a, mask, si, sj) == independent,
                                        "independent criterion mismatch")
                        valuations += 1
                generic += 1
    for kinds in product((1, 2), repeat=3):
        a, mask = direct_gram(kinds)
        si = kinds.count(1)
        algebra.require(algebra.accepts(a, mask, si, 3 - si), "nine-call control rejected")
        algebra.require(oracle.action(a, mask) == algebra.endpoint(a, mask),
                        "nine-call independent action mismatch")
        positives += 1
        dirty += dirty_columns(kinds)
        for deleted in range(9):
            a, mask = direct_gram(kinds, deleted)
            algebra.require(not algebra.accepts(a, mask, si, 3 - si), "omitted call accepted")
            omissions += 1
    return {"generic_words": generic, "criterion_valuations": valuations,
            "positive_nine_call_words": positives, "deleted_call_controls": omissions,
            "faithful_dirty_columns": dirty}
