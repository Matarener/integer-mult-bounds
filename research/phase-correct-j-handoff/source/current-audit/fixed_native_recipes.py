"""Check fixed selected-native witnesses without rerunning their synthesis.

The recipe side uses physical monomial/C arithmetic. The source phase side
uses an independently accumulated affine X-character map and an integer Walsh
transform. Signed Pauli images plus one exact full source column determine a
Clifford operator including global phase. Apache-2.0; Codex assistance.
"""
import copy
from functools import lru_cache

def need(ok,message):
    if not ok:raise ValueError(message)
def parity(x):return x.bit_count()&1
def image(rows,x):return sum(parity(row&x)<<i for i,row in enumerate(rows))
def rank(rows):
    pivots={}
    for x in rows:
        while x:
            i=x.bit_length()-1
            if i in pivots:x^=pivots[i]
            else:pivots[i]=x;break
    return len(pivots)
@lru_cache(None)
def inverse_transpose(rows):
    n=len(rows);a=[row|(1<<(n+i))for i,row in enumerate(rows)]
    for i in range(n):
        pivot=next((j for j in range(i,n)if a[j]>>i&1),None)
        need(pivot is not None,'invertible literal ADDRESS')
        a[i],a[pivot]=a[pivot],a[i]
        for j in range(n):
            if i!=j and a[j]>>i&1:a[j]^=a[i]
    inv=[row>>n for row in a]
    return tuple(sum(((inv[j]>>i)&1)<<j for j in range(n))for i in range(n))

def literal(ce,n,circuit):
    result=ce.ident(n)
    for e in circuit:
        k=e[0]
        if k=='P':op=ce.perm(n,e[1])
        elif k=='C':op=ce.cgate(n,e[1],e[2])
        elif k=='D':op=ce.diag(n,e[1],e[2])
        elif k=='X':op=ce.xgate(n,e[1])
        elif k=='phase':op=ce.Op(n,ce.identity(n),[('phase',e[1]%4)])
        else:raise ValueError('uncovered literal '+k)
        result=result.then(op)
    return result

