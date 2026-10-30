"""Small exact matrix implementation over Q or a prime field.
SHIN09-git, substantial OpenAI Codex assistance. Apache-2.0.
No numerical tolerances, numpy, SymPy or predecessor executable imports.
"""
from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


def scalar(x, p):
    if p:
        if isinstance(x, Fraction):
            return x.numerator * pow(x.denominator, -1, p) % p
        return x % p
    return Fraction(x)


def eliminate(rows, width, p):
    a = [[scalar(x, p) for x in row] for row in rows]
    need(all(len(row) == width for row in a), "ragged elimination input")
    pivots = []
    for c in range(width):
        i = len(pivots)
        j = next((j for j in range(i, len(a)) if a[j][c]), None)
        if j is None:
            continue
        a[i], a[j] = a[j], a[i]
        inv = pow(a[i][c], -1, p) if p else 1 / a[i][c]
        a[i] = [scalar(x * inv, p) for x in a[i]]
        for j in range(len(a)):
            if j != i and a[j][c]:
                z = a[j][c]
                a[j] = [scalar(x - z*y, p) for x,y in zip(a[j],a[i])]
        pivots.append(c)
    return a[:len(pivots)], pivots


class Mat:
    def __init__(self, rows, p=0, width=None):
        self.p = p
        self.a = tuple(tuple(scalar(x,p) for x in row) for row in rows)
        self.r = len(self.a)
        self.c = len(self.a[0]) if self.r else (0 if width is None else width)
        need(all(len(row)==self.c for row in self.a), "ragged matrix")
        if width is not None:
            need(self.c==width, "wrong explicit width")

    def __eq__(self, other):
        return isinstance(other,Mat) and (self.p,self.r,self.c,self.a)==(other.p,other.r,other.c,other.a)

    def __matmul__(self, b):
        need(self.p==b.p and self.c==b.r, "matrix product shape/field")
        bt=list(zip(*b.a)) if b.r else [() for _ in range(b.c)]
        return Mat([[sum(x*y for x,y in zip(row,col)) for col in bt] for row in self.a],self.p,b.c)

    def __add__(self,b):
        need((self.r,self.c,self.p)==(b.r,b.c,b.p),"matrix sum shape/field")
        return Mat([[x+y for x,y in zip(row,col)] for row,col in zip(self.a,b.a)],self.p,self.c)

    def __neg__(self):
        return Mat([[-x for x in row] for row in self.a],self.p,self.c)

    def __sub__(self,b):
        return self + (-b)

    @property
    def T(self):
        return Mat(list(zip(*self.a)) if self.r else [[] for _ in range(self.c)],self.p,self.r)

    def take(self,rows,cols):
        return Mat([[self.a[i][j] for j in cols] for i in rows],self.p,len(cols))

    def rank(self):
        return len(eliminate(self.a,self.c,self.p)[1])

    def inverse(self):
        need(self.r==self.c,"inverse needs square matrix")
        n=self.r
        a,piv=eliminate([list(row)+list(e) for row,e in zip(self.a,eye(n,self.p).a)],2*n,self.p)
        need(piv[:n]==list(range(n)) and len(piv)==n,"singular matrix")
        return Mat([row[n:] for row in a],self.p,n)

    def kernel(self):
        a,piv=eliminate(self.a,self.c,self.p)
        result=[]
        for c in range(self.c):
            if c in piv:
                continue
            v=[scalar(0,self.p)]*self.c
            v[c]=scalar(1,self.p)
            for i,j in enumerate(piv):
                v[j]=-a[i][c]
            result.append(tuple(scalar(x,self.p) for x in v))
        return result

    def image(self):
        _,piv=eliminate(self.a,self.c,self.p)
        return [tuple(self.a[i][j] for i in range(self.r)) for j in piv]

    def json(self):
        return [[x if self.p else str(x) for x in row] for row in self.a]


def zeros(r,c,p):
    return Mat([[0]*c for _ in range(r)],p,c)


def eye(n,p):
    return Mat([[int(i==j) for j in range(n)] for i in range(n)],p,n)


def from_columns(cols,height,p):
    return Mat([[v[i] for v in cols] for i in range(height)],p,len(cols))


def stack(blocks):
    need(bool(blocks),"empty stack")
    need(all(b.c==blocks[0].c and b.p==blocks[0].p for b in blocks),"stack shape/field")
    return Mat([row for b in blocks for row in b.a],blocks[0].p,blocks[0].c)


def join(blocks):
    need(bool(blocks),"empty join")
    need(all(b.r==blocks[0].r and b.p==blocks[0].p for b in blocks),"join shape/field")
    return Mat([sum((list(b.a[i]) for b in blocks),[]) for i in range(blocks[0].r)],blocks[0].p,sum(b.c for b in blocks))


def block(rows):
    return stack([join(row) for row in rows])


def extension(start,candidates,width,p):
    out=list(start)
    need(Mat(out,p,width).rank()==len(out),"dependent starting basis")
    extra=[]
    for v in candidates:
        if Mat(out+[v],p,width).rank()>len(out):
            out.append(tuple(v))
            extra.append(tuple(v))
    return extra
