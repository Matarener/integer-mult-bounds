#!/usr/bin/env python3
"""Check two scoped binary helper bounds. Apache-2.0.

Ali Romman, with substantial OpenAI Codex assistance.
This is an exact finite certificate check, not a formal proof checker.
"""
import argparse
from copy import deepcopy
from hashlib import sha256
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def outer(column, row, size):
    return tuple(row if column >> i & 1 else 0 for i in range(size))


def add(*matrices):
    result = [0] * len(matrices[0])
    for matrix in matrices:
        for i, row in enumerate(matrix):
            result[i] ^= row
    return tuple(result)


def multiply(left, right):
    result = []
    for row in left:
        value = 0
        for j, other in enumerate(right):
            if row >> j & 1:
                value ^= other
        result.append(value)
    return tuple(result)


def rank(matrix):
    pivots = {}
    for row in matrix:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def identity(size):
    return tuple(1 << i for i in range(size))


def reduce_state(rows):
    size = len(rows)
    isolated = [i for i in range(size) if rows[i] in (0, 1 << i)
                and not any(rows[j] >> i & 1 for j in range(size) if j != i)]
    gain = sum(bool(rows[i]) for i in isolated)
    live = [i for i in range(size) if i not in isolated]
    if len(live) > 3:
        return None
    options = []
    for order in itertools.permutations(live):
        result = tuple(sum(((rows[i] >> j) & 1) << k for k, j in enumerate(order))
                       for i in order)
        options.append(result)
    return min(options) if options else (), gain


def full_matrix(parameters):
    u, v, p, h = (parameters[key] for key in ('u', 'v', 'p', 'h'))
    need(all(isinstance(x, int) and not isinstance(x, bool) for x in (u, v, p, h)),
         'FULL parameters must be integers')
    need(0 < u < 8 and 0 < v < 8 and 0 < p < 8 and 0 <= h < 16,
         'FULL support is outside the stated alphabet')
    need(not parity(u & v) and not parity(u & p) and p != v,
         'FULL nilpotent and helper-row conditions failed')
    return add(outer(u, v, 4), outer(h, p, 4))


def full_alphabet():
    matrices = {}
    for u, v, p, h in itertools.product(range(1, 8), range(1, 8), range(1, 8), range(16)):
        if parity(u & v) or parity(u & p) or p == v:
            continue
        parameters = dict(u=u, v=v, p=p, h=h)
        matrix = full_matrix(parameters)
        matrices[matrix] = parameters
    return list(matrices.items())


def raw_edges(state, alphabet):
    before = state + (0,) * (4 - len(state))
    for matrix, parameters in alphabet:
        result = reduce_state(add(before, matrix))
        if result is not None:
            target, gain = result
            yield target, gain, 0, 1, parameters
    size = min(4, len(state) + 1)
    before = state + (0,) * (size - len(state))
    for u, v in itertools.product(range(1, 1 << size), repeat=2):
        result = reduce_state(add(before, outer(u, v, size)))
        if result is not None:
            target, gain = result
            yield target, gain, 1, 0, dict(u=u, v=v)


def build_graph():
    alphabet = full_alphabet()
    states = [()]
    seen = {()}
    edges = []
    raw_count = 0
    for state in states:
        best = {}
        for target, gain, thin, full, parameters in raw_edges(state, alphabet):
            raw_count += 1
            key = (target, thin, full)
            if key not in best or gain > best[key][1]:
                best[key] = (target, gain, thin, full, parameters)
        for target, gain, thin, full, parameters in best.values():
            if target not in seen:
                seen.add(target)
                states.append(target)
            edges.append((state, target, gain, thin, full, parameters))
    return alphabet, states, edges, raw_count


def check_potential(potential, edges):
    for source, target, gain, thin, full, _ in edges:
        need(potential[target] - potential[source] >= 3 * gain - 3 * thin - 5 * full,
             'An edge violates the integer potential')


