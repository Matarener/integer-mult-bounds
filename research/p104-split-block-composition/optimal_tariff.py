"""Classify the optimal chart for every recursive power and audit PR5756.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
PR5756 supplies the published composition. This file adds the all-exponent
chart proof and checks the exact word and complete numerical receipt.
"""
import argparse
from collections import Counter
from contextlib import ExitStack
from fractions import Fraction as Q
from hashlib import sha1,sha256
import gzip
import json
from pathlib import Path
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from sources import sources,load,need
from construct import interval,span
from native_interval import basis


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix=='.gz' else raw)


def encode(x):
    if isinstance(x,Q):
        return str(x)
    if isinstance(x,dict):
        return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):
        return [encode(v) for v in x]
    return x


def profiles(d):
    paid = [d-3]*8+[9-d]*7+[8-d]
    return sorted([x for x in paid if x],reverse=True),sorted([d,9-d],reverse=True)


def majorizes(a,b):
    need(len(a)==len(b) and sum(a)==sum(b),'Equal count and rank mass')
    differences = [sum(a[:i])-sum(b[:i]) for i in range(1,len(a)+1)]
    need(min(differences)>=0,'Every sorted prefix inequality')
    return differences


def balance(a,b):
    current,steps = list(a),[]
    while current!=b:
        i = next(i for i,(x,y) in enumerate(zip(current,b)) if x!=y)
        need(current[i]>b[i],'First unequal prefix has excess')
        j = next(j for j in range(i+1,len(b)) if current[j]<b[j])
        need(current[i]>=current[j]+2,'Strict balancing transfer')
        before = current[:]
        current[i]-=1
        current[j]+=1
        current.sort(reverse=True)
        need(sum(x*x for x in current)<sum(x*x for x in before),'Strict integer potential decrease')
        majorizes(current,b)
        steps.append({'before':before,'donor':i,'receiver':j,'after':current[:]})
    return steps


