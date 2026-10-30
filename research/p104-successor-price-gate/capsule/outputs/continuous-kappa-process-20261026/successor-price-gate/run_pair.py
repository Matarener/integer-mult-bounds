#!/usr/bin/env python3
"""One frozen sequential normal/-O exact gate pair, only under root's guard."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

B = Path(__file__).resolve().parent
ROOT = B.parents[2]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    raw_request = (B/'REQUEST.json').read_bytes()
    request = json.loads(raw_request)
    need(request['schema'] == 'bounded-successor-price-gate/v1', 'request schema')
    need(request['modes'] == ['normal','optimized'] and request['total_seconds'] == 150
         and request['memory_mib'] == 512 and request['per_child_seconds'] == 60,
         'frozen serial resource limits')
    for relative, expected in request['files'].items():
        need(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == expected,
             'frozen file mismatch '+relative)
    names=['RESULT-normal.json','RESULT-optimized.json','STDERR-normal.txt',
           'STDERR-optimized.txt','PAIR-RECEIPT.json']
    need(not any((B/name).exists() for name in names), 'preserve attempted pair; no automatic rerun')
    for mode, flags in [('normal',[]),('optimized',['-O'])]:
        with (B/('RESULT-'+mode+'.json')).open('xb') as out, (B/('STDERR-'+mode+'.txt')).open('xb') as err:
            child=subprocess.run([sys.executable,*flags,'-B',str(B/'check.py')],
                                 stdout=out,stderr=err,cwd=ROOT,timeout=60)
        need(child.returncode == 0, mode+' failed; retain outputs')
        need((B/('STDERR-'+mode+'.txt')).stat().st_size == 0, mode+' emitted stderr')
        result=json.loads((B/('RESULT-'+mode+'.json')).read_bytes())
        need(result['status'] == 'PASS_SCOPED_EXACT_ECONOMIC_GATE', 'scientific gate marker')
    left,right=((B/('RESULT-'+mode+'.json')).read_bytes() for mode in ('normal','optimized'))
    need(left == right, 'complete scientific normal/-O outputs differ')
    receipt={'schema':'exact-pair-equality/v2','complete_output_equal':True,
             'scientific_fields_excluded':0,'modes':2,
             'request_sha256':hashlib.sha256(raw_request).hexdigest(),
             'result_sha256':hashlib.sha256(left).hexdigest(),
             'scope':'Exact two-point price gate, source bill census and paper all-n argument only; no construction or funded kappa.'}
    with (B/'PAIR-RECEIPT.json').open('x') as stream:
        stream.write(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True,separators=(',',':')))


if __name__ == '__main__':
    main()
