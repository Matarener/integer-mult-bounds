"""Replay the two-boundary helper split and complete conditional exponent invoice.

Prepared for flyingviper with substantial OpenAI Codex assistance. Apache-2.0.
The full local, native, caller and price engines retain predecessor attribution.
"""
import argparse
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
from sources import sources, load, need
import construct
import checks


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid invoice accepted')


def run():
    with ExitStack() as contexts:
        parent, _ = contexts.enter_context(sources())
        cursor = parent
        for depth in range(3):
            module = load(cursor/'sources.py', 'two_boundary_split_sources_'+str(depth))
            cursor, root = contexts.enter_context(module.sources())
        L = load(cursor/'local.py', 'local')
        L.ROOT = root
        source = L.read(parent/'WORD.json.gz')
        word, witness = construct.construct(source)
        independent = checks.audit(word)
        controls = checks.negative_controls(word, witness)
        local = L.replay(word)
        columns = L.reverse_columns(word)
        need(local['public_inputs'] == 744 and local['owned_fields'] == 9
             and local['owned_lifetimes'] == 11 and local['peak_owned_fields'] == 2,
             'Exact public/owned lifetime inventory')
        print('PASS all 753 scalar columns, literal charts and actual repair controls', flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'two_boundary_split_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'),
             'Retained complete physical caller')
        physical = C.physical(caller, word)
        print('PASS all 2917 native maps, phases and complete physical caller', flush=True)
        text = (parent/'pricing.py').read_text(encoding='utf-8')
        for before, after in L.read(HERE/'PRICING-EDITS.json'):
            need(text.count(before) == 1, 'Unique declared pricing edit')
            text = text.replace(before, after)
        need(text == (HERE/'pricing.py').read_text(encoding='utf-8'),
             'Only declared complete pricing edits')
        P = load(HERE/'pricing.py', 'two_boundary_split_price')
        price = P.run(local, native, caller, physical)
        controls.update(C.controls(caller))
        bad = deepcopy(local)
        bad['paid'][7] -= 1
        controls['unpaid_rank7_query'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][9] += 1
        controls['invented_extra_H9_target'] = reject(lambda: P.assemble(bad, native, caller, physical))
        result = {'status': 'PASS_P104_TWO_BOUNDARY_SPLIT_KAPPA_00311024570',
                  'source_commit': 'a5348f7143f95fe0046b92b96172e30763c7d731',
                  'local': local, 'separate_columns': columns, 'native': native,
                  'physical_caller': physical, 'complete_cost': price,
                  'independent_literal_audit': independent, 'negative_controls': controls,
                  'limits': ['The five inherited framework assumptions remain.',
                             'No selected-frontier admission or large improvement is claimed.',
                             'The huge uniform word and complete rounded multiplier are not materialized.',
                             'Independent agent checks are not human or formal acceptance.']}
        return P.encode(result), P.encode(witness), word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-two-boundary-bytecode-') as cache:
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
