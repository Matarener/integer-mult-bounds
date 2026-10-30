"""Literal pinned frame/gate edits; no optimizer is needed to replay them."""
import copy,gzip,hashlib,json
from pathlib import Path

def canonical(w):return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def need(ok,why):
 if not ok:raise ValueError(why)
def apply(parent,record):
 need(canonical(parent)==record['source_canonical_sha256'],'source canonical digest')
 w=copy.deepcopy(parent)
 for sec,edits in record['sections'].items():
  need(sec in ('A','B','restore'),'scalar section')
  old=parent[sec];out=[];cursor=0
  for edit in edits:
   a,b=edit['slice'];need(cursor<=a<=b<=len(old),'ordered slice')
   need(old[a:b]==edit['old'],'literal scalar preimage')
   out+=copy.deepcopy(old[cursor:a])+copy.deepcopy(edit['new']);cursor=b
  w[sec]=out+copy.deepcopy(old[cursor:])
 need(parent['start_extra']['544']==[51] and '544' not in parent['helper_final'],'ordinary helper544 entrance')
 w['start_extra']['544']=[414,51]
 need(len(parent['warps'])==len(record['warps']),'warp inventory')
 need(all(a[1:3]==b[1:3] for a,b in zip(parent['warps'],record['warps'])),'native identities and maps preserved')
 w['warps']=copy.deepcopy(record['warps']);w['report'].update(copy.deepcopy(record['report']))
 from staged_pair import cleanup
 w['cleanup']=cleanup(w)
 need(canonical(w)==record['target_canonical_sha256'],'target canonical digest')
 return w
