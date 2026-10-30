"""Literal linear-equation oracle for mixed pencil stabilizers.

No character formula, Hom recurrence or symmetric-power lift is used here.
The supplied field operations are shared exact arithmetic.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import product


def nullspace(rows,columns,field):
    a=[row[:]for row in rows];pivots=[];at=0
    for col in range(columns):
        pivot=next((i for i in range(at,len(a))if a[i][col]),None)
        if pivot is None:continue
        a[at],a[pivot]=a[pivot],a[at];scale=field.inv(a[at][col]);a[at]=[field.mul(scale,x)for x in a[at]]
        for i in range(len(a)):
            if i!=at and a[i][col]:
                scale=a[i][col];a[i]=[field.sub(x,field.mul(scale,y))for x,y in zip(a[i],a[at])]
        pivots.append(col);at+=1
    out=[]
    for free in sorted(set(range(columns))-set(pivots)):
        v=[0]*columns;v[free]=1
        for i,p in enumerate(pivots):v[p]=field.neg(a[i][free])
        out.append(v)
    return out


def equations(source,target,src_dims,dst_dims,field):
    ms,ns=src_dims;md,nd=dst_dims;columns=md*ms+nd*ns;rows=[]
    for a,b in zip(source,target):
        for i in range(md):
            for j in range(ns):
                row=[0]*columns
                for k in range(ms):row[i*ms+k]=a[k][j]
                for k in range(nd):row[md*ms+k*ns+j]=field.neg(b[i][k])
                rows.append(row)
    return rows,columns


def stabilizer_space(first,second,action,field):
    m,n=len(first),len(first[0]);mixed=[]
    for x,y in action:mixed.append([[field.add(field.mul(x,a),field.mul(y,b))for a,b in zip(row,other)]for row,other in zip(first,second)])
    rows,columns=equations(mixed,(first,second),(m,n),(m,n),field)
    return nullspace(rows,columns,field)


def determinant(a,field):
    """Row elimination for complete literal matrix domains."""
    rows=[row[:]for row in a];out=1
    for k in range(len(rows)):
        pivot=next((i for i in range(k,len(rows))if rows[i][k]),None)
        if pivot is None:return 0
        if pivot!=k:rows[k],rows[pivot]=rows[pivot],rows[k];out=field.neg(out)
        diagonal=rows[k][k];out=field.mul(out,diagonal);inv=field.inv(diagonal)
        for i in range(k+1,len(rows)):
            factor=field.mul(rows[i][k],inv)
            for j in range(k,len(rows)):rows[i][j]=field.sub(rows[i][j],field.mul(factor,rows[k][j]))
    return out


def enumerate_space(basis,m,n,field,limit=60000):
    if field.q**len(basis)>limit:raise ValueError('explicit oracle domain exceeds enumeration limit')
    columns=m*m+n*n;image=set();invertible=0
    for coefficients in product(range(field.q),repeat=len(basis)):
        v=[0]*columns
        for a,row in zip(coefficients,basis):
            if a:v=[field.add(x,field.mul(a,y))for x,y in zip(v,row)]
        p=[v[i*m:(i+1)*m]for i in range(m)];offset=m*m;c=[v[offset+i*n:offset+(i+1)*n]for i in range(n)]
        x,z=determinant(p,field),determinant(c,field)
        if x and z:image.add((x,field.inv(z)));invertible+=1
    return image,invertible
