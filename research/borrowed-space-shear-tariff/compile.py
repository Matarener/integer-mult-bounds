"""Exact borrowed-space shear words. Ali Romman with OpenAI Codex. Apache-2.0."""
from fractions import Fraction as Q


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def zero(n, m):
    return [[Q(0)] * m for _ in range(n)]


def transpose(a):
    return [list(row) for row in zip(*a)]


def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in transpose(b)] for row in a]


def add(a, b, sign=1):
    return [[x+sign*y for x,y in zip(r,s)] for r,s in zip(a,b)]


def rref(a):
    rows = [[Q(x) for x in row] for row in a]
    pivots=[]
    for j in range(len(rows[0]) if rows else 0):
        k=len(pivots)
        at=next((i for i in range(k,len(rows)) if rows[i][j]),None)
        if at is None:
            continue
        rows[k],rows[at]=rows[at],rows[k]
        c=rows[k][j]
        rows[k]=[x/c for x in rows[k]]
        for i in range(len(rows)):
            if i!=k and rows[i][j]:
                c=rows[i][j]
                rows[i]=[x-c*y for x,y in zip(rows[i],rows[k])]
        pivots.append(j)
        if len(pivots)==len(rows):
            break
    return rows,pivots


def rank(a):
    return len(rref(a)[1])


def inverse(a):
    n=len(a)
    rows,pivots=rref([row+e for row,e in zip(a,eye(n))])
    if pivots[:n]!=list(range(n)):
        raise ValueError('singular matrix')
    return [row[n:] for row in rows]


def factor_square_zero(a):
    n=len(a)
    if not n or any(len(row)!=n for row in a):
        raise ValueError('positive square matrix required')
    if mm(a,a)!=zero(n,n):
        raise ValueError('matrix square must be zero')
    _,cols=rref(a)
    r=len(cols)
    if not r:
        return zero(n,0),[]
    v=[[row[j] for j in cols] for row in a]
    _,rows=rref(transpose(v))
    l=mm(inverse([v[i] for i in rows]),[a[i] for i in rows])
    if mm(v,l)!=a or mm(l,v)!=zero(r,r):
        raise ArithmeticError('rank factorization failed')
    return v,l


def compile_factors(v, l, q, clean=False):
    """Emit cross-bank shears from V,L with LV=0; preserve arbitrary data."""
    n=len(v)
    r=len(l)
    if type(q) is not int or q<1 or not n or any(len(row)!=r for row in v) or any(len(row)!=n for row in l):
        raise ValueError('invalid dimensions')
    if r and mm(l,v)!=zero(r,r):
        raise ValueError('factor cross-products must vanish')
    if not r:
        return []
    return block_word(v,l,q,clean)


def block_word(v,l,q,clean=False):
    """Form the linear coefficient schedule after factor validation."""
    n=len(v);r=len(l)
    if not r:
        return []
    words=[]
    previous=zero(q,n)
    total=zero(n,q)
    for first in range(0,r,q):
        vb=[[Q(row[j]) if j<r else Q(0) for j in range(first,first+q)] for row in v]
        lb=[[Q(x) for x in l[j]] if j<r else [Q(0)]*n for j in range(first,first+q)]
        words.append(('G',add(lb,previous,-1)))
        words.append(('S',vb))
        previous=lb
        total=add(total,vb)
    words.append(('G',[[ -x for x in row] for row in previous]))
    if not clean:
        words.append(('S',[[ -x for x in row] for row in total]))
    return words


def scalar_ops(word, n, q):
    """Lower each nonzero rectangular coefficient to one scalar ADD."""
    out=[]
    for kind,matrix in word:
        expected=(q,n) if kind=='G' else (n,q)
        if kind not in ('G','S') or len(matrix)!=expected[0] or any(len(row)!=expected[1] for row in matrix):
            raise ValueError('invalid shear')
        for i,row in enumerate(matrix):
            for j,c in enumerate(row):
                if c:
                    out.append((n+i,j,c) if kind=='G' else (i,n+j,c))
    return out


