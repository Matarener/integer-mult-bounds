"""New staged544 dirty-word contract and constructive rejection controls.
Retained independent interpreter: Sagar Thakrar, PR3687/3693, Apache-2.0.
New adapter: dataisfire with substantial OpenAI Codex assistance.
"""
from pathlib import Path
from copy import deepcopy
import gzip,json
import audit_core as C
from audit_verify import semantics
import stage544_applier as S
P=Path(__file__).resolve().parent

def need(ok,why):
 if not ok:raise ValueError(why)
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def rejects(name,fn):
 try:fn()
 except (ValueError,C.AuditFailure):return name
 raise ValueError('control accepted '+name)
def inspect(w):
 C.hygiene(w);bill,widths,_,_,_=C.frame_bill(w)
 need(bill=={1:2440,2:725,3:224,4:102,5:20,8:8},'actual profile')
 need(widths=={4:26,5:2,6:18,7:53,8:96,9:213},'actual widths')
 need(w['cleanup']==C.derive_cleanup(w),'literal cleanup')
 return semantics(C,w)
rows=[]
for tag in ('base','extra'):
 old=load(P/'staged544'/f'PRE-{tag}.json.gz');w=load(P/'words'/f'BORROW-WORD-43{tag}.json.gz')
 rec=json.loads((P/'staged544'/f'RECORD-{tag}.json').read_text());need(S.apply(old,rec)==w,'declared edit reconstructs')
 semantic=inspect(w);controls=[]
 for defect in ('omit_release','flip_release','old_entrance','wrong_bill'):
  bad=deepcopy(w)
  if defect in ('omit_release','flip_release'):
   k=next(i for i,g in enumerate(bad['B']) if g[0]=='add' and g[1:3]==[672,544] and g[3:5]==[1,2])
   if defect=='omit_release':
    bad['B'].pop(k)
    for r in bad['warps']:
     if r[0]>k:r[0]-=1
   else:bad['B'][k][3]*=-1
   # Re-derive cleanup so rejection cannot be an obsolete inverse mismatch.
   bad['cleanup']=C.derive_cleanup(bad)
   controls.append(rejects(defect,lambda:semantics(C,bad)))
  elif defect=='old_entrance':
   bad['start_extra']['544']=[51];controls.append(rejects(defect,lambda:inspect(bad)))
  else:
   bad['report']['local_profile']['1']+=1
   controls.append(rejects(defect,lambda:need(C.frame_bill(bad)[0]=={int(r):n for r,n in bad['report']['local_profile'].items()},'changed report')))
 badrec=deepcopy(rec);badrec['sections']['B'][0]['old'][0][3]+=1
 controls.append(rejects('wrong_literal_preimage',lambda:S.apply(old,badrec)))
 rows.append(dict(provider=tag,semantics=semantic,controls=controls))
print(json.dumps(dict(status='PASS_STAGED544_DIRTY_WORD_AND_CONTROLS',providers=rows),sort_keys=True),flush=True)
