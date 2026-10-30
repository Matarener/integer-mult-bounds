#!/usr/bin/env python3
"""Frozen sequential normal/-O certificate pair; invoke only via existing guard."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

B = Path(__file__).resolve().parent
ROOT = B.parents[2]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    raw_request = (B/'REQUEST.json').read_bytes()
    request = json.loads(raw_request)
    need(request['schema'] == 'bounded-pooled-abc-ceiling-qualification/v1', 'request schema')
    need(request['modes'] == ['normal','optimized'] and request['total_seconds'] == 150 and
         request['memory_mib'] == 512 and request['per_child_seconds'] == 60,
         'frozen serial resource contract')
    for path, expected in request['files'].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, 'frozen request mismatch '+path)
    outputs = ['RESULT-normal.json','RESULT-optimized.json','STDERR-normal.txt',
               'STDERR-optimized.txt','PAIR-RECEIPT.json']
    need(not any((B/name).exists() for name in outputs), 'preserve previous attempted pair; stop instead of rerun')
    for mode, flags in [('normal',[]),('optimized',['-O'])]:
        with (B/('RESULT-'+mode+'.json')).open('xb') as out, (B/('STDERR-'+mode+'.txt')).open('xb') as err:
            run = subprocess.run([sys.executable,*flags,'-B',str(B/'check.py')],
                                 stdout=out,stderr=err,cwd=ROOT,timeout=60)
        need(run.returncode == 0, mode+' failed; preserve outputs')
        need((B/('STDERR-'+mode+'.txt')).stat().st_size == 0, mode+' emitted stderr')
        result = json.loads((B/('RESULT-'+mode+'.json')).read_bytes())
        need(result['status'] == 'PASS_SCOPED_POOLED_ABC_COEFFICIENT_CERTIFICATE', 'missing scientific marker')
    left,right = ((B/('RESULT-'+mode+'.json')).read_bytes() for mode in ('normal','optimized'))
    need(left == right, 'complete scientific normal/-O bytes differ')
    receipt = {'schema':'exact-pair-equality/v2','complete_output_equal':True,
               'scientific_fields_excluded':0,'modes':2,
               'result_sha256':hashlib.sha256(left).hexdigest(),
               'request_sha256':hashlib.sha256(raw_request).hexdigest(),
               'scope':'Finite rational coefficient qualification only; inherited baseline interval and paper analytic implications; no physical witness or new kappa.'}
    with (B/'PAIR-RECEIPT.json').open('x') as stream:
        stream.write(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True,separators=(',',':')))


if __name__ == '__main__':
    main()
