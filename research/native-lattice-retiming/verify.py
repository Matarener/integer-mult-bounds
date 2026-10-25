"""Exact replay of a changed native profile and its conditional full consumer.
Standard library only. Apache-2.0, substantial OpenAI Codex assistance.
"""
import argparse
from hashlib import sha1,sha256
import json
from pathlib import Path
import native
import arithmetic

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
need=native.need

def authenticate():
    seen=set()
    for row in native.read(HERE/'SOURCES.json')['files']:
        if row['usage']!='input':continue
        p=Path(row['path'])
        need(not p.is_absolute() and '..' not in p.parts and str(p) not in seen,'Canonical unique source')
        seen.add(str(p));actual=ROOT
        for part in p.parts:actual/=part;need(not actual.is_symlink(),'No source aliases')
        b=actual.read_bytes()
        need(sha256(b).hexdigest()==row['sha256'],'Changed source: '+str(p))
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'Changed source blob: '+str(p))
    return len(seen)

def run(write=False):
    count=authenticate()
    local=native.run()
    result=arithmetic.run(local)
    for name,value in [('NATIVE-RESULT.json',local),('RESULT.json',result)]:
        normalized=json.loads(json.dumps(value))
        if write:(HERE/name).write_text(json.dumps(normalized,sort_keys=True,indent=2)+'\n')
        else:need(normalized==native.read(HERE/name),'Exact regenerated receipt: '+name)
    return dict(status=result['status'],kappa_decimal=result['kappa_decimal'],sources=count,
                uniform_rank=result['compiler']['N'],same_kappa_uniform_rank=result['same_predecessor_kappa_compiler']['N'],
                outer_predicates='54 + 4 current, 63 legacy; nine rows agree')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write-receipts',action='store_true');a=p.parse_args()
    print(json.dumps(run(a.write_receipts),sort_keys=True))
