"""Independent rational Schur elimination and rejection controls.
JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q


def need(ok, why):
    if not ok:
        raise ValueError(why)


def encode(value):
    if isinstance(value, Q):
        return [value.numerator, value.denominator]
    if isinstance(value, (list, tuple)):
        return [encode(x) for x in value]
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    return value


def rowmass(row):
    return sum(map(abs, row), Q())


def norm(a):
    return max(map(rowmass, a), default=Q())


def gap(a):
    return min(a[i][i]-sum((abs(x) for j,x in enumerate(row) if j!=i), Q())
               for i,row in enumerate(a))


def product(a,b):
    return [[sum((x*y for x,y in zip(row,col)),Q()) for col in zip(*b)] for row in a]


def inverse(a):
    n=len(a); w=[list(row)+[Q(i==j) for j in range(n)] for i,row in enumerate(a)]
    for k in range(n):
        need(w[k][k]!=0,'independent inverse pivot')
        z=w[k][k]; w[k]=[x/z for x in w[k]]
        for i in range(n):
            if i!=k:
                z=w[i][k]; w[i]=[x-z*y for x,y in zip(w[i],w[k])]
    return [row[n:] for row in w]


def stage_lu(a):
    """Trailing Schur updates, independent of source Doolittle dot products."""
    n=len(a); current=[list(row) for row in a]
    lower=[[Q(i==j) for j in range(n)] for i in range(n)]
    upper=[[Q() for j in range(n)] for i in range(n)]
    stages=[]; losses=[Q() for _ in a]
    for k in range(n):
        trailing=[row[k:] for row in current[k:]]
        need(gap(trailing)>0,'positive dominance prerequisite')
        pivot=current[k][k]
        upper[k][k:]=current[k][k:]
        pivot_gap=pivot-sum(map(abs,current[k][k+1:]),Q())
        before=[rowmass(row[k:]) for row in current]
        for i in range(k+1,n):
            lower[i][k]=current[i][k]/pivot
            for j in range(k+1,n):
                current[i][j]-=lower[i][k]*current[k][j]
            current[i][k]=Q()
            loss=before[i]-rowmass(current[i][k+1:])
            need(loss>=abs(lower[i][k])*pivot_gap,'quantified rowmass depletion')
            losses[i]+=abs(lower[i][k])*pivot_gap
        stages.append({'pivot':pivot,'gap':gap(trailing),'norm':norm(trailing),
                       'matrix':trailing,'pivot_gap':pivot_gap})
    need(product(lower,upper)==a,'independent exact factor product')
    for i in range(n):
        need(losses[i]+rowmass(upper[i])<=rowmass(a[i]),'telescoped rowmass allocation')
    return lower,upper,stages


def schur(a, interior):
    order=list(interior)+[i for i in range(len(a)) if i not in interior]
    c=[[a[i][j] for j in order] for i in order]
    for _ in interior:
        need(c[0][0]>0,'Schur pivot')
        c=[[c[i][j]-c[i][0]*c[0][j]/c[0][0]
            for j in range(1,len(c))] for i in range(1,len(c))]
    return c


def truncate(a,P):
    unit=1<<P
    return [[Q(int(x*unit),unit) for x in row] for row in a]


def analyze(a,p):
    need(gap(a)>0 and norm(a)<2,'admitted rounded matrix')
    low,up,stages=stage_lu(a)
    d=gap(a); M=norm(a)
    need(all(z['gap']>=d and z['norm']<=M for z in stages),'all-stage gap and rowmass envelopes')
    need(norm(low)<=M/d and norm(up)<=M,'sharp factor caps')
    need(norm(inverse(a))<=1/d,'matrix inverse gap cap')
    need(norm(inverse(low))<=M/d,'lower inverse cap')
    need(norm(inverse(up))<=M/(d*d),'upper inverse cap')
    need(d>=Q(1,16*p),'production comparison gap')
    need(norm(low)<=32*p and norm(inverse(up))<=512*p*p,'sharper source caps')
    need(norm(low)<=65*p*p and norm(up)<2 and norm(inverse(low))<=32*p
         and norm(inverse(up))<=1040*p**3,'retained source caps')
    return low,up,stages


def checks():
    cases=stage_count=0
    for p in (1,2,5):
        P=6+p; eta=Q(1,1<<P); delta=Q(1,8*p)
        need(eta<=delta/2,'generic precision admission')
        for n in (2,3,5,8):
            for seed in range(4):
                a=[[Q(((7*i+11*j+seed)%9)-4,32*n) if i!=j else Q()
                    for j in range(n)] for i in range(n)]
                for i in range(n):a[i][i]=rowmass(a[i])+delta+Q(seed+1,1000)
                need(gap(a)>=delta and norm(a)<2,'synthetic old-H premises')
                for I in ([],[0],list(range(0,n-1,2))):
                    S=schur(a,I)
                    need(gap(S)>=gap(a) and norm(S)<=norm(a),'principal Schur preserves premises')
                    b=truncate(S,P)
                    need(gap(b)>gap(S)-eta and norm(b)<=norm(S),'towardzero single-entry gap loss')
                    _,_,stages=analyze(b,p)
                    need(all(z['gap']>=gap(b) and z['norm']<=norm(b) for z in stages),'all-stage envelopes')
                    cases+=1;stage_count+=len(stages)
    # Nearest rounding raises three small off-diagonal entries: loss exceeds eta.
    eta=Q(1,8); a=[[Q(i==j) for j in range(4)] for i in range(4)]
    a[0]=[1+eta/10,3*eta/5,3*eta/5,3*eta/5]
    nearest=[[Q((x/eta+Q(1,2)).__floor__())*eta for x in row] for row in a]
    need(gap(nearest)<gap(a)-eta,'nearest-rounding is not the one-entry gap contract')
    need(truncate([[-Q(3,16)]],3)==[[-Q(1,8)]],'negative towardzero differs from floor')
    # Removing positive gap permits a zero pivot at the next stage.
    singular=[[Q(1),Q(1)],[Q(1),Q(1)]]
    try:stage_lu(singular)
    except ValueError:pass
    else:raise ValueError('singular gap-free control accepted')
    scalar=[[1+Q(1,24)]]
    need(product(*stage_lu(truncate(scalar,3))[:2])!=scalar,'factors belong to rounded reference')
    need(norm([[Q(3)]])>2,'rowmass hypothesis required for U<2')
    return {'systems':cases,'elimination_stages':stage_count,
            'controls':['nearest-versus-truncate','signed-towardzero','zero-gap-pivot',
                        'rounded-reference-not-S','rowmass-cap-needed'],
            'scope':'finite corroboration; quantified proof is PROOF.md'}