def global_profiles(word,C):
    """Reduce all canonical subspaces to source-derived rank profiles."""
    model=interval(word)
    lower=frozenset(model['lower'])
    seen,todo={frozenset({0})},[frozenset({0})]
    while todo:
        w=todo.pop()
        for v in lower-w:
            extended=w|{x^v for x in w}
            if extended not in seen:
                seen.add(extended);todo.append(extended)
    need(len(seen)==67,'All subspaces of the four-dimensional input sum')
    incoming=[e[2] for e in word['program'] if e[0]=='MOVE' and e[3]==1090]
    outgoing=[e[3] for e in word['program'] if e[0]=='MOVE' and e[2]==1090]
    spaces={i:span(word['frames'][i]) for i in set(incoming+outgoing)}
    hist={}
    for d in range(4):
        row=Counter(sum(w<=spaces[i] for i in incoming) for w in seen if len(w)==2**d)
        hist[d]=dict(row)
    need(hist=={0:{8:1},1:{0:1,4:14},2:{0:7,2:28},3:{0:7,1:8}},'Exact small-chart incidence classes')
    best={}
    for d in range(4):
        h=max(hist[d])
        paid=[3-d]*h+[5-d]*(8-h)+[9-d]*7+[8-d]
        best[d]=([x for x in paid if x],[x for x in (d,9-d) if x])
    for d in range(4,9):best[d]=profiles(d)
    best[9]=([6]*8+[1],[9])
    representatives=set(seen)|{frozenset(w) for w in model['subspaces']}|{frozenset(range(512))}
    need(len(representatives)==134,'All representatives for the dominance reduction')
    def chart(vectors):
        op=C.canonical_frame(9,tuple(vectors));w=span(vectors)
        need(C.rank([x|(z<<9) for x,z,p in op.tab[9:]])==9,'Full image-space dimension')
        need(all(x in w and all(((x^z)&u).bit_count()%2==0 for u in vectors)
                 for x,z,p in op.tab[9:]),'General native image-space formula')
        return op
    fixed={i:chart(word['frames'][i]) for i in spaces}
    zero,full=chart([]),chart([1<<i for i in range(9)])
    def cost(a,b):return C.rank([x for x,z,p in a.adjoint().then(b).tab[9:]])
    checked=0
    for w in representatives:
        vectors=basis(w);d=len(vectors);op=chart(vectors)
        for i in incoming:
            expected=d+3-2*((len(w&spaces[i])).bit_length()-1)
            need(cost(fixed[i],op)==expected,'Actual incoming Grassmann distance');checked+=1
        for i in outgoing:
            expected=d+len(word['frames'][i])-2*((len(w&spaces[i])).bit_length()-1)
            need(cost(op,fixed[i])==expected,'Actual outgoing Grassmann distance');checked+=1
        need(cost(zero,op)==d and cost(op,full)==9-d,'Both productive target ranks');checked+=2
    need(checked==2412,'Complete representative rank inventory')
    counts=[1]
    for n in range(1,10):
        old=counts;counts=[1]+[old[k]+2**(n-k)*old[k-1] for k in range(1,n)]+[1]
    need(sum(counts)==8283458,'Number of binary subspaces in dimension nine')
    def signed(profile):
        paid,targets=profile;out=Counter(targets);out.subtract(paid);return out
    # Each term is positive, monotone, or a concave subadditivity inequality.
    certificates={
      0:[('difference',7,9,6),('difference',1,8,6),('positive',7,3,0),('difference',1,3,1)],
      1:[('difference',1,9,6),('difference',6,8,6),('difference',1,7,6),('difference',4,2,1),('difference',4,4,1),('positive',6,1,0)],
      2:[('difference',1,9,6),('difference',6,7,6),('positive',5,3,0),('difference',1,3,2),('positive',1,1,0)],
      3:[('difference',1,9,6),('difference',1,5,3),('subadditive',3,2,6),('difference',1,2,1),('positive',3,2,0)]}
    for d,terms in certificates.items():
        total=Counter();positive=False
        for kind,m,a,b in terms:
            need(m>0 and a>0,'Positive coefficient and rank')
            total[a]+=m
            if kind=='positive':positive=True
            elif kind=='difference':need(a>b>0,'Monotone power difference');total[b]-=m
            else:need(kind=='subadditive' and m*a==b,'Exact equal-summand subadditivity');total[b]-=1
        expected=signed(best[9]);expected.subtract(signed(best[d]))
        need(positive and +total==+expected and -total==-expected,'Exact strict global dominance certificate')
    return best,{'lower_space_incidence':hist,'subspaces_by_dimension':counts,
                 'total_subspaces':sum(counts),'native_representatives':134,'native_rank_checks':checked,
                 'small_rank_dominance_certificates':certificates}


