#!/usr/bin/env python3
"""Independent fixed-site A2, cleanup and point-set frame certificate.

No primary or predecessor executable is imported.  The proof is compositional
on arbitrary inputs, rather than a second full free-operator interpreter.
Standard library, Python 3.9+.  Apache-2.0; ToikY with OpenAI Codex assistance.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
N, V = 704, 112
FULL_BASIS = [256, 128, 64, 32, 16, 8, 4, 2, 1]
PINS = {
    'base': '5ca4be99851f8878cbfe0fd6c454df926b11218f17feefa1664721cf03156699',
    'extra': '965268a9be73d3f62e7ef680d18f108cf064bfe1f44b82157baa61443232904e',
}
# This is the fixed witness, not a census or a search algorithm.
PLAN = (
    ('A', (1858, 1859, 1860), 2),
    ('B', (4, 53, 54), 0), ('B', (7, 49, 50), 0),
    ('restore', (20, 21, 36), 2), ('restore', (22, 23, 38), 2),
    ('restore', (26, 27, 51), 2), ('restore', (30, 31, 62), 2),
    ('restore', (32, 33, 73), 2),
)
PROFILE = {'1': 2440, '2': 725, '3': 224, '4': 102, '5': 20, '8': 8}
WIDTHS = {'4': 26, '5': 2, '6': 18, '7': 53, '8': 96, '9': 213}
KNOWN = {
    'base': '32415e93a50f0fdab5fa144da05977fe34bc8340bf967b91c7f7f0bc312df994',
    'extra': '439ce3544b68e3dffdb0cb4496fbc92330e825592515bc28c95580807c9d232d',
}


class Rejected(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Rejected(message)


def no_duplicates(pairs):
    answer = {}
    for key, value in pairs:
        require(key not in answer, 'duplicate JSON key')
        answer[key] = value
    return answer


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode('ascii')


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def target(r):
    return V <= r < 2 * V


def support(gate):
    require(gate[0] in ('add', 'scale'), 'non-scalar barrier')
    registers = gate[1:3] if gate[0] == 'add' else gate[1:2]
    require(all(type(r) is int and 0 <= r < N for r in registers), 'register domain')
    return frozenset(registers)


def scalar(gate):
    i = 3 if gate[0] == 'add' else 2
    a, b = gate[i:i + 2]
    require(type(a) is int and type(b) is int and b != 0 and a != 0, 'nonzero rational')
    return Fraction(a, b)


def coefficients(gates, registers):
    """Propagate three independent coordinate columns using exact fractions."""
    result = []
    for column in range(len(registers)):
        values = {r: Fraction(k == column) for k, r in enumerate(registers)}
        for gate in gates:
            require(gate[0] == 'add', 'A2 alphabet')
            values[gate[1]] += scalar(gate) * values[gate[2]]
        result.append(tuple(values[r] for r in registers))
    return tuple(result)


def certified_sites(word, plan=PLAN):
    records, occupied = [], set()
    for number, (section, indices, central) in enumerate(plan):
        require(section in ('A', 'B', 'restore'), 'section domain')
        require(len(indices) == 3 and all(type(i) is int for i in indices)
                and 0 <= indices[0] < indices[1] < indices[2] < len(word[section]), 'site indices')
        require(type(central) is int and central in (0, 1, 2), 'central position')
        if section == 'A':
            require(indices[0] >= word['prelude_events'], 'prelude barrier')
        if section == 'B':
            require(not any(indices[0] < w[0] <= indices[-1] for w in word['warps']),
                    'native warp barrier')
        gates = [word[section][i] for i in indices]
        require(all(g[0] == 'add' and len(g) == 6 for g in gates), 'three ADDs')
        touched = frozenset().union(*(support(g) for g in gates))
        require(len(touched) == 3 and len({tuple(g[1:3]) for g in gates}) == 3,
                'three distinct directed A2 edges')
        require(not occupied.intersection(touched), 'overlapping site support')
        occupied.update(touched)
        require(gates[0][-1] == gates[1][-1] == gates[2][-1], 'common ordered frame')
        for i in range(indices[0], indices[-1] + 1):
            if i not in indices:
                require(not support(word[section][i]).intersection(touched), 'intervening dependency')
        replacement = [deepcopy(g) for j, g in reversed(list(enumerate(gates))) if j != central]
        require(coefficients(gates, sorted(touched)) == coefficients(replacement, sorted(touched)),
                'exact three-coordinate identity')
        # Match the credited PR3998 publication's basis order on this old site.
        known = (section, indices, central) == PLAN[0]
        if known:
            for gate in replacement:
                gate[-1] = [42, 82]
        records.append({'section': section, 'indices': list(indices), 'removed_position': central,
                        'known': known, 'support': sorted(touched), 'gates': deepcopy(gates),
                        'replacement': replacement,
                        'crossed_disjoint_events': indices[-1] - indices[0] - 2})
    return records


def ordinary_events(word):
    yield from word['A'][word['prelude_events']:]
    positions = {}
    for k, warp in enumerate(word['warps'], 1):
        positions.setdefault(warp[0], []).append(['warp', warp[1], k])
    for i in range(len(word['B']) + 1):
        yield from positions.get(i, ())
        if i < len(word['B']):
            yield word['B'][i]
    yield from word['restore']


def inverse_cleanup(word):
    """Invert autonomous non-target block, then rename protected buffers."""
    protected = {int(r) for r in word['helper_final']}
    rename = lambda r: N + r if r in protected else r
    answer = []
    for gate in reversed(list(ordinary_events(word))):
        kind, dst = gate[:2]
        if kind == 'warp':
            answer.append(['warp', rename(dst), -gate[2], FULL_BASIS[:]])
        elif not target(dst):
            if kind == 'add':
                require(not target(gate[2]), 'non-target reads target')
                answer.append(['add', rename(dst), rename(gate[2]), -gate[3], gate[4], FULL_BASIS[:]])
            else:
                require(kind == 'scale', 'cleanup alphabet')
                answer.append(['scale', rename(dst), gate[3], gate[2], FULL_BASIS[:]])
    return answer


def reconstruct(word, records):
    edited = deepcopy(word)
    for section in ('A', 'B', 'restore'):
        selected = [r for r in records if r['section'] == section]
        first = {r['indices'][0]: r['replacement'] for r in selected}
        suppressed = {i for r in selected for i in r['indices']}
        edited[section], old_to_new = [], {}
        for i, gate in enumerate(word[section]):
            old_to_new[i] = len(edited[section])
            if i in first:
                edited[section].extend(deepcopy(first[i]))
            elif i not in suppressed:
                edited[section].append(deepcopy(gate))
        old_to_new[len(word[section])] = len(edited[section])
        if section == 'B':
            for warp in edited['warps']:
                warp[0] = old_to_new[warp[0]]
    edited['cleanup'] = inverse_cleanup(edited)
    require(all(edited[k] == word[k] for k in word if k not in ('A', 'B', 'restore', 'cleanup', 'warps')),
            'unrelated field changed')
    require([w[1:] for w in edited['warps']] == [w[1:] for w in word['warps']], 'native record changed')
    return edited


@lru_cache(maxsize=None)
def span(basis):
    result = {0}
    for vector in basis:
        require(type(vector) is int and 0 <= vector < 512, 'binary vector domain')
        result |= {point ^ vector for point in result}
    return frozenset(result)


def rank(points):
    length = len(points)
    require(length > 0 and length & (length - 1) == 0, 'binary subspace cardinality')
    return length.bit_length() - 1


FULL = frozenset(range(512))
ZERO = frozenset([0])


def binary_map(columns):
    require(len(columns) == 9, 'binary map dimension')
    table = []
    for vector in range(512):
        image = 0
        for j, column in enumerate(columns):
            if vector & (1 << j):
                image ^= column
        table.append(image)
    require(len(set(table)) == 512, 'singular binary map')
    return table


def frame_audit(word):
    """Separate point-set trace; receipt includes full states at fixed cuts."""
    live = tuple(r for r in range(N) if r not in word['removed'])
    require(len(live) == 632 and len(word['helper_final']) == 91, 'fixed all-input scope')
    maps = [binary_map(w[2]) for w in word['warps']]
    for w, table in zip(word['warps'], maps):
        require(0 <= w[0] <= len(word['B']), 'warp position')
        old, new = span(tuple(w[3])), span(tuple(w[4]))
        require(rank(old) == len(w[3]) == len(w[4]) == rank(new), 'warp frame bases')
        require(frozenset(table[x] for x in old) == new, 'binary warp frame action')
    start, finish = {}, {}
    for r in live:
        if r < V:
            start[r], finish[r] = span((word['ports'][r],)), FULL
        elif target(r):
            port = word['ports'][r - V]
            start[r], finish[r] = ZERO, frozenset(x for x in range(512) if bin(x & port).count('1') % 2 == 0)
        else:
            start[r], finish[r] = ZERO, FULL
    for r, basis in word['start_extra'].items():
        start[int(r)] = span(tuple(basis))
    for r, basis in word['helper_final'].items():
        finish[int(r)] = span(tuple(basis))
    current, paid, boundaries = start.copy(), Counter(), []
    def snapshot(label):
        boundaries.append((label, tuple(tuple(sorted(current[r])) for r in live)))
    def climb(register, frame):
        require(register in current and current[register] <= frame, 'frame containment')
        delta = rank(frame) - rank(current[register])
        if delta:
            paid[delta] += 1
        current[register] = frame
    def ordinary(gate):
        for r in support(gate):
            if not target(gate[1]) and gate[0] == 'add':
                require(not target(gate[2]), 'non-target reads target')
            climb(r, span(tuple(gate[-1])))
    snapshot('entrance')
    for i, gate in enumerate(word['A']):
        if gate[0] == 'warp':
            require(i < word['prelude_events'], 'A native warp outside prelude')
            _, r, op, before, after = gate
            table = maps[abs(op) - 1]
            if op < 0:
                inverse = [0] * 512
                for x, y in enumerate(table):
                    inverse[y] = x
                table = inverse
            require(current[r] == span(tuple(before)), 'prelude entry')
            require(frozenset(table[x] for x in current[r]) == span(tuple(after)), 'prelude binary image')
            current[r] = span(tuple(after))
        else:
            ordinary(gate)
    snapshot('A_exit')
    levels = {V + int(r): span(tuple(frame)) for r, frame in word['target_levels'].items()}
    require(all(current[r] == levels.get(r, ZERO) for r in range(V, 2 * V)), 'target cut frame')
    for r, frame in zip(word['centers'], word['center_frames']):
        view = span(tuple(frame))
        require(current[r] == view, 'center entry')
        served = {levels.get(g[1], ZERO) for g in word['cut'] if g[2] == r}
        for child in sorted(served, key=lambda points: -rank(points)):
            require(child <= view, 'center descent containment')
            delta = rank(view) - rank(child)
            if delta:
                paid[delta] += 1
            view = child
    at = {}
    for k, warp in enumerate(word['warps']):
        at.setdefault(warp[0], []).append(k)
    for i in range(len(word['B']) + 1):
        for k in at.get(i, ()):
            _, r, _, before, after = word['warps'][k]
            snapshot(('before_native', k))
            require(current[r] == span(tuple(before)), 'native entry')
            current[r] = span(tuple(after))
            snapshot(('after_native', k))
        if i < len(word['B']):
            ordinary(word['B'][i])
    snapshot('B_exit')
    for gate in word['restore']:
        ordinary(gate)
    snapshot('restore_exit')
    for r in live:
        climb(r, finish[r])
    snapshot('terminal')
    widths = Counter(rank(finish[r]) - rank(start[r]) for r in live if r >= 2 * V)
    return ({str(k): v for k, v in sorted(paid.items())},
            {str(k): v for k, v in sorted(widths.items())}, boundaries)


def word_receipt(word):
    profile, widths, boundaries = frame_audit(word)
    require(word['cleanup'] == inverse_cleanup(word), 'literal projected inverse cleanup')
    require(profile == PROFILE and widths == WIDTHS, 'complete fixed recursive bill')
    counts = {s: {op: sum(g[0] == op for g in word[s]) for op in ('add', 'scale', 'warp')}
              for s in ('A', 'B', 'restore', 'cleanup')}
    return {'profile': profile, 'helper_widths': widths, 'lengths': {s: len(word[s]) for s in counts},
            'primitive_counts': counts, 'canonical_word_sha256': sha(word),
            'cleanup_sha256': sha(word['cleanup']), 'native_operations': len(word['warps'])}, boundaries


def rejected(function):
    try:
        function()
    except Rejected:
        return
    raise Rejected('negative control escaped')


def controls(word, records, contracted):
    wrong = deepcopy(word)
    wrong['B'][4][3] *= -1
    rejected(lambda: certified_sites(wrong))
    dependent = deepcopy(word)
    dependent['B'][5][2] = 518
    rejected(lambda: certified_sites(dependent))
    rejected(lambda: certified_sites(word, PLAN + PLAN[:1]))
    crossed = deepcopy(word)
    crossed['warps'][0][0] = 8
    rejected(lambda: certified_sites(crossed))
    framed = deepcopy(word)
    framed['B'][4][-1] = [31]
    rejected(lambda: certified_sites(framed))
    stale = deepcopy(contracted)
    stale['cleanup'] = deepcopy(word['cleanup'])
    rejected(lambda: require(stale['cleanup'] == inverse_cleanup(stale), 'stale inverse cleanup'))
    omitted = deepcopy(records)
    omitted[1]['replacement'] = omitted[1]['replacement'][:1]
    rejected(lambda: require(coefficients(records[1]['gates'], records[1]['support']) ==
                             coefficients(omitted[1]['replacement'], records[1]['support']), 'missing retained gate'))
    return 7


def audit(root):
    expected = json.loads((root / 'data.json').read_bytes(), object_pairs_hook=no_duplicates)
    require(isinstance(expected, dict) and set(expected) == {'schema_version', 'providers'},
            'certificate root schema')
    require(type(expected['schema_version']) is int and expected['schema_version'] == 1,
            'typed certificate schema version')
    require(isinstance(expected['providers'], dict) and set(expected['providers']) == {'base', 'extra'},
            'certificate providers')
    result = {}
    for provider in ('base', 'extra'):
        source = root / 'inputs' / ('BORROW-WORD-' + provider + '.json.gz')
        require(not source.is_symlink(), 'input symlink')
        raw = source.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == PINS[provider], 'source bytes')
        word = json.loads(gzip.decompress(raw), object_pairs_hook=no_duplicates)
        records = certified_sites(word)
        known, changed = reconstruct(word, records[:1]), reconstruct(word, records)
        require(sha(known) == KNOWN[provider], 'published PR3998 word')
        require(expected['providers'][provider]['sites'] == records, 'literal fixed-site receipt')
        receipts, traces = {}, []
        for name, candidate in (('source', word), ('credited_3998', known), ('separated', changed)):
            receipt, trace = word_receipt(candidate)
            reference = {k: v for k, v in expected['providers'][provider]['words'][name].items()
                         if k != 'semantics'}
            require(receipt == reference, 'independent complete word/cleanup/frame receipt: ' + name)
            receipts[name], traces = receipt, traces + [trace]
        require(traces[0] == traces[1] == traces[2], 'all fixed whole-register boundary frames')
        before, after = receipts['credited_3998']['primitive_counts'], receipts['separated']['primitive_counts']
        delta = sum(before[s]['add'] - after[s]['add'] for s in ('A', 'B', 'restore'))
        cleanup_delta = before['cleanup']['add'] - after['cleanup']['add']
        require((delta, cleanup_delta) == (7, 5), 'additional exact scalar record saving')
        negative_count = controls(word, records, changed)
        result[provider] = {'new_sites': 7, 'known_sites': 1, 'inputs': 723,
                            'local_exact_identities': 8, 'boundary_states': len(traces[0]),
                            'negative_controls': negative_count,
                            'forward_add_saving_vs_3998': delta,
                            'cleanup_add_saving_vs_3998': cleanup_delta,
                            'profile': PROFILE, 'helper_widths': WIDTHS}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=HERE, help='explicit package root for private checking')
    args = parser.parse_args()
    result = audit(args.root)
    print('PASS_INDEPENDENT_SEPARATED_A2 ' + json.dumps(result, sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        import sys
        print('FAIL_INDEPENDENT_SEPARATED_A2 ' + str(error), file=sys.stderr)
        raise SystemExit(1)
