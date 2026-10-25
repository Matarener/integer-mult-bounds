#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate exact shipped native runs or actual fresh compiler sources.

These are input/provenance checks, not another native semantic replay. The
complete native interpreters and ordinary admission remain separate gates.
Substantial OpenAI assistance; retained PR3734 / PR2768 source credit is kept
in the authenticated scientific source and predecessor native receipts.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
PINS_SHA256='244f97a4590856fe19db10dfdcff80a35e07595235a1863d7abc767a1f4c7568'
STEPS=['native','ledgers','local-replay','wrappers','phases']

def need(value,message):
    if not value:raise RuntimeError(message)

def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(4*1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()

def read(path):return json.loads(Path(path).read_bytes())

def tree(path,exclude=()):
    path=Path(path)
    need(path.is_dir() and not path.is_symlink(),'real directory required: '+str(path))
    result={}
    for item in sorted(path.rglob('*')):
        need(not item.is_symlink(),'no symlink in authenticated tree: '+str(item))
        if item.is_file():
            name=item.relative_to(path).as_posix()
            if name not in exclude:result[name]=sha(item)
    return result

def map_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def load_pins():
    path=HERE/'NATIVE-PINS.json'
    need(sha(path)==PINS_SHA256,'immutable shipped-native pin file')
    pins=read(path)
    need(pins['status']=='PINNED_SHIPPED_RECEIVER_NATIVE_RUNS' and set(pins['providers'])=={'base','extra'},'two pinned native providers')
    for tag,p in pins['providers'].items():
        need(p['directory']=='native-'+tag and len(p['files'])==39 and len(p['native_output_files'])==12 and len(p['scientific_source_files'])==18,'complete pinned run inventory')
        need({k[7:]:v for k,v in p['files'].items() if k.startswith('source/')}==p['scientific_source_files'],'source pin projection')
        need({k[7:]:v for k,v in p['files'].items() if k.startswith('native/')}==p['native_output_files'],'native output pin projection')
        need(p['files']['INPUT.json.gz']==p['word_sha256'],'pinned input word')
    return pins

def authenticate_fresh_native(run,tag):
    """Hash actual scientific source bytes of a completed fresh target run.

    Regenerated output bytes and elapsed times may differ from the shipped
    run. Exact source identity, target input, source declarations, stage order,
    successful statuses, and complete output inventory must still agree.
    """
    pins=load_pins();need(tag in pins['providers'],'known native provider')
    p=pins['providers'][tag];run=Path(run)
    actual_source=tree(run/'source')
    need(actual_source==p['scientific_source_files'],'actual eighteen scientific source files must match PR3734 pins')
    result=read(run/'RESULT.json')
    need(result['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY','completed native run status')
    need(result['source_sha256']==actual_source,'native RESULT declarations must equal the actual authenticated sources')
    need(result['word_sha256']==sha(run/'INPUT.json.gz')==p['word_sha256'],'exact target input of native execution')
    for rows in [result['steps'],read(run/'native/STEPS.json')]:
        need([r['step'] for r in rows]==STEPS and all(r['exit_code']==0 for r in rows),'all five native stages in order')
    outputs=tree(run/'native')
    need(set(outputs)==set(p['native_output_files']),'complete fresh native output inventory')
    return dict(provider=tag,word_sha256=p['word_sha256'],scientific_source_files=len(actual_source),
                scientific_source_tree_sha256=map_sha(actual_source),native_output_files=len(outputs),
                native_output_tree_sha256=map_sha(outputs),result_sha256=sha(run/'RESULT.json'),
                source_declarations_match_actual_bytes=True)

def authenticate_reused(root):
    """Accept only an exact byte-preserving copy of both shipped native runs."""
    root=Path(root);pins=load_pins();providers={}
    for tag,p in pins['providers'].items():
        run=root/p['directory'];actual=tree(run)
        need(actual==p['files'],'exact byte-preserving shipped native run: '+tag)
        checked=authenticate_fresh_native(run,tag)
        checked.update(exact_shipped_files=len(actual),exact_shipped_tree_sha256=map_sha(actual))
        providers[tag]=checked
    return dict(status='PASS_EXACT_SHIPPED_NATIVE_REUSE',pins_sha256=PINS_SHA256,providers=providers,
                scope='All 78 shipped run files and both actual eighteen-file scientific source trees authenticated. This command binds completed evidence; it does not rerun native semantics.')

def authenticate_admission_inputs(work):
    """Read-only check of the two current caches in an already prepared run."""
    work=Path(work);pins=load_pins();source=work/'inputs/source'
    receipt=read(work/'NATIVE-RECEIPT.json');providers={}
    for tag,p in pins['providers'].items():
        word=source/'new/borrow/words'/('BORROW-WORD-43'+tag+'.json.gz')
        need(sha(word)==p['word_sha256'],'prepared candidate container: '+tag)
        vendor=source/'new/fastnative/vendor'
        # The surrounding source manifest authenticates the full vendor tree;
        # these are the exact eighteen files copied and executed by this engine.
        actual_source={name:sha(vendor/name) for name in p['scientific_source_files']}
        need(actual_source==p['scientific_source_files'],'prepared compiler source bytes: '+tag)
        entry=work/'inputs/native-cache'/p['word_sha256']
        outputs=tree(entry,exclude=('CACHE.json',))
        need(outputs==p['native_output_files'],'prepared native cache equals shipped completed outputs: '+tag)
        cache=read(entry/'CACHE.json')
        need(cache['word_sha256']==p['word_sha256'] and cache['files']==outputs,'prepared CACHE declaration binds actual files')
        binding=receipt['providers'][tag]
        need(binding['word_sha256']==p['word_sha256'] and binding['complete_native_files']==outputs,'prepared native receipt binds actual files')
        for name,digest in outputs.items():
            need(receipt['cache_files'][p['word_sha256']+'/'+name]==digest,'top-level native receipt binds current cache')
        providers[tag]=dict(word_sha256=p['word_sha256'],native_output_files=len(outputs),
                            native_output_tree_sha256=map_sha(outputs),scientific_source_files=len(actual_source),
                            scientific_source_tree_sha256=map_sha(actual_source))
    return dict(status='PASS_PREPARED_ADMISSION_CURRENT_NATIVE_INPUTS',pins_sha256=PINS_SHA256,
                source_manifest_sha256=sha(source/'MANIFEST.json'),native_receipt_sha256=sha(work/'NATIVE-RECEIPT.json'),
                providers=providers,retained_ancestry_not_reaudited=True,
                scope='Read-only identity check of both new-provider prepared caches and their actual compiler sources. Existing ancestor caches and complete admission are separate bound gates.')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    group=ap.add_mutually_exclusive_group()
    group.add_argument('--reuse-root',type=Path)
    group.add_argument('--fresh-run',type=Path)
    group.add_argument('--admission-work',type=Path)
    ap.add_argument('--provider',choices=['base','extra'])
    ap.add_argument('--out',type=Path)
    args=ap.parse_args()
    if args.fresh_run:
        need(args.provider is not None,'--fresh-run requires --provider')
        result=dict(status='PASS_ACTUAL_FRESH_NATIVE_SOURCES',pins_sha256=PINS_SHA256,
                    native=authenticate_fresh_native(args.fresh_run,args.provider))
    elif args.admission_work:result=authenticate_admission_inputs(args.admission_work)
    else:result=authenticate_reused(args.reuse_root or HERE.parent/'native-alternatives')
    payload=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(payload)
    print(payload,end='')

if __name__=='__main__':main()
