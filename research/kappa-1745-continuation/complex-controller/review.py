#!/usr/bin/env python3
"""Read-only source and exact finite-control review for this controller scope."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def module(name):
    path = HERE / name
    spec = importlib.util.spec_from_file_location(name.replace('.', '_'), path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def tuples(x):
    return tuple(tuples(v) for v in x) if isinstance(x, list) else x


def rank(rows):
    rows = [[Q(x) for x in row] for row in rows]
    pivot = 0
    for column in range(len(rows[0])):
        chosen = next((j for j in range(pivot, len(rows)) if rows[j][column]), None)
        if chosen is None:
            continue
        rows[pivot], rows[chosen] = rows[chosen], rows[pivot]
        value = rows[pivot][column]
        rows[pivot] = [x / value for x in rows[pivot]]
        for j in range(len(rows)):
            if j != pivot:
                coefficient = rows[j][column]
                rows[j] = [x - coefficient * y for x, y in zip(rows[j], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def chart_rank(paired):
    operations = [op for op in paired.OPERATIONS if op[0] == 'B'][:8]
    matrix = [[Q(int(i == j)) for j in range(3)] for i in range(3)]
    derivative = [[[Q(0) for _ in range(3)] for _ in range(3)] for _ in range(8)]
    for _, dst, src, index in operations:
        coefficient = Q(index + 1)
        for k in range(8):
            derivative[k][dst] = [x + coefficient * y for x, y in zip(derivative[k][dst], derivative[k][src])]
        derivative[index][dst] = [x + y for x, y in zip(derivative[index][dst], matrix[src])]
        matrix[dst] = [x + coefficient * y for x, y in zip(matrix[dst], matrix[src])]
    return rank([[derivative[k][i][j] for k in range(8)] for i in range(3) for j in range(3)])


def main():
    ap = ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    target = json.loads((HERE / 'TARGET-PROFILE-ORBIT.json').read_text())
    control = json.loads((HERE / 'CURRENT-PROFILE-CONTROL.json').read_text())
    for receipt in (target, control):
        for path, digest in receipt['source_sha256'].items():
            assert sha256((ROOT / path).read_bytes()).hexdigest() == digest
    assert target['status'] == 'NO_F2_CONTROLLER_WITH_THIS_PROFILE'
    assert control['status'] == 'F2_PROFILE_WITNESS'
    orbit = module('orbit_profile_witness.py').load_orbits()
    current = tuples(control['initial_state_after_F0'])
    advances = []
    calls = 1
    for row in control['events_after_F0']:
        assert tuples(row['before']) == current
        event = tuples(row['event'])
        if row['kind'] == 'local':
            successors = orbit.local_successors(current, event[0])
            calls += 1
        else:
            successors = orbit.idle_successors(current, max_jump=6)
            advances.append(event[1] - event[0])
        following = tuples(row['after'])
        assert any(nxt == following and ev == event for nxt, ev in successors)
        current = following
    assert orbit.potential(current) == 0 and calls == 9
    advances.extend(8 - level for level, top, _ in current for _ in top if level < 8)
    assert sorted(advances) == control['profile_recomputed']

    paired = module('rational_topology_probe.py')
    independent = module('independent_topology_probe.py')
    exact_rejections = 0
    for filename, engine in [('RATIONAL-TOPOLOGY-PROBE.json', paired),
                             ('INDEPENDENT-TOPOLOGY-PROBE.json', independent),
                             ('CONTINUATION-PROBE.json', independent)]:
        receipt = json.loads((HERE / filename).read_text())
        pins = receipt['source_sha256']
        if isinstance(pins, str):
            assert pins == sha256((HERE / 'rational_topology_probe.py').read_bytes()).hexdigest()
        else:
            for path, digest in pins.items():
                assert sha256((HERE / path).read_bytes()).hexdigest() == digest
        rows = receipt.get('trials', receipt.get('rows'))
        for row in rows:
            values = [Q(x) for x in row['rounded_rational_coefficients']]
            if engine is paired:
                _, residual = engine.exact_endpoint(values)
            else:
                _, residual = engine.endpoint(values, exact=True)
            assert any(residual) and not row['exact_rational_endpoint']
            exact_rejections += 1
    dimension = chart_rank(paired)
    assert dimension == 8
    # Expand the displayed Laurent determinants over Q[a,a^-1,c,d,d^-1].
    from itertools import permutations
    def multiply(left, right):
        answer = {}
        for p, x in left.items():
            for q, y in right.items():
                power = tuple(a + b for a, b in zip(p, q))
                answer[power] = answer.get(power, Q(0)) + x * y
        return {p: x for p, x in answer.items() if x}
    def determinant(matrix):
        answer = {}
        for order in permutations(range(len(matrix))):
            inversions = sum(order[i] > order[j] for i in range(len(order)) for j in range(i + 1, len(order)))
            term = {(0, 0, 0): Q((-1) ** inversions)}
            for i, j in enumerate(order):
                term = multiply(term, matrix[i][j])
            for p, x in term.items():
                answer[p] = answer.get(p, Q(0)) + x
        return {p: x for p, x in answer.items() if x}
    first_minor = determinant([[{(-1, 0, 0): Q(1)}, {(-1, 1, -1): Q(-1)}],
                               [{(0, 1, 0): Q(-1)}, {(0, 0, -1): Q(1)}]])
    assert first_minor == {(-1, 0, -1): Q(1), (-1, 2, -1): Q(-1)}
    one = {(0, 0, 0): Q(1)}
    membership = determinant([[one, {(0, 1, -1): Q(-1)}, {}], [{}, {}, one], [{}, one, {}]])
    assert membership == {(0, 0, 0): Q(-1)}
    dependency_paths = [HERE.parent / 'bit-geometry/controller_clock_orbits.py',
                        HERE.parent / 'bit-geometry/controller-orbits/K4.json',
                        HERE.parent / 'bit-geometry/CLOCK-MODEL-PROOF.md',
                        HERE.parent / 'bit-geometry/COMPLEX-CLOCK-PACKING.json']
    result = {'status': 'PASS', 'target_profile_orbit_nodes': target['statistics']['orbit_nodes'],
              'positive_control_calls': calls, 'positive_control_idle_profile': sorted(advances),
              'rounded_rational_endpoints_exactly_rejected': exact_rejections,
              'SL3_parameter_chart_exact_jacobian_rank': dimension,
              'K3_triangle_determinant_numerator': '1-c^2',
              'K3_accessible_projection_membership_determinant': '-1',
              'new_controller_admitted': False, 'new_kappa_claimed': False,
              'dependency_sha256': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                    for p in dependency_paths},
              'source_sha256': {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                for p in sorted(HERE.iterdir()) if p.suffix in ('.py', '.md')},
              'scope': 'Source binding; exact positive finite path; exact rational rejection gates; '
                       'parameter-chart rank. The negative F2 enumeration is not rerun by this light review.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
