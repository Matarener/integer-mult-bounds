"""Check the retained operand, native word, complete price and compiler.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The source chain and price follow PR6144 by DreamingOfClouds and PR5827 by
Ali Romman. NOTICE retains the earlier construction and checker credits.
"""
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
from pathlib import Path
import json
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sources import sources, source_bytes, base_word, load, need, read, authenticate
from construct import construct, matches_shipped

STATUS = 'PASS_P104_RETAINED_OPERAND_KAPPA_003128645'
PROTECTED = {41, 42, 65, 106, 240, 400, 401, 403, 405, 410, 741,
             57, 81, 92, 224, 225, 227, 229, 234, 742}


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid control accepted')


def protected_events(word):
    return [e for e in word['program'] if e[1] in PROTECTED or
            (e[0] in ('ADD', 'COPY') and e[2] in PROTECTED)]


def word_controls(L, word):
    out = {}
    edits = [
        ('missing_copy', ['COPY', 770, 228, '1', 737], None),
        ('wrong_copy_sign', ['COPY', 770, 228, '1', 737],
         ['COPY', 770, 228, '-1', 737]),
        ('wrong_root_coefficient', ['ADD', 451, 772, '-4', 595],
         ['ADD', 451, 772, '-2', 595]),
        ('missing_root_move', ['MOVE', 772, 520, 595, True], None),
        ('missing_reader_restoration', ['MOVE', 451, 595, 737, False], None),
        ('missing_late_operand', ['ADD', 451, 770, '1', 737], None),
        ('missing_cache_clear', ['CLEAR', 770, 737], None)]
    for label, event, replacement in edits:
        bad = deepcopy(word)
        need(bad['program'].count(event) == 1, 'Unique control event: ' + label)
        index = bad['program'].index(event)
        bad['program'][index:index+1] = [] if replacement is None else [replacement]
        out[label] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    copy = ['COPY', 770, 228, '1', 737]
    bad['program'].remove(copy)
    index = bad['program'].index(['ADD', 451, 770, '1', 737])
    bad['program'].insert(index, copy)
    out['copy_after_source_departure'] = reject(lambda: L.replay(bad))
    return out


def run(build_only):
    with ExitStack() as contexts:
        parent = contexts.enter_context(sources())
        cursor = contexts.enter_context(load(parent / 'sources.py', 'base_source_top').sources())
        for depth in range(7):
            module = load(cursor / 'sources.py', 'base_source_' + str(depth))
            cursor, root = contexts.enter_context(module.sources())
        text = source_bytes('pricing_source').decode()
        for old, new in read(HERE / 'PRICING-EDITS.json'):
            need(text.count(old) == 1, 'Unique declared pricing edit')
            text = text.replace(old, new)
        need(text == (HERE / 'pricing.py').read_text(), 'Exact declared pricing edits')
        L = load(parent / 'local.py', 'local')
        L.ROOT = root
        source = base_word()
        word = construct(source)
        need(matches_shipped(word, (HERE / 'WORD.json.gz').read_bytes()),
             'Every regenerated payload byte')
        need(all(type(e[4]) is bool for e in word['program'] if e[0] == 'MOVE'),
             'Boolean ownership flags')
        need(protected_events(word) == protected_events(source), 'Protected contact events unchanged')
        baseline, local = L.replay(source), L.replay(word)
        need(local['helpers'] == baseline['helpers'], 'All productive targets unchanged')
        paid_delta = Counter(local['paid'])
        paid_delta.subtract(baseline['paid'])
        paid_delta = {r: n for r, n in paid_delta.items() if n}
        need(paid_delta == {1: 1, 2: -1, 4: -1, 5: 1}, 'Exact local paid change')
        need(tuple(local[k] for k in ('public_inputs', 'owned_fields', 'owned_lifetimes',
                                     'peak_owned_fields', 'real_scalar_allowance')) ==
             (770, 29, 32, 13, 189670), 'Exact storage and scalar inventory')
        need(local['owned_lifetimes'] == baseline['owned_lifetimes'] + 1 and
             local['real_scalar_allowance'] == baseline['real_scalar_allowance'] + 12,
             'Charge the added cache lifetime and scalar work')
        print('PASS regeneration, arbitrary inputs, ownership and paid change', flush=True)
        if build_only:
            return None
        columns = L.reverse_columns(word)
        need(columns['columns'] == 799 and columns['coefficients'] == 638401,
             'Every input column and output coefficient')
        print('PASS separate dense transpose', flush=True)
        native = L.native(word)
        C = load(root / 'research/p104-productive-controller/caller.py', 'base_caller')
        caller = C.construct()
        need(caller == read(root / 'research/p104-productive-controller/CONTROLLER.json'),
             'Exact physical caller')
        physical = C.physical(caller, word)
        print('PASS native maps, absolute phases and complete physical caller', flush=True)
        P = load(HERE / 'pricing.py', 'retained_operand_price')
        price = P.run(local, native, caller, physical)
        need(price['raw_root_interval'] ==
             ['31286520159/10000000000000', '312865201591/100000000000000'],
             'Exact rational crossing interval')
        E = L.load(root / 'research/higher-moment-strictification/verify.py', 'base_price_engine')
        old_paid = {int(r): n for r, n in price['paid'].items()}
        targets = {int(r): n for r, n in price['targets'].items()}
        for rank, count in paid_delta.items():
            old_paid[rank] -= 18 * count
        old_margin = E.moment(targets, 1 - P.KAPPA)[1] - E.moment(old_paid, 1 - P.KAPPA)[0]
        need(old_margin < 0, 'The full PR6144 profile fails at the new claim')
        controls = word_controls(L, word)
        controls.update(C.controls(caller))
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        controls['unpaid_query'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][9] += 1
        controls['extra_target_credit'] = reject(lambda: P.assemble(bad, native, caller, physical))
        for key in ('base_word', 'pricing_source'):
            pin = read(HERE / 'SOURCES.json')[key]
            raw = (HERE / pin['local_path']).read_bytes()
            controls['damaged_' + key] = reject(
                lambda raw=raw, pin=pin: authenticate(bytes([raw[0] ^ 1]) + raw[1:], pin))
        print('PASS two interval engines, all costs, compiler, outer checks and controls', flush=True)
        return P.encode(dict(
            status=STATUS, base_commit=read(HERE / 'SOURCES.json')['base_commit'],
            source_local=baseline, local=local, paid_delta=paid_delta,
            separate_columns=columns, native=native, physical_caller=physical,
            complete_cost=price, source_margin_upper_at_new_claim=old_margin,
            controls=controls,
            limits=['All five inherited framework assumptions remain.',
                    'The large uniform word and rounded multiplier are not materialized.',
                    'Author checks do not establish independent acceptance.',
                    'The selected frontier is unchanged.']))


def main():
    with tempfile.TemporaryDirectory(prefix='retained-operand-bytecode-') as cache:
        sys.pycache_prefix = cache
        result = run('--build-only' in sys.argv)
    if result is not None:
        if '--write' in sys.argv:
            (HERE / 'RESULT.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
        else:
            need(read(HERE / 'RESULT.json') == result, 'Exact retained result')
    print(STATUS + ('_BUILD' if result is None else ''), flush=True)


if __name__ == '__main__':
    main()
