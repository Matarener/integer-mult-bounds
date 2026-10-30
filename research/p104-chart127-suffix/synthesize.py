"""Exact dyadic elimination for the chart-127 block. Apache-2.0.

Produced by Nick Petalas. Classical sparse elimination and row sharing;
CubeJerry's PR6116 motivates applying whole-block synthesis beyond the prefix.
"""
from collections import Counter
from fractions import Fraction

START, STOP, FRAME = 17461, 20431, 127
MAX_ROLES, MAX_EVENTS, MAX_SHARING = 799, 26000, 2000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unit(q):
    n, d = abs(q.numerator), q.denominator
    return n > 0 and n & (n - 1) == 0 and d & (d - 1) == 0


def roles_of(program):
    return sorted({e[1] for e in program} |
                  {e[2] for e in program if e[0] == 'ADD'})


def add_row(rows, destination, source, q):
    require(destination != source, 'Distinct row operands')
    for column, value in rows[source].items():
        total = rows[destination].get(column, 0) + q * value
        if total:
            rows[destination][column] = total
        else:
            rows[destination].pop(column, None)


def matrix(program):
    require(0 < len(program) <= MAX_EVENTS, 'Bounded nonempty scalar block')
    roles = roles_of(program)
    require(len(roles) <= MAX_ROLES, 'Bounded roles')
    rows = {r: {r: Fraction(1)} for r in roles}
    for e in program:
        require(e[0] in ('ADD', 'SCALE') and e[-1] == FRAME,
                'Fixed scalar chart')
        q = Fraction(e[-2])
        require(q and q.denominator & (q.denominator - 1) == 0,
                'Nonzero dyadic coefficient')
        if e[0] == 'ADD':
            add_row(rows, e[1], e[2], q)
        else:
            require(unit(q), 'Invertible dyadic scale')
            rows[e[1]] = {c: q * v for c, v in rows[e[1]].items()}
    return rows


def sharing_choice(rows, destination, source):
    a, b = rows[destination], rows[source]
    common = a.keys() & b.keys()
    if 2 * len(common) - len(b) < 2:
        return None
    counts = Counter(a[c] / b[c] for c in sorted(common))
    choices = []
    for q, count in counts.items():
        if q.denominator & (q.denominator - 1) == 0 and abs(q) < 4096:
            gain = len(common) + count - len(b)
            if gain >= 2:
                choices.append((gain, -abs(q.numerator).bit_length()
                                - q.denominator.bit_length(), q))
    if not choices:
        return None
    gain, _, q = max(choices)
    return gain, destination, source, -q


def share(rows, operations):
    candidates = {}
    for d in rows:
        for s in rows:
            if d != s:
                choice = sharing_choice(rows, d, s)
                if choice:
                    candidates[d, s] = choice
    for count in range(MAX_SHARING + 1):
        if not candidates:
            return count
        require(count < MAX_SHARING, 'Row-sharing capacity')
        _, d, s, q = max(candidates.values())
        add_row(rows, d, s, q)
        operations.append(['ADD', d, s, str(q), FRAME])
        for key in tuple(candidates):
            if d in key:
                del candidates[key]
        for other in rows:
            if other != d:
                for left, right in ((d, other), (other, d)):
                    choice = sharing_choice(rows, left, right)
                    if choice:
                        candidates[left, right] = choice
    raise ValueError('Unreachable sharing exhaustion')


def eliminate(rows, operations):
    pending_rows, pending_columns = set(rows), set(rows)
    for _ in range(len(rows)):
        occupancy = Counter(c for r in pending_rows for c in rows[r]
                            if c in pending_columns)
        choices = []
        for r in sorted(pending_rows):
            for c, value in rows[r].items():
                if c in pending_columns and unit(value):
                    choices.append(((len(rows[r]) - 1) * (occupancy[c] - 1),
                                    len(rows[r]), occupancy[c], r != c, r, c))
        require(bool(choices), 'A dyadic-unit pivot must exist')
        *_, pivot, column = min(choices)
        q = rows[pivot][column]
        if q != 1:
            rows[pivot] = {c: v / q for c, v in rows[pivot].items()}
            operations.append(['SCALE', pivot, str(1 / q), FRAME])
        for destination in rows:
            if destination != pivot and column in rows[destination]:
                q = -rows[destination][column]
                add_row(rows, destination, pivot, q)
                operations.append(['ADD', destination, pivot, str(q), FRAME])
        pending_rows.remove(pivot)
        pending_columns.remove(column)
    require(not pending_rows and not pending_columns, 'All pivots completed')


def unpermute(rows, operations):
    exchanges = 0
    for r in rows:
        if rows[r] == {r: Fraction(1)}:
            continue
        matches = [s for s in rows if rows[s] == {r: Fraction(1)}]
        require(len(matches) == 1, 'A unique permutation row')
        s = matches[0]
        for d, source, q in ((r, s, 1), (s, r, -1), (r, s, 1)):
            add_row(rows, d, source, Fraction(q))
            operations.append(['ADD', d, source, str(q), FRAME])
        rows[s] = {c: -v for c, v in rows[s].items()}
        operations.append(['SCALE', s, '-1', FRAME])
        exchanges += 1
    require(all(row == {r: Fraction(1)} for r, row in rows.items()),
            'Elimination ends at the full identity')
    return exchanges


def inverse(program):
    answer = []
    for e in reversed(program):
        item = e.copy()
        q = Fraction(e[-2])
        item[-2] = str(-q if e[0] == 'ADD' else 1 / q)
        answer.append(item)
    return answer


def synthesize(program):
    rows = matrix(program)
    operations = []
    shared = share(rows, operations)
    eliminate(rows, operations)
    exchanges = unpermute(rows, operations)
    require(len(operations) <= MAX_EVENTS, 'Bounded emitted circuit')
    return inverse(operations), {'roles': len(rows), 'sharing_steps': shared,
                                 'exchanges': exchanges}
