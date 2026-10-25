#!/usr/bin/env python3
"""Exact necessary screens for the frozen five-terminal BIT word.

No floats decide signs. No producer/checker modules are imported. Frozen inputs
are authenticated and read only. This is not an operator or native admission.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
from math import isqrt
from pathlib import Path
import gzip
import hashlib
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
SCALE = 10**65
H = {1:1322, 2:1342, 3:79, 4:39, 5:102, 6:11, 7:18}
C = 5101
PINS = {}

def need(ok, msg):
    if not ok:
        raise ValueError(msg)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def read(path, expected=None):
    raw = Path(path).read_bytes()
    got = digest(raw)
    need(expected is None or got == expected, 'input digest: '+str(path))
    PINS[str(Path(path).relative_to(HERE))] = got
    return raw

def pinned(path):
    known = {
        'research/r438-native-rehost/CERTIFICATE.json':
            ('R438-CERTIFICATE.json','6da8c593257c8440f0fe35488d941715d953d715e2e464ffdfffff7ed31eee9c'),
        'research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage/vendor/e8-r715-eleven-stage-whole/code/global_k.py':
            ('global_k.py','6368196a393ac25bb2918880e4c4bd31ed733b762c27b6873ab391cbc0c5c3c8'),
    }
    need(path in known,'declared portable source')
    name,expected=known[path]
    return read(HERE/'inputs'/name,expected)

def authenticate():
    candidate=json.loads(read(HERE/'inputs/FIVE-TERMINALS.json',
        '75e029f9bb6ca42540fa633b51bf2d8d62125c57a0ee184fbf3c94e08a8c7d58'))
    local=candidate['literal_roundtrip_profile']
    need({int(r):n for r,n in local['H'].items()}==H,'candidate histogram')
    need((local['mass'],local['ADDs'],local['COPYs'],local['private_fields'])
         ==(5101,36005,9,1),'complete local inventory')
    old=json.loads(pinned('research/r438-native-rehost/CERTIFICATE.json'))
    need(old['local']['candidate']['profile']=={str(r):n+(5 if r==4 else 0) for r,n in H.items()},'predecessor profile')
    invoice=old['pipeline']['candidate']['hosted']['invoice']
    need(invoice['bit']['live']==28416 and invoice['replicas']==32 and invoice['stages']==9,'predecessor stock')
    need(invoice['bit']['rank_mass']==1808352,'predecessor global mass')
    need(sum(r*n for r,n in H.items())==C==111*14+433*8+5*4+63,'local mass identity')
    return {'source_mode':'portable pinned profile, R438 certificate and controller',
            'operator_validation':'separate finite-word producer and independent audit; not executed here',
            'word_decompressed_sha256_provenance':'3bca74a2a8427eb18e86566baa19de597f10d0bc40c30b7443febd499ee2189a'}

def emit_result(name,out):
    import argparse
    parser=argparse.ArgumentParser(description='Check shipped exact mathematical evidence; --write regenerates it.')
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    path=HERE/name
    if args.write:
        path.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
        return
    saved=json.loads(path.read_bytes())
    def mathematical(value):
        value=json.loads(json.dumps(value))
        # Runtime provenance varies across environments; every source digest,
        # arithmetic endpoint, scope field and control remains compared.
        value.pop('checked_at_utc',None)
        value.pop('python',None)
        return value
    need(mathematical(saved)==mathematical(out),'shipped mathematical result differs: '+name)

def down(q):
    return Q((q*SCALE).__floor__(),SCALE)

def up(q):
    return Q((q*SCALE).__ceil__(),SCALE)

def plus(a,b):
    return a[0]+b[0],a[1]+b[1]

def minus(a,b):
    return a[0]-b[1],a[1]-b[0]

def times(a,c):
    return (a[0]*c,a[1]*c) if c>=0 else (a[1]*c,a[0]*c)

def decimal(q):
    with localcontext() as ctx:
        ctx.prec=27
        return str(Decimal(q.numerator)/Decimal(q.denominator))

def interval(a):
    return {'lower':str(a[0]),'upper':str(a[1]),'decimal_lower':decimal(a[0]),'decimal_upper':decimal(a[1])}

@lru_cache(None)
def log_interval(x):
    need(x>=1, 'log domain')
    k=0
    while x>2:
        x/=2
        k+=1
    def unit(y):
        z=(y-1)/(y+1)
        z2=z*z
        power=z
        total=Q(0)
        for j in range(110):
            total+=2*power/(2*j+1)
            power*=z2
        # The omitted positive series starts at exponent221.
        tail=2*power/(221*(1-z2))
        return down(total),up(total+tail)
    return plus(unit(x),times(unit(Q(2)),k))

def exp_point(x):
    need(0<=x<Q(1,2), 'exp domain')
    lowterm=highterm=lowsum=highsum=SCALE
    for j in range(1,61):
        den=x.denominator*j
        lowterm=lowterm*x.numerator//den
        highterm=-((-highterm*x.numerator)//den)
        lowsum+=lowterm
        highsum+=highterm
    tail=Q(highterm)*x/61/(1-x/62)
    return Q(lowsum,SCALE),Q(highsum+tail.__ceil__(),SCALE)

@lru_cache(None)
def power(x,b):
    lo,hi=log_interval(Q(x))
    return exp_point(b*lo)[0],exp_point(b*hi)[1]

def local_bill(m,b,hist=None):
    out=(Q(0),Q(0))
    for r,n in (hist or H).items():
        out=plus(out,times(power(Q(m,r),b),n*r))
    return out

def geometry(L):
    m=7*L+1
    w=Q(111*(L-1),L)
    total=(m-1)*w+63
    extra=max(Q(0),Q(C-total,m))
    idle=max(Q(0),total-C)
    need(total==777*L-714, 'coverage formula')
    need(C+idle==total+m*extra, 'returned idle accounting')
    return m,w,extra,idle

def relaxed_excess(L,b,depth=2):
    # Any proper child at depth d satisfies r < m*2^(-1/d).
    # At depth=None we even grant idle rank m, an invalid recursive child.
    m,w,extra,idle=geometry(L)
    unit=(Q(1),Q(1)) if depth is None else power(Q(2),b/depth)
    return minus(plus(local_bill(m,b),times(unit,idle)),(m*(w+extra),)*2)

def fixed_excess(b,cap=45,surcharge=True,hist=None):
    hist=hist or H
    mass=sum(r*n for r,n in hist.items())
    idle=6279-mass
    need(idle>=0 and 0<cap<64, 'fixed geometry')
    out=plus(local_bill(64,b,hist),times(power(Q(64,cap),b),idle))
    if surcharge:
        minimum_calls=sum(hist.values())+Q(idle,cap)
        out=plus(out,times(power(Q(64),b),Q(32*64**2,10**16)*minimum_calls))
    return minus(out,(Q(64*296,3),)*2)

def root_bracket(fun):
    den=10**15
    lo,hi=0,den//100
    need(fun(Q(lo,den))[1]<0<fun(Q(hi,den))[0], 'strict initial root signs')
    while hi-lo>1:
        mid=(lo+hi)//2
        v=fun(Q(mid,den))
        if v[1]<0:
            lo=mid
        elif v[0]>0:
            hi=mid
        else:
            raise ValueError('insufficient endpoint separation')
    return {'lower':str(Q(lo,den)),'upper':str(Q(hi,den)),
            'decimal_lower':decimal(Q(lo,den)),'decimal_upper':decimal(Q(hi,den)),
            'lower_excess':interval(fun(Q(lo,den))),'upper_excess':interval(fun(Q(hi,den)))}

def poly_after_shift(b,depth,start):
    # E'(L) >= 7bC/(7L+1) + 518b/depth - 111/L^2,
    # since A>=C and log(2)>2/3. Coefficients of its positive denominator
    # numerator after L=start+x are returned in ascending x order.
    a=Q(0) if depth is None else 518*b/depth
    p=[Q(-111),Q(-777),a+7*b*C,7*a]
    from math import comb
    return [sum(p[j]*comb(j,k)*start**(j-k) for j in range(k,4)) for k in range(4)]

def independent_power_check(x,b):
    # Independent exact integer/rational-power calibration for requested
    # rational target exponents, no log/exp identities are used here.
    need(b.denominator<=1000, 'calibration denominator')
    lo,hi=power(x,b)
    target=Q(x)**b.numerator
    need(lo**b.denominator<=target<=hi**b.denominator,'exact rational power calibration')

def negative_controls():
    controls=[]
    def rejects(name,fn):
        try:
            fn()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError('negative control accepted: '+name)
    rejects('retirement_without_returned_idle',lambda:need(C+1158==6279,'missing20 idle ranks'))
    rejects('old_width8_stock_for_five_width4_terminals',lambda:need(C==111*14+438*8+63,'inflated stock'))
    rejects('rank46_under_two_level_guard',lambda:need(64**2>2*46**2,'halving guard'))
    rejects('rank64_as_actual_recursive_child',lambda:need(0<64<64,'proper rank'))
    rejects('corrupted_frozen_word_digest',lambda:need(digest(b'corrupt')=='3bca74a2a8427eb18e86566baa19de597f10d0bc40c30b7443febd499ee2189a','source corruption'))
    return controls

def main():
    auth=authenticate()
    targets=[Q('0.002'),Q('0.003'),Q('0.005')]
    rows=[]
    old=Counter(H)
    old[4]+=5
    for b in targets:
        v=fixed_excess(b)
        need(v[0]>0,'favorable fixed model must fail requested target')
        nofallback=fixed_excess(b,surcharge=False)
        saving=minus(fixed_excess(b,hist=old),v)
        # Exact independent target-power verification for every used base.
        for x in [Q(64,r) for r in H]+[Q(64,45),Q(64),Q(2)]:
            independent_power_check(x,b)
        rows.append({'b':str(b),'complete_optimistic_excess_per_call':interval(v),
                     'without_fallback_excess_per_call':interval(nofallback),
                     'max_retirement_gain_per_call_vs_old_ideal':interval(saving)})
    roots={'native_no_fallback':root_bracket(lambda b:fixed_excess(b,surcharge=False)),
           'conservative_fallback':root_bracket(fixed_excess)}
    allarity=[]
    for depth,start,cutoff in [(2,9,Q('0.002')),(10,11,Q('0.002')),
                               (None,13,Q('0.002019323862'))]:
        checked=[]
        for L in range(3,start+1,2):
            v=relaxed_excess(L,cutoff,depth)
            need(v[0]>0,'all-arity finite starting cases')
            checked.append({'L':L,'excess_per_call':interval(v)})
        poly=poly_after_shift(cutoff,depth,start)
        need(all(x>=0 for x in poly) and poly[0]>0,'all-arity derivative polynomial')
        allarity.append({'depth':depth,'b':str(cutoff),'monotone_for_real_L_at_least':start,
                        'positive_derivative_numerator_coefficients_in_L_minus_start':list(map(str,poly)),
                        'finite_cases':checked})
    # An explicitly unbuilt alternative illustrates the coverage boundary.
    need(64**11>2*60**11 and 64**10<=2*60**10,'depth11 threshold for rank60')
    deeper=fixed_excess(Q('0.002'),cap=60)
    need(deeper[1]<0,'depth11 fractional packing allowance')
    capfree11=root_bracket(lambda b:relaxed_excess(11,b,None))
    out={'status':'PASS_FIVE_TERMINAL_FULL_MOMENT_NECESSARY_SCREENS',
         'checked_at_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,
         'scientific_pin':PIN,'authentication':auth,'inputs':PINS,
         'word':{'H':H,'mass':C,'helpers8':433,'helpers4':5,'adds':36005,'copies7':9,'private_fields':1},
         'fixed_model':{'m':64,'stock_per_call':'296/3','total_mass_per_call':6279,
                        'idle_mass_per_call':1178,'native_halving_rank_cap':45,
                        'deficit_per_call':'107/3','local_child_count':sum(H.values()),
                        'optimistic_fallback_call_count':str(sum(H.values())+Q(1178,45)),
                        'extra_adapters':0,'meaning':'lower bound on actual bill; no owner realization'},
         'targets':rows,'optimistic_roots':roots,'all_odd_arity_obstructions':allarity,
         'cap_free_L11_root':capfree11,
         'unbuilt_depth11_rank60_target_002_excess_per_call':interval(deeper),
         'negative_controls':negative_controls(),
         'scope':'All-parameter written proof plus exact rational endpoint checks; no native, precision, chronological owner or outer admission. Fixed H and unchanged one-unpaid-coordinate coverage. No new kappa.',
         'no_new_kappa':True}
    emit_result('RESULT.json',out)
    print(out['status']+' no_new_kappa')
    print('native optimistic root:',roots['native_no_fallback']['decimal_lower'],roots['native_no_fallback']['decimal_upper'])
    print('fallback optimistic root:',roots['conservative_fallback']['decimal_lower'],roots['conservative_fallback']['decimal_upper'])
    for row in rows:
        print('b='+row['b'],'raw excess/call='+row['complete_optimistic_excess_per_call']['decimal_lower'])
    print('all odd L>=3: b=.002 impossible at depth<=10; b=.002019323862 impossible even with idle rank m')
    print('depth11/rank60 unbuilt budget:',deeper and decimal(-deeper[1]))

if __name__=='__main__':
    main()
