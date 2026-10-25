"""Exact dyadic residue arithmetic and literal reversible gates. Apache-2.0.
Chris R / Clear1nsight, substantial OpenAI Codex assistance.
Borrowed-bit lowering is the credited PR4017 Barenco reconstruction.
"""
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('credited_circuit',Path(__file__).parent/'frozen'/'PR4017-circuit.py')
circuit=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(circuit)

def need(x,msg):
    if not x:raise ValueError(msg)

def half(x,b):return (x>>1)|((x&1)<<(b-1))
def neg(x,b):
    m=(1<<b)-1
    return (-x)%m if x<m else m

def add(y,x,b):
    m=(1<<b)-1
    return (y+x)%m if y<m else m

def endpoint_swap(bits,control=None):
    # Gray path 0,1,3,...,2^b-1 and its return except the final edge.
    gates=[]
    for k in range(len(bits)):
        cc=[(bits[j],int(j<k))for j in range(len(bits))if j!=k]
        if control is not None:cc=[(control,1)]+cc
        gates.append((tuple(cc),bits[k]))
    return gates+gates[-2::-1]

def rotate_right(bits):
    # Old bit1 -> bit0, ..., old bit0 -> high bit.
    return [g for j in range(len(bits)-1)for g in circuit.swap([bits[j]],[bits[j+1]])]

def add_gates(src,dst,inverse=False):
    need(len(src)==len(dst) and not set(src)&set(dst),'disjoint equal words')
    b=len(src);g=[]
    for s in src:
        g += [(tuple([(s,1)]+[(dst[j],1)for j in range(k)]),dst[k])for k in range(b-1,-1,-1)]
        g += endpoint_swap(dst,s)
        g += rotate_right(dst)
    return g[::-1] if inverse else g

def negate_gates(bits):
    return [((),t)for t in bits]+endpoint_swap(bits)

def pair(x,y,b,inverse=False):
    m=(1<<b)-1
    need(all(0<=z<m for z in x+y),'canonical residue required')
    if inverse:
        # C inverse = conjugate(C), equally linear over the odd ring.
        a,ai=x;c,ci=y
        return (((a+ai+c-ci)*pow(2,-1,m))%m,((ai-a+ci+c)*pow(2,-1,m))%m),(((a-ai+c+ci)*pow(2,-1,m))%m,((ai+a+ci-c)*pow(2,-1,m))%m)
    ar,ai=x;cr,ci=y
    ar=(ar-cr)%m;ai=(ai-ci)%m
    cr=(cr+half(ar,b)+half(ai,b))%m
    ci=(ci+half(ai,b)-half(ar,b))%m
    ar,ai=neg(ai,b),ar
    return ((ar+cr)%m,(ai+ci)%m),(cr,ci)

def pair_gates(b,inverse=False):
    ar=list(range(b));ai=list(range(b,2*b));cr=list(range(2*b,3*b));ci=list(range(3*b,4*b))
    har=ar[1:]+ar[:1];hai=ai[1:]+ai[:1]
    g=add_gates(cr,ar,True)+add_gates(ci,ai,True)
    g+=add_gates(har,cr)+add_gates(hai,cr)+add_gates(hai,ci)+add_gates(har,ci,True)
    g+=circuit.swap(ar,ai)+negate_gates(ar)
    g+=add_gates(cr,ar)+add_gates(ci,ai)
    return g[::-1]if inverse else g

def phase(z,p,b):
    a,c=z
    return [(a,c),(neg(c,b),a),(neg(a,b),neg(c,b)),(c,neg(a,b))][p%4]

def decode(rec):
    rows=rec['matrix_rows'];q=rec['quadratic_rows'];alpha=rec['linear_Z4'];perm=[];ph=[]
    for x in range(512):
        ii=[i for i in range(9)if x>>i&1]
        perm.append(sum(((x&r).bit_count()%2)<<j for j,r in enumerate(rows))^rec['offset'])
        ph.append((rec['phase']+sum(alpha[i]for i in ii)+2*sum((q[i]>>j)&1 for i in ii for j in ii if i<j))%4)
    need(len(set(perm))==512,'monomial permutation')
    return perm,ph

def monomial(v,rec,b,inverse=False):
    perm,ph=decode(rec);out=[None]*512
    for x,y in enumerate(perm):
        if inverse:out[x]=phase(v[y],-ph[x],b)
        else:out[y]=phase(v[x],ph[x],b)
    return out

def macro(v,b,recipe,inverse=False):
    v=monomial(v,recipe['left']if inverse else recipe['right'],b,inverse)
    for j in (range(recipe['rank']-1,-1,-1)if inverse else range(recipe['rank'])):
        for x in range(512):
            if not x>>j&1:v[x],v[x^(1<<j)]=pair(v[x],v[x^(1<<j)],b,inverse)
    return monomial(v,recipe['right']if inverse else recipe['left'],b,inverse)

def bill(b):
    p=circuit.bill(pair_gates(b));a=circuit.bill(add_gates(list(range(b)),list(range(b,2*b))));n=circuit.bill(negate_gates(list(range(b))))
    return {'bits_per_complex_pair':4*b,'extra_clean_bits':0,'extra_dirty_bits':0,'modular_additions_per_pair':8,'pair':p,'adder':a,'macro':{k:1280*p[k]+(2512*3*b if k=='CNOT'else 0)+1024*n[k]for k in ['X','CNOT','Toffoli']}}

def centered_decode(r,b,exponent):
    m=(1<<b)-1;need(0<=r<m,'canonical decode')
    z=(r*pow(2,exponent,m))%m
    return z-m if z>m//2 else z

def decode_gates(bits,exponent):
    # Multiply by2^exponent by rotations, then encode the centered numerator
    # in ordinary two's complement. The unused code is mapped bijectively too.
    b=len(bits);g=[]
    for _ in range((-exponent)%b):g+=rotate_right(bits)
    g += [(tuple([(bits[-1],1)]+[(bits[j],1)for j in range(k)]),bits[k])for k in range(b-2,-1,-1)]
    return g
