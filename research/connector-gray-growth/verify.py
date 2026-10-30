"""Source-bound checks of the explicit Gray connector construction.

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.
Predecessor interface, prefix criterion and counting: Nick Petalas's
PR4231/4248/6035, following Ross Richardson and the retained lineage.
All finite checks support the written proof; no supplier or new kappa.
"""
from collections import Counter
from hashlib import sha256
import json
from math import comb
from pathlib import Path
from types import ModuleType

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name):
    path = PACKAGE / (name + '.py')
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def source_checks():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_bytes())
    inputs = [row for row in manifest['files'] if row['usage'] == 'input']
    wanted = {
        'research/connector-depth-blocks/README.md',
        'research/connector-five-halves-growth/README.md',
        'research/unsigned-connector-characteristic/README.md',
    }
    require(len(inputs) == 3 and {row['path'] for row in inputs} == wanted,
            'source input coverage changed')
    for row in inputs:
        require(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                'source bytes changed: ' + row['path'])
    return len(inputs)


def block_checks(prod, independent):
    cases = masks = events = repeated = 0
    for k in range(1, 13):
        threshold = max(2, 1 << (k - 1))
        for c in (threshold, threshold + 1, threshold + 7):
            word, hits = prod.gray_block(k, c)
            reference_word, reference_hits = independent.block(independent.gray(k), k, c)
            require(word == reference_word, 'independent source word differs')
            require(hits[0] == (), 'zero mask should consume no depth')
            require({m: list(ts) for m, ts in hits.items() if m} == reference_hits,
                    'independent readout boundaries differ')
            independent.check_prefix(word, reference_hits, k, c, depth=2)
            require(all(len(ts) == 2 and ts[0] <= ts[1] for m, ts in hits.items() if m),
                    'two chronological reads missing')
            events += len(word)
            masks += len(reference_hits)
            cases += 1
    for k in range(1, 8):
        reflected = independent.gray(k)
        # First a backtrack before coverage, then a closed covering walk.
        walks = ([0, 1, 0] + reflected[1:], reflected + reflected[-2::-1])
        for states in walks:
            counts = Counter((a ^ b).bit_length() - 1 for a, b in zip(states, states[1:]))
            c = max(2, max(counts.values()))
            word, hits = prod.covering_block(k, c, states)
            reference_word, reference_hits = independent.block(states, k, c)
            require(word == reference_word, 'repeated walk source mismatch')
            require({m: list(ts) for m, ts in hits.items() if m} == reference_hits,
                    'repeated walk readout mismatch')
            independent.check_prefix(word, reference_hits, k, c, depth=2)
            repeated += 1
    return cases, masks, events, repeated


def execute(calls, k, c, independent):
    """Execute the actual yielded call sequence on all source/dirty columns.

    Every entry is a 2x2 matrix over Z/c; no A/B commutation is imposed.
    Each old output has its unchanged identity contribution because outputs
    are only destinations. All source and dirty columns are computed.
    """
    zero, ident = independent.ZERO, independent.I
    mul, add = independent.mul, independent.add
    maps = [(0, 1, 0, 0), (0, 0, 1, 0), (1, 1, 0, 1), (1, 0, 1, 1)]
    require(mul(maps[0], maps[1], c) != mul(maps[1], maps[0], c), 'commuting fixture')
    B = [maps[j % len(maps)] for j in range(k)]
    masks = range(1, 1 << k)
    A = {m: maps[(m + 1) % len(maps)] for m in masks}
    z = [zero] * k + [ident]
    outputs = {m: [zero] * (k + 1) for m in masks}
    count = Counter()
    total = 0
    for kind, index in calls:
        count[kind, index] += 1
        total += 1
        if kind == 'B':
            require(type(index) is int and 0 <= index < k, 'invalid source event')
            z[index] = add(z[index], B[index], c)
        elif kind == 'A':
            require(index in outputs, 'invalid output event')
            outputs[index] = [add(y, mul(A[index], a, c), c)
                              for y, a in zip(outputs[index], z)]
        else:
            raise ValueError('unknown call type')
    require(z == [zero] * k + [ident], 'dirty connector not restored')
    for mask in masks:
        expected = [mul(A[mask], B[j], c) if mask >> j & 1 else zero for j in range(k)] + [zero]
        require(outputs[mask] == expected, 'wrong full operator, including dirty dependence')
    expected_counts = Counter({('B', j): c for j in range(k)})
    expected_counts.update({('A', mask): c for mask in masks})
    require(count == expected_counts, 'complete-call multiplicities changed')
    require(total == c * (k + (1 << k) - 1), 'complete-call floor differs')
    return total


