#!/usr/bin/env python3
"""Exact literal Pauli-history certificates; no imports from predecessor code.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as F
import json
from pathlib import Path


class Q:
    """Gaussian rationals, with exact arithmetic and no floating point."""
    __slots__ = ('a', 'b')

    def __init__(self, a=0, b=0):
        if isinstance(a, Q):
            self.a, self.b = a.a, a.b
        else:
            self.a, self.b = F(a), F(b)

    def __add__(self, other):
        other = Q(other)
        return Q(self.a + other.a, self.b + other.b)

    __radd__ = __add__

    def __neg__(self):
        return Q(-self.a, -self.b)

    def __sub__(self, other):
        return self + -Q(other)

    def __mul__(self, other):
        other = Q(other)
        return Q(self.a*other.a-self.b*other.b,
                 self.a*other.b+self.b*other.a)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = Q(other)
        d = other.a**2 + other.b**2
        if not d:
            raise ZeroDivisionError('Gaussian zero denominator')
        return self * Q(other.a/d, -other.b/d)

    def __pow__(self, exponent):
        if not isinstance(exponent, int) or exponent < 0:
            raise ValueError('nonnegative integer exponent required')
        result, base = Q(1), self
        while exponent:
            if exponent & 1:
                result = result * base
            base = base * base
            exponent //= 2
        return result

    def __bool__(self):
        return bool(self.a or self.b)

    def __eq__(self, other):
        other = Q(other)
        return self.a == other.a and self.b == other.b


def need(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def scale(c, a):
    return [[c*x for x in row] for row in a]


def add(a, b):
    return [[x+y for x, y in zip(ar, br)] for ar, br in zip(a, b)]


def mul(a, b):
    out = [[Q() for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, value in enumerate(row):
            if value:
                for j, other in enumerate(b[k]):
                    if other:
                        out[i][j] = out[i][j] + value*other
    return out


def kron(a, b):
    return [[x*y for x in ar for y in br] for ar in a for br in b]


def power(a, f):
    out = [[Q(1)]]
    for _ in range(f):
        out = kron(out, a)
    return out


def flat(a):
    return [x for row in a for x in row]


def rank(rows):
    basis = {}
    for original in rows:
        row = list(original)
        for pivot, vector in sorted(basis.items()):
            c = row[pivot]
            if c:
                row = [x-c*y for x, y in zip(row, vector)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            c = row[pivot]
            basis[pivot] = [x/c for x in row]
    return len(basis)


def span_rank(matrices):
    return rank([flat(a) for a in matrices])


def model(a, b, f):
    need(isinstance(f, int) and not isinstance(f, bool) and f > 0,
         'positive integer width required')
    need(bool(a*b*(a*a-b*b)), 'target must satisfy ab(a^2-b^2) != 0')
    x = [[Q(0), Q(1)], [Q(1), Q(0)]]
    z = [[Q(1), Q(0)], [Q(0), Q(-1)]]
    p, c = power(x, f), power(z, f)
    ordinary = [eye(2**f), p, c, mul(p, c)]
    h = power(add(scale(a, eye(2)), scale(b, x)), f)
    return ordinary, h


def owner_rows(matrices, owner, count):
    width = len(flat(matrices[0]))
    return [[Q()]*(owner*width) + flat(m) +
            [Q()]*((count-owner-1)*width) for m in matrices]


def main_check():
    samples = [(Q(1), Q(2)), (Q(2), Q(1)), (Q(1), Q(0, 1)),
               (Q(F(1, 2), F(1, 2)), Q(F(1, 2), F(-1, 2))),
               (Q(0, 1), Q(2)), (Q(2, 1), Q(1, -1))]
    rows, phase_cases, owner_cases = [], 0, 0
    for sample, (a, b) in enumerate(samples):
        for f in range(1, 5):
            ordinary, h = model(a, b, f)
            ident, p, c, pc = ordinary
            n = len(h)
            need(span_rank(ordinary) == 4, 'ordinary dimension')
            need(mul(p, c) == scale(Q((-1)**f), mul(c, p)), 'phase twist')
            need(mul(p, p) == ident and mul(c, c) == ident, 'involutions')
            # Independent coefficient expansion in the computational basis.
            expanded = [[a**(f-(r^s).bit_count()) * b**((r^s).bit_count())
                         for s in range(n)] for r in range(n)]
            need(h == expanded, 'Kronecker vs Hamming expansion')
            target = [mul(g, h) for g in ordinary]
            combined = span_rank(ordinary + target)
            need(span_rank(target) == 4, 'invertible target module')
            if f == 1:
                need(combined == 4, 'width-one ordinary target')
            elif f % 2:
                need(combined == 8, 'odd-width direct-sum separation')
            e = scale(Q(F(1, 4)), mul(add(ident, p), add(ident, c)))
            projected_rank = span_rank([mul(e, g) for g in ordinary])
            if f % 2 == 0:
                need(mul(e, e) == e and projected_rank == 1, 'even character')
                need(span_rank([e, mul(e, h)]) == 2, 'character detects target')
            else:
                need(mul(e, e) != e and projected_rank != 1,
                     'odd-width false character control')
            rows.append({'sample': sample, 'width': f, 'ordinary': 4,
                         'ordinary_plus_target': combined,
                         'candidate_character_dimension': projected_rank})

            if sample == 3:
                # All 16 actual group matrices, including width-dependent phases.
                x = [[Q(), Q(1)], [Q(1), Q()]]
                z = [[Q(1), Q()], [Q(), Q(-1)]]
                for phase in range(4):
                    for u in range(2):
                        for v in range(2):
                            g = mul(x if u else eye(2), z if v else eye(2))
                            literal = power(scale(Q(0, 1)**phase, g), f)
                            lifted = mul(p if u else ident, c if v else ident)
                            need(literal == scale(Q(0, 1)**(phase*f), lifted),
                                 'actual phase lift')
                            phase_cases += 1

            if sample == 0 and f in (2, 3):
                base = [e] if f == 2 else ordinary
                targets = [mul(e, h)] if f == 2 else target
                per = len(base)
                for q in (1, 2, 3):
                    count = q+1  # An independent dirty coordinate remains present.
                    initial = sum((owner_rows(base, j, count) for j in range(count)), [])
                    goals = sum((owner_rows(targets, j, count) for j in range(q)), [])
                    need(rank(initial + goals) == per*(count+q), 'independent owners')
                    cached = owner_rows(targets, 0, count)
                    need(rank(initial + cached + goals)-rank(initial+cached) == per*(q-1),
                         'cached observation control')
                    duplicate = owner_rows(targets, 0, count)*q
                    need(rank(initial+duplicate)-rank(initial) == per,
                         'duplicate owner control')
                    owner_cases += 3

    # The scalar separation identity is checked independently of tensor matrices.
    scalar_cases = 0
    for a, b in samples:
        lp, lm = a+b, a-b
        for f in range(2, 33):
            for k in (0, 1) if f >= 3 else (0,):
                need(lp**(f-k)*lm**k-lp**(f-k-2)*lm**(k+2) ==
                     Q(4)*a*b*lp**(f-k-2)*lm**k, 'weight separation identity')
                scalar_cases += 1
    controls = 0
    for a, b in [(Q(), Q(1)), (Q(1), Q()), (Q(1), Q(1)), (Q(1), Q(-1))]:
        try:
            model(a, b, 3)
        except ValueError:
            controls += 1
        else:
            raise ValueError('invalid target admitted')
    for f in (0, -1, True):
        try:
            model(Q(1), Q(2), f)
        except ValueError:
            controls += 1
        else:
            raise ValueError('invalid width admitted')
    # Merely excluding actual G is insufficient: 2X is projectively ordinary.
    for f in (1, 2, 3):
        ordinary, _ = model(Q(1), Q(2), f)
        need(span_rank(ordinary+[scale(Q(2)**f, ordinary[1])]) == 4,
             'projectively ordinary target control')
        controls += 1
    # A single involution character does not stay scalar after adding Z.
    for f in (2, 3, 4):
        ordinary, _ = model(Q(1), Q(2), f)
        small_e = scale(Q(F(1, 2)), add(ordinary[0], ordinary[1]))
        need(span_rank([mul(small_e, g) for g in ordinary]) == 2,
             'smaller-alphabet projector must not be reused')
        controls += 1
    return {'status': 'PASS_PAULI_TWISTED_HISTORY_THRESHOLD',
            'literal_cases': rows, 'actual_group_lifts': phase_cases,
            'owner_and_history_controls': owner_cases,
            'scalar_identity_cases': scalar_cases, 'boundary_controls': controls,
            'theorem': 'zero at width one; at least q at every width >=2',
            'upper_bound_condition': 'each requested H is an available paid primitive',
            'scope': 'finite checks corroborate PROOF.md; no physical caller admission'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit', action='store_true')
    args = parser.parse_args()
    result = main_check()
    if not args.emit:
        expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
        need(result == expected, 'committed certificate mismatch')
    print(json.dumps(result, indent=2, sort_keys=True))
