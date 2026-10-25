#!/usr/bin/env python3
"""Exact architectural price gates; no native supplier or outer replay.
Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
Exchange/convexity predecessors: Ali Romman, Cinna Davis and Chris R.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256, sha1
from itertools import product
from math import factorial
from pathlib import Path
import argparse
import base64
import json
import zlib

ROOT = Path(__file__).resolve().parent
Q = 1 << 224


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceildiv(a, b):
    return -((-a) // b)


class I:
    """Closed interval of integers divided by Q, with directed rounding."""
    def __init__(self, lo, hi=None):
        self.lo, self.hi = lo, lo if hi is None else hi
        require(self.lo <= self.hi, 'reversed interval')

    @staticmethod
    def of(x):
        if isinstance(x, I):
            return x
        x = F(x)
        return I(x.numerator * Q // x.denominator,
                 ceildiv(x.numerator * Q, x.denominator))

    def __add__(self, other):
        o = I.of(other)
        return I(self.lo + o.lo, self.hi + o.hi)
    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + (-I.of(other))

    def __rsub__(self, other):
        return I.of(other) - self

    def __mul__(self, other):
        o = I.of(other)
        products = [a*b for a in (self.lo,self.hi) for b in (o.lo,o.hi)]
        return I(min(products)//Q, ceildiv(max(products),Q))
    __rmul__ = __mul__

    def __truediv__(self, n):
        require(type(n) is int and n > 0, 'positive integer divisor required')
        return I(self.lo//n, ceildiv(self.hi,n))

    def positive(self):
        return self.lo > 0

    def negative(self):
        return self.hi < 0

    def contains_zero(self):
        return self.lo <= 0 <= self.hi

    def json(self):
        return {'lower':str(F(self.lo,Q)), 'upper':str(F(self.hi,Q))}


def log_series(z):
    """2 atanh(z), 0<=z<=1/3; rational remainder after 96 terms."""
    require(0 <= z <= F(1,3), 'log series domain')
    x = I.of(z)
    x2 = x*x
    term, total = x, I.of(0)
    for j in range(96):
        total += term/(2*j+1)
        term = term*x2
    tail = 2*z**193/(193*(1-z*z))
    return 2*total + I(0,ceildiv(tail.numerator*Q,tail.denominator))


@lru_cache(None)
def log_int(n):
    require(type(n) is int and n > 0, 'positive log input')
    k = n.bit_length()-1
    return k*log_series(F(1,3)) + log_series(F(n-2**k,n+2**k))


def exp_positive(x):
    require(x.lo >= 0 and x.hi <= 16*Q, 'exp domain')
    y = x/16
    term, total = I.of(1), I.of(1)
    for j in range(1,65):
        term = (term*y)/j
        total += term
    # y<=1: tail <= 1/65! * sum_(k>=0) (1/66)^k.
    tail = F(66,65*factorial(65))
    total += I(0,ceildiv(tail.numerator*Q,tail.denominator))
    for _ in range(4):
        total = total*total
    return total


@lru_cache(None)
def power(r,t):
    require(type(r) is int and r >= 0 and 0 <= t <= 1, 'power domain')
    if r == 0:
        require(t > 0, 'zero to zero excluded')
        return I.of(0)
    if t == 0 or r == 1:
        return I.of(1)
    if t == 1:
        return I.of(r)
    return exp_positive(log_int(r)*t)


def moment(hist,t):
    return sum((w*power(r,t) for r,w in hist.items()),I.of(0))


def clean(hist):
    return {int(k):v for k,v in hist.items() if v}


def canonical(n,v,paid,helpers,b=8):
    """Complete attained minimum at fixed FULL count, including n=0,1,2."""
    P = Counter({r:n*w for r,w in paid.items()})
    T = Counter({r:n*w for r,w in helpers.items()})
    T[1+b*n] += 2*v
    if n < 3:
        P[1] += v*(3-n)
    else:
        P[1] += v*(n-3)
        a = (n-3)//2
        for length in (a,n-3-a):
            for k in range(2,length+2):
                P[b*k] += 2*v
                T[1+b*k] += 2*v
    return clean(P),clean(T)


def cost(profile,n,C):
    p,h = canonical(n,*profile)
    return moment(p,1-C)-moment(h,1-C)


def derivative_gate(profile,b=8):
    """Upper bound on d/dt [L(t)/b^t] throughout 0<t<1."""
    _,P,H = profile
    U = -F(P.get(1,0),b)*log_int(b)
    for r,w in P.items():
        if r > b:
            U += F(w*r,b)*(log_int(r)-log_int(b))
    for r,w in H.items():
        if r < b:
            U += w*(log_int(b)-log_int(r))
    require(U.negative(),'local monotonicity not certified')
    return U


def gate(profile,C,n):
    x = cost(profile,n,C)
    before = x-cost(profile,n-1,C)
    after = cost(profile,n+1,C)-x
    require(x.positive() and before.negative() and after.positive(),
            'all-n exclusion gate failed')
    return {'C':str(C),'minimizing_full_count':n,'minimum':x.json(),
            'previous_difference':before.json(),'next_difference':after.json()}


def ratio_gate(profile,C,n):
    # J_j=j*C_(j+1)-(j+1)*C_j. Strict convexity makes J strictly increasing.
    x = cost(profile,n,C)
    before = (n-1)*x-n*cost(profile,n-1,C)
    after = n*cost(profile,n+1,C)-(n+1)*x
    require(before.negative() and after.positive(),'all-n discount gate failed')
    return {'C':str(C),'minimizing_full_count':n,'discount':(x/n).json(),
            'previous_ratio_numerator':before.json(),'next_ratio_numerator':after.json()}


def authenticate():
    origins = json.loads((ROOT/'ORIGINS.json').read_text())
    objects = {}
    for oid,record in origins['objects'].items():
        decoder = zlib.decompressobj()
        raw = decoder.decompress(base64.b64decode(record['zlib_base64']),2**20+1)
        require(len(raw) <= 2**20 and decoder.eof and not decoder.unused_data,
                'origin object size or stream')
        kind = record['type']
        require(kind in ('tree','commit'),'origin object type')
        header = (kind+' '+str(len(raw))+'\0').encode()
        require(sha1(header+raw).hexdigest() == oid,'origin object hash')
        objects[oid] = (kind,raw)
    def obj(oid,kind):
        require(oid in objects and objects[oid][0] == kind,'missing origin object')
        return objects[oid][1]
    def edge(tree,name):
        raw = obj(tree,'tree')
        offset = 0
        matches = []
        while offset < len(raw):
            end = raw.index(b'\0',offset)
            mode,label = raw[offset:end].split(b' ',1)
            require(end+21 <= len(raw),'truncated origin tree')
            if label == name.encode():
                matches.append((mode,raw[end+1:end+21].hex()))
            offset = end+21
        require(len(matches) == 1,'origin edge missing or ambiguous')
        return matches[0]
    for row in origins['files']:
        raw = (ROOT/row['retained_path']).read_bytes()
        require(sha256(raw).hexdigest() == row['sha256'],'retained source hash')
        header = ('blob '+str(len(raw))+'\0').encode()
        require(sha1(header+raw).hexdigest() == row['git_blob'],'retained Git blob')
        commit = obj(row['commit'],'commit')
        first = commit.splitlines()[0]
        require(first.startswith(b'tree '),'origin commit root')
        tree = first[5:].decode()
        parts = row['path'].split('/')
        for index,part in enumerate(parts):
            mode,tree = edge(tree,part)
            require(mode in ((b'100644',b'100755') if index == len(parts)-1 else (b'40000',)),
                    'origin edge mode')
        require(tree == row['git_blob'],'origin leaf differs')


def load_profiles():
    neutral = json.loads((ROOT/'inputs/neutral-invoice.json').read_text())
    profiles = {'neutral5413':(112,clean(neutral['local_paid']),
                              clean(neutral['local_productive_helpers']))}
    for pr in (5544,5545,5551):
        d = json.loads((ROOT/f'inputs/p104-{pr}.json').read_text())
        prof = (104,clean(d['local']['paid']),clean(d['local']['helpers']))
        profiles[f'p104_{pr}'] = prof
        require(canonical(18,*prof) == (clean(d['complete_cost']['paid']),
                clean(d['complete_cost']['targets'])),'P104 source path invoice')
    require(canonical(18,*profiles['neutral5413']) ==
            (clean(neutral['histograms']['paid']),clean(neutral['histograms']['productive'])),
            'neutral source path invoice')
    profiles['round3_4610'] = (112,{1:2201,2:412,3:510,4:127,5:40,8:8},
                             {4:28,7:7,8:47,9:326})
    source = (ROOT/'inputs/round3-proof.md').read_text()
    require('P = {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}' in source and
            'H = {4:28, 7:7, 8:47, 9:326}' in source,'round3 profile binding')
    v,p,h = profiles['neutral5413']
    free_p = dict(p)
    require(free_p.pop(8) == 8,'free-centre relaxation source')
    profiles['neutral_free_eight_H8'] = (v,free_p,dict(h))
    return profiles


def mask_invoice(profile,p,a,bits):
    """Literal path equation, separate from canonical implementation."""
    v,paid,helpers = profile
    n = sum(bits)
    P = Counter({r:n*w for r,w in paid.items()})
    H = Counter({r:n*w for r,w in helpers.items()})
    P[1] += v*(2*p+1-n)
    H[1+8*n] += 2*v
    for j in range(1,p):
        h = sum(bits[:2*j]) if j <= a else sum(bits[2*j+1:])
        e = bits[2*j]
        if h:
            P[8*h] += 2*v
        if e:
            P[8] += 2*v
        H[1+8*(h+e)] += 2*v
    return clean(P),clean(H)


def controls(profiles):
    require(log_int(1).contains_zero(),'ln 1')
    require((log_int(4)-2*log_int(2)).contains_zero(),'log identity')
    require((power(9,F(1,2))-3).contains_zero(),'sqrt identity')
    require((power(81,F(1,4))-3).contains_zero(),'fourth root identity')
    checks = 0
    prof = profiles['p104_5551']
    for t in (F(1,2),F(999,1000)):
        for p in range(1,4):
            for a in range(p):
                for bits in product((0,1),repeat=2*p+1):
                    P,H = mask_invoice(prof,p,a,bits)
                    cp,ch = canonical(sum(bits),*prof)
                    delta = Counter(P)
                    for hist,sign in ((H,-1),(cp,-1),(ch,1)):
                        for r,w in hist.items():
                            delta[r] += sign*w
                    delta = clean(delta)
                    require(not delta or moment(delta,t).positive(),
                            'mask dominance control failed')
                    checks += 1
    for t in (F(1,10),F(1,2),F(999,1000)):
        require((power(6,t)-1-power(5,t)).negative(),'H1+H5 -> H6')
        delta = 2-3*power(2,t)+power(3,t)-power(4,t)+power(5,t)
        require(delta.negative(),'joint contact concavity')
        require((power(9,t)-power(8,t)-1).negative(),'completion must be charged')
    p,h = canonical(18,*prof)
    bad_p = dict(p); bad_p[1] -= 104*15
    require((bad_p,h) != canonical(18,*prof),'missing query not rejected')
    bad_h = dict(h); bad_h[9] += 1
    require((p,bad_h) != canonical(18,*prof),'fake helper not rejected')
    bad_idle = dict(p); bad_idle.pop(72)
    require((bad_idle,h) != canonical(18,*prof),'missing idle not rejected')
    try:
        gate(prof,F('0.00304153'),18)
    except ValueError:
        pass
    else:
        raise ValueError('positive raw witness falsely excluded')
    return {'tiny_mask_comparisons':checks,'arithmetic_identities':4,
            'concavity_controls':9,'accounting_controls':3,'false_ceiling_rejected':True}


def calculate():
    authenticate()
    profiles = load_profiles()
    brackets = {
        'round3_4610':('0.00302177587077','0.00302177587079',18),
        'neutral5413':('0.00302728824993','0.00302728824995',18),
        'p104_5544':('0.00304057807630','0.00304057807631',18),
        'p104_5545':('0.00304117181649','0.00304117181650',18),
        'p104_5551':('0.00304153116714','0.00304153116715',18),
        'neutral_free_eight_H8':('0.00807671283977','0.00807671283979',7),
    }
    result = {'schema':'kappa-architecture-frontier/v1','grid':str(Q),
              'claims_are_raw_moment_bounds':True,'native_or_outer_admission':False,
              'profiles':{},'discounts':{}}
    for name,(lo,hi,n) in brackets.items():
        prof = profiles[name]
        lower = cost(prof,n,F(lo))
        require(lower.negative(),'lower raw witness failed')
        result['profiles'][name] = {
            'ports':prof[0],'paid':prof[1],'helper_targets':prof[2],
            'root_bracket':[lo,hi],'lower_witness':lower.json(),
            'all_n_upper_gate':gate(prof,F(hi),n),
            'all_exponent_derivative_upper':derivative_gate(prof).json(),
            'rank_surplus_per_full':17*prof[0]+sum(r*w for r,w in prof[2].items())
                                        -sum(r*w for r,w in prof[1].items()),
        }
    for name in ('neutral5413','p104_5551'):
        result['discounts'][name] = [ratio_gate(profiles[name],F(c),n)
            for c,n in [('0.0031',18),('0.0033',17),('0.0034',16),
                        ('0.004',14),('0.006',9),('0.01',5)]]
    result['discounts']['neutral_free_eight_H8'] = [ratio_gate(
        profiles['neutral_free_eight_H8'],F('0.01'),5)]
    claim = json.loads((ROOT/'inputs/selected-claim.json').read_text())
    result['retained_admitted_BIT_budget'] = claim['admitted_BIT_saving']
    result['controls'] = controls(profiles)
    return result


def price_profile(path,C):
    """Optimistic raw filter for a new autonomous rank-eight path provider."""
    d = json.loads(path.read_text())
    require(type(d.get('ports')) is int and 1 <= d['ports'] <= 10**6,
            'ports must be an integer in 1..1000000')
    histograms = []
    for key in ('paid','helper_targets'):
        require(isinstance(d.get(key),dict),'paid/helper_targets dictionaries required')
        hist = {}
        for r,w in d[key].items():
            rank = int(r)
            require(str(rank) == r and 1 <= rank <= 65536,
                    'canonical integer ranks in 1..65536 required')
            require(type(w) is int and 0 <= w <= 10**9,'integer multiplicities required')
            if w:
                hist[rank] = w
        histograms.append(hist)
    require(0 < C < 1,'saving must lie strictly between zero and one')
    prof = (d['ports'],*histograms)
    def J(n):
        return n*cost(prof,n+1,C)-(n+1)*cost(prof,n,C)
    if J(1).positive():
        return {'C':str(C),'minimizing_full_count':1,
                'discount':cost(prof,1,C).json(),'next_ratio_numerator':J(1).json(),
                'scope':'Raw path invoice only; independent helper and main contracts assumed.'}
    require(J(1).negative(),'unresolved interval at initial ratio gate')
    lo,hi = 1,2
    while J(hi).negative() and hi < 4096:
        lo,hi = hi,2*hi
    require(J(hi).positive(),'unknown: ratio gate unresolved or beyond 4096 FULLs')
    while hi-lo > 1:
        mid = (lo+hi)//2
        if J(mid).negative():
            lo = mid
        else:
            require(J(mid).positive(),'unresolved interval during ratio search')
            hi = mid
    result = ratio_gate(prof,C,hi)
    result['scope'] = 'Raw path invoice only; independent helper and main contracts assumed.'
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',type=Path,help='write a new receipt without overwriting')
    parser.add_argument('--price',type=Path,help='JSON with ports, paid, helper_targets; assumes the path contract')
    parser.add_argument('--C',type=F,help='exact candidate supplier saving for --price')
    args = parser.parse_args()
    if args.price:
        require(args.C is not None and args.write is None,'--price requires --C and excludes --write')
        print(json.dumps(price_profile(args.price,args.C),sort_keys=True,indent=2))
        return
    require(args.C is None,'--C requires --price')
    result = calculate()
    encoded = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write:
        require(not args.write.exists(),'refusing to overwrite receipt')
        args.write.write_text(encoded)
    else:
        require(json.loads(encoded) == json.loads((ROOT/'RESULT.json').read_text()),
                'fresh scientific result differs')
    print('PASS_KAPPA_ARCHITECTURE_FRONTIER: six all-n ceilings, thirteen price gates, finite controls')


if __name__ == '__main__':
    main()
