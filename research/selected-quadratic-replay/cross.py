"""Compare every actual state input with both retained literal interpreters."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pins import authenticate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--record', action='store_true')
    args = parser.parse_args()
    authenticate()
    import binding
    import checks
    import state_adapter as A
    import verify_source
    binding.check()
    A.TRACE = set()
    verify_source.main([])
    trace = sorted(A.TRACE)
    A.TRACE = None
    calls = dict(A.COUNTS)
    C = checks.load('selected_cross_literal_compiler', 'research/p104-native-channel/vendor/clifford_exact.py')
    V = checks.load('selected_cross_literal_native', 'research/p104-native-channel/vendor/native_verify.py')
    entries = 0
    for n, circuit, initial in trace:
        checks.need(n == 9, 'Actual selected native width')
        literal = C.Op(n, V.tableau(circuit, n), list(circuit)).zero_state(initial)
        checks.need(A.dense_state(n, circuit, initial) == literal, 'Actual dense amplitude and denominator')
        expected = ({i: pair for i, pair in enumerate(literal[0]) if pair != (0, 0)}, literal[1])
        checks.need(A.sparse_state(circuit, initial) == expected == V.state(circuit, initial),
                    'Actual sparse amplitudes and both literal denominators')
        entries += 1 << n
    result = {'actual_state_calls': calls, 'distinct_inputs': len(trace),
              'amplitudes_per_literal_interpreter': entries, 'literal_interpreters': 2,
              'input_trace_sha256': sha256(json.dumps(trace, separators=(',', ':')).encode()).hexdigest()}
    path = HERE / 'CROSS.json'
    if args.record:
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    elif result != json.loads(path.read_bytes()):
        raise ValueError('Actual selected state coverage changed')
    print('PASS_ALL_SELECTED_LITERAL_STATES', json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
