"""All-width precision certificates. Standard library; exact rational arithmetic.
No selected native consumer is assumed to have these metric bounds.
"""
from fractions import Fraction as Q
from math import ceil, log2
import json


def need(condition,message):
    if not condition: raise ValueError(message)


def qmat(rows): return [[Q(x) for x in row] for row in rows]


def weighted_infinity_certificate(transitions,left,right,weights,a,b,rho):
    """T[y][x][v][w], F[role][virtual], B[virtual][role].
    Proves ||complete physical endpoint at width f||_infinity <= a*b*rho**f.
    Rows include every coherent physical input, never independent-column tests.
    """
    d=len(transitions); D=len(weights)
    need(d>0 and D>0,'empty contract')
    need(all(w>0 for w in weights),'strictly positive virtual weights required')
    need(a>=0 and b>=0 and rho>=0,'nonnegative bounds required')
    need(all(len(r)==D for r in left),'left dimension')
    need(len(right)==D and len(right[0])>0,'right dimension')
    q=len(right[0]); need(all(len(r)==q for r in right),'right dimension')
    for row in left:
        need(sum(abs(row[j])*weights[j] for j in range(D))<=a,'left bound')
    for i in range(D):
        need(sum(abs(x) for x in right[i])<=b*weights[i],'right bound')
    for y in range(d):
        need(len(transitions[y])==d,'input dimension')
        for x in range(d):
            need(len(transitions[y][x])==D and all(len(r)==D for r in transitions[y][x]),'virtual dimension')
        for i in range(D):
            value=sum(abs(transitions[y][x][i][j])*weights[j] for x in range(d) for j in range(D))
            need(value<=rho*weights[i],'full coherent row bound')
    return True


def matmul(a,b):
    return [[sum((a[i][k]*b[k][j] for k in range(len(b))),Q(0)) for j in range(len(b[0]))] for i in range(len(a))]


def literal_endpoint(T,F,B,f):
    d=len(T); D=len(B); p=len(F); q=len(B[0]); dimension=d**f
    out=[[Q(0) for _ in range(q*dimension)] for _ in range(p*dimension)]
    def digits(n):
        result=[]
        for _ in range(f): result.append(n%d); n//=d
        return result[::-1]
    words=[digits(i) for i in range(dimension)]
    for yy,y in enumerate(words):
        for xx,x in enumerate(words):
            product=F
            for yi,xi in zip(y,x): product=matmul(product,T[yi][xi])
            product=matmul(product,B)
            for i in range(p):
                for j in range(q): out[i*dimension+yy][j*dimension+xx]=product[i][j]
    return out


def infinity_norm(a): return max(sum(abs(x) for x in row) for row in a)


def nearest(x): return (2*x.numerator+x.denominator)//(2*x.denominator)


def recover(y,step):
    need(step>0,'positive lattice step')
    return step*nearest(y/step)


def fft_sufficient_bits(L,D):
    need(isinstance(L,int) and L>=1 and isinstance(D,int) and D>=1,'L,D positive integers')
    # Q >= 4*N^2*((5D^2+2D)*L+8D+8), exact ceil(log2()) by bit length.
    n=1<<L; required=4*n*n*((5*D*D+2*D)*L+8*D+8)
    return (required-1).bit_length()


def fft_exact_budget(L,D,bits):
    delta=Q(1,1<<bits); n=1<<L
    def stages(M,E):
        for _ in range(L): M,E=2*M,(2+delta)*E+delta*M+delta
        return M,E
    M,E=stages(Q(D),Q(0)); EP=2*M*E+E*E+delta
    _,EI=stages(M*M,EP)
    return EI/n


def verify():
    infinity_cases=0; endpoint_cases=0; recovery_cases=0
    h=Q(1,1<<74); eps=h/32; zero=qmat([[0,0],[0,0]])
    identity=qmat([[1,0],[0,1]]); sign=qmat([[1,0],[0,-1]])
    parityT=[[identity,zero],[zero,sign]]
    parityF=qmat([[eps/2,-eps/2]]); parityB=qmat([[1],[1]])
    rotation=qmat([[0,-1],[1,0]]); flip=qmat([[1,0],[0,-1]])
    # Noncommuting transitions under a nonidentity rational virtual scaling.
    S=qmat([[2,0],[0,3]]); Si=qmat([[Q(1,2),0],[0,Q(1,3)]])
    AT=matmul(matmul(Si,rotation),S); BT=matmul(matmul(Si,flip),S)
    noncommutingT=[[AT,zero],[zero,BT]]
    noncommutingF=matmul(qmat([[eps,0]]),S); noncommutingB=matmul(Si,qmat([[1],[0]]))
    for T,F,B,w in [(parityT,parityF,parityB,[Q(1),Q(1)]),
                    (noncommutingT,noncommutingF,noncommutingB,[Q(1,2),Q(1,3)])]:
        weighted_infinity_certificate(T,F,B,w,eps,Q(1),Q(1)); infinity_cases+=1
        for f in range(1,7):
            endpoint=literal_endpoint(T,F,B,f); need(infinity_norm(endpoint)<=eps,'literal norm exceeds certificate'); endpoint_cases+=1
            values=[Q(15 if i%3 else -15) for i in range(2**f)]
            perturbed=[values[i]+sum(endpoint[i][j]*values[j] for j in range(len(values))) for i in range(len(values))]
            need([recover(y,h) for y in perturbed]==values,'strict lattice recovery failed'); recovery_cases+=1
    # Column-wise local bounds are insufficient for coherent inputs.
    coherent=[[[[Q(1)]],[[Q(1)]]],[[[Q(0)]],[[Q(0)]]]]
    try: weighted_infinity_certificate(coherent,[[Q(1)]],[[Q(1)]],[Q(1)],Q(1),Q(1),Q(1))
    except ValueError: pass
    else: raise AssertionError('coherent row control accepted')
    need(recover(h/2,h)!=0,'half-step equality control failed')
    exact_budgets=[]
    for L in range(1,33):
        for D in (1,15,255):
            bits=fft_sufficient_bits(L,D); e=fft_exact_budget(L,D,bits)
            need(e<=Q(1,4),'closed form insufficient')
            exact_budgets.append({'log2_N':L,'digit_abs_bound':D,'sufficient_bits':bits})
    return {'status':'PASS','weighted_infinity_contracts':infinity_cases,'literal_endpoints':endpoint_cases,
      'literal_lattice_recovery_cases':recovery_cases,'universal_precision_instantiations':len(exact_budgets),
      'fft_precision_examples':[x for x in exact_budgets if x['log2_N'] in (9,16,32) and x['digit_abs_bound']==15],
      'selected_grid_endpoint':{'controller_grid_bits':74,'digit_abs_bound':15,'sufficient_residual_scale':'2^(-79)',
        'status':'sufficient example for the cited parity transfer; no selected caller residual table or norm binding claimed'},
      'controls':['half-step equality rejects recovery','coherent cross-input row requires full row sum'],
      'kappa_effect':'none established; no complete selected paid-profile change or outer-record replacement'}

if __name__=='__main__': print(json.dumps(verify(),indent=2))
