#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent
for name in ('SOURCE-PINS.json','MANIFEST.json'):
 for x in json.loads((D/name).read_text())['files']:
  p=Path(x['path']);p=p if p.is_absolute() else D/p
  if hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:raise ValueError(str(p))
print('PASS_FROZEN_SOURCE_AND_REVIEW_MANIFEST')
