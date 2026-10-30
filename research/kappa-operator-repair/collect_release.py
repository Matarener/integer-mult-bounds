#!/usr/bin/env python3
"""Retain source-bound current release evidence without bulky runtime clones.

All scientific source/package bytes are inventoried. Current concise proof
receipts and all top-level execution logs are retained. Reconstructed owner
tables, ancestral clones and installed dependencies remain reproducible from
the authenticated archive, words, adapters and dependency wheels.
Apache-2.0. Substantial OpenAI assistance.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import shutil

HERE=Path(__file__).resolve().parent

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda:f.read(4*1024*1024),b''):
            h.update(data)
    return h.hexdigest()

def read(p):
    return json.loads(p.read_text())

def need(ok,why):
    if not ok:
        raise ValueError(why)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--work',type=Path,default=HERE/'composed-supplier/release-work')
    ap.add_argument('--out',type=Path,default=HERE/'evidence/full-release')
    a=ap.parse_args()
    need(__debug__,'Assertions enabled')
    work=a.work.resolve();out=a.out.resolve()
    need(not out.exists(),'Fresh evidence collection directory')
    result=read(work/'RESULT.json');admit=read(work/'admission/RESULT.json')
    release=read(work/'admission/release/RELEASE-RECEIPT.json')
    need(result['status']=='PASS_TERMINAL_RECEIVER_COMPLETE_CONDITIONAL_RELEASE','Completed current release runner')
    need(admit['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and release['status']=='PASS_RELEASE','Both inherited release gates')
    expected=Q('.001730824595303184580890')-Q(1,10**46)-Q(1,10**70)
    need(Q(result['kappa_rational'])==Q(admit['kappa'])==Q(release['kappa_decimal'])==expected,'Exact final conditional kappa')
    need(sha(work/'admission/RESULT.json')==result['release_result_sha256'],'Admission result binding')
    need(sha(work/'admission/release/RELEASE-RECEIPT.json')==result['release_receipt_sha256'],'Release receipt binding')
    need(sha(HERE/'composed-supplier/run_release.py')==result['runner_sha256'],'Actual unchanged executed runner')
    need(sha(work/'inputs/source/MANIFEST.json')==result['source_manifest_sha256'],'Original scientific source manifest')
    need(sha(work/'admission/package/MANIFEST.json')==admit['package_manifest_sha256']==release['manifest_sha256'],'Final admitted package manifest')
    for prefix,data in [('',result),('admission/',admit)]:
        need(read(work/(prefix+'STAGES.json'))==data['stages'],'Complete stage receipt')
        for stage in data['stages']:
            need(stage['exit_code']==0 and sha(work/(prefix+stage['name']+'.log'))==stage['log_sha256'],
                 'Executed stage/log binding '+stage['name'])
    exact={
        'RESULT.json','STAGES.json','PREPARED.json','ADAPTER.json','COMPOSED-ADMISSION-ADAPTER.json',
        'SOURCE-ADAPTATION.json','NATIVE-RECEIPT.json','ACTUAL-NATIVE-SOURCES.json','DEPENDENCIES.json',
        'admit_terminal.py','admit_composed.py','inputs/source/MANIFEST.json',
        'inputs/source/new/borrow/receiver_share.py','inputs/source/new/borrow/review_receiver_share.py',
        'inputs/source/new/borrow/terminal_review.py','inputs/source/outer/check_ledger.py',
        'inputs/source/outer/independent_check.py',
        'admission/RESULT.json','admission/STAGES.json','admission/package/MANIFEST.json',
        'admission/package/CLAIM.json','admission/package/new/SPEC.json',
        'admission/release/RELEASE-RECEIPT.json','admission/release/verify/RESULT.json',
        'admission/release/verify/strict/ASSEMBLY.json',
    }
    out.mkdir(parents=True)
    indexed,retained={},{}
    excluded_parts={'hosted','source','data','new-data','rebuilt-parent','rebuilt-owners','native-cache',
                    'parent','layout','vendor','python-deps'}
    for p in sorted(work.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.suffix=='.pyc' or 'python-deps' in p.relative_to(work).parts:
            continue
        rel=p.relative_to(work);name=rel.as_posix();size=p.stat().st_size
        indexed[name]=dict(bytes=size,sha256=sha(p))
        top_log=p.suffix=='.log' and len(rel.parts)<=2
        concise=(name.startswith(('admission/discovery/','admission/release/'))
                 and not (set(rel.parts)&excluded_parts)
                 and p.suffix in ('.json','.log','.jsonl') and size<=2*1024*1024)
        outer=(name.startswith('admission/package/outer/') and p.name in
               ('B.json','LEDGER.json','INDEPENDENT.json','OUTER-CLAIM.json','check_ledger.py','independent_check.py','run_outer.py'))
        if name in exact or top_log or concise or outer:
            dest=out/rel;dest.parent.mkdir(parents=True,exist_ok=True)
            dest.write_bytes(p.read_bytes())
            need(sha(dest)==indexed[name]['sha256'],'Exact retained bytes')
            retained[name]=indexed[name]
    need(exact<=set(retained),'All mandatory release receipts retained')
    for prefix in ('inputs/source/','admission/package/'):
        actual={p[len(prefix):]:v['sha256'] for p,v in indexed.items() if p.startswith(prefix) and p!=prefix+'MANIFEST.json'}
        need(actual==read(work/prefix/'MANIFEST.json'),'Every actual scientific source/package byte')
    runner=HERE/'composed-supplier/run_release.py'
    (out/'RUNNER-EXECUTED.py').write_bytes(runner.read_bytes())
    inventory=dict(status='PASS_CURRENT_RELEASE_EVIDENCE_COLLECTION',files=indexed,retained_files=retained,
                   executed_runner_sha256=sha(runner),collector_sha256=sha(Path(__file__)),
                   native_mode='Both native providers freshly executed this turn and authenticated by the release runner; full native outputs are retained in composed-supplier/native-base and native-extra.',
                   scope='Every non-bytecode scientific/runtime file except installed dependency trees is hashed. Current concise receipts and logs are retained; bulky generated owners, ancestral clones and dependencies are reproducible from pinned inputs.')
    (out/'FILE-INVENTORY.json').write_text(json.dumps(inventory,indent=2,sort_keys=True)+'\n')
    print(inventory['status'],len(indexed),'indexed',len(retained),'retained')

if __name__=='__main__':
    main()
