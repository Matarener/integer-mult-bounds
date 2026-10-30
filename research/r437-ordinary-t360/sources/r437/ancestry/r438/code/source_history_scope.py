"""Distinguish unchanged SOURCE access/clean history from new dirty propagation."""
from pathlib import Path
import json,gzip
import sys
H=Path(sys.argv[1]).resolve();I=Path(__file__).resolve().parents[1]/'data'
read=lambda n:json.loads(gzip.decompress((I/n).read_bytes()))
def trace(w):
 v=w['v'];a=[1<<i for i in range(2*v+w['R'])];out=[]
 for sec in ('D','A','B','C'):
  if sec=='B':
   cap=[a[r] for r in w['ret']]
   for t,js in enumerate(w['scatter']):
    for j in js:a[v+t]^=cap[j]
  for f,d,ss in w[sec]:
   for s in ss:a[d]^=a[s]
   if d<v:out.append((sec,f,d,ss,a[d]))
 return out
old=trace(read('SELECTED589.json.gz'));new=trace(read('r0028/FINAL-R438-WORD.json.gz'))
assert len(old)==len(new)==966
drop=lambda r:(r&((1<<464)-1))|((r>>465)<<464)
counts={};diff={}
for a,b in zip(old,new):
 sec,f,d,ss,row=a;s2,f2,d2,ss2,row2=b
 assert (sec,f,d)==(s2,f2,d2)
 assert [s-int(s>464) for s in ss]==ss2
 assert row&((1<<111)-1)==row2&((1<<111)-1)
 counts[sec]=counts.get(sec,0)+1
 if drop(row)!=row2:diff[sec]=diff.get(sec,0)+1
out={'status':'PASS_SOURCE_ACCESS_AND_CLEAN_HISTORY_SCOPE',
 'SOURCE_write_events':counts,'same_write_frames_destinations_and_remapped_operands':True,
 'same_clean_SOURCE_projection_after_each_write':True,
 'full_dirty_response_differences_after_restricting_old_removed_DIRTY_column':diff,
 'interpretation':'RESULT SOURCE_write_history_unchanged means the write access schedule and clean SOURCE rows. It does NOT claim all intermediate full SOURCE VALUE/DIRTY rows equal selected589. New dirty propagation is allowed and checked by fresh D0 and full660 final restoration.',
 'no_new_SOURCE_access_assumption':True}
with (H/'SOURCE-HISTORY-SCOPE.json').open('x',encoding='utf8') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps(out))
