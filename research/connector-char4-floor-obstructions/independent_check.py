"""Independent outside-component and cyclic charge checks from literal states."""
from itertools import combinations, product
from random import Random
from math import comb
import json
import hashlib
from pathlib import Path

HERE = Path(__file__).resolve().parent


def cycle_states(walk, k, start):
    state = list(start)
    states = [tuple(state)]
    for source in walk:
        state[source] = (state[source] + 1) % 4
        states.append(tuple(state))
    if states[0] != states[-1]:
        raise ArithmeticError('cycle not restored')
    return states


def component_stats(states, walk, first, last):
    bad = [0] * len(states[0])
    internal = 0
    for t in range(first, last):
        source = walk[t]
        if states[t][source] == 0:
            internal += 1
        else:
            bad[source] += 1
    if any(count not in (0, 3) for count in bad):
        raise ArithmeticError('source bad arc split between components')
    d = sum(count == 3 for count in bad)
    if d < 1 or last - first != 3 * d + internal:
        raise ArithmeticError('component length formula fails')
    seen = set()
    repeated = []
    for t in range(first, last + 1):
        parity = tuple(value % 2 for value in states[t])
        if parity in seen:
            repeated.append(t)
        seen.add(parity)
    if internal == 0 and d <= 3 and len(repeated) < 2:
        raise ArithmeticError('small component has fewer than two repeats')
    return d, internal, repeated


