#!/usr/bin/env python3
"""Source-bound serial PR6030 audit. Douglas Colkitt / OpenAI Codex; Apache-2.0."""
import argparse,hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/'docs/research/pr-intake-evidence/pr6030-audit'
PRIMARY='research/p104-helper470-twin-rung-removal'
CONTROL='b51a7d19c10faea7d569a48e9536db8ba1e7418f8dd8dfb25646cc87cc9c4009'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def read(p):return json.loads(p.read_bytes())
def validate(work):
    inputs=read(AUDIT/'INPUTS.json')['files']
    changed='research/p104-caller-independent-audit/capsule/outputs/p104-caller-route-audit-v2-20261025/check.py'
    for name,digest in inputs.items():
        raw=(work/'source'/name).read_bytes()
        expected=hashlib.sha256((AUDIT/'caller-check.py').read_bytes()).hexdigest() if name==changed else digest
        need(hashlib.sha256(raw).hexdigest()==expected,'Changed export '+name)
    for name in ('run_caller.py','independent.py'):
        need((work/name).read_bytes()==(AUDIT/name).read_bytes(),'Changed audit script '+name)
    need((work/'run_bounded.py').read_bytes()==(ROOT/'docs/research/pr-intake-evidence/pr6030-repair/run_bounded.py').read_bytes(),'Changed watchdog')
    guards={}
    for name in ('primary','independent','control','candidate','optimized'):
        guard=read(work/'review-evidence'/f'{name}.json');raw=(work/'review-evidence'/f'{name}.log').read_bytes()
        need(guard['exit']==0 and guard['resource_stop'] is None,'Incomplete '+name)
        need(hashlib.sha256(raw).hexdigest()==guard['log_sha256'],'Changed log '+name)
        guards[name]=guard
    normal=(work/'review-evidence/primary.log').read_bytes()
    need(normal==(work/'review-evidence/optimized.log').read_bytes(),'Optimized scientific output changed')
    need(b'PASS_P104_BASE5907_EDIT_KAPPA_312580400\n' in normal,'Missing primary marker')
    need(guards['control']['log_sha256']==CONTROL,'Original caller positive control differs')
    candidate=read(work/'review-evidence/candidate.log');independent=read(work/'independent-result.json')
    result=read(work/'source'/PRIMARY/'RESULT.json');cost=result['complete_cost']
    need(candidate['status']=='PASS_SCOPED_CALLER_AND_TARGET_BINDING','Caller incomplete')
    need(independent['status']=='PASS_INDEPENDENT_6030_WORD_NATIVE_INVOICE_FUNDING','Independent checks incomplete')
    for name in ('paid','targets'):
        need(candidate[name]==cost[name]==independent[name],'Invoice mismatch '+name)
    need(candidate['native_checks']['fresh_helpers']==10116 and candidate['native_checks']['owned_peak']==13,'Caller inventory')
    need(len(candidate['field_maps'])==18 and all(len(x['local_to_global'])==770 and len(x['owned_lifetimes'])==29 for x in candidate['field_maps']),'Physical field maps')
    need(len(candidate['controls'])==10 and len(independent['new_native_maps'])==7,'Incomplete controls/native delta')
    need(candidate['ordinary']['abstract_address_phase_scalar_pass_upper']<=candidate['ordinary']['retained_raw_scalar_upper'],'Ordinary funding')
    report={'status':'PASS_SOURCE_BOUND_6030_INDEPENDENT_APPLICATION_REPLAYS','kappa':'0.003125804','guards':guards,'caller_summary':{k:candidate[k] for k in ('native_checks','ordinary','controls')},'independent':independent,'five_framework_assumptions_retained':True,'scope':'Finite/source-bound execution; the written application review is separate. No full uniform word, rounded multiplier or formal/human proof.'}
    (work/'VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
def main():
    need(not sys.flags.optimize,'Driver requires ordinary Python mode')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work',type=Path,required=True);p.add_argument('--validate-only',action='store_true');a=p.parse_args();work=a.work.resolve()
    if not a.validate_only:
        subprocess.run([sys.executable,'-I','-B',str(AUDIT/'prepare.py'),str(work)],check=True)
        env=dict(os.environ)
        for key in ('PYTHONPATH','PYTHONHOME','PYTHONOPTIMIZE','P104_WORD','P104_RESULT'):env.pop(key,None)
        runs=[('primary',['-I','source/'+PRIMARY+'/verify.py']),('independent',['-I','independent.py']),('control',['-I','run_caller.py','control']),('candidate',['-I','run_caller.py','candidate']),('optimized',['-I','-O','source/'+PRIMARY+'/verify.py'])]
        for name,args in runs:
            print('START '+name,flush=True)
            subprocess.run([sys.executable,'-I','-B',str(work/'run_bounded.py'),name,'600',*args],cwd=work,env=env,check=True)
    print(validate(work)['status'])
if __name__=='__main__':main()
