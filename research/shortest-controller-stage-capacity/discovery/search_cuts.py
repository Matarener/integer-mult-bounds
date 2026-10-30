"""Search exact subspace cuts for the formal common-stage caller.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from itertools import combinations
import json
from pathlib import Path
import random


def basis(values):
    pivots = {}
    for x in values:
        for p in sorted(pivots, reverse=True):
            if (x >> p) & 1:
                x ^= pivots[p]
        if x:
            p = x.bit_length()-1
            for j in pivots:
                if (pivots[j] >> p) & 1:
                    pivots[j] ^= x
            pivots[p] = x
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def apply(matrix, x):
    y = 0
    for k, column in enumerate(matrix):
        if (x >> k) & 1:
            y ^= column
    return y


def cut(matrix, u):
    return len(basis((*u, *(apply(matrix, x) for x in u))))-len(u)


def check(d, q, u, max_degree=8):
    dim = len(d)
    doubled = (*u, *(x << dim for x in u))
    images = [apply(d, x) for x in u]
    images += [apply(d, apply(q, x)) ^ (apply(d, x) << dim) for x in u]
    full = len(basis((*doubled, *images)))-2*len(u)
    power = [1 << i for i in range(dim)]
    targets = []
    for _ in range(max_degree+1):
        targets.append(cut([apply(q, x) for x in power], u))
        power = [apply(d, x) for x in power]
    return full, targets


def search(half, rounds, seed):
    rng = random.Random(seed)
    dim = 2*half
    q = [1 << i for i in range(half)] + [(1 << i) ^ (1 << (i+half)) for i in range(half)]
    if dim == 6:
        subspaces = sorted({basis(c) for c in combinations(range(1, 1 << dim), 3) if len(basis(c)) == 3})
    else:
        subspaces = sorted({basis(rng.randrange(1, 1 << dim) for _ in range(half)) for _ in range(2000)})
        subspaces = [u for u in subspaces if len(u) == half]
    best, witness = 0, None
    checked = 0
    for _ in range(rounds):
        while True:
            a = [rng.randrange(1 << half) for _ in range(half)]
            if len(basis(a)) == half:
                break
        b = [rng.randrange(1 << half) for _ in range(half)]
        d = a + [x ^ (y << half) for x, y in zip(b, a)]
        for u in subspaces:
            full, targets = check(d, q, u, 4)
            checked += 1
            # The six-field balanced candidate uses seven full calls.
            gap = 4*targets[2]+2*targets[3]-7*full
            if gap > best:
                best, witness = gap, {'d': d, 'q': q, 'u': list(u), 'full_cut': full, 'target_cuts': targets}
                print(json.dumps({'new_gap': best, 'witness': witness}), flush=True)
                if gap > 0:
                    return {'checked': checked, 'seed': seed, 'half': half, 'best_gap': best, 'witness': witness}
    return {'checked': checked, 'seed': seed, 'half': half, 'best_gap': best, 'witness': witness}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--half', type=int, default=3)
    parser.add_argument('--rounds', type=int, default=100)
    parser.add_argument('--seed', type=int, default=5593)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = search(args.half, args.rounds, args.seed)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
