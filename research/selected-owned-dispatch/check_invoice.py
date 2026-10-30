"""Independent observer-only exact boundary cost check."""
import json
from pathlib import Path
import prototype as p

def run(width, records, prefix):
 s,q=p.s,p.q
 counts=s.Counts()
 payloads=[s.Tape([1]*prefix,counts=counts) for _ in range(16)]
 control=s.Tape([0]*prefix,s.BASE,counts)
 descriptor=s.Tape([],s.BASE,counts)
 relays=[s.Tape([],s.BASE,counts) for _ in range(4)]
 depth=s.Tape([],s.BASE,counts)
 words=[p.bits([2,-1]*records,width),p.bits([-2,1]*records,width),[],
        [int(c) for c in bin(width)[2:][::-1]]+[q.RIGHT],
        [int(c) for c in bin(records)[2:][::-1]]+[q.RIGHT],[],[],[]]
 for t,word in zip(payloads,words):
  for bit in p.code([q.LEFT]+word):s.emit(t,bit)
  p.query_origin(t)
 dispatcher=p.Dispatcher(payloads,control,descriptor,relays,depth)
 p.execute(p.TABLES[0],dispatcher.ports)
 def extent(t):
  # Oracle only: origins obtained from actual nearest physical LEFT.
  origin=t.head-1
  while t.cells[origin]!=s.LEFT:origin-=1
  origin+=1
  end=origin
  while end<len(t.cells) and t.cells[end]!=s.BLANK:end+=1
  return end-origin,t.head-origin
 parent=[extent(t) for t in payloads]
 lz,lp,lm=[parent[i][0] for i in (q.Z,q.WD,q.MD)]
 before=counts.total
 dispatcher.descend()
 descent=counts.total-before
 p.execute(p.TABLES[0],dispatcher.ports)
 p.execute(p.TABLES[1],dispatcher.ports)
 child=[extent(t) for t in payloads]
 output=child[q.Y][0]
 before=counts.total
 dispatcher.ascend()
 ascent=counts.total-before
 sp,hp=sum(x[0] for x in parent),sum(x[1] for x in parent)
 w,hc=sum(x[0] for x in child),sum(x[1] for x in child)
 inherited=13*hp+4*sp+38*16+18*1+5*0+2*7+2*hc+5*w+17*output+61
 additional=34*lz+21*lp+21*lm+13*output+283
 s.need(descent+ascent==inherited+additional,'complete source-bound boundary invoice mismatch')
 return dict(p=width,records=records,prefix=prefix,Sp=sp,Hp=hp,W=w,Hc=hc,L=output,
             Lz=lz,Lp=lp,Lm=lm,inherited=inherited,additional=additional,
             descent=descent,ascent=ascent,total=descent+ascent)

def run_checks():
 return [run(w,m,x) for w in (5,9,17) for m in (1,2,4) for x in (0,17,257)]

if __name__ == '__main__':
 print(json.dumps(run_checks(),indent=2))
