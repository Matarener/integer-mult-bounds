"""Compile sector maps with distinct-role ADDs and ordinary shifts."""
from fractions import Fraction as F


def emit(s, r=1, mode="perturbation"):
    if s < 1 or r < 1 or mode not in ("perturbation", "gauge"):
        raise ValueError("invalid circuit parameters")
    n = 1 << s
    word = []
    def add(dst, src, c, mask=0):
        word.append(("ADD", dst, src, F(c), mask))
    def route(offset):
        for k in range(s):
            for a in range(n):
                if a & (1 << k):
                    continue
                x, y = offset+a, offset+a+(1 << k)
                for dst, src, sign in ((x,y,1),(y,x,-1),(x,y,1)):
                    add(dst,src,F(sign,2))
                    add(dst,src,F(-sign,2),1 << k)
                word.append(("SHIFT",y,1 << k))
    if mode == "perturbation":
        word.append(("CLEAR", r*n))
    for b in range(r):
        x = b*n
        route(x)
        if mode == "perturbation":
            add(r*n,x,1)
            word.append(("QUERY",r*n))
            add(x,r*n,F(1,2))
            word.append(("CLEAR",r*n))
        else:
            word.append(("QUERY",x))
        route(x)
    return word


def tariff(s, r, mode):
    n = 1 << s
    return dict(QUERY=r, ADD=6*r*n*s+(2*r if mode=="perturbation" else 0),
                SHIFT=r*n*s, CLEAR=r+1 if mode=="perturbation" else 0,
                owned=1 if mode=="perturbation" else 0)


def emit_preserving(s, r=1, mode="perturbation"):
    """Keep the inputs and put the result in separate output fields."""
    size = r*(1 << s)
    word = []
    for i in range(size):
        word.extend([("CLEAR",size+i),("ADD",size+i,i,F(1),0)])
    for op in emit(s,r,mode):
        if op[0]=="ADD":
            word.append((op[0],op[1]+size,op[2]+size,*op[3:]))
        else:
            word.append((op[0],op[1]+size,*op[2:]))
    return word
