"""Check free-algebra witnesses without the search or solver code.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
import gzip
import hashlib
import itertools
import json
from pathlib import Path


def require(condition,message):
    if not condition:raise ValueError(message)

# A polynomial is a dictionary of words with coefficient one over F2.
def toggle(out,word):
    if word in out:del out[word]
    else:out[word]=1

def xor(*polys):
    out={}
    for p in polys:
        for word in p:toggle(out,word)
    return out

def times(p,q):
    out={}
    for left in p:
        for right in q:toggle(out,left+right)
    return out

ONE={():1}

def letter(k):return {(k,):1}

def zeros():return [[{} for _ in range(4)] for _ in range(4)]

def matrix_sum(a,b):return [[xor(a[i][j],b[i][j]) for j in range(4)] for i in range(4)]

def matrix_product(a,b):
    return [[xor(*(times(a[i][k],b[k][j]) for k in range(4))) for j in range(4)] for i in range(4)]


def setup():
    gates=[];base=[]
    for s in range(3):
        a,b=letter(2*s),letter(2*s+1)
        p,r,e,all_r=zeros(),zeros(),zeros(),zeros()
        for i in (0,s+1):
            e[i][i]=ONE
            for j in (0,s+1):
                p[i][j]=xor(a,b) if i==j else b
                r[i][j]=a;all_r[i][j]=ONE
        gates.extend(((p,r),(matrix_sum(p,e),matrix_sum(r,all_r))))
        base.extend((xor(times(a,a),a),xor(times(a,b),times(b,a),b)))
    c=letter(6);base.append(xor(times(c,c),c))
    for h in (c,xor(ONE,c)):
        p,forward,backward=zeros(),zeros(),zeros()
        p[0][0]=h
        for i in range(1,4):
            forward[0][i]=h;backward[i][0]=h
            for j in range(1,4):p[i][j]=h
        gates.extend(((p,forward),(p,backward)))
    # Compute ordered-pair contributions once. This uses pair sums, not the
    # search program's suffix accumulator.
    commutators={}
    for i in range(6):
        for j in range(10):
            commutators[i,j]=matrix_sum(matrix_product(gates[i][0],gates[j][1]),matrix_product(gates[j][1],gates[i][0]))
    return base,commutators


def equations(order,base,commutators,with_labels=False):
    out=[zeros() for _ in range(3)]
    for earlier,i in enumerate(order):
        if i>=6:continue
        for j in order[earlier+1:]:out[i//2]=matrix_sum(out[i//2],commutators[i,j])
    result=list(base);labels=[None]*len(base)
    for s,mat in enumerate(out):
        for r in range(4):
            for c in range(4):
                if r in (0,s+1) and c in (0,s+1):continue
                if mat[r][c]:
                    result.append(mat[r][c]);labels.append((s,r,c))
    return (result,labels) if with_labels else result


def all_orders():
    # Build the order list independently from permutations of six good slots.
    # Canonical first occurrences remove exactly the six good-stage renamings.
    good=[]
    def extend(prefix,counts):
        if len(prefix)==6:
            good.append(tuple(prefix));return
        for s in range(3):
            if counts[s]==2:continue
            if counts[s]==0 and any(counts[t]==0 for t in range(s)):continue
            updated=counts.copy();updated[s]+=1
            extend(prefix+[s],updated)
    extend([], [0,0,0])
    for word in good:
        for occupied in itertools.combinations(range(10),6):
            positions=set(occupied)
            for extra in itertools.permutations((6,7,8,9)):
                ni=nj=0;seen=[0,0,0];order=[]
                for k in range(10):
                    if k in positions:
                        s=word[ni];ni+=1;order.append(2*s+seen[s]);seen[s]+=1
                    else:order.append(extra[nj]);nj+=1
                yield tuple(order)


def check_witness(eqs,witness,degree):
    total={}
    for index,left,right in witness:
        require(type(index) is int and 0<=index<len(eqs),'Equation index')
        require(all(type(v) is int and 0<=v<7 for v in left+right),'Variable index')
        for term in eqs[index]:
            word=tuple(left)+term+tuple(right)
            require(len(word)<=degree,'Degree bound')
            toggle(total,word)
    require(total==ONE,'The witness does not expand to one')


def verify(path=None):
    path=Path(path) if path else Path(__file__).with_name('ORDER-CERTIFICATES.json.gz')
    data=path.read_bytes();certificate=json.loads(gzip.decompress(data))
    require(certificate['schema']==1,'Certificate schema')
    witnesses=certificate['witnesses'];require(len(witnesses)==75600,'Order coverage')
    base,commutators=setup();counts=Counter();seen=set();digest=hashlib.sha256();largest=0
    for order,record in zip(all_orders(),witnesses,strict=True):
        require(order not in seen,'Duplicate order');seen.add(order)
        degree,witness=record
        require(degree in (2,3),'Unexpected witness degree')
        check_witness(equations(order,base,commutators),witness,degree)
        counts[degree]+=1;largest=max(largest,len(witness));digest.update(bytes(order))
    require(len(seen)==75600,'Order enumeration')
    # A different enumeration counts all labelled orders before the quotient.
    require(75600*6==3628800//8,'Labelled-order count')
    first_order=next(all_orders());first_eq=equations(first_order,base,commutators)
    first_witness=witnesses[0][1]
    try:check_witness(first_eq,[],2)
    except ValueError:pass
    else:raise ValueError('An empty witness was accepted')
    corrupted=first_witness+[[0,[],[]]]
    try:check_witness(first_eq,corrupted,witnesses[0][0])
    except ValueError:pass
    else:raise ValueError('A changed witness was accepted')
    return {'orders':len(seen),'degree_counts':{str(k):v for k,v in sorted(counts.items())},'largest_witness_terms':largest,'certificate_sha256':hashlib.sha256(data).hexdigest(),'order_sha256':digest.hexdigest(),'corruptions_rejected':['empty_witness','extra_nonzero_equation']}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
