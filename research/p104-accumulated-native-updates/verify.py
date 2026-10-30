"""Check accumulated updates and the complete conditional price.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
NOTICE retains all predecessor credit.
"""
import argparse
from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
from fractions import Fraction as Q
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


def delta(before, after):
    change = Counter(after)
    change.subtract(before)
    return {rank: count for rank, count in change.items() if count}


def concavity(before, after):
    paid = delta(before['paid'], after['paid'])
    targets = delta(before['helpers'], after['helpers'])
    need(paid == {1: -6, 2: 4, 6: 2, 7: -2}, 'Exact local paid change')
    need(targets == {1: -2, 2: 2, 7: 2, 8: -2}, 'Exact helper change')
    signed = Counter(targets)
    signed.subtract(paid)
    signed = {r: c for r, c in signed.items() if c}
    need(signed == {1: 4, 2: -2, 6: -2, 7: 4, 8: -2}, 'Two strict concavity gaps')
    positive = [1, 1, 1, 1, 7, 7, 7, 7]
    negative = [0, 0, 2, 2, 6, 6, 8, 8]
    margins = [sum(positive[:j])-sum(negative[:j]) for j in range(1, 9)]
    need(sum(positive) == sum(negative) == 32 and min(margins) >= 0
         and max(margins) > 0, 'Independent padded majorization check')
    need(after['paid_rank_mass'] == before['paid_rank_mass'], 'Unchanged paid rank mass')
    return {'delta_paid': paid, 'delta_targets': targets, 'signed_gain': signed,
            'positive_ranks': positive, 'negative_ranks': negative,
            'ascending_prefix_margins': margins,
            'identity': '2*((2*H1-H2)+(2*H7-H6-H8))',
            'scope': 'Strict gain for every 0<t<1, with Hr=r^t and H0=0.'}


def protected(source, word):
    roles = {41, 42, 65, 106, 240, 400, 401, 403, 405, 410, 741,
             57, 81, 92, 224, 225, 227, 229, 234, 742}

    def events(w):
        return [e for e in w['program'] if e[1] in roles
                or (e[0] in ('ADD', 'COPY') and e[2] in roles)]

    need(events(source) == events(word), 'Protected R22 and 102-contact subsequences')
    need(all(source[side][r] == word[side][r] for side in ('initial', 'final') for r in roles),
         'Protected public boundaries')
    copies = [e[:-1] for e in word['program'] if e[0] == 'COPY']
    need(copies == [e[:-1] for e in source['program'] if e[0] == 'COPY'],
         'All source COPY roles and coefficients retained')
    payloads = copy_values(word)
    need(payloads == copy_values(source), 'Every source COPY keeps its exact decoded value')
    return {'roles': sorted(roles), 'events': len(events(word)), 'copy_events': len(copies),
            'event_sha256': digest(events(word)), 'copy_value_sha256': digest(payloads),
            'scope': 'Protected events and boundaries stay fixed. COPY frames can change; all COPY roles, coefficients and exact decoded values stay fixed.'}


def copy_values(word):
    rows = [{r: Q(1)} for r in range(word['public']+word['owned_fields'])]
    values = []
    for event in word['program']:
        op, role = event[:2]
        if op == 'MOVE':
            continue
        if op in ('INIT', 'CLEAR'):
            rows[role] = {}
            continue
        q = Q(event[-2])
        if op == 'SCALE':
            rows[role] = {k: q*v for k, v in rows[role].items()}
            continue
        source = rows[event[2]]
        if op == 'COPY':
            rows[role] = {k: q*v for k, v in source.items()}
            values.append([event[:-1], [[k, str(v)] for k, v in sorted(rows[role].items())]])
        else:
            for k, v in tuple(source.items()):
                value = rows[role].get(k, 0)+q*v
                if value:
                    rows[role][k] = value
                else:
                    rows[role].pop(k, None)
    return values


