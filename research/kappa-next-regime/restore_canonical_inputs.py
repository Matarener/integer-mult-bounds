#!/usr/bin/env python3
"""Restore only absent, published hash-pinned T740 inputs from public main.

No verifier gate is changed. Existing bytes must match exactly. Public raw
bytes and their Git object identities are independently checked before write.
"""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha1,sha256
import json
from pathlib import Path
from urllib.request import Request,urlopen

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
HEAD='20ecf2891d80b5acf18d980b2164fb44ea7faa90'
PACKAGE='research/coupled-carrier-cap740'


def fetch(url):
    with urlopen(Request(url,headers={'User-Agent':'kappa-next-regime-source-replay'}),timeout=45) as response:
        return response.read()


def main():
    p=ROOT/PACKAGE
    manifest=json.loads((p/'MANIFEST.json').read_text())
    declared=json.loads((p/'SOURCE-PINS.json').read_text())
    names=['evidence/PREFIX-AND-INVOICE.json.gz','vendor/PR3133-FILL.json.gz',
           'words/base.json.gz','words/extra.json.gz']
    planned={PACKAGE+'/'+n:manifest[n] for n in names}
    planned.update({n:h for n,h in declared.items() if n.endswith('/PLAN.json.gz') or n.endswith('/TEMPLATE.json.gz')})
    def one(item):
        name,pin=item
        path=ROOT/name
        if path.is_file():
            raw=path.read_bytes()
            if sha256(raw).hexdigest()!=pin:raise ValueError('existing declared input changed: '+name)
        else:
            raw=fetch('https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/'+HEAD+'/'+name)
        if sha256(raw).hexdigest()!=pin:raise ValueError('published SHA256 mismatch: '+name)
        meta=json.loads(fetch('https://api.github.com/repos/CrocSwap/integer-mult-bounds/contents/'+name+'?ref='+HEAD))
        blob=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if meta['sha']!=blob:raise ValueError('public Git object mismatch: '+name)
        path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():path.write_bytes(raw)
        return {'path':name,'bytes':len(raw),'sha256':pin,'git_blob':blob,'head':HEAD}
    with ThreadPoolExecutor(max_workers=4) as pool:
        rows=list(pool.map(one,planned.items()))
    report={'status':'PASS_EXACT_PUBLIC_T740_DEPENDENCIES_RESTORED','files':rows}
    (HERE/'sources/RESTORED-T740-INPUTS.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
