"""Deterministic abstract tests; no source/native replay, files, or subprocesses."""
from collections import Counter
from itertools import product
import json
import sys
sys.dont_write_bytecode = True
import accounting as A


def need(ok, message):
    if not ok:
        raise ValueError(message)


def reject(label, call):
    try:
        call()
    except ValueError:
        return
    raise ValueError('invalid argument accepted: ' + label)


def compositions(total, length):
    if length == 1:
        yield (total,)
    else:
        for n in range(total+1):
            for tail in compositions(total-n, length-1):
                yield (n,) + tail


def make_groups(sizes, kinds, rotation=0):
    R, start, groups = sum(sizes), 0, []
    for size, common in zip(sizes, kinds):
        ids = tuple((i+rotation) % R for i in range(start, start+size))
        groups.append(A.Group('local_cover_sweep' if common else 'idle',
                              'low-major' if common else 'id-major', ids, common))
        start += size
    return tuple(groups)


def reference_word(groups, rho, N, wrong_order=False):
    """Stable-sort construction independent of projected_keys' nested loops."""
    need(rho*sum(len(g.request_ids) for g in groups)*N <= 64, 'reference history bound')
    word = []
    for g in groups:
        block = [(identifier, g.common, b) for identifier in g.request_ids for b in range(N)]
        if g.order == 'low-major' and not wrong_order:
            block.sort(key=lambda key: key[2])
        word.extend(block*rho)
    return tuple(word)


def wrapper_model(word):
    """Per-birth identities under the audited fresh-wrapper contract, not source execution.

    Only begin/end references are modeled; no assumptions about plan/block storage.
    All identities remain live, so object IDs cannot be recycled during the check.
    """
    need(len(word) <= 64, 'wrapper history bound')
    births = [(key, object()) for key in word]
    code = [(tag, wrapper) for _, wrapper in births for tag in ('begin', 'end')]
    uses = Counter(id(wrapper) for _, wrapper in code)
    need(len(uses) == len(births) and all(n == 2 for n in uses.values()), 'fresh retained identities')
    need(all(code[2*i][1] is code[2*i+1][1] for i in range(len(births))), 'paired references')
    return dict(fresh_residual_objects=len(births), retained_residual_objects=len(uses),
                begin_references=sum(tag == 'begin' for tag, _ in code),
                end_references=sum(tag == 'end' for tag, _ in code),
                begin_end_references=len(code)), Counter(key for key, _ in births)


def check_schedule(groups, rho, N):
    word = reference_word(groups, rho, N)
    need(tuple(A.projected_keys(groups, rho, N)) == word, 'group/replica/LOW/ID order')
    counts, born_keys = wrapper_model(word)
    got = A.visit_invoice(groups, rho, N)
    need(got['source_visits'] == len(word) and got['distinct_keys'] == len(Counter(word)), 'T/M census')
    need(born_keys == Counter(word) and set(born_keys.values()) == {rho}, 'per-key multiplicity')
    need(got['key_multiplicity'] == rho, 'multiplicity invoice')
    need(all(got[k] == v for k, v in counts.items()), 'fresh wrappers and begin/end refs')
    need(got['block_references'] is None and got['total_reference_formula'] == '2*T+B', 'B uncounted')


def run():
    cases = histories = 0
    # Exhaust weak group compositions, kinds, cyclic ID placements, rho and N.
    for R, length in product(range(1, 4), range(1, 4)):
        for sizes in compositions(R, length):
            for kinds, rotation in product(product((False, True), repeat=length), range(R)):
                groups = make_groups(sizes, kinds, rotation)
                for rho, N in product(range(1, 4), range(1, 4)):
                    check_schedule(groups, rho, N)
                    cases += 1
    for length in range(5):
        for word in product(range(3), repeat=length):
            counts, born_keys = wrapper_model(word)
            need(counts['retained_residual_objects'] == length and born_keys == Counter(word), 'birth census')
            need(counts['begin_end_references'] == 2*length, 'generic reference count')
            histories += 1
    groups = (A.Group('idle', 'id-major', (2,), False),
              A.Group('local_cover_sweep', 'low-major', (1, 0), True))
    word, mutant = reference_word(groups, 2, 3), reference_word(groups, 2, 3, True)
    need(tuple(A.projected_keys(groups, 2, 3)) == word != mutant, 'wrong-loop-order mutant detected')
    need(word.index((0, True, 0)) == 7 and mutant.index((0, True, 0)) == 9, 'order witness')
    need(Counter(word) == Counter(mutant) and wrapper_model(word) == wrapper_model(mutant),
         'order mutant preserves aggregate counts, key multiplicities and object/reference counts')
    one = (A.Group('local_cover_sweep', 'low-major', (0,), True),)
    check_schedule(one, 1, 64)
    invalid = [
        ('no groups', lambda: A.visit_invoice((), 1, 1)),
        ('not iterable', lambda: A.validate(None, 1)),
        ('not Group', lambda: A.validate(({},), 1)),
        ('all empty', lambda: A.validate(make_groups((0,), (True,)), 1)),
        ('overlap', lambda: A.validate(one+one, 1)),
        ('gapped IDs', lambda: A.validate((A.Group('idle', 'id-major', (0, 2), False),), 1)),
        ('boolean ID', lambda: A.validate((A.Group('idle', 'id-major', (False,), False),), 1)),
        ('negative ID', lambda: A.validate((A.Group('idle', 'id-major', (-1,), False),), 1)),
        ('IDs not tuple', lambda: A.validate((A.Group('idle', 'id-major', [0], False),), 1)),
        ('common not bool', lambda: A.validate((A.Group('idle', 'id-major', (0,), 0),), 1)),
        ('wrong order', lambda: A.validate((A.Group('local_cover_sweep', 'id-major', (0,), True),), 1)),
        ('wrong kind', lambda: A.validate((A.Group('other', 'low-major', (0,), True),), 1)),
        ('boolean rho', lambda: A.visit_invoice(one, True, 1)),
        ('zero rho', lambda: A.visit_invoice(one, 0, 1)),
        ('negative rho', lambda: A.visit_invoice(one, -1, 1)),
        ('boolean N', lambda: A.visit_invoice(one, 1, True)),
        ('noninteger N', lambda: A.visit_invoice(one, 1, 1.0)),
        ('zero N', lambda: A.visit_invoice(one, 1, 0)),
        ('negative N', lambda: A.visit_invoice(one, 1, -1)),
        ('total history bound', lambda: tuple(A.projected_keys(one, 2, 33))),
    ]
    for label, call in invalid:
        reject(label, call)
    return dict(status='PASS', scope='public grouped visits and fresh wrappers; block references uncounted',
                schedule_cases=cases, generic_history_cases=histories, rejected_inputs=len(invalid),
                max_exhaustive_calls=27, boundary_calls=64, per_birth_identity_checked=True,
                order_mutant_detected_with_unchanged_counts=True)


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True))
