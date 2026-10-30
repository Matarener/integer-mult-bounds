"""Verify the distributed update and its complete conditional kappa.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
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


def rejected(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('An invalid construction was accepted')


def difference(after, before):
    delta = Counter(after)
    delta.subtract(before)
    return {rank: count for rank, count in delta.items() if count}


def run():
    witness = json.loads((HERE/'WITNESS.json').read_bytes())
    with sources() as (parent, _):
        with load(parent/'sources.py', 'temporal_parent_sources').sources() as (prior, _):
            with load(prior/'sources.py', 'temporal_prior_sources').sources() as (stack, root):
                L = load(stack/'local.py', 'local')
                L.ROOT = root
                source = L.read(HERE/'inputs/pr5684/WORD.json.gz')
                source_constructor = load(HERE/'inputs/pr5684/construct.py', 'temporal_source_constructor')
                need(source_constructor.construct(L.read(parent/'WORD.json.gz')) == source,
                     'Exact PR5684 construction from pinned PR5678')
                old = L.replay(source)
                word, identity = construct.construct(source, witness)
                local = L.replay(word)
                need(difference(local['paid'], old['paid']) == {1: -1, 2: -1, 3: 1},
                     'One H1 and one H2 are replaced by one H3')
                need(local['helpers'] == old['helpers'], 'Every productive target is retained')
                need((local['public_inputs'], local['owned_fields'], local['owned_lifetimes'],
                      local['peak_owned_fields']) == (743, 9, 11, 2), 'Public and owned inventory')
                need(len(word['program']) == 25453, 'Complete emitted instruction count')
                for key in source:
                    if key not in ('program', 'schema'):
                        need(word[key] == source[key], 'Unchanged boundary and geometry: '+key)
                columns = L.reverse_columns(word)
                print('PASS temporal source identity and all 565504 endpoint entries', flush=True)
                native = L.native(word)
                C = load(root/'research/p104-productive-controller/caller.py', 'temporal_caller')
                caller = C.construct()
                need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'),
                     'Exact retained caller')
                physical = C.physical(caller, word)
                print('PASS all native maps, phases and the complete physical caller', flush=True)
                price_source = (HERE/'inputs/pr5684/pricing.py').read_text()
                for before, after in L.read(HERE/'PRICING-EDITS.json'):
                    need(price_source.count(before) == 1, 'One declared price edit')
                    price_source = price_source.replace(before, after)
                need(price_source == (HERE/'pricing.py').read_text(), 'Only declared price edits')
                P = load(HERE/'pricing.py', 'temporal_price')
                price = P.run(local, native, caller, physical)
                controls = C.controls(caller)
                bad = deepcopy(witness)
                bad['inserts'][0]['coefficient'] = '-1/4'
                controls['wrong_history_sign'] = rejected(lambda: construct.identity(source, bad))
                bad = deepcopy(witness)
                bad['inserts'].pop()
                controls['missing_late_update'] = rejected(lambda: construct.identity(source, bad))
                bad = deepcopy(witness)
                bad['stop'] += 1
                controls['interval_crosses_target_read'] = rejected(lambda: construct.identity(source, bad))
                bad = deepcopy(witness)
                bad['inserts'][0]['frame'] = 598
                controls['wrong_common_frame'] = rejected(lambda: construct.identity(source, bad))
                bad = deepcopy(word)
                bad['program'].remove(['MOVE', 715, 3, 396, False])
                controls['missing_native_transport'] = rejected(lambda: L.replay(bad))
                bad = deepcopy(word)
                bad['program'].remove(['CLEAR', 747, 598])
                controls['missing_owned_erasure'] = rejected(lambda: L.replay(bad))
                bad = deepcopy(local)
                bad['paid'][1] -= 1
                controls['unpaid_query'] = rejected(lambda: P.assemble(bad, native, caller, physical))
                bad = deepcopy(local)
                bad['helpers'][9] += 1
                controls['extra_target'] = rejected(lambda: P.assemble(bad, native, caller, physical))
                result = {'status': 'PASS_P104_TEMPORAL_UPDATES_KAPPA_00310915222',
                          'source_commit': 'd0f6fa2555410a1e23fe4191424c2097ab3d5d97',
                          'source_local': old, 'temporal_identity': identity, 'local': local,
                          'separate_columns': columns, 'local_paid_delta': {1: -1, 2: -1, 3: 1},
                          'local_helper_delta': {}, 'native': native, 'physical_caller': physical,
                          'complete_cost': price, 'negative_controls': controls,
                          'limits': ['The five inherited framework assumptions remain.',
                                     'The complete rounded multiplier and huge uniform word are not materialized.',
                                     'Author checks do not establish independent scientific acceptance.',
                                     'The gain is small. No large gain or global optimum is claimed.']}
                return P.encode(result), word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-temporal-bytecode-') as cache:
        sys.pycache_prefix = cache
        result, word = run()
    for name, value in (('RESULT.json', result), ('WORD.json.gz', word)):
        path = HERE/name
        payload = (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()
        if args.write:
            path.write_bytes(gzip.compress(payload, mtime=0) if name.endswith('.gz') else payload)
        else:
            raw = path.read_bytes()
            need(json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw) == value,
                 'Exact retained output: '+name)
    print(result['status'])


if __name__ == '__main__':
    main()
