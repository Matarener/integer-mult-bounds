"""Freeze terminal receipts and logs, retaining failures/reuse separately."""
from pathlib import Path
import argparse,hashlib,json,shutil
P=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--admission',type=Path,required=True);ap.add_argument('--inputs',type=Path,required=True);a=ap.parse_args();w=a.admission;rel=w/'release-v2';s=rel/'verify/strict';out=P/'evidence/complete';assert not out.exists();out.mkdir()
 items={'RESULT.json':w/'RESULT-v2.json','RELEASE-RECEIPT.json':rel/'RELEASE-RECEIPT.json','NATIVE-RECEIPT.json':a.inputs/'NATIVE-RECEIPT.json','STAGES.json':w/'V2-STAGES.json','REUSE-COVERAGE.json':w/'V2-REUSE-COVERAGE.json','SOURCE-DERIVATION.json':a.inputs/'V2-DERIVATION.json','PACKAGE-MANIFEST.json':w/'package/MANIFEST.json','VERIFY-RESULT.json':rel/'verify/RESULT.json','VERIFY-STAGES.json':rel/'verify/STAGES.json','STRICT-RESULT.json':s/'RESULT.json','STRICT-STAGES.json':s/'STAGES.json','INDEPENDENT.json':s/'INDEPENDENT.json','PREFIX-AND-INVOICE.json':s/'global/audit/PREFIX-AND-INVOICE.json','ASSEMBLY.json':s/'ASSEMBLY.json','ADMISSION-CONTROLS.json':s/'ADMISSION-CONTROLS.json','BIT-CONTROLS.json':s/'BIT-CONTROLS.json','GEOMETRY-CONTROLS.json':rel/'verify/GEOMETRY-CONTROLS.json','OUTER-LEDGER.json':w/'package/outer/LEDGER.json','OUTER-CLAIM.json':w/'package/outer/OUTER-CLAIM.json','FIRST-FAILED-VERIFY-STAGES.json':w/'release/verify/STAGES.json','FIRST-FAILED-REBUILD.txt':w/'release/verify/rebuild-borrow-words.log','FIRST-FAILED-RELEASE.txt':w/'release.log','RELEASE-V2.txt':w/'release-v2.log','VERIFY.txt':rel/'verify.log','OUTER.txt':rel/'outer.log'}
 for name,f in items.items():assert f.is_file(),f;shutil.copy2(f,out/name)
 # Preserve and bind each directly recorded execution log, without large generated trees.
 for prefix,root,stages in [('PREP',w,json.loads((w/'V2-STAGES.json').read_text())[:-1]),('VERIFY',rel/'verify',json.loads((rel/'verify/STAGES.json').read_text())),('STRICT',s,json.loads((s/'STAGES.json').read_text()))]:
  for stage in stages:
   f=root/(stage['name']+'.log')
   if not f.exists():continue
   if 'log_sha256' in stage:assert sha(f)==stage['log_sha256']
   name=prefix+'-'+stage['name']+'.txt';shutil.copy2(f,out/name)
 pins={f.name:sha(f) for f in sorted(out.iterdir())};(out/'PINS.json').write_text(json.dumps(dict(scope='Authenticated stored completed execution, not a fresh replay',files=pins),sort_keys=True,indent=2)+'\n');print(sha(out/'PINS.json'))
if __name__=='__main__':main()
