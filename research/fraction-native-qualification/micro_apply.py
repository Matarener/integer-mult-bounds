"""Fixed complete coefficient-loop comparison, separate from cache-only screen."""
import json,time
from fractions import Fraction as F
import slot_parent
import fraction_table as table
import native_backend
from frozen import require

native_backend.load();n=128;repetitions=512
weights=[(F(i%5,4),F(i%7,8)) for i in range(n)];tokens=table.weight_tokens(weights)
src={i:F(i%5-2,2) for i in range(n)};old={i:F(i%3-1,4) for i in range(n)}
results=[]
for label in 'BCCB':
    cls=slot_parent.CompactContributions if label=='B' else table.CompactContributions
    c=cls(16384,weights,tokens);step=c.event(F(1,2));checksum=F(0)
    cpu=time.process_time();wall=time.perf_counter()
    for k in range(repetitions):
        dst=dict(old);scores=[F(0),F(0),F(0)]
        if label=='C':step.apply(dst,src,scores)
        else:
            for i,v in src.items():
                value,a,b,change=step(dst.get(i,F(0)),v,i)
                scores[0]+=a;scores[1]+=b;scores[2]+=change
                if value:dst[i]=value
                else:dst.pop(i,None)
        checksum+=scores[0]+scores[1]+scores[2]
    results.append(dict(label=label,wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu,checksum=str(checksum),last_row={str(i):str(v) for i,v in dst.items()},last_scores=list(map(str,scores)),statistics=c.statistics()))
require(all({k:v for k,v in r.items() if k not in ('label','wall_seconds','cpu_seconds')}=={k:v for k,v in results[0].items() if k not in ('label','wall_seconds','cpu_seconds')} for r in results),'full apply micro equality/counters')
print(json.dumps(dict(status='PASS_NATIVE_APPLY_MICRO_ONLY',fixed_order='BCCB',updates_per_arm=n*repetitions,results=results,build=native_backend.receipt()),sort_keys=True))
