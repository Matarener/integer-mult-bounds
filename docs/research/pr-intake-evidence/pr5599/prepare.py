"""Export the source-bound P104 review without running scientific checks.
Douglas Colkitt with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse
import hashlib
import json
import shutil

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CHECK='research/p104-caller-independent-audit/capsule/outputs/p104-caller-route-audit-v2-20261025/check.py'

def require(ok, message):
    if not ok: raise ValueError(message)

def copy_inputs(files, target):
    for name, digest in files.items():
        rel=Path(name)
        require(not rel.is_absolute() and '..' not in rel.parts, 'Invalid source path')
        src=ROOT/rel
        require(not src.is_symlink(), 'Source symlink')
        raw=src.read_bytes()
        require(hashlib.sha256(raw).hexdigest()==digest, 'Changed source: '+name)
        dest=target/rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args=parser.parse_args()
    work=args.work.resolve()
    require(not work.exists(), 'Use a fresh work directory')
    work.mkdir(parents=True)
    export=json.loads((HERE/'EXPORT.json').read_text())
    copy_inputs(export['files'], work/'source')
    original=json.loads((HERE/'CALLER-ORIGINAL.json').read_text())
    copy_inputs(original, work/'caller-source')
    (work/'caller-source'/CHECK).write_bytes((HERE/'caller-check.py').read_bytes())
    adapted=json.loads((HERE/'CALLER-EXPORT.json').read_text())
    for name, digest in adapted.items():
        require(hashlib.sha256((work/'caller-source'/name).read_bytes()).hexdigest()==digest, 'Caller adapter mismatch')
    for name in ('run_bounded.py','run_caller.py','EXPORT.json','CALLER-ORIGINAL.json','CALLER-EXPORT.json'):
        shutil.copy2(HERE/name, work/name)
    print('PASS_REVIEW_EXPORT_ONLY (no scientific replay)')

if __name__=='__main__':main()
