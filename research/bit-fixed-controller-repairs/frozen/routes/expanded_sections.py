#!/usr/bin/env python3
"""Exact135-repair scalar closure and actual fresh-coordinate route witness.

Scalar closure is not a native endpoint. The fresh-coordinate test proves
that this candidate fails even on arbitrary binary VALUE functions over an
explicit odd ADDRESS field. No kappa or completed supplier is claimed.
Substantial OpenAI Codex assistance.
"""
import argparse,gzip,json,sys
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OLD=Path('/Users/ross/git/math/.research-automation/runs/kappa-3605-successor-20261018T0940Z/major-frontier')
REPO=Path('/Users/ross/git/math/integer-mult-bounds')
sys.path.insert(0,str(OLD/'recursive'))
import bit_cap_copy_local as cap

def need(b,s):
    if not b:raise ValueError(s)

def bits(x):
    while x:
        b=x&-x;yield b.bit_length()-1;x^=b
def xor(xs):
    x=0
    for a in xs:x^=a
    return x
def eye(n):return [1<<i for i in range(n)]
def product(a,b):return [xor(b[j] for j in bits(r)) for r in a]
def inverse(a):
    n=len(a);w=[r|(1<<(n+i)) for i,r in enumerate(a)]
    for j in range(n):
        p=next((p for p in range(j,n) if w[p]>>j&1),None)
        need(p is not None,'singular binary code');w[p],w[j]=w[j],w[p]
        for p in range(n):
            if p!=j and w[p]>>j&1:w[p]^=w[j]
    need([r&((1<<n)-1) for r in w]==eye(n),'exact inverse reduction')
    return [r>>n for r in w]

def mm(a,b):
    bt=list(zip(*b));return [[sum(x*y for x,y in zip(row,col)) for col in bt] for row in a]
