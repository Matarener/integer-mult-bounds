"""Verify paid intermediate meetings and the complete conditional exponent.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
All source, native, caller and compiler credit is retained in NOTICE.
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
    raise ValueError('Invalid full invoice accepted')


def run():
    with ExitStack() as contexts:
        parent, _ = contexts.enter_context(sources())
        cursor = parent
        for depth in range(4):
            module = load(cursor/'sources.py', 'paid_meeting_source_'+str(depth))
            cursor, root = contexts.enter_context(module.sources())
        declared_copy(cursor/'local.py', HERE/'local.py', HERE/'LOCAL-EDITS.json')
        L = load(HERE/'local.py', 'local')
        L.ROOT = root
        source = L.read(parent/'WORD.json.gz')
        word, witness = construct.construct(source, L.read(HERE/'PLAN.json'))
        audit = checks.audit(word)
        controls = checks.negative_controls(word)
        local = L.replay(word)
        transpose = L.reverse_columns(word)
        need(local['public_inputs'] == 767 and local['owned_fields'] == 9
             and local['owned_lifetimes'] == 11 and local['peak_owned_fields'] == 2,
             'Exact public and owned inventory')
        print('PASS exact construction, all scalar columns, frames, ownership and controls', flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'paid_meeting_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'),
             'Unchanged complete physical caller')
        physical = C.physical(caller, word)
        print('PASS actual native maps, phases and complete physical caller', flush=True)
        declared_copy(parent/'pricing.py', HERE/'pricing.py', HERE/'PRICING-EDITS.json')
        P = load(HERE/'pricing.py', 'paid_meeting_price')
        price = P.run(local, native, caller, physical)
        controls.update(C.controls(caller))
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        controls['omit_paid_query_from_bill'] = reject(lambda: P.assemble(bad, native, caller, physical))
        bad = deepcopy(local)
        bad['helpers'][9] += 1
        controls['invent_extra_productive_target'] = reject(lambda: P.assemble(bad, native, caller, physical))
        result = dict(status='PASS_P104_PAID_MEETINGS_KAPPA_00311301600',
                      source_commit='a1534ac45401c9a9c80c07aa65c89e00e33594f8',
                      local=local, separate_columns=transpose, native=native,
                      physical_caller=physical, complete_cost=price,
                      literal_audit=audit, negative_controls=controls,
                      limits=['The five inherited framework assumptions remain.',
                              'The gain is below the requested one percent.',
                              'The huge uniform word and rounded multiplier are not materialized.',
                              'Author checks are not independent human or formal acceptance.',
                              'The selected frontier is unchanged.'])
        return P.encode(result), P.encode(witness), word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-paid-meeting-bytecode-') as cache:
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
