"""Source-bound child-rank interface discriminator. Apache-2.0.
Chris R / Clear1nsight with substantial OpenAI Codex assistance.
The native exact arithmetic is retained PR3987 code, explicitly credited.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import sys,json,gzip,hashlib,math,argparse
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P/'frozen'))
import exact_phase as phase

def need(ok,why):
    if not ok:raise ValueError(why)

def span(bs):
    s={0}
    for b in bs:s|={x^b for x in tuple(s)}
    return frozenset(s)

def dim(s):
    n=len(s);need(n>0 and n&(n-1)==0,'not a subspace size')
    return n.bit_length()-1

REGS=(600,601,602,604)
POSITIONS=(936,937,938,941)
ENTRANCE=(45,)
TERMINAL=(409,80,40,5,2)

def trace_group(w):
    """Trace source frame state through literal A/B ordering; never retime native maps."""
    current={r:span([w['ports'][r]]) if r<112 else span([]) for r in range(704) if r not in w['removed']}
    for r,b in w['start_extra'].items():current[int(r)]=span(b)
    calls=[]
    def gate(g,section,index):
        if g[0]=='warp':
            need(current[g[1]]==span(g[3]),'A warp entrance');current[g[1]]=span(g[4]);return
        need(g[0] in ('add','scale'),'scalar kind')
        for r in g[1:3] if g[0]=='add' else g[1:2]:
            target=span(g[-1]);need(current[r]<=target,'scalar containment')
            if section=='B' and r in REGS and index in POSITIONS:
                calls.append(dict(register=r,index=index,old=sorted(current[r]),new=sorted(target),rank=dim(target)-dim(current[r])))
            current[r]=target
    for i,g in enumerate(w['A']):gate(g,'A',i)
    # The middle cut only writes target families. Its centre descents are
    # temporary readouts, not persistent helper-frame updates (BORROW-WORD).
    need(all(g[0]=='add' and 112<=g[1]<224 and g[-1] is None for g in w['cut']),'target-only cut contract')
    native=[]
    for i in range(max(POSITIONS)+1):
        for pos,r,cols,u,e in w['warps']:
            if pos==i:
                need(current[r]==span(u),'B warp entrance');current[r]=span(e)
                if min(POSITIONS)<=i<=max(POSITIONS):native.append(dict(index=i,register=r,entrance=u,terminal=e,columns=cols))
        gate(w['B'][i],'B',i)
    positive=[x for x in calls if x['rank']]
    need([(x['register'],x['index'],x['rank']) for x in positive]==list(zip(REGS,POSITIONS,[4]*4)),'actual group ranks')
    need(all(set(x['old'])==set(span(ENTRANCE)) and set(x['new'])==set(span(TERMINAL)) for x in positive),'actual group frames')
    need([(x['index'],x['register']) for x in native]==[(936,564),(936,405),(939,565)],'native ordering')
    # A local dependency check only. No whole-word rewrite or dirty-state replay is claimed.
    for call in positive:
        for j in range(min(POSITIONS),call['index']):
            g=w['B'][j]
            touched=g[1:3] if g[0]=='add' else g[1:2]
            need(call['register'] not in touched,'future call is touched early')
        need(all(x['register']!=call['register'] for x in native if x['index']<=call['index']),'native touches future call')
    return dict(calls=positive,native_events_preserved=native,scalar_window=w['B'][936:942],scope='Source chronology and disjoint-future-input check; no provider rewrite')

def native_support():
    """All 512 columns of actual T_U T_E^-1, with exact Gaussian arithmetic."""
    columns=Counter();rows=Counter();digest=hashlib.sha256()
    for x in range(512):
        v,d0=phase.frame({x:(1,0)},ENTRANCE,True)
        v,d1=phase.frame(v,TERMINAL)
        columns[len(v)]+=1
        for y in v:rows[y]+=1
        need(all(Q(a*a+b*b,1<<(2*(d0+d1)))==Q(1,16) for a,b in v.values()),'residual entry magnitude')
        digest.update(json.dumps([x,d0+d1,sorted(v.items())],separators=(',',':')).encode())
    need(columns=={16:512} and Counter(rows.values())=={16:512},'actual residual support')
    return dict(columns=512,column_support={str(k):v for k,v in columns.items()},row_support={str(k):v for k,v in Counter(rows.values()).items()},raw_gaussian_digest=digest.hexdigest())

def budget():
    k=Q(1730663236534549309146,10**24)
    z=Q(1,3);loglo=2*sum((z**(2*j+1)/Q(2*j+1) for j in range(60)),Q(0))
    loghi=loglo+2*z**121/(121*(1-z*z))
    def power2(exponent):
        a,b=k*exponent*loglo,k*exponent*loghi
        def expm(x,n):return sum(((-x)**i/Q(math.factorial(i)) for i in range(n+1)),Q(0))
        need(0<a<=b<1,'Taylor interval')
        return (1<<exponent)*expm(b,19),(1<<exponent)*expm(a,20)
    p4,p16=power2(2),power2(4)
    lo,hi=4*p4[0]-p16[1],4*p4[1]-p16[0]
    need(0<lo<=hi<Q(1,20),'optimistic allowance less than 0.05 H1')
    scale=10**24
    return dict(kappa=str(k),definition='H_r=r^(1-kappa)',allowance='4 H4 - H16',lower_numerator=lo.numerator*scale//lo.denominator,upper_numerator=-((-hi.numerator*scale)//hi.denominator),denominator=scale,one_extra_H1_exceeds_allowance=True)

def can_be_monomial_equivalent(source_degrees,target_degrees):
    return Counter(source_degrees)==Counter(target_degrees)

def controls():
    # Row-degree is necessary, not sufficient, for monomial equivalence.
    need(can_be_monomial_equivalent([16]*2048,[16]*2048),'spectator batching control')
    need(not can_be_monomial_equivalent([16]*2048+[1]*(65536-2048),[65536]*65536),'rank16 dirty-padding rejection')
    need(not can_be_monomial_equivalent([16]*2048+[1]*(4096-2048),[4096]*4096),'rank12 control')
    # Minimal two-copy witness: I_selector tensor C differs from C tensor C.
    c,_=phase.coordinate({0:(1,0)},[0]);tensor,_=phase.coordinate({0:(1,0)},[0,1])
    need(len(c)==2 and len(tensor)==4,'selector-versus-transform control')
    w=json.loads(gzip.decompress((P/'frozen/WORD-base.json.gz').read_bytes()))
    w['B'][936][-1]=[]
    try:trace_group(w)
    except ValueError as e:need(str(e)=='scalar containment','frame mutant rejected for wrong reason')
    else:raise ValueError('bad source frame accepted')
    return ['spectator-direct-sum positive','rank16 monomial/dirty-padding negative','rank12 monomial/dirty-padding negative','two-axis exact tensor versus selector negative','actual source frame contraction negative']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--record',action='store_true');args=parser.parse_args()
    manifest=json.loads((P/'SOURCES.json').read_text())
    for item in manifest['snapshots']:
        data=(P/item['local']).read_bytes()
        need(len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'],'frozen source changed: '+item['local'])
    providers={}
    for tag in ('base','extra'):
        w=json.loads(gzip.decompress((P/f'frozen/WORD-{tag}.json.gz').read_bytes()))
        providers[tag]=trace_group(w)
    result=dict(status='PASS_JOINT_CHILD_INTERFACE_DISCRIMINATOR',providers=providers,native=native_support(),budget=budget(),controls=controls(),new_kappa=False,whole_provider_dirty_replay=False)
    if args.record:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(result==json.loads((P/'RESULT.json').read_text()),'retained result differs')
    print(json.dumps({k:result[k] for k in ('status','native','budget','new_kappa','whole_provider_dirty_replay')},sort_keys=True))

if __name__=='__main__':main()
