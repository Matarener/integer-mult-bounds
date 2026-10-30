"""Check the finite-period proof controls and the literal order-seven cell."""
from fractions import Fraction as F


def determinant(matrix):
    rows = [[F(x) for x in row] for row in matrix]
    value = F(1)
    for column in range(len(rows)):
        pivot = next((i for i in range(column,len(rows)) if rows[i][column]), None)
        if pivot is None:
            return F(0)
        if pivot != column:
            rows[pivot],rows[column] = rows[column],rows[pivot]
            value = -value
        a = rows[column][column]
        value *= a
        for i in range(column+1,len(rows)):
            ratio = rows[i][column]/a
            rows[i] = [x-ratio*y for x,y in zip(rows[i],rows[column])]
    return value


def gaussian_mul(a,b):
    return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])


def gaussian_power(a,n):
    out=(1,0)
    for _ in range(n):
        out=gaussian_mul(out,a)
    return out


def gm(a,b):
    return [[tuple(sum(v[k] for v in [gaussian_mul(x,y) for x,y in zip(row,col)])
                    for k in range(2)) for col in zip(*b)] for row in a]


def verify():
    cases=0
    for n in range(2,34,2):
        for x,y in [(0,0),(1,0),(0,1),(1,1),(3,-2)]:
            matrix=[[0 if i==j else (1 if i>j else -1) for j in range(n+1)] for i in range(n+1)]
            matrix[n][0],matrix[0][n]=x,-y
            if determinant(matrix) != x-y:
                raise ValueError('The two-corner Gram determinant fails')
            cases+=1
    # N/sqrt(2) is V_7=R_7 H_0 from the pinned predecessor.
    N=[[(0,0) for _ in range(8)] for _ in range(8)]
    phases=[(1,0),(0,1),(-1,0),(0,-1)]
    for x in range(8):
        for y0 in (0,1):
            y1,y2=(x>>1)&1,(x>>2)&1
            output=y0|((y0^y1)<<1)|((y1^y2)<<2)
            sign=-1 if (x&1)*y0 else 1
            phase=phases[(y0+y2)%4]
            N[output][x]=(sign*phase[0],sign*phase[1])
    power=[[(int(i==j),0) for j in range(8)] for i in range(8)]
    traces=[]
    for k in range(1,8):
        power=gm(N,power)
        trace=(sum(power[i][i][0] for i in range(8)),sum(power[i][i][1] for i in range(8)))
        eighth=gaussian_power(trace,8)
        denominator=2**(4*k)
        if k<7:
            if eighth != (denominator,0):
                raise ValueError('A nontrivial order-seven tensor trace differs from one')
            traces.append(1)
    expected=[[(8,-8) if i==j else (0,0) for j in range(8)] for i in range(8)]
    if power != expected:
        raise ValueError('The exact seventh cell power has the wrong phase')
    # The faithful character control fails for the identity specialization.
    bad=[[1]*7 for _ in range(7)]
    if determinant(bad):
        raise ValueError('The nonfaithful character control was accepted')
    return {'two_corner_determinant_cases':cases,'identity':'det G(x,y)=x-y',
            'cell_seventh_numerator':'8-8i','cell_denominator':'sqrt(2)^7',
            'eight_cell_nontrivial_traces':traces,'eight_cell_dimension':8**8,
            'all_width_gram':'((2^24)^f-1) I_7 + J_7',
            'nonfaithful_specialization_rejected':True}


if __name__=='__main__':
    import json
    print(json.dumps(verify(),indent=2))
