"""Check the complete conditional P104 contact rewrite and its price.

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
import patterns


def rejected(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('An invalid certificate was accepted')


def difference(after, before):
    delta = Counter(after)
    delta.subtract(before)
    return {r:v for r,v in delta.items() if v}


def run():
    witness = json.loads((HERE/'WITNESS.json').read_bytes())
    with sources() as (parent, root):
        L = load(parent/'local.py', 'local')
        source = L.read(parent/'WORD.json.gz')
        old = L.replay(source)
        cleanup = load(HERE/'inputs/pr5644-construct.py', 'released_helper_cleanup')
        clean, clean_changes, clean_local = cleanup.construct(
            source, L.read(HERE/'inputs/pr5644-witness.json'), L)
        need(clean == L.read(HERE/'inputs/pr5644-word.json.gz'), 'Exact released PR5644 word')
        construct.check_a2_source(source, L.read(HERE/'inputs/pr5643-word.json.gz'), L)
        composed = construct.rebuild(clean, construct.replace_a2(construct.skeleton(clean), L), L)
        published = L.read(HERE/'inputs/pr5650-word.json.gz')
        normalized = construct.rebuild(published, construct.skeleton(published), L)
        normalized['schema'] = composed['schema']
        need(normalized == composed, 'Exact released PR5650 composition after public MOVE ordering')
        composed_local = L.replay(composed)
        need(L.replay(published) == composed_local, 'Same complete published composition receipt')
        need(difference(composed_local['paid'], clean_local['paid']) == {2:1,3:-1,5:-1,6:1},
             'The released A2 change composes with all three helper relations')
        word, local = construct.rewrite(composed, witness, L)
        pattern_before, pattern_after = patterns.find(composed), patterns.find(word)
        need(pattern_before == [dict(first=12754,second=12755,previous=[12513,12753],roles=[165,586,733])]
             and pattern_after == [], 'One tested scalar pattern before the change and none after')
        columns = L.reverse_columns(word)
        need(cleanup.owned_events(word) == cleanup.owned_events(source), 'All owned instructions stay fixed')
        need((local['public_inputs'],local['owned_fields'],local['owned_lifetimes'],local['peak_owned_fields']) ==
             (743,9,11,2), 'Complete public and owned inventories')
        need(difference(local['paid'],old['paid']) == {1:-5,2:2,3:-1,5:-4,6:4}, 'Combined exact paid delta')
        need(local['helpers'] == old['helpers'] == composed_local['helpers'], 'No target debit or added credit')
        print('PASS released composition, four-gate identity and all 565504 endpoint coefficients', flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'contact_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'), 'Same complete controller')
        physical = C.physical(caller, word)
        print('PASS all native phases, target maps and physical caller contacts', flush=True)
        price = (parent/'pricing.py').read_text()
        for before, after in json.loads((HERE/'PRICING-EDITS.json').read_bytes()):
            need(price.count(before) == 1, 'One declared price change')
            price = price.replace(before, after)
        need((HERE/'pricing.py').read_text() == price, 'Only declared price and attribution changes')
        P = load(HERE/'pricing.py', 'contact_price')
        costs = P.run(local, native, caller, physical)
        controls = C.controls(caller)
        bad = deepcopy(witness)
        bad['replacement'][0][3] = '-1/2'
        controls['wrong_compensation_sign'] = rejected(lambda: construct.rewrite(composed,bad,L))
        bad = deepcopy(witness)
        bad['indices'][0] += 1
        controls['wrong_source_version'] = rejected(lambda: construct.rewrite(composed,bad,L))
        bad = deepcopy(word)
        bad['program'].remove(next(e for e in bad['program'] if e == witness['replacement'][0]))
        controls['missing_early_read'] = rejected(lambda: L.replay(bad))
        bad = deepcopy(word)
        site = next(i for i,e in enumerate(bad['program']) if e == witness['replacement'][0])
        bad['program'][site][-1] = 597
        controls['wrong_early_frame'] = rejected(lambda: L.replay(bad))
        bad = deepcopy(word)
        bad['program'].pop(max(i for i,e in enumerate(bad['program']) if e[0] == 'CLEAR'))
        controls['missing_owned_erasure'] = rejected(lambda: L.replay(bad))
        bad = deepcopy(local)
        bad['helpers'][1] += 1
        controls['extra_target_credit'] = rejected(lambda: P.assemble(bad,native,caller,physical))
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        controls['unpaid_query'] = rejected(lambda: P.assemble(bad,native,caller,physical))
        result = dict(status='PASS_P104_CONTACT_REWRITE_KAPPA_00310676333',
                      authenticated_package_inputs=6, authenticated_source_files=36,
                      source_commit='ed4dc88a09a7d201971f6603b8c2074e95dd9c32',
                      released_helper_changes=clean_changes,
                      released_a2_paid_delta={2:1,3:-1,5:-1,6:1},
                      scalar_pattern_census=dict(before=pattern_before,after=pattern_after),
                      new_four_gate_paid_delta={1:-2,2:1},
                      local_paid_delta={1:-5,2:2,3:-1,5:-4,6:4},local_helper_delta={},
                      source_local=old,pr5644_local=clean_local,composed_local=composed_local,
                      local=local,separate_columns=columns,native=native,physical_caller=physical,
                      complete_cost=costs,negative_controls=controls,
                      limits=['The five selected framework assumptions and helper endpoint contract remain.',
                              'The enormous uniform word and complete rounded multiplier are not materialized.',
                              'These author checks are not independent scientific acceptance or a proof-kernel theorem.',
                              'This is a small improvement. No global optimum or large breakthrough is established.'])
        return P.encode(result), word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-contact-bytecode-') as cache:
        sys.pycache_prefix = cache
        result, word = run()
    for name, value in (('RESULT.json',result),('WORD.json.gz',word)):
        path = HERE/name
        if args.write:
            raw = (json.dumps(value,sort_keys=True,indent=None if name.endswith('.gz') else 2)+'\n').encode()
            path.write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
        else:
            raw = path.read_bytes()
            need(json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw) == value,
                 'Exact saved artifact: '+name)
    print(result['status'])
    print(json.dumps({k:result['complete_cost'][k] for k in
                     ('kappa_decimal','gain','raw_root_interval','productive_fields','paid_calls')},sort_keys=True))


if __name__ == '__main__':
    main()
