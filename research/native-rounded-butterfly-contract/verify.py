"""Source-authenticated rounded execution against retained exact matrix arithmetic."""
import hashlib,itertools,json,sys
from fractions import Fraction as Q
from pathlib import Path
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P));sys.path.insert(0,str(P/'source'))
import rounded as r
c=None


def norm2(z):return z[0]*z[0]+z[1]*z[1]


def error2(a,b):return max(norm2(c.add(x,c.scale(-1,y)))for x,y in zip(a,b))


def reference(x,y,f,kind,reverse):
    letters={k:c.power(v,f)for k,v in c.letters().items()}
    A,C2,Pm,Qm,W,M=(letters[k] for k in ('A','C2','P','Q','W','M'))
    if reverse:
        if kind==3:y=c.apply(c.adjoint(M),y);y=c.apply(c.adjoint(C2),y);y=c.apply(c.adjoint(W),y)
        y=c.apply(c.adjoint(A),y);y=c.vplus(y,c.apply(Pm,x),-1);y=c.vplus(y,c.apply(Qm,x),-2);x=c.apply(c.adjoint(A),x)
    else:
        x=c.apply(A,x);y=c.vplus(y,c.apply(Pm,x));y=c.vplus(y,c.apply(Qm,x),2);y=c.apply(A,y)
        if kind==3:y=c.apply(W,y);y=c.apply(C2,y);y=c.apply(M,y)
    return x,y


def oracle_round_half(n):
    value=Q(n,2);lower=value.numerator//value.denominator;upper=lower+1
    return min((lower,upper),key=lambda a:(abs(Q(a)-value),a%2))


