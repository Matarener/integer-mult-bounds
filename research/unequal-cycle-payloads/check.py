"""Exact small matrices, source principal-core binding and large compressed recipes."""
from collections import Counter
from hashlib import sha256
from itertools import product
import json
import random

from cycle import construct, matrix, fits, need, minimum
import source


def rank_mod(a, prime):
    a = [[x%prime for x in row] for row in a]
    rank = 0
    for col in range(len(a[0]) if a else 0):
        pivot = next((i for i in range(rank,len(a)) if a[i][col]),None)
        if pivot is None:continue
        a[rank],a[pivot] = a[pivot],a[rank]
        inv = pow(a[rank][col],-1,prime)
        a[rank] = [x*inv%prime for x in a[rank]]
        for i in range(rank+1,len(a)):
            c=a[i][col]
            a[i]=[(x-c*y)%prime for x,y in zip(a[i],a[rank])]
        rank+=1
    return rank


def principal(d,model):
    need(len(d)==112 and all(type(x) is int and x>=0 for x in d), 'actual port dimensions')
    widths = [sum(d[p] for p in model['pairs'][i]) for i in model['core']]
    separate = sum(d[p] for i in model['clique'] for p in model['pairs'][i])
    recipe=construct(widths)
    return dict(core_widths=widths,separated_dimension=separate,
                principal_minimum=separate+recipe['rank'],recipe=recipe)


def charted_fixture():
    d=(2,2,3,1,4)
    recipe=construct(d);a=matrix(recipe)
    offsets=[sum(d[:i]) for i in range(5)]
    charts=[];inverses=[]
    for i,n in enumerate(d):
        p=[[int(x==y) for y in range(n)] for x in range(n)]
        inv=[row[:] for row in p]
        if n>=2:
            x,y=(0,1) if i%2==0 else (1,0)
            p[x][y]=1;inv[x][y]=-1
        charts.append(p);inverses.append(inv)
    transformed=[[0]*sum(d) for _ in range(sum(d))]
    for i in range(5):
        for j in range(5):
            for x in range(d[i]):
                for y in range(d[j]):
                    transformed[offsets[i]+x][offsets[j]+y]=sum(
                        charts[i][x][u]*a[offsets[i]+u][offsets[j]+v]*inverses[j][v][y]
                        for u in range(d[i]) for v in range(d[j]))
    fits(transformed,d)
    need(transformed!=a,'nontrivial directed chart changes')
    need(any(transformed[i][j]!=transformed[j][i] for i in range(sum(d)) for j in range(sum(d))),
         'nonsymmetric fitting fixture')
    need(all(rank_mod(transformed,p)==recipe['rank'] for p in (2,3,101)), 'charted exact rank')
    p,q=charts[:2]
    mul=lambda x,y:[[sum(x[i][k]*y[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    need(mul(p,q)!=mul(q,p),'noncommuting equal-size charts')
    return dict(dimensions=list(d),rank=recipe['rank'],matrix=transformed)


def run():
    model=source.model();digest=sha256();branches=Counter()
    for d in product(range(4),repeat=5):
        recipe=construct(d);a=matrix(recipe);fits(a,d)
        need(all(rank_mod(a,p)==recipe['rank'] for p in (2,3,101)), 'actual finite-field fitting rank')
        branches[recipe['branch']]+=1
        digest.update(json.dumps(recipe,sort_keys=True,separators=(',',':')).encode())
    rng=random.Random(40);large=[]
    for _ in range(80):
        d=[rng.getrandbits(512) for _ in range(5)]
        recipe=construct(d);large.append(recipe)
    giant=construct([2**10000,1,2,3,4])
    # Store a digest rather than printing 3,011 decimal digits for this fixture.
    large_digest=sha256(json.dumps(large,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    uniform=[]
    for n in range(1,17):
        row=principal([n]*112,model)
        need(row['principal_minimum']==49*n,'recover retained uniform 49d obstruction')
        uniform.append(row['principal_minimum'])
    d=[1+(40+7*i)%4 for i in range(112)]
    mixed=principal(d,model)
    core_matrix=matrix(mixed['recipe'])
    w=mixed['separated_dimension'];n=w+len(core_matrix)
    actual=[[int(i==j) if i<w and j<w else
             core_matrix[i-w][j-w] if i>=w and j>=w else 0 for j in range(n)] for i in range(n)]
    need(all(rank_mod(actual,p)==mixed['principal_minimum'] for p in (2,3,101)),
         'actual 54-port principal matrix attains bound')
    mixed['principal_matrix_size']=n
    return dict(small_cases=4**5,field_ranks=3*4**5,small_sha256=digest.hexdigest(),branches=dict(branches),
                seed=40,large_cases=80,large_sha256=large_digest,
                giant_rank_offset=giant['rank']-2**10000,giant_recipe_integers=11,
                core=model['core'],clique=model['clique'],selected_payload_sha256=model['payload_sha256'],
                uniform_49d=uniform,unequal_principal=mixed,charted=charted_fixture())
