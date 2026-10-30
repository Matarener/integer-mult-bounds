#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Small exact controls for the parametric rank theorem and its limits.

Clear1nsight, substantial OpenAI assistance; not a native supplier proof.
"""
from fractions import Fraction as Q
from pathlib import Path
import types
import unittest

HERE=Path(__file__).resolve().parent
m=types.ModuleType('source_tangent')
m.__file__=str(HERE/'verify.py')
exec(compile((HERE/'verify.py').read_bytes(),m.__file__,'exec'),m.__dict__)


def ident(n):
    return [[Q(int(i==j)) for j in range(n)] for i in range(n)]


def mm(a,b):
    return [[sum((x*y for x,y in zip(row,col)),Q(0)) for col in zip(*b)] for row in a]


def plus(a,b):
    return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]


def rk(a):
    a=[list(map(Q,r)) for r in a]; k=0
    for j in range(len(a[0])):
        hit=next((i for i in range(k,len(a)) if a[i][j]),None)
        if hit is None: continue
        a[k],a[hit]=a[hit],a[k]; d=a[k][j]; a[k]=[x/d for x in a[k]]
        for i in range(k+1,len(a)):
            d=a[i][j]; a[i]=[x-d*y for x,y in zip(a[i],a[k])]
        k+=1
        if k==len(a): break
    return k


def product_dual(gates):
    n=len(gates[0][0]); base=ident(n); tangent=[[Q(0)]*n for _ in range(n)]
    for g,dg in gates:
        tangent=plus(mm(dg,base),mm(g,tangent))
        base=mm(g,base)
    return base,tangent


class Tests(unittest.TestCase):
    def test_causal_product_rule_and_rank(self):
        for n in range(2,7):
            zero=[[Q(0)]*n for _ in range(n)]
            for count in range(1,2*n+1):
                gates=[]; total=0
                for j in range(count):
                    free=ident(n); free[j%n][(j+1)%n]=Q((-1)**j,j+1)
                    derivative=[[Q(0)]*n for _ in range(n)]
                    derivative[j%n][j%n]=Q((-1)**j)
                    gates.extend([(free,zero),(ident(n),derivative)])
                    total+=rk(derivative)
                _,d=product_dual(gates)
                self.assertLessEqual(rk(d),total)

    def test_exact_full_rank_tight_example(self):
        n=5; gates=[]
        for i in range(n):
            d=[[Q(0)]*n for _ in range(n)]; d[i][i]=1
            gates.append((ident(n),d))
        _,derivative=product_dual(gates)
        self.assertEqual(derivative,ident(n)); self.assertEqual(rk(derivative),5)

    def test_singular_clear_cannot_increase_rank(self):
        n=3; zero=[[Q(0)]*n for _ in range(n)]; d=ident(n); d[1][1]=d[2][2]=0
        clear=ident(n); clear[0]=[Q(0)]*n
        _,before=product_dual([(ident(n),d)])
        _,after=product_dual([(ident(n),d),(clear,zero)])
        self.assertEqual(rk(before),1); self.assertEqual(rk(after),0)

    def test_fixed_operator_escape(self):
        # Four queries per coordinate give z^4 I. At z^4=1 the same fixed
        # response is I with zero queries, despite derivative 4I at z=1.
        n=3; gates=[]
        for i in range(n):
            for _ in range(4):
                d=[[Q(0)]*n for _ in range(n)]; d[i][i]=1
                gates.append((ident(n),d))
        base,d=product_dual(gates)
        self.assertEqual(base,ident(n)); self.assertEqual(d,[[4*x for x in r] for r in ident(n)])
        self.assertEqual(rk(d),n)
        self.assertEqual((1j)**4,1)
        self.assertEqual((-1j)**4,1)

    def test_free_parameter_dependence_breaks_premise(self):
        n=4
        # Calling a zI operation 'free' gives rank n with zero charged calls.
        self.assertEqual(rk(ident(n)),4)
        self.assertGreater(rk(ident(n)),0)

    def test_coordinate_change_preserves_rank(self):
        b=[[Q(1),Q(0)],[Q(0),Q(1)],[Q(1),Q(1)]]
        c=[[Q(1),Q(0),Q(3)],[Q(0),Q(1),Q(2)]]
        a=[[Q(1),Q(2)],[Q(0),Q(1)]]; inv=[[Q(1),Q(-2)],[Q(0),Q(1)]]
        self.assertEqual(mm(mm(b,a),mm(inv,c)),mm(b,c))
        self.assertEqual(rk(mm(b,c)),2)

    def test_missing_history_or_output_invalidates_full_rank(self):
        b=ident(4); c=ident(4)
        self.assertEqual(rk(mm(b,c)),4)
        b[3]=[Q(0)]*4
        self.assertEqual(rk(mm(b,c)),3)

    def test_source_and_typed_result_guards(self):
        self.assertNotEqual(m.canon({'rank':1}),m.canon({'rank':True}))
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'regular selected archive'): m.load(Path(tmp))
            path=Path(tmp)/m.ARCHIVE; path.parent.mkdir(parents=True); path.write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'selected archive hash'): m.load(Path(tmp))


if __name__=='__main__': unittest.main()
