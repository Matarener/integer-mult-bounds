"""Integer arithmetic and finite controls for the eighteen-source obstruction.

The written proof supplies the graph and cube bounds. This module evaluates
all parity-repeat cases and checks literal-run axis replacements independently
of the arithmetic. It uses no external solver or local package dependency.
"""
from itertools import combinations
import json
from math import comb

K = 18
LENGTH = 72
TARGET = 1 << K


def independent_triples(vertices, edges, degree, wedge_cap):
    if not (3 <= vertices <= LENGTH and 0 <= edges <= comb(vertices, 2)):
        raise ValueError('invalid graph-count arguments')
    if degree < 1 or wedge_cap < 0:
        raise ValueError('invalid degree or wedge cap')
    wedges = min((degree-1)*edges, wedge_cap)
    return comb(vertices, 3)-edges*(vertices-2)+wedges


def cube_cap(repeats):
    if not 0 <= repeats <= 20:
        raise ValueError('repeat row outside the bounded table')
    small = min(K, repeats//2)
    return K+small+(K-small)//4


def incidence_numerator(values, components, parities, cap, axis_cost):
    if axis_cost not in (3, 4):
        raise ValueError('unsupported component cost')
    component_coefficient = 2*K-cap-axis_cost+2
    parity_coefficient = 2*cap-2*K-2
    if min(values, components, parities, component_coefficient, parity_coefficient) < 0:
        raise ValueError('negative incidence parameter')
    return axis_cost*values+component_coefficient*components+parity_coefficient*parities


def base_rows():
    values = independent_triples(LENGTH, 6*K-3, 6, 22*K)
    rows = []
    for repeats in range(21):
        n = LENGTH-repeats
        cap = cube_cap(repeats)
        x_edges = max(0, 12*K-6-2*repeats)
        z_edges = max(0, 15*K-7-13*repeats)
        components = independent_triples(LENGTH, x_edges, 9, 70*K)
        parities = independent_triples(n, z_edges, 10, 108*K)
        numerator = incidence_numerator(values, components, parities, cap, 3)
        upper = 1+comb(n, 2)+numerator//4
        rows.append({'r': repeats, 'cube_cap': cap, 'V_upper': values,
                     'X_upper': components, 'Z_upper': parities,
                     'incidence_numerator': numerator, 'mask_upper': upper,
                     'excluded': upper < TARGET})
    return rows


def residual_rows(rows):
    by_repeat = {row['r']: row for row in rows}
    result = []
    for repeats, deletions in ((2, 2), (4, 4), (5, 4)):
        base = by_repeat[repeats]
        n = LENGTH-repeats
        cap = base['cube_cap']
        vertices = LENGTH-deletions
        edges = 12*K-6-2*repeats-9*deletions
        components = independent_triples(vertices, edges, 9, 70*K)
        attained = incidence_numerator(base['V_upper'], components, base['Z_upper'], cap, 3)
        absent = incidence_numerator(base['V_upper'], base['X_upper'], base['Z_upper'], cap-1, 4)
        pair_count = 1+comb(n, 2)
        result.append({'r': repeats, 'cube_cap': cap, 'axis_deletions': deletions,
                       'X_vertices': vertices, 'X_edges_lower': edges,
                       'X_upper': components, 'attained_H_upper': pair_count+attained//4,
                       'not_attained_H_upper': pair_count+absent//4})
    return result


def evaluate():
    rows = base_rows()
    residual = residual_rows(rows)
    exceptions = [row['r'] for row in rows if not row['excluded']]
    if exceptions != [2, 4, 5]:
        raise RuntimeError('unexpected residual cases')
    for row in residual:
        if max(row['attained_H_upper'], row['not_attained_H_upper']) >= TARGET:
            raise RuntimeError('residual case was not excluded')
    tail = 1+comb(51, 2)+comb(51, 4)
    if tail >= TARGET:
        raise RuntimeError('parity tail was not excluded')
    return {'source_count': K, 'target_masks_including_zero': TARGET,
            'base_rows': rows, 'base_exceptions': exceptions,
            'residual_rows': residual, 'r_at_least_21_upper': tail}


def inspect_axis_word(word, replacements):
    if len(word) != LENGTH or any(word.count(j) != 4 for j in range(K)):
        raise ValueError('invalid control word')
    vectors, parities, current = [], [], [0]*K
    for source in word:
        vectors.append(tuple(current))
        parities.append(sum((x % 2) << j for j, x in enumerate(current)))
        current[source] = (current[source]+1) % 4
    if any(current):
        raise RuntimeError('control word did not restore')
    for later, (earlier, source) in replacements.items():
        if not 0 <= earlier < later < LENGTH:
            raise ValueError('invalid replacement indices')
        difference = tuple((x-y) % 4 for x, y in zip(vectors[later], vectors[earlier]))
        if difference != tuple(2 if j == source else 0 for j in range(K)):
            raise RuntimeError('axis difference failed')
    prefix_parities = set(parities)
    checked = 0
    for triple in combinations(range(LENGTH), 3):
        parity = parities[triple[0]] ^ parities[triple[1]] ^ parities[triple[2]]
        if parity in prefix_parities:
            continue
        for later in triple:
            if later not in replacements:
                continue
            earlier, _ = replacements[later]
            if earlier in triple:
                raise RuntimeError('good triple replacement collided')
            changed = tuple(sorted(earlier if t == later else t for t in triple))
            if not changed[::-1] < triple[::-1]:
                raise RuntimeError('colex did not decrease')
            after = parities[changed[0]] ^ parities[changed[1]] ^ parities[changed[2]]
            if after != parity:
                raise RuntimeError('triple parity changed')
            checked += 1
    return checked


def axis_controls():
    checked = 0
    state = 1020426
    for case in range(100):
        word = [0, 1]+[j for j in range(2, K) for _ in range(4)]
        for i in range(len(word)-1, 0, -1):
            state = (6364136223846793005*state+1442695040888963407) & ((1 << 64)-1)
            other = state % (i+1)
            word[i], word[other] = word[other], word[i]
        at = 5+(case % 50)
        word[at:at] = [0]*3
        word += [1]*3
        replacements = {at+2: (at, 0), at+3: (at+1, 0), 70: (0, 1), 71: (69, 1)}
        checked += inspect_axis_word(word, replacements)
    return {'words': 100, 'axis_pairs': 400, 'good_triple_moves': checked}


def short_component_controls():
    result = []
    for length in (6, 4):
        repeats = []
        for chosen in combinations(range(length), 3):
            word = [0 if i in chosen else 1 for i in range(length)]
            parity, seen, count = 0, {0}, 0
            for source in word:
                parity ^= 1 << source
                count += parity in seen
                seen.add(parity)
            repeats.append(count)
        result.append({'multiplicities': [3, length-3], 'words': len(repeats),
                       'min_local_repeats': min(repeats)})
    if [row['min_local_repeats'] for row in result] != [3, 1]:
        raise RuntimeError('short-component repeat bound failed')
    return result


def calibrate():
    return {'axis_replacements': axis_controls(), 'short_components': short_component_controls()}


if __name__ == '__main__':
    print(json.dumps({'arithmetic': evaluate(), 'controls': calibrate()}, indent=2, sort_keys=True))
