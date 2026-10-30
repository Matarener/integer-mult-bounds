"""R16 lever ceilings on the selected #5413 profile (numerical screens, Decimal 50 digits)."""
import sys; sys.path.insert(0, __file__.rsplit('/',1)[0])
from price16 import *
U = D('0.00302728825')
base = root()
HCL = {1:1513,2:201,3:432,4:50,5:12}          # per-local helper climbs (#4610 word, r13 sec.3)
LOC = {1:2201,2:412,3:510,4:127,5:40}        # per-local non-centre paid (centre = 8 x rank 8 separate)
MCL = {k: LOC.get(k,0)-HCL.get(k,0) for k in LOC}  # main x/y climbs
assert sum(k*v for k,v in MCL.items()) == 224*8
HEL = {4:28,7:7,8:47,9:326}
def x18(h, s=1): return {k: s*18*v for k,v in h.items()}
cases = {
 'one helper split 9->4+5 (all 18 locals)': (add(T0,{9:-18,4:18,5:18}), P0),
 'all rank-9 helpers split 4+5': (add(T0,{9:-5724,4:5724,5:5724}), P0),
 'helpers credited per climb (helper defragmentation ceiling)': (add(add(T0, x18(HEL,-1)), x18(HCL)), P0),
 'one 1+1->2 helper visit merge (all 18 locals)': (T0, add(P0,{1:-36,2:18})),
 'main x/y single rank-8 climb (main defragmentation ceiling)': (T0, add(add(P0, x18(MCL,-1)), {8:18*224})),
 'query/local fusion 1680 x (1+1->2)': (T0, add(P0,{1:-3360,2:1680})),
 'free observation: delete all 1680 query shears': (T0, add(P0,{1:-1680})),
 'delete one rank-1 per local (18)': (T0, add(P0,{1:-18})),
 'paid 4+4->3+5 once per local': (T0, add(P0,{4:-36,3:18,5:18})),
 'centre: 8 rank-8 per local merged to rank-144 (contested)': (T0, add(P0,{8:-144,144:8})),
 'centre removed (contested, #4659)': (T0, add(P0,{8:-144})),
}
print('base root', base, ' U', U)
for name,(T,P) in cases.items():
    r = root(T,P)
    print(f'{name:62s} root {float(r):.10f}  dC {float(r-base):+.3e}  beats U: {r>U}')
