"""Supplemental exact noncommuting 2x2 oracle; imports no primary checker.

Finite specializations calibrate parser/order conventions, not the free-group proof.
Tekalign with substantial OpenAI Codex assistance. Apache-2.0.
"""
import gzip,json,hashlib
from pathlib import Path
from fractions import Fraction as F
P=Path(__file__).resolve().parent

def need(ok,msg):
    if not ok:raise ValueError(msg)

def matrix(k):
    a=abs(k)%5+1
    # Alternating shears are invertible and do not mutually commute.
    m=(1,a,0,1) if abs(k)%2 else (1,0,a,1)
    if k<0:return (m[3],-m[1],-m[2],m[0])
    return m

def execute(w,seed):
    regs=sorted(set(range(704))-set(w['removed']))+[int(h)+704 for h in w['helper_final']]
    initial={r:(F((r*seed+7)%97-48),F((r*r+seed)%89-44)) for r in regs}
    v=dict(initial)
    def warp(r,k):
        a,b,c,d=matrix(k);x,y=v[r];v[r]=(a*x+b*y,c*x+d*y)
    def gate(g):
        if g[0]=='add':
            _,r,s,a,b,*_=g;q=F(a,b);v[r]=tuple(x+q*y for x,y in zip(v[r],v[s]))
        elif g[0]=='scale':
            _,r,a,b,*_=g;v[r]=tuple(F(a,b)*x for x in v[r])
        else:need(g[0]=='warp','unknown');warp(g[1],g[2])
    for c in w['initial_corrections']:
        z=v[c['source']]
        for k in reversed(c['operator_word']):
            a,b,c0,d=matrix(k);x,y=z;z=(a*x+b*y,c0*x+d*y)
        r=c['target'];q=F(c['coefficient']);v[r]=tuple(x+q*y for x,y in zip(v[r],z))
    for s in ('precondition','compensation','A','cut'):
        for g in w[s]:gate(g)
    for i in range(len(w['B'])+1):
        for j,x in enumerate(w['warps']):
            if x[0]==i:warp(x[1],j+1)
        if i<len(w['B']):gate(w['B'][i])
    for g in w['restore']:gate(g)
    boundary=dict(v)
    for g in w['cleanup']:gate(g)
    for r,z in initial.items():
        e=tuple(x+y for x,y in zip(z,initial[r-112])) if 112<=r<224 else z
        need(v[r]==e,'numeric endpoint '+str(r))
    return initial,boundary

def main():
    pins=json.loads((P/'PINS.json').read_text());cases=0
    for tag in ('base','extra'):
        words=[]
        for k in ('OLD','NEW'):
            name=k+'-'+tag+'.json.gz';raw=(P/'inputs'/name).read_bytes()
            need(hashlib.sha256(raw).hexdigest()==pins[name]['sha256'],'source pin');words.append(json.loads(gzip.decompress(raw)))
        for seed in (69,70,71):
            init,old=execute(words[0],seed);_,new=execute(words[1],seed)
            expected={417:tuple((x+y)/2 for x,y in zip(init[608],init[609])),
                      565:tuple(x/2 for x in init[600]),602:tuple(-x for x in init[600]),
                      610:tuple(-x-y for x,y in zip(init[608],init[609]))}
            for r in old:need(tuple(x-y for x,y in zip(new[r],old[r]))==expected.get(r,(0,0)),'numeric defect '+str(r))
            cases+=1
    # Actual neighboring native symbols do not accidentally commute in this oracle.
    def mul(a,b):return (a[0]*b[0]+a[1]*b[2],a[0]*b[1]+a[1]*b[3],a[2]*b[0]+a[3]*b[2],a[2]*b[1]+a[3]*b[3])
    need(mul(matrix(1),matrix(2))!=mul(matrix(2),matrix(1)),'commuting oracle')
    print('PASS_NONCOMMUTING_STAGING_ORACLE cases='+str(cases)+' complete_original_cleanup=true')
if __name__=='__main__':main()
