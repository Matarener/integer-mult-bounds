"""Check recognition against complete tiny orbits and literal products.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('recognition', HERE / 'recognize.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
N = R.N


def require(test, message):
    if not test:
        raise ValueError(message)


def action(t, u, v, p):
    out = [0] * len(t)
    for i, x in enumerate(u):
        for j, y in enumerate(v):
            for k, z in enumerate(t[i][j]):
                out[k] = (out[k] + x*y*z) % p
    return out


def model(p, heights):
    sizes = [p**h for h in heights]
    exponents = list(product(*(range(s) for s in sizes)))
    index = {e:i for i,e in enumerate(exponents)}
    n = len(exponents)
    t = [[[0]*n for _ in range(n)] for _ in range(n)]
    for i,a in enumerate(exponents):
        for j,b in enumerate(exponents):
            c = tuple(x+y for x,y in zip(a,b))
            if all(x<s for x,s in zip(c,sizes)):
                t[i][j][index[c]] = 1
    return t


def quotient(p, poly):
    n = len(poly)-1
    powers = []
    for degree in range(2*n-1):
        v = [0]*max(n,degree+1)
        v[degree] = 1
        for j in range(len(v)-1,n-1,-1):
            coefficient = v[j]
            for i in range(n+1):
                v[j-n+i] = (v[j-n+i]-coefficient*poly[i]) % p
        powers.append(v[:n])
    return [[powers[i+j] for j in range(n)] for i in range(n)]


def direct_sum(*tables):
    n = sum(map(len,tables))
    out = [[[0]*n for _ in range(n)] for _ in range(n)]
    offset = 0
    for t in tables:
        for i,j,k in product(range(len(t)),repeat=3):
            out[offset+i][offset+j][offset+k] = t[i][j][k]
        offset += len(t)
    return out


def change(t, P, Q, S, p):
    n = len(t)
    # The complete binary oracle uses the explicit two-by-two inverse formula.
    def inv(a):
        if n != 2:
            return N.inverse(a,p)
        z = pow((a[0][0]*a[1][1]-a[0][1]*a[1][0]) % p,-1,p)
        return [[a[1][1]*z % p,-a[0][1]*z % p],[-a[1][0]*z % p,a[0][0]*z % p]]
    u, v = list(zip(*inv(P))), list(zip(*inv(Q)))
    return [[[sum(S[k][l]*x for l,x in enumerate(action(t,u[i],v[j],p))) % p
              for k in range(n)] for j in range(n)] for i in range(n)]


def key(t):
    return tuple(x for row in t for v in row for x in v)


def check(t, c, p, algebra=None):
    n = len(t)
    a = c['table'] if algebra is None else algebra
    maps = [c[name] for name in ['U','V','W']]
    require(all(N.rank(m,p)==n for m in maps), 'singular transporter')
    U,V,W = maps
    for i,j in product(range(n),repeat=2):
        left = action(t,[row[i] for row in U],[row[j] for row in V],p)
        right = [sum(row[k]*a[i][j][k] for k in range(n)) % p for row in W]
        require(left==right, 'literal transported basis product')
    if algebra is None:
        require(all(a[i][j]==a[j][i] for i,j in product(range(n),repeat=2)), 'commutative table')
        basis=N.identity(n)
        for i,j,k in product(range(n),repeat=3):
            require(action(a,a[i][j],basis[k],p)==action(a,basis[i],a[j][k],p), 'associative table')
        # Recover a unit by linear equations, then check both unit laws literally.
        eq=[[a[i][j][k] for i in range(n)]+[int(j==k)] for j,k in product(range(n),repeat=2)]
        rows,pivots=N.rref(eq,p)
        require(pivots==list(range(n)), 'unit equations')
        unit=[rows[i][-1] for i in range(n)]
        for b in basis:
            require(action(a,unit,b,p)==b==action(a,b,unit,p), 'two-sided unit')
    return n*n


def census():
    G=[]
    for a,b,c,d in product(range(2),repeat=4):
        if (a*d-b*c) % 2:
            G.append([[a,b],[c,d]])
    models=[direct_sum(model(2,[]),model(2,[])),quotient(2,[1,1,1]),model(2,[1])]
    orbits=[]
    for t in models:
        orbits.append({key(change(t,*maps,2)) for maps in product(G,repeat=3)})
    require(not any(orbits[i]&orbits[j] for i in range(3) for j in range(i)), 'distinct model orbits')
    expected=set().union(*orbits)
    got, got_frobenius=set(),set()
    counts={}; products=0
    for flat in product(range(2),repeat=8):
        t=[[list(flat[4*i+2*j:4*i+2*j+2]) for j in range(2)] for i in range(2)]
        cert,reason=R.recognize_commutative(t,2)
        if cert is not None:
            got.add(flat); products+=check(t,cert,2)
        else:
            counts[reason]=counts.get(reason,0)+1
        cert,reason=R.recognize_frobenius(t,2)
        if cert is not None:
            require(cert['heights']==[1], 'binary recovered height')
            got_frobenius.add(flat); products+=check(t,cert,2,model(2,[1]))
    require(got==expected and got_frobenius==orbits[2], 'complete tensor orbit oracle')
    return dict(total=256,commutative=len(got),frobenius=len(got_frobenius),
                orbit_sizes=list(map(len,orbits)),rejections=counts),products


def presentations(t,p,count=3):
    yield t
    n=len(t)
    for trial in range(1,count):
        maps=[]
        for salt in range(3):
            a=N.identity(n)
            if n>1:
                for step in range(2*n+trial):
                    i=(step+salt)%n; j=(i+1)%n
                    a[i]=[(x+(trial+salt+1)*y)%p for x,y in zip(a[i],a[j])]
                a=a[1:]+a[:1]
            else:
                a[0][0]=1+(trial+salt)%(p-1)
            maps.append(a)
        yield change(t,*maps,p)


def main():
    controls=0
    def rejected(call):
        nonlocal controls
        try:
            call()
        except ValueError:
            controls+=1
        else:
            raise ValueError('negative control passed')
    for pin in json.loads((HERE/'INPUTS.json').read_text()):
        data=(HERE/pin['local']).read_bytes()
        blob=b'blob '+str(len(data)).encode()+b'\0'+data
        require(hashlib.sha256(data).hexdigest()==pin['sha256'] and
                hashlib.sha1(blob).hexdigest()==pin['git_blob'], 'source copy')
        rejected(lambda: require(hashlib.sha256(data+b' ').hexdigest()==pin['sha256'], 'source corruption'))
    domains,products=census()
    fixtures=0
    for p,heights in [(2,[]),(2,[1]),(2,[2]),(2,[1,1]),(2,[1,2]),(3,[1]),(3,[2]),(5,[1]),(7,[1]),(13,[])]:
        t=model(p,heights)
        for changed in presentations(t,p,2 if len(t)>7 else 3):
            cert,reason=R.recognize_frobenius(changed,p)
            require(cert is not None and cert['heights']==heights, 'Frobenius presentation')
            products+=check(changed,cert,p,t); fixtures+=1
    square_zero=[[[0]*3 for _ in range(3)] for _ in range(3)]
    for i in range(3):square_zero[0][i][i]=square_zero[i][0][i]=1
    general=[(2,square_zero),(2,quotient(2,[1,0,1,0,1])),
             (3,direct_sum(model(3,[1]),model(3,[]))),
             (2,direct_sum(square_zero,model(2,[])))]
    for p,t in general:
        for changed in presentations(t,p):
            cert,reason=R.recognize_commutative(changed,p)
            require(cert is not None, 'general commutative algebra rejected')
            products+=check(changed,cert,p); fixtures+=1
            specific,reason=R.recognize_frobenius(changed,p)
            require(specific is None and reason.startswith('algebra class:'), 'class boundary')
            controls+=1
    for p in [2,3,5]:
        dual=[[[square_zero[i][k][j] for k in range(3)] for j in range(3)] for i in range(3)]
        for transpose_input,reason in [(False,'output top multiplicity'),(True,'input top multiplicity')]:
            t=[[dual[j][i] for j in range(3)] for i in range(3)] if transpose_input else dual
            X,Y=N.nucleus(t,p)
            require(len(X)==3 and all(N.rank([N.flat(a) for a in b],p)==3 for b in [X,Y]), 'faithful dual control')
            cert,why=R.recognize_commutative(t,p)
            require(cert is None and why==reason, 'nonregular module accepted'); controls+=1
    a=[[[0]*4 for _ in range(4)] for _ in range(4)]
    for i,j,k,l in product(range(2),repeat=4):
        if j==k:a[2*i+j][2*k+l][2*i+l]=1
    cert,why=R.recognize_commutative(a,2)
    require(cert is None and why=='noncommutative nucleus','noncommutative algebra'); controls+=1
    t=model(2,[2]); cert,_=R.recognize_frobenius(t,2)
    for name in ['U','V','W']:
        for i,j in product(range(4),repeat=2):
            changed=deepcopy(cert); changed[name][i][j]^=1
            rejected(lambda:check(t,changed,2,t))
    for t,p in [([],2),([[[0]]],4),([[[True]]],2),([[[2]]],2),([[[0,0]]],2),([[[1]]],True)]:
        rejected(lambda:R.recognize_commutative(t,p))
    print('PASS_NONREDUCED_TENSOR_RECOGNITION '+json.dumps(dict(binary=domains,
          presentations=fixtures,literal_basis_products=products,controls=controls),sort_keys=True))


if __name__=='__main__':
    main()
