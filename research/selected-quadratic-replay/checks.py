"""Check exact state conversion, complete cache keys and source-proof guards."""
import importlib.util
from pathlib import Path
import sys

import binding
import state_adapter as A

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def need(ok, why):
    if not ok:
        raise ValueError(why)


def rejects(action):
    try:
        action()
    except (ValueError, AssertionError):
        return
    raise ValueError('Invalid state or proof was accepted')


def run():
    C = load('selected_literal_compiler', 'research/p104-native-channel/vendor/clifford_exact.py')
    V = load('selected_literal_native', 'research/p104-native-channel/vendor/native_verify.py')
    cases = entries = 0
    for n in range(1, 5):
        gates = [('phase', j) for j in range(4)]
        gates += [('X', q) for q in range(1 << n)]
        gates += [('C', q, s) for q in range(1, 1 << n) for s in (-1, 1)]
        gates += [('P', tuple(1 << ((i + shift) % n) for i in range(n))) for shift in range(n)]
        for mask in range(1 << n):
            rows = tuple((1 << i) if mask >> i & 1 else 0 for i in range(n))
            gates.append(('D', rows, tuple((mask >> i) & 1 for i in range(n))))
        for j in range(len(gates)):
            circuit = tuple(gates[k % len(gates)] for k in (j, 3 * j + 1, 7 * j + 2))
            operator = C.Op(n, V.tableau(circuit, n), list(circuit))
            for initial in range(1 << n):
                expected = operator.zero_state(initial)
                need(A.dense_state(n, circuit, initial) == expected, 'Literal dense amplitude or denominator')
                cases += 1
                entries += 1 << n
    for initial in (0, 1, 17, 511):
        circuit = (('C', 511, 1), ('C', 17, -1), ('phase', 3), ('X', 39))
        need(A.sparse_state(circuit, initial) == V.state(circuit, initial), 'Literal sparse state')
        cases += 1
        entries += 512

    A.signature.cache_clear()
    circuit = [['C', 1, 1]]
    first = A.dense_state(2, circuit)
    need(A.signature.cache_info().misses == 1, 'Cold cache')
    need(A.dense_state(2, circuit) == first and A.signature.cache_info().hits == 1, 'Exact key reuse')
    circuit.append(['phase', 1])
    need(A.dense_state(2, circuit) != first and A.signature.cache_info().misses == 2, 'Changed gate invalidates')
    need(A.dense_state(2, circuit, 2) != A.dense_state(2, circuit, 0), 'Changed initial basis invalidates')
    need(len(A.dense_state(3, circuit)[0]) == 8, 'Changed width invalidates')
    # Numeric aliases must fail even after their integer counterpart is cached.
    A.dense_state(1, [('X', 1)], 0)
    for n, gates, initial in ((True, [('X', 1)], 0), (1, [('X', True)], 0),
                              (1, [('X', 1)], False), (1, [('X', 1.0)], 0)):
        rejects(lambda n=n, gates=gates, initial=initial: A.dense_state(n, gates, initial))
    matrix = [[1, 2]]
    A.dense_state(2, [('P', matrix[0])])
    matrix[0][0] = 0
    rejects(lambda: A.dense_state(2, [('P', matrix[0])]))
    dense, _ = A.dense_state(2, [('C', 1, 1)])
    dense[0] = (99, 99)
    need(A.dense_state(2, [('C', 1, 1)])[0][0] != (99, 99), 'Dense output cannot mutate cache')
    sparse, _ = A.sparse_state((('phase', 0),))
    sparse.clear()
    need(A.sparse_state((('phase', 0),))[0] == {0: (1, 0)}, 'Sparse output cannot mutate cache')
    for phase in range(8200):
        A.dense_state(0, [('phase', phase)])
    need(A.signature.cache_info().currsize == 8192, 'Bounded cache capacity')
    misses = A.signature.cache_info().misses
    A.dense_state(0, [('phase', 0)])
    need(A.signature.cache_info().misses == misses + 1, 'Evicted key is recomputed')

    native = (binding.HERE / 'native_fast.py').read_text()
    rejects(lambda: binding.check({'native_fast.py': native.replace(
        'require(state(actual) == state(expected),', 'require(True,')}))
    source = (binding.HERE / 'verify_source.py').read_text()
    rejects(lambda: binding.check({'verify_source.py': source.replace(
        'costs = P.run(local, native, controller, physical)', 'costs = {}')}))
    local = (binding.HERE / 'local_fast.py').read_text()
    rejects(lambda: binding.check({'local_fast.py': local.replace(
        "need(row == expected, 'All public and owned rows')", 'pass')}))
    fast = load('selected_derived_compiler_check', 'research/selected-quadratic-replay/clifford_fast.py')
    rejects(lambda: fast.ident(1).then(fast.ident(2)))
    A.signature.cache_clear()
    A.COUNTS.clear()
    return {'literal_state_cases': cases, 'literal_amplitude_entries': entries,
            'cache_controls': 'Complete keys, type aliases, changed inputs, output mutation, capacity and eviction',
            'proof_controls': 3, 'explicit_assertion_control': 'Mismatched widths reject, including under -O'}
