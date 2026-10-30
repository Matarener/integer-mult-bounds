#!/usr/bin/env python3
"""Source-pinned extension of the selected PR5599 independent caller adapter.

Prepare is lightweight. `run ... original` and `run ... candidate` are separate,
serial scientific replays; neither is implicit. Prepared for flyingviper with
substantial OpenAI Codex assistance. Apache-2.0; original notices are retained.
"""
from pathlib import Path
import argparse
import contextlib
import difflib
import gzip
import hashlib
import importlib.util
import json
import os
import sys
import types

HERE = Path(__file__).resolve().parent
SELECTED_SHA = '6fce1e331747aebee13ecc6e33ab2fd49b9383640c20546e245be3e624933b52'
ORIGINAL_SHA = '0e5e0e3d56165437fc2821f41927e3f0cae838c60841a93e8b5cb46caeb7657c'
EXPECTED_SHA = 'b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009'

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

def load_interface():
    spec = importlib.util.spec_from_file_location('p104_caller_interface', HERE/'interface.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def adapted(source):
    edits = []
    def replace(old, new, label):
        nonlocal source
        need(source.count(old) == 1, 'Unique selected-checker anchor: '+label)
        source = source.replace(old, new)
        edits.append(label)
    replace('B = Path(__file__).resolve().parent',
            "B = Path(os.environ['P104_CAPSULE_CHECKER']).resolve().parent\nfrom p104_caller_interface import audit, allocation, caller_schedule", 'authenticated capsule location')
    replace("    helper_count = public - 208\n    field_count = 3328 + 18*helper_count",
            "    interface = audit(word, source)\n    helper_count = interface['helper_count']\n    field_count = interface['productive_fields']", 'independent public inventory')
    replace("source['physical_caller']['route_payload_sha256']", "source_physical(source)['route_payload_sha256']", 'source physical receipt schema')
    replace("    helpers = [r for r in range(public) if r not in local_main]",
            "    helpers = interface['helpers']\n    need(local_main == set(interface['main']), 'Independent main inventory agrees')", 'retired-public target exclusion')
    old = """    fields = []
    for site, event in enumerate(full):
        mapping = {}
        for p, r in enumerate(word['live']):
            mapping[r], mapping[r+112] = 2*event[2]*104+p, (2*event[2]+1)*104+p
        mapping.update({h:3328+site*helper_count+i for i, h in enumerate(helpers)})
        need(len(mapping) == len(set(mapping.values())) == public, 'injective full-call public inventory')
        fields.append({'site': site, 'stage': event[1], 'local_to_global': [mapping[i] for i in range(public)], 'owned_lifetimes': {f'{public}..{public+7}':field_count}})"""
    replace(old, "    fields = allocation(interface, full, word['live'])\n    global_owned = caller_schedule(interface, controller, fields)\n    controls.update(interface['controls'])\n    controls.update(global_owned['controls'])", 'literal overlapping owned schedule')
    replace("+4*104+4*8)*1000", "+4*104+4*interface['lifetime_count'])*1000", 'ordinary recount actual owned lifetimes')
    replace("    events, boundary = len(controller['physical_events'])",
            "    need(scalar == interface['scalar'] and nr['local_routes'] == interface['routes'], 'Second literal ordinary recount agrees')\n    events, boundary = len(controller['physical_events'])", 'second ordinary recount agreement')
    replace("'schema':'p104-physical-caller-target-binding/v1'", "'schema':'p104-physical-caller-target-binding/explicit-owned-interface-v2'", 'result interface schema')
    replace("'owned_peak':1}", "'owned_peak':interface['peak']}", 'actual simultaneous scratch census')
    replace("    checkpoint('invoice_complete', paid=sum(paid.values()), targets=sum(targets.values()))",
            """    result['candidate_input'] = CANDIDATE_INPUT
    result['local_interface'] = {key:interface[key] for key in
        ('public_slots','fields','independent','owned','retired','helper_count','productive_fields','lifetime_count','peak')}
    result['owned_scratch_fields'] = list(range(field_count, field_count+interface['peak']))
    result['owned_caller_schedule'] = global_owned
    checkpoint('invoice_complete', paid=sum(paid.values()), targets=sum(targets.values()))""", 'explicit candidate source and scratch evidence')
    # Keep the existing route, Laurent, native-normalizer, phase and fault code.
    compile(source, '<adapted-caller>', 'exec')
    return source, edits

def source_physical(result):
    keys = [key for key in ('physical_caller', 'physical') if key in result]
    need(keys, 'Source contains physical caller evidence')
    if len(keys) == 2:
        need(result[keys[0]] == result[keys[1]], 'Unambiguous physical caller evidence')
    return result[keys[0]]

def original_paths(repo):
    package = repo/'research/p104-caller-independent-audit'
    return (repo/'docs/research/pr-intake-evidence/pr5599/caller-check.py',
            package/'capsule/outputs/p104-caller-route-audit-v2-20261025/check.py',
            package/'expected/caller.json.gz')

def prepare(args):
    repo, word_path, result_path = map(lambda p:Path(p).resolve(), (args.repo,args.word,args.result))
    selected, original, expected = original_paths(repo)
    need(sha(selected.read_bytes()) == SELECTED_SHA, 'Selected independent adapter pin')
    need(sha(original.read_bytes()) == ORIGINAL_SHA, 'Original positive-control checker pin')
    need(sha(gzip.decompress(expected.read_bytes())) == EXPECTED_SHA, 'Original scientific output pin')
    word, result = read(word_path), read(result_path)
    interface = load_interface().audit(word, result)
    source_physical(result)
    new_source, edits = adapted(selected.read_text())
    binding = dict(schema='p104-explicit-interface-binding/v1', declared_source_head=args.head,
        repo=str(repo), word=str(word_path), result=str(result_path),
        word_bytes_sha256=sha(word_path.read_bytes()), word_canonical_sha256=sha(canonical(word)),
        result_bytes_sha256=sha(result_path.read_bytes()), selected_checker_sha256=SELECTED_SHA,
        original_checker_sha256=ORIGINAL_SHA, original_output_sha256=EXPECTED_SHA,
        interface_sha256=sha((HERE/'interface.py').read_bytes()), adapter_sha256=sha(Path(__file__).read_bytes()),
        generated_checker_sha256=sha(new_source.encode()), edits=edits)
    stem = HERE/args.name
    need(stem.parent == HERE and stem.name == args.name, 'Outputs stay inside the assigned work directory')
    stem.with_suffix('.binding.json').write_text(json.dumps(binding,sort_keys=True,indent=2)+'\n')
    stem.with_suffix('.interface.json').write_text(json.dumps(interface,sort_keys=True,indent=2)+'\n')
    stem.with_suffix('.check.py').write_text(new_source, newline='\n')
    diff = difflib.unified_diff(selected.read_text().splitlines(True),new_source.splitlines(True),
                                fromfile='selected-caller-check.py',tofile='explicit-interface-caller-check.py')
    stem.with_suffix('.patch').write_text(''.join(diff), newline='\n')
    print(json.dumps(dict(status='PREPARED_LIGHTWEIGHT_INTERFACE_PASS',binding=str(stem.with_suffix('.binding.json')),
                          helper_count=interface['helper_count'],peak=interface['peak'],lifetimes=interface['lifetime_count']),sort_keys=True))

def run(args):
    binding_path = Path(args.binding).resolve()
    need(binding_path.parent == HERE, 'Use a binding in the assigned work directory')
    binding = read(binding_path)
    selected, original, expected = original_paths(Path(binding['repo']))
    need(sha(selected.read_bytes()) == SELECTED_SHA and sha(original.read_bytes()) == ORIGINAL_SHA, 'Both source checker pins')
    need(sha(gzip.decompress(expected.read_bytes())) == EXPECTED_SHA, 'Positive scientific output pin')
    need(sha((HERE/'interface.py').read_bytes()) == binding['interface_sha256'] and
         sha(Path(__file__).read_bytes()) == binding['adapter_sha256'], 'Prepared adapter code unchanged')
    for key in ('word','result'):
        need(sha(Path(binding[key]).read_bytes()) == binding[key+'_bytes_sha256'], 'Bound candidate '+key)
    need(sha(canonical(read(Path(binding['word'])))) == binding['word_canonical_sha256'], 'Bound canonical candidate word')
    # Windows has no resource module. This supplies only nullable operational
    # RSS metadata; the original checker and its scientific output are unchanged.
    try:
        import resource
    except ImportError:
        sys.modules['resource'] = types.SimpleNamespace(RUSAGE_SELF=0,
            getrusage=lambda _:types.SimpleNamespace(ru_maxrss=None))
    for key in ('P104_WORD','P104_RESULT','P104_TRACE_FILE','P104_CAPSULE_CHECKER'):
        os.environ.pop(key,None)
    prefix = binding_path.name.removesuffix('.binding.json')+'-'+args.mode
    output = HERE/(prefix+'.json')
    trace = HERE/(prefix+'.jsonl')
    need(not output.exists() and not trace.exists(), 'Keep existing run evidence; choose a fresh binding name')
    os.environ['P104_TRACE_FILE'] = str(trace)
    namespace = dict(__name__='__main__',__file__=str(original))
    if args.mode == 'original':
        source = original.read_text()
    else:
        source, _ = adapted(selected.read_text())
        need(sha(source.encode()) == binding['generated_checker_sha256'], 'Prepared generated checker unchanged')
        os.environ.update(P104_WORD=binding['word'],P104_RESULT=binding['result'],P104_CAPSULE_CHECKER=str(original))
        module = load_interface()
        sys.modules['p104_caller_interface'] = module
        namespace.update(source_physical=source_physical,CANDIDATE_INPUT={k:binding[k] for k in
            ('declared_source_head','word_bytes_sha256','word_canonical_sha256','result_bytes_sha256','selected_checker_sha256','interface_sha256','adapter_sha256')})
    with output.open('w',encoding='utf-8',newline='\n') as stream, contextlib.redirect_stdout(stream):
        exec(compile(source,str(original) if args.mode == 'original' else prefix+'.check.py','exec'),namespace)
    if args.mode == 'original':
        need(output.read_bytes() == gzip.decompress(expected.read_bytes()), 'Unmodified original full scientific positive control')
    data = read(output)
    receipt = dict(status='PASS_ORIGINAL_BYTE_EQUAL' if args.mode == 'original' else 'PASS_CANDIDATE_SCOPED_CALLER',
        output=str(output),output_sha256=sha(output.read_bytes()),native_checks=data['native_checks'],ordinary=data['ordinary'],
        controls=data['controls'],paid=sum(data['paid'].values()),targets=sum(data['targets'].values()))
    (HERE/(prefix+'-receipt.json')).write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    p=commands.add_parser('prepare')
    for key in ('repo','word','result','head','name'): p.add_argument('--'+key,required=True)
    p=commands.add_parser('run');p.add_argument('binding');p.add_argument('mode',choices=('original','candidate'))
    args=parser.parse_args()
    (prepare if args.command == 'prepare' else run)(args)
