"""Copy exact immutable local inputs; no network or edits to old packages."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parent;RUN=ROOT.parent;H=RUN/'center-bit-extension'
def need(c,m):
 if not c:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 dest=ROOT/'inputs';dest.mkdir(exist_ok=True);provider=ROOT/'provider';provider.mkdir(exist_ok=True);sources=RUN/'source4359/current-main-repository';pub=RUN/'bootstrap-publication/gitfree-0003/research/bit-compact-productive-controller'
 mapping={
  'BASELINE-LOCAL.json.gz':RUN/'native-small/gate0003/local-partial/WORD.json.gz',
  'FORWARD.json.gz':H/'gate0020-shadow-assisted-query-fusion/WORD.json.gz',
  'INVERSE.json.gz':H/'gate0022-shadow-fusion-inverse-and-requests/INVERSE-WORD.json.gz',
  'FRAMES.json':H/'gate0001-native-coupled667/FRAMES.json',
  'CONTROLLER.json':sources/'research/query-thinned-controllers/BIT-CONTROLLER.json',
  'REFERENCE111.json.gz':sources/'research/kappa-rebuild/bit/sources/pr589-regenerated/WORD.json.gz',
  'BASELINE-GLOBAL-RESULT.json':RUN/'native-small/gate0004/RESULT.json',
  'BASELINE-RATIONAL-BINDING.json':RUN/'native-small/gate0004/RATIONAL-BINDING.json',
  'ACTIVE-AXES.json':RUN/'native-small/gate0004/ACTIVE-AXES.json',
  'G20-WINDOW.json':H/'gate0020-shadow-assisted-query-fusion/SELECTED-WINDOW.json',
  'G22-FRESH-REQUESTS.json':H/'gate0022-shadow-fusion-inverse-and-requests/FRESH-QUERY-REQUESTS.json',
  'G23-EXPECTED.json':H/'gate0023-shadow-fusion-controller/RESULT.json',
  'G23-RAW-PRICE.json':H/'gate0023-shadow-fusion-controller/PRICE.json',
  'DELAYED-COVER-BRIDGE.md':sources/'research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md',
  'FINITE-PRECOMPILATION.md':sources/'research/kappa-rebuild/architecture/FINITE-PRECOMPILATION.md',
  'three-stage-cover-bit.tex':sources/'notes/three-stage-cover-bit.tex',
  'three-stage-cover-rows.tex':sources/'notes/three-stage-cover-rows.tex',
  '02-streams.tex':RUN.parent/'20261020/framework/openai109/02-streams.tex',
  '4814-local_word.py.txt':pub/'local_word.py',
  '4814-global_word.py.txt':pub/'global_word.py',
  '4814-audit_stream.py.txt':pub/'audit_stream.py',
  '4814-independent_native.py.txt':pub/'independent_native.py',
 }
 pins=[]
 for name,source in mapping.items():
  b=source.read_bytes();target=dest/name
  if target.exists():need(target.read_bytes()==b,'Refuse changed input '+name)
  else:target.write_bytes(b)
  pins.append({'relative_path':'inputs/'+name,'sha256':sha(target),'bytes':len(b),'read_only_origin':str(source)})
 out=ROOT/'INPUT-PINS.json'
 if out.exists():need(json.loads(out.read_bytes())['files']==pins,'Inputs immutable')
 else:out.write_text(json.dumps({'schema':'g20-private-candidate-inputs/1','at_utc':datetime.now(timezone.utc).isoformat(),'files':pins,'scope':'Historical4760/4814 and research proof bytes are copied read-only. Runtime provider uses these relative local paths only. No publication/ordinary claim.'},indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'status':'PINNED_LOCAL_READONLY_INPUTS','files':len(pins),'bytes':sum(p['bytes']for p in pins)}))
if __name__=='__main__':main()
