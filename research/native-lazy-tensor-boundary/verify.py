"""Independent finite controls for the written uniform proof; no predecessor imports."""
import hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P))
import routing as r


def direct(m,x,f,bits):
    p,q=m; y=phase=0
    for j in range(f):
        a=(x>>(bits*j))&((1<<bits)-1)
        y |= p[a]<<(bits*j); phase+=q[a]
    return y,phase%4


def oracle(v,m,f,bits):
    out=[None]*len(v)
    for x,z in enumerate(v):
        y,q=direct(m,x,f,bits); out[y]=r.rotate(z,q)
    return out


def check_lanes(m,f,bits):
    lanes=r.tables(m); bill={}; count=0
    for x,pos,ph in r.odometer(lanes,f,bits,bill):
        a=x
        for k in range(len(lanes)):
            _,q=direct(m,a,f,bits)
            r.need(pos[k]==a and ph[k]==q,'odometer versus independent tensor routing')
            a,_=direct(m,a,f,bits)
        count+=1
    N=1<<(bits*f); U=sum((N-1)//(1<<bits)**j for j in range(f))
    r.need(bill['lane_digit_updates']==len(lanes)*U,'exact odometer bill')
    return count


def verify():
    pins=json.loads((P/'source/pins.json').read_text())
    for name,h in pins.items(): r.need(hashlib.sha256((P/'source'/name).read_bytes()).hexdigest()==h,'source hash '+name)
    b=json.loads((P/'source/BOUNDARY.json').read_text())
    r.need((b['register'],b['pre_b_index'],b['next_b_index'])==(333,1081,1097),'actual lender boundary')
    M=r.decode(b['warp']); R=r.decode(b['child']['right']); L=r.decode(b['child']['left']); F=r.compose(R,M)
    r.need([r.order(m[0]) for m in (M,R,F,L)]==[12,24,28,252],'base orders')
    for m in (M,R,F): r.need(all(x!=y for x,y in enumerate(m[0])),'no fixed coordinates')
    for m in (R,F): r.need([m[1].count(j) for j in range(4)]==[128]*4,'uniform phase distribution')
    arrays=[[(17*x-3*k,5*x+11*k) for x in range(512)] for k in range(4)]
    strong,bs=r.boundary(arrays,M,R,1,9,False); lazy,bl=r.boundary(arrays,M,R,1,9,True)
    r.need(strong==lazy,'four arbitrary dirty arrays before common suffix')
    mv=oracle(arrays[0],M,1,9); rv=oracle(mv,R,1,9)
    want=[rv]+[[(a+sg*c,b+sg*d) for (a,b),(c,d) in zip(t,mv)] for t,sg in zip(arrays[1:],(-1,-1,1))]
    r.need(strong==want,'separate out-of-place oracle')
    r.need(bs['complex_stores']-bl['complex_stores']==512,'source store delta')
    for bill,lanes,comparisons in ((bs,36,34),(bl,29,27)):
        r.need(bill['lane_digit_updates']==lanes*511 and bill['leader_comparisons']==comparisons*512,'actual counted routing invoice')
    # Small alphabets exercise tensor cycles, nontrivial fixed phases and mixed periods.
    fixtures=[((1,0),(0,3)),((1,2,3,0),(0,1,2,3)),((0,2,1,3),(2,0,3,1))]
    columns=0
    for m in fixtures:
        bits=(len(m[0])-1).bit_length()
        for f in range(1,5):
            columns+=check_lanes(m,f,bits)
            data=[(i+7,3-i) for i in range(len(m[0])**f)]; got=list(data)
            r.cycle_apply(got,m,f,bits,{})
            r.need(got==oracle(data,m,f,bits),'tensor cycle exactness')
    # Real width-two columns include carries and affine/global phases; no full array allocated.
    for x in [0,1,511,512,513,65535,131072,262143]:
        y,a=direct(M,x,2,9); z,c=direct(R,y,2,9)
        r.need(direct(F,x,2,9)==(z,(a+c)%4),'actual width-two composition')
    controls=0
    for wrong in [(M[0],tuple((q-3)%4 for q in M[1])),(tuple(y^458 for y in M[0]),M[1])]:
        r.need(oracle(arrays[0],wrong,1,9)!=mv,'phase/translation mutation'); controls+=1
    r.need(r.compose(M,R)!=F,'reversed composition mutation');controls+=1
    for bad in (0,-1,True):
        try:r.invoice(bad)
        except ValueError:controls+=1
        else:raise ValueError('invalid width accepted')
    for f in range(1,33):
        z=r.invoice(f);r.need(z['materialized_source_real_writes']-z['lazy_source_real_writes']==2*z['N'],'uniform invoice')
    return dict(status='PASS_NATIVE_LAZY_TENSOR_BOUNDARY',orders=[12,24,28,252],small_tensor_columns=columns,controls=controls,actual_dense_width=1,actual_width2_columns=8,invoice=[r.invoice(f) for f in (1,2,3,16)])

if __name__=='__main__':
    result=verify()
    if '--write' in sys.argv: (P/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:r.need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((P/'RESULT.json').read_text()),sort_keys=True),'receipt mismatch')
    print(result['status'])
