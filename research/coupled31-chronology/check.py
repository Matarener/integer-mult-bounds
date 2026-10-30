"""Check the prefix lemmas and complete endpoint controls.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product
import json
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return tuple(1 << i for i in range(n))


def add(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def mul(a, b):
    out = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length()-1]
            row ^= bit
        out.append(value)
    return tuple(out)


def basis(rows):
    out = {}
    for value in rows:
        while value:
            pivot = value.bit_length()-1
            if pivot not in out:
                out[pivot] = value
                break
            value ^= out[pivot]
    return out


def rank(rows):
    return len(basis(rows))


def trans(a):
    return tuple(sum(((a[j] >> i) & 1) << j for j in range(len(a)))
                 for i in range(len(a)))


def polynomial_mul(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        b >>= 1
    return out


def determinant_x(s):
    """Compute det(I+xS) over F2[x] by subsets of columns."""
    n = len(s)
    dp = {0: 1}
    for i in range(n):
        new = {}
        for mask, value in dp.items():
            for j in range(n):
                if not (mask >> j) & 1:
                    entry = int(i == j) ^ (2*((s[i] >> j) & 1))
                    target = mask | (1 << j)
                    new[target] = new.get(target, 0) ^ polynomial_mul(value, entry)
        dp = new
    return dp[(1 << n)-1]


def prefix_controls():
    rng = random.Random(310526)
    cases = noncommuting = 0
    for d in range(2, 8):
        for repeat in range(8):
            stages = []
            for i in range(d):
                a = [0]*d
                a[i] = (1 << i) | (rng.randrange(1 << (d-i-1)) << (i+1))
                stages.append(tuple(a))
            s = (0,)*d
            expected = 1
            for a in stages:
                require(mul(a, a) == a and rank(a) == 1, 'prefix idempotent')
                require(mul(a, s) == (0,)*d, 'prefix annihilation')
                noncommuting += mul(s, a) != (0,)*d
                s = add(s, a)
                expected = polynomial_mul(expected, 3)
                require(determinant_x(s) == expected, 'formal determinant identity')
                cases += 1
            require(rank(s) == d, 'full prefix is invertible')
            require(all(mul(a, s) != (0,)*d for a in stages), 'next call must fail')
    require(noncommuting > 0, 'noncommuting prefix controls')
    return {'formal_prefix_updates': cases, 'noncommuting_updates': noncommuting}


def solve_binary(rows):
    pivots = {}
    for coefficients, value in rows:
        while coefficients:
            p = coefficients.bit_length()-1
            if p not in pivots:
                pivots[p] = (coefficients, value)
                break
            c, v = pivots[p]
            coefficients ^= c
            value ^= v
        if not coefficients and value:
            return None
    answer = 0
    for p in sorted(pivots):
        c, v = pivots[p]
        if v ^ ((c & answer).bit_count() & 1):
            answer |= 1 << p
    return answer


def signature_dimension(ms, d):
    if not ms:
        return 0
    h = len(ms[0])
    columns = []
    for m in ms[1:]:
        for c in range(d):
            columns.append(sum((((m[t] ^ ms[0][t]) >> c) & 1) << t
                               for t in range(h)))
    return rank(columns)


def drop_controls():
    rng = random.Random(73131)
    d = 2
    projections = [tuple(a) for a in product(range(4), repeat=2)
                   if mul(a, a) == tuple(a)]
    proper = [a for a in projections if rank(a) == 1]
    checked = solved = drops = rejected = 0
    for h in (1, 2, 3):
        for g in (3, 5, 7):
            for repeat in range(300):
                a = rng.choice(proper)
                ps = [rng.choice(((0, 0), add(eye(d), a)))]
                ps += [rng.choice(projections) for _ in range(g-1)]
                ms = [tuple(rng.randrange(4) for _ in range(h)) for _ in range(g)]
                c_rows = []
                for row in range(d):
                    equations = []
                    for k in range(1, g):
                        ap = mul(a, ps[k])
                        for col in range(d):
                            lhs = (1 << col) | sum(((ms[k][t] >> col) & 1) << (d+t)
                                                  for t in range(h))
                            equations.append((lhs, (ap[row] >> col) & 1))
                    solution = solve_binary(equations)
                    if solution is None:
                        break
                    c_rows.append(solution >> d)
                checked += 1
                if len(c_rows) != d:
                    rejected += 1
                    continue
                solved += 1
                s = (0,)*d
                for p in ps:
                    s = add(s, p)
                untouched = [k for k in range(1, g) if ps[k] == (0,)*d]
                if untouched and mul(a, s) != (0,)*d:
                    require(signature_dimension([ms[k] for k in untouched], d)
                            < signature_dimension(ms, d), 'strict signature dimension drop')
                    drops += 1
    require(drops > 20 and rejected > 0, 'nonvacuous dimension controls')
    return {'local_systems': checked, 'consistent': solved,
            'inconsistent': rejected, 'strict_drop_instances': drops}


def static_witness():
    """Reproduce the binary PR5681 fixture from its written formula."""
    d, g, n = 4, 31, 128
    labels = [0] + [v for v in range(1, 16) for _ in range(2)]
    u = sum(value << ((j+1)*d) for j, value in enumerate(labels))
    e = tuple(u if (u >> i) & 1 else 0 for i in range(n))
    fs, gs = [], []
    for axis in range(d):
        f, z = [0]*n, [0]*n
        for j in range(1, g+1):
            f[axis] ^= 1 << (j*d+axis)
            z[j*d+axis] ^= 1 << axis
        fs.append(tuple(f))
        gs.append(tuple(z))
    queries = [add(fs[0], e), add(gs[1], e)]
    queries += [add(fs[i], gs[(i+1) % d]) for i in range(1, d)]
    k = (0,)*n
    for z in queries:
        require(rank(z) == 2 and mul(z, z) == (0,)*n, 'static rank and square')
        k = add(k, z)
    a = rank([row for z in queries for row in trans(z)])-2*d
    b = rank([row for z in queries for row in z])-2*d
    require(rank(k) == 2*d and a == b == 1, 'static excess dimensions')
    require(g > 3*b+2, 'new chronological rejection')
    return {'leaves': g, 'd': d, 'thin_maps': len(queries), 'thin_rank': 10,
            'extra_image_dimension': a, 'extra_row_dimension': b,
            'static_checks_pass': True, 'chronology_bound': 3*b+2,
            'chronology_rejected': True}


def commuting_word(g, q):
    d, n = 2*q, 2*q*(g+1)
    calls = []
    for j in range(g):
        for half in range(2):
            p, r = [0]*n, [0]*n
            for c in range(half*q, (half+1)*q):
                i, k = c, (j+1)*d+c
                p[i], p[k] = 1 << i, 1 << k
                r[i] = r[k] = (1 << i) | (1 << k)
            calls.append({'stage': j, 'p': p, 'r': r})
        if j % 2 == 0:
            leaves = [j+1] + ([j+2] if j+1 < g else [])
            z = [0]*n
            for leaf in leaves:
                for c in range(d):
                    z[c] ^= 1 << (leaf*d+c)
                    z[leaf*d+c] ^= 1 << c
            if g % 2 == 0 and j == 0:
                for c in range(d):
                    z[c] ^= 1 << c
            calls.append({'stage': g, 'p': [0]*n, 'r': z})
    return {'g': g, 'q': q, 'order': list(range(len(calls))), 'calls': calls}


def check_contract(word):
    g, q = word['g'], word['q']
    d, n = 2*q, 2*q*(g+1)
    calls = word['calls']
    require(sorted(word['order']) == list(range(len(calls))), 'call order permutation')
    projections = [[] for _ in range(g)]
    for call in calls:
        j = call['stage']
        p, r = tuple(call['p']), tuple(call['r'])
        require(len(p) == len(r) == n and all(0 <= x < 1 << n for x in p+r), 'matrix shape')
        if j == g:
            require(not any(p), 'thin stage-free contract')
            continue
        require(0 <= j < g, 'stage range')
        projections[j].append(p)
        require(mul(p, p) == p and rank(p) == d, 'full projection rank')
        require(mul(p, r) == mul(r, p) == r and rank(r) == q, 'full query compatibility')
        t = [0]*n
        for c in range(d):
            t[c] = t[(j+1)*d+c] = (1 << c) | (1 << ((j+1)*d+c))
        require(mul(p, t) == r, 'prescribed stage query')
    for j, pair in enumerate(projections):
        require(len(pair) == 2, 'two full stage halves')
        target = tuple((1 << i) if i < d or (j+1)*d <= i < (j+2)*d else 0
                       for i in range(n))
        require(add(*pair) == target and not any(mul(*pair)), 'orthogonal resolution')


def laurent_endpoint(word):
    """Check every Laurent coefficient after exact diagonal normalization."""
    check_contract(word)
    g = word['g']
    n = len(word['calls'][0]['p'])
    degrees = [[0]*g for _ in range(n)]
    terms = set()
    contributions = 0
    for index in word['order']:
        call = word['calls'][index]
        j, p, r = call['stage'], call['p'], call['r']
        for i, row in enumerate(r):
            for k in range(n):
                if (row >> k) & 1:
                    exponent = tuple(y-x for x, y in zip(degrees[i], degrees[k]))
                    key = (i, k, exponent)
                    if key in terms:
                        terms.remove(key)
                    else:
                        terms.add(key)
                    contributions += 1
        if j < g:
            for i, row in enumerate(p):
                require(row in (0, 1 << i), 'diagonal full-call entry')
                degrees[i][j] += int(bool(row))
    d = 2*word['q']
    for i, degree in enumerate(degrees):
        require(degree == [int(i < d or i//d == j+1) for j in range(g)], 'pure stage endpoint')
    require(terms == {(i, i, (0,)*g) for i in range(n)}, 'complete Laurent endpoint')
    return {'fields': n, 'full_calls': 2*g, 'thin_maps': len(word['calls'])-2*g,
            'thin_rank': sum(rank(c['r']) for c in word['calls'] if c['stage'] == g),
            'query_entry_contributions': contributions, 'final_coefficients': len(terms)}


def gf4_mul(a, b):
    value = 0
    for i in range(2):
        if (b >> i) & 1:
            value ^= a << i
    return value ^ (7 if value & 4 else 0)


def apply_binary(a, b):
    n = len(a)
    out = []
    for bits in a:
        row = [0]*n
        while bits:
            bit = bits & -bits
            source = b[bit.bit_length()-1]
            row = [x ^ y for x, y in zip(row, source)]
            bits ^= bit
        out.append(row)
    return out


def grid_endpoint(word):
    """Three distinct F4 points decide degree-at-most-two stage polynomials."""
    check_contract(word)
    g = word['g']
    n = len(word['calls'][0]['p'])
    d = 2*word['q']
    count = 0
    for values in product((0, 1, 2), repeat=g):
        pure = [[int(i == j) for j in range(n)] for i in range(n)]
        derivative = [[0]*n for _ in range(n)]
        for index in word['order']:
            call = word['calls'][index]
            j, p, r = call['stage'], call['p'], call['r']
            rb = apply_binary(r, pure)
            if j == g:
                derivative = [[a ^ b for a, b in zip(x, y)] for x, y in zip(derivative, rb)]
            else:
                pe, pb = apply_binary(p, derivative), apply_binary(p, pure)
                derivative = [[a ^ gf4_mul(values[j] ^ 1, b) ^ gf4_mul(values[j], c)
                               for a, b, c in zip(x, y, z)] for x, y, z in zip(derivative, pe, rb)]
                pure = [[a ^ gf4_mul(values[j] ^ 1, b) for a, b in zip(x, y)]
                        for x, y in zip(pure, pb)]
        for i in range(n):
            value = 1
            for j in range(g):
                if i < d or i//d == j+1:
                    value = gf4_mul(value, values[j])
            expected = [value if i == k else 0 for k in range(n)]
            require(pure[i] == derivative[i] == expected, 'full F4 grid endpoint')
        count += 1
    return count


def endpoint_controls():
    grid_cases = 0
    for g in range(1, 4):
        word = commuting_word(g, 1)
        laurent_endpoint(word)
        grid_cases += grid_endpoint(word)
    old = json.loads((ROOT/'sources/escape-word.json').read_text())
    old.update(g=3, q=1)
    grid_cases += grid_endpoint(old)
    # D^2+D vanishes at both binary points, but not at the third grid point.
    require(all(gf4_mul(x, x) ^ x == 0 for x in (0, 1)), 'binary alias control')
    require(gf4_mul(2, 2) ^ 2 != 0, 'extension point rejects alias')
    word = json.loads((ROOT/'WORD31.json').read_text())
    receipt = laurent_endpoint(word)
    rejected = 0
    for kind in ('deleted', 'moved'):
        broken = json.loads(json.dumps(word))
        thin = next(i for i, c in enumerate(broken['calls']) if c['stage'] == word['g'])
        if kind == 'deleted':
            broken['calls'][thin]['r'] = [0]*len(broken['calls'][thin]['r'])
        else:
            broken['order'].remove(thin)
            broken['order'].append(thin)
        try:
            laurent_endpoint(broken)
        except ValueError:
            rejected += 1
        else:
            raise ValueError('damaged endpoint accepted')
    require(rejected == 2, 'endpoint controls')
    return {'full_grid_assignments': grid_cases, 'binary_alias_rejected': True,
            'damaged_words_rejected': rejected, 'long_word': receipt}


def run():
    return {'prefix': prefix_controls(), 'dimension_drop': drop_controls(),
            'static_target': static_witness(), 'endpoints': endpoint_controls()}
