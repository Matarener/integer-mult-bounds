#!/usr/bin/env python3
"""A closed, non-winning hybrid BIT B4 controller over a free group ring.

No stored source or primary checkout is edited. This is a mathematical
comparison word, not a physical supplier admission or new kappa result.
Apache-2.0; prepared with substantial OpenAI Codex assistance.
"""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/Users/ross/git/math/integer-mult-bounds')
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
RECIPE = REPO / ('research/e8-bit-p111-tuned/vendor/pr510/'
    'e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py')


def need(p, message):
    if not p:
        raise ValueError(message)


def reduce_word(word):
    out = []
    for generator in word:
        if out and out[-1] == -generator:
            out.pop()
        else:
            out.append(generator)
    return tuple(out)


def inverse_word(word):
    return tuple(-x for x in reversed(word))


def add(a, b, coefficient=1):
    out = dict(a)
    for key, value in b.items():
        out[key] = out.get(key, 0) + coefficient * value
        if not out[key]:
            del out[key]
    return out


def left(row, word):
    out = {}
    for (suffix, column), value in row.items():
        key = (reduce_word(tuple(word) + suffix), column)
        out[key] = out.get(key, 0) + value
        if not out[key]:
            del out[key]
    return out


def identity(n=8):
    return [{((), i): 1} for i in range(n)]


def serial(rows):
    return [[[list(word), column, value]
        for (word, column), value in sorted(row.items())] for row in rows]


def recipe():
    raw = RECIPE.read_bytes()
    tree = ast.parse(raw)
    function = next(x for x in tree.body
        if isinstance(x, ast.FunctionDef) and x.name == 'recipe')
    env = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]),
        str(RECIPE), 'exec'), env)
    events = env['recipe'](4)
    need(len(events) == 19, 'actual B4 event count')
    return events, sha256(raw).hexdigest()


def old_word(events):
    return [dict(e, coded=False) if e['kind'] == 'local' else dict(e)
        for e in events]


def hybrid_word(events, mutation=None):
    out = []
    for event in events:
        if event['kind'] == 'local':
            stage = event['stage']
            coded = stage in (0, 1)
            if mutation == 'stale_coded_F2' and stage == 2:
                coded = True
            out.append(dict(event, coded=coded))
            if stage in (0, 1):
                if mutation == 'omit_current_B_pullback' and stage == 1:
                    continue
                out.append({'kind': 'code', 'register': 0,
                    'word': [-(stage + 1)],
                    'cut': 'immediately after local' + str(stage),
                    'side': 'X', 'native_level': stage})
        elif event['kind'] == 'exchange':
            out.append({'kind': 'normalize', 'register': 1,
                'direction': 'cap_to_FULL', 'rank_one_children': 111})
            out.append({'kind': 'code', 'register': 1, 'word': [2],
                'cut': 'terminal after all idle owners return',
                'side': 'FULL', 'native_level': 8})
            out.append({'kind': 'code', 'register': 0, 'word': [2],
                'cut': 'terminal after all idle owners return',
                'side': 'FULL', 'native_level': 8})
            out.append({'kind': 'shear', 'dst': 0, 'src': 1,
                'coefficient': -1})
            out.append({'kind': 'code', 'register': 1, 'word': [1],
                'cut': 'terminal source preparation',
                'side': 'FULL', 'native_level': 8})
            out.append({'kind': 'shear', 'dst': 0, 'src': 1,
                'coefficient': -1 if mutation == 'wrong_compensation_sign' else 1})
            out.append({'kind': 'code', 'register': 1, 'word': [-1],
                'cut': 'terminal exact source unprepare',
                'side': 'FULL', 'native_level': 8})
            out.append({'kind': 'normalize', 'register': 1,
                'direction': 'FULL_to_cap', 'rank_one_children': 111})
            out.append(dict(event))
        else:
            out.append(dict(event))
    return out


