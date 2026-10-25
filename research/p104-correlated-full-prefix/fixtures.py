"""Full physical 2,040-event fixtures, including a nonzero dirty baseline.

This finite replay is separate from the quantified module proof. Apache-2.0.
"""

import json
import sys
from fractions import Fraction

from engine import (HERE, ZERO, digest, load, monomial, native, need, plan)


def initial(word, masks):
    state = {}
    for index, name in enumerate(sorted(word['initial_frames'])):
        mask = (index * 37) % 512
        reserve = 4 if name.startswith('Y') else 2 if name.startswith('N') else 0
        state[name] = monomial(mask, mask.bit_count() + reserve)
    y = [ZERO] * 512
    for mask in masks:
        term = monomial(mask, mask.bit_count() + 3)
        y = [(a + c, b + d) for (a, b), (c, d) in zip(y, term, strict=True)]
    state['Y27'] = y
    state['Y26'] = [(-a, -b) for a, b in y]
    return state


def scalar_add(dst, source, coefficient, event):
    p, q = Fraction(coefficient).as_integer_ratio()
    need(all(p * v % q == 0 for z in source for v in z),
         f'event {event} nonintegral ADD product')
    return [(a + p * c // q, b + p * d // q)
            for (a, b), (c, d) in zip(dst, source, strict=True)]


def run(word, recipes, state, wrong_cleanup=False):
    for event, row in enumerate(word['program'][:2040]):
        op, dst = row[:2]
        if op == 'transport':
            recipe = recipes[event]
            ready = {**recipe, 'left_plan': plan(recipe['left']),
                     'right_plan': plan(recipe['right'])}
            state[dst] = native(state[dst], ready)
        elif op == 'add':
            coefficient = -Fraction(row[3]) if wrong_cleanup and event == 2038 else row[3]
            state[dst] = scalar_add(state[dst], state[row[2]], coefficient, event)
        elif op == 'sign':
            need(row[2] == '-1', 'literal sign')
            state[dst] = [(-a, -b) for a, b in state[dst]]
        elif op == 'zero':
            need(dst not in state, 'owned private initialization')
            state[dst] = [ZERO] * 512
        elif op == 'erase':
            need(all(z == ZERO for z in state[dst]), 'strict private zero erasure')
            del state[dst]
        else:
            raise ValueError('unsupported full-fixture opcode')
    need('C' not in state and len(state) == 358, 'persistent endpoint inventory')
    return digest(state)


def calculate():
    word, recipes = load()
    masks = [0, 162, 170, 490, 506, 507, 510]
    state = initial(word, masks)
    before = digest(state)
    after = run(word, recipes, state)
    try:
        run(word, recipes, initial(word, masks), wrong_cleanup=True)
    except ValueError as exc:
        need(str(exc) == 'strict private zero erasure', 'wrong-cleanup rejection location')
    else:
        raise ValueError('wrong cleanup accepted')
    return {'literal_events': 2040, 'initial_fields': 358, 'initial_sha256': before,
            'final_sha256': after, 'all_ADD_products_and_native_prefixes_exact': True,
            'strict_private_zero_erasure': True, 'wrong_cleanup_rejected': True}


def main():
    need(sys.argv[1:] in ([], ['--emit']), 'usage: fixtures.py [--emit]')
    result = calculate()
    if sys.argv[1:] == ['--emit']:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    with (HERE / 'FIXTURES.json').open('rb') as handle:
        raw = handle.read(1024 * 1024 + 1)
    need(len(raw) <= 1024 * 1024 and digest(json.loads(raw)) == digest(result),
         'full-fixture receipt mismatch')
    print('PASS_P104_FULL_PREFIX_PHYSICAL_FIXTURE events=2040 cleanup=exact')


if __name__ == '__main__':
    main()
