#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent dyadic interval evaluator for finite positive rank moments.

All runtime arithmetic is integer/Fraction; no floating point, Decimal, NumPy,
or imports from predecessor moment engines. The analytic enclosures and outward
rounding argument are proved in PROOF.md. This code is not formally verified.
Dugongue, with substantial OpenAI Codex assistance.
"""
from fractions import Fraction


def need(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(a, b):
    need(b > 0, 'positive denominator')
    return -((-a) // b)


class DyadicMoment:
    def __init__(self, profile, dimension, live, bits=512, log_terms=256, exp_terms=96):
        need(type(dimension) is int and dimension > 1, 'dimension')
        need(type(live) is int and live > 0, 'live count')
        need(type(bits) is int and bits >= 32, 'precision bits')
        need(type(log_terms) is int and log_terms > 0, 'log terms')
        need(type(exp_terms) is int and exp_terms > 0, 'exp terms')
        need(bool(profile), 'nonempty profile')
        need(all(type(r) is int and 0 < r < dimension and
                 type(n) is int and n > 0 for r,n in profile.items()), 'positive strict child ranks')
        self.profile = dict(profile)
        self.dimension, self.live = dimension, live
        self.scale = 1 << bits
        self.bits, self.log_terms, self.exp_terms = bits, log_terms, exp_terms
        self.logs = {r:self.log_ratio(dimension,r) for r in profile}

    def log_unit(self, num, den):
        """Enclose log(num/den) for 1 <= num/den <= 2."""
        need(0 < den <= num <= 2*den, 'log reduction')
        s = self.scale
        lo = s*(num-den)//(num+den)
        hi = ceil_div(s*(num-den), num+den)
        sqlo, sqhi = lo*lo//s, ceil_div(hi*hi,s)
        plo, phi = lo, hi
        total_lo = total_hi = 0
        for j in range(self.log_terms):
            total_lo += (2*plo)//(2*j+1)
            total_hi += ceil_div(2*phi,2*j+1)
            plo, phi = plo*sqlo//s, ceil_div(phi*sqhi,s)
        # phi / s bounds t^(2N+1); 2/(1-t^2) <= 9/4.
        total_hi += ceil_div(9*phi,4*(2*self.log_terms+1))
        return total_lo,total_hi

    def log_ratio(self,num,den):
        need(num >= den > 0, 'positive ratio >= 1')
        k = 0
        while num >= 2*den:
            den *= 2
            k += 1
        a,b = self.log_unit(num,den)
        c,d = self.log_unit(2,1)
        return a+k*c,b+k*d

    def exp_interval(self,lo,hi):
        """Enclose exp(x) whenever lo/S <= x <= hi/S <= 1/2."""
        s = self.scale
        need(0 <= lo <= hi <= s//2, 'exponential small-argument domain')
        tlo = thi = s
        alo = ahi = s
        for j in range(1,self.exp_terms+1):
            tlo = tlo*lo//(s*j)
            thi = ceil_div(thi*hi,s*j)
            alo += tlo
            ahi += thi
        # The first omitted term bounds subsequent ratios by <= 1/2.
        first = ceil_div(thi*hi,s*(self.exp_terms+1))
        return alo,ahi+2*first

    def weights(self,b):
        need(type(b) is Fraction and b >= 0, 'nonnegative exact rational endpoint')
        out = {}
        for r,(lo,hi) in self.logs.items():
            a = lo*b.numerator//b.denominator
            z = ceil_div(hi*b.numerator,b.denominator)
            out[r] = self.exp_interval(a,z)
        return out

    def moment(self,b):
        weights = self.weights(b)
        a = sum(n*r*weights[r][0] for r,n in self.profile.items())
        z = sum(n*r*weights[r][1] for r,n in self.profile.items())
        den = self.scale*self.dimension*self.live
        return Fraction(a,den),Fraction(z,den)

    def bracket(self,digits=60):
        need(type(digits) is int and 1 <= digits <= 100, 'requested grid')
        grid = 10**digits
        lo,hi = 0,grid//100
        need(self.moment(Fraction(lo,grid))[1] < 1,'lower bracket')
        need(self.moment(Fraction(hi,grid))[0] > 1,'upper bracket')
        evaluations = 2
        while hi-lo > 1:
            mid = (lo+hi)//2
            a,z = self.moment(Fraction(mid,grid))
            evaluations += 1
            if z < 1:lo = mid
            elif a > 1:hi = mid
            else:raise ValueError('precision insufficient at trial point')
        return Fraction(lo,grid),Fraction(hi,grid),evaluations


def certify(profile,dimension,live,digits=60):
    evaluator = DyadicMoment(profile,dimension,live)
    lo,hi,count = evaluator.bracket(digits)
    lower = evaluator.moment(lo)
    upper = evaluator.moment(hi)
    need(lower[1] < 1 < upper[0],'strict adjacent grid certificate')
    return {'lower':str(lo),'upper':str(hi),'digits':digits,'bits':evaluator.bits,
            'log_terms':evaluator.log_terms,'exp_terms':evaluator.exp_terms,
            'evaluations':count,'margin_lower':str(1-lower[1]),
            'margin_upper':str(upper[0]-1),
            'weights':{str(r):{'lower':str(a),'upper':str(b),'scale':str(evaluator.scale)}
                       for r,(a,b) in evaluator.weights(lo).items()}}


if __name__ == '__main__':
    import json
    profile={1:7989840,2:2349000,3:749088,4:330480,5:69120,8:25920,48:137952}
    print(json.dumps(certify(profile,73,896*360),indent=2))
