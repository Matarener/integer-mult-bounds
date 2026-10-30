"""Check temporal helper splits and the full conditional kappa price.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
NOTICE retains the source, native, caller and compiler credit.
"""
import argparse
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from sources import sources, load, need
import construct


def digest(word):
    return sha256(json.dumps(word, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def declared_copy(source, target, edits):
    text = source.read_text(encoding='utf-8')
    for before, after in json.loads(edits.read_bytes()):
        need(text.count(before) == 1, 'Unique declared source edit')
        text = text.replace(before, after)
    need(text == target.read_text(encoding='utf-8'), 'Only declared source edits: '+target.name)


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid construction accepted')


def difference(before, after):
    delta = Counter(after)
    delta.subtract(before)
    return {r: n for r, n in delta.items() if n}


def controls(word, plan, L):
    step = plan['steps'][-1]
    buffer, frame = step['buffer'], step['frame']
    move = step['query_events'][0]
    events = {
        'omit_history_collection': ['ADD', buffer, 438, '-1', frame],
        'omit_paid_access_query': ['MOVE', move[1], move[2], frame, move[4]],
        'omit_buffer_clear': ['CLEAR', buffer, frame],
    }
    reasons = {}
    for name, event in events.items():
        need(word['program'].count(event) == 1, 'Unique actual control event: '+name)
        bad = deepcopy(word)
        bad['program'].remove(event)
        reasons[name] = reject(lambda: L.replay(bad))
    clear_index = word['program'].index(['CLEAR', buffer, frame])
    need(word['program'][clear_index-1] == ['ADD', word['public']-1, buffer, '1', frame],
         'Actual final injection immediately before CLEAR')
    bad = deepcopy(word)
    del bad['program'][clear_index-1]
    reasons['omit_continuation_injection'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['initial'][-1] = 3
    reasons['wrong_fresh_input_frame'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['final'][step['pivot']] = 127
    reasons['retain_old_rank_nine_target'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['owned_fields'] -= 1
    reasons['omit_owned_buffer'] = reject(lambda: L.replay(bad))
    return reasons


def run():
    with ExitStack() as contexts:
        parent, _ = contexts.enter_context(sources())
        cursor = parent
        for depth in range(6):
            module = load(cursor/'sources.py', 'async_helper_source_'+str(depth))
            cursor, root = contexts.enter_context(module.sources())
        declared_copy(parent/'local.py', HERE/'local.py', HERE/'LOCAL-EDITS.json')
        declared_copy(parent/'pricing.py', HERE/'pricing.py', HERE/'PRICING-EDITS.json')
        L = load(HERE/'local.py', 'local')
        L.ROOT = root
        source = L.read(parent/'WORD.json.gz')
        plan = L.read(HERE/'PLAN.json')
        need(digest(source) == plan['source_canonical_sha256'], 'Exact PR5774 source word')
        baseline = L.replay(source)
        word, witnesses = deepcopy(source), []
        for step in plan['steps']:
            need(digest(word) == step['source_sha256'], 'Exact step input')
            word, witness = construct.construct(word, step)
            need(digest(word) == step['output_sha256'], 'Exact step output')
            witness['local'] = L.replay(word)
            witnesses.append(witness)
        need(len(witnesses) == 3 and sum(len(s['queries']) for s in plan['steps']) == 4,
             'Three helper splits and four paid access points')
        local = L.replay(word)
        need((local['public_inputs'], local['owned_fields'], local['owned_lifetimes'],
              local['peak_owned_fields']) == (770, 25, 27, 13), 'Exact storage inventory')
        need(local['public_inputs']+local['owned_fields'] < 1000, 'Retained fixed slot allowance')
        need(local['paid'] == {1: 2235, 2: 452, 3: 498, 4: 98, 5: 159, 6: 7, 7: 8},
             'Exact local paid invoice')
        need(local['helpers'] == {1: 26, 2: 5, 3: 4, 4: 105, 5: 8, 7: 7, 8: 22, 9: 385},
             'Exact independent helper invoice')
        paid_delta = difference(baseline['paid'], local['paid'])
        target_delta = difference(baseline['helpers'], local['helpers'])
        need(paid_delta == {1: 4, 2: -2, 3: 2, 4: 2, 7: -2}, 'Exact paid change')
        need(target_delta == {1: 1, 4: 2, 5: 2, 8: 1, 9: -3}, 'Exact target change')
        transpose = L.reverse_columns(word)
        negative = controls(word, plan, L)
        print('PASS temporal identities, all scalar columns, frames, ownership and controls', flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'async_helper_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'),
             'Unchanged complete physical caller')
        physical = C.physical(caller, word)
        print('PASS exact native maps, phases and full physical caller', flush=True)
        P = load(HERE/'pricing.py', 'async_helper_price')
        price = P.run(local, native, caller, physical)
        need(price['previous_pr5774'] == L.read(parent/'RESULT.json')['complete_cost']['kappa'],
             'Exact predecessor exponent')
        negative.update(C.controls(caller))
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        negative['omit_paid_query_from_invoice'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][9] += 1
        negative['invent_helper_credit'] = reject(lambda: P.assemble(bad, native, caller, physical))
        result = {
            'status': 'PASS_P104_ASYNC_HELPER_HUBS_KAPPA_00312265044',
            'source_commit': '7d6ec0cdef31d0c37b7d2563e709979caa0d5eae',
            'canonical_word_sha256': digest(word), 'instructions': len(word['program']),
            'local': local, 'separate_columns': transpose, 'native': native,
            'physical_caller': physical, 'complete_cost': price,
            'delta_paid': paid_delta, 'delta_targets': target_delta,
            'negative_controls': negative,
            'limits': ['The five inherited framework assumptions remain.',
                       'This gain is below the requested one percent.',
                       'The large uniform word and rounded multiplier are not materialized.',
                       'Author checks are not independent human or formal acceptance.',
                       'The selected frontier is unchanged.'],
        }
        return P.encode(result), P.encode(witnesses), word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-async-helper-bytecode-') as cache:
        sys.pycache_prefix = cache
        result, witnesses, word = run()
    for name, value in (('RESULT.json', result), ('WITNESS.json', witnesses), ('WORD.json.gz', word)):
        path = HERE/name
        if args.write:
            raw = (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()
            path.write_bytes(gzip.compress(raw, mtime=0) if name.endswith('.gz') else raw)
        else:
            raw = path.read_bytes()
            need(json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw) == value,
                 'Complete retained output: '+name)
    print(result['status'])


if __name__ == '__main__':
    main()