def controls(source, word, plan, L):
    slot = source['public']+source['owned_fields']
    move = next(i for i, e in enumerate(word['program']) if e[0] == 'MOVE' and e[1] == slot)
    component = next(i for i, e in enumerate(word['program']) if e[0] == 'ADD' and e[1] == slot)
    delivery = next(i for i, e in enumerate(word['program']) if e[0] == 'ADD' and e[2] == slot)
    clear = next(i for i, e in enumerate(word['program']) if e[0] == 'CLEAR' and e[1] == slot)
    out = {}
    for name, index in [('omit_paid_sum_query', move), ('omit_sum_component', component),
                        ('omit_sum_delivery', delivery), ('omit_buffer_clear', clear)]:
        bad = deepcopy(word)
        del bad['program'][index]
        out[name] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['program'][delivery][-2] = '-1'
    out['wrong_delivery_sign'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    event = bad['program'].pop(clear)
    bad['program'].insert(delivery, event)
    out['clear_before_delivery'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    bad['owned_fields'] -= 1
    out['omit_owned_storage'] = reject(lambda: L.replay(bad))
    bad = deepcopy(word)
    role = next(r for r in range(word['public']) if word['final'][r] != source['final'][r])
    bad['final'][role] = source['final'][role]
    out['retain_old_target_credit'] = reject(lambda: L.replay(bad))
    bad = deepcopy(source)
    group = plan['steps'][0]['accumulation']
    at = group['uses'][-1]-1
    bad['program'][at] = ['ADD', 0, group['role'], '1', group['before']]
    out['read_before_delivery'] = reject(lambda: construct.construct(bad, plan['steps'][0]))
    return out


def run():
    with ExitStack() as contexts:
        parent, _ = contexts.enter_context(sources())
        cursor = parent
        for depth in range(7):
            module = load(cursor/'sources.py', 'accumulated_source_'+str(depth))
            cursor, root = contexts.enter_context(module.sources())
        declared_copy(parent/'local.py', HERE/'local.py', HERE/'LOCAL-EDITS.json')
        declared_copy(parent/'pricing.py', HERE/'pricing.py', HERE/'PRICING-EDITS.json')
        L = load(HERE/'local.py', 'local')
        L.ROOT = root
        source = L.read(parent/'WORD.json.gz')
        plan = L.read(HERE/'PLAN.json')
        need(digest(source) == plan['source_canonical_sha256'], 'Exact PR5786 word')
        baseline = L.replay(source)
        word, witnesses = deepcopy(source), []
        for step in plan['steps']:
            need(digest(word) == step['source_sha256'], 'Exact step input')
            word, witness = construct.construct(word, step)
            need(digest(word) == step['output_sha256'], 'Exact step output')
            witness['local'] = L.replay(word)
            witnesses.append(witness)
        local = L.replay(word)
        need(len(witnesses) == 3 and sum(w['removed_queries'] for w in witnesses) == 5,
             'Three paid sums replace five source queries')
        need((local['public_inputs'], local['owned_fields'], local['owned_lifetimes'],
              local['peak_owned_fields']) == (770, 28, 30, 13), 'Exact storage inventory')
        need(local['public_inputs']+local['owned_fields'] < 1000, 'Retained slot allowance')
        protected_events = protected(source, word)
        gain = concavity(baseline, local)
        transpose = L.reverse_columns(word)
        negative = controls(source, word, plan, L)
        print('PASS construction, all scalar columns, read barriers, ownership and concavity', flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'accumulated_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'),
             'Unchanged complete physical caller')
        physical = C.physical(caller, word)
        print('PASS exact native maps, phases and complete physical caller', flush=True)
        P = load(HERE/'pricing.py', 'accumulated_price')
        price = P.run(local, native, caller, physical)
        need(price['previous_pr5786'] == L.read(parent/'RESULT.json')['complete_cost']['kappa'],
             'Exact predecessor exponent')
        negative.update(C.controls(caller))
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        negative['omit_paid_query_from_invoice'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][9] += 1
        negative['invent_helper_credit'] = reject(lambda: P.assemble(bad, native, caller, physical))
        result = {'status': 'PASS_P104_ACCUMULATED_NATIVE_UPDATES',
                  'source_commit': '6b936acd68a7e0f9062037900f0fe9bc4b6fdd25',
                  'canonical_word_sha256': digest(word), 'instructions': len(word['program']),
                  'local': local, 'separate_columns': transpose, 'concavity': gain,
                  'protected_contacts': protected_events, 'native': native,
                  'physical_caller': physical, 'complete_cost': price,
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
    with tempfile.TemporaryDirectory(prefix='p104-accumulated-bytecode-') as cache:
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