def check_certificate(certificate, alphabet, states, edges):
    need(certificate['schema'] == 'binary-helper-five-thirds/1', 'Certificate schema')
    entries = certificate['states']
    potential = {tuple(row['matrix']): row['potential'] for row in entries}
    need(len(entries) == len(potential) and set(potential) == set(states),
         'Certificate state coverage differs from reachable states')
    need(all(isinstance(z, int) and not isinstance(z, bool) for z in potential.values()),
         'The potential must use integers')
    need(certificate['operators'] == len(alphabet) == 315, 'FULL matrix census')
    need(certificate['edge_count'] == len(edges) == 10035, 'Dominant edge census')
    check_potential(potential, edges)
    # Check all retained and discarded edges. A smaller reward must not escape.
    for source in states:
        raw = [(source, *edge) for edge in raw_edges(source, alphabet)]
        check_potential(potential, raw)
    state = ()
    gain = thin = full = 0
    for step in certificate['cycle']:
        need(tuple(step['source']) == state, 'The witness does not start at its stated state')
        parameters = step['parameters']
        if step['kind'] == 'FULL':
            matrix = full_matrix(parameters)
            before = state + (0,) * (4 - len(state))
            full += 1
        else:
            need(step['kind'] == 'THIN', 'Unknown witness operation')
            size = min(4, len(state) + 1)
            u, v = parameters['u'], parameters['v']
            need(0 < u < (1 << size) and 0 < v < (1 << size), 'THIN support')
            matrix = outer(u, v, size)
            before = state + (0,) * (size - len(state))
            thin += 1
        result = reduce_state(add(before, matrix))
        need(result is not None, 'The witness leaves the finite grammar')
        state, increment = result
        need(state == tuple(step['target']) and increment == step['gain'], 'Witness edge mismatch')
        gain += increment
    need(state == () and full > 0 and 3 * (gain - thin) == 5 * full,
         'The witness does not attain the closed-word bound')
    return potential, dict(gain=gain, thin=thin, full=full)


def jordan_type(matrix):
    square = multiply(matrix, matrix)
    return rank(matrix) == 2 and rank(square) == 1 and multiply(square, matrix) == square


def embed(matrix, support, size):
    return tuple(sum(((matrix[support.index(i)] >> j) & 1) << k
                     for j, k in enumerate(support)) if i in support else 0
                 for i in range(size))


def two_call_control():
    terms = [tuple((bits >> (3 * i)) & 7 for i in range(3)) for bits in range(512)]
    terms = [matrix for matrix in terms if jordan_type(matrix)]
    need(len(terms) == 84, 'The three-dimensional Jordan-type census changed')
    diagonal = {}
    trials = 0
    for second_support in itertools.combinations(range(4), 3):
        for first, second in itertools.product(terms, repeat=2):
            total = add(embed(first, (0, 1, 2), 4), embed(second, second_support, 4))
            trials += 1
            if all(row in (0, 1 << i) for i, row in enumerate(total)):
                degree = rank(total)
                diagonal[degree] = diagonal.get(degree, 0) + 1
                need(degree <= 2, 'Two terms produced a diagonal of rank greater than two')
    return dict(three_dimensional_terms=len(terms), pairs=trials,
                diagonal_rank_counts={str(k): v for k, v in sorted(diagonal.items())})


def polynomial_multiply(left, right):
    size = len(left)
    result = [[set() for _ in range(size)] for _ in range(size)]
    for i, j, k in itertools.product(range(size), repeat=3):
        for a, b in itertools.product(left[i][k], right[k][j]):
            if a & b & 8:
                continue
            need(not (a & b & 7), 'A fresh stage symbol occurs twice')
            term = a | b
            if term in result[i][j]:
                result[i][j].remove(term)
            else:
                result[i][j].add(term)
    return result


def motif_terms():
    n1, n3 = outer(6, 6, 5), outer(12, 12, 5)
    return [add(outer(1, 1, 5), n1), add((0, 2, 4, 8, 0), n1, n3),
            add(outer(16, 16, 5), n3)]


