"""Optional full native/global/outer replay, with hash-bound retained ancestry.
Dugongue with OpenAI Codex assistance. Apache-2.0.
Requires Python 3.12, numpy, scipy, sympy==1.14.0 and mpmath==1.3.0.
No configuration or installed package is changed by this script.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,gzip,hashlib,json,os,shutil,subprocess,sys,tarfile,urllib.request
sys.dont_write_bytecode=True

HERE=Path(__file__).resolve().parent
PACKAGE=HERE.parent
HEAD='fa041037a3374eaa08feeca0b26a5d6893194147'
ARCHIVE_URL='https://raw.githubusercontent.com/CrocSwap/integer-mult-bounds/'+HEAD+'/research/staged544-producer-return/REPLAY-INPUTS.tar.gz'
SOURCE_MANIFEST='3d2ee0175b0cd8aec80c12fef82c2da3a3a54785ca9113140762fd5c41979608'
COMMIT='terminal-width5-20261019'
EXPECTED=Q('0.001730663236534549309146')-Q(1,10**46)-Q(1,10**70)

def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def write(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
def tree(p,exclude=()):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f.relative_to(p).as_posix() not in exclude}

def adapt_admission(original,admit):
 need(sha(original)=='76f1b45793abb32a902a8d3cd353b39a018a35a277bb4e223e7508226b71eb6e','retained admission engine hash');body=original.read_text(encoding='utf8');old="'staged544': dict(commit='staged544-literal-v1',manifest='4c4f7067b1b5404b59213f480e9d91c96ffc79b5458e2736b159f5a522ed2dc3'";new=f"'staged544': dict(commit='{COMMIT}',manifest='{SOURCE_MANIFEST}'";need(body.count(old)==1 and body.count('helpers=408,source_file_count=660')==1,'exact admission profile preimages');body=body.replace(old,new).replace('helpers=408,source_file_count=660','helpers=408,source_file_count=666');patch_log=[[old,new],['helpers=408,source_file_count=660','helpers=408,source_file_count=666']]
 # The inherited engine's constant 139 assumes six width types. Preserve its
 # complete mutation generator and bind only closure/report counts to frozen SPEC.
 for old_count,new_count in [("len(rd(work/'ADMISSION-CONTROLS.json')['rejected_controls'])==139","len(rd(work/'ADMISSION-CONTROLS.json')['rejected_controls'])==rd(spec)['expected']['assembly_controls_rejected']"),("controls=dict(admission=139,bit=12,controller=15,independent_owner=8,geometry=6)","controls=dict(admission=rd(P/'new/SPEC.json')['expected']['assembly_controls_rejected'],bit=12,controller=15,independent_owner=8,geometry=6)")]:
  before,after=repr(old_count),repr(new_count)
  # admit544 stores literal patch destinations using single-quoted Python strings.
  variants=[(q+old_count.replace('\\','\\\\').replace(q,'\\'+q)+q,q+new_count.replace('\\','\\\\').replace(q,'\\'+q)+q) for q in [chr(39),chr(34)]]
  hits=[pair for pair in variants if body.count(pair[0])==1];need(len(hits)==1,'exact inherited count patch destination');body=body.replace(*hits[0]);patch_log.append(list(hits[0]))
 admit.write_text(body,encoding='utf8',newline='\n');compile(body,str(admit),'exec');write(admit.with_name('ADAPTER.json'),{'original_engine_sha256':sha(original),'effective_engine_sha256':sha(admit),'literal_patches':patch_log,'scope':'Only exact source-profile/file-count and frozen-spec mutation-count closure/report adaptations; scientific predicates unchanged.'})

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--work',type=Path,required=True);ap.add_argument('--archive',type=Path);ap.add_argument('--prepare-only',action='store_true');ap.add_argument('--reuse-base-native',type=Path);ap.add_argument('--reuse-extra-native',type=Path);ap.add_argument('--jobs',type=int,default=1);a=ap.parse_args()
 need(__debug__ and a.jobs>0,'assertions and positive jobs required');work=a.work.resolve();need(not work.exists() and not work.is_relative_to(PACKAGE),'fresh external work directory required');work.mkdir(parents=True)
 pins=read(HERE/'PREDECESSOR.json');archive=a.archive.resolve() if a.archive else work/'predecessor.tar.gz'
 if a.archive is None:
  with urllib.request.urlopen(ARCHIVE_URL) as src,archive.open('wb') as dst:shutil.copyfileobj(src,dst)
 need(sha(archive)==pins['archive_sha256'],'pinned predecessor archive digest');inputs=work/'inputs';inputs.mkdir();seen=set()
 with tarfile.open(archive) as t:
  for m in t:
   need(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and m.name not in seen and m.name in pins['files'],'safe declared predecessor member');raw=t.extractfile(m).read();need(hashlib.sha256(raw).hexdigest()==pins['files'][m.name],'predecessor member digest');seen.add(m.name);out=inputs/m.name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
 need(seen==set(pins['files']),'complete 756-file retained input inventory');source=inputs/'source';old_source_manifest=sha(source/'MANIFEST.json');need(old_source_manifest=='4c4f7067b1b5404b59213f480e9d91c96ffc79b5458e2736b159f5a522ed2dc3','retained 660-source manifest');need(tree(source,('MANIFEST.json',))==read(source/'MANIFEST.json'),'retained source file hashes')
 borrow=source/'new/borrow';terminal=borrow/'terminal';terminal.mkdir();registry=read(source/'new/BORROW-PROVIDERS.json')
 shutil.copy2(HERE/'terminal_applier.py',borrow/'terminal_applier.py');shutil.copy2(HERE/'terminal_review.py',borrow/'terminal_review.py');sys.path.insert(0,str(borrow));import terminal_applier as T
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  name='BORROW-WORD-43'+tag+'.json.gz';old=borrow/'words'/name;before=read(old);final=PACKAGE/'inputs'/('NEW-'+tag+'.json.gz');new=read(final);shutil.copy2(old,terminal/('PRE-'+tag+'.json.gz'));old.write_bytes(final.read_bytes())
  record={'source_canonical_sha256':T.canonical(before),'candidate_canonical_sha256':T.canonical(new),'new_fields':{k:v for k,v in new.items() if before[k]!=v},'source_attribution':'PR3734 dataisfire and retained lineage; terminal derivative Dugongue/OpenAI Codex'};write(terminal/('RECORD-'+tag+'.json'),record);need(T.apply(before,record)==new,'declared terminal generator')
  canonical=read(PACKAGE/'owner/inputs'/('old-NATIVE-'+tag+'.json.gz'));origin=canonical['helper_origin'];need(len(origin)==408,'retained native helper order');widths=[len(new['helper_final'].get(str(r),[1<<i for i in range(9)]))-len(new['start_extra'].get(str(r),[])) for r in origin];registry[pid]={'widths':widths,'actual_paid_profile':new['report']['local_profile']}
 write(source/'new/BORROW-PROVIDERS.json',registry)
 for patch in read(HERE/'SOURCE-PATCHES.json'):
  out=source/patch['path'];need(sha(out)==patch['before_sha256'],'generator patch source hash');body=out.read_text(encoding='utf8');need(body.count(patch['old'])==1,'generator patch literal preimage');out.write_text(body.replace(patch['old'],patch['new']),encoding='utf8',newline='\n');need(sha(out)==patch['after_sha256'],'generator patch output hash')
 write(source/'MANIFEST.json',tree(source,('MANIFEST.json',)));need(len(read(source/'MANIFEST.json'))==666 and sha(source/'MANIFEST.json')==SOURCE_MANIFEST,'exact 666-file changed source closure');write(work/'PREPARED.json',{'status':'PASS_TERMINAL_SOURCE_RECONSTRUCTION','predecessor_head':HEAD,'archive_sha256':pins['archive_sha256'],'old_source_manifest_sha256':old_source_manifest,'new_source_manifest_sha256':SOURCE_MANIFEST,'source_files':666})
 adapt_admission(inputs/'admit544.py',work/'admit_terminal.py')
 prepared=read(work/'PREPARED.json');prepared['admission_adapter_sha256']=sha(work/'ADAPTER.json');write(work/'PREPARED.json',prepared)
 if a.prepare_only:print('PASS_TERMINAL_SOURCE_RECONSTRUCTION',flush=True);return
 import numpy,scipy,sympy,mpmath
 need(sympy.__version__=='1.14.0' and mpmath.__version__=='1.3.0','exact symbolic dependency versions required');env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONINTMAXSTRDIGITS='0',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');env.pop('PYTHONOPTIMIZE',None)
 if os.name=='nt':env['PYTHONPATH']=str(HERE)
 def run(name,command):
  with (work/(name+'.log')).open('w',encoding='utf8',newline='\n') as log:r=subprocess.run(command,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
  need(r.returncode==0,'failed '+name+'; retained scoped log');print('PASS',name,flush=True)
 receipt=read(inputs/'NATIVE-RECEIPT.json');cache=inputs/'native-cache'
 for tag,pid,reuse in [('base','gauge44',a.reuse_base_native),('extra','extra',a.reuse_extra_native)]:
  word=borrow/'words'/('BORROW-WORD-43'+tag+'.json.gz');native=reuse.resolve() if reuse else work/('native-'+tag)
  if reuse is None:run('native-'+tag,[sys.executable,'-B',str(source/'new/fastnative/run_native.py'),str(word),str(native)])
  nr=read(native/'RESULT.json');need(nr['source_sha256']==tree(source/'new/fastnative/vendor'),'complete native scientific source closure, including reused directories');need(nr['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY' and nr['word_sha256']==sha(word),'exact fresh native word binding');need([z['step'] for z in nr['steps']]==['native','ledgers','local-replay','wrappers','phases'] and all(z['exit_code']==0 for z in nr['steps']),'five-stage native coverage')
  need(read(native/'native/local/FULL-WORD.json.gz')==read(word),'native complete word equality');entry=cache/sha(word);need(not entry.exists(),'fresh changed native cache entry');shutil.copytree(native/'native',entry);write(entry/'CACHE.json',{'word_sha256':sha(word),'files':tree(entry)});receipt['providers'][tag]={'word_sha256':sha(word),'complete_native_files':tree(entry,('CACHE.json',))}
  canonical=read(entry/'local/CANONICAL-WORD.json.gz');widths=[len(canonical['frames'][canonical['final'][r]])-len(canonical['frames'][canonical['start'][r]]) for r in range(224,632)];need(widths==registry[pid]['widths'] and read(entry/'local/LOCAL-CHECKS.json')['forward']['paid_profile']==registry[pid]['actual_paid_profile'],'native metadata equality')
 receipt.update(status='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE',source_commit=COMMIT,manifest_sha256=SOURCE_MANIFEST,cache_files=tree(cache));write(work/'NATIVE-RECEIPT.json',receipt)
 admit=work/'admit_terminal.py'
 arguments={'source':source,'fill':PACKAGE/'owner/FILL.json.gz','order':PACKAGE/'owner/inputs/ORDER.json','dispatch':PACKAGE/'owner/inputs/DISPATCH.json','native-cache':cache,'native-receipt':work/'NATIVE-RECEIPT.json','work':work/'admission','replica-helper-dir':inputs/'helpers','reconstructor':inputs/'helpers/reconstruct_replica.py','comparison-claim':PACKAGE/'admission/PR3682-CLAIM.json','blocknorm-checker':inputs/'extension_blocknorm.py'}
 command=[sys.executable,'-B',str(admit)]
 for k,v in arguments.items():command+=['--'+k,str(v)]
 command+=['--source-profile','staged544','--comparison-profile','pr3682','--jobs',str(a.jobs)];run('complete-admission',command);result=read(work/'admission/RESULT.json');need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE' and Q(result['kappa'])==EXPECTED,'exact new complete headline');need(result['profile']==read(PACKAGE/'owner/PROFILE.json'),'exact complete paid profile');write(work/'RESULT.json',{'status':'PASS_TERMINAL_WIDTH5_COMPLETE_CONDITIONAL_RELEASE','kappa':str(EXPECTED),'source_manifest_sha256':SOURCE_MANIFEST,'retained_ancestry_reused':True,'new_native_reuse':{'base':bool(a.reuse_base_native),'extra':bool(a.reuse_extra_native)},'release_receipt_sha256':sha(work/'admission/release/RELEASE-RECEIPT.json')});print('PASS_TERMINAL_WIDTH5_COMPLETE_CONDITIONAL_RELEASE',flush=True)

if __name__=='__main__':main()
