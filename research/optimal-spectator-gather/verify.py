#!/usr/bin/env python3
"""Exact optimization and operator certificates for the new gather.

Produced by Nick Petalas. Apache-2.0. No predecessor verifier is imported.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ZERO = (F(0), F(0))
ONE = (F(1), F(0))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def cycle_cost(permutation):
    seen = set()
    cycles = 0
    for start in range(len(permutation)):
        if start in seen:
            continue
        cycles += 1
        current = start
        for _ in range(len(permutation)):
            if current in seen:
                break
            seen.add(current)
            current = permutation[current]
        need(current == start, 'Cycle decomposition did not close')
    return len(permutation)-cycles


def permutation_oracle(api):
    pair_count = permutation_count = image_count = 0
    for size in range(1, 8):
        minima = {}
        for permutation in permutations(range(size)):
            permutation_count += 1
            moved = sum(i != j for i, j in enumerate(permutation))
            swaps = cycle_cost(permutation)
            images = [0]*(1 << size)
            for mask in range(1 << size):
                if mask:
                    low = mask & -mask
                    images[mask] = images[mask ^ low] | (1 << permutation[low.bit_length()-1])
                key = (mask, images[mask])
                old = minima.get(key, (size+1, size+1))
                minima[key] = (min(old[0], moved), min(old[1], swaps))
                image_count += 1
        for (source, target), best in minima.items():
            missing = (source & ~target).bit_count()
            need(best == (2*missing, missing), 'Independent permutation optimum')
            if source:
                sources = tuple(i for i in range(size) if source >> i & 1)
                targets = tuple(i for i in range(size) if target >> i & 1)
                plan = api.compile_gather(size, 1, sources, targets)
                mapping = plan.mapping()
                need(len(mapping) == best[0], 'Constructed support attains minimum')
                need(len(plan.bit_swaps()) == best[1], 'Constructed word attains minimum')
                need({mapping.get(i, i) for i in sources} == set(targets), 'Exact gather image')
                need(all(mapping.get(mapping.get(i, i), i) == i for i in range(size)),
                     'Involution restores every coordinate')
            pair_count += 1
    return dict(permutations=permutation_count, subset_images=image_count,
                equal_cardinality_pairs=pair_count, maximum_blocks=7)


def ordered_counts(plan):
    """Count the ordered S-to-T completion used for the before fixture."""
    sources = tuple(block*plan.width+j for block in plan.sources
                    for j in range(plan.width))
    targets = tuple(block*plan.width+j for block in plan.targets
                    for j in range(plan.width))
    mapping = dict(zip(sources, targets))
    for a, b in zip(sorted(set(targets)-set(sources)),
                    sorted(set(sources)-set(targets))):
        mapping[a] = b
    support = tuple(sorted(mapping))
    indices = {value: i for i, value in enumerate(support)}
    permutation = tuple(indices[mapping[value]] for value in support)
    moved = sum(a != b for a, b in mapping.items())
    return moved, cycle_cost(permutation)


def multiply(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def gaussian(values, positions, bits):
    out = list(values)
    for position in positions:
        mask = 1 << (bits-1-position)
        for x in range(len(out)):
            if x & mask:
                continue
            ar, ai = out[x]
            br, bi = out[x | mask]
            out[x] = ((ar-ai+br+bi)/2, (ar+ai-br+bi)/2)
            out[x | mask] = ((ar+ai+br-bi)/2, (-ar+ai+br+bi)/2)
    return out


def gaussian_column(column, positions, bits):
    """Independent matrix-entry formula, with no butterfly evaluation."""
    out = [ZERO]*(1 << bits)
    for flips in range(1 << len(positions)):
        row, coefficient = column, ONE
        for j, position in enumerate(positions):
            flip = (flips >> j) & 1
            row ^= flip << (bits-1-position)
            coefficient = multiply(coefficient, (F(1, 2), F(-1 if flip else 1, 2)))
        out[row] = coefficient
    return out


def complete_columns(api):
    columns = 0
    for width, sizes in ((1, range(1, 5)), (2, range(1, 4))):
        for size in sizes:
            bits = width*size
            for count in range(1, size+1):
                choices = tuple(combinations(range(size), count))
                for sources in choices:
                    for targets in choices:
                        plan = api.compile_gather(size, width, sources, targets)
                        for offset in range(width):
                            selected = tuple(i*width+offset for i in sources)
                            placed = tuple(i*width+offset for i in targets)
                            for column in range(1 << bits):
                                values = [ZERO]*(1 << bits)
                                values[column] = ONE
                                actual = api.permute(gaussian(api.permute(values, plan), placed, bits), plan)
                                need(actual == gaussian_column(column, selected, bits),
                                     'Complete exact Gaussian operator column')
                                columns += 1
    return columns


def nonsymmetric_block(values, blocks, width):
    """A nonseparable integer block operator distinguishes every offset."""
    bits = (len(values)-1).bit_length()
    out = list(values)
    for block in blocks:
        shift = bits-(block+1)*width
        mask = ((1 << width)-1) << shift
        for index in range(len(out)):
            if index & mask:
                continue
            indices = tuple(index | (j << shift) for j in range(1 << width))
            incoming = tuple(out[j] for j in indices)
            for row, target in enumerate(indices):
                out[target] = incoming[row] + (row+2)*incoming[(row+1) % len(indices)]
    return out


def general_block_controls(api):
    cases = 0
    for size in range(2, 5):
        for count in range(1, size+1):
            for sources in combinations(range(size), count):
                for targets in combinations(range(size), count):
                    plan = api.compile_gather(size, 2, sources, targets)
                    values = [i*i-3*i+1 for i in range(1 << (2*size))]
                    actual = api.permute(nonsymmetric_block(api.permute(values, plan), targets, 2), plan)
                    need(actual == nonsymmetric_block(values, sources, 2),
                         'Identical general block operator, offsets preserved')
                    cases += 1
    plan = api.compile_gather(3, 1, (0, 1), (1, 2))
    # A distinguished source-to-target assignment cannot be dropped.
    values = list(range(8))
    expected = nonsymmetric_block(nonsymmetric_block(values, (0,), 1), (1,), 1)
    actual = api.permute(nonsymmetric_block(nonsymmetric_block(api.permute(values, plan), (1,), 1), (2,), 1), plan)
    # Equal operators are the positive control; unequal scalar-weighted jobs fail below.
    need(actual == expected, 'Equal-job control')
    unequal = [v*(1+((x >> 2) & 1)) for x, v in enumerate(values)]
    wrong = api.permute([v*(1+((x >> 1) & 1))
                         for x, v in enumerate(api.permute(values, plan))], plan)
    need(wrong != unequal, 'Distinguishable-job mutation must fail')
    return cases


def diagonal(values, bits, salt):
    phases = (ONE, (F(0), F(1)), (F(-1), F(0)), (F(0), F(-1)))
    return [multiply(value, phases[((x*salt) ^ (x >> 1)).bit_count() % 4])
            for x, value in enumerate(values)]


def wrapped(values, api, plan, row_bits, stock, early_diagonal=False):
    bits = plan.blocks*plan.width
    data = api.permute(values, plan)
    rows = 1 << row_bits
    padded = stock*((rows+stock-1)//stock)
    stride = 1 << (bits-row_bits)
    need(rows >= stock and rows <= padded < 2*rows, 'Single bounded whole-row padding')
    records = [data[j*stride:(j+1)*stride] for j in range(rows)]
    records += [[ZERO]*stride for _ in range(padded-rows)]
    records = records[1:] + records[:1]
    targets = tuple(block*plan.width-row_bits for block in plan.targets)
    records = [gaussian(row, targets, bits-row_bits) for row in records]
    records = records[-1:] + records[:-1]
    need(all(v == ZERO for row in records[rows:] for v in row), 'Padded zero return')
    data = [v for row in records[:rows] for v in row]
    if early_diagonal:
        data = diagonal(data, bits, 7)
    return api.permute(data, plan)


def wrapper_fixtures(api):
    # This is PR6070's geometry formula, not a replay of its scientific suite.
    width = guard = 1
    stock = 3
    cases = []
    for count in (1, 2, 3):
        row_bits = width*((stock-1).bit_length()+width-1)//width
        front = width*((2*count*guard+width-1)//width)
        back = width*((count*guard+width-1)//width)
        start = row_bits+front
        targets = tuple(range(start, start+count))
        sources = (0,)+targets[:-1]
        bits = start+count+back
        plan = api.compile_gather(bits, width, sources, targets)
        values = [(F(x % 7-3), F(x % 5-2)) for x in range(1 << bits)]
        inputs = diagonal(values, bits, 3)
        expected = diagonal(gaussian(inputs, sources, bits), bits, 7)
        actual = diagonal(wrapped(inputs, api, plan, row_bits, stock), bits, 7)
        need(actual == expected, 'Dirty complete rows and surrounding coarse diagonals')
        if count == 3:
            need(wrapped(inputs, api, plan, row_bits, stock, True) != expected,
                 'Early coarse diagonal must fail')
        mapping = plan.mapping()
        need(all(mapping.get(i, i) not in sources for i in range(row_bits)),
             'Exposed rows are genuine spectators')
        old_moved, old_swaps = ordered_counts(plan)
        need((old_moved, old_swaps) == (count+1, count), 'Ordered fixture cycle')
        cases.append(dict(h=count, K=width, n=bits, Q=stock,
                          old_moved=old_moved, new_moved=len(mapping),
                          old_minimum_swaps=old_swaps, new_swaps=len(plan.bit_swaps())))
    return cases


def rejection_controls(api):
    bad = [(0, 1, (0,), (0,)), (2, 0, (0,), (1,)),
           (2, 1, (), ()), (2, 1, (0,), (0, 1)),
           (2, 1, (0, 0), (0, 1)), (2, 1, (0,), (2,)),
           (2, 1, (True,), (0,)), (2, 1, {0}, (1,)),
           (257, 1, tuple(range(257)), tuple(range(257))),
           (2, 65536, (0, 1), (0, 1))]
    rejected = 0
    for args in bad:
        try:
            api.compile_gather(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('Malformed or over-capacity gather accepted')
    huge = api.compile_gather(1000000, 1, (0,), (999999,))
    for call in (lambda: api.address(0, huge),
                 lambda: api.address(4, api.compile_gather(2, 1, (0,), (1,))),
                 lambda: api.permute([1], api.compile_gather(2, 1, (0,), (1,)))):
        try:
            call()
        except ValueError:
            rejected += 1
        else:
            raise ValueError('Literal execution boundary accepted')
    return rejected


def encoded_geometry(api):
    logp = 32
    guard = 4*logp+6
    width = 128*guard
    # Q=3 gives R=K; h=3 gives front=back=K in the retained layout.
    blocks = (1 << logp)//(16*width)
    plan = api.compile_gather(blocks, width, (0, 2, 3), (2, 3, 4))
    need(width >= guard+4*logp+10, 'Retained finite K guard')
    need(plan.blocks*width > 9*(2*width)*guard+2*(2*width+1)*logp**2+6*width,
         'Encoded reservoir and suffix capacity')
    need(len(plan.mapping()) == 2*width and len(plan.bit_swaps()) == width,
         'Encoded optimal gather')
    old_moved, old_swaps = ordered_counts(plan)
    need((old_moved, old_swaps) == (4*width, 3*width), 'Encoded ordered cycles')
    return dict(log2p=logp, K=width, G=guard, Q=3, h=3,
                old_moved=old_moved, new_moved=len(plan.mapping()),
                old_minimum_swaps=old_swaps, new_swaps=len(plan.bit_swaps()),
                scope='Encoded aligned layout only; no production call or tensor execution')


def verify(api):
    return dict(status='PASS_OPTIMAL_SPECTATOR_GATHER',
                claim_type='scoped proof with finite exact corroboration',
                optimum='moved=2*K*(h-c); coordinate_swaps=K*(h-c)',
                oracle=permutation_oracle(api), gaussian_basis_columns=complete_columns(api),
                general_block_fixtures=general_block_controls(api),
                spectator_row_fixtures=wrapper_fixtures(api),
                encoded_geometry=encoded_geometry(api),
                malformed_or_capacity_rejections=rejection_controls(api),
                semantic_rejections=['distinguishable kernels', 'early coarse diagonal'],
                new_kappa=False)


def main():
    # A fresh read namespace prevents preexisting bytecode from replacing source.
    with tempfile.TemporaryDirectory(prefix='optimal-gather-bytecode-') as cache:
        sys.pycache_prefix = cache
        sys.path.insert(0, str(HERE))
        import gather
        result = verify(gather)
    result['package_sha256'] = {p.name: sha256(p.read_bytes()).hexdigest()
                                for p in sorted(HERE.iterdir()) if p.is_file()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
