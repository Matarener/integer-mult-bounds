"""Explicit derived source/native receipt for unchanged T360 owner admission.
Inputs remain read-only. APFS clones affect disk use only, never file content.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,shutil
P=Path(__file__).parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(p,exclude=()):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f.relative_to(p).as_posix() not in exclude}
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def clone(src,dst):
 subprocess.run(['/bin/cp','-cR',str(src),str(dst)],check=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('out',type=Path);a=ap.parse_args();out=a.out.resolve();assert not out.exists();out.mkdir()
 old=Path('/tmp/three-kappa-materialized/changed');source=out/'source';clone(old/'source',source)
 original=json.loads((source/'MANIFEST.json').read_text());assert tree(source,('MANIFEST.json',))==original
 for tag in ('base','extra'):shutil.copy2(P/'lead1-words'/f'DELAYED-{tag}.json.gz',source/'new/borrow/words'/f'BORROW-WORD-43{tag}.json.gz')
 write(source/'MANIFEST.json',tree(source,('MANIFEST.json',)));manifest=sha(source/'MANIFEST.json');commit='four-leads-delayed-release-v1'
 # Authorize exactly this new immutable source profile; no validation relaxed.
 body=(old/'admit_extension.py').read_text();before="'staged3605': dict(commit='pr3605-ac92a027c78b0c9bb0ada739b26959afda489d0e',manifest='318ede57c79d10323fb1918f7be4d451d1fcdac01c6456fe9851d51d05d59453',helpers=408,source_file_count=648,upstream_head='ac92a027c78b0c9bb0ada739b26959afda489d0e')"
 after=f"'staged3605': dict(commit='{commit}',manifest='{manifest}',helpers=408,source_file_count=648,upstream_head='3efbb5de06a49ffeea6684482f2d3fe48cdca3fb')"
 assert body.count(before)==1;body=body.replace(before,after);(out/'admit.py').write_text(body)
 cache=out/'native-cache';cache.mkdir();retained=old/'native-py312/native-cache';rec=json.loads((old/'native-py312/NATIVE-RECEIPT.json').read_text());assert tree(retained)==rec['cache_files']
 parent='e0eefc96567fbb45e19e6de0ca295381dbe0e686c08ddc783639b065c7c791d4';(cache/'_receipts').mkdir();clone(retained/'_receipts'/parent,cache/'_receipts'/parent)
 for name in ('gauge44-word.json.gz','extra-word.json.gz'):
  key=sha(source/'vendor/pr1297'/name);clone(retained/key,cache/key)
 providers={}
 for tag,runpath in [('base',Path('/tmp/four-kappa-native-base-v2')),('extra',Path('/tmp/four-kappa-native-extra'))]:
  word=source/'new/borrow/words'/f'BORROW-WORD-43{tag}.json.gz';key=sha(word);result=json.loads((runpath/'RESULT.json').read_text());assert result['status']=='PASS_COMPLETE_T74_NATIVE_REPLAY' and result['word_sha256']==key
  assert [s['step'] for s in result['steps']]==['native','ledgers','local-replay','wrappers','phases'] and all(s['exit_code']==0 for s in result['steps'])
  entry=cache/key;clone(runpath/'native',entry);write(entry/'CACHE.json',dict(word_sha256=key,files=tree(entry)));providers[tag]=dict(word_sha256=key,complete_native_files=tree(entry,('CACHE.json',)))
 new=dict(status='PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE',source_commit=commit,manifest_sha256=manifest,providers=providers,retained_parent_receipt_sha256=rec['retained_parent_receipt_sha256'],cache_files=tree(cache),fresh_current_provider_count=2,reused_retained_native_count=2,reused_retained_parent=True,retained_reuse_receipt_sha256=sha(old/'native-py312/NATIVE-RECEIPT.json'))
 updated=tree(source,('MANIFEST.json',))
 write(out/'NATIVE-RECEIPT.json',new);write(out/'DERIVATION.json',dict(old_manifest=sha(old/'source/MANIFEST.json'),new_manifest=manifest,old_driver_sha256=sha(old/'admit_extension.py'),new_driver_sha256=sha(out/'admit.py'),driver_replacements=[[before,after]],source_delta=[k for k in original if original[k]!=updated[k]]))
 print(manifest)
if __name__=='__main__':main()
