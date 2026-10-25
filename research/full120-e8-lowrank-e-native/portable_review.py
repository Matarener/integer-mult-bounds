from pathlib import Path
from hashlib import sha256
import importlib.util,json,sys
D=Path(__file__).resolve().parent
review=D/'review';spec=importlib.util.spec_from_file_location('portable_scoped_E120_review',review/'check.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
if sha256((review/'FILES.json').read_bytes()).hexdigest()!='bdf9a111fddef1b2b0fe27fe90af02613f0b3eef9aff79b67605a8a7f3f1d3ac':raise ValueError('original review seal')
for f in json.loads((review/'FILES.json').read_bytes())['files']:
 b=(review/f['path']).read_bytes()
 if len(b)!=f['bytes']or sha256(b).hexdigest()!=f['sha256']:raise ValueError('original review bytes '+f['path'])
m.AUTHOR=D/'author';r=m.calculate();expected=json.loads((review/'RESULT.json').read_bytes())
r['author_package']=expected['author_package'];r.pop('scientific_payload_sha256');r['scientific_payload_sha256']=sha256(m.canon(r)).hexdigest()
if r!=expected:raise ValueError('portable exact scoped review result')
print(json.dumps(r,sort_keys=True))
