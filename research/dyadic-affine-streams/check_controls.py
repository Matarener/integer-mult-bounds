"""Independent fragment identities and actual behavioral rejection controls."""
from itertools import product
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import fused_sources
fused_sources.activate()
from cardinal_counts import Count
from words import need
from fused_adapter import fuse
import affine


def reject(call, fragment):
    try:
        call()
    except ValueError as error:
        need(fragment in str(error), 'intended rejection: ' + str(error))
        return
    raise ValueError('mutation unexpectedly accepted: ' + fragment)


def evaluate(operations, values, q):
    values = list(values)
    for operation in operations:
        kind, t, *args = operation
        if kind == 'affine':
            a, c, inverse = args
            values[t] = pow(a, -1, q)*(values[t]-c) if inverse else a*values[t]+c
        elif kind == 'translate':
            values[t] += args[0]
        elif kind == 'double':
            values[t] *= 2
        elif kind == 'half':
            values[t] *= pow(2, -1, q)
        elif kind == 'negate':
            values[t] = -values[t]
        elif kind == 'swap':
            values[t], values[args[0]] = values[args[0]], values[t]
        elif kind == 'add':
            values[t] += args[1]*values[args[0]]
        else:
            raise ValueError('unknown oracle factor')
        values[t] %= q
    return tuple(values)


def fragment_checks():
    total = 0
    for q, inverse, amount, steps in product((3, 5, 7, 9, 17), (False, True), range(-4, 5), (1, 2)):
        scale = (('half' if inverse else 'double', 0),)*steps
        translation = (('translate', 0, amount),) if amount else ()
        word = translation+scale if inverse else scale+translation
        # The second field deliberately breaks fusion; its contents remain observable.
        word += (('double', 1), ('translate', 0, -1), ('half', 1), ('swap', 0, 1),
                 ('add', 0, 1, -2), ('negate', 0))
        optimized = fuse(word)
        need(fuse(optimized) == optimized, 'idempotent exact local fusion')
        for values in product(range(q), repeat=2):
            need(evaluate(word, values, q) == evaluate(optimized, values, q), 'independent fragment map')
            total += 1
    return total


def run():
    check = fused_sources.load('affine_kernel_controls', 'research/dyadic-affine-streams/check_affine.py')
    identities = fragment_checks()
    split = 0
    for q in range(3, 258, 2):
        count = Count.literal(q)
        try:
            for amount in range(-4, 5):
                need(affine.bounded_residue(count, amount) == abs(amount) % q, 'bounded finite-control residue')
                split += 1
        finally:
            count.close()
    reject(lambda: check.one_case(5, 2, 3, 4, -3, False, True, wrong_offset=True), 'independent input columns')
    reject(lambda: check.one_case(5, 2, 3, 4, -3, False, True, wrong_offset=True, zero_payload=True),
           'independent input columns')
    reject(lambda: check.one_case(5, 2, 3, 4, -3, True, True, extra_bit=True), 'complete affine source')
    reject(lambda: check.one_case(7, 2, 3, 2, 1, False, True, wrong_direction=True), 'independent input columns')
    good, _ = check.one_case(81, 2, 3, 4, -4, False, True, capacity=20)
    need(good['scratch'] == 17, 'seventeen free roles are sufficient and attained')
    reject(lambda: check.one_case(81, 2, 3, 4, -4, False, True, capacity=19), 'inventory exhausted')
    for multiplier, amount, inverse, fragment in [(3, 1, False, 'multiplier'), (True, 1, False, 'multiplier'),
                                                (2, 5, False, 'offset'), (2, True, False, 'offset'),
                                                (2, 1, 1, 'direction')]:
        reject(lambda: affine.transformed(None, None, None, None, multiplier, amount, None, inverse), fragment)
    original = affine.transformed

    def extra_read(source, *args, **kwargs):
        source.read()
        return original(source, *args, **kwargs)

    with patch.object(affine, 'transformed', extra_read):
        changed, _ = check.one_case(81, 2, 3, 4, -4, False, True)
    need(changed['total'] == good['total']+1 and changed['physical']['reads'] == good['physical']['reads']+1,
         'endpoint-preserving traffic defect detected')
    first = next(row for row in json.loads((fused_sources.HERE/'SOURCES.json').read_text())['files']
                 if row['usage'] == 'input')
    with TemporaryDirectory() as path:
        root = Path(path)
        target = root/first['path']
        target.parent.mkdir(parents=True)
        target.write_bytes((fused_sources.ROOT/first['path']).read_bytes()+b'\n')
        reject(lambda: fused_sources.authenticate(root), 'source changed')
    return dict(fragment_cases=identities, bounded_residue_cases=split, controls=12, scratch_peak=17)
