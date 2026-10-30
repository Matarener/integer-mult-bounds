"""Resume after a declared-edit binding repair; do not erase first failure.
Unchanged preparatory discovery is reused by exact source-change coverage.
The complete original release (including strict global admission) runs fresh.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,os,shutil,subprocess,sys,time
P=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def tree(p):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f!=p/'MANIFEST.json'}
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--admission',type=Path,required=True);ap.add_argument('--inputs-v1',type=Path,required=True);ap.add_argument('--inputs-v2',type=Path,required=True);a=ap.parse_args();work=a.admission.resolve();v1=a.inputs_v1.resolve();v2=a.inputs_v2.resolve();package=work/'package'
 assert __debug__ and tree(v1/'source')==read(v1/'source/MANIFEST.json') and tree(v2/'source')==read(v2/'source/MANIFEST.json')
 deriv=read(v2/'V2-DERIVATION.json');assert deriv['modified_files']==['new/borrow/review_staged3605.py','new/rebuild_borrow.py','verify.py']
 assert set(deriv['added_files'])=={'new/borrow/delay_applier.py','new/borrow/review_delayed.py','new/borrow/delayed/PR3605-base.json.gz','new/borrow/delayed/PR3605-extra.json.gz'}
 assert tree(package)==read(package/'MANIFEST.json')
 stages=read(work/'STAGES.json');expected=['owners','parent-lift','rebind','discovery','outer-check_ledger.py','outer-independent_check.py','release'];assert [s['name'] for s in stages]==expected and [s['exit_code'] for s in stages]==[0,0,0,0,0,0,1]
 for s in stages:
  assert sha(work/(s['name']+'.log'))==s['log_sha256'] and sha(Path(s['command'][2]))==s['script_sha256']
 failed=(work/'release/verify/rebuild-borrow-words.log').read_text();assert "'rebuild_plus_patches_equals_shipped': False" in failed and 'FAIL_REBUILD_BORROW' in failed
 assert read(work/'discovery/RESULT.json')['status']=='DISCOVERY' and all(z['exit_code']==0 for z in read(work/'discovery/RESULT.json')['steps'])
 # Changed files are only release reconstruction entry points; none is imported
 # by owners/parent-lift/rebind/discovery/outer checks. Every native source,
 # provider word, fill, scientific engine and corresponding code remains exact.
 coverage=dict(status='AUTHENTICATED_PREPARATORY_STAGE_REUSE_AFTER_DECLARED_EDIT_BINDING_REPAIR',source_manifest_v1=sha(v1/'source/MANIFEST.json'),source_manifest_v2=sha(v2/'source/MANIFEST.json'),derivation_sha256=sha(v2/'V2-DERIVATION.json'),reused_stages=stages[:-1],failed_stage=stages[-1],first_failure_scope='Declared reconstruction stops at PR3605; actual native endpoint/control checks passed but byte-for-content equality correctly fails.',source_changed_files=deriv['modified_files'],source_added_files=deriv['added_files'],native_scientific_words_and_engines_unchanged=True,fresh_stage='Entire original verify_release.py with all native binding/rebuild/independent/strict/outer/control stages; retained parent/native evidence remains explicit reuse.')
 write(work/'V2-REUSE-COVERAGE.json',coverage)
 for rel in deriv['added_files']+['new/rebuild_borrow.py','new/borrow/review_staged3605.py']:
  dst=package/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(v2/'source'/rel,dst)
 # Preserve every existing runtime patch to verify.py while appending one hook.
 entry=next(r for r in deriv['patches'] if r['path']=='verify.py');before,after=entry['replacement'];text=(package/'verify.py').read_text();assert text.count(before)==1;(package/'verify.py').write_text(text.replace(before,after))
 write(package/'MANIFEST.json',tree(package))
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None);env.pop('PYTHONPATH',None)
 out=work/'release-v2';assert not out.exists();cmd=[sys.executable,'-B',str(package/'verify_release.py'),'--main',str(v2),'--work',str(out),'--native-cache',str(v2/'native-cache'),'--jobs','1'];start=time.monotonic()
 with (work/'release-v2.log').open('w') as log:r=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
 finalstage=dict(name='release',command=cmd,script_sha256=sha(package/'verify_release.py'),log_sha256=sha(work/'release-v2.log'),exit_code=r.returncode,seconds=time.monotonic()-start)
 write(work/'V2-STAGES.json',stages[:-1]+[finalstage]);assert r.returncode==0,'see release-v2.log'
 result=read(work/'RESULT.json');receipt=read(out/'RELEASE-RECEIPT.json');C=Q(read(package/'new/SPEC.json')['expected']['complex_lower']);K=C-Q(1,10**46)-Q(1,10**70)
 assert receipt['status']=='PASS_RELEASE' and Q(receipt['kappa_decimal'])==K and receipt['manifest_sha256']==sha(package/'MANIFEST.json')
 assert result['profile']==read(P/'LEAD1-PRICE.json')['profile'] and C==Q(read(P/'LEAD1-PRICE.json')['root_interval'][0]) and K>Q(read(P/'sources/T360-PRICE.json')['root_interval'][1])
 result.update(status='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE',source_manifest_sha256=sha(v2/'source/MANIFEST.json'),source_file_count=652,native_receipt_sha256=sha(v2/'NATIVE-RECEIPT.json'),complex_lower=str(C),kappa=str(K),kappa_decimal=receipt['kappa_decimal'],release_receipt_sha256=sha(out/'RELEASE-RECEIPT.json'),package_manifest_sha256=sha(package/'MANIFEST.json'),stages=stages[:-1]+[finalstage],source_reconstruction_binding_repair=True,reuse_coverage_sha256=sha(work/'V2-REUSE-COVERAGE.json'),scope='Conditional finite construction and complete modern outer arithmetic. Preparatory discovery reused under exact source-change coverage; entire original release rerun after adding declared retiming stage. Both current native chains freshly executed earlier in this session; unchanged retained native/parent evidence explicitly reused. Inherited theorem hypotheses remain.')
 write(work/'RESULT-v2.json',result);print(result['status'],result['kappa_decimal'],flush=True)
if __name__=='__main__':main()
