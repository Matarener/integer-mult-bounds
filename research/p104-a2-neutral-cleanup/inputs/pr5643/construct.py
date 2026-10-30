"""Construct a complete P104 A2 paid-rank exchange against exact PR5627 bytes.

Retains Ali Romman's P104 local checker and all predecessor notices. The A2
identity and complete-boundary discipline are credited to Chris R/Clear1nsight
(PR3998), ToikY(PR4019), and the scoped audits(PR4112/4152). New P104 witness,
construction and checks with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import argparse,gzip,importlib.util,json,sys
HERE=Path(__file__).resolve().parent
SOURCE_WORD='162e6f13a6e3805517946309bd6247eaa45b337ab9c39621806b254b415075ec'
SOURCE_CHECKER='716d01a342467f87b14d67853d8de30740f9f2fa881afe271db0df5ef8b19697'
EXPECTED='c7545eab4e1394ba942a7ac8e4d70860d172cabda151a559fd566478aa38204b'
def need(ok,why):
 if not ok:raise ValueError(why)
def construct():
 for rel,digest in [('inputs/pr5627-WORD.json.gz',SOURCE_WORD),('inputs/pr5627-local.py',SOURCE_CHECKER)]:
  need(sha256((HERE/rel).read_bytes()).hexdigest()==digest,'Exact source pin '+rel)
 spec=importlib.util.spec_from_file_location('retained_p104_checker',HERE/'inputs/pr5627-local.py');L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)
 w=json.loads(gzip.decompress((HERE/'inputs/pr5627-WORD.json.gz').read_bytes()));v=deepcopy(w)
 need(w['program'][14975]==['ADD',388,715,'-4',825] and w['program'][14977]==['ADD',340,388,'1',825],'Literal old pair')
 need(w['program'][14976]==['MOVE',340,396,825,False],'Only the declared intermediate transport')
 replacement=[['ADD',340,715,'-4',396],['ADD',340,388,'1',825],['ADD',388,715,'-4',127]]
 need([w['frames'][f]for f in[396,825,127]]==[[13,70,416],[7,10,32,65,144,272],[1,2,4,8,16,32,64,128,256]],'Exact existing frames')
 scalar=[]
 for i,e in enumerate(w['program']):
  if i==14975:scalar.extend(replacement)
  if i not in(14975,14977) and e[0]!='MOVE':scalar.append(e[:])
 frames=[L.span(b)for b in w['frames']];n=w['public'];current=w['initial']+[None]*w['owned_fields'];active=set();out=[]
 def move(r,f):
  a=current[r]
  if a==f:return
  private=r in active
  need(a is not None and (frames[f]<frames[a]if private else frames[a]<frames[f]),'Strict nested typed transport')
  out.append(['MOVE',r,a,f,private]);current[r]=f
 for e in scalar:
  op,r=e[:2]
  if op=='INIT':need(current[r]is None,'Owned slot available');active.add(r);current[r]=e[2]
  elif op=='CLEAR':move(r,e[2]);active.remove(r);current[r]=None
  else:
   move(r,e[-1])
   if op!='SCALE':move(e[2],e[-1])
  out.append(e)
 for r in range(n):move(r,w['final'][r])
 v['program']=out;v['schema']='p104-a2-paid-rank-exchange/1'
 before,after=L.replay(w),L.replay(v)
 delta=Counter(after['paid']);delta.subtract(before['paid']);delta={r:c for r,c in delta.items()if c}
 need(delta=={2:1,3:-1,5:-1,6:1},'Exact full paid-rank exchange')
 need(before['helpers']==after['helpers'],'Every target retained')
 need(after['real_scalar_allowance']-before['real_scalar_allowance']==12,'Correction ADD fully counted')
 payload=(json.dumps(v,separators=(',',':'))).encode()
 need(sha256(payload).hexdigest()==EXPECTED,'Entire regenerated candidate payload')
 need(gzip.decompress((HERE/'WORD.json.gz').read_bytes())==payload,'Exact saved candidate')
 return payload,{'status':'PASS_P104_A2_PAID_RANK_EXCHANGE','paid_delta':delta,'target_delta':{},'local':after,'source_local':before,'candidate_decompressed_sha256':EXPECTED}
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path);args=ap.parse_args();payload,result=construct()
 if args.out:
  with args.out.open('xb')as f:f.write(gzip.compress(payload,mtime=0))
 print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__':main()
