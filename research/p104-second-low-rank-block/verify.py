"""Check the second rank-four block and its complete conditional cost.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Retained source authors are listed in NOTICE and the source archive.
"""
import argparse
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sources import sources, load, need, authenticate
from construct import construct

STATUS = 'PASS_P104_SECOND_RANK4_BLOCK_KAPPA_00311325989'


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def delta(after, before):
    value = Counter(after)
    value.subtract(before)
    return {str(r): c for r, c in sorted(value.items()) if c}


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid candidate accepted')


def run():
    with ExitStack() as contexts:
        parent = contexts.enter_context(sources())
        source = read(HERE/'inputs/pr5756-WORD.json.gz')
        word, witness = construct(source, read(HERE/'PLAN.json'))
        old_scalar = [e[:-1] for e in source['program'] if e[0] != 'MOVE']
        new_scalar = [e[:-1] for e in word['program'] if e[0] != 'MOVE']
        need(old_scalar == new_scalar, 'Every scalar coefficient, order and owned event is unchanged')
        for key in source:
            if key not in ('program', 'frames', 'initial', 'final', 'schema'):
                need(source[key] == word[key], 'Unchanged source field: '+key)
        need(word['frames'][:-1] == source['frames'], 'All source frames are unchanged')
        need([r for r, (a, b) in enumerate(zip(source['initial'], word['initial'])) if a != b] == [742],
             'Only helper 742 changes at entry')
        need([r for r, (a, b) in enumerate(zip(source['final'], word['final'])) if a != b] == [225],
             'Only helper 225 changes at exit')
        main = set(word['live']) | {r+112 for r in word['live']}
        need(225 not in main and 742 not in main, 'Only helper endpoints change')

        cursor = parent
        for depth in range(5):
            module = load(cursor/'sources.py', 'second_block_source_'+str(depth))
            cursor, framework = contexts.enter_context(module.sources())
        L = load(parent/'local.py', 'local')
        L.ROOT = framework
        before, local = L.replay(source), L.replay(word)
        paid_delta, target_delta = delta(local['paid'], before['paid']), delta(local['helpers'], before['helpers'])
        need(paid_delta == {'1': 1, '4': 1, '5': -1}, 'Complete changed paid profile')
        need(target_delta == {'1': -1, '4': 1, '5': 1, '8': -1}, 'Complete changed target profile')
        need(local['real_scalar_allowance'] == before['real_scalar_allowance'] == 224138,
             'Unchanged ordinary scalar charge')
        transpose = L.reverse_columns(word)
        print('PASS scalar order, all input columns, separate transpose and full local invoice', flush=True)
        native = L.native(word)
        C = load(framework/'research/p104-productive-controller/caller.py', 'second_block_caller')
        caller = C.construct()
        need(caller == read(framework/'research/p104-productive-controller/CONTROLLER.json'),
             'Exact retained caller')
        physical = C.physical(caller, word)
        print('PASS native maps, absolute phases, helper normalizers and physical caller', flush=True)

        price_text = (parent/'pricing.py').read_text(encoding='utf-8')
        for old, new in read(HERE/'PRICING-EDITS.json'):
            need(price_text.count(old) == 1, 'Unique declared pricing edit')
            price_text = price_text.replace(old, new)
        need(price_text == (HERE/'pricing.py').read_text(encoding='utf-8'), 'Only declared pricing edits')
        P = load(HERE/'pricing.py', 'second_block_price')
        price = P.run(local, native, caller, physical)
        E = L.load(framework/'research/higher-moment-strictification/verify.py', 'second_block_source_price')
        old_t = {int(r): c for r, c in price['targets'].items()}
        old_p = {int(r): c for r, c in price['paid'].items()}
        for r, c in target_delta.items():
            old_t[int(r)] -= 18*c
        for r, c in paid_delta.items():
            old_p[int(r)] -= 18*c
        t = 1-P.KAPPA
        old_margin = E.moment(old_t, t)[1]-E.moment(old_p, t)[0]
        need(old_margin < 0, 'The source invoice fails at the new claimed exponent')
        print('PASS both rational prices, complete completion, stock, compiler and outer costs', flush=True)

        controls = C.controls(caller)
        bad = deepcopy(word)
        bad['initial'][742] = 267
        controls['old_helper_entry'] = reject(lambda: L.replay(bad))
        bad = deepcopy(word)
        event = next(e for e in bad['program'] if e[0] == 'ADD' and e[-1] == witness['new_frame'])
        event[-1] = 267
        controls['old_block_chart'] = reject(lambda: L.replay(bad))
        bad = deepcopy(word)
        index = next(i for i, e in enumerate(bad['program']) if e[0] == 'MOVE' and e[3] == witness['new_frame'])
        bad['program'].pop(index)
        controls['missing_native_move'] = reject(lambda: L.replay(bad))
        bad = deepcopy(word)
        event = next(e for e in bad['program'] if e[0] == 'ADD' and e[-1] == witness['new_frame'])
        event[-2] = str(-Q(event[-2]))
        controls['wrong_scalar_coefficient'] = reject(lambda: L.replay(bad))
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        controls['unpaid_query'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][9] += 1
        controls['extra_target_credit'] = reject(lambda: P.assemble(bad, native, caller, physical))
        pin = read(HERE/'SOURCES.json')['direct_sources'][0]
        raw = (HERE/pin['local_path']).read_bytes()
        controls['damaged_source'] = reject(lambda: authenticate(bytes([raw[0] ^ 1])+raw[1:], pin))

        result = dict(status=STATUS, source_commit='a1b338e5d9271b541f2a198f4fc19cefc565feed',
                      local=local, source_local=before, paid_delta=paid_delta, target_delta=target_delta,
                      transpose=transpose, native=native, physical_caller=physical, complete_cost=price,
                      source_margin_upper_at_new_claim=old_margin, controls=controls,
                      limits=['The five inherited framework assumptions remain.',
                              'This small gain does not meet the requested large improvement.',
                              'The uniform word and rounded multiplier are not materialized.',
                              'These author checks are not independent human or formal acceptance.',
                              'The selected frontier is unchanged.'])
        return P.encode(result), witness, word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-second-block-bytecode-') as cache:
        sys.pycache_prefix = cache
        result, witness, word = run()
    for name, value in (('RESULT.json', result), ('WITNESS.json', witness), ('WORD.json.gz', word)):
        path = HERE/name
        if args.write:
            raw = (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()
            path.write_bytes(gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw)
        else:
            need(read(path) == value, 'Exact complete retained output: '+name)
    print(STATUS, flush=True)


if __name__ == '__main__':
    main()
