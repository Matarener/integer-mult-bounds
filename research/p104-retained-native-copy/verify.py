"""Check the retained native copies and the complete conditional price.

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
    raise ValueError('Invalid candidate accepted')


def delta(before, after):
    out = Counter(after)
    out.subtract(before)
    return {r: n for r, n in out.items() if n}


def majorization(before, after):
    paid = delta(before['paid'], after['paid'])
    targets = delta(before['helpers'], after['helpers'])
    need(paid == {1: 12, 3: 4, 4: 4, 5: -16, 6: 1, 7: -5}, 'Exact paid delta')
    need(targets == {3: 4, 4: 12, 7: 1, 8: -17}, 'Exact target delta')
    gain = Counter(targets)
    gain.subtract(paid)
    gain = {r: n for r, n in gain.items() if n}
    positive = sorted(r for r, n in gain.items() for _ in range(max(n, 0)))
    negative = sorted(r for r, n in gain.items() for _ in range(max(-n, 0)))
    need(len(positive) == len(negative) == 30 and sum(positive) == sum(negative) == 154,
         'Equal majorization lengths and rank sums')
    margins = [sum(positive[:j])-sum(negative[:j]) for j in range(1, 31)]
    need(min(margins) >= 0 and max(margins) > 0 and margins[-1] == 0,
         'Strict concave majorization gain')
    need(sum(before['paid'].values()) == sum(after['paid'].values())
         and sum(before['helpers'].values()) == sum(after['helpers'].values()),
         'Unchanged paid and productive call counts')
    need(before['paid_rank_mass']-after['paid_rank_mass'] == 69,
         'Paid and productive rank reduction')
    return {'delta_paid': paid, 'delta_targets': targets, 'signed_gain': gain,
            'positive_ranks': positive, 'negative_ranks': negative,
            'ascending_prefix_margins': margins,
            'scope': 'Strict signed-moment improvement for every exponent 0<t<1.'}


def controls(source, word, L):
    first_new = source['public']+source['owned_fields']
    copy = next(i for i, e in enumerate(word['program']) if e[0] == 'COPY' and e[1] >= first_new)
    move = next(i for i, e in enumerate(word['program']) if e[0] == 'MOVE' and e[1] >= first_new)
    clear = next(i for i, e in enumerate(word['program']) if e[0] == 'CLEAR' and e[1] >= first_new)
    out = {}
    bad = deepcopy(word)
    del bad['program'][move]
    out['omit_paid_cache_query'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['program'][copy][-2] = '2'
    out['wrong_cache_value'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    del bad['program'][clear]
    out['omit_cache_clear'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    event = bad['program'].pop(clear)
    last_use = max(i for i, e in enumerate(bad['program'])
                   if e[0] in ('COPY', 'ADD') and e[2] == event[1])
    bad['program'].insert(last_use, event)
    out['clear_before_last_use'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    changed = next(r for r in range(word['public']) if word['final'][r] != source['final'][r])
    bad['final'][changed] = source['final'][changed]
    out['retain_old_helper_credit'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['owned_fields'] -= 1
    out['omit_owned_storage'] = reject(lambda: L.replay(bad))
    return out


def run():
    with ExitStack() as contexts:
        parent, _ = contexts.enter_context(sources())
        cursor = parent
        for depth in range(5):
            module = load(cursor/'sources.py', 'native_copy_source_'+str(depth))
            cursor, root = contexts.enter_context(module.sources())
        declared_copy(parent/'local.py', HERE/'local.py', HERE/'LOCAL-EDITS.json')
        declared_copy(parent/'pricing.py', HERE/'pricing.py', HERE/'PRICING-EDITS.json')
        L = load(HERE/'local.py', 'local')
        L.ROOT = root
        source = L.read(parent/'WORD.json.gz')
        plan = L.read(HERE/'PLAN.json')
        need(digest(source) == plan['source_canonical_sha256'], 'Exact source word')
        baseline = L.replay(source)
        word = deepcopy(source)
        word['frames'].extend(plan['appended_frames'])
        witnesses = []
        for request in plan['steps']:
            need(digest(word) == request['source_sha256'], 'Exact step input')
            word, witness = construct.construct(word, request)
            need(digest(word) == request['output_sha256'], 'Exact step output')
            witness['local'] = L.replay(word)
            witnesses.append(witness)
        local = L.replay(word)
        need((local['public_inputs'], local['owned_fields'], local['owned_lifetimes'],
              local['peak_owned_fields']) == (767, 22, 24, 12), 'Exact storage inventory')
        need(local['public_inputs']+local['owned_fields'] < 1000, 'Retained fixed slot allowance')
        need(len(witnesses) == 9 and sum(len(w['caches']) for w in witnesses) == 13
             and sum(w['removed_zero_queries'] for w in witnesses) == 13,
             'Thirteen paid copies and thirteen removed zero transports')
        proof = majorization(baseline, local)
        transpose = L.reverse_columns(word)
        negative = controls(source, word, L)
        print('PASS exact construction, all scalar columns, ownership and majorization', flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'native_copy_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'),
             'Unchanged full physical caller')
        physical = C.physical(caller, word)
        print('PASS exact native maps, phases and complete physical caller', flush=True)
        P = load(HERE/'pricing.py', 'native_copy_price')
        price = P.run(local, native, caller, physical)
        need(price['previous_pr5751'] == L.read(parent/'RESULT.json')['complete_cost']['kappa'],
             'Exact predecessor exponent')
        negative.update(C.controls(caller))
        bad = deepcopy(local)
        bad['paid'][4] -= 1
        negative['omit_paid_query_from_invoice'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][8] += 1
        negative['invent_helper_credit'] = reject(lambda: P.assemble(bad, native, caller, physical))
        result = {'status': 'PASS_P104_RETAINED_NATIVE_COPY_KAPPA_00312192127',
                  'source_commit': '8483f9a679d06c1e270141dbc686a7e76e7a7522',
                  'canonical_word_sha256': digest(word), 'instructions': len(word['program']),
                  'local': local, 'separate_columns': transpose, 'majorization': proof,
                  'native': native, 'physical_caller': physical, 'complete_cost': price,
                  'negative_controls': negative,
                  'limits': ['The five inherited framework assumptions remain.',
                             'The large uniform word and rounded multiplier are not materialized.',
                             'Author checks do not establish independent acceptance.',
                             'The selected frontier is unchanged.']}
        return P.encode(result), P.encode(witnesses), word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-native-copy-bytecode-') as cache:
        sys.pycache_prefix = cache
        result, witness, word = run()
    for name, value in (('RESULT.json', result), ('WITNESS.json', witness), ('WORD.json.gz', word)):
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
