#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Small exact two-point tests; no native operator or source admission.

Clear1nsight, substantial OpenAI assistance.
"""
from fractions import Fraction as Q
from pathlib import Path
import types
import unittest

HERE=Path(__file__).resolve().parent

def module(name,filename):
    m=types.ModuleType(name); m.__file__=str(HERE/filename)
    exec(compile((HERE/filename).read_bytes(),m.__file__,'exec'),m.__dict__)
    return m

t=module('small_tangent','test_tangent.py')
s=module('small_secant','secant.py')


def sub(a,b): return [[x-y for x,y in zip(r,q)] for r,q in zip(a,b)]

def chain(gates,n):
    out=t.ident(n)
    for gate in gates: out=t.mm(gate,out)
    return out


class Tests(unittest.TestCase):
    def test_two_point_telescoping_noncommuting_words(self):
        cases=0
        for n in range(2,6):
            for count in range(1,2*n+1):
                plus=[]; minus=[]; tariff=0
                for j in range(count):
                    shear=t.ident(n); shear[j%n][(j+1)%n]=Q(j+1,j+2)
                    plus.append(shear); minus.append(shear)
                    gate=t.ident(n); gate[j%n][j%n]=-1
                    plus.append(t.ident(n)); minus.append(gate); tariff+=1
                difference=sub(chain(minus,n),chain(plus,n))
                reconstructed=[[Q(0)]*n for _ in range(n)]
                for j in range(len(plus)):
                    term=t.mm(chain(minus[j+1:],n),t.mm(sub(minus[j],plus[j]),chain(plus[:j],n)))
                    reconstructed=t.plus(reconstructed,term)
                self.assertEqual(difference,reconstructed)
                self.assertLessEqual(t.rk(difference),tariff)
                cases+=1
        self.assertEqual(cases,28)

    def test_tight_uniform_sign_query_bound(self):
        for n in range(2,7):
            gates=[]
            for i in range(n):
                gate=t.ident(n); gate[i][i]=-1; gates.append(gate)
            self.assertEqual(chain(gates,n),[[-x for x in row] for row in t.ident(n)])
            self.assertEqual(t.rk(sub(chain(gates,n),t.ident(n))),n)

    def test_fixed_fourth_power_has_zero_secant(self):
        for n in range(2,6):
            sign=[[-x for x in r] for r in t.ident(n)]
            self.assertEqual(chain([sign]*4,n),t.ident(n))
            self.assertEqual(t.rk(sub(chain([sign]*4,n),t.ident(n))),0)

    def test_causal_resolvent_on_reordered_sites(self):
        K=[{2:Q(2)},{0:Q(3),2:Q(1)},{}]; order=[2,0,1]
        for delta in (Q(-2),Q(1),Q(3,2)):
            columns=[]
            for j in range(3):
                rhs=[Q(int(i==j)) for i in range(3)]
                e=s.solve(K,order,rhs,delta)
                self.assertEqual([e[i]-delta*sum((q*e[k] for k,q in K[i].items()),Q(0))
                                  for i in range(3)], [delta*x for x in rhs])
                columns.append(e)
            self.assertEqual(t.rk(list(map(list,zip(*columns)))),3)
        with self.assertRaises(ValueError): s.triangular(K,[0,1,2])
        with self.assertRaises(ValueError): s.triangular(K,[2,0,0])

    def test_weaker_output_reduces_secant_rank(self):
        full=[[Q(-2)*x for x in row] for row in t.ident(4)]
        self.assertEqual(t.rk(full),4)
        self.assertEqual(t.rk(full[:2]),2)


if __name__=='__main__': unittest.main()