def norm(a):
    return max((sum(abs(x) for x in row) for row in a),default=Q(0))


def replay(ops, dimension):
    """Return the complete action and maximum scalar prefix and suffix norms."""
    a=eye(dimension)
    prefix=Q(1)
    for dst,src,c in ops:
        if dst==src or not 0<=dst<dimension or not 0<=src<dimension:
            raise ValueError('invalid scalar ADD')
        a[dst]=[x+c*y for x,y in zip(a[dst],a[src])]
        prefix=max(prefix,norm(a))
    suffix=Q(1)
    b=eye(dimension)
    for dst,src,c in reversed(ops):
        for row in b:
            row[src]+=c*row[dst]
        suffix=max(suffix,norm(b))
    if a!=b:
        raise ArithmeticError('row and column replay disagree')
    return a,prefix,suffix


def bounds(v,l,q):
    """Give scalar-ADD prefix/suffix bounds with no payload-volume factor."""
    r=len(l)
    if not r:
        return Q(1),Q(1)
    js=[];ds=[]
    for first in range(0,r,q):
        js.append(max(sum(abs(row[j]) for j in range(first,min(r,first+q))) for row in v))
        ds.append(max(sum(abs(x) for x in row) for row in l[first:first+q]))
    j=sum(js);d=max(ds)
    intermediate=max(1+2*d,1+j)
    forward=max(1+sum(x*y for x,y in zip(js,ds))+j,1+d)
    backward=max(1+j*(2*d+1),1+d)
    return forward*intermediate,(1+j*d)*backward*intermediate


def character_value(kernel, chi):
    first=next(iter(kernel.values()))
    out=zero(len(first),len(first[0]))
    for v,a in kernel.items():
        out=add(out,a,-1 if (v&chi).bit_count()%2 else 1)
    return out


def from_characters(matrices):
    m=len(matrices)
    n=len(matrices[0]);r=len(matrices[0][0])
    out={}
    for v in range(m):
        a=zero(n,r)
        for chi,mat in enumerate(matrices):
            a=add(a,mat,-1 if (v&chi).bit_count()%2 else 1)
        out[v]=[[x/m for x in row] for row in a]
    return out


def compile_kernel(kernel, q):
    """Compile a square-zero kernel over the elementary binary translation group."""
    if type(q) is not int or q<1:
        raise ValueError("positive borrowed dimension required")
    m=len(kernel)
    if m<1 or m&(m-1) or set(kernel)!=set(range(m)):
        raise ValueError('complete binary group coefficient list required')
    n=len(kernel[0])
    if not n or any(len(a)!=n or any(len(row)!=n for row in a) for a in kernel.values()):
        raise ValueError('square kernel matrices required')
    values=[character_value(kernel,chi) for chi in range(m)]
    factors=[factor_square_zero(a) for a in values]
    ranks=[len(l) for _,l in factors]
    r=max(ranks);n=len(values[0])
    if not r:
        return [],ranks
    vs=[];ls=[]
    for v,l in factors:
        k=len(l)
        vs.append([row+[Q(0)]*(r-k) for row in v])
        ls.append(l+zero(r-k,n))
    vk,lk=from_characters(vs),from_characters(ls)
    for chi in range(m):
        v,l=character_value(vk,chi),character_value(lk,chi)
        if mm(v,l)!=values[chi] or mm(l,v)!=zero(r,r):
            raise ArithmeticError('kernel factor mismatch')
    coefficient_words=[block_word(vk[g],lk[g],q) for g in range(m)]
    word=[(coefficient_words[0][i][0],{g:coefficient_words[g][i][1] for g in range(m)})
          for i in range(len(coefficient_words[0]))]
    return word,ranks


def kernel_scalar_ops(word,n,q):
    return [(dst,src,c,g) for kind,kernel in word for g,matrix in kernel.items()
            for dst,src,c in scalar_ops([(kind,matrix)],n,q)]
