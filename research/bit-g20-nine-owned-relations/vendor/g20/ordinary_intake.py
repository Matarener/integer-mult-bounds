"""Append-only source intake for the ordinary certificate, never old outputs."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
HERE=Path(__file__).resolve().parent;RUN=HERE.parent;OUT=HERE/'ordinary-certificate';PUB=RUN/'bootstrap-publication'/'gitfree-0003'/'research'
def need(c,m):
 if not c:raise ValueError(m)
def main():
 (OUT/'inputs').mkdir(parents=True,exist_ok=True)
 choices={
 'credited_intervals.py':PUB/'higher-moment-strictification'/'verify.py',
 'separate_series.py':PUB/'bit-compact-productive-controller'/'exact_series.py',
 'PR4814-PROOF.md':PUB/'bit-finite-ordinary-bootstrap'/'PROOF.md',
 'PR4814-RESULT.json':PUB/'bit-finite-ordinary-bootstrap'/'RESULT.json',
 'PR4814-verify.py.txt':PUB/'bit-finite-ordinary-bootstrap'/'verify.py',
 'PR4814-independent.py.txt':PUB/'bit-finite-ordinary-bootstrap'/'independent.py',
 'PR4760-PROOF.md':PUB/'bit-compact-productive-controller'/'PROOF.md',
 'PR4760-price.py.txt':PUB/'bit-compact-productive-controller'/'price.py',
 'tail-engine.py.txt':PUB/'query-thinned-controllers'/'verify.py',
 'provider-MANIFEST.json':HERE/'provider'/'MANIFEST.json',
 'provider-RESULT.json':HERE/'RESULT.json',
 'provider-INVOICE.json':HERE/'provider'/'data'/'INVOICE.json',
 'provider-FULL-FEES.json':HERE/'provider'/'data'/'FULL-FEES.json',
 'provider-GLOBAL-RESULT.json':HERE/'provider'/'data'/'GLOBAL-RESULT.json',
 'provider-cold-normal.json':HERE/'verification-normal-0002'/'RESULT.json',
 'provider-cold-O.json':HERE/'verification-optimized-0001'/'RESULT.json',
 'FINITE-PRECOMPILATION.md':HERE/'inputs'/'FINITE-PRECOMPILATION.md',
 'DELAYED-COVER-BRIDGE.md':HERE/'inputs'/'DELAYED-COVER-BRIDGE.md',
 'three-stage-cover-bit.tex':HERE/'inputs'/'three-stage-cover-bit.tex',
 'three-stage-cover-rows.tex':HERE/'inputs'/'three-stage-cover-rows.tex'}
 rows=[]
 for name,src in choices.items():
  raw=src.read_bytes();dst=OUT/'inputs'/name
  if dst.exists():need(dst.read_bytes()==raw,'Intake overwrite forbidden '+name)
  else:dst.write_bytes(raw)
  rows.append({'path':'inputs/'+name,'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'read_only_origin':str(src)})
 manifest=OUT/'INPUTS.json';need(not manifest.exists(),'Intake manifest already frozen')
 manifest.write_text(json.dumps({'schema':'g20-ordinary-inputs/1','at_utc':datetime.now(timezone.utc).isoformat(),'files':rows},indent=2)+'\n',encoding='utf-8');print(json.dumps({'inputs':len(rows),'bytes':sum(r['bytes']for r in rows)}))
if __name__=='__main__':main()
