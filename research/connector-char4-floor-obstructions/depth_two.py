"""Replay the scoped characteristic-four depth-two block census.

Each source occurs exactly four times. A depth-two block represents every
binary mask as the sum of two prefix vectors modulo four, with boundary zero
available for padding. Source labels are ordered by first occurrence. The safe
pruning lemma is documented in DEPTH2.md.

Resource bounds: k is validated in 1..5, table storage has at most
2 * 5**5 * 4**5 unsigned 32-bit entries, and DFS frames have capacity 4*k+1.
Python necessarily allocates integers and iterator objects during traversal;
live state stays within these fixed input-derived bounds. A separately written native implementation is retained as an optional
independent cross-check.
"""
from array import array
import argparse
import itertools
import json
import math
from typing import NamedTuple

MAX_K = 5


class Tables(NamedTuple):
    k: int
    past_count: int
    full: int
    actual: array
    future: array
    both_future: tuple
    valid_past: tuple
    children: tuple
    ways: tuple
    depths: tuple


def subcubes(k):
    """Index each Boolean subcube by its fixed-zero and fixed-one masks."""
    masks = 1 << k
    cubes = [0] * (1 << (2*k))
    for zero in range(masks):
        for one in range(masks):
            if not zero & one:
                cubes[zero | (one << k)] = sum(
                    1 << mask for mask in range(masks)
                    if not mask & zero and mask & one == one)
    return cubes


def allowed_future(past, current, cubes, k):
    """Masks feasible coordinatewise for one old and one future boundary."""
    zero = one = 0
    for j, (p, n) in enumerate(zip(past, current)):
        if p == 0:
            if n >= 2:
                zero |= 1 << j
        elif p == 1:
            if n == 4:
                one |= 1 << j
        elif p == 2:
            if n == 4:
                return 0
            if n == 3:
                one |= 1 << j
        elif p == 4:
            zero |= 1 << j
        else:
            raise RuntimeError('past-count three must be omitted')
    return cubes[zero | (one << k)]


def fill_pair_tables(currents, pasts, cubes, k):
    """Precompute actual new readouts and safe one-future-cut relaxations."""
    width = len(pasts)
    actual = array('I', [0]) * (len(currents)*width)
    future = array('I', [0]) * (len(currents)*width)
    if actual.itemsize != 4:
        raise RuntimeError('this replay requires 32-bit unsigned integer storage')
    for cid, current in enumerate(currents):
        base = cid*width
        for pid, past in enumerate(pasts):
            if any(p > n for p, n in zip(past, current)):
                continue
            residues = tuple((p+n) % 4 for p, n in zip(past, current))
            if all(r <= 1 for r in residues):
                actual[base+pid] = 1 << sum(r << j for j, r in enumerate(residues))
            future[base+pid] = allowed_future(past, current, cubes, k)
    return actual, future


