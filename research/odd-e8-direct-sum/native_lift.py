"""Check the separated native-lift cost gate for the odd E8 family.

This is a lower bound for a declared module interface, not all producers.
Prepared for Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from functools import cache
from hashlib import sha256
from math import comb, isqrt
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT/'research/native-center-free-code/SOURCE-WORD.json.gz'
NORMAL = ROOT/'research/coded-native-caller/NORMALIZERS.json'
SOURCE_SHA = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
NORMAL_SHA = 'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da'
EXPONENT = F(151, 50000)


def need(value, message):
    if not value:
        raise ValueError(message)


def rank(matrix):
    rows = [[F(x) for x in row] for row in matrix]
    pivot = 0
    for col in range(len(rows[0])):
        hit = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if hit is None:
            continue
        rows[pivot], rows[hit] = rows[hit], rows[pivot]
        scale = rows[pivot][col]
        rows[pivot] = [x/scale for x in rows[pivot]]
        for i in range(pivot+1, len(rows)):
            scale = rows[i][col]
            rows[i] = [x-scale*y for x,y in zip(rows[i], rows[pivot])]
        pivot += 1
    return pivot


def spectral_contract():
    raw = NORMAL.read_bytes()
    need(sha256(raw).hexdigest() == NORMAL_SHA, 'Normalizer bytes changed')
    data = json.loads(raw)
    roots = list(zip(*data['mode_columns']))
    supports = [tuple(j for j,x in enumerate(row) if x) for row in roots]
    C4 = [[sum(x*y for x,y in zip(a,b)) for b in roots] for a in roots]
    B4 = [[x if supports[i] == supports[j] else 0 for j,x in enumerate(row)]
          for i,row in enumerate(C4)]
    for i in range(112):
        for j in range(112):
            need(sum(B4[i][t]*B4[t][j] for t in range(112)) == 8*B4[i][j],
                 'The cube projection identity failed')
            need(sum(B4[i][t]*C4[t][j] for t in range(112)) == 8*C4[i][j],
                 'The full code must lie in the cube subspace')
    need(sum(C4[i][i] for i in range(112)) == 448, 'The trace changed')
    need(all(sum(data['mode_columns'][a][i]*data['mode_columns'][b][i]
                 for i in range(112)) == 56*(a == b)
             for a in range(8) for b in range(8)), 'The full code covariance failed')
    return {'kernel_dimension':56, 'active_dimension':56,
            'active_eigenvalues':{'2':48,'-12':8}}


def helper_profile(c,word):
    paid,targets = Counter(),Counter()
    for owner in range(224,632):
        steps = [e for e in word if e[0] == 'climb' and e[2] == owner]
        need(all(e[-1] == len(c['frames'][e[4]])-len(c['frames'][e[3]]) > 0
                 for e in steps), 'A helper climb has the wrong rank')
        segments = [e[-1] for e in steps]
        width = len(c['frames'][c['final'][owner]])-len(c['frames'][c['start'][owner]])
        need(sum(segments) == width and width > 0, 'A helper path does not partition its target')
        paid.update(segments)
        targets[width] += 1
    need(paid == {1:1513,2:201,3:432,4:50,5:12}, 'Helper paid profile changed')
    need(targets == {4:28,7:7,8:47,9:326}, 'Helper target profile changed')
    return paid,targets


def helper_bill():
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_SHA, 'Native payload changed')
    source = json.loads(raw)
    c = source['canonical']
    profiles = [helper_profile(c,source['programs'][direction])
                for direction in ('forward','backward')]
    need(profiles[0] == profiles[1], 'The two orientations have different helper bills')
    bad = source['programs']['forward'][:]
    omitted = next(i for i,e in enumerate(bad) if e[0] == 'climb' and e[2] >= 224)
    bad.pop(omitted)
    try:
        helper_profile(c,bad)
    except ValueError:
        pass
    else:
        raise ValueError('An omitted helper climb was accepted')
    return profiles[0]


def check_face(X,Y):
    for a in range(2):
        for b in range(2):
            for c in range(2):
                for d in range(2):
                    for e in range(2):
                        for f in range(2):
                            ha,hb = (2,-12)[a],(2,-12)[b]
                            lhs = ha*int(a == d)*X[2*b+c][2*e+f]+hb*int(b == e)*Y[2*a+c][2*d+f]
                            rhs = (ha+hb-F(ha*hb,2))*int(a == d and b == e and c == f)
                            need(lhs == rhs, 'The two-factor decomposition failed')


def face_fixtures():
    # The proof permits an arbitrary operator S on the passive space.
    matrices = [[[F(1,4),0],[0,F(-1,4)]],
                [[F(1,4),1],[0,F(1,4)]],
                [[0,1],[-1,0]]]
    receipts = []
    for S in matrices:
        pencils = [[[F(a)*int(i == j)+F(b)*S[i][j] for j in range(2)] for i in range(2)]
                   for a,b in ((F(1,2),2),(4,-12),(F(1,2),-2),(4,12))]
        ranks = list(map(rank,pencils))
        cost = 48*(ranks[0]+ranks[2])+8*(ranks[1]+ranks[3])
        need(cost >= 64*2, 'The operator-pencil lower bound failed')
        X = [[pencils[a//2][a%2][b%2] if a//2 == b//2 else 0 for b in range(4)] for a in range(4)]
        Y = [[pencils[2+a//2][a%2][b%2] if a//2 == b//2 else 0 for b in range(4)] for a in range(4)]
        check_face(X,Y)
        try:
            check_face(X,X)
        except ValueError:
            pass
        else:
            raise ValueError('The reversed pencil sign was accepted')
        receipts.append({'pencil_ranks':ranks,'weighted_rank_sum':cost})
    return receipts


def log_series(z):
    value = F(0)
    term = z
    for j in range(24):
        value += 2*term/(2*j+1)
        term *= z*z
    remainder = 2*term/(49*(1-z*z))
    return value, value+remainder


@cache
def power_interval(n):
    if n == 1:
        return F(1), F(1)
    shift = n.bit_length()-1
    low2,high2 = log_series(F(1,3))
    low,high = log_series(F(n-2**shift,n+2**shift))
    low,high = low+shift*low2,high+shift*high2
    unit = 10**30
    low = F((low*unit).__floor__(),unit)*EXPONENT
    high = F((high*unit).__ceil__(),unit)*EXPONENT
    terms = []
    for x in (low,high):
        total,term = F(1),F(1)
        for j in range(1,19):
            term *= x/j
            total += term
        terms.append(total)
    next_term = term*high/19
    upper_exp = terms[1]+next_term/(1-high/20)
    need(0 <= low <= high < 1, 'The exponential enclosure domain failed')
    return F(n)/upper_exp,F(n)/terms[0]


def small_interval(low,high):
    unit = 10**18
    return [str(F((low*unit).__floor__(),unit)),str(F((high*unit).__ceil__(),unit))]


def gate(paid,targets,copy_ranks):
    v = 112**3
    channels = 3*(2*56-48)*56
    need(channels == 10752, 'The channel floor changed')
    helper_low = sum(n*power_interval(r)[0] for r,n in paid.items())-sum(n*power_interval(r)[1] for r,n in targets.items())
    helper_high = sum(n*power_interval(r)[1] for r,n in paid.items())-sum(n*power_interval(r)[0] for r,n in targets.items())
    copy_counts = {copy_ranks[0]:21504,copy_ranks[1]:512}
    local_low = 10+power_interval(8)[0]+2*power_interval(15)[0]
    local_high = 10+power_interval(8)[1]+2*power_interval(15)[1]
    local_low += sum(n*power_interval(r)[0] for r,n in copy_counts.items())/v+channels*helper_low/v
    local_high += sum(n*power_interval(r)[1] for r,n in copy_counts.items())/v+channels*helper_high/v
    records = []
    for stages in range(3,63,2):
        m = 24*stages+1
        cap = isqrt((m*m-1)//2)
        target_low,target_high = [F(stages-1,stages)*x for x in power_interval(m)]
        idle_low,idle_high = [F(24*(stages-3),cap)*x for x in power_interval(cap)]
        lower,upper = target_low-idle_high-local_high,target_high-idle_low-local_low
        need(upper < 0, 'The separated lift was not excluded')
        records.append({'stages':stages,'ambient':m,'idle_cap':cap,
                        'margin_per_port_per_local_call':small_interval(lower,upper)})
    tail_upper = F(49,1513)*power_interval(1513)[1]-local_low
    need(tail_upper < 0, 'The all-stage tail gate failed')
    return {'copy_ranks':copy_ranks,'module_channels_lower_bound':channels,
            'module_fraction':'6/7','helper_cost_per_port':small_interval(helper_low/112,helper_high/112),
            'finite_stages':records,'tail_from_stage':63,
            'tail_margin_upper':small_interval(tail_upper,tail_upper)[1]}


def larger_factor_gates(paid,targets):
    helper_low = sum(n*power_interval(r)[0] for r,n in paid.items())-sum(n*power_interval(r)[1] for r,n in targets.items())
    k = 5
    v = 112**k
    copy_low = sum(comb(k,j)*8**j*112**(k-j)*power_interval(6*j+2)[0]
                   for j in range(3,6))/v
    local_low = 16+power_interval(14)[0]+2*power_interval(25)[0]
    local_low += copy_low+F(5,24)*helper_low/112
    records = []
    for stages in (3,5):
        m = 40*stages+1
        cap = isqrt((m*m-1)//2)
        upper = F(stages-1,stages)*power_interval(m)[1]-F(40*(stages-3),cap)*power_interval(cap)[0]-local_low
        need(upper < 0, 'The five-factor finite gate failed')
        records.append({'stages':stages,'margin_upper':small_interval(upper,upper)[1]})
    # For N>=7, even a parent-width idle child does not fit. The derivative
    # bound in the proof makes this upper bound decrease with N.
    tail_upper = F(80+1-F(1,7),281)*power_interval(281)[1]-local_low
    need(F(1,5)+F(1,40*25) < EXPONENT*(80+F(4,5)), 'The five-factor stage monotonicity bound failed')
    need(tail_upper < 0, 'The five-factor infinite tail failed')
    pent = {'module_fraction':'5/24','finite_stages':records,
            'tail_from_stage':7,'tail_margin_upper':small_interval(tail_upper,tail_upper)[1]}
    # For all k>=7 grant every copy and helper for free. The proof shows
    # that the remaining main-path bound decreases with k.
    main_low = 22+power_interval(20)[0]+2*power_interval(35)[0]
    upper3 = F(2,3)*power_interval(169)[1]-main_low
    upper5 = F(112+F(4,5),281)*power_interval(281)[1]-main_low
    need(F(1,5)+F(1,56*25) < EXPONENT*(112+F(4,5)), 'The large-factor stage monotonicity bound failed')
    need(upper3 < 0 and upper5 < 0, 'The all-factor main-path gate failed')
    large = {'factors_from':7,'all_copies_and_helpers_granted_free':True,
             'stage3_upper':small_interval(upper3,upper3)[1],
             'stages_from5_upper':small_interval(upper5,upper5)[1]}
    return {'five_factors':pent,'all_larger_odd_factors':large}


def run():
    spectrum = spectral_contract()
    paid,targets = helper_bill()
    result = {'status':'PASS_ODD_E8_SEPARATED_NATIVE_LIFT_GATE',
              'test_exponent':str(EXPONENT),'spectral_contract':spectrum,
              'helper_paid':dict(paid),'helper_targets':dict(targets),
              'controls':['omitted_helper_climb','reversed_pencil_sign'],
              'operator_pencil_fixtures':face_fixtures(),
              'gates':[gate(paid,targets,(14,20)),gate(paid,targets,(15,22))],
              'larger_factor_gates':larger_factor_gates(paid,targets),
              'scope':'Separated H_i modules with one frozen complete helper bank per coefficient channel; declared main paths and idle cap. Other coefficient maps are granted free. Joint producers, address-dependent coefficients, shared helper protocols, other module words and changed caller profiles are outside the result.'}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    receipt = HERE/'NATIVE-LIFT.json'
    if args.write:
        receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    else:
        need(result == json.loads(receipt.read_text()), 'The native-lift receipt differs')
    print(result['status'],'channels=10752 exponent=151/50000 odd_factors=all_at_least_3 odd_stages=all_at_least_3')
