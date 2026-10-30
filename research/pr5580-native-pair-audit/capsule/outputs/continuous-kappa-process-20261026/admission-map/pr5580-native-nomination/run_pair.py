#!/usr/bin/env python3
"""Root-only one serial normal/-O pair via the existing shared resource guard."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

B = Path(__file__).resolve().parent
ROOT = B.parents[3]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def main():
    raw = (B/'REQUEST.json').read_bytes()
    request = json.loads(raw)
    need(request['schema'] == 'single-native-interface-request/v1' and request['freeze_status'] == 'FROZEN_FOR_ROOT_REVIEW',
         'request frozen only after current source gate')
    need(request['modes'] == ['normal','optimized'] and request['total_seconds'] == 150 and
         request['per_child_seconds'] == 60 and request['memory_mib'] == 512, 'fixed resource contract')
    for path,digest in request['files'].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, 'frozen request '+path)
    outputs = ['RESULT-normal.json','RESULT-optimized.json','STDERR-normal.txt','STDERR-optimized.txt','PAIR-RECEIPT.json']
    need(not any((B/path).exists() for path in outputs), 'preserve previous attempt; no overwrite/rerun')
    for mode,flags in [('normal',[]),('optimized',['-O'])]:
        with (B/('RESULT-'+mode+'.json')).open('xb') as out,(B/('STDERR-'+mode+'.txt')).open('xb') as err:
            run = subprocess.run([sys.executable,*flags,'-B',str(B/'check.py')],cwd=ROOT,stdout=out,stderr=err,timeout=60)
        need(run.returncode == 0 and (B/('STDERR-'+mode+'.txt')).stat().st_size == 0, mode+' failed; preserve evidence')
        result = json.loads((B/('RESULT-'+mode+'.json')).read_bytes())
        need(result['status'] == 'PASS_PR5580_SINGLE_NATIVE_PAIR' and result['new_kappa'] is None, 'one scoped native result')
    left,right = [(B/('RESULT-'+mode+'.json')).read_bytes() for mode in ('normal','optimized')]
    need(left == right, 'all scientific output bytes agree normal/-O')
    receipt = {'schema':'exact-pair-equality/v2','complete_output_equal':True,'scientific_fields_excluded':0,
               'modes':2,'result_sha256':hashlib.sha256(left).hexdigest(),'request_sha256':hashlib.sha256(raw).hexdigest(),
               'scope':'One PR5580 source-bound native pair; no complete source/caller/funding or new kappa.'}
    with (B/'PAIR-RECEIPT.json').open('x') as out:
        out.write(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True,separators=(',',':')))


if __name__ == '__main__':
    main()
