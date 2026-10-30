"""Compare every actual native state to the frozen literal-vector evaluator."""
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from pins import authenticate
import binding
import quadratic as Q


def run():
    authenticate(); binding.run()
    import verify_source
    states = entries = 0
    digest = sha256()

    def equal(left, right):
        nonlocal states, entries
        if left.n != right.n or left.tab != right.tab:
            return False
        certificates = []
        for op in (left, right):
            state = Q.signature(op.n, op.circuit)
            n, offset, columns, terms, real, imag, den = state
            vector = [(0, 0)] * (1 << n)
            poly = dict(terms)
            for argument in range(1 << len(columns)):
                index = offset
                for bit in Q.bits(argument):
                    index ^= columns[bit]
                vector[index] = Q.multiply_i((real, imag), Q.value(poly, argument))
            Q.need((vector, den) == op.zero_state(), 'Complete actual literal-vector cross-check')
            digest.update(json.dumps(state, separators=(',', ':')).encode())
            certificates.append(state); states += 1; entries += len(vector)
        return certificates[0] == certificates[1]

    result = verify_source.run(equal)
    Q.need(result == json.loads((ROOT / 'source/RESULT.json').read_text()), 'Complete old scientific result')
    return dict(status='PASS_ALL_ACTUAL_NATIVE_STATES', state_evaluations=states,
                amplitude_entries=entries, canonical_digest=digest.hexdigest(),
                scientific_result_sha256=sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest())


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write']:
        (ROOT / 'CROSS.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        Q.need(not sys.argv[1:], 'No unknown arguments')
        Q.need(result == json.loads((ROOT / 'CROSS.json').read_text()), 'Complete actual-state receipt')
    print(result['status'])
