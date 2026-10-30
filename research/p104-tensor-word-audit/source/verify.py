#!/usr/bin/env python3
"""Exact dyadic tensor-code protocol and coefficient-ring audit; standard library, Apache-2.0."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIVOTS = (0, 1, 3, 6, 22, 31, 93, 103)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    def pairs(items):
        ans = {}
        for key, value in items:
            require(key not in ans, 'duplicate JSON key')
            ans[key] = value
        return ans
    return json.loads(path.read_text(), object_pairs_hook=pairs)


def authenticate():
    for row in read(HERE / 'SOURCES.json')['files']:
        if row['usage'] != 'input':
            continue
        path = ROOT / row['path']
        require(not path.is_symlink(), 'source symlink')
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row['sha256'], 'input hash: ' + row['path'])
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == row['git_blob'], 'input blob')


def source_matrix():
    roots = []
    for a, b in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[a], row[b] = 2, 2 * sign
            roots.append(tuple(row))
    roots.extend((1,) + tail for tail in itertools.product((-1, 1), repeat=7) if tail.count(-1) % 2 == 0)
    fixture = read(ROOT / 'research/p104-native-channel/inputs/P104-FIXTURE.json')['section4_explicit_P104']
    removed = {tuple(row) for row in fixture['F0'] + fixture['C']}
    ports = sorted(set(roots) - removed)
    require(len(ports) == 104, 'P104 port count')
    order = list(PIVOTS) + [i for i in range(104) if i not in PIVOTS]
    ports = [ports[i] for i in order]
    gram = [[sum(x*y for x,y in zip(a,b)) for b in ports] for a in ports]
    require(all(gram[i][j] == 8*(i == j) for i in range(8) for j in range(8)), 'pivot Gram')
    b2 = [[gram[i][j] // 4 for j in range(8,104)] for i in range(8)]
    require(all(v in (-1,0,1) for row in b2 for v in row), 'signed half coefficients')
    require(all(sum(b2[i][k]*b2[j][k] for k in range(96)) == 48*(i == j) for i in range(8) for j in range(8)), 'BBt=12I')
    require(all(sum(b2[k][i]*b2[k][j] for k in range(8)) == gram[i+8][j+8]//2 for i in range(96) for j in range(96)), 'nonpivot Gram')
    return b2



def index(bank,i,j,n): return (bank*n+i)*n+j


def triangular(b,bank,axis,fixed,transpose=False,inverse=False):
    p=len(b);n=p+len(b[0])
    def ix(k): return index(bank,k,fixed,n) if axis==0 else index(bank,fixed,k,n)
    donors=range(p) if transpose else range(p,n)
    for d in donors: yield ('half',ix(d))
    for j,row in enumerate(b):
        for k,v in enumerate(row,p):
            if v:
                dest,src=(k,j) if transpose else (j,k)
                yield ('add',ix(dest),ix(src),-v if inverse else v)
    for d in donors: yield ('double',ix(d))


def code_word(b,inverse=False):
    n=len(b)+len(b[0])
    steps=[(0,1,True,True),(0,0,False,False),(1,1,False,False),(1,0,True,True)]
    if inverse: steps=[(bank,axis,t,not inv) for bank,axis,t,inv in reversed(steps)]
    for bank,axis,t,inv in steps:
        for fixed in range(n):yield from triangular(b,bank,axis,fixed,t,inv)


def coded_pair(b):
    p=len(b);n=p+len(b[0])
    # lower: Y += P_r M_c X. upper: X -= M_r P_c Y.
    for source,axis in ((0,1),(1,0)):
        target=1-source;sign=1 if source==0 else -1
        for fixed in range(p):
            yield from triangular(b,source,axis,fixed,True)
            yield from triangular(b,source,axis,fixed)
            for k in range(n):
                i,j=(fixed,k) if axis==1 else (k,fixed)
                yield ('add',index(target,i,j,n),index(source,i,j,n),sign)
            yield from triangular(b,source,axis,fixed,inverse=True)
            yield from triangular(b,source,axis,fixed,True,True)


def reference_pair(b):
    p=len(b);n=p+len(b[0])
    for source,axis in ((0,0),(1,1)):
        target=1-source;sign=1 if source==0 else -1
        for fixed in range(n):
            def ix(bank,k):return index(bank,k,fixed,n) if axis==0 else index(bank,fixed,k,n)
            yield from triangular(b,source,axis,fixed)
            for j in range(p):yield ('add',ix(target,j),ix(source,j),sign)
            for j in range(p):yield ('half',ix(source,j))
            for j,row in enumerate(b):
                for k,v in enumerate(row,p):
                    if v:yield ('add',ix(target,k),ix(source,j),sign*v)
            for j in range(p):yield ('double',ix(source,j))
            yield from triangular(b,source,axis,fixed,inverse=True)


def evaluate(word,values):
    x=list(values)
    for op in word:
        if op[0]=='add':x[op[1]]+=op[3]*x[op[2]]
        elif op[0]=='half':
            require(x[op[1]]%2==0,'exact dyadic integer test scale')
            x[op[1]]//=2
        elif op[0]=='double':x[op[1]]*=2
        else:raise ValueError('unknown operation')
    return x


def invoice(word):
    from collections import Counter
    c=Counter(op[0] for op in word)
    return {key:c[key] for key in ('add','half','double')}


def mod_rank(a,p=13):
    a=[[x%p for x in row] for row in a];r=0
    for j in range(len(a[0])):
        pivot=next((i for i in range(r,len(a)) if a[i][j]),None)
        if pivot is None:continue
        a[r],a[pivot]=a[pivot],a[r];scale=pow(a[r][j],-1,p);a[r]=[(x*scale)%p for x in a[r]]
        for i in range(len(a)):
            if i!=r:
                c=a[i][j];a[i]=[(v-c*w)%p for v,w in zip(a[i],a[r])]
        r+=1
        if r==len(a):break
    return r


def result():
    authenticate();b=source_matrix();n=104;p=8
    enc=list(code_word(b));dec=list(code_word(b,True));cp=list(coded_pair(b));rp=list(reference_pair(b))
    ei=invoice(enc+dec);ci=invoice(cp);ri=invoice(rp)
    require(ei=={'add':319488,'half':43264,'double':43264},'boundary invoice')
    require(ci=={'add':26240,'half':3328,'double':3328},'coded pair invoice')
    require(ri=={'add':241280,'half':41600,'double':41600},'reference pair invoice')
    # Dense arbitrary integer fixture, including untouched dirty-helper sentinels.
    data=[((i*37+i//11)%31-15)*(1<<24) for i in range(2*n*n)]+[123,-77]
    require(evaluate(dec,evaluate(enc,data))==data,'full payload inverse')
    reference=evaluate(rp,evaluate(rp,data))
    coded=evaluate(dec,evaluate(cp,evaluate(cp,evaluate(enc,data))))
    require(coded==reference,'actual P104 two-pair scalar endpoint')
    require(coded[-2:]==data[-2:],'arbitrary dirty helper preservation')
    # A nonzero kernel payload is retained in syndrome coordinates.
    syndrome=[0]*(2*n*n)
    syndrome[index(0,8,0,n)]=2
    for i in range(p):syndrome[index(0,i,0,n)]=-b[i][0]
    require(any(syndrome),'nonzero syndrome')
    require(evaluate(dec,evaluate(enc,[v*(1<<16) for v in syndrome]))==[v*(1<<16) for v in syndrome],'kernel payload retained')
    # Reconstruct A mod13 from V=[I B], not by division by its eigenvalue.
    v=[[int(i==j) for j in range(p)]+[(x*7)%13 for x in b[i]] for i in range(p)]
    a=[[sum(v[k][i]*v[k][j] for k in range(p))%13 for j in range(n)] for i in range(n)]
    rank=mod_rank(a)
    require(rank==8 and all(sum(a[i][k]*a[k][j] for k in range(n))%13==0 for i in range(n) for j in range(n)),'nonzero square-zero mod13 Gram')
    require(mod_rank(b)==8,'B mod13 rank')
    v5=[[int(i==j) for j in range(p)]+[(x*3)%5 for x in b[i]] for i in range(p)]
    side5=[[(int(i==j)-sum(v5[k][i]*v5[k][j] for k in range(p)))%5 for j in range(n)] for i in range(n)]
    require(mod_rank(side5,5)==104,'full-rank identity side correction')
    # 13*(1/13)=1 cannot hold for dyadic coefficients; 13 reduces to zero.
    require(13%13==0 and pow(2,-1,13)==7 and 5*5%13==12,'ring homomorphism')
    return {'schema':'p104-tensor-code/1','data_degrees':2*n*n,'source_rank':8,'mod13_gram_rank':rank,'mod13_tensor_product_rank':rank*rank,'full_identity_side_rank':n*n,
      'code':'L=U_r U_c^-t; (Xhat,Yhat)=(L X,L^-t Y)',
      'transformed_lower':'P_r M_c','transformed_upper':'M_r P_c',
      'boundary_invoice':ei,'coded_pair_invoice':ci,'reference_pair_invoice':ri,
      'one_pair_add_difference':ei['add']+ci['add']-ri['add'],
      'two_pair_add_saving':2*ri['add']-ei['add']-2*ci['add'],
      'two_pair_half_saving':2*ri['half']-ei['half']-2*ci['half'],
      'first_add_break_even_integer':2,'first_half_break_even_integer':2,
      'arithmetic_scope':'exact common-chart Gaussian dyadic word; formal scalar counts, not physical/native upper bill',
      'remaining':'physical chart recipes, actual repeated consumer, identity-side correction, helpers/owners, full native moment and precision'}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write-result',action='store_true');parser.add_argument('--result',type=Path,default=HERE/'RESULT.json');args=parser.parse_args()
    r=result()
    if args.write_result:args.result.write_text(json.dumps(r,indent=2,sort_keys=True)+'\n')
    else:require(json.dumps(read(args.result),sort_keys=True)==json.dumps(r,sort_keys=True),'typed result mismatch')
    print('PASS_P104_TENSOR_CODE payload=21632 mod13_rank=64 two_pair_add_saving=110592 no_new_kappa')

if __name__=='__main__':main()
