"""Independent exact archive and v1/v2 delta closure; no production extractor imports."""
from pathlib import Path
import hashlib,json,tarfile,gzip
P=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
j=lambda b:json.loads(b)
pins=j((P/'REPLAY-INPUTS.json').read_bytes());raw=(P/'REPLAY-INPUTS.tar.gz').read_bytes();assert sha(raw)==pins['archive_sha256']
with tarfile.open(P/'REPLAY-INPUTS.tar.gz') as tf:
 members=tf.getmembers();assert all(m.isfile() for m in members);assert len(members)==len({m.name for m in members})
 data={m.name:tf.extractfile(m).read() for m in members}
assert {k:sha(v) for k,v in data.items()}==pins['files']
d=j(data['V2-DERIVATION.json']);a=j(data['_provenance/v1/source/MANIFEST.json']);b=j(data['source/MANIFEST.json'])
assert sha(data['_provenance/v1/source/MANIFEST.json'])==d['old_manifest'];assert sha(data['source/MANIFEST.json'])==d['new_manifest']
assert len(a)==648 and len(b)==652 and not set(a)-set(b)
assert sorted(set(b)-set(a))==sorted(d['added_files'])
assert sorted(k for k in a if a[k]!=b[k])==sorted(d['modified_files'])
for k,h in b.items():assert sha(data['source/'+k])==h
for k,h in a.items():assert sha(data[('_provenance/v1/source/' if k in d['modified_files'] else 'source/')+k])==h
for patch in d['patches']:
 k=patch['path'];old=data['_provenance/v1/source/'+k];new=data['source/'+k];before,after=map(str.encode,patch['replacement'])
 assert sha(old)==patch['before'] and sha(new)==patch['after'] and old.count(before)==1 and old.replace(before,after)==new
old=data['_provenance/v1/admit.py'];new=data['admit.py'];assert sha(old)==d['old_driver_sha256'] and sha(new)==d['new_driver_sha256']
assert old.replace(d['old_manifest'].encode(),d['new_manifest'].encode()).replace(b'source_file_count=648',b'source_file_count=652')==new
for tag in ('base','extra'):
 assert data[f'source/new/borrow/delayed/PR3605-{tag}.json.gz']==(P/'sources'/f'STAGED644-660-{tag}.json.gz').read_bytes()
 assert data[f'source/new/borrow/words/BORROW-WORD-43{tag}.json.gz']==(P/'lead1-words'/f'DELAYED-{tag}.json.gz').read_bytes()
# New copied checker must differ from independently reviewed checker only in paths/pin checks.
old=(P/'reviews/lead1/check.py').read_text();new=data['source/new/borrow/review_delayed.py'].decode()
# Every mathematical function retained byte-for-byte.
assert old[old.index('def span'):old.index('rows=[]')]==new[new.index('def span'):new.index('rows=[]')]
print(json.dumps(dict(status='PASS_INDEPENDENT_V2_SOURCE_CLOSURE',commit='29b904054c67a40b140806698398a4af547f1d03',archive_sha256=sha(raw),files=len(data),v1_files=len(a),v2_files=len(b),modified=d['modified_files'],added=d['added_files'],scope='Exact archive closure, all predecessor source hashes reconstructible, exact declared text changes, original current word bytes retained; no terminal admission assertion.'),indent=2))
