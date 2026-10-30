"""Add an explicit final edit stage without weakening predecessor reconstruction."""
from pathlib import Path
import argparse,hashlib,gzip,json,shutil,subprocess
P=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def tree(p):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file() and f.name!='MANIFEST.json' or f.is_file() and f.parent!=p and f.name=='MANIFEST.json'}
def write(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('old',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();old=a.old.resolve();out=a.out.resolve();assert not out.exists();subprocess.run(['/bin/cp','-cR',str(old),str(out)],check=True);s=out/'source';b=s/'new/borrow';(b/'delayed').mkdir()
 oldmanifest=json.loads((s/'MANIFEST.json').read_text());assert tree(s)==oldmanifest
 for tag in ('base','extra'):shutil.copy2(P/'sources'/f'STAGED644-660-{tag}.json.gz',b/'delayed'/f'PR3605-{tag}.json.gz')
 body=(P/'delay_release.py').read_text();body=body[:body.index("if __name__=='__main__':")];body=body.replace('from invoice import profile\n','').replace('from sources.staged_pair import cleanup','from staged_pair import cleanup').replace("P=Path(__file__).parent\n",'')
 body=body.replace("bill,inv,_=profile(x);x['report']['local_profile']={str(k):v for k,v in bill.items()}","bill={1:2437,2:724,3:226,4:102,5:20,8:8};inv={4:26,5:2,6:18,7:52,8:97,9:213}\n assert w['report']['local_profile']=={'1':2439,'2':726,'3':224,'4':102,'5':20,'8':8}\n x['report']['local_profile']={str(k):v for k,v in bill.items()}")
 body+='\n# Explicit final declared stage; source pin checked by literal predecessor chain.\ndef apply(w):\n return build(w)[0]\n';(b/'delay_applier.py').write_text(body)
 review=(P/'reviews/lead1/check.py').read_text();review=review.replace('P=Path(__file__).resolve().parents[2]','P=Path(__file__).resolve().parent').replace("for pin in json.loads((P/'SOURCE-PINS.json').read_text()):assert sha((P/pin['retained']).read_bytes())==pin['sha256']\n",'')
 review=review.replace("P/'sources'/f'STAGED644-660-{provider}.json.gz'","P/'delayed'/f'PR3605-{provider}.json.gz'").replace("P/'lead1-words'/f'DELAYED-{provider}.json.gz'","P/'words'/f'BORROW-WORD-43{provider}.json.gz'")
 review='\n'.join(line for line in review.splitlines() if not line.startswith(' native=json.loads'))+'\n';review=review.replace(',native_word_hash_matches=True','');(b/'review_delayed.py').write_text(review)
 patches=[]
 def patch(rel,before,after):
  f=s/rel;txt=f.read_text();assert txt.count(before)==1,(rel,before);h=sha(f);f.write_text(txt.replace(before,after));patches.append(dict(path=rel,before=h,after=sha(f),replacement=[before,after]))
 patch('new/rebuild_borrow.py',"steps.append('staged3605')","steps.append('staged3605')\n    import delay_applier\n    chain.append(delay_applier.apply(chain[-1]));steps.append('delayed-release-v1')")
 patch('new/borrow/review_staged3605.py',"D/f'words/BORROW-WORD-43{tag}.json.gz'","D/f'delayed/PR3605-{tag}.json.gz'")
 patch('verify.py',"run('staged3605-review',P/'new/borrow/review_staged3605.py')","run('staged3605-review',P/'new/borrow/review_staged3605.py')\nrun('delayed-release-independent-review',P/'new/borrow/review_delayed.py')")
 manifest=tree(s);write(s/'MANIFEST.json',manifest);newsha=sha(s/'MANIFEST.json')
 driver=out/'admit.py';txt=driver.read_text();txt=txt.replace(sha(old/'source/MANIFEST.json'),newsha).replace('source_file_count=648','source_file_count='+str(len(manifest)));driver.write_text(txt)
 receipt=json.loads((out/'NATIVE-RECEIPT.json').read_text());receipt['manifest_sha256']=newsha;receipt['native_scientific_engines_unchanged_from_manifest']=sha(old/'source/MANIFEST.json');receipt['declared_source_reconstruction_changed_only']=True;write(out/'NATIVE-RECEIPT.json',receipt)
 write(out/'V2-DERIVATION.json',dict(old_manifest=sha(old/'source/MANIFEST.json'),new_manifest=newsha,old_driver_sha256=sha(old/'admit.py'),new_driver_sha256=sha(driver),source_count=len(manifest),modified_files=[k for k in oldmanifest if oldmanifest[k]!=manifest[k]],added_files=sorted(set(manifest)-set(oldmanifest)),patches=patches,scope='Preserve PR3605 reconstruction against frozen intermediate words, append explicit literal retiming and independent reconstruction. Native scientific engines and actual current words unchanged; same-session native evidence explicitly rebound.'))
 print(newsha,len(manifest))
if __name__=='__main__':main()
