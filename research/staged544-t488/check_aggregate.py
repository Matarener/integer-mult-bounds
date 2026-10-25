"""Standard-library exact integer aggregate checker; no optimizer or inherited receipt."""
from pathlib import Path
import gzip,json,hashlib,argparse,sys
if not __debug__ or sys.flags.optimize:raise RuntimeError("Enabled assertions required")
from collections import Counter
ap=argparse.ArgumentParser();ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--out',type=Path);args=ap.parse_args();src=args.certificate;d=json.loads(gzip.decompress(src.read_bytes()));S=d['S'];G=d['groups'];W=d['widths'];C=len(d['order']);assert C==9*d['baseT'];assert d['T']==S*d['baseT'];assert sorted(map(tuple,d['order']))==[(s,r)for s in range(9)for r in range(d['baseT'])];bins=Counter();slots=Counter();supply=Counter();demand=Counter();degree=Counter();idle=Counter()
for g,q,n in d['x']:
 assert type(n)is int and n>0 and all(type(k)is int and k>=0 for k in q)and len(q)==len(W);cap,lo,hi,num=G[g];r=cap-sum(w*k for w,k in zip(W,q));assert r>=0;bins[g]+=n;idle[r]+=n
 for w,k in zip(W,q):slots[g,w]+=n*k
for g,t,w,n in d['z']:
 assert type(n)is int and n>0 and w in W and 0<=t<C;cap,lo,hi,num=G[g];assert lo<t<=hi;supply[g,w]+=n;demand[t,w]+=n;degree[g,t]+=n
assert all(bins[g]==num*S for g,(cap,lo,hi,num)in enumerate(G));assert supply==+slots
assert all(demand[t,w]==S*d['inventory'][str(w)]for t in range(C)for w in W);assert all(n<=G[g][3]*S for(g,t),n in degree.items())
profile=Counter({int(r):n*C*S for r,n in d['local_profile'].items()});profile.update({r:n for r,n in idle.items()if r});assert dict(profile)=={int(r):n for r,n in d['profile'].items()};assert sum(r*n for r,n in profile.items())==65088*d['T']
out={'status':'PASS_EXACT_INTEGER_AGGREGATE','replicas':d['T'],'S':S,'pattern_rows':len(d['x']),'flow_rows':len(d['z']),'profile':dict(profile),'pins':{str(q):hashlib.sha256(q.read_bytes()).hexdigest()for q in[src,Path(__file__)]},'scope':'Exact aggregate counts,windows,permacrocallgroupdegree andinvoice. Notcopycoloring/physicalownership/outeradmission.'};print(json.dumps(out,sort_keys=True))
if args.out:args.out.write_text(json.dumps(out,indent=2)+'\n')