def tr(a):return list(map(list,zip(*a)))
def eyeq(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def serial(a):return [[str(x) for x in row] for row in a]

def roots_and_routes(word):
    rawpath=REPO/'research/e8-bit-carrier-skeleton/data/bit/bitE8-r865.json.gz'
    raw=rawpath.read_bytes();full=json.loads(gzip.decompress(raw));lines=full['lines']
    I=eyeq(8);gs={0:I};todo=[0]
    while todo:
        more=[]
        for p in todo:
            for q in range(120):
                ip=sum(x*y for x,y in zip(lines[p],lines[q]))//2
                if q in gs or abs(ip)!=1:continue
                d=[F(x-y if ip==1 else x+y) for x,y in zip(lines[p],lines[q])]
                norm=sum(x*x for x in d)
                r=[[F(i==j)-2*d[i]*d[j]/norm for j in range(8)] for i in range(8)]
                gs[q]=mm(r,gs[p]);more.append(q)
        todo=more
    need(len(gs)==120,'all actual E8 routes')
    rho=[];AA=[];PP=[]
    for p,label in enumerate(word['ports_geom']):
        q=word['lines'][p];g=gs[label];a=[row[1:] for row in g]
        P=[[F(x*y,4) for y in q] for x in q]
        need(mm(tr(a),a)==eyeq(7),'actual orthonormal cap basis')
        need(mm(a,tr(a))==[[I[i][j]-P[i][j] for j in range(8)] for i in range(8)],'actual cap projector')
        r=[P[i]+a[i] for i in range(8)]+[row+[F(0)]*7 for row in tr(a)]
        need(mm(r,r)==eyeq(15) and tr(r)==r,'actual involutive route')
        rho.append(r);AA.append(a);PP.append(P)
    # Every ordered distinct pair moves the fresh coordinate, even mod101.
    failures=[];count=0
    for p in range(111):
        for q in range(111):
            if p==q:continue
            aq=mm(tr(AA[p]),[[F(x)] for x in word['lines'][q]])
            need(any(x[0] for x in aq),'distinct-line fresh crossblock')
            need(any((x[0].numerator*pow(x[0].denominator,-1,101))%101 for x in aq),
                 'fresh crossblock nonzero mod101')
            count+=1
    return rho,AA,PP,{'full_root_word_sha256':sha256(raw).hexdigest(),'ordered_distinct_pairs_checked':count,'address_prime':101}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
    inp=OLD/'recursive/BIT-THREE-ROW-INPUT.json';mat=json.loads(inp.read_bytes())['matrices'];R,K=mat['R'],mat['K']
    W=K[:]
    for p in (0,1,2):W[p]=0
    A=[i^r for i,r in zip(eye(111),product(W,R))];AI=inverse(A)
    J=[i^r for i,r in zip(eye(111),product(K,R))]
    codes=[A]*8+[eye(111)];repairs=[];prefix=eye(111)
    for s,a in enumerate(codes):
        ai=inverse(a);Q=[i^r for i,r in zip(eye(111),product(J,ai))]
        rows=[p for p,r in enumerate(Q) if r];need(rows==([0,1,2] if s<8 else list(range(111))),'actual physical repair rows')
        repairs.append({'stage':s,'rows':rows,'queries':Q})
        prefix=product(a if s%2==0 else ai,prefix)
    need(prefix==eye(111),'all111 scalar input columns close')
    wordpath=cap.RAW;raw=wordpath.read_bytes();need(sha256(raw).hexdigest()==cap.RAW_SHA,'R438 source word pin')
    word=json.loads(gzip.decompress(raw));rho,AA,PP,geo=roots_and_routes(word)
    # Latest nonidentity factor is reverse stage7, whose coefficient matrixAI
    # has an offdiagonal. Stage8 is the exact identity factor.
    p,q=next((p,q) for p,row in enumerate(AI) for q in bits(row) if p!=q)
    cross=mm(tr(AA[p]),PP[q]);i=next(i for i in range(8) if any(row[i] for row in cross))
    a=[F(j==i) for j in range(15)];b=[row[i] for row in mm(rho[p],rho[q])]
    need(a[8:]==[0]*7 and any(b[8:]),'fresh-fiber delta witness')
    # Literal pullback rule: row addresses use d*rho; the delta image is the
    # corresponding inverse map, column rho_p*rho_q*a as recorded above.
    need(b==[sum(rho[p][j][k]*rho[q][k][i] for k in range(15)) for j in range(15)],'ordered delta coordinate action')
    b101=[x.numerator*pow(x.denominator,-1,101)%101 for x in b]
    need(any(b101[8:]),'explicit odd-field delta witness')
    # A missing offdiagonal cannot diagnose this phenomenon; diagonal routes
    # fix the whole fresh coordinate. Omitting the port-relative route would
    # incorrectly turn every factor into its scalar augmentation.
    need(mm(rho[p],rho[p])==eyeq(15),'diagonal route control')
    off_without_routes=eyeq(15);need(not any(off_without_routes[j][i] for j in range(8,15)),'omitted-route control')
    sourcepath=REPO/'research/e8-bit-carrier-skeleton/code/nine/geometry.py'
    out={'status':'PASS135_REPAIR_SCALAR_CLOSURE_AND_NATIVE_FRESH_FIBER_FAILURE',
         'R438_word_sha256':sha256(raw).hexdigest(),'matrix_input_sha256':sha256(inp.read_bytes()).hexdigest(),
         'actual_geometry_source_sha256':sha256(sourcepath.read_bytes()).hexdigest(),
         'codes':codes,'stage_repairs':repairs,'total_rank_one_copies':135,'previous_total':27,'extra_copies':108,
         'source_codes_binary_invertible':True,'scalar_all111_columns_endpoint_identity':True,
         'local_tariff':'eight3-row coded calls plus one111-row ordinary-source call; one private field live per snapshot, no new dirty helper',
         'fresh_coordinate_witness':{'latest_stage':7,'local_factor':'A^-1','output_port':p,'input_port':q,
             'coefficient':(AI[p]>>q)&1,'input_address_15':list(map(str,a)),
             'output_address_15':list(map(str,b)),'output_address_mod101':b101,
             'global_fresh_axes':list(range(8+7*6,8+7*7)),
             'compact_endpoint_input':'(G6...G0)^-1 delta(input_port q,input_address a)',
             'difference':'G7 delta has nonzero output at port p with freshE7!=0; (G6...G0)^-1 delta is supported wholly in freshE7=0'},
         'geometry':geo,'controls':['diagonal relative route fixes fresh block','omitting relative route loses fresh witness'],
         'theorem_scope':'For any finite common-E controller with scalar invertible stage codes and these once-only fresh-block routes, exact endpointidentity forces every scalar stage code diagonal. OverF2 it forcesI, hence111physical repair rows perstage in this row-repair grammar.',
         'limits':['arbitrary changedcaller, operator-valued codes, revisiting fresh blocks, extra terminal stages and non-common-E controllers remain outside this theorem',
                   '135-copy candidate is only scalar closure and fails native endpoint; no whole supplier, signed local words or kappa admission']}
    out=json.loads(json.dumps(out));path=HERE/'EXPANDED-SECTIONS.json'
    if args.write:path.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    else:need(json.loads(path.read_bytes())==out,'complete route receipt differs')
    print(out['status']);print('scalarcopies135; actualfreshwitness',p,q,'axis',i,'mod101',b101[8:])

if __name__=='__main__':main()
