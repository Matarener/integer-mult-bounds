"""Bind the separate rational funding audit to this publication's bytes.

Prepared for thu-nmrc with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import gzip,importlib.util,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
P=HERE/'funding-peer'
spec=importlib.util.spec_from_file_location('independent_p104_funding',P/'check.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
result=json.loads(json.dumps(M.calculate(),sort_keys=True))
M.need(result==json.loads((P/'RECEIPT.json').read_bytes()),'Frozen independent funding review')
for name,retained in [('RESULT.json','PUBLIC-RESULT.json'),('SOURCES.json','SOURCES.json')]:
    M.need(json.loads((HERE/name).read_bytes())==M.read(retained),'Current publication '+name)
M.need(json.loads(gzip.decompress((HERE/'WORD.json.gz').read_bytes()))==json.loads(gzip.decompress((P/'inputs/PUBLIC-WORD.json.gz').read_bytes())),'Current publication WORD')
M.need((HERE/'pricing.py').read_bytes()==(P/'inputs/successor_pricing.py').read_bytes(),'Current publication pricing source')
M.need((HERE/'inputs/pr5545-source-closure.tar.gz').read_bytes()==(P/'inputs/pr5545-source-closure.tar.gz').read_bytes(),'Current publication retained source')
print('PASS_PUBLIC_P104_INDEPENDENT_FUNDING',sha256(json.dumps(result,sort_keys=True,separators=(',',':')).encode()).hexdigest())
