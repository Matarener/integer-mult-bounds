"""Literal scaled replay for all first-prefix reads. Apache-2.0."""

from fractions import Fraction

from engine import WIDTH, ZERO, digest, monomial, need, pair, plan, wrapper

COLLECTOR = ('D31', 'D30', 'D29', 'D28', 'D27', 'Q7')


def baseline(word):
    reserve = {name: 4 if name.startswith('Y') else 2 if name.startswith('N') else 0
               for name in word['initial_frames']}
    margins = []
    for event, row in enumerate(word['program'][:2025]):
        if row[0] == 'add':
            p, q = Fraction(row[3]).as_integer_ratio()
            need(abs(p) in (1, 2) and q in (1, 2, 4), 'baseline coefficient alphabet')
            margin = reserve[row[2]] + 2 * (abs(p).bit_length() - q.bit_length())
            need(margin >= 0, 'baseline quarter/half admission')
            reserve[row[1]] = min(reserve[row[1]], margin)
            margins.append([event, margin])
    need(len(margins) == 1038, 'baseline ADD coverage')
    return {'ADDs_checked': len(margins), 'reserve_ledger_sha256': digest(margins),
            'minimum_pi_reserve': min(r for _, r in margins)}


def schedule(word):
    coefficient = {n: Fraction(n == 'Y27') - Fraction(n == 'Y26')
                   for n in word['initial_frames']}
    frames = dict(word['initial_frames'])
    need(frames['Y27'] == frames['Y26'] == [], 'two-source initial frame')
    active, reads = [], []
    for event, row in enumerate(word['program'][:2025]):
        op, dst = row[:2]
        if op == 'transport':
            need(frames[dst] == row[2], 'chronological transport frame')
            frames[dst] = row[3]
            if coefficient[dst]:
                active.append((event, row, coefficient[dst]))
        elif op == 'add':
            need(frames[dst] == frames[row[2]] == row[4], 'common ADD frame')
            if coefficient[row[2]]:
                need(row[2] in ('Y27', 'Y26') and dst.startswith('D') and
                     abs(Fraction(row[3])) == Fraction(1, 4), 'active quarter source')
                active.append((event, row, coefficient[dst]))
                reads.append(event)
            coefficient[dst] += Fraction(row[3]) * coefficient[row[2]]
        elif op == 'sign':
            need(coefficient[dst] == 0 and frames[dst] == row[3],
                 'inactive signed frame')
            coefficient[dst] *= Fraction(row[2])
        else:
            raise ValueError('unexpected prefix opcode')
    need(len(active) == 38 and len(reads) == 12, 'active full-prefix coverage')
    need(all(coefficient[n] == 0 for n in COLLECTOR), 'ideal collector cancellation')
    return active, reads


def prepared(recipes, active):
    result = {}
    for event, row, _ in active:
        if row[0] == 'transport':
            recipe = recipes[event]
            result[event] = {**recipe, 'left_plan': plan(recipe['left']),
                             'right_plan': plan(recipe['right'])}
    need(len(result) == 26, 'active native count')
    return result


def transport(vector, recipe, event, dst):
    out = wrapper(vector, recipe['right_plan'])
    checks = []
    for bit in range(recipe['rank']):
        for x in range(WIDTH):
            if not x & (1 << bit):
                out[x], out[x | (1 << bit)] = pair(out[x], out[x | (1 << bit)])
        checks.append((f'{event}:C{bit}:{dst}', out[:]))
    return wrapper(out, recipe['left_plan']), checks


def replay(y, active, recipes):
    need(len(y) == WIDTH, 'source width')
    state = {'Y27': [(4 * a, 4 * b) for a, b in y],
             'Y26': [(-4 * a, -4 * b) for a, b in y]}
    checks = []
    for event, row, _ in active:
        op, dst = row[:2]
        if op == 'transport':
            vector, new = transport(state[dst], recipes[event], event, dst)
            state[dst] = vector
            checks.extend(new)
        else:
            p, q = Fraction(row[3]).as_integer_ratio()
            source = state[row[2]]
            need(all(p * v % q == 0 for z in source for v in z), 'scaled quarter')
            addend = [(p * a // q, p * b // q) for a, b in source]
            checks.append((f'{event}:addend:{dst}', addend))
            before = state.get(dst, [ZERO] * WIDTH)
            state[dst] = [(a + c, b + d) for (a, b), (c, d)
                          in zip(before, addend, strict=True)]
            if event in (1129, 1329, 1492):
                need(all(z == ZERO for z in state[dst]), 'actual correlated cancellation')
    need(all(all(z == ZERO for z in state.get(n, [])) for n in COLLECTOR),
         'literal ideal collector endpoint')
    need(len(checks) <= 64, 'checkpoint capacity')
    return checks, state


def first_failure(checks):
    for key, vector in checks:
        for address, z in enumerate(vector):
            if z[0] % 4 or z[1] % 4:
                return {'checkpoint': key, 'address': address, 'scaled_value': list(z)}
    return None


def matrix(active, recipes):
    keys, rows = [], []
    endpoints = []
    for mask in range(WIDTH):
        checks, state = replay(monomial(mask, mask.bit_count()), active, recipes)
        if mask == 0:
            keys = [key for key, _ in checks]
            rows = [[0, 0, 0, 0] for _ in range(len(keys) * WIDTH)]
        need([key for key, _ in checks] == keys, 'stable checkpoint order')
        bit = 1 << mask
        for cut, (_, vector) in enumerate(checks):
            for x, (a, b) in enumerate(vector):
                row = rows[cut * WIDTH + x]
                for index, flag in enumerate((a & 1, (a >> 1) & 1,
                                              b & 1, (b >> 1) & 1)):
                    if flag:
                        row[index] |= bit
        endpoints.append(digest({n: state.get(n, []) for n in COLLECTOR}))
    need(len(rows) <= 32768, 'working Gaussian row capacity')
    kept, filtered, zero = [], [], []
    for cut, key in enumerate(keys):
        block = rows[cut * WIDTH:(cut + 1) * WIDTH]
        if any(any(row) for row in block):
            kept.append(key)
            filtered.extend(block)
        else:
            zero.append(key)
    need(len(filtered) <= 20000, 'retained Gaussian row capacity')
    return kept, filtered, digest(endpoints), zero
