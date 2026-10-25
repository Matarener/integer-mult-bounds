"""Cost-stage semantic mutation controls; standard library, no network."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from random import Random

HERE = Path(__file__).resolve().parent

def module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def rejects(fn, label):
    try:
        fn()
    except ValueError:
        return
    raise ValueError('mutation accepted: ' + label)

def run():
    primary = module('costs')
    independent = module('independent_costs')
    receipt = json.loads((HERE / 'COSTS.json').read_bytes())
    shapes, _, metadata = primary.geometry(HERE.parents[1])
    primary.validate_metadata(shapes, metadata, receipt)
    no_orders, _, truncated = primary.geometry(HERE.parents[1], orientations=[(0, 1, 2)])
    rejects(lambda: primary.validate_metadata(no_orders, truncated, receipt), 'missing target orientations')
    altered = deepcopy(receipt)
    line_shape = next(i for i, e in enumerate(altered['envelopes']) if 1 in e['dimensions'])
    dimensions = altered['envelopes'][line_shape]['dimensions']
    dimensions[dimensions.index(1)] = 3
    rejects(lambda: primary.validate_metadata(shapes, metadata, altered), 'residual line treated as triad')
    altered = deepcopy(receipt)
    altered['envelopes'].pop()
    rejects(lambda: primary.validate_metadata(shapes, metadata, altered), 'missing shape')
    changed_shapes = deepcopy(shapes)
    old = changed_shapes[0]['table']
    changed_shapes[0]['table'] = bytes([old[0] ^ 1]) + old[1:]
    rejects(lambda: primary.validate_metadata(changed_shapes, metadata, receipt), 'changed physical tariff')

    random = Random(296)
    examples = []
    for _ in range(80):
        n = random.randrange(2, 6)
        table = [0] * (n * n)
        for i in range(n):
            for j in range(i, n):
                table[i * n + j] = table[j * n + i] = random.randrange(10)
        left = [tuple(random.randrange(n) for _ in range(5)) for _ in range(random.randrange(2, 10))]
        right = [tuple(random.randrange(n) for _ in range(5)) for _ in range(random.randrange(2, 10))]
        examples.append((bytes(table), n, left, right))
    examples += [(bytes([v]), 1, [(0,) * 5], [(0,) * 5]) for v in (0, 9)]
    for table, n, left, right in examples:
        minimum = min(sum(table[a * n + b] for a, b in zip(L, R)) for L in left for R in right)
        for verifier in (primary.exact_minimum, independent.verify_minimum):
            verifier(table, n, left, right, minimum)
            rejects(lambda: verifier(table, n, left, right, minimum - 1), 'false smaller minimum')
            rejects(lambda: verifier(table, n, left, right, minimum + 1), 'false larger minimum')
    return {'status': 'passed', 'geometry_mutations_rejected': 4,
            'independent_packed_engines': 2, 'brute_force_arithmetic_cases': len(examples),
            'false_minimum_mutations_rejected': 4 * len(examples)}

if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