def apply(rows, event, backwards=False):
    rows = [dict(row) for row in rows]
    k = event['kind']
    if k == 'local':
        p, s, rev = event['pair'], event['stage'], event['reverse']
        i, j = 2 * p, 2 * p + 1
        x, y = rows[i], rows[j]
        a = (s + 1,) if event.get('coded') else ()
        if not rev:
            if not backwards:
                rows[i] = left(x, a)
                rows[j] = add(y, rows[i])
            else:
                rows[j] = add(y, x, -1)
                rows[i] = left(x, inverse_word(a))
        elif not backwards:
            rows[i] = add(x, y, -1)
            rows[j] = left(y, inverse_word(a))
        else:
            rows[j] = left(y, a)
            rows[i] = add(x, rows[j])
    elif k == 'bridge':
        d, s = event['dst'], event['src']
        coefficient = event['coefficient'] * (-1 if backwards else 1)
        rows[2*d] = add(rows[2*d], rows[2*s], coefficient)
        rows[2*s+1] = add(rows[2*s+1], rows[2*d+1], -coefficient)
    elif k == 'code':
        word = tuple(event['word'])
        if backwards:
            word = inverse_word(word)
        rows[event['register']] = left(rows[event['register']], word)
    elif k == 'shear':
        coefficient = event['coefficient'] * (-1 if backwards else 1)
        rows[event['dst']] = add(rows[event['dst']],
            rows[event['src']], coefficient)
    elif k == 'exchange':
        rows = [row for p in range(4) for row in
            (rows[2*p+1], rows[2*p])]
    elif k == 'normalize':
        # Logical-value coordinate is unchanged; native D_P changes frame.
        # Native physical validity and its rank-one tariff are conditional.
        pass
    else:
        raise ValueError(k)
    return rows


def evaluate(word, start=None, backwards=False):
    rows = identity() if start is None else start
    for event in reversed(word) if backwards else word:
        rows = apply(rows, event, backwards)
    return rows


def transpose_operator_word(word):
    # a_s^T is an independent noncommuting generator, not a_s^-1.
    # The operation reverses multiplication order and preserves exponents.
    return tuple((1 if x > 0 else -1) * (abs(x)+9)
        for x in reversed(word))


def transpose_operators(rows):
    out = [{} for _ in range(len(rows))]
    for i, row in enumerate(rows):
        for (word, j), value in row.items():
            out[j][(transpose_operator_word(word), i)] = value
    return out


def product(a, b):
    out = []
    for row in a:
        value = {}
        for (word, j), coefficient in row.items():
            value = add(value, left(b[j], word), coefficient)
        out.append(value)
    return out