def inspect(walk, k, origin):
    states = cycle_states(walk, k, origin)
    inside = [all(value <= 1 for value in state) for state in states]
    if not any(inside):
        return 0
    pivot = inside.index(True)
    rotated = walk[pivot:] + walk[:pivot]
    states = cycle_states(rotated, k, states[pivot])
    inside = [all(value <= 1 for value in state) for state in states]
    vertices = [t for t, ok in enumerate(inside) if ok]
    components = [(a, b) for a, b in zip(vertices, vertices[1:]) if b - a > 1]
    stats = [component_stats(states, rotated, a, b) for a, b in components]
    s = len(vertices) - 1
    small = sum(h == 0 and d <= 3 for d, h, repeats in stats)
    internal_outside = sum(h for d, h, repeats in stats)
    if sum(d for d, h, repeats in stats) != k or s != k - internal_outside + len(stats):
        raise ArithmeticError('global edge/component accounting fails')
    global_seen, global_repeats = set(), set()
    for t, state in enumerate(states[:-1]):
        value = tuple(v % 2 for v in state)
        if value in global_seen:
            global_repeats.add(t)
        global_seen.add(value)
    r = len(global_repeats)
    charges = set()
    for d, h, repeats in stats:
        if h == 0 and d <= 3:
            for t in repeats:
                if t in charges or (t < len(walk) and t not in global_repeats):
                    raise ArithmeticError('duplicate or invalid parity charge')
                charges.add(t)
    if len(walk) in charges:
        start, end = components[-1]
        target = tuple(v % 2 for v in states[end])
        choices = [t for t in range(start + 1, end)
                   if tuple(v % 2 for v in states[t]) == target]
        if not choices or choices[0] in charges or choices[0] not in global_repeats:
            raise ArithmeticError('cyclic endpoint charge repair fails')
        charges.remove(end)
        charges.add(choices[0])
    capital_s = min(k, r // 2)
    bound = k + capital_s + (k - capital_s) // 4
    if 2 * small > len(charges) or len(charges) > r or s > bound:
        raise ArithmeticError('component charge/intersection bound fails')
    return 1


def compare_certificate(result):
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    actual = [(r["r"], r["H"], r["upper"]) for r in result["rows"]]
    expected = [(r["r"], r["cube_intersection"], r["mask_upper"]) for r in certificate["cube_control_rows"]]
    if actual != expected or result["max_k19_upper"] != certificate["cube_control_max_mask_upper"]:
        raise ArithmeticError("independent cube table differs from certificate")
    if result["component_cases"] != 21120 or result["nonempty_cases"] != 20976:
        raise ArithmeticError("independent component family incomplete")


def check_catalog():
    rows = json.loads((HERE / "MAXIMIZERS.json").read_text())["canonical_maximizers"]
    if len(rows) != 4:
        raise ArithmeticError("unexpected catalog size")
    words = set()
    for row in rows:
        word = row["walk"]
        if len(word) != 20 or any(word.count(j) != 4 for j in range(5)):
            raise ArithmeticError("invalid catalog word")
        order = list(dict.fromkeys(word))
        if order != list(range(5)) or tuple(word) in words:
            raise ArithmeticError("catalog is noncanonical or duplicated")
        words.add(tuple(word))
        q = cycle_states(word, 5, [0]*5)
        masks = set()
        for a, b in combinations(range(21), 2):
            value = tuple((x+y) % 4 for x, y in zip(q[a], q[b]))
            if max(value) <= 1:
                masks.add(sum(x << j for j, x in enumerate(value)))
        for a in range(21):
            value = tuple(2*x % 4 for x in q[a])
            if max(value) <= 1:
                masks.add(sum(x << j for j, x in enumerate(value)))
        if len(masks) != 29 or [m for m in range(1, 32) if m not in masks] != row["missing"]:
            raise ArithmeticError("independent catalog coverage differs")
        if not all(set(word[t:t+5]) == set(range(5)) for t in range(0, 20, 5)):
            raise ArithmeticError("catalog word lacks four permutation rounds")


def receipt():
    digest = hashlib.sha256()
    names = ('PROOF17.md', 'axis_obstruction.py', 'n4_controls.py', 'CERTIFICATE.json', 'CUBE-SHARPNESS.json', 'README.md', 'SOURCES.json', 'TASK.json', 'VERIFY.json', 'DEPTH2.md', 'MAXIMIZERS.json', 'depth_two.py', 'independent_depth2.c', 'independent_check.py', 'verify.py')
    for name in names:
        digest.update(name.encode() + b"\0" + hashlib.sha256((HERE / name).read_bytes()).digest())
    return digest.hexdigest()


def check_sharpness():
    data = json.loads((HERE / "CUBE-SHARPNESS.json").read_text())
    word = data["word"]
    if len(word) != 72 or any(word.count(j) != 4 for j in range(18)):
        raise ArithmeticError("sharpness word multiplicities")
    states = cycle_states(word, 18, [0]*18)[:-1]
    parity = {tuple(v % 2 for v in q) for q in states}
    inside = [t for t, q in enumerate(states) if all(v <= 1 for v in q)]
    if len(parity) != 72 or len(inside) != 22 or inside != data["valid_boundaries"]:
        raise ArithmeticError("independent sharpness check failed")


def check_seventeen(data):
    """Recompute all base cases and both residual branches without producer code."""
    total, target = 72, 1 << 18
    values = comb(total, 3) - 105 * 70 + min(5 * 105, 22 * 18)
    rows = []
    for repeats in range(21):
        retained = total - repeats
        cap = 18 + repeats // 2 + (18 - repeats // 2) // 4
        xedges, zedges = 210 - 2 * repeats, 263 - 13 * repeats
        xbound = comb(total, 3) - 70 * xedges + min(8 * xedges, 70 * 18)
        zbound = comb(retained, 3) - (retained - 2) * zedges + min(9 * zedges, 108 * 18)
        numerator = 3 * values + (35 - cap) * xbound + (2 * cap - 38) * zbound
        bound = 1 + comb(retained, 2) + numerator // 4
        rows.append({'r': repeats, 'cube_cap': cap, 'V_upper': values,
                     'X_upper': xbound, 'Z_upper': zbound,
                     'incidence_numerator': numerator, 'mask_upper': bound,
                     'excluded': bound < target})
    exceptions = [row['r'] for row in rows if not row['excluded']]
    if exceptions != [2, 4, 5]:
        raise ArithmeticError('independent base cases leave unexpected exceptions')
    residual = []
    for repeats, deletions in ((2, 2), (4, 4), (5, 4)):
        row = rows[repeats]
        vertices, edges = total - deletions, 210 - 2 * repeats - 9 * deletions
        xbound = comb(vertices, 3) - edges * (vertices - 2) + min(8 * edges, 70 * 18)
        cap = row['cube_cap']
        attained = 3 * values + (35 - cap) * xbound + (2 * cap - 38) * row['Z_upper']
        absent = 4 * values + (35 - cap) * row['X_upper'] + (2 * cap - 40) * row['Z_upper']
        pair_bound = 1 + comb(total - repeats, 2)
        yes, no = pair_bound + attained // 4, pair_bound + absent // 4
        if max(yes, no) >= target:
            raise ArithmeticError('independent residual branch does not exclude eighteen')
        residual.append({'r': repeats, 'cube_cap': cap, 'axis_deletions': deletions,
                         'X_vertices': vertices, 'X_edges_lower': edges, 'X_upper': xbound,
                         'attained_H_upper': yes, 'not_attained_H_upper': no})
    tail = 1 + comb(51, 2) + comb(51, 4)
    if tail >= target:
        raise ArithmeticError('independent parity tail does not exclude eighteen')
    expected = {'source_count': 18, 'target_masks_including_zero': target,
                'base_rows': rows, 'base_exceptions': exceptions, 'residual_rows': residual,
                'r_at_least_21_upper': tail}
    if data != expected:
        raise ArithmeticError('seventeen certificate differs from independent arithmetic')
    return {'base_rows': len(rows), 'residual_branches': 2 * len(residual),
            'tail_bound': tail, 'result': 'PASS'}


def main():
    checked = nonempty = 0
    for zero in combinations(range(8), 4):
        walk = [0 if t in zero else 1 for t in range(8)]
        for origin in product(range(4), repeat=2):
            nonempty += inspect(walk, 2, origin)
            checked += 1
    rng = Random(102052)
    for k in (3, 4, 9, 19):
        for _ in range(100):
            walk = [j for j in range(k) for _ in range(4)]
            rng.shuffle(walk)
            q = cycle_states(walk, k, [0] * k)
            for _ in range(50):
                point = rng.choice(q[:-1])
                origin = tuple((rng.randrange(2) - value) % 4 for value in point)
                nonempty += inspect(walk, k, origin)
                checked += 1
    rows = []
    for r in range(76):
        capital_s = min(19, (r + 1) // 2)
        h = 19 + capital_s + (19 - capital_s) // 4
        cube = comb(76, 3) * h // 4 + comb(76, 2) + 1
        n = 76 - r
        parity = 1 + comb(n, 2) + comb(n, 4) if n >= 4 else 1 + comb(n, 2)
        rows.append({'r': r, 'H': h, 'cube_bound': cube, 'parity_bound': parity,
                     'upper': min(cube, parity)})
    if max(row['upper'] for row in rows) >= 1 << 19:
        raise ArithmeticError('nineteen-source exclusion fails')
    result = {'component_cases': checked, 'nonempty_cases': nonempty,
              'max_k19_upper': max(row['upper'] for row in rows), 'rows': rows}
    compare_certificate(result)
    check_catalog()
    check_sharpness()
    data = json.loads((HERE / "CERTIFICATE.json").read_text())
    print("independent_seventeen", json.dumps(check_seventeen(data["eighteen_exclusion"]["arithmetic"]), sort_keys=True))
    print(json.dumps({key: value for key, value in result.items() if key != 'rows'}, sort_keys=True))
    print('receipt_sha256', receipt())
    print('PASS_INDEPENDENT_CHAR4_OBSTRUCTIONS N4<=17')


if __name__ == '__main__':
    main()