def check_motif_endpoint(terms):
    supports = [7, 14, 28]
    word = [[{0} if i == j else set() for j in range(5)] for i in range(5)]
    for stage, (support, matrix) in enumerate(zip(supports, terms)):
        local = [[set() for _ in range(5)] for _ in range(5)]
        for i, j in itertools.product(range(5), repeat=2):
            d = (1 << stage) if support >> i & 1 else 0
            if i == j:
                local[i][j].add(d)
            if matrix[i] >> j & 1:
                local[i][j].add(d | 8)
        word = polynomial_multiply(local, word)
    expected = [[set() for _ in range(5)] for _ in range(5)]
    for i in range(5):
        d = sum((1 << stage) for stage, support in enumerate(supports) if support >> i & 1)
        expected[i][i] = {d, d | 8}
    need(word == expected, 'The exact binary polynomial endpoint failed')


def motif_control():
    terms = motif_terms()
    partial = (0,) * 5
    for support, matrix in zip((7, 14, 28), terms):
        projector = tuple((1 << i) if support >> i & 1 else 0 for i in range(5))
        need(jordan_type(matrix), 'A motif term has the wrong Jordan type')
        need(multiply(projector, matrix) == multiply(matrix, projector) == matrix,
             'A motif term leaves its stage support')
        need(multiply(projector, partial) == multiply(partial, projector),
             'A motif stage does not commute with the prefix')
        partial = add(partial, matrix)
    need(partial == identity(5), 'The motif target is not identity')
    check_motif_endpoint(terms)
    return dict(full=3, outputs=5, stage_degrees=[1, 2, 3, 2, 1],
                exact_binary_polynomial_endpoint=True)


def reject(action):
    try:
        action()
    except ValueError:
        return True
    raise ValueError('A negative control was accepted')


def run(certificate):
    alphabet, states, edges, raw_count = build_graph()
    potential, cycle = check_certificate(certificate, alphabet, states, edges)
    tight = next(edge for edge in edges if edge[0] != edge[1]
                 and potential[edge[1]] - potential[edge[0]] == 3 * edge[2] - 3 * edge[3] - 5 * edge[4])
    bad_potential = potential.copy()
    bad_potential[tight[1]] -= 1
    missing = deepcopy(certificate)
    missing['states'].pop()
    wrong_terms = motif_terms()
    wrong_terms[1] = tuple(row ^ (1 if i == 0 else 0) for i, row in enumerate(wrong_terms[1]))
    controls = {
        'lowered_potential_rejected': reject(lambda: check_potential(bad_potential, edges)),
        'missing_state_rejected': reject(lambda: check_certificate(missing, alphabet, states, edges)),
        'free_thin_query_rejected': reject(lambda: check_potential(potential, [((), (), 1, 0, 0, {})])),
        'non_nilpotent_source_rejected': reject(lambda: full_matrix(dict(u=1, v=1, p=2, h=4))),
        'wrong_motif_endpoint_rejected': reject(lambda: check_motif_endpoint(wrong_terms)),
    }
    # Dropping the Jordan-type condition permits a one-call counterexample.
    need(not jordan_type(identity(3)) and 3 * 3 > 5, 'Hypothesis control')
    controls['identity_term_violates_bound_without_Jordan_condition'] = True
    canonical_edges = sorted([list(a), list(b), g, h, f] for a, b, g, h, f, _ in edges)
    graph_hash = sha256(json.dumps(canonical_edges, separators=(',', ':')).encode()).hexdigest()
    return dict(status='PASS_BINARY_HELPER_FIVE_THIRDS', graph=dict(
        full_matrices=len(alphabet), states=len(states), dominant_edges=len(edges),
        raw_edges=raw_count, sha256=graph_hash, exact_maximum='5/3', cycle=cycle),
        two_call_control=two_call_control(), sharp_motif=motif_control(), controls=controls,
        scope='Two separate binary classes; no complex lift, native admission, or kappa improvement.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true', help='Write the deterministic result receipt')
    args = parser.parse_args()
    result = run(json.loads((HERE / 'CERTIFICATE.json').read_text()))
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(json.loads(path.read_text()) == result, 'The retained result receipt differs')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
