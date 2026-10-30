"""Replay the complete composed P104 supplier. Ali Romman with OpenAI Codex.

The native, controller, interval, compiler and outer engines retain their
source authors and assumptions. Apache-2.0.
"""
import argparse
from copy import deepcopy
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import construct


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def reject(action):
    try:
        action()
    except ValueError as e:
        return str(e)
    raise ValueError('Invalid control accepted')


def run(quick=False):
    pins = json.loads((HERE/'SOURCE-CONTEXT.json').read_text())
    for p in pins:
        raw = (HERE/p['local']).read_bytes()
        need(len(raw) == p['size'] and sha256(raw).hexdigest() == p['sha256'], 'Exact source: '+p['local'])
    neutral = HERE/'inputs/pr5644'
    S = load(neutral/'sources.py', 'composed_sources')
    cleanup = load(neutral/'construct.py', 'retained_cleanup')
    with S.sources() as (parent, root):
        L = load(parent/'local.py', 'local')
        source = L.read(parent/'WORD.json.gz')
        witnesses = L.read(neutral/'WITNESS.json')
        word, changes, local, neutral_word, old = construct.compose(source, witnesses, cleanup, L)
        need(neutral_word == L.read(neutral/'WORD.json.gz'), 'Exact regenerated PR5644 word')
        need(construct.a2(source,L)['program'] == L.read(HERE/'inputs/pr5643/WORD.json.gz')['program'], 'Exact regenerated PR5643 word')
        need(local['real_scalar_allowance'] == 220220, 'Complete ordinary scalar charge')
        need((local['public_inputs'],local['owned_fields'],local['owned_lifetimes'],local['peak_owned_fields']) == (743,9,11,2), 'Complete input and owned inventory')
        print('PASS both source constructions and both composition orders', flush=True)
        if quick:
            print('PASS_P104_A2_CLEANUP_QUICK', flush=True)
            return None, word
        columns = L.reverse_columns(word)
        native = L.native(word)
        C = load(root/'research/p104-productive-controller/caller.py', 'composition_caller')
        caller = C.construct()
        need(caller == L.read(root/'research/p104-productive-controller/CONTROLLER.json'), 'Exact retained caller')
        physical = C.physical(caller, word)
        print('PASS all columns, native phases and complete physical caller', flush=True)
        original = (neutral/'pricing.py').read_text()
        for before, after in json.loads((HERE/'PRICING-EDITS.json').read_text()):
            need(original.count(before) == 1, 'Unique declared price edit')
            original = original.replace(before, after)
        need(original == (HERE/'pricing.py').read_text(), 'Only declared price changes')
        P = load(HERE/'pricing.py', 'composition_price')
        price = P.run(local,native,caller,physical)
        print('PASS two exact moment engines, compiler and all outer predicates', price['raw_root_interval'], flush=True)
        controls = C.controls(caller)
        bad = deepcopy(word)
        bad['program'].remove(['ADD',340,715,'-4',396])
        controls['missing_A2_correction'] = reject(lambda:L.replay(bad))
        bad = deepcopy(word)
        bad['program'].pop(0)
        controls['missing_helper_preparation'] = reject(lambda:L.replay(bad))
        bad = deepcopy(word)
        bad['program'].pop(max(i for i,e in enumerate(bad['program']) if e[0] == 'CLEAR'))
        controls['missing_owned_clear'] = reject(lambda:L.replay(bad))
        bad = deepcopy(local)
        bad['paid'][1] -= 1
        controls['unfunded_query'] = reject(lambda:P.assemble(bad,native,caller,physical))
        bad = deepcopy(local)
        bad['helpers'][1] += 1
        controls['extra_target'] = reject(lambda:P.assemble(bad,native,caller,physical))
        return P.encode(dict(status='PASS_P104_A2_CLEANUP_KAPPA_00310644469',
                             source_heads={str(p['pr']):p['commit'] for p in pins},
                             changes=changes, local=local, separate_columns=columns,
                             native=native, physical=physical, complete_cost=price, controls=controls)),word


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--quick', action='store_true')
    args = parser.parse_args()
    result, word = run(args.quick)
    if args.quick:
        return
    for name, value in [('RESULT.json',result),('WORD.json.gz',word)]:
        path = HERE/name
        if args.write:
            raw = (json.dumps(value,sort_keys=True,indent=None if name.endswith('.gz') else 2)+'\n').encode()
            path.write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
        else:
            raw = path.read_bytes()
            need(json.loads(gzip.decompress(raw) if name.endswith('.gz') else raw) == value, 'Exact saved artifact: '+name)
    print(result['status'],flush=True)


if __name__ == '__main__':
    main()
