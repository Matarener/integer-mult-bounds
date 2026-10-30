# delivery floors per unit: direct node floor (pairs x best ratio) and multihop adds LB (FRAMECHK layer-cake), for P112 and sampled P104/P108 (random J removed from P112)
import random,math,subprocess,json,sys
from fractions import Fraction as F
P112=[int(x) for x in open('ports112.txt').read().split()]
pc=lambda x:bin(x).count('1')
def census(ports,tag):
    fn=f'ports_{tag}.txt'; open(fn,'w').write(' '.join(map(str,ports)))
    out=subprocess.run(['./cen2',fn],capture_output=True,text=True).stdout.split('\n')
    res={'D':{},'B':{}}
    for l in out:
        t=l.split()
        if not t: continue
        if t[0]=='n': res['n']=int(t[1]); res['pairs']=int(t[3])
        elif t[0]=='D': res['D'][int(t[1])]=(float(t[2]),int(t[3]),int(t[4]))
        elif t[0]=='B': res['B'][int(t[1])]=int(t[2])
    ports=list(ports)
    res['Nj']=[sum(1 for q in ports if q!=p and not pc(p&q)&1) for p in ports]
    return res
def direct(res):
    best=min(v[0] for v in res['D'].values()); return best,res['pairs']*best
def hop(res):
    n=res['n']; Bm=res['B']; B={}; cur=0
    for h in range(n,0,-1):
        cur=max(cur,Bm.get(h,0)); B[h]=cur
    tot=F(0)
    for L in res['Nj']:
        w=[F(0)]*(L+1)
        for h in range(2,L+1): w[h]=F(1,max(1,B[h]))
        lb=F(0)
        for t in range(2,L+1): lb+=(w[t]-w[t-1])*(math.ceil(L/(t-1))-1)
        tot+=lb
    return float(tot)
if __name__=='__main__':
    random.seed(1)
    out={}
    r=census(P112,'112'); out['P112']=[{'direct_ratio':direct(r)[0],'direct_total':direct(r)[1],'hopLB':hop(r),'pairs':r['pairs'],'meanNj':sum(r['Nj'])/len(r['Nj'])}]
    for name,k in (('P108',4),('P104',8)):
        out[name]=[]
        for s in range(int(sys.argv[1]) if len(sys.argv)>1 else 12):
            J=set(random.sample(range(112),k)); ports=[p for i,p in enumerate(P112) if i not in J]
            r=census(ports,f'{name}_{s}')
            out[name].append({'direct_ratio':direct(r)[0],'direct_total':direct(r)[1],'hopLB':hop(r),'pairs':r['pairs'],'meanNj':sum(r['Nj'])/len(r['Nj'])})
    json.dump(out,open('floors.json','w'),indent=1)
    for k,v in out.items():
        for key in ('direct_ratio','direct_total','hopLB','pairs'):
            xs=[x[key] for x in v]; print(k,key,min(xs),max(xs))
