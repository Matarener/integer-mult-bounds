#!/usr/bin/env python3
"""Verify exact scoped checkpoint bytes and claim bindings, without rewriting.

Use replay_critical.py for the separately regenerated scientific chain.
Apache-2.0; substantial OpenAI assistance.
"""
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCOPES = ('research/kappa-rebuild','research/kappa-accounted-composition')


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def checked(name):
    parts = PurePosixPath(name)
    need(not parts.is_absolute() and all(p not in ('.','..') for p in parts.parts), 'Safe relative path')
    p = ROOT
    for part in parts.parts:
        p = p/part
        need(not p.is_symlink(), 'No symlink in checkpoint path')
    need(p.is_file(), 'Checkpoint file present: '+name)
    return p


def main():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    expected = set()
    for row in manifest['files']:
        name = row['path']; need(name not in expected,'Unique checkpoint path'); expected.add(name)
        p = checked(name)
        need(p.stat().st_size == row['bytes'], 'Exact byte count: '+name)
        need(p.stat().st_mode&0o777 == row['mode'], 'Exact file mode: '+name)
        need(sha256(p.read_bytes()).hexdigest() == row['sha256'], 'Exact checkpoint digest: '+name)
    actual = set()
    for scope in SCOPES:
        for p in (ROOT/scope).rglob('*'):
            need(not p.is_symlink(), 'No symlink in scopes')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc' and p != HERE/'SOURCES.json':
                actual.add(p.relative_to(ROOT).as_posix())
    need(actual == expected, 'Every scoped non-cache file is in the manifest')
    claim = json.loads((HERE/'CLAIM.json').read_text())
    for name,digest in claim['source_sha256'].items():
        need(sha256(checked(name).read_bytes()).hexdigest() == digest,'Claim source identity: '+name)
    need(claim['kappa'] == '23/10000' and claim['official_selected_frontier_modified'] is False,'Recorded claim scope')
    print(json.dumps({'status':'PASS_EXACT_SCOPE_AND_CONDITIONAL_CLAIM_BINDINGS',
        'files':len(expected),'source_bindings':len(claim['source_sha256']),
        'kappa':claim['kappa'],'scientific_replay_command':'research/kappa-rebuild/replay_critical.py',
        'mathematical_proof_not_inferred_from_byte_integrity':True},sort_keys=True))


if __name__ == '__main__':
    main()
