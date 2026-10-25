#!/usr/bin/env python3
"""Independent five-source canonical census using set partitions.

No native/C, predecessor verifier, primary lift implementation, or source
census receipt is read. Prefix pairs and literal intervals are separate
evaluations of each enumerated word.
"""
import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations
from math import comb, factorial
import hashlib
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


@lru_cache(maxsize=None)
def pairings(positions):
    if not positions:
        return ((),)
    first, rest = positions[0], positions[1:]
    answer = []
    for index, mate in enumerate(rest):
        remaining = rest[:index] + rest[index + 1:]
        for smaller in pairings(remaining):
            answer.append(((first, mate),) + smaller)
    return tuple(answer)


def five_words():
    """Unique size-four group plus four indistinguishable size-two groups."""
    for quadruple in combinations(range(12), 4):
        remaining = tuple(i for i in range(12) if i not in quadruple)
        for pairs in pairings(remaining):
            groups = sorted((quadruple,) + pairs, key=lambda group: group[0])
            word = [None] * 12
            for label, group in enumerate(groups):
                for position in group:
                    word[position] = label
            yield tuple(word)


def first_appearance(word):
    renaming = {}
    answer = []
    for source in word:
        if source not in renaming:
            renaming[source] = len(renaming)
        answer.append(renaming[source])
    return tuple(answer)


def prefix_pairs(word):
    prefixes, state = [], 0
    for source in word:
        prefixes.append(state)
        state ^= 1 << source
    need(state == 0, 'source word is not restored')
    return frozenset(prefixes[a] ^ prefixes[b]
                     for a in range(len(prefixes)) for b in range(a + 1, len(prefixes))
                     if prefixes[a] != prefixes[b])


def literal_intervals(word):
    masks = set()
    for first in range(len(word)):
        parity = 0
        for last in range(first, len(word)):
            parity ^= 1 << word[last]
            if parity:
                masks.add(parity)
    return frozenset(masks)


def target_set(n, weight=4):
    return frozenset(mask for mask in range(1, 1 << n) if mask.bit_count() <= weight)


def projection_control(word):
    """Every literal interval mask projects to an available prefix-pair mask."""
    original = prefix_pairs(word)
    checked = 0
    for removed in range(5):
        reduced_word = tuple(source for source in word if source != removed)
        kept_masks = prefix_pairs(reduced_word)
        for mask in original:
            projected = mask & ~(1 << removed)
            if projected:
                need(projected in kept_masks, 'projection lost a nonzero two-read influence')
            checked += 1
    return checked


def run():
    targets = target_set(5)
    need(len(targets) == 30 and len(target_set(6)) == 56 and len(target_set(7)) == 98,
         'required target-family size mismatch')
    histogram = Counter()
    four_label_histogram = Counter()
    full_four_label_histogram = Counter()
    full, seen = [], set()
    weak_only, projection_checks = None, 0
    all_digest = hashlib.sha256()
    for word in five_words():
        need(word not in seen, 'set-partition enumeration duplicated a canonical word')
        seen.add(word)
        need(first_appearance(word) == word, 'word is not first-appearance canonical')
        counts = Counter(word)
        need(sorted(counts.values()) == [2, 2, 2, 2, 4] and set(counts) == set(range(5)),
             'wrong canonical source multiplicities')
        four_label = next(source for source, number in counts.items() if number == 4)
        four_label_histogram[four_label] += 1
        available = prefix_pairs(word)
        need(available == literal_intervals(word), 'prefix pairs disagree with literal intervals')
        coverage = available & targets
        histogram[len(coverage)] += 1
        all_digest.update(bytes(word))
        all_digest.update(bytes(sorted(coverage)))
        if coverage == targets:
            full.append(word)
            full_four_label_histogram[four_label] += 1
            projection_checks += projection_control(word)
        if weak_only is None and target_set(5, 3) <= available and coverage != targets:
            weak_only = {'word': list(word), 'coverage': len(coverage),
                         'missing_weight_four': sorted(targets - available)}
    expected_by_groups = comb(12, 4) * 105
    expected_by_quotient = 5 * factorial(12) // (factorial(4) * factorial(2) ** 4 * factorial(5))
    need(len(seen) == expected_by_groups == expected_by_quotient == 51975,
         'enumeration does not close its analytic class count')
    need(set(four_label_histogram) == set(range(5)), 'four-use source was accidentally fixed to label zero')
    need(full and any(word.count(0) != 4 for word in full), 'nonzero first-appearance four-use control missing')
    need(weak_only is not None, 'weight-four omission control missing')
    nonrestored_rejected = False
    try:
        prefix_pairs((0, 1, 0))
    except RuntimeError:
        nonrestored_rejected = True
    need(nonrestored_rejected, 'odd-use unrestored word was admitted')
    full.sort()
    full_payload = json.dumps(full, separators=(',', ':')).encode()
    return {
        'status': 'PASS', 'method': 'unique four-block positions plus perfect matching of eight other positions',
        'canonical_words': len(seen), 'all_words_interval_pair_agreement': True,
        'target_counts': {'five': 30, 'six': 56, 'seven': 98},
        'coverage_histogram': dict(sorted(histogram.items())),
        'four_use_source_label_histogram': dict(sorted(four_label_histogram.items())),
        'full_coverage_four_use_label_histogram': dict(sorted(full_four_label_histogram.items())),
        'full30_count': len(full), 'full30_words': full,
        'full30_list_canonical_json_sha256': hashlib.sha256(full_payload).hexdigest(),
        'all_enumerated_word_and_coverage_digest': all_digest.hexdigest(),
        'count_proof': {'choose_quadruple': comb(12, 4), 'remaining_pairings': 105,
                        'group_count': expected_by_groups, 'label_quotient_count': expected_by_quotient},
        'projection_nonzero_mask_checks_on_full_five_words': projection_checks,
        'controls': {'four_use_label_not_fixed_to_zero': True,
                     'dropping_weight_four_targets_is_wrong': weak_only,
                     'unrestored_odd_use_word_rejected': nonrestored_rejected},
        'scope': 'Complete five-source (4,2,2,2,2) first-appearance core census only',
        'limitations': ['No six/seven-source lift enumeration in this oracle.',
            'Projection necessity is separate from sufficiency: a full five-core need not lift.',
            'No arbitrary-length word floor, supplier theorem, physical invoice, or new kappa.'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    print(json.dumps({k: result[k] for k in ('status', 'canonical_words', 'coverage_histogram',
        'full30_count', 'full30_list_canonical_json_sha256', 'scope')}, sort_keys=True))


if __name__ == '__main__':
    main()
