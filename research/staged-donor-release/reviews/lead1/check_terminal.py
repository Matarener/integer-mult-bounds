"""Independent bounded terminal linkage and exact numeric checks."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import hashlib,json,tarfile
P=Path(__file__).resolve().parents[2];D=P/'evidence/complete'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
assert sha(P/'REPLAY-INPUTS.tar.gz')=='fa4222b179c2b16c197620c4000781faa5f2364384e60ef623a95e88487677c8'
pins=read(D/'PINS.json')['files'];assert set(pins)=={p.name for p in D.iterdir() if p.is_file() and p.name!='PINS.json'}
for n,h in pins.items():assert sha(D/n)==h
r=read(D/'RESULT.json');release=read(D/'RELEASE-RECEIPT.json');manifest=read(D/'PACKAGE-MANIFEST.json');pr=read(P/'LEAD1-PRICE.json');ind=read(D/'INDEPENDENT.json');inv=read(D/'PREFIX-AND-INVOICE.json');assembly=read(D/'ASSEMBLY.json');outer=read(D/'OUTER-LEDGER.json')
for label in ('STRICT','VERIFY'):
 for s in read(D/(label+'-STAGES.json')):
  assert s['exit_code']==0
  if 'log_sha256' in s:assert sha(D/(label+'-'+s['name']+'.txt'))==s['log_sha256']
for s in r['stages']:
 assert s['exit_code']==0
 logfile='RELEASE-V2.txt' if s['name']=='release' else 'PREP-'+s['name']+'.txt'
 assert sha(D/logfile)==s['log_sha256']
 rel=s['command'][2].split('/package/')[-1] if '/package/' in s['command'][2] else 'replay.py'
 assert manifest[rel]==s['script_sha256']
assert r['package_manifest_sha256']==release['manifest_sha256']==sha(D/'PACKAGE-MANIFEST.json')
assert r['release_receipt_sha256']==sha(D/'RELEASE-RECEIPT.json')
assert r['profile']==pr['profile']==ind['profile']==assembly['complex_profile']==outer['profile']
H=Counter({k:n*3240 for k,n in next(iter(ind['local_profiles'].values())).items()});H.update(ind['idle']);assert dict(H)==r['profile']
assert sum(int(k)*n for k,n in H.items())==65088*360
assert ind['roles']==ind['checked_whole_helper_widths']==ind['checked_busy_family_windows']==1321920
assert ind['physical']==inv['physical']==896*360+408+8+91+2==323069
bn=inv['blocknorm'];assert bn['actual_prefix_bits']==95+37+18+1323+1+4==1478
assert bn['required_reserve_bits']==128+37+18+1323+1+4==1511<bn['retained_payload_bits']==2048
assert ind['prefix_bits']==inv['global_prefix_bits']==1478 and ind['charged_prefix_bits']==2048
C=Q(pr['root_interval'][0]);K=C-Q(1,10**46)-Q(1,10**70)
assert C==Q(assembly['complex_lower'])==Q(outer['complex_lower_pinned']['rational'])<Q(assembly['bit_lower'])
assert K==Q(r['kappa'])==Q(r['kappa_decimal'])==Q(release['kappa_decimal'])
row=outer['rows']['struct_boundary_radix_union'];assert Q(row['kappa']['rational'])==K
assert all(Q(v['rational'])>0 for v in row['margins'].values())
assert len(outer['rejecting_controls']['struct_boundary_radix_union'])==17
assert Q(outer['native_moment'][1]['rational'])<1
assert K>Q(read(P/'sources/T360-PRICE.json')['root_interval'][1])
with tarfile.open(P/'REPLAY-INPUTS.tar.gz') as tf:
 source=json.load(tf.extractfile('source/MANIFEST.json'))
 assert hashlib.sha256(tf.extractfile('source/MANIFEST.json').read()).hexdigest()==r['source_manifest_sha256']
 for tag in ('base','extra'):
  key=f'new/borrow/words/BORROW-WORD-43{tag}.json.gz';assert source[key]==sha(P/'lead1-words'/f'DELAYED-{tag}.json.gz')
print(json.dumps(dict(status='PASS_INDEPENDENT_TERMINAL_BINDING',commit='a3bdc591920a4b9003d8442d1fcca24218153661',stored_files=len(pins),roles=ind['roles'],physical=ind['physical'],actual_prefix_bits=1478,reserve=1511,paid=2048,kappa=str(K),scope='Authenticated stored complete execution and exact numeric linkage; not a new heavy native/global replay.'),indent=2))
