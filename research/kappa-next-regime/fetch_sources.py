#!/usr/bin/env python3
"""Retain public GitHub PR bytes, checking raw downloads against Git blob IDs.

Source acquisition only; this does not validate any mathematical claim.
Prepared with substantial OpenAI assistance for the user-directed continuation.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
API = 'https://api.github.com/repos/CrocSwap/integer-mult-bounds'


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'kappa-research-source-reader',
        'Accept': 'application/vnd.github+json',
    })
    with urllib.request.urlopen(req, timeout=45) as response:
        return response.read()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('prs', type=int, nargs='+')
    parser.add_argument('--metadata-only', action='store_true')
    args = parser.parse_args()
    dst = HERE / 'sources'
    dst.mkdir(parents=True, exist_ok=True)
    for number in args.prs:
        meta_path = dst / f'PR{number}.json'
        if not meta_path.exists():
            meta_path.write_bytes(fetch(f'{API}/pulls/{number}'))
        meta = json.loads(meta_path.read_bytes())
        rows = []
        page = 1
        while True:
            suffix = '' if page == 1 else f'-P{page}'
            path = dst / f'PR{number}-FILES{suffix}.json'
            if not path.exists():
                path.write_bytes(fetch(f'{API}/pulls/{number}/files?per_page=100&page={page}'))
            batch = json.loads(path.read_bytes())
            rows.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        head = meta['head']['sha']
        print(json.dumps({'pr': number, 'head': head, 'title': meta['title'],
                          'files': len(rows), 'changed_files_reported': meta['changed_files']}), flush=True)
        if len(rows) != meta['changed_files']:
            raise RuntimeError(f'Incomplete PR file listing for {number}')
        if args.metadata_only:
            continue
        root = dst / f'PR{number}'

        def download(row):
            if row['status'] == 'removed':
                return None
            rel = Path(row['filename'])
            if rel.is_absolute() or '..' in rel.parts:
                raise RuntimeError('Unsafe source path')
            path = root / rel
            url = f"https://raw.githubusercontent.com/{meta['head']['repo']['full_name']}/{head}/{row['filename']}"
            raw = path.read_bytes() if path.exists() else fetch(url)
            git_blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            if git_blob != row['sha']:
                raise RuntimeError(f'Git blob mismatch: {number} {rel}')
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
            return {'path': rel.as_posix(), 'git_blob': git_blob,
                    'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw), 'url': url}

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
            manifest = [r for r in pool.map(download, rows) if r is not None]
        receipt = {'status': 'PASS_EXACT_PUBLIC_SOURCE_ACQUISITION', 'pr': number,
                   'head': head, 'head_repository': meta['head']['repo']['full_name'],
                   'files': manifest}
        (dst / f'PR{number}-PINS.json').write_text(json.dumps(receipt, indent=2) + '\n')
        print(json.dumps({'pr': number, 'retained': len(manifest),
                          'bytes': sum(r['bytes'] for r in manifest)}), flush=True)


if __name__ == '__main__':
    main()
