import os
import json,sys
sys.path.insert(0,'.')
from bitval import *
inv=json.load(open(os.path.dirname(os.path.abspath(__file__)) + '/ext/BITADAPT/pkg/research/bit-g20-nine-owned-relations/INVOICE.json'))
T,P=from_pr_invoice(inv); k0=crossing(T,P)
def d(T2,P2): return crossing(T2,P2)-k0
out={'k0':mp.nstr(k0,15),'paid':{},'target':{}}
for r in sorted(P):
    P2=dict(P); P2[r]-=1; one=d(T,P2)
    P3=dict(P); P3[r]-=18; loc=d(T,P3)
    P4=dict(P); P4[r]=0; allr=d(T,P4)
    out['paid'][r]=dict(count=P[r],per_query=float(one),per_local_event_x18=float(loc),remove_all=float(allr))
for r in sorted(T):
    T2=dict(T); T2[r]+=1; out['target'][r]=dict(count=T[r],per_target_plus1=float(d(T2,P)),per_18=float(d({**T,r:T[r]+18},P)))
# step to next 1e-8 tested boundary
nxt=(int(k0*10**8)+1)/mpf(10**8); out['gap_to_next_1e-8_step']=float(nxt-k0)
# combos
comb={}
# removing the nine rank-7 local owned captures' relatives: one more owned relation = -18 T8 , -18 P7 (rank-7 paid) ?
comb['tenth_relation_(-18 T8,-18 P7,-18P1?)']=float(d({**T,8:T[8]-18},{**P,7:P[7]-18}))
comb['T8-18_only']=float(d({**T,8:T[8]-18},P))
# local rank-k Q -> rank j lowering e.g. a rank-2 paid becomes rank-1
for a,b in((2,1),(3,2),(3,1),(4,3),(5,4),(7,6),(7,5),(7,4)):
    comb['local_paid_%d->%d'%(a,b)]=float(d(T,{**P,a:P[a]-18,b:P.get(b,0)+18}))
out['combos']=comb
# continuous admitted equivalent: total gain needed to reach next boundary
print(json.dumps(out,indent=1))
print('relative: per query rank1 / kappa =',out['paid'][1]['per_query']/float(k0))
