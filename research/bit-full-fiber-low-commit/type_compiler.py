# SPDX-License-Identifier: Apache-2.0
"""Pre-input finite type compilation; no runtime payload or width arguments."""
from fractions import Fraction
from itertools import product
from math import isqrt


def inverse(a,q):
    n=len(a)
    rows=[list(row)+[int(i==j) for j in range(n)] for i,row in enumerate(a)]
    for j in range(n):
        i=next((i for i in range(j,n) if rows[i][j]%q),None)
        if i is None:
            raise ValueError('singular matrix')
        rows[i],rows[j]=rows[j],rows[i]
        c=pow(rows[j][j],-1,q)
        rows[j]=[x*c%q for x in rows[j]]
        for i in range(n):
            if i!=j:
                c=rows[i][j]
                rows[i]=[(x-c*y)%q for x,y in zip(rows[i],rows[j])]
    return [row[n:] for row in rows]


def right_action(g,a,q):
    n=len(a)
    return tuple(sum(g[r*n+j]*a[j][k] for j in range(n))%q
                 for r in range(n) for k in range(n))


def compile_types(q, matrix, inverse_direction=False):
    if type(q) is not int or q<3 or any(q%d==0 for d in range(2,isqrt(q)+1)):
        raise ValueError('odd prime fixed radix')
    n=len(matrix)
    if n<1 or any(len(row)!=n for row in matrix) or type(inverse_direction) is not bool:
        raise ValueError('fixed square matrix and direction')
    a=[[Fraction(v).numerator*pow(Fraction(v).denominator,-1,q)%q for v in row] for row in matrix]
    ai=inverse(a,q)
    if inverse_direction:
        a=ai
    types=[]
    for g in product(range(q),repeat=n*n):
        try:
            inverse([g[i*n:(i+1)*n] for i in range(n)],q)
        except ValueError:
            continue
        types.append(g)
    index={g:i for i,g in enumerate(types)}
    permutation=[index[right_action(g,a,q)] for g in types]
    bits=(q-1).bit_length()
    cache=[(x>>j)&1 for g in types for x in g for j in range(bits)]
    return types,permutation,cache
