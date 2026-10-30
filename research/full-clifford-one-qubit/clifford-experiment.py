from fractions import Fraction as F
import json

# Gaussian integers are pairs; all group matrices are represented as 2U.
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def neg(a): return (-a[0],-a[1])
def conj(a): return (a[0],-a[1])
def mul(a,b): return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
def power(a,n):
    z=(1,0)
    for _ in range(n): z=mul(z,a)
    return z
def mm(a,b):
    c=tuple(add(mul(a[2*i],b[j]),mul(a[2*i+1],b[2+j])) for i in range(2) for j in range(2))
    if not all(x%2==0 and y%2==0 for x,y in c): raise ValueError('nonintegral product')
    return tuple((x//2,y//2) for x,y in c)
I=((2,0),(0,0),(0,0),(2,0))
S=((2,0),(0,0),(0,0),(0,2))
V=((1,1),(1,-1),(1,-1),(1,1))
group={I}; todo=[I]
while todo:
    a=todo.pop()
    for b in (S,V):
        c=mm(a,b)
        if c not in group: group.add(c); todo.append(c)
def phase(a,j): return tuple(mul(x,power((0,1),j)) for x in a)
reps=sorted({min(phase(a,j) for j in range(4)) for a in group})
def inner(a,b):
    t=(0,0)
    for x,y in zip(a,b): t=add(t,mul(conj(x),y))
    if not all(v%4==0 for v in t): raise ValueError('nonintegral trace')
    return tuple(v//4 for v in t)
T=[[inner(a,b) for b in reps] for a in reps]
def div(a,b):
    n=b[0]*b[0]+b[1]*b[1]
    c=mul(a,conj(b))
    return (F(c[0],n),F(c[1],n))
def rref(rows):
    a=[[tuple(F(v) for v in z) for z in row] for row in rows]; piv=[]
    for j in range(len(a[0])):
        k=next((k for k in range(len(piv),len(a)) if a[k][j]!=(0,0)),None)
        if k is None: continue
        p=len(piv); a[p],a[k]=a[k],a[p]; z=a[p][j]
        a[p]=[div(v,z) for v in a[p]]
        for k in range(len(a)):
            if k==p or a[k][j]==(0,0): continue
            z=a[k][j]; a[k]=[add(x,neg(mul(z,y))) for x,y in zip(a[k],a[p])]
        piv.append(j)
    return a,piv
def need(c,msg):
    if not c: raise ValueError(msg)
need(len(group)==96 and len(reps)==24,'group census')
for a in group:
    adj=(conj(a[0]),conj(a[2]),conj(a[1]),conj(a[3]))
    need(mm(adj,a)==I,'unitarity')
result={'group':len(group),'projective':len(reps),'widths':[]}
for f in range(1,10):
    g=[[power(t,f) for t in row] for row in T]
    rr,piv=rref(g)
    item={'f':f,'rank':len(piv)}
    if len(piv)<24:
        j=next(j for j in range(24) if j not in piv)
        v=[(F(0),F(0))]*24; v[j]=(F(1),F(0))
        for i,col in enumerate(piv): v[col]=neg(rr[i][j])
        item['null_vector']=[[[z.numerator,z.denominator] for z in x] for x in v]
    result['widths'].append(item)
need([i['rank'] for i in result['widths']]==[4,10,20,23,24,24,24,24,24],'tensor ranks')
# Independent literal tensor-entry construction at the last failing and first
# faithful widths. Vectors use (2U)^tensor f, so their Gram is 4^f times
# the unnormalized trace-power Gram computed above.
for f in (4,5):
    vectors=[]
    for a in reps:
        v=[(1,0)]
        for _ in range(f): v=[mul(x,y) for x in v for y in a]
        vectors.append(v)
    for i,a in enumerate(vectors):
        for j,b in enumerate(vectors):
            z=(0,0)
            for x,y in zip(a,b): z=add(z,mul(conj(x),y))
            expected=power(T[i][j],f)
            need(z==tuple(4**f*x for x in expected),'literal tensor Gram')
# The explicit last-failing null vector must disappear at the next width of
# the same central-phase residue, not merely at a different phase quotient.
raw=result['widths'][3]['null_vector']
w=[tuple(F(*z) for z in x) for x in raw]
def action(f):
    out=[]
    for row in T:
        z=(F(0),F(0))
        for t,x in zip(row,w): z=add(z,mul(power(t,f),x))
        out.append(z)
    return out
need(all(z==(0,0) for z in action(4)),'width-four null witness')
need(any(z!=(0,0) for z in action(8)),'same-residue separation')
result['literal_tensor_gram_entries_checked']=1152
result['same_residue_witness']='width 4 zero; width 8 nonzero'
result['representatives_2U']=[list(a) for a in reps]
print(json.dumps(result,indent=2))
