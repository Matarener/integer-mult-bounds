"""Exact new-terminal-word review, separately from the retained stage544 review."""
from pathlib import Path
import gzip,json
import audit_core as C
from audit_verify import semantics
import terminal_applier as T
P=Path(__file__).resolve().parent
rows=[]
for tag in ['base','extra']:
 old=json.loads(gzip.decompress((P/'terminal'/f'PRE-{tag}.json.gz').read_bytes()));record=json.loads((P/'terminal'/f'RECORD-{tag}.json').read_bytes());actual=json.loads(gzip.decompress((P/'receiver-share-parent'/f'BORROW-WORD-43{tag}.json.gz').read_bytes()));w=T.apply(old,record);T.need(w==actual,'terminal declared recipe reconstructs actual word');rows.append({'provider':tag,'semantics':semantics(C,w),'canonical_sha256':T.canonical(w)})
print(json.dumps({'status':'PASS_TERMINAL_WIDTH5_WORD_DERIVATION_AND_DIRTY_SEMANTICS','providers':rows},sort_keys=True),flush=True)
