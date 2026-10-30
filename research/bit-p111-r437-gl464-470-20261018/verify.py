#!/usr/bin/env python3
"""One-command cold replay from a self-contained archive; no network. Apache-2.0."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile,time
if not __debug__:raise RuntimeError('Verification requires assertions; do not run with -O.')
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path);a=ap.parse_args()
 if a.output:
  out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
 else:out=Path(tempfile.mkdtemp(prefix='bit-r438-cold-'))
 env=os.environ.copy();env.pop('PYTHONOPTIMIZE',None);env.pop('PYTHONPATH',None)
 start=time.monotonic();runs=[]
 def run(script,*args):
  cache=out/('private-pycache-'+str(len(runs)));cache.mkdir(exist_ok=False)
  cmd=[sys.executable,'-E','-X','utf8','-X','pycache_prefix='+str(cache),'-B',str(script),*[str(x) for x in args]]
  before=time.monotonic();r=subprocess.run(cmd,cwd=out,env=env,capture_output=True,text=True,encoding='utf8',timeout=600)
  idx=len(runs);(out/(f'{idx:02d}-'+script.stem+'.log')).write_text(r.stdout+r.stderr,encoding='utf8')
  runs.append({'script':str(script.relative_to(P)),'arguments':[str(x) for x in args],
   'exit_code':r.returncode,'seconds':time.monotonic()-before})
  if r.returncode:raise RuntimeError(f'{script.name} failed; see {out}/{idx:02d}-{script.stem}.log')
 # All runtime inputs are local content-pinned archive files. The original
 # source manifests are provenance, not an assertion of current Git HEAD.
 for z in json.loads((P/'SOURCES.json').read_bytes())['files']:
  assert sha(P/z['path'])==z['sha256'],z['path']
 expected=json.loads((P/'EXPECTED.json').read_bytes())
 run(P/'code/generate.py',out)
 run(P/'vendor/xcheck_p.py',out/'WORD.json.gz','--json',out/'UPSTREAM-XCHECK.json')
 run(P/'code/word_audit.py',out)
 run(P/'code/catalog_check.py',out)
 run(P/'code/source_history_scope.py',out)
 run(P/'vendor/export_records.py',out/'WORD.json.gz',out/'records')
 assert sha(out/'records/249-records.bin')==expected['records_sha256']
 run(P/'code/local_counter.py',out)
 (out/'nine').mkdir();shutil.copyfile(P/'data/GEOMETRY.json',out/'nine/GEOMETRY.json')
 run(P/'vendor/global_k.py','--word',out/'WORD.json.gz','--local-check',out,'--out',out/'nine',
  '--isometries',P/'data/residual-isometries.json','--no-banks','--stages','9','--replicas','32')
 run(P/'code/match.py',out)
 run(P/'vendor/emit_k.py',out/'nine',out,out/'hosted','--selection',out/'SELECTION.json','--key','bit',
  '--host-all','--depth','2','--version-tag','r437-public470-plus-464GL')
 run(P/'vendor/audit_hosted_k.py',out,out/'hosted',out/'HOSTING-AUDIT.json')
 # Historical outer diagnostic is intentionally distinct from the new BIT record.
 run(P/'vendor/assemble9.py',out,out/'hosted',out/'HOSTING-AUDIT.json',P,
  out/'ASSEMBLY-BIT-AND-HISTORICAL-CONTROL.json','pr548')
 run(P/'code/invoice_audit.py',out)
 g=json.loads((out/'hosted/GLOBAL.json').read_bytes());z=json.loads((out/'INVOICE-INDEPENDENT.json').read_bytes())
 for key in ('live','physical','rank_mass','deficit','emitted_events','hosted_residuals'):assert g[key]==expected[key],key
 assert g['profile']==expected['profile'] and g['template_sha256']==expected['template_content_sha256']
 assert g['emitted_program_sha256']==expected['program_sha256']
 assert z['price']['candidate_c']==expected['BIT_c']
 elapsed=time.monotonic()-start;assert elapsed<=1200
 outputs={str(p.relative_to(out)).replace('\\','/'):sha(p) for p in out.rglob('*') if p.is_file()}
 record={'status':'PASS_COLD_REPLAY_CANONICAL_WORD_ACTUAL_PROGRAM_FULL_INVOICE_AND_BIT_RECORD',
  'at_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'seconds':elapsed,'commands':runs,
  'word_content_sha256':expected['word_content_sha256'],'program_sha256':g['emitted_program_sha256'],
  'BIT_c':expected['BIT_c'],'whole_kappa_changed':False,'hosted_CI':False,
  'scope':'Conditional finite supplier under unchanged selected all-size/SOURCE/field/PR442 interfaces; no unconditional multiplication theorem.',
  'outputs':outputs}
 (out/'REPLAY-RECEIPT.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'status':record['status'],'output':str(out),'seconds':elapsed,
  'BIT_c':record['BIT_c'],'program_sha256':record['program_sha256'],'receipt_sha256':sha(out/'REPLAY-RECEIPT.json')},indent=2))
if __name__=='__main__':main()
