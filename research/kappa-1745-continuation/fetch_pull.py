"""Retain exact public changed files for one explicitly selected research PR."""
import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath
import urllib.request

HERE = Path(__file__).resolve().parent
API = 'https://api.github.com/repos/CrocSwap/integer-mult-bounds'

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'kappa-1745-research'})
    with urllib.request.urlopen(req, timeout=40) as response:
        return response.read()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('number', type=int)
    args = parser.parse_args()
    if args.number <= 0:
        raise ValueError('positive public PR number')
    out = HERE/'sources'/('PR'+str(args.number))
    out.mkdir(parents=True, exist_ok=True)
    raw = get(API+'/pulls/'+str(args.number))
    meta = json.loads(raw)
    (out/'PULL.json').write_bytes(raw)
    files = []
    for page in range(1, 21):
        batch = json.loads(get(API+'/pulls/'+str(args.number)+'/files?per_page=100&page='+str(page)))
        files.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError('unexpectedly large research delta')
    (out/'FILES.json').write_text(json.dumps(files, indent=2)+'\n')
    head = meta['head']['sha']
    repository = meta['head']['repo']['full_name']
    def fetch(row):
        p = PurePosixPath(row['filename'])
        if p.is_absolute() or '..' in p.parts or not p.parts:
            raise ValueError('unsafe repository path')
        if row['status'] == 'removed':
            return dict(path=str(p), status='removed')
        url = 'https://raw.githubusercontent.com/'+repository+'/'+head+'/'+str(p)
        data = get(url)
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if blob != row['sha']:
            raise ValueError('Git blob mismatch: '+str(p))
        target = out.joinpath(*p.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        return dict(path=str(p), bytes=len(data), git_blob=blob, sha256=hashlib.sha256(data).hexdigest())
    with ThreadPoolExecutor(max_workers=6) as pool:
        retained = list(pool.map(fetch, files))
    receipt = dict(pull=args.number, head=head, repository=repository, files=retained)
    (out/'SOURCE.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(pull=args.number, head=head, files=len(retained), bytes=sum(r.get('bytes',0) for r in retained))))

if __name__ == '__main__':
    main()