def verify():
    pins=json.loads((P/'source/pins.json').read_text())
    for name,h in pins.items():r.need(hashlib.sha256((P/'source'/name).read_bytes()).hexdigest()==h,'source hash '+name)
    for n in range(-10001,10002):r.need(r.half_even(n)==oracle_round_half(n),'signed nearest-even half')
    global c
    import channels as c
    base=c.letters()
    for name in ('P','Q','W','M'):
        p,q=r.letters(name);r.need(c.monomial(p,q)==base[name],'source monomial phase')
    rounding=0;cases=[];calls=0
    for f in (1,2,3):
        N=8**f
        for axis in (0,2):
            for adj in (False,True):
                mat=c.power(base['A' if axis==0 else 'C2'],f)
                if adj:mat=c.adjoint(mat)
                for seed in range(3):
                    src=[((17*i+seed)%23-11,(7*i+3*seed)%19-9)for i in range(N)]
                    out=list(src);tr={};r.call(out,f,axis,32,adj,tr)
                    exact=c.apply(mat,[(Q(a),Q(b))for a,b in src])
                    # eta_f < 2*2^(f/2) grid units, proved in PROOF.
                    r.need(error2(out,exact)<4*(2**f),'actual completed-call defect bound')
                    r.need(tr['butterflies']==f*N//2,'literal paid-call work')
                    rounding+=tr['rounding_events'];calls+=1
        for kind in (2,3):
            for reverse in (False,True):
                precision=4;g=r.request_bits(precision,f,kind,reverse);width=r.signed_width(1,precision,f,kind,reverse)
                # Tiny grid-residue plus a macroscopic dirty component exercises nonzero rounding.
                x=[((i%5-2)*(1<<(g-2))+(i%3), (i%7-3)*(1<<(g-3))+1)for i in range(N)]
                y=[((i%3-1)*(1<<(g-2))+1,(i%5-2)*(1<<(g-3))-(i%2))for i in range(N)]
                a,b,tr,cuts=r.port(x,y,f,kind,reverse,width,capture=True)
                xx,yy=list(x),list(y)
                direct_a,direct_b,direct_trace,no_cuts=r.port(xx,yy,f,kind,reverse,width)
                r.need(direct_a is xx and direct_b is yy and no_cuts==[] and (direct_a,direct_b,direct_trace)==(a,b,tr),'production in-place and optional cut instrumentation')
                exact=reference([(Q(s),Q(t))for s,t in x],[(Q(s),Q(t))for s,t in y],f,kind,reverse)
                err=max(error2(a,exact[0]),error2(b,exact[1]))
                r.need(err<=Q(1<<(2*g),1<<(2*precision)),'full port target on actual rounded execution')
                for axis,adj,before,after in cuts:
                    mat=c.power(base['A' if axis==0 else 'C2'],f)
                    if adj:mat=c.adjoint(mat)
                    r.need(error2(after,c.apply(mat,before))<4*2**f,'defect against actual stored input')
                original_x=[(Q(s)+Q(1,3),Q(t)-Q(1,3)) for s,t in x]
                original_y=[(Q(s)-Q(1,3),Q(t)+Q(1,3)) for s,t in y]
                ideal=reference(original_x,original_y,f,kind,reverse)
                err_original=max(error2(a,ideal[0]),error2(b,ideal[1]))
                r.need(err_original<=Q(1<<(2*g),1<<(2*precision)),'input quantization plus actual call defects')
                cases.append(dict(input_quantized_max_error_squared_grid=str(err_original),f=f,kind=kind,reverse=reverse,grid_bits=g,signed_bits=width,rounding_events=tr['rounding_events'],max_error_squared_grid=str(err),butterflies=tr['butterflies']))
    # First exact reachable rounding defect and a non-independent error-channel constraint.
    unit=[(0,0)]*8;unit[0]=(1,0);lost=list(unit);r.call(lost,1,0,8)
    r.need(lost==[(0,0)]*8,'deterministic half-grid loss witness')
    patterns=set()
    for a,b,d,e in itertools.product(range(-2,3),repeat=4):
        v=[(0,0)]*8;v[0]=(a,b);v[1]=(d,e);out=list(v);r.call(out,1,0,8)
        exact=c.apply(base['A'],[(Q(x),Q(y))for x,y in v])
        defect=tuple(2*(Q(out[j][k])-exact[j][k])for j in (0,1)for k in (0,1))
        patterns.add(defect)
        r.need(all(z==0 for z in defect) or all(abs(z)==1 for z in defect),'four component ties share parity')
    # A coordinate error in only one real component is admitted by a ball but impossible here.
    r.need((Q(1),Q(0),Q(0),Q(0)) not in patterns,'independent fault not realizable')
    controls=[]
    for n in (-3,-1,1,3):
        if (n>>1)!=r.half_even(n):controls.append('floor differs at '+str(n))
    v=[(0,0)]*8;v[0]=(2,1);a=list(v);b=list(v);r.call(a,1,0,16);r.call(b,1,2,16)
    r.need(a!=b,'wrong actual C2 axis rejected');controls.append('wrong_axis')
    b=list(v);r.call(b,1,0,16,True);r.need(a!=b,'wrong adjoint rejected');controls.append('wrong_adjoint')
    try:r.call([(7,7)]*8,1,0,4)
    except ValueError:controls.append('internal_numerator_overflow')
    else:raise ValueError('overflow accepted')
    for args in [(0,0,2,False),(-1,1,2,False),(0,1,4,False)]:
        try:r.request_bits(*args)
        except ValueError:controls.append('domain')
        else:raise ValueError('invalid precision contract accepted')
    r.need(rounding>0 and all(x['rounding_events']>0 for x in cases),'nonzero rounding coverage')
    return dict(status='PASS_NATIVE_ROUNDED_BUTTERFLY_CONTRACT',half_rounding_cases=20003,completed_calls=calls,nonzero_call_roundings=rounding,port_cases=cases,one_butterfly_error_patterns=len(patterns),controls=controls)

if __name__=='__main__':
    result=verify()
    if '--write' in sys.argv:(P/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:r.need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((P/'RESULT.json').read_text()),sort_keys=True),'receipt mismatch')
    print(result['status'])