def composition_checks(prod, independent):
    words = outputs = calls = 0
    for c in range(2, 7):
        k = c.bit_length()
        word, hits = prod.gray_block(k, c)
        parts = [(k, word, hits)] * (c // 2)
        if c % 2:
            pair_word, pair_hits = prod.pair_block(c)
            independent.check_prefix(pair_word, {m: ts for m, ts in pair_hits.items() if m},
                                     2, c, depth=1)
            parts.append((2, pair_word, pair_hits))
        n = sum(width for width, _, _ in parts)
        require(n == prod.source_bound(c), 'attained source formula differs')
        joined, readouts = prod.compose_blocks(c, parts)
        oracle_word, oracle_reads, oracle_n = independent.compose(
            [(w, {m: list(ts) for m, ts in h.items() if m}, width) for width, w, h in parts], c)
        require(oracle_n == n and oracle_word == joined, 'concatenation mismatch')
        require({m: list(ts) for m, ts in readouts.items()} == oracle_reads,
                'concatenated readouts mismatch')
        independent.check_prefix(joined, readouts, n, c, depth=c)
        calls += execute(prod.literal_calls(joined, readouts), n, c, independent)
        outputs += len(readouts)
        words += 1
    return words, outputs, calls


def counting_checks(prod):
    require({c: prod.source_bound(c) for c in (256, 257, 512, 1024)} ==
            {256: 1152, 257: 1154, 512: 2560, 1024: 5632}, 'large source bounds')
    thresholds = []
    comparisons = 0
    for c in range(2, 129):
        n = 1
        # This is a finite arithmetic corroboration of the inherited bound,
        # not the proof that its first failure excludes all later n.
        while True:
            available = comb(c * n + c - 1, c)
            required = (1 << n) - 1
            comparisons += 1
            if available < required:
                break
            n += 1
            require(n <= 4 * c * (2*c).bit_length(), 'counting scan exceeded explicit cap')
        require(prod.source_bound(c) < n, 'construction contradicts counting bound')
        thresholds.append([c, n])
    require(thresholds[:8] == [[2, 7], [3, 14], [4, 22], [5, 30], [6, 38],
                               [7, 47], [8, 56], [9, 65]], 'predecessor threshold control')
    digest = sha256(json.dumps(thresholds, separators=(',', ':')).encode()).hexdigest()
    return len(thresholds), comparisons, digest


def mutation_checks(prod, independent):
    controls = 0
    reject = independent.rejected
    for args in ((0, 2), (2, 1), (3, 3), (True, 2)):
        controls += reject(lambda args=args: prod.gray_block(*args))
    for states in ([1, 0], [0, 3], [0, 1], [0, 1, 1, 0], [0, 4]):
        controls += reject(lambda states=states: prod.covering_block(2, 4, states))
    word, hits = prod.gray_block(3, 4)
    invalid = dict(hits)
    invalid[1] = (0, 0)
    controls += reject(lambda: independent.check_prefix(word, {m: ts for m, ts in invalid.items() if m},
                                                         3, 4, depth=2))
    controls += reject(lambda: prod.compose_blocks(4, [(3, word, hits)] * 3))
    controls += reject(lambda: prod.compose_blocks(4, [(3, word[:-1], hits)]))
    controls += reject(lambda: list(prod.literal_calls(word, {1: (-1,)})))
    # Test physical failures against the actual yielded schedule.
    full_word, readouts = prod.compose_blocks(4, [(3, word, hits)])
    calls = list(prod.literal_calls(full_word, readouts))
    first_a = next(i for i, x in enumerate(calls) if x[0] == 'A')
    controls += reject(lambda: execute(calls[:first_a] + calls[first_a+1:], 3, 4, independent))
    first_b = next(i for i, x in enumerate(calls) if x[0] == 'B')
    controls += reject(lambda: execute(calls[:first_b] + calls[first_b+1:], 3, 4, independent))
    bad_padding = {m: tuple(ts) for m, ts in readouts.items()}
    # Keep all c reads, but move a zero-state padding read to a nonzero prefix.
    times = list(bad_padding[1]); require(times[0] == 0, 'padding fixture')
    times[0] = 1; bad_padding[1] = tuple(sorted(times))
    controls += reject(lambda: independent.check_prefix(full_word, bad_padding, 3, 4, depth=4))
    controls += reject(lambda: execute(prod.literal_calls(full_word, bad_padding), 3, 4, independent))
    # The reversed-down order is part of the construction, not optional.
    word4, hits4 = prod.gray_block(4, 8)
    states4 = independent.gray(4)
    down = [(a ^ b).bit_length()-1 for a,b in zip(states4, states4[1:]) if not b & (a ^ b)]
    wrong_reverse = word4[:-len(down)] + down
    controls += reject(lambda: independent.check_prefix(wrong_reverse,
        {m: ts for m, ts in hits4.items() if m}, 4, 8, depth=2))
    return controls


def main():
    sources = source_checks()
    independent = load('independent')
    prod = load('construct')
    independent.run()
    blocks, masks, events, repeated = block_checks(prod, independent)
    compositions, outputs, literal = composition_checks(prod, independent)
    characteristics, comparisons, digest = counting_checks(prod)
    controls = mutation_checks(prod, independent)
    print(f'PASS_CONNECTOR_GRAY_GROWTH sources={sources} blocks={blocks} masks={masks} '
          f'source_events={events} repeated_walks={repeated} compositions={compositions} '
          f'outputs={outputs} literal_calls={literal} counting_characteristics={characteristics} '
          f'counting_comparisons={comparisons} controls={controls} no_new_kappa')
    print('COUNTING_THRESHOLDS_SHA256=' + digest)


if __name__ == '__main__':
    main()
