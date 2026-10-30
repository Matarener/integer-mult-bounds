"""Source-bound consumer verification for G20 controller query ranks.
Dennis / antunishdPursuit with OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from audit import audit, need
import test_audit


def load(root):
    out={}
    for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if row['usage']!='input':
            continue
        raw=(root/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA: '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
             'source blob: '+row['path'])
        out[row['path']]=raw
    return out


def reject(function):
    try:
        function()
    except ValueError:
        return
    raise ValueError('mutation survived')


def main():
    data=load(ROOT)
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_audit)
    tests=unittest.TextTestRunner(stream=io.StringIO()).run(suite)
    need(tests.wasSuccessful(),'self-contained controls')
    result={}
    for name,nesting in [('g20-conjugation-admission','prior/prior/prior/'),
                         ('g20-helper-split','prior/prior/')]:
        prefix='research/'+name+'/'
        c=json.loads(data[prefix+nesting+'source/vendor/g20/inputs/CONTROLLER.json'])
        inv=json.loads(data[prefix+'INVOICE.json'])
        records=[json.loads(line) for line in gzip.decompress(data[prefix+'GLOBAL.jsonl.gz']).splitlines()]
        result[name]=audit(c,records,inv['originals'],inv['owned_allocated'])
        index=next(i for i,e in enumerate(records) if e[0]=='QUERY' and e[3][0]=='WHOLE_IDLE')
        bad=records.copy();bad[index]=deepcopy(records[index]);bad[index][2]+=1
        reject(lambda:audit(c,bad,inv['originals'],inv['owned_allocated']))
    values=list(result.values());need(values[0]==values[1],'both candidate controller components agree')
    with tempfile.TemporaryDirectory() as directory:
        root=Path(directory)
        for path,raw in data.items():
            dest=root/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        path=next(p for p in data if p.endswith('CONTROLLER.json'))
        (root/path).write_bytes(data[path]+b' ')
        reject(lambda:load(root))
    result['controls']={'self_contained_tests':tests.testsRun,'semantic_mutations':17,
                        'live_wrong_rank_controls':2,'source_byte_controls':1}
    path=HERE/'RESULT.json'
    if sys.argv[1:]==['--write-result']:
        path.write_bytes((json.dumps(result,indent=2)+'\n').encode())
    else:
        need(not sys.argv[1:],'unexpected arguments')
        need(json.loads(path.read_text(encoding='utf-8'))==result,'fresh derivation equals committed result')
    print(json.dumps(result,sort_keys=True))
    print('PASS_G20_CONTROLLER_QUERY_RANKS')


if __name__=='__main__':
    main()
