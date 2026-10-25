#!/usr/bin/env python3
"""Behavioral controls for the current-word transfer and complete invoice."""
from copy import deepcopy
from pathlib import Path
import json,os,shutil,subprocess,sys,tempfile
import verify as V
ROOT=Path(__file__).resolve().parent

def reject(fn,label):
 try:fn()
 except (ValueError,AssertionError):return
 raise ValueError('escaped control '+label)
def main():
 t,core,tariff,cone,sep=V.load_engines();w=V.word('base');records=[sep.certify_site(w,s) for s in sep.SITES];changed=V.contract(w,records,core)
 # Production positives guard against rejecting everything.
 V.check_receipt(changed,core,sep);V.forced_site_frames(w,records,t)
 wrong=deepcopy(w);wrong['B'][4][3]*=-1;reject(lambda:sep.certify_site(wrong,sep.SITES[1]),'wrong rational sign')
 dependent=deepcopy(w);dependent['B'][5][2]=518;reject(lambda:sep.certify_site(dependent,sep.SITES[1]),'hidden intervening read')
 crossed=deepcopy(w);crossed['warps'][0][0]=8;reject(lambda:sep.certify_site(crossed,sep.SITES[1]),'native cut')
 reject(lambda:V.contract(w,records+records[:1],core),'overlapping supports')
 stale=deepcopy(changed);stale['cleanup']=deepcopy(w['cleanup']);reject(lambda:V.check_receipt(stale,core,sep),'stale cleanup')
 missing=deepcopy(records);missing[1]['replacement']=missing[1]['replacement'][:1]
 reject(lambda:V.need(sep.matrix(records[1]['gates'],records[1]['support'])==sep.matrix(missing[1]['replacement'],records[1]['support']),'omitted replacement'),'omitted replacement')
 # Exercise the actual optimized CLI and its stored-receipt/source checks.
 for kind in ('owner-debit','source-byte'):
  with tempfile.TemporaryDirectory(prefix='combined-a2-control-') as tmp:
   dest=Path(tmp)/'package';shutil.copytree(ROOT,dest,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
   if kind=='owner-debit':
    p=dest/'RESULT.json';p.chmod(0o600);x=json.loads(p.read_bytes());x['providers']['base']['cone_witnesses'][0]['owner_debit']={'1':0};p.write_text(json.dumps(x))
   else:
    p=dest/'inputs/WORD-base.json.gz';p.chmod(0o600);p.write_bytes(p.read_bytes()+b'\0')
   env=os.environ.copy();env['PYTHONPYCACHEPREFIX']=str(Path(tmp)/'fresh-cache')
   r=subprocess.run([sys.executable,'-O','-B',str(dest/'verify.py'),'--quick'],capture_output=True,text=True,env=env,timeout=120)
   V.need(r.returncode!=0 and ('result mismatch' if kind=='owner-debit' else 'frozen source hash') in r.stderr,'actual CLI rejection '+kind)
 print('PASS_COMPOSITION_CONTROLS positives=2 semantic_rejections=6 optimized_cli_rejections=2')
if __name__=='__main__':main()
