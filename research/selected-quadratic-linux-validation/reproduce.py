"""Prepare an isolated Git-free reproduction of the frozen Linux experiment.

The measured scientific source and original measurement runner are unchanged.
Prepared for Clear1nsight with OpenAI Codex assistance; Apache-2.0.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ARCHIVE_SHA256 = 'a3a4478938171072f7df7547f7b1e1d0ff080aa42083103450e7d02f509bfc26'
MANIFEST_SHA256 = '7be632febc51fa5040cdd06a86c1c4f8b95c2632cc885b49af05bba838b672be'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def prepare(destination):
    destination = Path(destination).resolve()
    require(not destination.exists(), 'Use a new reproduction directory')
    archive = HERE/'inputs/PR5757.tar'
    raw = archive.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==ARCHIVE_SHA256, 'Original official export SHA256')
    manifest_raw = (HERE/'INPUT-MANIFEST.json').read_bytes()
    require(hashlib.sha256(manifest_raw).hexdigest()==MANIFEST_SHA256,'Source manifest binding')
    manifest = json.loads(manifest_raw)
    rows = {r['path']:r for r in manifest['files']}
    require(len(rows)==len(manifest['files'])==54, 'Complete 54-file source manifest')
    with tarfile.open(archive,'r:') as stream:
        members = stream.getmembers()
        names = [m.name for m in members]
        require(len(names)==55 and len(set(names))==55, 'No duplicate or missing archive members')
        require(set(names)==set(rows)|{'.research-export.json'}, 'Exact official export inventory')
        content = {}
        for member in members:
            require(member.isfile() and 0<=member.size<=4*1024**2, 'Bounded regular archive file')
            value = stream.extractfile(member).read()
            if member.name in rows:
                row = rows[member.name]
                require(len(value)==row['bytes'] and hashlib.sha256(value).hexdigest()==row['sha256'], 'Exact source bytes: '+member.name)
                require(hashlib.sha1(b'blob '+str(len(value)).encode()+b'\0'+value).hexdigest()==row['git_blob'], 'Exact source blob: '+member.name)
                # Only authenticated manifest paths are materialized, never arbitrary tar paths.
                parts = Path(member.name).parts
                require(parts and not Path(member.name).is_absolute() and '..' not in parts, 'Canonical retained path')
                content[member.name] = value
            else:
                receipt = json.loads(value)
                require(receipt['commit']==manifest['source_head'], 'Official source commit')
    destination.mkdir(parents=True)
    source = destination/'payload/source'
    source.mkdir(parents=True)
    for name,value in content.items():
        path = source/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(value)
        path.chmod(0o444)
    for path in sorted(source.rglob('*'),reverse=True):
        if path.is_dir(): path.chmod(0o555)
    source.chmod(0o555)
    shutil.copyfile(HERE/'INPUT-MANIFEST.json',destination/'PAYLOAD-SOURCES.json')
    shutil.copyfile(HERE/'measurement-runner.py',destination/'guarded_runner.py')
    print('PASS_PREPARED_EXACT_READONLY_SOURCE',destination)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=('prepare','pair','remaining','qualification','cross-normal','all'))
    parser.add_argument('--workdir',type=Path,required=True)
    args=parser.parse_args()
    if args.phase in ('prepare','all'):
        prepare(args.workdir)
        if args.phase=='prepare':
            return
    runner=args.workdir.resolve()/'guarded_runner.py'
    require(runner.is_file() and hashlib.sha256(runner.read_bytes()).digest()==hashlib.sha256((HERE/'measurement-runner.py').read_bytes()).digest(), 'Exact measurement runner')
    require(hashlib.sha256((args.workdir.resolve()/'PAYLOAD-SOURCES.json').read_bytes()).hexdigest()==MANIFEST_SHA256,'Exact reproduction source manifest')
    phases=('pair','remaining','qualification','cross-normal') if args.phase=='all' else (args.phase,)
    for phase in phases:
        if phase=='cross-normal':
            driver="import runpy,fcntl,sys; m=runpy.run_path(sys.argv[1]); lock=(m['HERE']/'execution.lock').open('w'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB); m['run']('qualification-cross-normal','research/selected-quadratic-replay/cross.py')"
            command=[sys.executable,'-B','-c',driver,str(runner)]
        else:
            command=[sys.executable,'-B',str(runner),phase]
        completed=subprocess.run(command)
        if completed.returncode:
            raise SystemExit(completed.returncode)

if __name__=='__main__':
    main()
