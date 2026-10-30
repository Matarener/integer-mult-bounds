#!/usr/bin/env python3
"""Extend an authenticated cumulative content-addressed overlay without loss.

The retained byte applier is reused unchanged. Only the new research scope
and the thirteen recovered files may be appended; every prior record and
payload is preserved. Mathematical receipts are separate from this byte
integrity operation. Apache-2.0; substantial OpenAI assistance.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import argparse
import importlib.util
import json
import os
import shutil
import stat
import tempfile
import zipfile

HERE = Path(__file__).resolve().parent
APPLIER_SHA256 = '68900a2064f0f0e27c2c34842df235fd4c3a8b8c515e3e4aa628260b645040a8'
SCOPES = ('research/kappa-rebuild', 'research/kappa-accounted-composition')


def need(value, message):
    if not value:
        raise ValueError(message)


def metadata(path):
    digest = sha256()
    count = 0
    with path.open('rb') as source:
        for block in iter(lambda:source.read(1024*1024),b''):
            digest.update(block)
            count += len(block)
    return {'bytes':count, 'sha256':digest.hexdigest(), 'mode':path.stat().st_mode&0o777}


def zip_info(name):
    info = zipfile.ZipInfo(name,(2026,10,21,0,0,0))
    info.create_system = 3
    info.external_attr = (stat.S_IFREG|0o644)<<16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def load_applier(path):
    need(sha256(path.read_bytes()).hexdigest() == APPLIER_SHA256, 'Exact retained byte-applier identity')
    spec = importlib.util.spec_from_file_location('retained_kappa_overlay',path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base',type=Path,required=True)
    parser.add_argument('--prior',type=Path,required=True)
    parser.add_argument('--applier',type=Path,required=True)
    parser.add_argument('--repo',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--manifest',type=Path)
    args = parser.parse_args()
    api = load_applier(args.applier)
    need(not args.out.exists(), 'Output must be a new file')
    need(args.repo.is_dir() and not args.repo.is_symlink(), 'Plain repository directory')
    prior, prior_receipt = api.verify_blob_data(args.base,args.prior)
    records = {r['path']:deepcopy(r) for r in prior['records']}
    for name,record in records.items():
        path = api.checked_target(args.repo,name)
        need(path.is_file() and metadata(path) == record['after'], 'Prior cumulative path changed or disappeared: '+name)
    added = {}
    for scope in SCOPES:
        directory = args.repo/scope
        need(directory.is_dir(), 'Required cumulative scope is present: '+scope)
        for path in sorted(directory.rglob('*')):
            need(not path.is_symlink(), 'No symbolic links in appended research')
            if not path.is_file() or '__pycache__' in path.parts or path.suffix=='.pyc':
                continue
            name = path.relative_to(args.repo).as_posix()
            api.normalized_member('integer-mult-bounds/'+name)
            if name not in records:
                added[name] = path
    with zipfile.ZipFile(args.base) as base:
        base_files,base_safety = api.safe_index(base)
        for name,path in added.items():
            before = api.member_hash(base,base_files[name]) if name in base_files else None
            after = metadata(path)
            kind = 'added' if before is None else 'identical' if before['sha256']==after['sha256'] else 'changed'
            records[name] = {'path':name,'before':before,'after':after,'classification':kind,
                             'mode_changed':before is not None and before['mode']!=after['mode'],
                             'source':'new_supplement','generation':'kappa-rebuild-20261021'}
    union = set(base_files)|set(records)
    for name in union:
        need(all(str(p)=='.' or str(p) not in union for p in PurePosixPath(name).parents), 'No file/directory collision')
    updates = [r for r in records.values() if r['classification']!='identical' or r.get('mode_changed')]
    representatives = {}
    for record in sorted(updates,key=lambda r:r['path']):
        representatives.setdefault(record['after']['sha256'],record)
    readme = ('''# Complete cumulative kappa research overlay

This bundle contains every path from the supplied October20 cumulative
overlay, the surviving recovery files, and the complete October21 research
scope. Nothing is deleted. Read research/kappa-rebuild/README.md after
application for the current mathematical result, proof status and replay.
The byte applier itself makes no mathematical claim and remains unchanged.

Keep the exact attached base ZIP. Extract apply_overlay.py from this bundle,
then run (replace the three paths with your local filenames):

```sh
python3 apply_overlay.py blob-verify --base BASE.zip --bundle THIS.zip
python3 apply_overlay.py blob-apply --base BASE.zip --bundle THIS.zip --repo CHECKOUT --receipt applied.json
```

The applier checks the complete base archive fingerprint and every touched
preimage. It rejects mismatches and symlinks. Per-file writes are atomic;
a repeated application is idempotent. It does not delete or validate
unrelated checkout files. It does not publish, merge, or change a remote.

An optional complete binary review patch can be generated using:

```sh
python3 apply_overlay.py review-diff --base BASE.zip --bundle THIS.zip --out cumulative-review.patch.gz
```

The earlier reported 332-entry archive discrepancy, including34 reported
dependencies, remains an explicitly unresolved historical recovery flag.
Newly reconstructed files have fresh provenance; they are not presented
as recovered originals with their lost historical identities.
''').encode()
    tool = args.applier.read_bytes()
    manifest = deepcopy(prior)
    manifest.update({
        'records':[records[name] for name in sorted(records)],
        'update_paths':sorted(r['path'] for r in updates),
        'counts':dict(Counter(r['classification'] for r in records.values())),
        'result_regular_files':len(union),'blob_sha256s':sorted(representatives),
        'supplemental_files':prior['supplemental_files']+len(added),
        'content_deduplication':{'update_paths':len(updates),'unique_blobs':len(representatives),
            'path_bytes':sum(r['after']['bytes'] for r in updates),
            'unique_blob_bytes':sum(r['after']['bytes'] for r in representatives.values())},
        'control_sha256':{'apply_overlay.py':sha256(tool).hexdigest(),'README.md':sha256(readme).hexdigest()},
        'prior_overlay':api.archive_fingerprint(args.prior),
        'prior_records_preserved_byte_for_byte':len(prior['records']),
        'current_round_paths':sorted(added),'deletions':[],
        'local_tree_audit':{'scope':'Every prior cumulative path was checked for exact bytes and mode. New files are appended only from the two named research scopes. Runtime caches are excluded.',
                            'divergent_files':[],'extra_local_files':[]},
    })
    api.validate_manifest(manifest)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix='.cumulative-build-',suffix='.zip',dir=args.out.parent,delete=False) as temp:
            temp_path = Path(temp.name)
        with zipfile.ZipFile(args.prior) as source, zipfile.ZipFile(temp_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as sink:
            for name,data in [('MANIFEST.json',(json.dumps(manifest,indent=2,sort_keys=True)+'\n').encode()),
                              ('apply_overlay.py',tool),('README.md',readme)]:
                sink.writestr(zip_info(name),data)
            old_blobs = set(prior['blob_sha256s'])
            for digest,record in sorted(representatives.items()):
                incoming = source.open('blobs/'+digest) if digest in old_blobs else added[record['path']].open('rb')
                copied = sha256(); count = 0
                with incoming, sink.open(zip_info('blobs/'+digest),'w',force_zip64=True) as target:
                    for block in iter(lambda:incoming.read(1024*1024),b''):
                        target.write(block); copied.update(block); count += len(block)
                need(copied.hexdigest()==digest and count==record['after']['bytes'], 'Source changed while packaging')
        os.link(temp_path,args.out)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    _,verification = api.verify_blob_data(args.base,args.out)
    receipt = {'schema':'extended-cumulative-kappa-overlay/1','status':'PASS_ALL_PRIOR_PATHS_PRESERVED_AND_COMPLETE_NEW_OVERLAY_VERIFIED',
               'base':api.archive_fingerprint(args.base),'prior':api.archive_fingerprint(args.prior),
               'bundle':api.archive_fingerprint(args.out),'old_records':len(prior['records']),
               'new_records':len(added),'total_records':len(records),'counts':manifest['counts'],
               'verification':verification,'deletions':[],
               'scientific_claim_not_inferred_from_byte_packaging':True}
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    args.receipt.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    if args.manifest:
        args.manifest.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','bundle','old_records','new_records','total_records','counts')}))


if __name__=='__main__':
    main()