def run():
    pins = read(HERE/'SOURCES.json')
    for row in pins['audit_sources']:
        raw = (HERE/row['local_path']).read_bytes()
        need(sha256(raw).hexdigest()==row['sha256']
             and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],
             'Exact PR5756 audit source')
    word = read(HERE/'WORD.json.gz')
    published = read(HERE/'source/pr5756/WORD.json.gz')
    a,b = dict(word),dict(published)
    a.pop('schema');b.pop('schema')
    need(a==b,'Same complete PR5756 word, apart from schema label')
    canonical_hash = sha256(json.dumps(a,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    own,other = read(HERE/'RESULT.json'),read(HERE/'source/pr5756/RESULT.json')
    keys = ['kappa','kappa_decimal','raw_root_interval','targets','paid','productive_fields',
            'paid_calls','rank_mass_surplus','strictification','compiler','outer','ordinary_BIT','nonrecursive']
    for key in keys:
        need(own['complete_cost'][key]==other['complete_cost'][key],'Same complete invoice field: '+key)
    need(own['local']==other['local'] and own['native']==other['native']
         and own['physical_caller']==other['physical'],'Same local, native and physical receipts')
    spaces = interval(word)
    p4,t4 = profiles(4)
    witnesses = {}
    for d in (5,6,7):
        pd,td = profiles(d)
        paid = majorizes(p4,pd)
        targets = majorizes(td,t4)
        need(max(paid)>0,'Strict paid majorization')
        witnesses[d] = {'paid_prefix_differences':paid,'target_prefix_differences':targets,
                        'paid_balancing_transfers':balance(p4,pd),
                        'target_balancing_transfers':balance(td,t4)}
    # After equal terms cancel, the rank-four minus rank-eight margin is D(C).
    def signed(d):
        p,t = profiles(d)
        out = Counter(t)
        out.subtract(p)
        return out
    delta = signed(4)
    delta.subtract(signed(8))
    need({r:c for r,c in delta.items() if c}=={1:-2,5:2,8:-1},'Exact two-chart power difference')
    with ExitStack() as contexts:
        cursor,_ = contexts.enter_context(sources())
        for depth in range(5):
            cursor,root = contexts.enter_context(load(cursor/'sources.py','tariff_source_'+str(depth)).sources())
        E = load(root/'research/higher-moment-strictification/verify.py','block_tariff_intervals')
        def D(c):
            a,b = E.power(5,1-c),E.power(8,1-c)
            return 2*a[0]-b[1]-2,2*a[1]-b[0]-2
        l5,l8 = E.log_bounds(5),E.log_bounds(8)
        d0 = 8*l8[0]-10*l5[1],8*l8[1]-10*l5[0]
        d1 = l8[0]-2*l5[1],l8[1]-2*l5[0]
        need(d0[0]>0 and d1[1]<0,'Opposite strict derivative signs at the endpoints')
        # D'(C)/5^(1-C) = (8/5)^(1-C) log(8) - 2 log(5).
        # It strictly decreases. Thus D has one maximum and one interior zero.
        need(2*5-8-2==0 and 2-1-2==-1,'Exact endpoint values D(0), D(1)')
        grid = 10**14
        lo,hi = grid//10,grid//5
        need(D(Q(lo,grid))[0]>0 and D(Q(hi,grid))[1]<0,'Initial strict root bracket')
        while hi-lo>1:
            mid = (lo+hi)//2
            if D(Q(mid,grid))[0]>0:
                lo = mid
            else:
                hi = mid
        low,high = Q(lo,grid),Q(hi,grid)
        need(D(low)[0]>0 and D(high)[1]<0,'Strict rational switch enclosure')
        need(Q('.0034')<low and D(Q('.0034'))[0]>0,'Current admitted BIT band lies in rank-four regime')
        need(D(Q(1,10))[0]>0 and D(Q(1,5))[1]<0,'Reject either chart as a universal winner')
        C=load(root/'research/p104-native-channel/vendor/clifford_exact.py','global_block_native')
        best,global_data=global_profiles(word,C)
        l6,l9=E.log_bounds(6),E.log_bounds(9)
        derivative_gaps={
          '9_vs_4_t0':8*l6[0]-l9[1]-6*l5[1],
          '9_vs_4_t1':8*l6[0]-Q(3,2)*l9[1]-5*l5[1],
          '9_vs_8_t0':8*l6[0]+l8[0]-l9[1]-8*l5[1],
          '9_vs_8_t1':8*l6[0]+l8[0]-Q(3,2)*l9[1]-Q(20,3)*l5[1]}
        need(min(derivative_gaps.values())>0,'Convex endpoint bounds prove both global differences strictly increase in C')
        def difference(positive,negative,c):
            a,b=E.moment(positive,1-c),E.moment(negative,1-c)
            return a[0]-b[1],a[1]-b[0]
        def global_margin(d,c):
            p9,t9=best[9];pd,td=best[d]
            pos=Counter(t9);pos.update(pd);neg=Counter(p9);neg.update(td)
            return difference(pos,neg,c)
        def increasing_root(d):
            a,b=0,grid
            need(global_margin(d,Q(0))[1]<0 and global_margin(d,Q(1))[0]>0,'Strict global endpoint signs')
            while b-a>1:
                m=(a+b)//2;value=global_margin(d,Q(m,grid))
                if value[0]>0:b=m
                else:need(value[1]<0,'Root comparison resolves exactly');a=m
            result=[Q(a,grid),Q(b,grid)]
            need(global_margin(d,result[0])[1]<0 and global_margin(d,result[1])[0]>0,'Exact global root bracket')
            return result
        switch94,switch98=increasing_root(4),increasing_root(8)
        need(switch98[1]<switch94[0]<switch94[1]<low,'Strict ordering removes rank eight from the global envelope')
        need(Q('.01')<switch94[0],'All canonical charts are optimized through the one-percent target')
        claim=Q(own['complete_cost']['kappa'])
        T=Counter({int(r):n for r,n in own['complete_cost']['targets'].items()})
        P=Counter({int(r):n for r,n in own['complete_cost']['paid'].items()})
        complete=difference(T,P,claim)
        margins={}
        for d in (5,6,7,8,9):
            paid,targets=best[d]
            pos=Counter(t4);pos.update(paid);neg=Counter(p4);neg.update(targets)
            margins[d]=difference(pos,neg,claim)
        # A different rank-four position has at least one extra rank-two cost.
        a9,a7=E.power(9,1-claim),E.power(7,1-claim)
        outside4=a9[0]-a7[1]
        need(0<complete[0]<=complete[1]<min([outside4]+[x[0] for x in margins.values()]),
             'One changed local chart already destroys the published complete margin')
        global_data.update(best_profiles=best,strict_derivative_endpoint_gaps=derivative_gaps,
            rank9_vs_rank4_switch=switch94,rank9_vs_rank8_switch=switch98,
            complete_margin_at_published_claim=E.display(complete),
            per_local_alternative_gaps={d:E.display(v) for d,v in margins.items()},
            alternative_rank4_gap_lower=outside4,
            classification={'C=0':'The 67 nested-interval charts tie',
                '0<C<C_global':'Only the rank-four lower space wins',
                'C=C_global':'The rank-four lower space and the full rank-nine space tie',
                'C_global<C<=1':'Only the full rank-nine space wins'},
            scope='Optimistic one-canonical-chart rank tariff; nonnested Gaussian transitions are allowed and all boundary ranks are charged. Zero-rank jobs have zero recursive price. This does not admit the high-saving caller.')
        return encode({'status':'PASS_EXACT_ALL_EXPONENT_BLOCK_CHART_OPTIMUM_AND_PR5756_AUDIT',
            'source_pr5756':'a1b338e5d9271b541f2a198f4fc19cefc565feed',
            'canonical_word_sha256_without_schema':canonical_hash,'equal_invoice_fields':keys,
            'productive_fields':own['complete_cost']['productive_fields'],
            'paid_calls':own['complete_cost']['paid_calls'],
            'subspaces_by_rank':spaces['subspaces_by_rank'],'strict_majorization':witnesses,
            'rank4_minus_rank8':'2*5^(1-C) - 8^(1-C) - 2',
            'switch_interval':[low,high],'switch_margins':[E.display(D(low)),E.display(D(high))],
            'derivative_endpoints':[E.display(d0),E.display(d1)],
            'classification':{'C=0':'All 67 charts tie by rank mass',
                '0<C<C_star':'The unique rank-four chart is optimal',
                'C=C_star':'The rank-four and rank-eight charts tie; all others lose',
                'C_star<C<=1':'The unique rank-eight chart is optimal'},
            'current_band':'The rank-four chart wins for every 0<C<=.0034',
            'global_canonical_relaxation':global_data,
            'limits':['This is a fixed-block recursive tariff theorem, not a multiplication exponent near C_star.',
                      'The published composition and kappa are credited to PR5756.',
                      'The complete replay retains its five framework assumptions.']})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='block-tariff-cache-') as cache:
        sys.pycache_prefix=cache
        result=run()
    path=HERE/'TARIFF.json'
    if args.write:
        path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        need(read(path)==result,'Exact all-exponent receipt')
    print(result['status'])
    print('Nested switch interval:',result['switch_interval'])
    print('Global switch interval:',result['global_canonical_relaxation']['rank9_vs_rank4_switch'])


if __name__=='__main__':
    main()
