"""Determinant witnesses for bounded supplied mixed singular pencil models.

The proof covers all fields and indices. This executable uses the retained
F2/F3/F4/F5 arithmetic and positive-index lifts in its stated bounded domain.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
from math import gcd
import importlib.util
import json

ROOT=Path(__file__).resolve().parent
for item in json.loads((ROOT/'INPUTS.json').read_text()):
    if sha256((ROOT/item['local']).read_bytes()).hexdigest()!=item['sha256']:
        raise ValueError('Frozen input '+item['local'])
spec=importlib.util.spec_from_file_location('credited_kronecker',ROOT/'source/pencil.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
Field=old.Field
need=old.require


def types(model):
    need(isinstance(model,(list,tuple)) and model,'nonempty supplied block model')
    grouped={}
    for item in model:
        need(isinstance(item,(list,tuple)) and len(item)==3,'block has orientation, index and multiplicity')
        side,e,r=item
        need(side in ('R','L') and type(e)is int and 0<=e<=5 and type(r)is int and 1<=r<=3,'bounded block domain')
        grouped[side,e]=grouped.get((side,e),0)+r
    need(all(r<=3 for r in grouped.values()),'bounded combined multiplicity')
    out=[(s,e,r) for (s,e),r in grouped.items()]
    out.sort(key=lambda x:(x[0]=='L',x[1] if x[0]=='R'else-x[1]))
    m=sum((e+(s=='L'))*r for s,e,r in out);n=sum((e+(s=='R'))*r for s,e,r in out)
    need(0<m<=16 and 0<n<=16,'both total dimensions must be positive and at most16')
    return out


def layout(model):
    out=[];m=n=0
    for side,e,r in types(model):
        a=(e+(side=='L'))*r;b=(e+(side=='R'))*r
        out.append(dict(side=side,e=e,r=r,row=m,col=n,m=a,n=b));m+=a;n+=b
    return out,m,n


def slices(model):
    parts,m,n=layout(model);a=[[0]*n for _ in range(m)];b=[[0]*n for _ in range(m)]
    for c in parts:
        r,e=c['r'],c['e']
        for i in range(e):
            for j in range(r):
                x,y=c['row']+i*r+j,c['col']+i*r+j;a[x][y]=1
                if c['side']=='R':b[x][y+r]=1
                else:b[x+r][y]=1
    return a,b


def character_data(model):
    parts=types(model);side,e,_=parts[0]
    ell=(e+1,e) if side=='R' else(e,e+1)
    vectors=[(j,-j-1) if s=='R' else(-j-1,j)for s,j,r in parts]
    a=sum(r*j*(j-1)//2 if s=='R'else-r*j*(j+1)//2 for s,j,r in parts)
    b=sum(-r*j*(j+1)//2 if s=='R'else r*j*(j-1)//2 for s,j,r in parts)
    values=[ell[0]*u+ell[1]*v for u,v in vectors];d=0
    for value in values:d=gcd(d,value)
    return dict(types=parts,vectors=vectors,ell=ell,slice_shift=(a,b),character_slice_exponent=-ell[0]*a-ell[1]*b,relation_values=values,power_index=d)


def character(model,triple,field):
    need(isinstance(triple,(tuple,list)) and len(triple)==3 and all(type(x)is int and 0<x<field.q for x in triple),'three nonzero field determinants')
    data=character_data(model);x,y,z=triple;l,h=data['ell']
    return field.mul(field.mul(field.power(x,l),field.power(y,h)),field.power(z,data['character_slice_exponent']))


def accepts(model,triple,field):
    c=character(model,triple,field);d=character_data(model)['power_index']
    return any(field.power(u,d)==c for u in range(1,field.q))


def extended(a,b):
    x0,x1,y0,y1=1,0,0,1
    while b:
        q,a,b=a//b,b,a%b;x0,x1=x1,x0-q*x1;y0,y1=y1,y0-q*y1
    return (a,x0,y0) if a>=0 else(-a,-x0,-y0)


def bezout(values):
    d=0;coeff=[]
    for value in values:
        d,a,b=extended(d,value);coeff=[a*x for x in coeff]+[b]
    need(sum(a*b for a,b in zip(coeff,values))==d,'Exact integral Bezout witness')
    return d,coeff


def block_diagonal(blocks):
    size=sum(len(a)for a in blocks);out=[[0]*size for _ in range(size)];offset=0
    for block in blocks:
        for i,row in enumerate(block):out[offset+i][offset:offset+len(block)]=row
        offset+=len(block)
    return out


def lift(model,action,scalars,field):
    parts=types(model);need(len(scalars)==len(parts),'one determinant per distinct type')
    need(len(action)==2 and all(len(row)==2 for row in action) and all(type(x)is int and 0<=x<field.q for row in action for x in row) and old.determinant(action,field)!=0,'invertible supplied slice action')
    ps=[];qs=[]
    for (side,e,r),u in zip(parts,scalars):
        need(type(u)is int and 0<u<field.q,'nonzero multiplicity determinant')
        d=old.identity(r);d[0][0]=u
        if e:p,q,_=old.lift(e,r,action,d,field)
        else:p,q=[],old.transpose(old.inverse(d,field))
        if side=='L':p,q=q,p
        ps.append(p);qs.append(q)
    return block_diagonal(ps),block_diagonal(qs),action


def witness(model,triple,field,action=None):
    need(accepts(model,triple,field),'mixed character excludes triple')
    data=character_data(model);chi=character(model,triple,field);d,coeff=bezout(data['relation_values'])
    need(d==data['power_index'],'Same character lattice index')
    root=next(u for u in range(1,field.q)if field.power(u,d)==chi)
    scalars=[field.power(root,c)for c in coeff]
    x,y,z=triple;a,b=data['slice_shift'];x=field.mul(x,field.power(z,-a));y=field.mul(y,field.power(z,-b))
    for u,(c,h)in zip(scalars,data['vectors']):x=field.mul(x,field.power(u,-c));y=field.mul(y,field.power(u,-h))
    correction=field.inv(field.mul(x,y));scalars[0]=field.mul(scalars[0],correction)
    if action is None:action=[[z,0],[0,1]]
    result=lift(model,action,scalars,field);a0,a1=slices(model)
    need(old.determinant(action,field)==z,'Prescribed slice determinant')
    need(old.fixes(a0,a1,result,field),'Literal mixed stabilizer witness')
    need(tuple(old.determinant(a,field)for a in result)==tuple(triple),'All requested determinants')
    return result


def hom_single(src,dst):
    """Return all coefficient-basis pairs U,C with U L_src=L_dst C."""
    s,e=src;t,f=dst
    ms,ns=e+(s=='L'),e+(s=='R');md,nd=f+(t=='L'),f+(t=='R')
    if s==t=='L':
        return [(old.transpose(c),old.transpose(u))for u,c in hom_single(('R',f),('R',e))]
    if s=='R' and t=='L':return []
    count=max(e-f+1,0) if s==t=='R' else e+f
    result=[]
    for k in range(count):
        if s==t=='R':
            u=[[int(j-i==k)for j in range(ms)]for i in range(md)]
            c=[[int(j-i==k)for j in range(ns)]for i in range(nd)]
        else:
            u=[[int(i+j==k)for j in range(ms)]for i in range(md)]
            c=[[int(i+j==k)for j in range(ns)]for i in range(nd)]
        result.append((u,c))
    return result


def fixed_slice_basis(model):
    parts,m,n=layout(model);out=[]
    for src in parts:
        for dst in parts:
            for u,c in hom_single((src['side'],src['e']),(dst['side'],dst['e'])):
                for i in range(dst['r']):
                    for j in range(src['r']):
                        p=[[0]*m for _ in range(m)];v=[[0]*n for _ in range(n)]
                        for a,row in enumerate(u):
                            for b,value in enumerate(row):p[dst['row']+a*dst['r']+i][src['row']+b*src['r']+j]=value
                        for a,row in enumerate(c):
                            for b,value in enumerate(row):v[dst['col']+a*dst['r']+i][src['col']+b*src['r']+j]=value
                        out.append([x for row in p+v for x in row])
    return out


def tensor_image(model,maps,field):
    first,second=slices(model);p,q,r=maps
    return [old.multiply(old.multiply(p,old.mix(first,second,*row,field),field),old.transpose(q),field)for row in r]


def correct_given_map(model,maps,field):
    """Preserve a supplied GL map's tensor image while making every determinant one."""
    _,m,n=layout(model);need(isinstance(maps,(tuple,list))and len(maps)==3,'three supplied factor maps')
    for matrix,size in zip(maps,(m,n,2)):
        need(isinstance(matrix,(tuple,list))and len(matrix)==size and all(isinstance(row,(tuple,list))and len(row)==size for row in matrix),'supplied map dimensions')
        need(all(type(x)is int and 0<=x<field.q for row in matrix for x in row),'supplied map field entries')
    triple=tuple(old.determinant(a,field)for a in maps);need(all(triple),'supplied maps are invertible')
    stabilizer=witness(model,triple,field)
    result=tuple(old.multiply(g,old.inverse(h,field),field)for g,h in zip(maps,stabilizer))
    need(all(old.determinant(a,field)==1 for a in result),'All corrected map determinants')
    need(tensor_image(model,result,field)==tensor_image(model,maps,field),'Same supplied tensor image')
    return result
