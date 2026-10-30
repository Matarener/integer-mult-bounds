#!/usr/bin/env python3
"""Source-bound exchange floor; exact finite corroboration, stdlib only."""
from collections import Counter, deque
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BLOCKS = ((16, 17, 28, 29), (18, 19, 26, 27), (20, 21, 24, 25))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def components(rows):
    """Undirected support components, using a disjoint-set forest."""
    parent = list(range(len(rows)))
    def root(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for i, row in enumerate(rows):
        for j in range(len(rows)):
            if row >> j & 1:
                parent[root(i)] = root(j)
    return len({root(i) for i in range(len(rows))})


def independent_components(rows):
    """Separate adjacency-set traversal."""
    unseen = set(range(len(rows)))
    count = 0
    while unseen:
        stack = [unseen.pop()]
        count += 1
        while stack:
            i = stack.pop()
            neighbors = {j for j in unseen if (rows[i] >> j | rows[j] >> i) & 1}
            unseen -= neighbors
            stack.extend(neighbors)
    return count


def floor(rows):
    return len(rows) - components(rows) + sum(not (row >> i & 1) for i, row in enumerate(rows))


def apply(word, n):
    rows = [1 << i for i in range(n)]
    for d, s in word:
        require(0 <= d < n and 0 <= s < n and d != s, 'invalid ADD')
        rows[d] ^= rows[s]
    return tuple(rows)


def apply_input(word, value):
    for d, s in word:
        value ^= ((value >> s) & 1) << d
    return value


def block_maps():
    gl2 = [(a, b) for a in range(1, 4) for b in range(1, 4) if a != b]
    return [tuple((a[0] << 2, a[1] << 2, b[0], b[1])) for a, b in product(gl2, repeat=2)]


def sum_blocks(blocks):
    return tuple(row << (4 * k) for k, block in enumerate(blocks) for row in block)


def swap_word(pairs):
    return tuple(gate for a, b in pairs for gate in ((a, b), (b, a), (a, b)))


def check_sources():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for item in manifest['files']:
        if item.get('usage') == 'input':
            require(sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'], 'source mismatch')
    return json.loads((ROOT / 'research/g20-isolated-exchange-floor/inputs/CONTROLLER.json').read_text())


def source_endpoint(controller):
    wires = tuple(w for block in BLOCKS for w in block)
    require(len(set(wires)) == 12, 'repeated wire')
    index = {wire: i for i, wire in enumerate(wires)}
    expected = sum_blocks([(4, 8, 1, 2)] * 3)
    for side in ('left', 'right'):
        pairs = []
        for op, a, b in controller['boundaries'][side + '_program']:
            if a not in index and b not in index:
                continue
            require(a in index and b in index and op == 'SWAP', 'source component is not isolated swaps')
            pairs.append((index[a], index[b]))
        require(len(pairs) == 6, 'source swap count')
        require(apply(swap_word(pairs), 12) == expected, 'source word endpoint')
        full = controller['boundaries'][side + '_rows']
        projected = []
        mask = sum(1 << w for w in wires)
        for wire in wires:
            require(full[wire] & ~mask == 0, 'outside source coefficient')
            projected.append(sum(((full[wire] >> w) & 1) << i for i, w in enumerate(wires)))
        require(tuple(projected) == expected, 'source matrix endpoint')
    return expected


def finite_lemma_check():
    identity = (1, 2, 4)
    distances = {identity: 0}
    queue = deque([identity])
    edges = 0
    while queue:
        rows = queue.popleft()
        for d in range(3):
            for s in range(3):
                if d == s:
                    continue
                nxt = list(rows)
                nxt[d] ^= nxt[s]
                nxt = tuple(nxt)
                require(abs(components(nxt) - components(rows)) <= 1, 'component step')
                if components(nxt) < components(rows):
                    require(tuple((row >> i) & 1 for i, row in enumerate(nxt)) ==
                            tuple((row >> i) & 1 for i, row in enumerate(rows)), 'link changes diagonal')
                require(floor(nxt) <= floor(rows) + 1, 'bound step')
                edges += 1
                if nxt not in distances:
                    distances[nxt] = distances[rows] + 1
                    queue.append(nxt)
    require(len(distances) == 168 and edges == 1008, 'GL3 coverage')
    require(all(floor(rows) <= distance for rows, distance in distances.items()), 'distance lower bound')
    return edges


def main():
    source = source_endpoint(check_sources())
    maps = block_maps()
    require(len(set(maps)) == 36, 'local endpoint inventory')
    hist = Counter()
    witnesses = 0
    for blocks in product(maps, repeat=3):
        rows = sum_blocks(blocks)
        count = independent_components(rows)
        require(count == sum(components(block) for block in blocks), 'direct-sum graph count')
        require(all(not (row >> i & 1) for i, row in enumerate(rows)), 'endpoint diagonal')
        lower = 24 - count
        require(lower >= 18, 'exchange floor')
        hist[lower] += 1
        if lower == 18:
            require(all(row.bit_count() == 1 for row in rows), 'equality is not a permutation')
            pairs = [(i, row.bit_length() - 1) for i, row in enumerate(rows) if i < row.bit_length() - 1]
            word = swap_word(pairs)
            require(len(word) == 18 and apply(word, 12) == rows, 'attaining word')
            for i in range(12):
                expected = sum(((row >> i) & 1) << j for j, row in enumerate(rows))
                require(apply_input(word, 1 << i) == expected, 'independent arbitrary-input column')
                require(apply_input(tuple(reversed(word)), expected) == 1 << i, 'inverse column')
            witnesses += 1
    require(dict(hist) == {18: 8, 19: 408, 20: 6936, 21: 39304}, 'floor histogram')
    require(witnesses == 8 and floor(source) == 18, 'sharp source floor')
    edges = finite_lemma_check()
    # Controls distinguish the restricted endpoint family and a real gate defect.
    word = swap_word([(i, i + 2) for i in (0, 1, 4, 5, 8, 9)])
    require(all(apply(word[:i] + word[i + 1:], 12) != source for i in range(18)), 'omission control')
    require(floor(tuple(1 << i for i in range(12))) == 0, 'identity control')
    mixed = sum_blocks([maps[0], maps[0], next(m for m in maps if components(m) == 1)])
    require(floor(mixed) > 18, 'nonmatching-bank control')
    print('PASS_G20_JOINT_EXCHANGE_FLOOR maps=46656 floor=18 attaining=8 GL3_edges=' + str(edges) + ' no_new_kappa')


if __name__ == '__main__':
    main()
