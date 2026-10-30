"""Independent all-interval dyadic exponent upper bound for the fixed WORD.

No author code imports. This is a flat-template range lemma, not a recursive
backend or physical stock proof. Apache-2.0; prepared with OpenAI assistance.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import gzip,json
HERE=Path(__file__).resolve().parent
SHA='48f8734ca9c5adf5d60ded3a5fefbc24894d2c358ed7cb30fcc0d71718599446'
def need(ok,why):
    if not ok:raise ValueError(why)
def ceiling_log2(q):
    q=F(q);need(q>0,'Positive logarithm argument')
    h=q.numerator.bit_length()-q.denominator.bit_length()
    bound=F(2**h) if h>=0 else F(1,2**(-h))
    return h if q<=bound else h+1
def envelope(program,roles):
    e=[0]*roles;largest=0;witness={'cut':0,'role':0,'exponent':0}
    for i,event in enumerate(program):
        op,r=event[:2]
        if op in ('INIT','CLEAR'):e[r]=0
        elif op=='SCALE':
            q=abs(F(event[2]));e[r]=max(0,e[r]+ceiling_log2(q)) if q else 0
        elif op in ('ADD','COPY'):
            q=abs(F(event[3]))
            if q:e[r]=max(e[r],e[event[2]]+ceiling_log2(q))+1
        else:need(op=='MOVE','Known actual opcode')
        if e[r]>largest:
            largest=e[r];witness={'cut':i+1,'role':r,'exponent':largest}
    return largest,witness
def exact_multiply(a,b):
    n=len(a)
    return [[sum((a[i][k]*b[k][j] for k in range(n)),F(0)) for j in range(n)] for i in range(n)]
def small_all_intervals():
    # This fixture contains contractions, expansion, zero reset and ADD-COPY.
    p=[['ADD',0,1,'-3/2',0],['SCALE',1,'1/8',0],['INIT',2,0],
       ['COPY',2,0,'1',0],['ADD',1,2,'7/4',0],['CLEAR',2,0],['SCALE',0,'0',0]]
    emax,_=envelope(p,3);identity=[[F(i==j) for j in range(3)] for i in range(3)]
    operators=[]
    for x in p:
        a=[row[:] for row in identity];op,r=x[:2]
        if op in ('INIT','CLEAR'):a[r]=[F(0)]*3
        elif op=='SCALE':a[r]=[F(x[2])*z for z in a[r]]
        else:a[r][x[2]]+=F(x[3])
        operators.append(a)
    maximum=F(1)
    for start in range(len(p)+1):
        a=[row[:] for row in identity]
        for m in operators[start:]:
            a=exact_multiply(m,a)
            maximum=max(maximum,max(sum(map(abs,row)) for row in a))
    need(maximum<=2**emax,'Exhaustive small all-interval control')
    need(ceiling_log2(F(1,65536))==-16 and ceiling_log2(F(65537,2))==16,'Exact logarithm controls')
    return {'events':len(p),'exact_maximum':str(maximum),'dyadic_bound_exponent':emax}
def run():
    raw=(HERE/'WORD.json.gz').read_bytes();need(sha256(raw).hexdigest()==SHA,'Exact actual WORD')
    w=json.loads(gzip.decompress(raw));e,where=envelope(w['program'],743)
    return {'status':'PASS_INDEPENDENT_ALL_INTERVAL_RANGE_ENVELOPE','word_sha256':SHA,
      'E':e,'Gamma':'2^'+str(e),'maximizer_of_computed_envelope':where,
      'small_control':small_all_intervals(),
      'physical_interval_bounds':{'completed_semantic_cuts':'Gamma N^18','native_layer_cuts':'Gamma N^36'},
      'fixed_integer_magnitude_bits_literal':'2 + max(0, b + 17 + 20 f, ceil_log2(K) + E + 36 f - p)',
      'fixed_integer_magnitude_bits_service':'2 + max(0, b + 17 + 14 f, ceil_log2(K) + E + 18 f - p)',
      'additional_exact_scalar_accumulator_guard_bits':35,
      'limits':'Conservative dyadic upper envelope, not an exact all-interval maximum; finite flat-template range bound only; service output-error ABI and native chart assumptions retained; no recursive runtime, stock/tape, or scientific-adoption claim'}
if __name__=='__main__':print(json.dumps(run(),indent=2,sort_keys=True))
