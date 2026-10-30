# SPDX-License-Identifier: Apache-2.0
"""Recreate exact scientific inputs from frozen main files and a pinned overlay.
This module does not run an optimizer or weaken any scientific validator.
"""
import hashlib
import json
from pathlib import PurePosixPath
import tarfile

MAX_FILE = 32 * 1024**2
MAX_TOTAL = 64 * 1024**2
MAX_ENTRIES = 1000


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(name):
    need(type(name) is str and name, 'nonempty string path')
    p = PurePosixPath(name)
    need(not p.is_absolute() and '..' not in p.parts and '\\' not in name,
         'unsafe path')
    need(p.as_posix() == name and all(x not in ('', '.') for x in name.split('/')),
         'non-normal path')
    return p


def authenticate(recipe, overlay, recipe_sha, overlay_sha):
    need(recipe.stat().st_size <= MAX_FILE and overlay.stat().st_size <= MAX_FILE,
         'bounded recipe and archive')
    need(sha(recipe) == recipe_sha and sha(overlay) == overlay_sha,
         'unauthenticated recipe/archive')
    data = json.loads(recipe.read_text())
    entries = data['entries']
    need(0 < len(entries) <= MAX_ENTRIES, 'entry count')
    total = 0
    for name, record in entries.items():
        safe(name)
        need(type(record['bytes']) is int and 0 <= record['bytes'] <= MAX_FILE,
             'file size')
        total += record['bytes']
        need(total <= MAX_TOTAL, 'total bytes')
        need(record['source_kind'] in ('canonical_main', 'overlay'), 'source kind')
    return data


def main_files(root, entries):
    pending = {}
    for name, record in entries.items():
        if record['source_kind'] != 'canonical_main':
            continue
        relative = safe(record['source_path'])
        path = root / relative
        need(path.resolve().is_relative_to(root.resolve()), 'source escapes root')
        need(not any((root / PurePosixPath(*relative.parts[:i])).is_symlink()
                     for i in range(1, len(relative.parts) + 1)), 'source symlink')
        need(path.is_file() and path.stat().st_size == record['bytes'], 'source size')
        body = path.read_bytes()
        need(hashlib.sha256(body).hexdigest() == record['sha256'], 'changed main file')
        pending[name] = body
    return pending


def overlay_files(archive, entries, pending):
    seen = set()
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar:
            safe(member.name)
            need(member.isfile() and member.name not in seen and
                 member.name in entries, 'unexpected/nonregular/duplicate member')
            seen.add(member.name)
            record = entries[member.name]
            need(record['source_kind'] == 'overlay' and
                 member.size == record['bytes'], 'wrong archive entry')
            stream = tar.extractfile(member)
            need(stream is not None, 'missing regular-file stream')
            with stream:
                body = stream.read(MAX_FILE + 1)
            need(len(body) == record['bytes'] and
                 hashlib.sha256(body).hexdigest() == record['sha256'], 'changed payload')
            pending[member.name] = body
    expected = {n for n, r in entries.items() if r['source_kind'] == 'overlay'}
    need(seen == expected and set(pending) == set(entries), 'incomplete archive')


def build(root, recipe, overlay, out, recipe_sha, overlay_sha):
    need(not out.exists(), 'fresh output required')
    data = authenticate(recipe, overlay, recipe_sha, overlay_sha)
    pending = main_files(root, data['entries'])
    overlay_files(overlay, data['entries'], pending)
    out.mkdir(parents=True)
    for name, body in pending.items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    (out / 'BUNDLE-MANIFEST.json').write_text(
        json.dumps(data['original_bundle_manifest'], sort_keys=True, indent=2) + '\n')
    return {'status': 'PASS_EXACT_GITFREE_MATERIALIZATION', 'entries': len(pending),
            'recipe_sha256': recipe_sha, 'overlay_sha256': overlay_sha}
