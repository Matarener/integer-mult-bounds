"""New independent Python record semantics, geometry and five-stage882 columns.
Not a relabelled C++ checker receipt. Only the documented schema is supplied
to the unchanged parent emitter after these actual checks pass.
"""
from pathlib import Path
from collections import Counter
import json,struct,time,hashlib
import sys
H=Path(sys.argv[1]).resolve();t=time.process_time();rec=list(struct.iter_unpack('<6i',(H/'records/249-records.bin').read_bytes()));S=json.loads((H/'records/249-states.json').read_text());F=json.loads((H/'records/frames.json').read_text())['frames'];n=S['n'];v=S['v'];R=S['R'];cur=[S['initial'][str(i)]for i in range(n)]+[-1];hist=Counter();copies=erasures=adds=0;center=None;norm=[1]*n+[0];peak=1
def nested(a,b):return F[str(a)]['dim']<=F[str(b)]['dim']and all(sum(x*y for x,y in zip(r,s))==0 for r in F[str(a)]['B']for s in F[str(b)]['A'])
for op,d,s,c,f,z in rec:
 if op==0:
  assert cur[d]==s and nested(s,c)and F[str(c)]['dim']-F[str(s)]['dim']==f
  cur[d]=c
  if f:hist[f]+=1
 elif op==1:
  assert d!=s and d<n and cur[d]==cur[s]==f and(center is None or d!=center)
  assert s!=n or center is not None
  norm[d]+=abs(c)*norm[s];peak=max(peak,norm[d]);adds+=1
 elif op==2:
  assert center is None and s==n and cur[d]==c and z==F[str(c)]['dim']
  center=d;cur[n]=f;norm[n]=norm[d];copies+=1;hist[z]+=1
 else:
  assert op==3 and center==d and s==n and cur[d]==c and cur[n]==f
  center=None;cur[n]=-1;norm[n]=0;erasures+=1
assert copies==erasures==9 and center is None and cur[:n]==[S['final'][str(i)]for i in range(n)]
def prefix(reverse):
 nm=[1]*n+[0];largest=1;opened=False
 for op,d,s,c,f,z in (reversed(rec)if reverse else rec):
  if op==1:nm[d]+=abs(c)*nm[s];largest=max(largest,nm[d])
  elif op==(3 if reverse else 2):assert not opened;nm[n]=nm[d];opened=True
  elif op==(2 if reverse else 3):assert opened;nm[n]=0;opened=False
 assert not opened;return largest
pf=prefix(False);pb=prefix(True);payload=64*pf**3*pb**2;assert payload<1<<104,(pf,pb,payload.bit_length())
globaln=4*v+R;temp=globaln;a=[1<<i for i in range(globaln)]+[0];active=[(0,1),(1,0),(0,1),(3,2),(2,3)];bridges={1:[(0,2),(3,1)],2:[(3,1),(0,2)],4:[(1,3),(2,0)]}
for stage in range(5):
 rev=stage in [1,3];opened=False;cnt=0
 def role(r):return active[stage][0]*v+r if r<v else active[stage][1]*v+r-v if r<2*v else 4*v+r-2*v if r<n else temp
 for op,d,s,c,f,z in (reversed(rec)if rev else rec):
  if op==1:a[role(d)]^=(a[role(s)]if c&1 else 0)
  elif op==(3 if rev else 2):assert not opened and a[temp]==0;a[temp]=a[role(d)];opened=True;cnt+=1
  elif op==(2 if rev else 3):assert opened and a[temp]==a[role(d)];a[temp]=0;opened=False
 assert not opened and cnt==9
 if stage==0:assert all(a[i]==((1<<i)^((1<<(i-v))if v<=i<2*v else 0))for i in range(globaln))
 for d,s in bridges.get(stage,[]):
  for i in range(v):a[d*v+i]^=a[s*v+i]
for bank in [0,2]:
 for i in range(v):a[bank*v+i],a[(bank+1)*v+i]=a[(bank+1)*v+i],a[bank*v+i]
assert a==[1<<i for i in range(globaln)]+[0]
(H/'cout').mkdir(exist_ok=True)
leg=dict(status='PASS_INDEPENDENT_PYTHON_RECORD_GEOMETRY_COPY_LIFECYCLE',copies=copies,erasures=erasures,common_frame_ADDs=adds,records=len(rec),rank_mass=sum(r*c for r,c in hist.items()),paid_histogram=dict(hist),scope='New Python exact geometry/record audit, not a C++ receipt')
col=dict(status='PASS_INDEPENDENT_PYTHON_FIVE_STAGE_882_COLUMNS_AND_PREFIX',formal_columns_checked=globaln,local_scalar_additions=adds,local_raw_H=sorted(hist.items()),payload_prefix_bits=payload.bit_length(),forward_l1=pf,reverse_l1=pb,scope='Actual all882 F2 input columns, shared arbitrary438-helper dirt, COPY originals/WORK tested. Native parent realization remains inherited conditional.')
assert globaln==882
(H/'cout/legality.json').write_text(json.dumps(leg,indent=2)+'\n',encoding='utf-8');(H/'cout/columns.json').write_text(json.dumps(col,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(legality=leg,columns=col,cpu_seconds=time.process_time()-t),indent=2))
