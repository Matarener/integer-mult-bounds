"""Exact finite pooled-pattern bound for the immutable PR4088 export.

No optimizer is imported.  Rational logarithm/exponential enclosures are loaded
unchanged from PR4088's vendor/exact_root.py (PR3945/4076 lineage).  This checker
proves a relaxation, and does not claim a legal chronological/family owner fill.
Prepared with OpenAI Codex assistance.  Apache-2.0.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
import argparse, gzip, hashlib, importlib.util, json, sys
from pathlib import Path

P=Path(__file__).resolve().parent
S=P/'source4088'
W=(5,6,7,8,9)
CAPS=(8,16,32,48)
N=3240
SOURCE_HEAD='76088d49e3ed4142a958659aa996b0ca4da5e88e'
LOWER=Q('0.001730980255989036959962')
UPPER=Q('0.001730980255989036959963')
EXPONENT_RANGE=(Q('0.00173'),Q('0.00174'))

E=None

def load_engine():
    global E
    spec=importlib.util.spec_from_file_location('pinned_exact_root',S/'vendor/exact_root.py')
    E=importlib.util.module_from_spec(spec)
    old=sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode=True
        spec.loader.exec_module(E)
    finally:sys.dont_write_bytecode=old
    E.power_bounds=lru_cache(None)(E.power_bounds)

def need(ok,why):
    if not ok:raise ValueError(why)

def read(rel):
    raw=(S/rel).read_bytes()
    return json.loads(gzip.decompress(raw) if rel.endswith('.gz') else raw)

def rank(vectors):
    pivots={}
    for v in vectors:
        need(type(v) is int and 0<=v<512,'binary frame vector')
        while v:
            p=v.bit_length()-1
            if p in pivots:v^=pivots[p]
            else:pivots[p]=v;break
    return len(pivots)

def source_data():
    t=read('owner/TEMPLATE.json.gz')
    counts=Counter(c['rank'] for c in t['idle_children'])
    children={c['child']:c['rank'] for c in t['idle_children']}
    need(counts=={8:672,16:448,32:448,48:448},'template includes all ports')
    need(len(set(c['port'] for c in t['idle_children']))==112,'112 ports')
    need(Counter(children.values())=={8:6,16:4,32:4,48:4},'18 child slots')
    B={c:counts[c]*360 for c in CAPS}
    local={};widths={}
    for tag in ('base','extra'):
        by_role={};origins={}
        for kind in ('THREE','FOUR'):
            d=read(f'inputs/{kind}-{tag}.json.gz')
            origin=sorted(set(range(224,704))-set(d['removed']));origins[kind]=origin
            need(len(origin)==408,'408 helper identities')
            by_role[kind]={h:rank(d['helper_final'].get(str(h),[1<<j for j in range(9)]))-
                            rank(d['start_extra'].get(str(h),[])) for h in origin}
            width=Counter(by_role[kind].values())
            profile={int(r):v for r,v in d['report']['local_profile'].items()}
            if kind in widths:need(widths[kind]==width and local[kind]==profile,'orientation equality')
            widths[kind]=width;local[kind]=profile
        need(origins['THREE']==origins['FOUR'],'same helper identities')
        changed={h:(by_role['THREE'][h],by_role['FOUR'][h]) for h in origins['THREE']
                 if by_role['THREE'][h]!=by_role['FOUR'][h]}
        need(changed=={601:(8,7)},'only helper601 changes width8 to7')
    need(widths['THREE']=={5:28,6:18,7:56,8:93,9:213},'THREE widths')
    need(widths['FOUR']=={5:28,6:18,7:57,8:92,9:213},'FOUR widths')
    need(local['THREE']=={1:2487,2:713,3:224,4:102,5:20,8:8},'THREE local profile')
    need(local['FOUR']=={1:2489,2:713,3:227,4:99,5:20,8:8},'FOUR local profile')
    return B,local,widths

def patterns():
    out=[]
    for cap in CAPS:
        def rec(i,left,nn):
            if i==len(W):out.append((cap,tuple(nn),left));return
            for n in range(left//W[i]+1):rec(i+1,left-n*W[i],nn+[n])
        rec(0,cap,[])
    need(len(out)==841,'all841 patterns')
    return out

def expr(r=0):return {r:Q(1)} if r else {}

def lin(*terms):
    out=Counter()
    for coeff,x in terms:
        for r,c in x.items():out[r]+=Q(coeff)*c
    return {r:c for r,c in sorted(out.items()) if c}

DELTA=lin((2,expr(1)),(3,expr(3)),(-3,expr(4)))

def potentials(which='middle'):
    v={9:lin((Q(1,5),expr(3)),(-Q(1,5),expr(48)))}
    v[7]=lin((Q(1,2),v[9]),(-Q(1,2),expr(5)))
    if which=='middle':v[8]=lin((1,v[7]),(1,DELTA))
    elif which=='left':v[8]=lin((Q(1,2),v[7]),(Q(1,2),v[9]))
    elif which=='right':
        v[6]=lin((-Q(1,2),expr(48)),(-2,v[9]))
        v[8]=lin((2,v[7]),(-1,v[6]))
    else:raise ValueError(which)
    v[6]=lin((2,v[7]),(-1,v[8]));v[5]=lin((-1,expr(5)))
    u={8:lin((-1,v[8])),16:lin((-1,v[7]),(-1,v[9])),
       32:lin((1,expr(5)),(-3,v[9])),48:expr(48)}
    return u,v

def bound_expression(e,lo,hi,factor_a=False):
    """Enclose sum e[r] H_r uniformly for a in [lo,hi].

    H_r decreases with a.  If sum r e[r]=0, dividing by a rewrites
    this as sum e[r] g_r(a), g_r=(H_r-r)/a.  The derivative of g_r is
    r[1-(1+a log r)exp(-a log r)]/a^2 >=0, so endpoint enclosures suffice.
    """
    if not e:return Q(),Q()
    if factor_a:need(sum(r*c for r,c in e.items())==0,'zero rank mass before factoring a')
    low=high=Q()
    for r,c in e.items():
        if factor_a:
            l=(E.power_bounds(r,lo)[0]-r)/lo
            h=(E.power_bounds(r,hi)[1]-r)/hi
        else:
            l=E.power_bounds(r,hi)[0];h=E.power_bounds(r,lo)[1]
        low+=c*(l if c>0 else h);high+=c*(h if c>0 else l)
    return E.outward(low,high)

def certify_dual(which,lo,hi):
    u,v=potentials(which)
    zero=[];positive=[]
    for cap,nn,r in patterns():
        slack=lin((1,expr(r)),(-1,u[cap]),*((-n,v[w]) for n,w in zip(nn,W)))
        if not slack:zero.append((cap,list(nn),r));continue
        interval=bound_expression(slack,lo,hi,True)
        need(interval[0]>0,f'{which}: nonpositive pattern slack {cap,nn,r,interval}')
        positive.append((interval[0],cap,list(nn),r))
    need(positive,'nontrivial feasibility')
    slope=lin((1,DELTA),(1,v[7]),(-1,v[8]))
    if which=='middle':need(not slope,'exact global mixture stationarity')
    else:
        interval=bound_expression(slope,lo,hi,True)
        need(interval[1]<0 if which=='left' else interval[0]>0,'strict kink slope')
    smallest=min(positive)
    return {'range':list(map(str,(lo,hi))),'patterns':len(patterns()),'identically_tight':zero,
            'strict_pattern_count':len(positive),'minimum_normalized_slack_lower':str(smallest[0]),
            'minimum_normalized_slack_pattern':list(smallest[1:]),
            'capacity_dual':{str(c):{str(r):str(a) for r,a in e.items()} for c,e in u.items()},
            'item_dual':{str(w):{str(r):str(a) for r,a in e.items()} for w,e in v.items()},
            'slope_expression':{str(r):str(a) for r,a in slope.items()},
            'slope_over_a_interval':list(map(str,bound_expression(slope,lo,hi,True)))}

def primal(x):
    # This is the central x=1080 integer witness, not a chronological fill.
    need(x==1080,'central witness mixture')
    return [(8,(0,0,0,1,0),241920),
            (16,(0,0,1,0,1),161280),
            (32,(0,0,0,0,3),1620),
            (32,(0,0,2,0,2),10620),
            (32,(0,1,0,1,2),58320),
            (32,(1,0,0,0,3),90720),
            (48,(0,0,0,0,0),138492),
            (48,(0,0,0,0,5),22788)]

def check_primal(rows,x,B,widths):
    bins=Counter();items=Counter();idle=Counter()
    for cap,nn,y in rows:
        need(all(type(n) is int and n>=0 for n in nn),'whole helper pattern')
        need(type(y) in (int,Q),'exact pattern multiplicity')
        need(y>=0,'nonnegative pattern multiplicity')
        r=cap-sum(w*n for w,n in zip(W,nn));need(r>=0,'capacity')
        bins[cap]+=y
        for w,n in zip(W,nn):items[w]+=y*n
        if r:idle[r]+=y
    need(bins==B,'bin balance')
    need(items=={w:N*widths['THREE'][w]+x*((w==7)-(w==8)) for w in W},'helper balance')
    return dict(sorted(idle.items()))

def determinant(A):
    A=[list(map(Q,row)) for row in A];out=Q(1)
    for j in range(len(A)):
        k=next((k for k in range(j,len(A)) if A[k][j]),None)
        if k is None:return Q()
        if k!=j:A[k],A[j]=A[j],A[k];out=-out
        v=A[j][j];out*=v
        for k in range(j+1,len(A)):
            z=A[k][j]/v
            for t in range(j+1,len(A)):A[k][t]-=z*A[j][t]
    return out

def all_mixture_witness(x):
    """Affine exact relaxation witness for every real x in [0,3240]."""
    x=Q(x)
    need(0<=x<=N,'mixture domain')
    rows=[(8,(0,0,0,1,0),Q(241920)),(16,(0,0,1,0,1),Q(161280)),
          (32,(1,0,0,0,3),Q(90720))]
    if x<=1080:
        rows += [(32,(0,0,0,0,3),1890-x/4),
                 (32,(0,0,1,2,1),540-x/2),
                 (32,(0,0,2,0,2),9810+3*x/4),
                 (32,(0,1,0,1,2),Q(58320)),
                 (48,(0,0,0,0,0),138438+x/20),
                 (48,(0,0,0,0,5),22842-x/20)]
    else:
        rows += [(32,(0,0,0,0,3),1080+x/2),
                 (32,(0,0,2,0,2),10080+x/2),
                 (32,(0,1,0,1,2),59400-x),
                 (48,(0,0,0,0,0),Q(138492)),
                 (48,(0,0,0,0,5),23328-x/2),
                 (48,(0,2,0,0,4),(x-1080)/2)]
    return rows

def reject(label,fn):
    try:fn()
    except ValueError:return label
    raise ValueError('mutation accepted: '+label)

def controls(B,widths,rows,profile):
    out=[]
    out.append(reject('changed_mixture_with_unchanged_primal',lambda:check_primal(rows,1079,B,widths)))
    bad=list(rows);cap,nn,y=bad[2];bad[2]=(cap,nn,y+1)
    out.append(reject('one_extra_primal_pattern',lambda:check_primal(bad,1080,B,widths)))
    wrong=dict(profile);wrong[1]+=1
    out.append(reject('unpaid_extra_rank1',lambda:E.certify_bracket(wrong,LOWER,UPPER)))
    out.append(reject('missing_empty_pattern',lambda:need(len([v for v in patterns() if any(v[1])])==841,'empty patterns required')))
    u,v=potentials();u[8]=lin((1,u[8]),(Q(1,10),expr(1)))
    slack=lin((-1,u[8]),(-1,v[8]))
    out.append(reject('wrong_capacity_dual_sign',lambda:need(bound_expression(slack,UPPER,UPPER)[0]>=0,'dual feasibility')))
    return out

def compute():
    B,local,widths=source_data();rows=primal(1080)
    idle=check_primal(rows,1080,B,widths)
    need(idle=={3:22788,5:1620,48:138492},'optimal idle profile')
    profile=Counter(idle)
    for r,n in local['THREE'].items():profile[r]+=N*n
    for r,n in {1:2,3:3,4:-3}.items():profile[r]+=1080*n
    profile=dict(sorted(profile.items()))
    need(sum(r*n for r,n in profile.items())==65088*360,'complete paid rank mass')
    ml,mh=E.certify_bracket(profile,LOWER,UPPER)
    dual={}
    for which in ('middle','left','right'):
        dual[which]=certify_dual(which,*EXPONENT_RANGE)
    # Affine identities are checked by endpoint values on each linear region;
    # the written proof additionally states nonnegativity throughout the segment.
    for x in map(Q,(0,1080,3240)):
        check_primal(all_mixture_witness(x),x,B,widths)
        u,v=potentials('left' if x<=1080 else 'right')
        for cap,nn,y in all_mixture_witness(x):
            r=cap-sum(w*n for w,n in zip(W,nn))
            slack=lin((1,expr(r)),(-1,u[cap]),*((-n,v[w]) for w,n in zip(W,nn)))
            need(not slack,'affine witness complementary slackness')
    A=[]
    for c in CAPS:A.append([int(cap==c) for cap,nn,y in rows]+[0])
    for w in W:A.append([nn[W.index(w)] for cap,nn,y in rows]+[-int(w==7)+int(w==8)])
    det=determinant(A);need(det!=0,'unique active primal including x')
    old=read('RESULT.json');oldlo,oldhi=Q(old['root_lower']),Q(old['root_upper'])
    literal={int(r):n for r,n in old['profile'].items()}
    delta=lin(*((literal.get(r,0)-profile.get(r,0),expr(r)) for r in set(literal)|set(profile)))
    need(delta=={3:Q(-3),5:Q(5),16:Q(1),32:Q(2),48:Q(-2)},'literal-minus-ideal complete delta')
    gap=bound_expression(delta,LOWER,UPPER,True)
    need(gap[0]>0,'strict literal paid-moment gap')
    sources=['owner/TEMPLATE.json.gz','inputs/THREE-base.json.gz','inputs/THREE-extra.json.gz',
             'inputs/FOUR-base.json.gz','inputs/FOUR-extra.json.gz','RESULT.json','PROOF.md','vendor/exact_root.py']
    with localcontext() as ctx:
        ctx.prec=80
        decimals=[format(Decimal(q.numerator)/Decimal(q.denominator),'.24f') for q in (LOWER,UPPER)]
    output={'status':'PASS_EXACT_POOLED_PATTERN_OPTIMUM','source_head':SOURCE_HEAD,
            'scope':'Optimistic pooled pattern LP; real multiplicities and x; no chronology/family constraints; no supplier or kappa claim.',
            'bin_counts':B,'calls':N,'optimum_fourth_calls':1080,'covered_exponent_range':list(map(str,EXPONENT_RANGE)),
            'primal':[{'capacity':cap,'helper_counts':dict(zip(W,nn)),'multiplicity':y,
                       'residual':cap-sum(w*n for w,n in zip(W,nn))} for cap,nn,y in rows],
            'active_matrix_determinant':str(det),'idle':idle,'complete_profile':profile,
            'root_bracket':[str(LOWER),str(UPPER)],'root_decimal_bracket':decimals,
            'root_bracket_moments':[list(map(str,ml)),list(map(str,mh))],
            'dual':dual,'literal_root_bracket':[str(oldlo),str(oldhi)],
            'ideal_root_gain_over_literal_interval':[str(LOWER-oldhi),str(UPPER-oldlo)],
            'literal_minus_ideal':{r:str(c) for r,c in delta.items()},
            'literal_minus_ideal_moment_over_a_interval':list(map(str,gap)),
            'source_sha256':{f:hashlib.sha256((S/f).read_bytes()).hexdigest() for f in sources},
            'defect_controls':controls(B,widths,rows,profile)}
    return output

def main():
    global S
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=S)
    parser.add_argument('--output',type=Path,help='Write a new certificate; by default compare recomputation with RESULT.json.')
    parser.add_argument('--expected',type=Path,default=P/'RESULT.json')
    parser.add_argument('--controls',action='store_true',help='Accepted explicitly; defect controls always run.')
    args=parser.parse_args();S=args.source.resolve();load_engine();output=compute()
    if args.output:args.output.write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    else:
        # JSON object keys are strings even when the exact calculation used
        # integer ranks.  Compare the serialized value, not Python key types.
        need(json.loads(json.dumps(output))==json.loads(args.expected.read_text()),
             'recomputed exact certificate equals saved JSON value')
    print(json.dumps({k:output[k] for k in ('status','covered_exponent_range','optimum_fourth_calls','idle','complete_profile',
                                         'active_matrix_determinant','root_bracket','ideal_root_gain_over_literal_interval')},sort_keys=True))

if __name__=='__main__':main()
