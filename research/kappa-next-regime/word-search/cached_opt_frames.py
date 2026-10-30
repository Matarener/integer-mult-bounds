#!/usr/bin/env python3
"""Cache unchanged frame components during scalar-graph exploration.

The optimizer and exact frame algebra are imported read-only from the frozen
adaptive continuation.  A cache key retains every variable's ordered lower
and upper frame plus every paid edge with multiplicity; external fixed nodes
are replaced by their exact fixed frame.  Numeric register/node labels do not
affect this objective.  Cached assignments are relabelled on return.

This is discovery acceleration only.  Emitted words require uncached profile
replay and complete native verification before their saving is claimed.
Credit Nick Petalas's joint graph method and the frozen implementation's
retained attribution.  Substantial OpenAI assistance.  Apache-2.0.
"""
from collections import Counter, OrderedDict
from pathlib import Path
import sys

FROZEN = Path(__file__).resolve().parents[2] / 'kappa-adaptive-continuation' / 'native-alternatives'
sys.path.insert(0, str(FROZEN))
import opt_frames as original

_uncached = original.solve_component
CACHE = OrderedDict()
STATS = Counter()


def solve_component(comp, edges, lo, hi, max_bucket):
    labels = {node: index for index, node in enumerate(comp)}
    def endpoint(node, frame):
        if node in labels:
            return labels[node], ()
        return -1, lo[node] if node >= 0 else frame
    normalized = []
    for _, a, af, b, bf in edges:
        if a in labels or b in labels:
            normalized.append((endpoint(a, af), endpoint(b, bf)))
    key = (max_bucket, tuple((lo[node], hi[node]) for node in comp), tuple(sorted(normalized)))
    if key in CACHE:
        values, count = CACHE[key]
        CACHE.move_to_end(key)
        STATS['hits'] += 1
        return {node: values[index] for index, node in enumerate(comp)}, count
    answer, count = _uncached(comp, edges, lo, hi, max_bucket)
    values = tuple(answer[node] for node in comp)
    CACHE[key] = values, count
    STATS['misses'] += 1
    if len(CACHE) > 10000:
        CACHE.popitem(last=False)
        STATS['evictions'] += 1
    return answer, count


def optimize(word, max_bucket=100000):
    prior = original.solve_component
    original.solve_component = solve_component
    try:
        return original.optimize(word, max_bucket)
    finally:
        original.solve_component = prior


def uncached_optimize(word, max_bucket=100000):
    return original.optimize(word, max_bucket)
