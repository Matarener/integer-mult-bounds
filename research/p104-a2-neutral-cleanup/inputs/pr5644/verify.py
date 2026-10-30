"""Verify the three helper relations and the complete conditional kappa.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
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
    raise ValueError('An invalid certificate was accepted')


def run():
    witnesses = json.loads((HERE/'WITNESS.json').read_bytes())
    with sources() as (parent, root):
        L = load(parent/'local.py', 'local')
        source = L.read(parent/'WORD.json.gz')
        old = L.replay(source)
        word, changes, local = construct.construct(source, witnesses, L)
        columns = L.reverse_columns(word)
        need((local['public_inputs'],local['owned_fields'],local['owned_lifetimes'],local['peak_owned_fields']) ==
             (743,9,11,2), 'All independent inputs and owned lifetimes')
        print('PASS three exact relations, unchanged targets and all 565504 matrix entries', flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'neutral_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'), 'Exact retained controller')
        physical = C.physical(caller, word)
        print('PASS all native phases and the full physical caller', flush=True)
        original_price = (parent/'pricing.py').read_text()
        edits = [
            ("Q('.00310440546'), Q('.003104405465')", "Q('.00310626335'), Q('.003106263355')"),
            ("PREVIOUS = Q('.00308595')", "PREVIOUS = Q('.00310440546')"),
            ('== 66546', '== 66492'),
            ("'kappa_decimal':'.00310440546'", "'kappa_decimal':'.00310626335'"),
            ('previous_open_pr5601', 'previous_open_pr5627')]
        for before, after in edits:
            need(original_price.count(before) == 1, 'One declared price substitution')
            original_price = original_price.replace(before, after)
        need((HERE/'pricing.py').read_text() == original_price, 'Only declared price changes')
        P = load(HERE/'pricing.py', 'neutral_price')
        costs = P.run(local, native, caller, physical)
        controls = C.controls(caller)
        bad = deepcopy(witnesses[0])
        key = next(iter(bad['cancel']))
        bad['cancel'][key] = str(L.Q(bad['cancel'][key])+1)
        controls['false_cancellation'] = rejected(lambda: construct.relation(source, bad, L))
        bad = deepcopy(witnesses[0])
        bad['cut'] += 1
        controls['wrong_cut'] = rejected(lambda: construct.relation(source, bad, L))
        bad = deepcopy(word)
        bad['program'].pop(0)
        controls['missing_input_basis'] = rejected(lambda: L.replay(bad))
        bad = deepcopy(word)
        bad['program'].pop(max(i for i,e in enumerate(bad['program']) if e[0] == 'CLEAR'))
        controls['missing_owned_erasure'] = rejected(lambda: L.replay(bad))
        bad = deepcopy(local)
        bad['helpers'][1] += 1
        controls['extra_target_credit'] = rejected(lambda: P.assemble(bad,native,caller,physical))
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        controls['unpaid_query'] = rejected(lambda: P.assemble(bad,native,caller,physical))
        result = dict(status='PASS_P104_NEUTRAL_HELPER_KAPPA_00310626335',
                      source_commit='ed4dc88a09a7d201971f6603b8c2074e95dd9c32',
                      authenticated_source_files=36, changes=changes,
                      local_paid_delta={1:-3,5:-3,6:3}, local_helper_delta={},
                      source_local=old, local=local, separate_columns=columns,
                      native=native, physical_caller=physical, complete_cost=costs,
                      negative_controls=controls,
                      limits=['The five selected framework assumptions and helper-endpoint contract remain.',
                              'The enormous uniform word and complete rounded multiplier are not materialized.',
                              'These author checks are not independent scientific review or a proof-kernel theorem.',
                              'The improvement is small. No large gain or global optimum is established.'])
        return P.encode(result), word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-neutral-bytecode-') as cache:
        sys.pycache_prefix = cache
        result, word = run()
    for name, value in (('RESULT.json', result), ('WORD.json.gz', word)):
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
