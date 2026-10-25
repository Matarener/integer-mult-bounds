#!/usr/bin/env python3
"""Check a rational uniform operator bound for a physical transfer family.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction as Q
import json
from pathlib import Path


def scalar(x):
    if type(x) not in (int,str): raise ValueError('use exact rational values')
    return Q(x)


def matrix(a,n,m):
    if not isinstance(a,list) or len(a)!=n or any(not isinstance(r,list) or len(r)!=m for r in a):
        raise ValueError('matrix shape mismatch')
    return [[scalar(x) for x in r] for r in a]


def eye(n): return [[Q(i==j) for j in range(n)] for i in range(n)]
def transpose(a): return list(map(list,zip(*a)))
def mul(a,b): return [[sum(x*y for x,y in zip(r,c)) for c in zip(*b)] for r in a]
def sub(a,b): return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def scale(c,a): return [[c*x for x in r] for r in a]


def psd(a,strict=False):
    if a!=transpose(a): return False
    a=[list(r) for r in a]
    for k in range(len(a)):
        pivot=a[k][k]
        if pivot<0: return False
        if pivot==0:
            if strict or any(a[k][j] for j in range(k+1,len(a))): return False
        else:
            for i in range(k+1,len(a)):
                for j in range(k+1,len(a)):
                    a[i][j]-=a[i][k]*a[k][j]/pivot
    return True


def check(data):
    D,d=data['transfer_dimension'],data['local_dimension']
    if type(D) is not int or type(d) is not int or min(D,d)<1:
        raise ValueError('dimensions must be positive integers')
    P=matrix(data['metric'],D,D)
    F=matrix(data['left'],len(data['left']),D)
    if not F: raise ValueError('empty output roles')
    B=matrix(data['right'],D,len(data['right'][0]))
    if not B[0]: raise ValueError('empty input roles')
    raw=data['transitions']
    if len(raw)!=d or any(len(row)!=d for row in raw): raise ValueError('incomplete physical table')
    T=[[matrix(raw[y][x],D,D) for x in range(d)] for y in range(d)]
    a,b,c=[scalar(data[k]) for k in ('left_bound','right_bound','squared_rate')]
    if min(a,b,c)<0 or c>1: raise ValueError('invalid uniform-bound scalar')
    if not psd(P,strict=True): raise ValueError('metric is not positive definite')
    if not psd(sub(scale(a,P),mul(transpose(F),F))): raise ValueError('left boundary bound fails')
    if not psd(sub(scale(b,eye(len(B[0]))),mul(transpose(B),mul(P,B)))):
        raise ValueError('right boundary bound fails')
    gram=[[Q(0) for _ in range(d*D)] for _ in range(d*D)]
    for x in range(d):
        for xp in range(d):
            block=scale(c,P) if x==xp else scale(Q(0),P)
            for y in range(d): block=sub(block,mul(transpose(T[y][x]),mul(P,T[y][xp])))
            for i in range(D):
                for j in range(D): gram[x*D+i][xp*D+j]=block[i][j]
    if not psd(gram): raise ValueError('full physical block contraction fails')
    return {'status':'PASS_UNIFORM_TRANSFER_METRIC','squared_boundary_factor':str(a*b),
            'squared_rate':str(c),'all_positive_width_squared_bound':'boundary_factor * squared_rate ** width',
            'uniform_positive_width_squared_bound':str(a*b*c)}


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('input',type=Path); args=parser.parse_args()
    try: result=check(json.loads(args.input.read_text()))
    except (ValueError,KeyError,TypeError,IndexError,ZeroDivisionError) as error: parser.error(str(error))
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__': main()