def receipt():
    events, recipe_pin = recipe()
    old = old_word(events)
    word = hybrid_word(events)
    target = evaluate(old)
    out = evaluate(word)
    need(out == target, 'exact all-input old-clean endpoint equality')
    need(evaluate(word, out, backwards=True) == identity(),
        'literal reverse-inverse cleanup')
    need(evaluate(word, identity(), backwards=True) == target,
        'inverse target endpoint')
    # The old clean signed word ends (Xout,Yout)=(x,-y), not literal Z identity.
    expected = identity()
    for i in range(1, 8, 2):
        expected[i] = {key: -value for key, value in expected[i].items()}
    need(target == expected, 'all clean signed controller target')
    need(product(out, evaluate(word, identity(), True)) == identity(),
        'independent matrix multiplication inverse')
    # Compare chronological gatewise inverse-transpose propagation to the
    # transpose of the complete inverse. Transpose generators are independent.
    inverse = evaluate(word, identity(), True)
    inverse_transpose = transpose_operators(inverse)
    need(product(transpose_operators(out), inverse_transpose) == identity(),
        'free-ring independent transpose inverse')
    gatewise_dual = identity()
    for event in word:
        gatewise_dual = product(transpose_operators(apply(identity(), event, True)),
            gatewise_dual)
    need(gatewise_dual == inverse_transpose,
        'chronological gatewise inverse-transpose propagation')
    controls = []
    for mutation in ('omit_current_B_pullback', 'wrong_compensation_sign',
                     'stale_coded_F2'):
        bad_word = hybrid_word(events, mutation)
        need(bad_word != word, 'mutation changed actual word')
        bad = evaluate(bad_word)
        need(bad != target, 'affected endpoint mutant rejected')
        delta = [add(a, b, -1) for a, b in zip(bad, target)]
        controls.append({'mutation': mutation, 'rejected': True,
            'first_bad_output': next(i for i, row in enumerate(delta) if row),
            'defect': serial(delta)})
    wrong_inverse, changed = out, False
    for event in reversed(word):
        if event['kind'] == 'code' and not changed:
            wrong_inverse = apply(wrong_inverse, event, backwards=False)
            changed = True
        else:
            wrong_inverse = apply(wrong_inverse, event, backwards=True)
    need(changed and wrong_inverse != identity(), 'wrong inverse code direction')
    controls.append({'mutation': 'one_code_uses_forward_instead_of_inverse',
        'rejected': True,
        'control_note': 'Repeating the whole forward endpoint is a vacuous control here because the signed target is involutive; one actual inverse gate is changed instead.'})
    # State just before the terminal normalization is an informative witness.
    before = []
    for event in word:
        if event['kind'] == 'normalize':
            break
        before.append(event)
    partial = evaluate(before)
    x0 = add(left(identity()[0], (-2,)),
        left(identity()[0], (-2, 1)), -1)
    x0 = add(x0, left(identity()[1], (-2,)), -1)
    need(partial[0] == x0 and partial[1] == left(identity()[0], (-2,)),
        'current-word terminal pullbacks')
    for p in range(1, 4):
        need(partial[2*p] == {key: -value for key, value in identity()[2*p+1].items()}
            and partial[2*p+1] == identity()[2*p], 'other identity slots')
    source_applications = sum(len(e['word']) for e in word if e['kind'] == 'code')
    n = 111
    return {
        'status': 'PASS_CLOSED_NONCOMMUTATIVE_HYBRID_NO_GAIN',
        'scientific_pin': PIN, 'recipe_source_sha256': recipe_pin,
        'formal_input_rows': 8, 'coefficient_ring': 'Z[free group(a0,...,a8)]',
        'operator_relations': 'only a_s^-1 a_s=a_s a_s^-1=1; no commutation',
        'dual_relations': 'a_s^T are independent transpose symbols, not inverse symbols; chronological gatewise inverse-transpose matches transpose of full inverse',
        'local_coded_stages': [0, 1], 'local_clean_stages': list(range(2, 9)),
        'terminal_before_decoder': serial(partial), 'endpoint': serial(out),
        'word': word, 'controls': controls,
        'invoice_per_replica': {
            'clean_replacements_from_fullycoded': 7,
            'additional_private_rank_one_equivalent': 7*60,
            'terminal_normalization_rank_one_children': 2*n,
            'total_extra_rank_one_equivalent': 7*60+2*n,
            'necessary_allowance_at_beta_002': 492,
            'necessary_allowance_at_beta_003': 309,
            'excess_over_beta_002_allowance': 7*60+2*n-492,
            'net_rank_mass_saved_vs_all_old_clean': 2*60-2*n,
            'source_code_applications': source_applications,
            'R429_1499_ADD_code_scalar_invoice': source_applications*1499+2*n,
            'new_private_or_arbitrary_helper_fields_for_controller': 0,
            'original_terminal_idle_split': False},
        'scope': ['all eight independent public logical input banks, arbitrary values',
            'old local ordinary dirty helper restoration used as explicit premise',
            'actual complete 19-event B4 order including both bridge signs',
            'exact group-ring coefficient and reverse-inverse proof; characteristic2 specialization valid',
            'terminal two-N physical realization and local old/code tariffs are conditional source mechanisms'],
        'unresolved': ['no native global phase admission',
            'no mixed 438/429 helper owner allocation or full width/stock moment',
            'no source-access, precision, tape or outer all-size theorem',
            'fails the necessary beta002 budget, so not a positive kappa candidate']}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    data = receipt()
    path = HERE / 'CLOSED-HYBRID.json'
    if args.write:
        path.write_text(json.dumps(data, sort_keys=True, indent=2)+'\n')
    else:
        need(json.loads(path.read_bytes()) == data, 'stored receipt differs')
    print(data['status'])
    print('extra642 > allowance492; rank-saving vs old = -102; all8 inputs restored')


if __name__ == '__main__':
    main()
