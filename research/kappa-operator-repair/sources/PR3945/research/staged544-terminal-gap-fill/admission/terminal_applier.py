"""Explicit terminal-frame derivative of the retained staged544 word.
Dugongue with OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
import hashlib,json
import audit_core as C
def canonical(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def opcode(g):
 if g[0]=='warp':return tuple(g[:3])
 return tuple(g[:-1])
def operations(seq):return [opcode(g) for g in seq if not(g[0]=='scale' and g[2]==g[3])]
def apply(old,record):
 need(canonical(old)==record['source_canonical_sha256'],'terminal source preimage')
 allowed={'A','B','restore','warps','helper_final','report','cleanup'};need(set(record['new_fields'])<=allowed,'terminal changed field contract');w=deepcopy(old);w.update(deepcopy(record['new_fields']))
 for sec in ['A','B','restore']:need(operations(old[sec])==operations(w[sec]),'terminal scalar/warp operator preservation')
 need(len(w['warps'])==len(old['warps']) and all(a[1:3]==b[1:3] for a,b in zip(old['warps'],w['warps'])),'terminal native identities/maps')
 changed=[r for r in old['helper_final'] if old['helper_final'][r]!=w['helper_final'][r]];need(set(old['helper_final'])==set(w['helper_final']) and len(changed)==26,'terminal26 declared endpoints')
 for r in changed:need(len(w['helper_final'][r])==len(old['helper_final'][r])+1 and len(old['helper_final'][r])-len(old['start_extra'].get(r,[]))==4,'terminal4-to5 return widths')
 C.hygiene(w);bill,widths,*_=C.frame_bill(w,lagrangian=True);need(bill=={int(r):n for r,n in w['report']['local_profile'].items()},'terminal actual paid bill');need(widths=={int(r):n for r,n in w['report']['width_inventory'].items()},'terminal actual inventory');need(w['cleanup']==C.derive_cleanup(w),'terminal literal cleanup');need(canonical(w)==record['candidate_canonical_sha256'],'terminal exact candidate content');return w
