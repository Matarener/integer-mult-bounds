#!/usr/bin/env python3
"""Direct set/operator checker; imports no package/predecessor verifier."""
import json
from fractions import Fraction
from pathlib import Path

P = Path(__file__).resolve().parent

def need(ok, message):
    if not ok:
        raise ValueError(message)

def incidence(n, row_mask, col_mask):
    rows = {i for i in range(n) if row_mask >> i & 1}
    cols = {j for j in range(n) if col_mask >> j & 1}
    touched = {(i,j) for i in rows for j in range(n)} | {(i,j) for j in cols for i in range(n)}
    twice = {(i,j) for i,j in touched if i in rows and j in cols}
    dangling = touched-twice
    return len(rows),len(cols),len(touched),len(dangling)

def main():
    checked = 0
    for n in range(1,8):
        for rows in range(1<<n):
            for cols in range(1<<n):
                a,b,t,d = incidence(n,rows,cols)
                need(t==n*(a+b)-a*b,'union coverage')
                need(d==n*(a+b)-2*a*b,'dangling coverage')
                need((d==0)==((a==b==0) or (a==b==n)),'closed endpoint')
                checked += 1
    # Direct pair operators on a basis, without using matrix identities from verify.py.
    s = lambda x,y:(x,x+y)
    r = lambda x,y:(x-y,y)
    columns = ((1,0),(0,1))
    maps = {'S':[s(*z) for z in columns], 'R':[r(*z) for z in columns],
            'RS':[r(*s(*z)) for z in columns]}
    need(maps['S'] != maps['RS'] and maps['R'] != maps['RS'],'one-stage endpoint failure')
    # Exact rational bilinear extremum, including asymmetric negative excess controls.
    for n in range(1,9):
        for er in (Fraction(-1,2),Fraction(n-1,2),Fraction(2*n-1,2),Fraction(n),Fraction(n+1)):
            for ec in (Fraction(-1,2),Fraction(n-1,2),Fraction(2*n-1,2),Fraction(n),Fraction(n+1)):
                values = [(er-n)*a+(ec-n)*b+a*b for a in range(n+1) for b in range(n+1) if a+b]
                need((min(values)<0)==(min(er,ec)<n),'all-mask exact criterion')
                both = [(er-n)*a+(ec-n)*b+a*b for a in range(1,n+1) for b in range(1,n+1)]
                corners=[(er-n)*a+(ec-n)*b+a*b for a,b in ((1,1),(1,n),(n,1),(n,n))]
                need(min(both)==min(corners),'two-axis four-corner criterion')
    result=json.loads((P/'RESULT.json').read_text())
    need(result['minimum_nonempty_excess']==160,'minimum')
    need(result['closed_masks']==[[0,0],[104,104]],'receipt closure')
    need(result['sparse_discrimination_control']['dangling']==206,'sparse control')
    for row in result['full_inventory_controls']:
        n=104; c=208; width=row['width']
        need(row['excess']==c*(2576-2312)-n*n==44096,'independent full excess')
        need(row['lower_rank']==81*width+44096,'independent bill')
    print('PASS_INDEPENDENT_INCIDENCE: '+str(checked)+' explicit masks, exact pair operators and rational corners')

if __name__=='__main__':
    main()
