#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact-series oracle and behavioral checks, including -O.

The oracle follows the classical atanh/Taylor identities also used by the
credited predecessor root.py; it sums exact Fractions and rounds only at the
logarithm boundary, unlike the dyadic evaluator's repeated interval rounding.
This is a second arithmetic implementation, not a new transcendental method.
Dugongue, with substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import types
import unittest

P=Path(__file__).resolve().parent
module=types.ModuleType('dyadic_source')
exec(compile((P/'dyadic_moment.py').read_bytes(),'dyadic_moment.py','exec'),module.__dict__)
D=module.DyadicMoment
PROFILE={1:7989840,2:2349000,3:749088,4:330480,5:69120,8:25920,48:137952}

@lru_cache(None)
def log_oracle(x):
    k=0
    while x>=2:x/=2;k+=1
    def unit(y):
        t=(y-1)/(y+1);power=t;total=Q(0)
        for j in range(128):
            total+=2*power/(2*j+1);power*=t*t
        return total,total+2*power/(257*(1-t*t))
    lo,hi=unit(x);a,b=unit(Q(2));lo+=k*a;hi+=k*b
    scale=10**100
    return Q((lo*scale).__floor__(),scale),Q((hi*scale).__ceil__(),scale)

def exp_oracle(x):
    if not 0<=x<=Q(1,2):raise ValueError('oracle exponential domain')
    term=total=Q(1)
    for j in range(1,65):term*=x/j;total+=term
    return total,total+term*x/65/(1-x/66)

def oracle_moment(b):
    low=high=Q(0)
    for r,n in PROFILE.items():
        a,z=log_oracle(Q(73,r));weight=Q(n*r,73*896*360)
        low+=weight*exp_oracle(b*a)[0]
        high+=weight*exp_oracle(b*z)[1]
    # Final directed decimal rounding keeps the public receipt compact.
    scale=10**90
    return Q((low*scale).__floor__(),scale),Q((high*scale).__ceil__(),scale)

class ArithmeticTests(unittest.TestCase):
    def test_exact_zero(self):
        e=D(PROFILE,73,896*360)
        self.assertEqual(e.log_unit(1,1),(0,0))
        self.assertEqual(e.exp_interval(0,0),(e.scale,e.scale))
        self.assertEqual(e.moment(Q(0)),(Q(65088,73*896),)*2)

    def test_rational_oracle_root(self):
        a=json.loads((P/'CLAIM.json').read_bytes());c=Q(a['complex_lower'])
        self.assertLess(oracle_moment(c)[1],1)
        self.assertGreater(oracle_moment(c+Q(1,10**80))[0],1)

    def test_independent_precision_replay(self):
        c=Q(json.loads((P/'CLAIM.json').read_bytes())['complex_lower'])
        for bits in (384,512,640):
            e=D(PROFILE,73,896*360,bits=bits)
            self.assertLess(e.moment(c)[1],1)
            self.assertGreater(e.moment(c+Q(1,10**80))[0],1)

    def test_log_intervals_against_series(self):
        e=D(PROFILE,73,896*360,bits=256)
        for numerator,denominator in ((1,1),(2,1),(3,2),(73,48),(73,1),(1024,1)):
            a,b=e.log_ratio(numerator,denominator);lo,hi=log_oracle(Q(numerator,denominator))
            self.assertLessEqual(Q(a,e.scale),hi)
            self.assertLessEqual(lo,Q(b,e.scale))

    def test_exp_half_boundary(self):
        e=D(PROFILE,73,896*360,bits=256)
        for x in (Q(0),Q(1,1000),Q(1,2)):
            a,b=e.exp_interval((x*e.scale).__floor__(),(x*e.scale).__ceil__())
            lo,hi=exp_oracle(x)
            self.assertLessEqual(Q(a,e.scale),hi)
            self.assertLessEqual(lo,Q(b,e.scale))

    def test_rank_mass_insufficient(self):
        # Preserve weighted rank mass, but concentrate it on rank 1.
        bad={1:65088*360};c=Q(json.loads((P/'CLAIM.json').read_bytes())['complex_lower'])
        self.assertEqual(sum(r*n for r,n in bad.items()),65088*360)
        self.assertGreater(D(bad,73,896*360).moment(c)[0],1)

    def test_domain_guards(self):
        for profile,m,w in (({0:1},73,1),({73:1},73,1),({1:-1},73,1),({},73,1),({1:1},73,0),({True:1},73,1)):
            with self.assertRaises(ValueError):D(profile,m,w)
        e=D(PROFILE,73,896*360)
        for lo,hi in ((-1,0),(2,1),(0,e.scale//2+1)):
            with self.assertRaises(ValueError):e.exp_interval(lo,hi)
        with self.assertRaises(ValueError):e.weights(0.001)
        with self.assertRaises(ValueError):e.weights(Q(-1))
        with self.assertRaises(ValueError):D(PROFILE,73,896*360,bits=32).bracket(60)

if __name__=='__main__':unittest.main(verbosity=2)
