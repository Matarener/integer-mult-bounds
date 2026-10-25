#!/usr/bin/env python3
"""Complete optimistic H6 mixed-channel rank/stock/moment screens.

Pinned exact positive-series oracle, actual m=1+16L, full816 ordinary K
centres plus816 width17 private K copies, actual idle parts and helper pads.
No constructed full H6 supplier or kappa is inferred from a passing screen.
"""
from collections import Counter
from decimal import Decimal, localcontext
from fractions import Fraction as F
from math import isqrt
from pathlib import Path
import hashlib, json, subprocess, types

HERE = Path(__file__).resolve().parent
REPO = Path('/Users/ross/git/math/integer-mult-bounds')
PIN = '20ecf2891d80b5acf18d980b2164fb44ea7faa90'
N,H,KC,KBILL = 30960,17,816,13872
ORACLE = 'research/h6-independent-audit/invoice/verify.py'
raw = subprocess.check_output(['git','show',PIN+':'+ORACLE],cwd=REPO)
oracle = types.ModuleType('pinned_h6_oracle'); oracle.__file__ = str(REPO/ORACLE)
exec(compile(raw,oracle.__file__,'exec'),oracle.__dict__)
need = oracle.require
SOURCE_HASHES = {ORACLE:hashlib.sha256(raw).hexdigest()}
for rel in ('research/h6-compensation-network/k_encoder/RESULT.json',
            'research/h6-compensation-network/pricing/verify.py'):
    content = subprocess.check_output(['git','show',PIN+':'+rel],cwd=REPO)
    SOURCE_HASHES[rel] = hashlib.sha256(content).hexdigest()
    if rel.endswith('RESULT.json'):
        kr = json.loads(content)
        need(kr['K_ordinary_roles'] == KC and kr['private_descent_C'] == KBILL, 'actual full K inventory')


def dec(x):
    with localcontext() as c:
        c.prec = 24
        return str(Decimal(x.numerator)/Decimal(x.denominator))


def interval(a,b): return {'lower':str(a),'upper':str(b),'lo':dec(a),'hi':dec(b)}


