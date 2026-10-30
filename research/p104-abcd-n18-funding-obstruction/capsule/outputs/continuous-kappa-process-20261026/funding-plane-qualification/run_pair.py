#!/usr/bin/env python3
"""One root-only frozen normal/-O n18 funding-plane qualification pair."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

B=Path(__file__).resolve().parent
ROOT=B.parents[2]


def need(condition,message):
    if not condition:raise ValueError(message)


def main():
    raw_request=(B/'REQUEST.json').read_bytes();request=json.loads(raw_request)
    need(request['schema']=='bounded-n18-funding-plane-qualification/v1','request schema')
    need(request['modes']==['normal','optimized'] and request['total_seconds']==150 and
         request['memory_mib']==512 and request['per_child_seconds']==60,'frozen serial resource contract')
    for name,expected in request['files'].items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==expected,'frozen request byte '+name)
    names=['RESULT-normal.json','RESULT-optimized.json','STDERR-normal.txt','STDERR-optimized.txt','PAIR-RECEIPT.json']
    need(not any((B/name).exists() for name in names),'preserve existing attempted pair; no automatic rerun')
    for mode,flags in [('normal',[]),('optimized',['-O'])]:
        with tempfile.TemporaryDirectory(prefix='funding-plane-bytecode-') as cache:
            with (B/('RESULT-'+mode+'.json')).open('xb') as out,(B/('STDERR-'+mode+'.txt')).open('xb') as err:
                child=subprocess.run([sys.executable,'-I','-X','pycache_prefix='+cache,*flags,'-B',str(B/'check.py')],
                    cwd=ROOT,stdout=out,stderr=err,timeout=60)
        need(child.returncode==0 and (B/('STDERR-'+mode+'.txt')).stat().st_size==0,'mode failed '+mode)
        result=json.loads((B/('RESULT-'+mode+'.json')).read_bytes())
        need(result['status']=='PASS_SCOPED_N18_ABCD_NECESSARY_FUNDING_OBSTRUCTION','scientific marker '+mode)
        controls=result['mutation_controls']
        need(len(controls)==27 and all(v['outcome'] in ('rejected','inconclusive_as_required') for v in controls.values()) and
             sum(v['outcome']=='inconclusive_as_required' for v in controls.values())==2,'27 classified controls '+mode)
    left,right=((B/('RESULT-'+mode+'.json')).read_bytes() for mode in ('normal','optimized'))
    need(left==right,'complete scientific normal/-O bytes differ')
    receipt={'schema':'exact-pair-equality/v2','modes':2,'complete_output_equal':True,'scientific_fields_excluded':0,
      'result_sha256':hashlib.sha256(left).hexdigest(),'request_sha256':hashlib.sha256(raw_request).hexdigest(),
      'scope':'Finite necessary funding obstruction for all nonnegative real invariant ABCD profiles at original n18 and two fixed points, retained cutoff17/floor18/tau1/5/.97 only. No physical contacts or new kappa.'}
    with (B/'PAIR-RECEIPT.json').open('x') as stream:stream.write(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True,separators=(',',':')))


if __name__=='__main__':main()
