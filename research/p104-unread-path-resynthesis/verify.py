"""Check the exact path rewrite and its complete conditional price.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
All predecessor notices are retained in NOTICE and the source archive.
"""
import argparse
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
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

STATUS = 'PASS_P104_UNREAD_PATH_KAPPA_00312476680'


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def declared_copy(origin, target, edits):
    text = origin.read_text(encoding='utf-8')
    for old, new in read(edits):
        need(text.count(old) == 1, 'Unique declared source edit')
        text = text.replace(old, new)
    need(text == target.read_text(encoding='utf-8'), 'Only declared source edits')


def delta(after, before):
    value = Counter(after)
    value.subtract(before)
    return {str(r): n for r, n in sorted(value.items()) if n}


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid candidate accepted')


def run():
    with ExitStack() as contexts:
        parent = contexts.enter_context(sources())
        cursor = parent
        for depth in range(7):
            module = load(cursor/'sources.py', 'unread_path_source_'+str(depth))
            cursor, root = contexts.enter_context(module.sources())
        declared_copy(parent/'local.py', HERE/'local.py', HERE/'LOCAL-EDITS.json')
        declared_copy(parent/'pricing.py', HERE/'pricing.py', HERE/'PRICING-EDITS.json')
        L = load(HERE/'local.py', 'local')
        L.ROOT = root
        source = read(HERE/'inputs/pr5811-WORD.json.gz')
        plan = read(HERE/'PLAN.json')
        word, witness = construct(source, plan)
        baseline, local = L.replay(source), L.replay(word)
        need(delta(local['paid'], baseline['paid']) == {'1': -1, '4': -1, '5': 1}, 'Exact paid gain')
        need(local['helpers'] == baseline['helpers'], 'Every productive target is retained')
        need((local['public_inputs'], local['owned_fields'], local['owned_lifetimes'],
              local['peak_owned_fields']) == (770, 29, 31, 13), 'Exact storage inventory')
        need(local['public_inputs']+local['owned_fields'] < 1000, 'All arrays fit the retained slot bound')
        need(local['real_scalar_allowance']-baseline['real_scalar_allowance'] == 8,
             'The additional ordinary ADD is charged')
        need(local['paid_rank_mass'] == baseline['paid_rank_mass'] == 5934, 'Unchanged local rank mass')
        columns = L.reverse_columns(word)
        print('PASS all input columns, separate transpose, storage and exact paid delta', flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'unread_path_caller')
        caller = C.construct()
        need(caller == read(root/'research/p104-productive-controller/CONTROLLER.json'), 'Exact physical caller')
        physical = C.physical(caller, word)
        print('PASS native maps, absolute phases, adapters and complete physical caller', flush=True)
        P = load(HERE/'pricing.py', 'unread_path_price')
        price = P.run(local, native, caller, physical)
        E = L.load(root/'research/higher-moment-strictification/verify.py', 'unread_path_source_price')
        old_p = {int(r): n for r, n in price['paid'].items()}
        old_p[1] += 18
        old_p[4] += 18
        old_p[5] -= 18
        old_t = {int(r): n for r, n in price['targets'].items()}
        margin = E.moment(old_t, 1-P.KAPPA)[1]-E.moment(old_p, 1-P.KAPPA)[0]
        need(margin < 0, 'The old full profile fails at the new claim')
        print('PASS both rational engines, completion, compiler and all outer costs', flush=True)

        controls = C.controls(caller)
        at = plan['start']
        bad = deepcopy(word)
        bad['program'].pop(at)
        controls['missing_early_observation'] = reject(lambda: L.replay(bad))
        bad = deepcopy(word)
        bad['program'][at+2][-2] = '-1'
        controls['wrong_late_sign'] = reject(lambda: L.replay(bad))
        bad = deepcopy(word)
        bad['program'].pop(at+1)
        controls['missing_direct_query'] = reject(lambda: L.replay(bad))
        bad = deepcopy(word)
        bad['program'].insert(at+7, bad['program'].pop(at))
        controls['late_use_of_old_value'] = reject(lambda: L.replay(bad))
        bad = deepcopy(source)
        bad['program'][at+3][-2] = '2'
        controls['changed_source_interval'] = reject(lambda: construct(bad, plan))
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        controls['unpaid_query'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][9] += 1
        controls['extra_target_credit'] = reject(lambda: P.assemble(bad, native, caller, physical))
        for pin in read(HERE/'SOURCES.json')['direct_sources']:
            raw = (HERE/pin['local_path']).read_bytes()
            controls['damaged_source_'+Path(pin['path']).name] = reject(
                lambda raw=raw, pin=pin: authenticate(bytes([raw[0]^1])+raw[1:], pin))

        result = dict(status=STATUS, source_commit='33d7760d0a6fea6394aefd014eea68f0af02a92e',
                      source_local=baseline, local=local, paid_delta={'1': -1, '4': -1, '5': 1},
                      target_delta={}, separate_columns=columns, native=native,
                      physical_caller=physical, complete_cost=price,
                      source_margin_upper_at_new_claim=margin, controls=controls,
                      limits=['All five inherited framework assumptions remain.',
                              'This is a small gain and does not meet the donor large-improvement target.',
                              'The large uniform word and rounded multiplier are not materialized.',
                              'Author checks do not establish independent acceptance.',
                              'The selected frontier is unchanged.'])
        return P.encode(result), witness, word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-unread-path-bytecode-') as cache:
        sys.pycache_prefix = cache
        result, witness, word = run()
    for name, value in (('RESULT.json', result), ('WITNESS.json', witness), ('WORD.json.gz', word)):
        path = HERE/name
        if args.write:
            raw = (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()
            path.write_bytes(gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw)
        else:
            need(read(path) == value, 'Exact retained output: '+name)
    print(STATUS, flush=True)


if __name__ == '__main__':
    main()
