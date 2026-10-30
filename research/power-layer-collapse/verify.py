"""Exact rational-power corroboration of the all-p exchange proof. Apache-2.0."""
from fractions import Fraction as F
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(None)
def power_interval(r, p):
    require(r > 0 and p > 0, "power domain")
    a, b = p.numerator, p.denominator
    d = 1 << 64
    n = (r ** a) * (d ** b)
    lo, hi = 0, (r ** max(1, a)) * d + 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid ** b <= n:
            lo = mid
        else:
            hi = mid
    require(lo ** b <= n < (lo + 1) ** b, "root bracket")
    return F(lo, d), F(lo if lo ** b == n else lo + 1, d)


def invoice(m, selected):
    require(1 <= m <= 11, "m domain")
    selected = frozenset(selected)
    require(selected <= set(range(1, m + 1)), "subset domain")
    hist = {}
    for i in range(1, m + 1):
        for r in ((2*i-1, 2*i+1) if i in selected else (2*i, 2*i)):
            hist[r] = hist.get(r, 0) + 1
    require(sum(hist.values()) == 2*m, "paid count")
    require(sum(r*n for r,n in hist.items()) == 2*m*(m+1), "paid mass")
    hist[2*m*(m+1)] = -1
    return hist


def bounds(hist, p):
    lo = hi = F(0)
    for r, n in hist.items():
        a,b = power_interval(r,p)
        lo += n*(a if n>0 else b)
        hi += n*(b if n>0 else a)
    return lo,hi


def difference(left,right):
    return {r:left.get(r,0)-right.get(r,0) for r in left.keys()|right.keys()}


def reject(thunk):
    try:
        thunk()
    except ValueError:
        return
    raise ValueError("negative control accepted")


def strict_less(left,right,p):
    require(bounds(difference(left,right),p)[1] < 0, "strict dominance")


def main():
    source = HERE.parents[1] / 'research/concave-invoice-antichains/README.md'
    pins = json.loads((HERE/'SOURCES.json').read_text())
    pin = next(x for x in pins['files'] if x['path'].endswith('concave-invoice-antichains/README.md'))
    require(hashlib.sha256(source.read_bytes()).hexdigest()==pin['sha256'], 'source bytes')
    ps = sorted({F(a,b) for b in range(2,9) for a in range(1,b)})
    compared = 0
    for m in range(1,12):
        for k in range(m+1):
            best = invoice(m,range(1,k+1))
            for s in combinations(range(1,m+1),k):
                bill = invoice(m,s)
                if s != tuple(range(1,k+1)):
                    for p in ps:
                        strict_less(best,bill,p)
                        compared += 1
                for p in (0,1):
                    require(sum(n*(r**p) for r,n in best.items()) ==
                            sum(n*(r**p) for r,n in bill.items()), 'endpoint tie')
        for p in ps:
            for i in range(1,m):
                left={2*i-1:1,2*i+1:1,2*i:-2}
                j=i+1
                right={2*j-1:1,2*j+1:1,2*j:-2}
                strict_less(left,right,p)
    first,second=invoice(2,{1}),invoice(2,{2})
    diff=difference(first,second)
    require(sum(n*min(r,2) for r,n in diff.items())==-1,'hinge 2')
    require(sum(n*min(r,4) for r,n in diff.items())==1,'hinge 4')
    strict_less(second,first,F(3,2))
    reject(lambda: strict_less(first,second,F(3,2)))
    changed_target=dict(first)
    changed_target[12]=0
    reject(lambda: strict_less(changed_target,second,F(1,2)))
    extra_fee=dict(first)
    extra_fee[1]=extra_fee.get(1,0)+1
    reject(lambda: strict_less(extra_fee,second,F(1,2)))
    reject(lambda: invoice(0,()))
    reject(lambda: invoice(2,{3}))
    reject(lambda: strict_less(second,first,F(1,2)))
    require(len(list(combinations(range(1,11),5)))==252,'m10 layer')
    require(len(list(combinations(range(1,12),5)))==462,'m11 layer')
    print(json.dumps({'status':'PASS_POWER_LAYER_COLLAPSE','rational_powers':len(ps),
                      'strict_comparisons':compared,'m10_survivors':1,'m11_survivors':1,
                      'scope':'written all-p proof with finite exact corroboration; no new kappa'},sort_keys=True))


if __name__=='__main__':
    main()
