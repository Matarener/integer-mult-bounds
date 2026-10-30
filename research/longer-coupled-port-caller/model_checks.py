"""Independent matrix and polynomial controls for the star theorem.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import random


def require(test,message):
    if not test:raise ValueError(message)


def eye(n):return tuple(1<<i for i in range(n))
def zero(n):return (0,)*n
def add(a,b):return tuple(x^y for x,y in zip(a,b))

def mul(a,b):
    out=[]
    for row in a:
        value=0
        while row:
            low=row&-row;value^=b[low.bit_length()-1];row^=low
        out.append(value)
    return tuple(out)

def rank(a):
    pivots={}
    for row in a:
        while row:
            p=row.bit_length()-1
            if p not in pivots:pivots[p]=row;break
            row^=pivots[p]
    return len(pivots)

def inverse(a):
    n=len(a);rows=[a[i]|(1<<(n+i)) for i in range(n)]
    for j in range(n):
        pivot=next(i for i in range(j,n) if rows[i]>>j&1)
        rows[j],rows[pivot]=rows[pivot],rows[j]
        for i in range(n):
            if i!=j and rows[i]>>j&1:rows[i]^=rows[j]
    require(tuple(x&((1<<n)-1) for x in rows)==eye(n),'Matrix inverse')
    return tuple(x>>n for x in rows)

def choose(q,rng):
    d=2*q;g=list(eye(d))
    for _ in range(8*d):
        i,j=rng.sample(range(d),2);g[i]^=g[j]
    gi=inverse(g);diagonal=tuple(1<<i if i<q else 0 for i in range(d))
    off=tuple(sum((rng.randrange(2)<<j) for j in range(d) if (i<q)!=(j<q)) for i in range(d))
    return mul(mul(g,diagonal),gi),mul(mul(g,off),gi)

def block_put(rows,block,rr,cc,d):
    for i,row in enumerate(block):rows[rr*d+i]^=row<<(cc*d)


def frame(q,g,rng):
    d=2*q;n=d*(g+1);calls=[];target=[];noncommuting=0;parameters=[]
    for j in range(g):
        a,b=choose(q,rng);p=[0]*n;r=[0]*n;e=[0]*n;t=[0]*n
        parameters.extend((a,b))
        noncommuting+=mul(a,b)!=mul(b,a)
        for row in (0,j+1):
            block_put(e,eye(d),row,row,d)
            for col in (0,j+1):
                block_put(p,add(a,b) if row==col else b,row,col,d)
                block_put(r,a,row,col,d);block_put(t,eye(d),row,col,d)
        calls.extend(((j,tuple(p),tuple(r)),(j,add(e,p),add(t,r))))
        target.append(tuple(e))
    c,_=choose(q,rng)
    parameters.append(c)
    for half,h in enumerate((c,add(eye(d),c))):
        p=[0]*n;ra=[0]*n;rb=[0]*n
        block_put(p,h,0,0,d)
        for j in range(1,g+1):
            block_put(ra,h,0,j,d);block_put(rb,h,j,0,d)
            for k in range(1,g+1):block_put(p,h,j,k,d)
        calls.extend(((g+half,tuple(p),tuple(ra)),(g+half,tuple(p),tuple(rb))))
        target.append(zero(n))
    total=zero(n)
    for _,p,r in calls:
        require(mul(p,p)==p and rank(p)==2*q,'Native projector')
        require(mul(r,r)==zero(n) and rank(r)==q,'Native query')
        require(mul(p,r)==r and mul(r,p)==r,'Native compatibility')
        total=add(total,r)
    require(total==eye(n),'Query sum')
    return calls,target,noncommuting,parameters


def polynomial_product(a,b):
    n=len(next(iter(a.values())));out={}
    for x,ax in a.items():
        for y,by in b.items():
            if x&y:continue
            key=x|y;out[key]=add(out.get(key,zero(n)),mul(ax,by))
    return {key:mat for key,mat in out.items() if any(mat)}


def literal(calls,order,stage=None):
    n=len(calls[0][1]);out={0:eye(n)}
    for index in order:
        group,p,r=calls[index]
        gate={0:eye(n),1:r}
        if stage is None or group==stage:
            bit=1<<(group+1) if stage is None else 2
            gate[bit]=p;gate[bit|1]=r
        out=polynomial_product(gate,out)
    return out


def defects(calls,order,group):
    result=zero(len(calls[0][1]))
    for i,left in enumerate(order):
        if calls[left][0]!=group:continue
        p=calls[left][1]
        for right in order[i+1:]:
            r=calls[right][2];result=add(result,add(mul(p,r),mul(r,p)))
    return result


def submatrix(matrix,indices):
    return tuple(sum(((matrix[i]>>j)&1)<<k for k,j in enumerate(indices)) for i in indices)


def evaluate(poly,parameters):
    n=len(parameters[0]);result=zero(n)
    for word in poly:
        term=eye(n)
        for letter in word:term=mul(term,parameters[letter])
        result=add(result,term)
    return result


def run(checker=None):
    rng=random.Random(20261026);cases=0;checked=0;noncommuting=0;symbolic_blocks=0;restriction_blocks=0
    for q in (1,2,3,4):
        for g in (3,5):
            for _ in range(3):
                calls,targets,nc,parameters=frame(q,g,rng);noncommuting+=nc
                order=list(range(len(calls)));rng.shuffle(order);n=len(calls[0][1]);failed=0
                numeric=[]
                for group in range(g):
                    defect=defects(calls,order,group);numeric.append(defect)
                    actual=literal(calls,order,group).get(3,zero(n))
                    require(actual==add(targets[group],defect),'Literal mixed coefficient')
                    failed+=bool(any(defect));checked+=1
                require(failed>0,'Excluded frame passed all necessary equations');cases+=1
                d=2*q
                if g==3 and checker is not None:
                    base,commutators=checker.setup()
                    eqs,labels=checker.equations(order,base,commutators,with_labels=True)
                    for polynomial,label in zip(eqs,labels):
                        actual=evaluate(polynomial,parameters)
                        if label is None:require(actual==zero(d),'Local symbolic equation')
                        else:
                            stage,row,col=label
                            expected=tuple((numeric[stage][row*d+i]>>(col*d))&((1<<d)-1) for i in range(d))
                            require(actual==expected,'Symbolic equation matches the literal matrix defect');symbolic_blocks+=1
                if g==5:
                    chosen=sorted(rng.sample(range(g),3));indices=list(range(d))
                    for stage in chosen:indices.extend(range((stage+1)*d,(stage+2)*d))
                    selected=[i for i,(stage,_,_) in enumerate(calls) if stage in chosen or stage>=g]
                    mapping={old:new for new,old in enumerate(selected)}
                    reduced=[(chosen.index(stage) if stage<g else stage-g+3,submatrix(p,indices),submatrix(r,indices)) for i in selected for stage,p,r in (calls[i],)]
                    reduced_order=[mapping[i] for i in order if i in mapping]
                    for small,large in enumerate(chosen):
                        full=submatrix(numeric[large],indices);cut=defects(reduced,reduced_order,small)
                        for row in range(4):
                            for col in range(4):
                                if row in (0,small+1) and col in (0,small+1):continue
                                for i in range(d):
                                    mask=((1<<d)-1)<<(col*d)
                                    require((full[row*d+i]&mask)==(cut[row*d+i]&mask),'Three-leaf restriction')
                                restriction_blocks+=1
    require(noncommuting>0,'Coupled controls must include noncommuting matrices')
    # An actual one-leaf word: each channel uses its three-query identity.
    calls,targets,_,_=frame(1,1,random.Random(37));order=list(range(6));n=4
    result=literal(calls,order)
    expected={0:eye(n),1:eye(n),2:eye(n),3:eye(n)}
    require(result==expected,'One-leaf positive word')
    changed=list(calls);group,p,r=changed[0];changed[0]=(group,p,zero(n))
    require(literal(changed,order)!=expected,'Deleted query control')
    # The two-row argument can be checked without a matrix inventory.
    row_cases=0
    for dimension in range(1,7):
        for a in range(1<<dimension):
            for b in range(1<<dimension):
                if (a&1)!=(b&1) or (a&b).bit_count()%2:continue
                require(((a^1)&(b^1)).bit_count()%2==1,'Three-occurrence parity')
                row_cases+=1
    return {'coupled_frames':cases,'mixed_coefficients':checked,'noncommuting_local_controls':noncommuting,'symbolic_blocks_checked':symbolic_blocks,'three_leaf_restriction_blocks':restriction_blocks,'one_leaf_full_word_coefficients':len(result),'three_occurrence_row_controls':row_cases,'deleted_query_rejected':True}

if __name__=='__main__':
    import json
    print(json.dumps(run(),indent=2))