def build_tables(k):
    """Initialize every fixed-capacity table before the census traversal."""
    if not 1 <= k <= MAX_K:
        raise ValueError(f'k must lie in 1..{MAX_K}')
    cubes = subcubes(k)
    powers = tuple(5**j for j in range(k))
    pasts = tuple(itertools.product((0, 1, 2, 4), repeat=k))
    past_index = {past: pid for pid, past in enumerate(pasts)}
    currents = [None] * (5**k)
    for counts in itertools.product(range(5), repeat=k):
        currents[sum(v*powers[j] for j, v in enumerate(counts))] = counts
    actual, future = fill_pair_tables(currents, pasts, cubes, k)
    both_future, valid_past, children, ways, depths = [], [], [], [], []
    for cid, counts in enumerate(currents):
        depth = sum(counts)
        introduced = sum(v != 0 for v in counts)
        denominator = math.factorial(k-introduced) * math.prod(
            math.factorial(4-v) for v in counts)
        numerator = math.factorial(4*k-depth)
        if numerator % denominator:
            raise RuntimeError('nonintegral subtree completion count')
        ways.append(numerator // denominator)
        depths.append(depth)
        children.append(tuple(cid+powers[j] for j, v in enumerate(counts)
                              if v < 4 and j <= introduced))
        both_future.append(cubes[sum((v >= 3) << j for j, v in enumerate(counts))])
        valid_past.append(past_index.get(counts, -1))
    return Tables(k, len(pasts), (1 << (1 << k))-1, actual, future,
                  tuple(both_future), tuple(valid_past), tuple(children),
                  tuple(ways), tuple(depths))


def inspect_state(tables, cid, served, prefix_ids, count):
    """Update served masks and the safe future-representation upper bound."""
    pid = tables.valid_past[cid]
    if pid >= 0:
        if count >= len(prefix_ids):
            raise RuntimeError('past-prefix capacity exhausted')
        prefix_ids[count] = pid
        count += 1
    base = cid*tables.past_count
    possible = tables.both_future[cid]
    for index in range(count):
        position = base+prefix_ids[index]
        served |= tables.actual[position]
        possible |= tables.future[position]
    return served, possible | served, count


def walk_tables(tables, threshold):
    """Traverse the canonical word tree with a bounded explicit DFS stack."""
    capacity = 4*tables.k+1
    prefix_ids = [0]*capacity
    state_ids, served_masks = [0]*capacity, [1]*capacity
    prefix_counts, next_children = [0]*capacity, [-1]*capacity
    pruned_depth = [0]*capacity
    nodes = pruned = accounted = solutions = 0
    depth = 0
    step_limit = 2*capacity*tables.ways[0]+1
    for _ in range(step_limit):
        if depth < 0:
            return nodes, pruned, accounted, solutions, pruned_depth
        cid = state_ids[depth]
        if next_children[depth] == -1:
            nodes += 1
            served, possible, count = inspect_state(
                tables, cid, served_masks[depth], prefix_ids, prefix_counts[depth])
            served_masks[depth], prefix_counts[depth] = served, count
            if served.bit_count() >= threshold or possible.bit_count() < threshold:
                accounted += tables.ways[cid]
                if served.bit_count() >= threshold:
                    solutions += tables.ways[cid]
                else:
                    pruned += 1
                    pruned_depth[tables.depths[cid]] += 1
                depth -= 1
                continue
            next_children[depth] = 0
            if not tables.children[cid]:
                raise RuntimeError('unclassified terminal state')
        child_index = next_children[depth]
        children = tables.children[cid]
        if child_index == len(children):
            depth -= 1
            continue
        next_children[depth] += 1
        child = children[child_index]
        inherited_served, inherited_count = served_masks[depth], prefix_counts[depth]
        depth += 1
        if depth >= capacity:
            raise RuntimeError('DFS frame capacity exhausted')
        state_ids[depth], served_masks[depth] = child, inherited_served
        prefix_counts[depth], next_children[depth] = inherited_count, -1
    raise RuntimeError('canonical traversal iteration bound exhausted')


def census(k, threshold=None):
    if not 1 <= k <= MAX_K:
        raise ValueError(f'k must lie in 1..{MAX_K}')
    if threshold is None:
        threshold = 1 << k
    if not 1 <= threshold <= 1 << k:
        raise ValueError('threshold exceeds the mask count')
    tables = build_tables(k)
    nodes, pruned, accounted, solutions, pruned_depth = walk_tables(tables, threshold)
    expected = math.factorial(4*k) // (math.factorial(4)**k * math.factorial(k))
    if accounted != expected:
        raise RuntimeError(f'completion accounting failed: {accounted} != {expected}')
    return {'k': k, 'covered_threshold': threshold, 'canonical_words': expected, 'visited_nodes': nodes,
            'pruned_nodes': pruned, 'accounted_words': accounted,
            'solutions': solutions, 'pruned_depth': pruned_depth}


def served_by_pairs(word, k):
    """Direct integer-coordinate calibration, without future-cut pruning."""
    if not 1 <= k <= MAX_K:
        raise ValueError(f'k must lie in 1..{MAX_K}')
    if len(word) != 4*k or any(word.count(j) != 4 for j in range(k)):
        raise ValueError('expected a balanced characteristic-four source word')
    prefix = [(0,)*k]
    for label in word:
        current = list(prefix[-1])
        current[label] += 1
        prefix.append(tuple(current))
    served = 0
    for a, b in itertools.combinations_with_replacement(prefix, 2):
        residues = tuple((x+y) % 4 for x, y in zip(a, b))
        if all(value <= 1 for value in residues):
            served |= 1 << sum(value << j for j, value in enumerate(residues))
    return served


def canonical(word):
    if len(word) > 4*MAX_K:
        raise ValueError('canonical calibration word exceeds the size bound')
    introduced = set()
    for label in word:
        if label not in introduced:
            if label != len(introduced):
                return False
            introduced.add(label)
    return True


def brute_histogram(k):
    """Unpruned control on all k**(4*k) strings, restricted to k<=3."""
    if not 1 <= k <= 3:
        raise ValueError('unpruned calibration is bounded at three sources')
    histogram = [0] * ((1 << k)+1)
    words = 0
    for word in itertools.product(range(k), repeat=4*k):
        if any(word.count(j) != 4 for j in range(k)) or not canonical(word):
            continue
        words += 1
        histogram[served_by_pairs(word, k).bit_count()] += 1
    return words, histogram


def coordinate_controls():
    tables = build_tables(1)
    for current in range(5):
        expected = sum(1 << bit for bit in (0, 1) if any(
            (a+b) % 4 == bit for a, b in itertools.combinations_with_replacement(
                range(current, 5), 2)))
        if tables.both_future[current] != expected:
            raise RuntimeError('two-future-cut relaxation control failed')
        for pid, past in enumerate((0, 1, 2, 4)):
            if past > current:
                continue
            expected = sum(1 << bit for bit in (0, 1) if any(
                (past+future) % 4 == bit for future in range(current, 5)))
            if tables.future[current*4+pid] != expected:
                raise RuntimeError('old/future-cut relaxation control failed')
    positive = (0, 1, 0, 0, 0, 1, 1, 1, 2, 3, 2, 2, 2, 3, 3, 3)
    if served_by_pairs(positive, 4) != (1 << 16)-1:
        raise RuntimeError('known four-source depth-two block rejected')
    try:
        served_by_pairs(positive[:-1], 4)
    except ValueError:
        pass
    else:
        raise RuntimeError('dropped-call word accepted')
    negative = tuple(j for j in range(5) for _ in range(4))
    if served_by_pairs(negative, 5).bit_count() != 16:
        raise RuntimeError('sorted five-source depth-two control failed')
    for invalid in (0, MAX_K+1):
        try:
            build_tables(invalid)
        except ValueError:
            continue
        raise RuntimeError('invalid table dimension accepted')


def calibrate():
    coordinate_controls()
    result = []
    for k in range(1, 4):
        words, histogram = brute_histogram(k)
        for threshold in range(1, (1 << k)+1):
            pruned = census(k, threshold)
            expected = sum(histogram[threshold:])
            if words != pruned['canonical_words'] or expected != pruned['solutions']:
                raise RuntimeError(f'unpruned threshold control disagrees at k={k}')
        result.append({'k': k, 'canonical_words': words, 'solutions': histogram[-1]})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--k', type=int, choices=range(1, MAX_K+1), default=5)
    parser.add_argument('--threshold', type=int, default=None)
    args = parser.parse_args()
    print(json.dumps({'census': census(args.k, args.threshold), 'calibration': calibrate()}, sort_keys=True))


if __name__ == '__main__':
    main()
