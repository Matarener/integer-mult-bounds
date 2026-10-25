"""Read public canonical GitHub metadata into this new research scope."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
URLS = {
    'MAIN-COMMIT.json': 'https://api.github.com/repos/CrocSwap/integer-mult-bounds/commits/main',
    'OPEN-PULLS-P1.json': 'https://api.github.com/repos/CrocSwap/integer-mult-bounds/pulls?state=open&per_page=100&sort=updated&direction=desc',
    'DISCUSSION-1163.html': 'https://github.com/CrocSwap/integer-mult-bounds/discussions/1163',
    'DISCUSSIONS.html': 'https://github.com/CrocSwap/integer-mult-bounds/discussions',
}

def fetch(item):
    name, url = item
    req = urllib.request.Request(url, headers={
        'User-Agent': 'kappa-1745-research',
        'Accept': 'application/vnd.github+json' if 'api.github' in url else 'text/html',
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read()
        (HERE / 'sources' / name).write_bytes(raw)
        return dict(file=name, url=url, bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), status='saved')
    except Exception as error:
        return dict(file=name, url=url, status='error', error=str(error))

if __name__ == '__main__':
    (HERE / 'sources').mkdir(exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(fetch, URLS.items()))
    (HERE / 'sources' / 'REFRESH.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps(rows, indent=2))
