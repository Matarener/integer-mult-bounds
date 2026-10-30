"""Finite conformance and cache-failure controls before a full candidate."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace
from unittest.mock import patch

from setup_cache import Setup, bind, require

from contextlib import contextmanager
from retained import baseline


@contextmanager
def prepared_source():
    with baseline() as base:
        sys.path.insert(0, str(base))
        from source import prepared
        with prepared() as root:
            yield root


def reject(action, label, results):
    try:
        action()
    except (ValueError, TypeError, RuntimeError, AttributeError) as error:
        results[label] = type(error).__name__ + ': ' + str(error)
    else:
        raise ValueError('Invalid setup accepted: ' + label)


def main():
    with prepared_source() as root:
        sys.path.insert(0, str(root / 'research/selected-quadratic-replay'))
        import checks
        C = checks.load('setup_feasibility_literal', 'research/p104-native-channel/vendor/clifford_exact.py')
        setup, old, binding = bind(C)
        cases = amplitudes = 0
        try:
            for n in range(1, 5):
                gates = [('phase', j) for j in range(4)]
                gates += [('X', q) for q in range(1 << n)]
                gates += [('C', q, s) for q in range(1, 1 << n) for s in (-1, 1)]
                gates += [('P', tuple(1 << ((i + shift) % n) for i in range(n))) for shift in range(n)]
                for mask in range(1 << n):
                    rows = tuple((1 << i) if mask >> i & 1 else 0 for i in range(n))
                    gates.append(('D', rows, tuple((mask >> i) & 1 for i in range(n))))
                for j in range(len(gates)):
                    circuit = tuple(gates[k % len(gates)] for k in (j, 3*j+1, 7*j+2))
                    operator = C.Op(n, (), list(circuit))
                    for initial in range(1 << n):
                        expected = old(operator, initial)
                        require(operator.zero_state(initial) == expected, 'Every exact dense amplitude and denominator')
                        cases += 1
                        amplitudes += 1 << n
            n = 9
            permutation = tuple(1 << ((i + 3) % n) for i in range(n))
            quadratic = tuple((1 << i) | (1 << ((i+1) % n)) for i in range(n))
            linear = tuple(i % 4 for i in range(n))
            circuit = [('C', 511, 1), ('P', permutation), ('D', quadratic, linear),
                       ('phase', 3), ('C', 17, -1)]
            operator = C.Op(n, (), circuit)
            for initial in (0, 1, 17, 511):
                require(operator.zero_state(initial) == old(operator, initial), 'Full-width literal conformance')
                cases += 1
                amplitudes += 512
            controls = {}
            p = ['P', [1, 2]]
            value = setup(2, p)
            setup(2, p)
            before = setup.cached.cache_info()
            require(before.hits > 0, 'Exact key reuse')
            p[1][0] = 3
            require(setup(2, p) != value and value == (0, 1, 2, 3), 'Mutable input snapshot and invalidation')
            controls['input_snapshot'] = 'PASS'
            reject(lambda: value.__setitem__(0, 99), 'immutable_return', controls)
            require(setup(2, ['D', [1, 2], [0, 0]]) != setup(2, ['D', [1, 2], [1, 0]]), 'Changed phase invalidates')
            controls['changed_phase'] = 'PASS'
            require(len(setup(3, ('P', (1, 2, 4)))) == 8, 'Changed width retains domain')
            controls['changed_width'] = 'PASS'
            for name, width, gate in [('bool_width', True, ('P', (1,))),
                                     ('float_width', 1.0, ('P', (1,))),
                                     ('bool_matrix', 2, ('P', (True, 2))),
                                     ('float_matrix', 2, ('P', (1.0, 2))),
                                     ('bool_phase', 2, ('D', (1, 2), (True, 0))),
                                     ('bad_matrix_length', 3, ('P', (1, 2))),
                                     ('bad_phase_length', 2, ('D', (1, 2), (0,))),
                                     ('unknown_gate', 2, ('X', 1)),
                                     ('unbounded_width', 10, ('P', tuple(1 << i for i in range(10))))]:
                reject(lambda width=width, gate=gate: setup(width, gate), name, controls)
            for capacity in (0, True, 513):
                reject(lambda capacity=capacity: Setup(C, capacity), 'capacity_' + str(capacity), controls)
            tiny = Setup(C, 3)
            for phase in range(5):
                tiny(1, ('D', (0,), (phase,)))
            require(tiny.cached.cache_info().currsize == 3, 'Bounded cache residency')
            misses = tiny.cached.cache_info().misses
            tiny(1, ('D', (0,), (0,)))
            require(tiny.cached.cache_info().misses == misses + 1, 'Eviction recomputes')
            controls['bounded_eviction'] = 'PASS'
            attempts = []
            def broken(rows, address):
                attempts.append(address)
                raise RuntimeError('setup sentinel')
            failing = Setup(SimpleNamespace(mv=broken, qvalue=C.qvalue))
            for i in range(2):
                reject(lambda: failing(1, ('P', (1,))), 'exception_' + str(i), controls)
            require(attempts == [0, 0] and failing.cached.cache_info().currsize == 0, 'Exceptions never cached')
            operator = C.Op(2, (), [('C', 1, 1), ('P', (1, 2)), ('D', (1, 2), (1, 0))])
            expected = old(operator, 0)
            returned = operator.zero_state(0)
            returned[0][0] = (99, 99)
            require(operator.zero_state(0) == expected, 'Fresh dense output after mutation')
            controls['fresh_dense_output'] = 'PASS'
            saved_cache = setup.cached
            for tag in ('P', 'D'):
                def corrupted(width, gate, tag=tag):
                    values = saved_cache(width, gate)
                    if gate[0] == tag:
                        return tuple((x+1) % ((1 << width) if tag == 'P' else 4) for x in values)
                    return values
                setup.cached = corrupted
                fault = C.Op(2, (), [('P', (1, 2))] if tag == 'P' else [('D', (1, 2), (0, 0))])
                try:
                    require(fault.zero_state(0) != old(fault, 0), 'Wrong address or absolute phase detected')
                    controls['corrupt_' + tag + '_detected'] = 'PASS'
                finally:
                    setup.cached = saved_cache
            C.Op.zero_state = old
            with patch('setup_cache.inspect.getsource', return_value='def zero_state(self):\n    pass\n'):
                reject(lambda: bind(C), 'changed_literal_method', controls)
        finally:
            C.Op.zero_state = old
    result = {'cases': cases, 'amplitude_entries': amplitudes, 'controls': controls,
              'binding': binding, 'full_width_cases': 4, 'max_setup_capacity': 512}
    print('PASS_LITERAL_SETUP_FEASIBILITY', json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
