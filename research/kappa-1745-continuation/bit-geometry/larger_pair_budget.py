#!/usr/bin/env python3
"""Exact larger-pair cap relaxation and complete BIT B5 width8 packing dual.

All computations use the standard library. No owner chronology or native
construction is asserted. Frozen B_K recipe and the preceding generalized
paired-chain theorem retain their source credit; Apache-2.0, substantial
OpenAI assistance.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
import ast
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PRICE = REPO/'research/kappa-next-regime/width-search/review_invoice_outer.py'
RECIPE = REPO/'research/kappa-next-regime/sources/PR3647/research/bit-p111-r437-gl464-470-20261018/vendor/global_k.py'
WORD = HERE.parent/'bit-word/early-birth-prefixes/WORD.json.gz'
DIGEST = 'f84bdf9b2d4e8758584e3a4759519acc2307e3723fb23568bb7ed4fde617a908'
spec = importlib.util.spec_from_file_location('independent_large_pair_price',PRICE)
price = importlib.util.module_from_spec(spec); spec.loader.exec_module(price)
TARGET = Q('.001745')


def decimal(q,places=30):
    s = '-' if q < 0 else ''; z = abs(q*10**places).__floor__()
    return s+str(z//10**places)+'.'+str(z%10**places).zfill(places)


def H(m,r,a):
    if not r:
        return Q(0),Q(0)
    lo,hi = price.log_interval(Q(m,r)); lo,hi = price.exp_interval(a*lo,a*hi)
    return r*lo,r*hi


def moment(profile,m,W,a):
    costs = [(n,H(m,r,a)) for r,n in profile.items()]
    return tuple(sum(n*x[i] for n,x in costs)/(m*W) for i in (0,1))


def bracket(profile,m,W):
    # Complete rational bisection on an 18-decimal grid. Outward interval
    # signs, not approximate root-finder output, decide every branch.
    den = 10**18; low,high = 0,2*10**15
    assert moment(profile,m,W,Q(low,den))[1] < 1
    assert moment(profile,m,W,Q(high,den))[0] > 1
    while high-low > 1:
        mid = (low+high)//2; lo,hi = moment(profile,m,W,Q(mid,den))
        assert hi < 1 or lo > 1, 'insufficient interval precision'
        if hi < 1: low = mid
        else: high = mid
    return {'lower':str(Q(low,den)),'upper':str(Q(high,den)),
            'lower_decimal':decimal(Q(low,den),18),'upper_decimal':decimal(Q(high,den),18),
            'lower_moment_upper':str(moment(profile,m,W,Q(low,den))[1]),
            'upper_moment_lower':str(moment(profile,m,W,Q(high,den))[0])}


def literal_B5_slots():
    function = next(x for x in ast.parse(RECIPE.read_text()).body if isinstance(x,ast.FunctionDef) and x.name == 'recipe')
    namespace = {}; exec(compile(ast.Module(body=[function],type_ignores=[]),str(RECIPE),'exec'),namespace)
    events = namespace['recipe'](5)
    identity = [[int(i == j) for j in range(10)] for i in range(10)]
    matrix = [row[:] for row in identity]
    levels = [-1]*5; advances = []; calls = []
    def add(d,s,c): matrix[d] = [x+c*y for x,y in zip(matrix[d],matrix[s])]
    def advance(pair,to):
        if levels[pair] < to:
            advances.append((pair,levels[pair],to)); levels[pair] = to
    for e in events:
        if e['kind'] == 'local':
            p,s,reverse = e['pair'],e['stage'],e['reverse']; calls.append(s)
            advance(p,s-1); levels[p] = s
            add(2*p,2*p+1,-1) if reverse else add(2*p+1,2*p,1)
        elif e['kind'] == 'bridge':
            d,s,c = e['dst'],e['src'],e['coefficient']
            advance(d,max(levels[d],levels[s])); advance(s,max(levels[d],levels[s]))
            add(2*d,2*s,c); add(2*s+1,2*d+1,-c)
        else:
            assert e['kind'] == 'exchange'
            for p in range(5):
                advance(p,10); matrix[2*p],matrix[2*p+1] = matrix[2*p+1],[-x for x in matrix[2*p]]
    assert matrix == identity and calls == list(range(11))
    slots = Counter()
    for p,x,y in advances: slots[7*(y-x)] += 222
    assert slots == {7:888,14:444,28:444,42:444,56:444}
    return slots,advances


def main():
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    assert sha256(json.dumps(word,sort_keys=True,separators=(',',':')).encode()).hexdigest() == DIGEST
    parent = json.loads(gzip.decompress((HERE.parent/'bit-word/retimed444/WORD.json.gz').read_bytes()))
    assert all(word[k] == parent[k] for k in ('h','v','R','frames','lines','start','final','ret','scatter'))
    programs,details = price.record_programs(word)
    local_bit = details['forward']['profile']
    assert local_bit == details['reverse']['profile'] == {1:1330,2:1327,3:79,4:49,5:90,6:20,7:18}
    local_complex = {1:2439,2:724,3:225,4:102,5:20,8:8}
    rows = []
    for name,v,s,width,local in [('BIT',111,7,3496,local_bit),('complex',112,8,3278,local_complex)]:
        local_mass = sum(r*n for r,n in local.items())
        for K in range(5,9):
            L,m,W = 2*K+1,1+s*(2*K+1),2*K*v
            remaining = 2*v*s*(K-1)*L-L*width
            cap = isqrt((m*m-1)//2)
            assert 2*cap*cap < m*m <= 2*(cap+1)**2
            deficit = m*W-L*local_mass-remaining
            assert deficit == 96*K-(63 if name == 'BIT' else 64)
            relaxed = Counter({r:Q(L*n) for r,n in local.items()}); relaxed[cap] += Q(remaining,cap)
            lo,hi = moment(relaxed,m,W,TARGET)
            row = {'supplier':name,'pairs':K,'calls':L,'m':m,'W_per_replica':W,
                   'local_profile':local,'helper_width_sum':width,'remaining_idle_rank_mass':remaining,
                   'raw_deficit':deficit,'halving_cap':cap,
                   'target_moment_interval':[str(lo),str(hi)],
                   'target_margin_lower_decimal':decimal(lo-1),
                   'target_margin_upper_decimal':decimal(hi-1),
                   'target_rejected_by_relaxation':lo>1,'optimistic_root':bracket(relaxed,m,W)}
            rows.append(row)
    assert all(row['target_rejected_by_relaxation'] for row in rows if row['supplier'] == 'complex')
    assert all(not row['target_rejected_by_relaxation'] for row in rows if row['supplier'] == 'BIT')
    slots,advances = literal_B5_slots()
    m,W,L,cap,demand = 78,1110,11,55,4807
    assert sum((r//8)*n for r,n in slots.items()) == 7104 > demand
    cost = {}
    for r in range(57):
        children = [r] if 0 < r <= cap else ([cap,r-cap] if r > cap else [])
        cost[r] = tuple(sum(H(m,x,TARGET)[j] for x in children) for j in (0,1))
    lam = cost[56][0]/7
    slotdual = {r:min(cost[r-8*k][0]+lam*k for k in range(r//8+1)) for r in slots}
    constraints = []
    for rank in slots:
        for count in range(rank//8+1):
            slack = cost[rank-8*count][0]+lam*count-slotdual[rank]
            assert slack >= 0
            constraints.append({'slot_rank':rank,'width8_roles':count,'residual_rank':rank-8*count,'exact_dual_slack':str(slack)})
    selected = [(7,0,Q(888)),(14,1,Q(444)),(28,3,Q(444)),(42,5,Q(444)),
                (56,7,Q(811,7)),(56,0,Q(2297,7))]
    use,roles,idle = Counter(),Q(0),Counter()
    for r,k,n in selected:
        use[r] += n; roles += k*n; rest = r-8*k
        assert cost[rest][0]+lam*k == slotdual[r]
        for child in ([rest] if 0 < rest <= cap else ([cap,rest-cap] if rest > cap else [])):
            idle[child] += n
    assert use == slots and roles == demand
    profile = Counter({r:Q(L*n) for r,n in local_bit.items()}); profile.update(idle)
    lo,hi = moment(profile,m,W,TARGET)
    lower = (L*sum(n*H(m,r,TARGET)[0] for r,n in local_bit.items())
             +sum(n*slotdual[r] for r,n in slots.items())-lam*demand)/(m*W)
    assert lower == lo and lo > 1
    assert sum(r*n for r,n in profile.items()) == m*W-417
    b5 = {'status':'EXACT_B5_HALVING_LEGAL_PACKING_DUAL_REJECTS_TARGET',
          'literal_10_by_10_integer_recipe_identity':True,'idle_advances':advances,
          'slots':dict(slots),'helper_demand':demand,'whole_width8_capacity':7104,
          'fractional_selection':[{'slot_rank':r,'helpers':k,'count':str(n)} for r,k,n in selected],
          'idle_profile':{r:str(n) for r,n in idle.items()},'halving_cap':cap,
          'helper_dual':str(lam),'slot_dual':{r:str(p) for r,p in slotdual.items()},
          'all_slot_pattern_inequalities':constraints,'complete_rank_deficit':417,
          'target_moment_interval':[str(lo),str(hi)],'target_margin_lower_decimal':decimal(lo-1),
          'optimistic_root':bracket(profile,m,W),
          'scope':'Frozen B5 paired-chain slots, unchanged complete width8 helper stock, fractional pattern counts, no chronology or owner injection. Every nonzero remaining child obeys exact 2r^2<m^2. Omitting fallback favors the construction. Exact dual equality certifies optimality of the stated fractional packing at the target, not a physical realization.'}
    old_certificate = REPO/'research/kappa-adaptive-continuation/architecture/evidence/PAIR-COUNT-CERTIFICATE.json'
    sources = [Path(__file__),PRICE,RECIPE,WORD,HERE.parent/'bit-word/retimed444/WORD.json.gz',
               HERE.parent/'complex/TARGET-BUDGET.json',old_certificate,
               REPO/'research/kappa-adaptive-continuation/architecture/pair_count_certificate.py']
    result = {'status':'EXACT_K5_TO_K8_CAP_SCREEN_AND_STRICT_B5_BIT_PACKING_EXCLUSION',
              'target':str(TARGET),'BIT_word_canonical_sha256':DIGEST,'cap_relaxations':rows,'B5_BIT':b5,
              'scope':'Cap-only rows need only the stated pair-count coverage law and paid-child guard. They impose no slot histogram or clock restriction. Their favorable BIT signs are survival of a relaxation, not evidence of a supplier. The additional B5 dual is narrower and rejects its actual native-bin family.',
              'source_sha256':{str(p.relative_to(REPO)):sha256(p.read_bytes()).hexdigest() for p in sources}}
    (HERE/'LARGER-PAIR-BUDGET.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(result['status'],'B5 root',b5['optimistic_root']['upper_decimal'],'target excess',b5['target_margin_lower_decimal'],flush=True)


if __name__ == '__main__':
    main()
