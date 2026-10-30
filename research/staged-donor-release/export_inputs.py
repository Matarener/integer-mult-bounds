"""Retain the exact full source/cache/owner closure and reconstruction predecessor."""
from pathlib import Path
import argparse,tarfile,hashlib,json
P=Path(__file__).parent
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,required=True);ap.add_argument('--predecessor',type=Path,required=True);ap.add_argument('--retained',type=Path,required=True);ap.add_argument('--allocation',type=Path,required=True);ap.add_argument('--fill',type=Path,required=True);a=ap.parse_args();src=a.inputs;items={}
 for folder in ['source','native-cache']:
  for f in (src/folder).rglob('*'):
   if f.is_file():items[f.relative_to(src).as_posix()]=f
 for n in ['admit.py','NATIVE-RECEIPT.json','DERIVATION.json','V2-DERIVATION.json']:items[n]=src/n
 for n in ['lift_parent.py','replica_parent.py','reconstruct_replica.py']:items['helpers/'+n]=a.retained/'helpers'/n
 for n,f in [('extension_blocknorm.py',a.retained/'adapters/extension_blocknorm.py'),('PR2969-CLAIM.json',a.retained/'PR2969-CLAIM.json'),('FILL.json.gz',a.fill),('ORDER.json',a.allocation/'ORDER.json'),('DISPATCH.json',a.allocation/'DISPATCH.json')]:items[n]=f
 for n in ['admit.py','NATIVE-RECEIPT.json','source/MANIFEST.json','source/verify.py','source/new/rebuild_borrow.py','source/new/borrow/review_staged3605.py']:items['_provenance/v1/'+n]=a.predecessor/n
 manifest={n:sha(f) for n,f in sorted(items.items())};archive=P/'REPLAY-INPUTS.tar.gz';tmp=P/'REPLAY-INPUTS-new.tar.gz'
 with tarfile.open(tmp,'w:gz',compresslevel=9) as tf:
  for n,f in sorted(items.items()):
   info=tf.gettarinfo(str(f),arcname=n);info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
   with f.open('rb') as stream:tf.addfile(info,stream)
 tmp.replace(archive)
 (P/'REPLAY-INPUTS.json').write_text(json.dumps(dict(archive_sha256=sha(archive),files=manifest,scope='Self-contained exact v2 input/source export. Includes exact v1 source manifest and all differing v1 source files/driver/receipt, so the preparatory reuse source tree can be reconstructed without private caches or Git. Explicit retained native/parent reuse, current changed native fresh in this session.'),indent=2)+'\n');print(archive.stat().st_size,len(items))
if __name__=='__main__':main()
