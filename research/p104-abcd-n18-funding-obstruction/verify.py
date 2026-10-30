#!/usr/bin/env python3
"""Portable replay of the byte-preserved scoped n18 ABCD funding certificate.

Chris R/Clear1nsight with substantial OpenAI Codex assistance; Apache-2.0.
The retained source and interval engine keep their predecessor credit.
"""
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
AUDIT='outputs/continuous-kappa-process-20261026/funding-plane-qualification'
REQUEST_SHA='affa58572a019b90640961b57c2f93934ca3dc623192565f44892b635e62c5ce'
RESULT_SHA='b6c70c4779a0e1648a965a15143af337fb78be0a82893e66eb9012e457cee036'


def need(ok,message):
    if not ok:raise ValueError(message)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def regular(root,name):
    p=Path(name)
    need(not p.is_absolute() and p.as_posix()==name and '..' not in p.parts,'canonical relative path '+name)
    current=root
    for part in p.parts:
        current=current/part;need(not current.is_symlink(),'symlink '+name)
    need(current.is_file(),'regular file '+name)
    return current


def semantic(r):
    need(r['status']=='PASS_SCOPED_N18_ABCD_NECESSARY_FUNDING_OBSTRUCTION' and
         r['reviewed_head']=='6efa248cf456d6101d757e9d09ba29711d18a13a' and
         r['new_kappa'] is None and r['physical_witness'] is False,'exact original scope/source')
    need(not r['all_n_funding_claim'] and not r['n17_funding_claim'] and
         not r['compiler_universal_claim'] and not r['selected_promotion'] and
         not r['source_gamma_author_interval_used_as_proof'],'preserved claim boundaries')
    need(r['source_C0']=='6163781/2000000000' and
         Q(r['source_gamma_independent_interval'][0])>Q(193,200),'independent source gamma lower bound')
    law=r['retained_compiler_guard_binding']
    need(law['gamma']=='M_P(1-C+1/5)/(17^(1/5)*M_T(1-C))' and
         law['delta']=='18*|T|/(17^C*M_T(1-C))' and not law['source_modules_executed'],
         'literal retained compiler guard applicability')
    need([p['C'] for p in r['points']]==['33/10000','6600001/2000000000'],'exact two-point domain')
    for p in r['points']:
        need(Q(p['necessary_tail_increment_per_FULL_strict_lower'])>Q(p['available_tail_increment_per_FULL_strict_upper']) and
             p['six_rank_dual_lower_slacks']['1']==p['six_rank_dual_lower_slacks']['2']=='0' and
             all(Q(p['six_rank_dual_lower_slacks'][str(k)])>0 for k in range(3,7)),
             'strict all-profile Farkas separation and all six coefficient slacks')
    controls=r['mutation_controls']
    need(len(controls)==27 and sum(c['outcome']=='rejected' for c in controls.values())==25 and
         sum(c['outcome']=='inconclusive_as_required' for c in controls.values())==2,
         'all 27 classified controls, including two inconclusive sensitivities')
    need(r['fifth_root_extension']['maximum_rank']==145 and r['fifth_root_extension']['negative_C_calls']==0,
         'bounded finite fifth-root extension and positive-C engine reuse')


def authenticate():
    inventory=json.loads((HERE/'PAYLOAD-INVENTORY.json').read_bytes())['files']
    actual=set()
    for path in HERE.rglob('*'):
        need(not path.is_symlink(),'symlink package member')
        if path.is_file() and path!=HERE/'PAYLOAD-INVENTORY.json':actual.add(path.relative_to(HERE).as_posix())
    need(actual==set(inventory),'complete package inventory')
    for name,row in inventory.items():
        raw=regular(HERE,name).read_bytes()
        need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'frozen package byte '+name)
    capsule=HERE/'capsule';raw=regular(capsule,AUDIT+'/REQUEST.json').read_bytes()
    need(sha(raw)==REQUEST_SHA,'original frozen request')
    request=json.loads(raw)
    need(request['caller']==18 and request['cutoff']==17 and request['floor']==18 and
         request['tail_offset']=='1/5' and request['decay']=='97/100' and
         request['goals']==['33/10000','6600001/2000000000'] and request['expected_controls']==27,
         'original caller/tail/domain contract')
    for name,digest in request['files'].items():need(sha(regular(capsule,name).read_bytes())==digest,'original frozen input '+name)
    expected=regular(HERE,'original-evidence/RESULT-normal.json').read_bytes()
    need(sha(expected)==RESULT_SHA and regular(HERE,'original-evidence/RESULT-optimized.json').read_bytes()==expected,
         'both original complete scientific output bytes')
    pair=json.loads(regular(HERE,'original-evidence/PAIR-RECEIPT.json').read_bytes())
    need(pair['request_sha256']==REQUEST_SHA and pair['result_sha256']==RESULT_SHA and
         pair['complete_output_equal'] and pair['scientific_fields_excluded']==0,'original exact pair joins')
    need(not regular(HERE,'original-evidence/STDERR-normal.txt').read_bytes() and
         not regular(HERE,'original-evidence/STDERR-optimized.txt').read_bytes(),'original empty stderr')
    semantic(json.loads(expected))
    return expected


def child_limits():resource.setrlimit(resource.RLIMIT_AS,(512*1024*1024,512*1024*1024))


def main():
    expected=authenticate()
    if sys.argv[1:]==['--integrity-only']:
        print('PASS_P104_ABCD_FUNDING_INTEGRITY_ONLY_NO_SCIENCE');return
    need(not sys.argv[1:],'unsupported verifier arguments')
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONOPTIMIZE',None)
    with tempfile.TemporaryDirectory(prefix='p104-abcd-funding-') as temp:
        command=[sys.executable,'-I','-X','pycache_prefix='+temp+'/bytecode']
        command+=['-O'] if sys.flags.optimize else []
        command+=['-B',str(HERE/'capsule'/AUDIT/'check.py')]
        with (Path(temp)/'stdout.json').open('wb+') as out,(Path(temp)/'stderr.txt').open('wb+') as err:
            child=subprocess.run(command,cwd=HERE/'capsule',env=env,stdout=out,stderr=err,timeout=60,preexec_fn=child_limits)
            out.seek(0);actual=out.read();err.seek(0);errors=err.read()
        need(child.returncode==0 and not errors,'scientific child failed: '+errors.decode(errors='replace')[:3000])
        need(actual==expected,'complete original scientific output equality')
    semantic(json.loads(actual));authenticate()
    print('PASS_P104_ABCD_N18_FUNDING_OBSTRUCTION')
    print(json.dumps({'complete_original_output_sha256':sha(actual),'goals':['33/10000','6600001/2000000000'],
      'caller':18,'controls_rejected':25,'sensitivity_controls_inconclusive':2,'all_n_funding_claim':False,
      'new_kappa':None},sort_keys=True,separators=(',',':')))


if __name__=='__main__':main()
