"""Verify the materialized PR5806 hybrid and its complete conditional price.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
Retain PR5806 and every parent construction notice.
"""
import argparse
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


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def reject(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError('Invalid hybrid was accepted')


def declared_copy(source, target, edits):
    text = source.read_text()
    for before, after in json.loads(edits.read_text()):
        need(text.count(before) == 1, 'Unique declared source edit')
        text = text.replace(before, after)
    need(text == target.read_text(), 'Only declared source edits: '+target.name)


def run():
    with ExitStack() as contexts:
        parent, _ = contexts.enter_context(sources())
        cursor = parent
        for depth in range(8):
            module = load(cursor/'sources.py', 'hybrid_source_'+str(depth))
            cursor, root = contexts.enter_context(module.sources())
            if depth == 0:
                common_source = cursor
        L = load(HERE/'local.py', 'local'); L.ROOT = root
        declared_copy(parent/'local.py', HERE/'local.py', HERE/'LOCAL-EDITS.json')
        declared_copy(parent/'pricing.py', HERE/'pricing.py', HERE/'PRICING-EDITS.json')
        common = L.read(common_source/'WORD.json.gz')
        source = L.read(parent/'WORD.json.gz')
        bindings = {r['archive_role']: r for r in L.read(HERE/'SOURCES.json')['paper_word_bindings']}
        for role, value in [('common', common), ('accumulated', source)]:
            need(sha256(canonical(value)).hexdigest() == bindings[role]['canonical_sha256'],
                 'Archived word equals the exact PR5806 decoded source: '+role)
        edits, plan = L.read(HERE/'inputs/R22-EDITS.json'), L.read(HERE/'inputs/SECOND-BLOCK.json')
        word = construct.construct(common, source, edits, plan)
        local, transpose = L.replay(word), L.reverse_columns(word)
        need(local['paid'] == {1:2231, 2:456, 3:498, 4:100, 5:157, 6:9, 7:6}, 'Exact hybrid paid bill')
        need(local['helpers'] == {1:22, 2:7, 3:4, 4:107, 5:10, 7:9, 8:18, 9:385},
             'Exact independent helper bill')
        need((local['owned_fields'], local['owned_lifetimes'], local['peak_owned_fields']) == (28, 30, 13),
             'Every owned label, lifetime and peak')
        controls = {}
        for name, predicate in [('missing_new_query', lambda e:e[0]=='MOVE' and 1092 in e[2:4]),
                                ('missing_owned_clear', lambda e:e[0]=='CLEAR' and e[1]==797),
                                ('missing_sum_delivery', lambda e:e[0]=='ADD' and e[2]==797)]:
            bad = deepcopy(word)
            at = next(i for i,e in enumerate(bad['program']) if predicate(e))
            del bad['program'][at]
            controls[name] = reject(lambda:L.replay(bad))
        bad = deepcopy(word); bad['final'][225] = source['final'][225]
        controls['old_helper_credit'] = reject(lambda:L.replay(bad))
        bad = deepcopy(source)
        at = next(i for i,e in enumerate(bad['program']) if e[0]=='ADD' and construct.touches(e))
        bad['program'][at][-2] = '99'
        controls['wrong_protected_trace'] = reject(lambda:construct.construct(common,bad,edits,plan))
        print('PASS exact hybrid, all798 columns, separate transpose and source controls',flush=True)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'hybrid_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'), 'Exact source caller')
        physical = C.physical(caller, word)
        print('PASS complete native maps, phases, helper matchers and physical caller',flush=True)
        P = load(HERE/'pricing.py', 'hybrid_pricing')
        price = P.run(local, native, caller, physical)
        need(price['previous_pr5802'] == L.read(parent/'RESULT.json')['complete_cost']['kappa'],
             'Exact previous conditional claim')
        controls.update(C.controls(caller))
        bad = deepcopy(local); bad['paid'][1] -= 1
        controls['missing_paid_query'] = reject(lambda:P.assemble(bad,native,caller,physical))
        bad = deepcopy(local); bad['helpers'][9] += 1
        controls['extra_productive_target'] = reject(lambda:P.assemble(bad,native,caller,physical))
        result = {'status':'PASS_P104_MATERIALIZED_HYBRID_KAPPA_00312360607355',
                  'source_pr5806':'20e7289b63d240715aa96006571ae38a46291d97',
                  'canonical_word_sha256':sha256(canonical(word)).hexdigest(),
                  'instructions':len(word['program']),'local':local,'separate_columns':transpose,
                  'native':native,'physical_caller':physical,'complete_cost':price,'negative_controls':controls,
                  'limits':['The five inherited framework assumptions remain.',
                            'The large uniform word and rounded multiplier are not materialized.',
                            'Author checks are not independent acceptance.',
                            'The selected frontier is unchanged.']}
        return P.encode(result), word


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='p104-hybrid-cache-') as cache:
        sys.pycache_prefix=cache
        result,word=run()
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
    for name,value in [('RESULT.json',result),('WORD.json.gz',word)]:
        raw=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
        if args.output:
            (args.output/name).write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
        else:
            retained=(HERE/name).read_bytes()
            if name.endswith('.gz'):retained=gzip.decompress(retained)
            need(canonical(json.loads(retained))==canonical(value),'Complete typed receipt: '+name)
    print(result['status'])


if __name__=='__main__':main()
