#!/usr/bin/env python3
"""Exact bounded checks, not a formal proof of arbitrary-field completeness.

apoursh with substantial OpenAI Codex assistance; Apache-2.0.
"""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent


def load(name):
    # Execute current source bytes; -B alone still permits stale cache reads.
    module = ModuleType(name)
    path = HERE / (name + '.py')
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


pencil = load('pencil')
oracle = load('oracle')
require = pencil.require
LIFT_DOMAINS = ((1, 1, 2), (2, 1, 2), (3, 2, 2), (5, 1, 2),
                (2, 2, 3), (3, 2, 3), (4, 2, 3),
                (2, 1, 4), (3, 1, 4), (2, 2, 4), (3, 2, 4), (2, 3, 4), (4, 1, 5))


def field_checks():
    count = 0
    for q in (2, 3, 4, 5):
        f = pencil.Field(q)
        for a, b, c in product(range(q), repeat=3):
            require(f.mul(f.mul(a, b), c) == f.mul(a, f.mul(b, c)), 'associativity')
            require(f.mul(a, f.add(b, c)) == f.add(f.mul(a, b), f.mul(a, c)),
                    'distributivity')
            count += 1
        for a in range(1, q):
            require(f.mul(a, f.inv(a)) == 1, 'field inverse')
    return count


def kernel(e, r, f, left=False):
    return {triple for triple in product(range(1, f.q), repeat=3)
            if pencil.character(e, r, triple, f, left) == 1}


def oracle_checks():
    reports = oracle.report()
    for row in reports:
        e, r, q = row['index'], row['multiplicity'], row['prime']
        f = pencil.Field(q)
        require(set(row['image']) == kernel(e, r, f), 'independent image mismatch')
        # GL_r size is a separate elementary count, not a generated witness count.
        glr = 1
        for i in range(r):
            glr *= q ** r - q ** i
        require(row['stabilizer_count'] == glr * (q*q-1) * (q*q-q),
                'complete stabilizer count mismatch')
    require(sum(row['tested_pr_pairs'] for row in reports) == 7710, 'oracle coverage')
    require(sum(row['stabilizer_count'] for row in reports) == 4470, 'oracle count')
    return reports


def determinants(witness, field):
    return tuple(pencil.determinant(matrix, field) for matrix in witness)


def check_witness(e, r, witness, field, left=False):
    first, second = pencil.slices(e, r)
    if left:
        first, second = pencil.transpose(first), pencil.transpose(second)
    require(pencil.fixes(first, second, witness, field), 'literal lift equation')
    require(pencil.character(e, r, determinants(witness, field), field, left) == 1,
            'witness determinant character')


