"""Fixed BCCB cache/loop screen, not a complete performance benchmark."""
import json,time
from fractions import Fraction as F
import slot_parent
import fraction_table as table
import native_backend
from frozen import require

def main():
    native_backend.load();weights=[(F(2),F(3)),(F(5),F(7))];tokens=[0,1]
    results=[];count=65536
    for label,cls in [('B',slot_parent.CompactContributions),('C',table.CompactContributions),('C',table.CompactContributions),('B',slot_parent.CompactContributions)]:
        c=cls(16384,weights,tokens);step=c.event(F(1));total=F(0)
        cpu=time.process_time();wall=time.perf_counter()
        for i in range(count):total+=step(F(0),F(i%4),i%2)[1]
        results.append(dict(label=label,wall_seconds=time.perf_counter()-wall,cpu_seconds=time.process_time()-cpu,total=str(total),statistics=c.statistics()))
    require(all(r['total']==results[0]['total'] and r['statistics']==results[0]['statistics'] for r in results),'all complete micro outputs/counters')
    print(json.dumps(dict(status='PASS_NATIVE_MICRO_SCREEN_ONLY',fixed_order='BCCB',updates_per_arm=count,results=results,build=native_backend.receipt()),sort_keys=True))

if __name__=='__main__':main()
