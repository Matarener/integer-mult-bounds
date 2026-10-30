"""Independent exact checks for the connector theorem and escape word.

The default replay uses no search program, solver, or predecessor code.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import itertools
import json
from pathlib import Path
import random

PACKAGE=Path(__file__).resolve().parent

def require(value,message):
    if not value:raise ValueError(message)

def eye(n):return tuple(1<<i for i in range(n))
def add(a,b):return tuple(x^y for x,y in zip(a,b))
def zero(n):return (0,)*n

def mul(a,b):
    return tuple(sum((sum((row>>k&1)*(b[k]>>j&1) for k in range(len(b)))%2)<<j for j in range(len(b))) for row in a)

def rank(a):
    basis={}
    for row in a:
        while row:
            j=row.bit_length()-1
            if j not in basis:basis[j]=row;break
            row^=basis[j]
    return len(basis)

def inverse(a):
    n=len(a);rows=[row|(1<<(n+i)) for i,row in enumerate(a)]
    for j in range(n):
        p=next(i for i in range(j,n) if rows[i]>>j&1);rows[j],rows[p]=rows[p],rows[j]
        for i in range(n):
            if i!=j and rows[i]>>j&1:rows[i]^=rows[j]
    return tuple(row>>n for row in rows)

def product(a,b):
    n=len(next(iter(a.values())));out={}
    for x,ax in a.items():
        for y,by in b.items():
            if x[0]+y[0]>1:continue
            key=tuple(u+v for u,v in zip(x,y));out[key]=add(out.get(key,zero(n)),mul(ax,by))
    return {k:v for k,v in out.items() if any(v)}

def replay(calls,order,g):
    n=len(calls[0]['p']);base=(0,)*(g+1);ebit=(1,)+(0,)*g
    word={base:eye(n)};expected={base:eye(n),ebit:eye(n)};targets=[zero(n) for _ in range(g)]
    for c in calls:
        if c['stage']<g:targets[c['stage']]=add(targets[c['stage']],c['p'])
    for j,e in enumerate(targets):
        d=list(base);d[j+1]=1;expected=product({base:eye(n),tuple(d):e},expected)
    for i in order:
        c=calls[i];r=tuple(c['r']);gate={base:eye(n),ebit:r}
        if c['stage']<g:
            d=list(base);d[c['stage']+1]=1;ed=d.copy();ed[0]=1
            gate[tuple(d)]=tuple(c['p']);gate[tuple(ed)]=r
        word=product(gate,word)
    return word,expected

def escape():
    data=json.loads((PACKAGE/'ESCAPE-WORD.json').read_text());calls=data['calls'];order=data['order'];n=8;g=3
    require(sorted(order)==list(range(14)),'Escape order inventory')
    require([c['stage'] for c in calls]==[0,0,1,1,2,2]+[3]*8,'Escape stage inventory')
    total=zero(n)
    for i,c in enumerate(calls):
        p=tuple(c['p']);r=tuple(c['r']);require(len(p)==len(r)==n,'Matrix size')
        require(all(isinstance(v,int) and 0<=v<1<<n for v in p+r),'Binary matrix encoding')
        require(rank(r)==1 and mul(r,r)==zero(n),'Query rank and square')
        if i<6:
            require(rank(p)==2 and mul(p,p)==p,'Full projector')
            require(mul(p,r)==r and mul(r,p)==r,'Full compatibility')
        else:require(p==zero(n),'Thin call has no stage')
        total=add(total,r)
    require(total==eye(n),'Total query')
    for j in range(g):
        a,b=calls[2*j:2*j+2];e=tuple(1<<i if i in (0,1,2*j+2,2*j+3) else 0 for i in range(n))
        require(add(a['p'],b['p'])==e and mul(a['p'],b['p'])==zero(n),'Paired target resolution')
        t=[0]*n
        for channel in range(2):
            value=(1<<channel)|(1<<(2*j+2+channel));t[channel]=value;t[2*j+2+channel]=value
        require(add(a['r'],b['r'])==tuple(t),'Grouped star query')
    word,expected=replay(calls,order,g);require(word==expected,'Complete escape word')
    changed=[dict(c) for c in calls];changed[order[-1]]=dict(changed[order[-1]],r=[0]*n)
    require(replay(changed,order,g)[0]!=expected,'Deleted query control')
    shifted=order.copy();shifted[0],shifted[-1]=shifted[-1],shifted[0]
    require(replay(calls,shifted,g)[0]!=expected,'Moved call control')
    thin=calls[6:];columns=[];rows=[]
    for leaf in range(3):
        block=(2*leaf+2,2*leaf+3)
        columns.append(tuple(tuple((c['r'][i]>>j)&1 for i in range(n) for j in block) for c in thin))
        rows.append(tuple(tuple(c['r'][i] for i in block) for c in thin))
    require(len(set(columns))==3 and len(set(rows))==3,'The word must leave both equal-signature classes')
    trap=json.loads((PACKAGE/'MIXED-ONLY-CANDIDATE.json').read_text());wrong,wanted=replay(trap['calls'],trap['order'],g)
    for j in range(g):
        key=[1,0,0,0];key[j+1]=1
        require(wrong.get(tuple(key),zero(n))==wanted.get(tuple(key),zero(n)),'First mixed coefficient control')
    require(all(wrong.get(k,zero(n))==wanted.get(k,zero(n)) for k in wrong.keys()|wanted.keys() if k[0]==0),'Pure stage word control')
    require(wrong!=wanted,'Full-word trap must fail')
    return {'first_mixed_false_positive_rejected':True,'fields':n,'full_calls':6,'thin_queries':8,'full_polynomial_coefficients':len(word),'deleted_query_rejected':True,'moved_call_rejected':True,'distinct_leaf_column_signatures':3,'distinct_leaf_row_signatures':3}

# Polynomials in three free, noncommuting variables over F2.
ONE=frozenset(((),));Z=frozenset()
def times(a,b):
    result=set()
    for x in a:
        for y in b:
            w=x+y
            if w in result:result.remove(w)
            else:result.add(w)
    return frozenset(result)

def pair_equations(order):
    projections=[(frozenset(((j,),)),ONE^frozenset(((j,),))) for j in range(3)];eq=[]
    for j in range(3):
        for h,k in itertools.product(range(2),repeat=2):
            p=times(projections[j][h],projections[j][k])^(projections[j][h] if h==k else Z)
            if p:eq.append(p)
    ordered={}
    for j,k in itertools.permutations(range(3),2):
        p=Z
        for pos,(c,h) in enumerate(order):
            if c!=j:continue
            for d,l in order[pos+1:]:
                if d==k:p^=times(projections[j][h],projections[k][l])
        ordered[j,k]=p
    for j in range(3):
        k,l=[x for x in range(3) if x!=j];eq.append(ordered[j,k]^ordered[j,l])
    return eq

def orders():
    result=[]
    for word in sorted(set(itertools.permutations((0,0,1,1,2,2)))):
        if not word.index(0)<word.index(1)<word.index(2):continue
        seen=set();out=[]
        for j in word:out.append([j,int(j in seen)]);seen.add(j)
        result.append(out)
    return result

def certificates():
    records=json.loads((PACKAGE/'PAIR-CERTIFICATES.json').read_text());require([r['order'] for r in records]==orders(),'Complete pair order list')
    terms=0;maximum=0
    for record in records:
        eq=pair_equations(record['order']);value=set()
        for index,left,right in record['terms']:
            require(0<=index<len(eq),'Certificate equation index')
            require(all(0<=i<3 for i in left+right),'Certificate variable index')
            value^={tuple(left)+word+tuple(right) for word in eq[index]}
            maximum=max(maximum,len(left)+len(right)+max(map(len,eq[index]),default=0));terms+=1
        require(value=={()},'Free-algebra certificate')
    corrupted=json.loads(json.dumps(records[0]));corrupted['terms']=corrupted['terms'][1:];value=set();eq=pair_equations(corrupted['order'])
    for index,left,right in corrupted['terms']:value^={tuple(left)+w+tuple(right) for w in eq[index]}
    require(value!={()},'Deleted certificate term control')
    return {'orders':len(records),'terms':terms,'maximum_degree':maximum,'deleted_term_rejected':True}

def scalar_multiply(a,b):
    out=0
    while b:
        if b&1:out^=a
        b>>=1;a<<=1
    return out

def determinant_polynomial(matrix):
    n=len(matrix);out=0
    for permutation in itertools.permutations(range(n)):
        value=1
        for i,j in enumerate(permutation):value=scalar_multiply(value,matrix[i][j])
        out^=value
    return out

def prefix_controls():
    checked=0;updates=0;rejections=0;rng=random.Random(20261026)
    for n in (2,3,4):
        for trial in range(20):
            change=list(eye(n))
            for _ in range(5*n):
                i,j=rng.sample(range(n),2);change[i]^=change[j]
            change=tuple(change);back=inverse(change)
            flags=[mul(mul(change,tuple(1<<i if i==j else 0 for i in range(n))),back) for j in range(n)]
            if trial%2:
                upper=[tuple((1<<i)|sum(rng.randrange(2)<<k for k in range(i+1,n)) if j==i else 0 for j in range(n)) for i in range(n)]
                flags=[mul(mul(change,a),back) for a in upper]
            else:rng.shuffle(flags)
            prefix=zero(n);poly={0:eye(n)}
            for a in flags:
                require(mul(a,prefix)==zero(n),'Prefix annihilation')
                changed=dict(poly)
                for degree,coefficient in poly.items():changed[degree+1]=add(changed.get(degree+1,zero(n)),mul(a,coefficient))
                poly={k:v for k,v in changed.items() if any(v)};prefix=add(prefix,a)
                require(poly=={0:eye(n),1:prefix},'Prefix product factorization');updates+=1
            determinant=determinant_polynomial([[int(i==j)|(((prefix[i]>>j)&1)<<1) for j in range(n)] for i in range(n)])
            expected=1
            for _ in range(n):expected=scalar_multiply(expected,3)
            require(determinant==expected,'Projection determinant');checked+=1
            require(mul(flags[0],prefix)!=zero(n),'A completed resolution cannot restart this prefix walk');rejections+=1
    return {'matrix_flags':checked,'prefix_updates':updates,'projection_determinants':checked,'restarted_walks_rejected':rejections}

def rank_cut(g,d,field_size):
    require(g>=3 and d>=1 and field_size>=2 and field_size&(field_size-1)==0,'Rank-cut parameters');h=0
    while 2*field_size**(d*h)<g:h+=1
    return 2*d+2*h

def rank_controls():
    cases=[]
    for g in (3,4,7,8,9,31,32,33,63,127,128,129,255):
        lower=rank_cut(g,2,2);cases.append({'g':g,'d':2,'field_size':2,'thin_rank_lower_bound':lower})
        h=(lower-4)//2
        require(2*2**(2*h)>=g and (h==0 or 2*2**(2*(h-1))<g),'Least signature dimension')
    for g in (3,4,5):
        d=2;n=d*(g+1);k=[0]*n
        for i in range(d):
            if (g+1)%2:k[i]^=1<<i
            for j in range(1,g+1):k[i]^=1<<(d*j+i);k[d*j+i]^=1<<i
        require(rank(k)==2*d,'Thin residual rank, even and odd leaf counts')
    require(rank_cut(127,2,2)==10,'One-port 127-leaf cut')
    require(rank_cut(31,2,2)==8 and rank_cut(31,4,2)==10,'Five-query coupling boundary')
    require(rank_cut(127,208,2)==418,'Coupled ports use the actual block dimension')
    return cases


def put(rows,block,row,col,d):
    for i,value in enumerate(block):rows[row*d+i]^=value<<(col*d)

def block(matrix,row,col,d):return tuple((matrix[row*d+i]>>(col*d))&((1<<d)-1) for i in range(d))

def chronology_controls():
    rng=random.Random(57721);cases=0;coefficient_checks=0;prefix_checks=0;one_sided=0
    for m,q in ((2,1),(3,1),(2,2)):
        d=m*q;g=3;n=4*d
        for trial in range(2):
            calls=[];parameters=[];targets=[]
            for j in range(g):
                basis=list(eye(d))
                for _ in range(5*d):
                    a,b=rng.sample(range(d),2);basis[a]^=basis[b]
                basis=tuple(basis);back=inverse(basis);x=tuple(rng.randrange(1<<d) for _ in range(d));aa=[];e=[0]*n
                for b in (0,j+1):put(e,eye(d),b,b,d)
                targets.append(tuple(e))
                for h in range(m):
                    diagonal=tuple(1<<i if h*q<=i<(h+1)*q else 0 for i in range(d))
                    a=mul(mul(basis,diagonal),back);b=add(mul(x,a),mul(a,x));p=[0]*n;r=[0]*n
                    for row,col in itertools.product((0,j+1),repeat=2):put(p,add(a,b) if row==col else b,row,col,d);put(r,a,row,col,d)
                    calls.append({'stage':j,'p':tuple(p),'r':tuple(r),'a':a});aa.append(a)
                parameters.append(aa)
            total=zero(n)
            for c in calls:total=add(total,c['r'])
            for _ in range(4):
                z=[0]*n
                for row in range(4):
                    u=tuple(rng.randrange(1<<d) for _ in range(d));v=tuple(rng.randrange(1<<d) for _ in range(d))
                    put(z,u,row,0,d)
                    for col in range(1,4):put(z,v,row,col,d)
                calls.append({'stage':3,'p':zero(n),'r':tuple(z)});total=add(total,z)
            calls.append({'stage':3,'p':zero(n),'r':add(total,eye(n))});order=list(range(len(calls)));rng.shuffle(order)
            good_order=[i for i in order if calls[i]['stage']<3];s={}
            for j,k in itertools.permutations(range(3),2):
                value=zero(d)
                for pos,i in enumerate(good_order):
                    if calls[i]['stage']!=j:continue
                    for h in good_order[pos+1:]:
                        if calls[h]['stage']==k:value=add(value,mul(calls[i]['a'],calls[h]['a']))
                s[j,k]=value
            prefixes=[zero(d) for _ in range(3)]
            for i in good_order:
                j=calls[i]['stage'];a=calls[i]['a']
                for k in range(3):
                    if k==j:continue
                    require(mul(a,s[j,k])==mul(a,add(eye(d),prefixes[k])),'Projected chronology prefix');prefix_checks+=1
                prefixes[j]=add(prefixes[j],a)
            failures=0
            for j in range(3):
                defect=zero(n);tail=zero(n)
                for i in reversed(order):
                    c=calls[i]
                    if c['stage']==j:defect=add(defect,add(mul(c['p'],tail),mul(tail,c['p'])))
                    tail=add(tail,c['r'])
                k,l=[x for x in range(3) if x!=j]
                observed=add(add(block(defect,0,k+1,d),block(defect,j+1,k+1,d)),add(block(defect,0,l+1,d),block(defect,j+1,l+1,d)))
                require(observed==add(s[j,k],s[j,l]),'Equal-column cancellation');failures+=any(observed)
                # Keep one independent D variable, without setting Q to one.
                local=[]
                for c in calls:local.append({'stage':0 if c['stage']==j else 1,'p':c['p'] if c['stage']==j else zero(n),'r':c['r']})
                word,_=replay(local,order,1)
                require(word.get((1,1),zero(n))==add(targets[j],defect),'Literal mixed coefficient');coefficient_checks+=1
            require(failures>0,'One-sided connector must fail a necessary equation')
            z=calls[-2]['r'];one_sided+=block(z,1,0,d)!=block(z,2,0,d);cases+=1
    require(one_sided>0,'Controls must leave the old two-sided aggregate contract')
    return {'coupled_frames':cases,'literal_mixed_coefficients':coefficient_checks,'prefix_equations':prefix_checks,'one_sided_nonaggregate_frames':one_sided}


def run():
    return {'escape':escape(),'paired_certificates':certificates(),'prefix':prefix_controls(),'rank_cut_cases':rank_controls(),'chronology':chronology_controls()}

if __name__=='__main__':print(json.dumps(run(),indent=2))
