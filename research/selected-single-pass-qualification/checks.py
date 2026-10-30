"""Small real-adapter feasibility and adversarial orchestration controls."""
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import importlib.util
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace

from orchestration import qualify, require
from source import prepared


def fixture(adapter, C, V, fault=None):
    circuits = [(('phase', 1), ('X', 1)), (('C', 3, 1), ('phase', 2)), ()]
    keys = [(9, circuits[0], 0), (9, circuits[1], 17), (9, circuits[2], 511)]
    events = []
    result = {}

    def replay(argv):
        events.append('source')
        for key in [*keys, keys[0]]:
            adapter.dense_state(*key)
        return 'source-return'

    source = SimpleNamespace(main=replay)

    def verify():
        events.append('controls')
        adapter.dense_state(1, [('phase', 3)])
        adapter.signature.cache_clear()
        adapter.COUNTS.clear()
        if fault == 'control_contamination':
            adapter.TRACE = {('synthetic-control',)}
        if fault == 'dirty_counter':
            adapter.COUNTS['dirty'] = 1
        if fault != 'omit_source':
            require(source.main([1] if fault == 'source_argv' else []) == 'source-return'
                    or source.main is not replay, 'Forwarded source return')
        if fault == 'repeat_source':
            source.main([])
        if fault == 'verify_exception':
            raise RuntimeError('sentinel verify exception')
        result['verify'] = {'counts': dict(adapter.COUNTS), 'cache': adapter.signature.cache_info()._asdict()}

    def cross():
        if fault == 'counter_leak':
            adapter.COUNTS['dirty'] = 1
        if fault == 'cache_leak':
            adapter.signature(1, (), 0)
        adapter.TRACE = {('stale',)} if fault == 'stale_cross' else set()
        if fault != 'omit_handoff':
            source.main([1] if fault == 'cross_argv' else [])
        if fault == 'repeat_handoff':
            source.main([])
        trace = sorted(adapter.TRACE)
        adapter.TRACE = None
        calls = dict(adapter.COUNTS)
        oracle_entries = 0
        for n, circuit, initial in trace:
            literal = C.Op(n, V.tableau(circuit, n), list(circuit)).zero_state(initial)
            require(adapter.dense_state(n, circuit, initial) == literal, 'Tiny dense exact amplitudes')
            expected = ({i: pair for i, pair in enumerate(literal[0]) if pair != (0, 0)}, literal[1])
            require(adapter.sparse_state(circuit, initial) == expected == V.state(circuit, initial),
                    'Tiny sparse and second literal amplitudes')
            oracle_entries += 1 << n
        result['cross'] = {'calls': calls, 'trace': trace, 'entries_per_interpreter': oracle_entries}
        if fault == 'cross_exception':
            raise RuntimeError('sentinel cross exception')

    return source, verify, cross, result, events, replay


def reset(adapter):
    adapter.TRACE = None
    adapter.COUNTS.clear()
    adapter.signature.cache_clear()


def run(root):
    adapter_path = root / 'research/selected-quadratic-replay'
    sys.path.insert(0, str(adapter_path))
    import state_adapter as A
    import checks as collision_guard
    # This module is executed as __main__; load the retained helper by a distinct name.
    spec = importlib.util.spec_from_file_location('retained_checks', adapter_path / 'checks.py')
    retained = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(retained)
    C = retained.load('tiny_literal_compiler', 'research/p104-native-channel/vendor/clifford_exact.py')
    V = retained.load('tiny_literal_native', 'research/p104-native-channel/vendor/native_verify.py')
    reset(A)
    source, verify, cross, expected, baseline_events, original = fixture(A, C, V)
    verify()
    reset(A)  # The legacy second command starts in a fresh interpreter.
    cross()
    require(baseline_events == ['controls', 'source', 'source'], 'Legacy duplicate execution fixture')
    reset(A)
    source, verify, cross, actual, events, original = fixture(A, C, V)
    receipt = qualify(verify, cross, source, A)
    require(actual == expected, 'Complete tiny receipts unchanged')
    require(events == ['controls', 'source'], 'Single actual execution')
    require(source.main is original and A.TRACE is None, 'Successful instrumentation restoration')
    require(receipt['source_executions'] == receipt['trace_handoffs'] == 1, 'One execution and one handoff')
    require(receipt['distinct_inputs'] == 3 and actual['cross']['entries_per_interpreter'] == 1536,
            'Every tiny input and all amplitudes retained')
    controls = {}
    for fault, predicate in {
        'control_contamination': 'No control trace contamination',
        'dirty_counter': 'Controls reset state counters',
        'omit_source': 'Complete verify entry point',
        'repeat_source': 'Exactly one source execution',
        'source_argv': 'Exact source arguments',
        'counter_leak': 'Unchanged pre-oracle counters',
        'cache_leak': 'Unchanged pre-oracle cache',
        'stale_cross': 'Fresh cross observer',
        'omit_handoff': 'Complete cross entry point',
        'repeat_handoff': 'One trace handoff',
        'cross_argv': 'Exact cross source arguments',
        'verify_exception': 'sentinel verify exception',
        'cross_exception': 'sentinel cross exception',
    }.items():
        reset(A)
        source, verify, cross, _, _, original = fixture(A, C, V, fault)
        try:
            qualify(verify, cross, source, A)
        except (ValueError, RuntimeError) as error:
            require(str(error) == predicate, 'Exact intended fault predicate: ' + fault + ': ' + str(error))
            controls[fault] = predicate
        else:
            raise ValueError('Fault accepted: ' + fault)
        require(source.main is original and A.TRACE is None, 'Exception instrumentation restoration')
    reset(A)
    return {'tiny_inputs': 3, 'amplitudes_per_interpreter': 1536,
            'literal_interpreters': 2, 'complete_tiny_receipts_equal': True,
            'controls': controls, 'source_executions': 1}


if __name__ == '__main__':
    with prepared() as root:
        result = run(root)
    print('PASS_SINGLE_PASS_SMALL_FEASIBILITY', json.dumps(result, sort_keys=True))
