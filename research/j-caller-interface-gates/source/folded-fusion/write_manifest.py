#!/usr/bin/env python3
"""Write and immediately check the local repaired-package manifest."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
rows=[]
for p in sorted(HERE.iterdir()):
    if p.is_file()and p.name!='MANIFEST.json':
        rows.append({'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
preserved=HERE/'before-metadata-repair-20261019T130921Z/PRESERVED-BYTES.json'
rows.append({'path':str(preserved.relative_to(HERE)),'sha256':hashlib.sha256(preserved.read_bytes()).hexdigest(),'bytes':preserved.stat().st_size})
out={'schema':'folded-fusion-current-word-v2','scientific_pin':'20ecf2891d80b5acf18d980b2164fb44ea7faa90',
     'scope':'repaired explicit current-word metadata; local exact finite all-input/all-f verification; no new kappa','files':rows}
(HERE/'MANIFEST.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
for r in rows:
    if hashlib.sha256((HERE/r['path']).read_bytes()).hexdigest()!=r['sha256']:raise ValueError('manifest mismatch '+r['path'])
print('PASS_REPAIRED_MANIFEST',len(rows),'files')
