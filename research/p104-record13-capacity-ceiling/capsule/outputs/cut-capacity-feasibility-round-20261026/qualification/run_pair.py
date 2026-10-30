#!/usr/bin/env python3
"""Root-only one-attempt serial normal/-O pair, under the unchanged guard."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def main():
    raw = (HERE/'REQUEST.json').read_bytes(); request = json.loads(raw)
    need(request['schema']=='one-pre13-cut-capacity-request/v1','request schema')
    need(request['modes']==['normal','optimized'] and request['total_seconds']==150 and
         request['memory_mib']==512 and request['per_child_seconds']==60,'fixed resources')
    for path,expected in request['files'].items():
        need(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,'request byte '+path)
    names = ['RESULT-normal.json','RESULT-optimized.json','STDERR-normal.txt','STDERR-optimized.txt','PAIR-RECEIPT.json']
    need(not any((HERE/name).exists() for name in names),'attempt already exists; no automatic retry')
    accepted = {'PREMISE_FAILURE_STOP_THIS_EXACT_OBJECT','NO_ADDITIONAL_RESTRICTED_CHANNEL_STOP_THIS_OBJECT',
                'CONDITIONAL_ALGEBRAIC_EXTRA_CHANNEL_ONLY'}
    for mode,flags in [('normal',[]),('optimized',['-O'])]:
        with tempfile.TemporaryDirectory(prefix='onecut-bytecode-') as cache:
            with (HERE/('RESULT-'+mode+'.json')).open('xb') as out,(HERE/('STDERR-'+mode+'.txt')).open('xb') as err:
                try:
                    child = subprocess.run([sys.executable,'-I','-X','pycache_prefix='+cache,*flags,'-B',str(HERE/'check.py')],
                                           cwd=ROOT,stdout=out,stderr=err,timeout=60)
                except subprocess.TimeoutExpired:
                    with (HERE/'PAIR-RECEIPT.json').open('x') as report:
                        report.write(json.dumps({'status':'INCONCLUSIVE_RESOURCE_LIMIT_STOP','mode':mode,
                            'request_sha256':hashlib.sha256(raw).hexdigest(),'no_retry':True},sort_keys=True)+'\n')
                    raise SystemExit(3)
        need(child.returncode==0 and (HERE/('STDERR-'+mode+'.txt')).stat().st_size==0,'input/parser/resource/certificate failure '+mode)
        result = json.loads((HERE/('RESULT-'+mode+'.json')).read_bytes())
        need(result['status'] in accepted,'unexpected outcome')
    left,right = [(HERE/('RESULT-'+mode+'.json')).read_bytes() for mode in ('normal','optimized')]
    need(left==right,'complete normal/-O result bytes differ')
    result = json.loads(left)
    receipt = {'schema':'one-pre13-cut-exact-pair/v1','status':result['status'],'complete_output_equal':True,
               'scientific_fields_excluded':0,'request_sha256':hashlib.sha256(raw).hexdigest(),
               'result_sha256':hashlib.sha256(left).hexdigest(),'physical_witness':False,'new_kappa':None}
    with (HERE/'PAIR-RECEIPT.json').open('x') as stream:
        stream.write(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True,separators=(',',':')))


if __name__=='__main__':
    main()
