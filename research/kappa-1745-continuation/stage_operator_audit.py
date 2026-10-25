"""Stage pinned PR4046 and its exact canonical dependencies in an isolated tree."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = HERE/'sources/PR4046'
DEST = HERE/'operator-audit/checkout'
MAIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
PACKAGE = 'research/pr3934-pr3955-operator-replay'

def need(value, message):
    if not value:
        raise ValueError(message)

def main():
    rows = json.loads((SOURCE/'SOURCE.json').read_text())['files']
    rows += json.loads((SOURCE/PACKAGE/'SOURCES.json').read_text())['files']
    unique = {}
    for row in rows:
        p = PurePosixPath(row['path'])
        need(not p.is_absolute() and '..' not in p.parts, 'relative repository input')
        if str(p) in unique:
            need(unique[str(p)]['sha256'] == row['sha256'], 'consistent source pins')
        unique[str(p)] = row
    kept = []
    for name, row in sorted(unique.items()):
        candidate = SOURCE/name if (SOURCE/name).is_file() else ROOT/name
        if candidate.is_file():
            raw = candidate.read_bytes()
            origin = 'retained_pr' if candidate.is_relative_to(SOURCE) else 'canonical_workspace'
        elif name.endswith('/BASE-FILL.json.gz'):
            candidate = ROOT/'research/coupled-carrier-cap740/vendor/PR3133-FILL.json.gz'
            raw = candidate.read_bytes()
            origin = 'identical_retained_PR3133_fill'
        else:
            url = 'https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/'+MAIN+'/'+name
            req = urllib.request.Request(url, headers={'User-Agent':'kappa-1745-research'})
            with urllib.request.urlopen(req, timeout=40) as response:
                raw = response.read()
            origin = 'public_canonical_commit'
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'exact source bytes: '+name)
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        need(blob == row['git_blob'], 'exact Git blob: '+name)
        target = DEST/name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        kept.append(dict(path=name, sha256=row['sha256'], git_blob=blob, bytes=len(raw), origin=origin))
    receipt = dict(status='PASS_EXACT_OPERATOR_AUDIT_STAGE', canonical_main=MAIN, files=kept)
    (HERE/'operator-audit/STAGE.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(status=receipt['status'],files=len(kept),bytes=sum(r['bytes'] for r in kept))))

if __name__ == '__main__':
    main()