def x_description(n,circuit):
    rows=tuple(1<<i for i in range(n));offset=0;constant=0;terms={}
    for e in circuit:
        kind=e[0]
        if kind=='P':
            b=inverse_transpose(tuple(e[1]));rows=tuple(xor_selected(rows,row)for row in b);offset=image(b,offset)
        elif kind=='D':
            need(not any(e[1])and all(x%2==0 for x in e[2]),'source X-character diagonal is an actual Pauli')
            offset^=sum(((x//2)&1)<<i for i,x in enumerate(e[2]))
        elif kind in('C','X'):
            mask,coefficient=(e[1],e[2])if kind=='C'else(e[1],2)
            direction=xor_selected(rows,mask);flip=parity(mask&offset)
            constant=(constant+coefficient*flip)%4
            terms[direction]=(terms.get(direction,0)+coefficient*(-1 if flip else 1))%4
        elif kind=='phase':constant=(constant+e[1])%4
        else:raise ValueError('uncovered source X-character literal '+kind)
    return rows,offset,constant,tuple(sorted((mask,c)for mask,c in terms.items()if mask and c))
def xor_selected(rows,mask):
    out=0
    while mask:
        bit=mask&-mask;out^=rows[bit.bit_length()-1];mask^=bit
    return out
def polynomial(description,x):
    _,_,constant,terms=description
    return (constant+sum(c*parity(mask&x)for mask,c in terms))%4
def signature(description):
    rows,offset,c,_=description;n=len(rows)
    alpha=tuple((polynomial(description,1<<i)-c)%4 for i in range(n));quad=[]
    for i in range(n):
        row=0
        for j in range(i+1,n):
            d=(polynomial(description,(1<<i)|(1<<j))-c-alpha[i]-alpha[j])%4
            need(d%2==0,'quadratic source Gaussian phase');row|=(d//2)<<j
        quad.append(row)
    return rows,offset,c,alpha,tuple(quad)

UNITS=((1,0),(0,1),(-1,0),(0,-1))
def unit(value,p):
    a,b=value
    return ((a,b),(-b,a),(-a,-b),(b,-a))[p%4]
def normalize(state,denominator):
    state={x:v for x,v in state.items()if v!=(0,0)}
    while denominator and all(not((a|b)&1)for a,b in state.values()):
        state={x:(a//2,b//2)for x,(a,b)in state.items()};denominator-=1
    return state,denominator
def source_zero_column(n,circuit):
    description=x_description(n,circuit);rows,offset,_,_=description
    values=[(0,0)]*(1<<n)
    for x in range(1<<n):values[image(rows,x)^offset]=UNITS[polynomial(description,x)]
    step=1
    while step<len(values):
        for first in range(0,len(values),2*step):
            for j in range(first,first+step):
                a,b=values[j];c,d=values[j+step];values[j]=(a+c,b+d);values[j+step]=(a-c,b-d)
        step*=2
    return normalize(dict(enumerate(values)),n)

def validate_monomial(n,record):
    need(isinstance(record,dict),'fixed monomial recipe present')
    rows=record['matrix_rows'];quad=record['quadratic_rows'];alpha=record['linear_Z4'];bound=1<<n
    need(len(rows)==len(quad)==len(alpha)==n,'fixed monomial dimensions')
    need(all(type(x)is int and 0<=x<bound for x in rows+quad),'fixed monomial binary row domain')
    need(rank(rows)==n,'fixed monomial invertible ADDRESS')
    need(all(((quad[i]>>j)&1)==((quad[j]>>i)&1)for i in range(n)for j in range(n)),'fixed monomial symmetric quadratic')
    need(all(type(x)is int and 0<=x<4 and x%2==((quad[i]>>i)&1)for i,x in enumerate(alpha)),'fixed monomial exact Z4 diagonal')
    need(type(record['offset'])is int and 0<=record['offset']<bound,'fixed monomial offset domain')
    need(type(record['phase'])is int and 0<=record['phase']<4,'fixed monomial phase domain')
def monomial(ce,n,record):
    validate_monomial(n,record)
    return ce.diag(n,record['quadratic_rows'],record['linear_Z4']).then(ce.perm(n,record['matrix_rows'])).then(ce.xgate(n,record['offset'])).then(ce.Op(n,ce.identity(n),[('phase',record['phase'])]))
def monomial_phase(record,x):
    n=len(record['matrix_rows']);phase=record['phase']+sum(a for i,a in enumerate(record['linear_Z4'])if x>>i&1)
    phase+=2*sum(parity(row&x&~((1<<(i+1))-1))for i,row in enumerate(record['quadratic_rows'])if x>>i&1)
    return phase%4
def recipe_zero_column(n,record):
    r=record['rank']
    if r==0:
        left=record['left'];return {left['offset']:UNITS[monomial_phase(left,0)]},0
    right,left=record['right'],record['left'];state={right['offset']:UNITS[monomial_phase(right,0)]}
    for i in range(r):
        out={}
        for x,(a,b)in state.items():
            for y,v in ((x,(a-b,a+b)),(x^(1<<i),(a+b,b-a))):
                u,w=out.get(y,(0,0));out[y]=(u+v[0],w+v[1])
        state=out
    out={image(left['matrix_rows'],x)^left['offset']:unit(v,monomial_phase(left,x))for x,v in state.items()}
    return normalize(out,r)

def check_entry(ce,entry):
    n=len(entry['one_coordinate_tableau'])//2
    recipe=entry.get('selected_native_recipe');need(isinstance(recipe,dict),'fixed selected-native recipe missing')
    actual=literal(ce,n,entry['one_coordinate_definition_circuit'])
    need(actual.tab==tuple(tuple(t)for t in entry['one_coordinate_tableau']),'source signed tableau rebuilt from literal circuit')
    r=recipe['rank'];need(type(r)is int and 0<=r<=n and r==rank(x for x,z,p in actual.tab[n:]),'actual selected native rank')
    left=monomial(ce,n,recipe['left'])
    if r:
        right=monomial(ce,n,recipe['right']);compiled=right.then(ce.fourier(n,range(r))).then(left)
    else:
        need(recipe['right']is None,'zero-rank right recipe absent');compiled=left
    need(compiled.tab==actual.tab,'compiled signed source tableau')
    need(recipe_zero_column(n,recipe)==source_zero_column(n,entry['one_coordinate_definition_circuit']),'fixed recipe exact source Gaussian column')
    return dict(bits=n,rank=r,source_column_entries=1<<n)

def embed(circuit,n,axes):
    d=len(axes)
    def bits(value):return sum(1<<axes[i]for i in range(d)if value>>i&1)
    out=[]
    for e in circuit:
        if e[0]=='P':
            rows=[1<<i for i in range(n)]
            for i,row in enumerate(e[1]):rows[axes[i]]=bits(row)
            out.append(['P',rows])
        elif e[0]=='D':
            rows=[0]*n;alpha=[0]*n
            for i,row in enumerate(e[1]):rows[axes[i]]=bits(row);alpha[axes[i]]=e[2][i]
            out.append(['D',rows,alpha])
        elif e[0]in('C','X'):out.append([e[0],bits(e[1]),*e[2:]])
        elif e[0]=='phase':out.append(list(e))
        else:raise ValueError('uncovered embedded recipe literal')
    return out

def audit_fixture(ce,fixture):
    pool=fixture['native_recipe_pool'];checks=[]
    for name,entry in pool.items():checks.append(dict(name=name,**check_entry(ce,entry)))
    count=0;n=fixture['ambient_arity']
    for event in fixture['full_events']+fixture['inverse_events']:
        if event['kind']!='NATIVE':continue
        need(event.get('native_recipe_id')in pool,'every paid native event has retained recipe')
        entry=pool[event['native_recipe_id']];d=len(entry['one_coordinate_tableau'])//2;axes=event['recipe_embedding']
        need(len(axes)==d and len(set(axes))==d and all(type(i)is int and 0<=i<n for i in axes),'actual native recipe embedding')
        need(event['phase_exponent']==entry['phase_exponent'],'all-f once-per-field phase tag')
        need(event['rank_per_f']==entry['selected_native_recipe']['rank'],'actual paid recipe rank')
        source=embed(entry['one_coordinate_definition_circuit'],n,axes)
        need(signature(x_description(n,source))==signature(x_description(n,event['one_coordinate_literal_circuit'])),'embedded recipe source including exact Gaussian phase')
        count+=1
    # A wrong global phase preserves tableau and rank, and must fail the
    # separate physical Gaussian column comparison.
    good=copy.deepcopy(next(iter(pool.values())))
    good['selected_native_recipe']['left']['phase']=(good['selected_native_recipe']['left']['phase']+1)%4
    good['selected_native_recipe']['right']['phase']=(good['selected_native_recipe']['right']['phase']-1)%4
    check_entry(ce,good)
    entry=copy.deepcopy(next(iter(pool.values())));entry['selected_native_recipe']['left']['phase']=(entry['selected_native_recipe']['left']['phase']+1)%4
    try:check_entry(ce,entry)
    except ValueError as error:need('fixed recipe exact source Gaussian column'in str(error),'wrong phase control predicate')
    else:raise ValueError('wrong recipe global phase accepted')
    wrong=copy.deepcopy(next(iter(pool.values())));wrong['selected_native_recipe']['rank']+=1
    try:check_entry(ce,wrong)
    except ValueError as error:need('actual selected native rank'in str(error),'wrong rank control predicate')
    else:raise ValueError('wrong selected native rank accepted')
    return dict(q=fixture['q'],fixed_recipes=checks,paid_event_embeddings=count,wrong_global_phase_rejected=True,wrong_rank_rejected=True,equivalent_phase_gauge_accepted=True,operator_lemma='Complete signed Pauli images and one exact nonzero input-column equality prove the whole Clifford including global phase; the source column is independently computed by integer Walsh arithmetic.')