def lift_checks():
    reports = []
    for e, r, q in LIFT_DOMAINS:
        f = pencil.Field(q)
        count = 0
        for action in pencil.general_linear_two(f):
            z = pencil.determinant(action, f)
            for u in range(1, q):
                d = pencil.identity(r)
                d[0][0] = u
                if r > 1:
                    d[0][1] = 1  # non-scalar mixing between repeated blocks
                witness = pencil.lift(e, r, action, d, f)
                check_witness(e, r, witness, f)
                check_witness(e, r, (witness[1], witness[0], action), f, True)
                predicted = (f.mul(f.power(u, e), f.power(z, r*e*(e-1)//2)),
                             f.mul(f.power(u, -e-1), f.power(z, -r*e*(e+1)//2)), z)
                require(determinants(witness, f) == predicted, 'parametrized determinant')
                count += 1
        reports.append({'index': e, 'multiplicity': r, 'field': q,
                        'right_lifts': count, 'transposed_lifts': count})
    return reports


def converse_checks():
    accepted = rejected = 0
    for e, r, q in LIFT_DOMAINS:
        f = pencil.Field(q)
        for left in (False, True):
            image = kernel(e, r, f, left)
            require(len(image) == (q-1)**2, 'image size')
            for triple in product(range(1, q), repeat=3):
                if triple in image:
                    w = pencil.witness_for_triple(e, r, triple, f, left)
                    check_witness(e, r, w, f, left)
                    require(determinants(w, f) == triple, 'constructive converse')
                    accepted += 1
                else:
                    try:
                        pencil.witness_for_triple(e, r, triple, f, left)
                    except ValueError:
                        rejected += 1
                    else:
                        raise ValueError('excluded determinant triple accepted')
    return {'accepted': accepted, 'excluded': rejected}


def mutation_checks():
    f3, f4, f5 = (pencil.Field(q) for q in (3, 4, 5))
    require(kernel(2, 1, f3) != {t for t in product((1, 2), repeat=3) if t[0] == 1},
            'omitted slice exponent was not detected')
    require(kernel(1, 2, f3) != kernel(1, 1, f3), 'omitted multiplicity undetected')
    require(kernel(2, 1, f3) != kernel(2, 1, f3, True), 'omitted orientation undetected')
    first, second = pencil.slices(1, 1)
    w = pencil.lift(1, 1, [[1, 1], [0, 2]], [[1]], f5)
    for bad_q in (pencil.transpose(w[1]), pencil.inverse(w[1], f5)):
        require(not pencil.fixes(first, second, (w[0], bad_q, w[2]), f5),
                'wrong right-factor convention undetected')
    # Squaring X+Y in characteristic two has no XY term; F4 is not Z/4Z.
    sym = pencil.symmetric_power(2, [[1, 1], [0, 1]], f4)
    require(sym[1][0] == 0 and f4.mul(2, 2) == 3, 'characteristic-two arithmetic')
    bad = [row[:] for row in sym]
    bad[1][0] = 2  # incorrect binomial coefficient modulo q instead of p
    p = pencil.transpose(pencil.symmetric_power(1, [[1, 1], [0, 1]], f4))
    a, b = pencil.slices(2, 1)
    require(not pencil.fixes(a, b, (p, pencil.inverse(bad, f4), [[1, 1], [0, 1]]), f4),
            'incorrect characteristic reduction undetected')
    return 6


def invalid_checks():
    f = pencil.Field(3)
    operations = (
        lambda: pencil.Field(6), lambda: pencil.Field(True),
        lambda: pencil.slices(0, 1), lambda: pencil.slices(1, 0),
        lambda: pencil.slices(6, 1), lambda: pencil.slices(True, 1),
        lambda: pencil.lift(1, 1, [[1, 0], [0, 0]], [[1]], f),
        lambda: pencil.lift(1, 1, [[1, 0], [0, 1]], [[0]], f),
        lambda: pencil.witness_for_triple(1, 1, (0, 1, 1), f),
        lambda: oracle.enumerate_image(2, 2, 3),
        lambda: pencil.witness_for_triple(10**9, 1, (1, 1, 1), f),
        lambda: pencil.witness_for_triple(1, 1, (1, 1), f),
        lambda: pencil.lift(1, 1, [[1]], [[1]], f),
        lambda: pencil.lift(1, 1, [[1, 0], [0, 1]], [[3]], f),
    )
    for operation in operations:
        try:
            operation()
        except ValueError:
            continue
        raise ValueError('invalid fixture accepted')
    return len(operations)


def main():
    result = {'field_axiom_triples': field_checks(), 'oracle': oracle_checks(),
              'lift_domains': lift_checks(), 'converse': converse_checks(),
              'mutation_controls': mutation_checks(), 'invalid_controls': invalid_checks(),
              'claim': 'scoped written proof with bounded exact corroboration; no new kappa'}
    hashes = {p.name: sha256(p.read_bytes()).hexdigest()
              for p in sorted(HERE.iterdir()) if p.is_file()}
    print('RESULT ' + json.dumps(result, sort_keys=True))
    print('PACKAGE_SHA256 ' + json.dumps(hashes, sort_keys=True))
    print('PASS_KRONECKER_DETERMINANT_IMAGE')
    return 0


if __name__ == '__main__':
    sys.exit(main())