def model(L,source,target,helper,R):
    need(L >= 3 and L%2 == 1, 'odd stages at least3')
    need(sum(source) == sum(target) == 16 and sum(helper) == 17, 'whole residual paths')
    m = 1+16*L; q,p = divmod(m,H); cap = isqrt((m*m-1)//2)
    census = Counter()
    def add(path,count):
        for r in path:
            if r: census[r] += count
    add(source,L*N); add(target,L*N)
    add([17],L*KC)  # K private descents; NOT its ordinary centres
    inherited = oracle.model(L)
    for block in inherited['idle_parts']: add(block,2*N)
    # Ordinary K centres and compensation roles have disjoint paid banks.
    add([17],L*KC); add(helper,L*R)
    if p: add(oracle.partition(p,cap),F(L*(KC+R),q))
    W = F((L-1)*N)+F(L*(KC+R),q)
    D = (L-1)*N-L*KBILL
    need(sum(r*n for r,n in census.items()) == m*W-D, 'complete paid rank mass')
    need(all(m*m > 2*r*r for r in census), 'strict native child cap')
    need(all((q*n).denominator == 1 for n in census.values()), 'integral q-replica profile')
    return {'L':L,'m':m,'q':q,'pad':p,'cap':cap,'H':census,'W':W,'D':D,
            'source':source,'target':target,'helper':helper,'R':R,
            'idle':inherited['idle_slots'],'idle_parts':inherited['idle_parts']}


def pressure(row,b):
    terms = [(n*r,r) for r,n in row['H'].items()]
    return oracle.pressure(terms,row['m'],b)


def target_row(row,k):
    b = k+F(1,10**24)
    lo,hi = pressure(row,b)
    sl,su = row['D']-hi,row['D']-lo
    return {'target':str(k),'exponent_b':str(b),'pressure':interval(lo,hi),
            'raw_slack':interval(sl,su),
            'normalized_moment':interval(1-sl/(row['m']*row['W']),1-su/(row['m']*row['W']))
              if False else interval(1+(lo-row['D'])/(row['m']*row['W']),1+(hi-row['D'])/(row['m']*row['W'])),
            'verdict':'PASSES_OPTIMISTIC_RANK_SCREEN_ONLY' if sl>0 else 'FAILS_OPTIMISTIC_RANK_SCREEN' if su<0 else 'UNRESOLVED'}


def helper_boundary(row,k):
    base = model(row['L'],row['source'],row['target'],row['helper'],0)
    one = model(row['L'],row['source'],row['target'],row['helper'],1)
    unit = Counter(one['H']); unit.subtract(base['H']); need(all(n>=0 for n in unit.values()), 'positive helper bill')
    b = k+F(1,10**24)
    bl,bu = pressure(base,b)
    ul,uu = oracle.pressure([(n*r,r) for r,n in unit.items() if n],row['m'],b)
    need(ul>0,'strict helper monotonicity')
    low,high = (row['D']-bu)/uu,(row['D']-bl)/ul
    count = low.__floor__()
    need(count == high.__floor__(),'exact adjacent integer helper boundary')
    if count < 0:
        need(row['D']-bl < 0,'even zero helpers fails')
        return {'largest_nonnegative_R':None,'zero_helper_verdict':'FAILS','real_threshold':interval(low,high)}
    pass_slack = row['D']-bu-count*uu,row['D']-bl-count*ul
    fail_slack = row['D']-bu-(count+1)*uu,row['D']-bl-(count+1)*ul
    need(pass_slack[0]>0>fail_slack[1],'adjacent strict helper signs')
    return {'largest_nonnegative_R':count,'R_over_N':str(F(count,N)),
            'real_threshold':interval(low,high),'pass_slack':interval(*pass_slack),'next_slack':interval(*fail_slack)}


def main():
    configs = [('single_plane_u2',[1,15],[2,14],[2,15]),
               ('single_plane_u4',[3,13],[4,12],[4,13]),
               ('single_plane_u8',[7,9],[8,8],[8,9]),
               ('single_plane_u16',[15,1],[16],[16,1]),
               ('cyclic_three_group_two_levels',[1,15],[2,1,13],[2,1,14]),
               ('cyclic_seven_group_six_levels',[1,15],[2,1,1,1,1,1,9],[2,1,1,1,1,1,10])]
    targets = list(map(F,('0.002','0.003','0.005')))
    rows = []
    for name,s,t,h in configs:
        for L in range(3,34,2):
            r = model(L,s,t,h,N)
            rows.append({'name':name,'stages':L,'m':r['m'],'q':r['q'],'pad':r['pad'],
                         'child_cap':r['cap'],'source_path':s,'target_path':t,'helper_path':h,
                         'compensation_R':N,'ordinary_K_roles':KC,'K_private_rank':KBILL,
                         'stock_W':str(r['W']),'coverage_deficit':r['D'],
                         'complete_rank_mass':str(sum(rank*n for rank,n in r['H'].items())),
                         'rank_histogram':{rank:str(n) for rank,n in sorted(r['H'].items())},
                         'q_replica_stock':str(r['q']*r['W']),
                         'q_replica_helper_banks':L*(N+KC),
                         'q_replica_helper_pad_rank':L*(N+KC)*r['pad'],
                         'idle_slots':r['idle'],'idle_parts':r['idle_parts'],
                         'targets':[dict(target_row(r,k),helper_boundary=helper_boundary(r,k)) for k in targets]})
    # A cheap all-L tail for the .005 screen, even before helpers/centres.
    # Active data mass is32NL and every split rank<=16. Thus pressure/(NL)
    # >=32*b*log(m/16)>32*b*log L; D/(NL)<1-KBILL/N.
    log33 = oracle.log_interval(F(33))[0]
    tailgap = 32*(F('0.005')+F(1,10**24))*log33-(1-F(KBILL,N))
    need(tailgap>0,'all odd L>=33 fail .005 from active data alone')
    need(all(x['targets'][2]['verdict'].startswith('FAILS') for x in rows if x['stages']<33), 'all scanned L<=31 fail .005 with R=N')
    # Defect controls change a material whole histogram / arity assumption.
    control = model(5,[1,15],[2,1,13],[2,1,14],N)
    before = pressure(control,F('0.003'))
    bad = dict(control,H=Counter(control['H'])); bad['H'][13]-=F(5*(N+KC),4)
    need(pressure(bad,F('0.003')) != before,'omitted helper padding detected')
    badm = dict(control,m=86)
    need(pressure(badm,F('0.003')) != before,'wrong m86 detected')
    badk = dict(control,H=Counter(control['H'])); badk['H'][17]-=5*KC
    need(pressure(badk,F('0.003')) != before,'omitted ordinary K centres detected')
    badc = dict(control,H=Counter(control['H'])); badc['H'][17]-=5*KC
    need(sum(rank*n for rank,n in badc['H'].items()) != control['m']*control['W']-control['D'], 'omitted K private copies break coverage')
    out = {'status':'PASS_COMPLETE_OPTIMISTIC_H6_MIXED_BUDGET_NO_NEW_KAPPA','source_pin':PIN,
           'source_hashes':SOURCE_HASHES,'modern_exponent_convention':'b=k+1e-24; both complete suppliers and all changed-arity/native/physical/analytic interfaces still required.',
           'N':N,'h':H,'K_center_count':KC,'K_private_C':KBILL,
           'rows':rows,'all_L_005_tail_gap_lower':str(tailgap),'negative_controls':4,
           'scope':'Full leading rank/stock moment for declared favorable profiles. No full-domain decomposition, geometry, common labels, approximate-child precision, bank/controller/tape, BIT or outer supplier admitted. Single-plane profiles cannot realize connected full C under the one-visit static-rectangle contract.'}
    (HERE/'OPTIMISTIC-BUDGET-RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']+' rows='+str(len(rows))+' targets=3 controls=4')
    for name,_,_,_ in configs:
        for k in map(str,targets):
            candidates=[x for x in rows if x['name']==name]
            best=max(candidates,key=lambda x:F(next(y for y in x['targets'] if y['target']==k)['raw_slack']['lower']))
            z=next(y for y in best['targets'] if y['target']==k)
            print(name,'target',k,'bestL',best['stages'],'M',z['normalized_moment']['lo'],'maxR',z['helper_boundary']['largest_nonnegative_R'])


if __name__ == '__main__':main()
