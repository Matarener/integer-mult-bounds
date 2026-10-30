#!/usr/bin/env python3
"""Pin public canonical guidance and a bounded current-overlap snapshot.

Adapted from kappa-1745-continuation/refresh_sources.py. No authenticated
account, Library read, or remote write is used. Apache-2.0.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
API = 'https://api.github.com/repos/CrocSwap/integer-mult-bounds'


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'kappa-operator-repair-research'})
    with urllib.request.urlopen(req, timeout=40) as response:
        return response.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--checkpoint', default='initial')
    args = ap.parse_args()
    if not args.checkpoint.replace('-', '').isalnum():
        raise ValueError('simple checkpoint label required')
    out = HERE / 'sources' / args.checkpoint
    out.mkdir(parents=True, exist_ok=False)
    urls = {
        'MAIN-COMMIT.json': API + '/commits/main',
        'OPEN-PULLS-P1.json': API + '/pulls?state=open&per_page=100&sort=updated&direction=desc',
        'DISCUSSION-1163.html': 'https://github.com/CrocSwap/integer-mult-bounds/discussions/1163',
        'DISCUSSION-1166.html': 'https://github.com/CrocSwap/integer-mult-bounds/discussions/1166',
        'DISCUSSIONS.html': 'https://github.com/CrocSwap/integer-mult-bounds/discussions',
    }

    def fetch(item):
        name, url = item
        try:
            raw = get(url)
            p = out / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(raw)
            return {'file': name, 'url': url, 'bytes': len(raw),
                    'sha256': hashlib.sha256(raw).hexdigest(), 'status': 'saved'}
        except Exception as exc:
            return {'file': name, 'url': url, 'status': 'error', 'error': str(exc)}

    started = datetime.now(timezone.utc).isoformat()
    with ThreadPoolExecutor(max_workers=5) as pool:
        rows = list(pool.map(fetch, urls.items()))
    main_file = out / 'MAIN-COMMIT.json'
    head = json.loads(main_file.read_bytes())['sha'] if main_file.exists() else None
    guidance = ['AGENTS.md', 'autoresearch.md', 'CONTRIBUTING.md',
                'docs/research/current-priorities.md', 'docs/research/research-family-status.md',
                'docs/research/agent-task-catalog.json', 'certificates/selected-result.json']
    if head:
        with ThreadPoolExecutor(max_workers=5) as pool:
            rows += list(pool.map(fetch, [('main/' + p,
                'https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/' + head + '/' + p)
                for p in guidance]))
    report = {'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'canonical_main': head, 'coverage': 'Guidance, start-here, handoffs, discussion index, 100 most recently updated open PRs; not a complete overlap or novelty census.',
              'requests': rows}
    (out / 'REFRESH.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'canonical_main': head, 'saved': sum(r['status'] == 'saved' for r in rows),
                      'errors': [r for r in rows if r['status'] != 'saved'], 'output': str(out)}))


if __name__ == '__main__':
    main()
