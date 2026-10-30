"""Source-bound reuse of independently checked T360 owner journal, not a fresh journal replay."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
import gzip,hashlib,json,sys
P=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_bytes())
def span(bs):
 s={0}
 for b in bs:s|={x^b for x in tuple(s)}
 return s

def check(inputs):
 d=P/'sources/owner-transfer';receipt=read(d/'NATIVE-RECEIPT.json');pins=read(d/'EVIDENCE-PINS.json');owner=read(d/'INDEPENDENT-OWNERS.json')
 assert sha(d/'NATIVE-RECEIPT.json')==pins['files']['NATIVE-RECEIPT.json'] and sha(d/'INDEPENDENT-OWNERS.json')==pins['files']['INDEPENDENT-OWNERS.json']
 assert owner['status']=='PASS_INDEPENDENT_LITERAL_OWNER_WINDOWS_FAMILIES_PREFIXES_AND_INVOICE'
 assert (owner['replicas'],owner['calls'],owner['roles'],owner['physical'])==(360,3240,1321920,323069)
 for name in ['ORDER.json','DISPATCH.json']:
  assert [h for f,h in owner['input_sha256'].items() if f.endswith('/'+name)]==[sha(inputs/name)]
 # The original owner audit used the literal container; the admitted fill is
 # an authenticated semantic conversion differing only in dispatch_overrides.
 binding=read(d/'FILL-BINDING.json');assert sha(d/'FILL-BINDING.json')==pins['files']['FILL-BINDING.json']
 assert sha(inputs/'FILL.json.gz')==binding['admission_sha256'] and binding['semantic_equality'] is True
 assert [h for f,h in owner['input_sha256'].items() if f.endswith('/FILL.json.gz')]==[binding['literal_sha256']]
 payload=gzip.decompress((inputs/'FILL.json.gz').read_bytes())
 # The literal writer terminates its compact JSON with LF; the admission
 # conversion has the exact same bytes except that terminal LF.
 assert hashlib.sha256(payload+b'\n').hexdigest()==binding['literal_payload_sha256']
 native=read(inputs/'NATIVE-RECEIPT.json');L=None;vectors={}
 for tag in ('base','extra'):
  old=read(d/f'CANONICAL-{tag}.json.gz');new=read(inputs/'native-cache'/native['providers'][tag]['word_sha256']/'local/CANONICAL-WORD.json.gz')
  assert sha(d/f'CANONICAL-{tag}.json.gz')==receipt['providers'][tag]['complete_native_files']['local/CANONICAL-WORD.json.gz']
  assert old['helper_origin']==new['helper_origin'] and old['R']==new['R']==408 and old['zero_buffers']==new['zero_buffers'] and len(new['zero_buffers'])==91
  oldpairs=[(span(old['frames'][old['start'][224+i]]),span(old['frames'][old['final'][224+i]])) for i in range(408)]
  newpairs=[(span(new['frames'][new['start'][224+i]]),span(new['frames'][new['final'][224+i]])) for i in range(408)]
  assert oldpairs==newpairs
  widths=[len(b).bit_length()-len(a).bit_length() for a,b in newpairs];assert Counter(widths)=={4:26,5:2,6:18,7:52,8:97,9:213};vectors[tag]=widths
  assert L is None or L==new['local_profile'];L=new['local_profile']
 assert L=={'1':2437,'2':724,'3':226,'4':102,'5':20,'8':8}
 h=Counter({k:n*3240 for k,n in L.items()});h.update(owner['idle']);assert dict(h)==read(P/'LEAD1-PRICE.json')['profile']
 assert sum(int(r)*n for r,n in h.items())==65088*360
 return dict(status='PASS_EXACT_OWNER_WIDTH_AND_BILL_TRANSFER_WITH_EXPLICIT_JOURNAL_REUSE',roles=1321920,physical=323069,replicas=360,calls=3240,profile=dict(h),idle=owner['idle'],old_owner_receipt_sha256=sha(d/'INDEPENDENT-OWNERS.json'),new_native_receipt_sha256=sha(inputs/'NATIVE-RECEIPT.json'),scope='Same literal fill/order/dispatch and identical actual per-helper entrance/terminal subspaces preserve whole-call windows, family exclusion, offset/capacity and prefix obligations. New local native bill recomputed; no fresh independent million-row journal replay claimed. Original full global owner audit is separately rerun in the complete release.')
if __name__=='__main__':print(json.dumps(check(Path(sys.argv[1])),indent=2))
