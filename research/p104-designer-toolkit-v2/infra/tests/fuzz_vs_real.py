"""Cross-validate legal.check against the REAL PR5544 local.replay on random mutations of the P104 word (agreement on accept/reject).
usage: python fuzz_vs_real.py N [seed]"""
import os
import sys,copy,random,gzip,json,time
sys.path.insert(0,__file__.rsplit('/',2)[0])
import legal
REAL=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + '/ext/AUDIT5544/src/r/research/p104-productive-controller'
sys.path.insert(0,REAL); sys.dont_write_bytecode=True
import local as L
w0=legal.load(REAL+'/WORD.json.gz'); N=int(sys.argv[1]); rnd=random.Random(int(sys.argv[2]) if len(sys.argv)>2 else 1)
def mutate(w):
    w=copy.deepcopy(w); p=w['program']; k=rnd.choice(['swap','drop','frame','coef','move_frame','dup','owned_order','final'])
    i=rnd.randrange(len(p))
    if k=='swap': j=min(len(p)-1,i+rnd.randrange(1,30)); p[i],p[j]=p[j],p[i]
    elif k=='drop': del p[i]
    elif k=='dup': p.insert(i,list(p[i]))
    elif k=='frame':
        e=p[i]
        if e[0] in('ADD','COPY','SCALE'): e[-1]=rnd.randrange(len(w['frames']))
    elif k=='move_frame':
        mv=[x for x in p if x[0]=='MOVE']; e=rnd.choice(mv); e[3]=rnd.randrange(len(w['frames']))
    elif k=='coef':
        e=p[i]
        if e[0] in('ADD','COPY','SCALE'): e[-2]=rnd.choice([3,-3,'1/3','5/2',0,2])
    elif k=='owned_order':   # move an INIT early
        ii=[x for x,e in enumerate(p) if e[0]=='INIT']; a=rnd.choice(ii); e=p.pop(a); p.insert(max(0,a-rnd.randrange(1,3000)),e)
    elif k=='final': w['final'][rnd.randrange(len(w['final']))]=rnd.randrange(len(w['frames']))
    return k,w
agree=0;dis=[];t=time.time();stats={}
for n in range(N):
    k,w=mutate(w0)
    mine=legal.check(w)['ok']
    try: L.replay(w); real=True
    except Exception as e: real=False
    except BaseException as e: real=False
    stats.setdefault(k,[0,0]); stats[k][0]+=1
    if mine==real: agree+=1; stats[k][1]+=1
    else: dis.append((k,mine,real))
print('N',N,'agree',agree,'disagree',dis,'by kind [n,agree]',stats,'%.0fs'%(time.time()-t))
