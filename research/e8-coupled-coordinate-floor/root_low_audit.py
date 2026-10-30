"""Independent root-normal neighbor correction rank-seven boundary, conorholds."""
from independent_model import root_model, check_model, dot, binary_rank, require
from collections import Counter
import json

def run():
 rows,labels=root_model();check_model(rows,labels)
 v=0; ov={i for i,u in enumerate(labels) if (u&labels[v]).bit_count()%2}; hv=set(range(120))-ov
 oz=[0]+[sum(1<<i for i,u in enumerate(labels) if (u&z).bit_count()%2) for z in range(1,512)]
 hist=Counter();minimum=121;witness=None;planes=0
 for a,row in enumerate(rows):
  off=sum(1<<i for i,r in enumerate(rows) if dot(row,r))
  forced=sum(1<<i for i in ov if off>>i&1)
  chars=[z for z in range(1,512) if not forced&oz[z]]
  hist[len(chars)]+=1
  seen=set()
  for z in chars:
   for t in chars:
    if z>=t: continue
    key=tuple(sorted((z,t,z^t)))
    if key in seen: continue
    seen.add(key);planes+=1
    deleted=off&(oz[z]|oz[t]);count=deleted.bit_count()
    require(all(i in hv for i in range(120) if deleted>>i&1),'neighbor support')
    if count<minimum:
     minimum=count;witness={'root':a,'characters':key,'deleted':[i for i in range(120) if deleted>>i&1]}
 require(minimum==29,'root mixed weight-seven threshold29')
 return {'root_lines':120,'forced_character_counts':dict(hist),'planes':planes,'minimum_deletions_for_root_weight_at_most_seven':minimum,'witness':witness}
if __name__=='__main__': print(json.dumps(run(),sort_keys=True,indent=2))
