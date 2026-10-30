"""Validate the fast BIT oracle against the PR's own native.replay on the published word + >=200 random mutants (TKAUDIT style).  run: python3 bitmut.py [ALIAS] [N] [SEED]"""
import sys,os,json,random,subprocess,tempfile,copy
sys.dont_write_bytecode=True
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
import bitword
alias=sys.argv[1] if len(sys.argv)>1 else 'bit5708'; N=int(sys.argv[2]) if len(sys.argv)>2 else 240; seed=int(sys.argv[3]) if len(sys.argv)>3 else 1
ctx=bitword.Ctx(alias); w=ctx.baseword; R=w['records']; rnd=random.Random(seed)
frames=sorted(ctx.dims)
def mut(kind):
    r=copy.deepcopy(R); n=len(r)
    def pick(ops):
        while True:
            i=rnd.randrange(n)
            if r[i][0] in ops: return i
    if kind=='q_rank': i=pick(('Q',)); r[i][4]=max(1,min(7,r[i][4]+rnd.choice((-1,1))))
    elif kind=='q_target': i=pick(('Q',)); r[i][3]=rnd.choice(frames)
    elif kind=='add_frame': i=pick(('ADD',)); r[i][3]=rnd.choice(frames)
    elif kind=='add_src': i=pick(('ADD',)); r[i][2]=rnd.randrange(ctx.width)
    elif kind=='drop_add': i=pick(('ADD',)); del r[i]
    elif kind=='drop_q': i=pick(('Q',)); del r[i]
    elif kind=='swap_adj': i=rnd.randrange(n-1); r[i],r[i+1]=r[i+1],r[i]
    elif kind=='swap_far': i=rnd.randrange(n); j=min(n-1,i+rnd.randrange(2,400)); r[i],r[j]=r[j],r[i]
    elif kind=='dup_add': i=pick(('ADD',)); r.insert(i,copy.deepcopy(r[i]))
    elif kind=='drop_erase': i=pick(('ERASE',)); del r[i]
    elif kind=='erase_frame': i=pick(('ERASE',)); r[i][2]=rnd.choice(frames+[None])
    elif kind=='move_add': i=pick(('ADD',)); e=r.pop(i); r.insert(max(0,min(len(r),i+rnd.randrange(-300,300))),e)
    return r
kinds=['q_rank','q_target','add_frame','add_src','drop_add','drop_q','swap_adj','swap_far','dup_add','drop_erase','erase_frame','move_add']
muts=[(kinds[i%len(kinds)],None) for i in range(N)]
words=[R]+[mut(k) for k,_ in muts]; labels=['PUBLISHED']+[k for k,_ in muts]
tmp=tempfile.mkdtemp(prefix='bitmut-'); inp=tmp+'/m.json'; out=tmp+'/o.json'; json.dump(words,open(inp,'w'))
pk=bitword.pkgdir(alias)
env={'PATH':'/usr/bin:/bin','HOME':tmp,'PYTHONDONTWRITEBYTECODE':'1'}
subprocess.run(['/opt/homebrew/bin/python3.12','-I','-B',HERE+'/bitmut_pr.py',pk,inp,out],env=env,cwd=tmp,timeout=3000)
pr=json.load(open(out)); rows=[]; agree=0; bad=[]
for lab,recs,v in zip(labels,words,pr):
    mine=bitword.check(dict(w,records=recs),ctx,3); a=(not mine); b=(v is None)
    rows.append(dict(kind=lab,fast_legal=a,pr_legal=b,fast=(mine[0][0] if mine else None),pr=v))
    if a==b: agree+=1
    else: bad.append(rows[-1])
from collections import Counter
print('mutants',len(words)-1,'agree',agree,'of',len(words)); print('PR-legal among mutants:',sum(r['pr_legal'] for r in rows[1:]),'fast-legal:',sum(r['fast_legal'] for r in rows[1:]))
print('disagreements:',len(bad)); 
for b in bad[:10]: print(' ',b)
print('by kind (pr_legal count):',Counter(r['kind'] for r in rows[1:] if r['pr_legal']))
json.dump(rows,open(os.path.join(HERE,'out','bitmut_%s.json'%alias),'w'),indent=1)
