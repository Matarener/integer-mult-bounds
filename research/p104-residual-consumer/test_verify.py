#!/usr/bin/env python3
"""Semantic mutations, model separators, and actual isolated CLI failures."""
import copy
from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('consumer_under_test',HERE/'verify.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result,cls.ctx=v.calculate()
        cls.A,cls.B,cls.J,cls.N,cls.ops,cls.expected=cls.ctx
        cls.d=v.expanded_cleanup(cls.B,cls.J,cls.N)
        cls.s,cls.f=v.cut_state(cls.A,cls.d)
        cls.post,cls.pf=v.run(cls.s,cls.f,cls.ops)

    def check_bad(self,ops,match=None):
        if match:
            with self.assertRaisesRegex(ValueError,match):v.run(self.s,self.f,ops)
        else:
            s,f=v.run(self.s,self.f,ops)
            self.assertNotEqual(s,self.expected)

    def test_complete_positive(self):
        self.assertEqual(self.post,self.expected)
        self.assertEqual(self.pf,v.desired_frames(self.J))

    def test_missing_cleanup(self):
        self.check_bad(v.tail(self.B,self.J,self.N))

    def test_sign_error(self):
        x=list(self.ops);e=list(x[-1]);e[3]*=-1;x[-1]=tuple(e)
        self.check_bad(x)

    def test_double_cleanup(self):
        old=[('add',f'Q{k}',f'X{i}',int(c/abs(c))) for k,row in enumerate(self.d)
             for i,c in enumerate(row) if c for _ in range(abs(int(c)))]
        self.check_bad(old+self.ops)

    def test_raw_sources_after_exchange(self):
        old=[('add',f'Q{k}',f'X{i}',int(c/abs(c))) for k,row in enumerate(self.d)
             for i,c in enumerate(row) if c for _ in range(abs(int(c)))]
        self.check_bad(v.tail(self.B,self.J,self.N)+old,'ADD source frame')

    def test_dirty_helper_not_data_pivot(self):
        x=list(self.ops);e=list(x[-1]);e[2]='G0';x[-1]=tuple(e)
        self.check_bad(x)

    def test_cleanup_before_gather(self):
        self.check_bad(v.consumer(self.J)+v.tail(self.B,self.J,self.N))

    def test_missing_source_doubling(self):
        x=list(self.ops);i=next(i for i,e in enumerate(x) if e[0]=='scale' and e[2]=='2');del x[i]
        self.check_bad(x)

    def test_wrong_output_location(self):
        x=self.N[0]
        self.assertNotEqual(self.post[f'Y{x}'],{x:F(1),104+x:F(1)})

    def test_return_adapter_without_lift(self):
        x=v.return_adapter(self.B,self.J,self.N)[1:]
        with self.assertRaisesRegex(ValueError,'arithmetic target not FULL|ADD source frame'):
            v.run(self.post,self.pf,x)

    def test_return_adapter_without_descent(self):
        x=v.return_adapter(self.B,self.J,self.N)[:-1]
        _,f=v.run(self.post,self.pf,x)
        self.assertNotEqual(f[f'Y{self.N[-1]}'],'H'+str(self.N[-1]))

    def test_all_96_information_separators(self):
        for n in self.N:
            s={name:{} for name in v.NAMES};s[f'X{n}']={0:F(1)}
            r,_=v.run(s,self.pf,v.return_adapter(self.B,self.J,self.N))
            self.assertEqual(r[f'X{n}'],{0:F(1)})

    def test_free_coordinate_bank_does_not_fix_budget(self):
        for stages in (3,9,101):
            m=8*stages+1;w=104*(stages-1);gap=160*stages+104
            for banks in (0,1,1000):
                self.assertGreater(F((m*(w+banks)+gap),m*(w+banks)),1)
        self.assertEqual(9*2576+(72*832-9*2312)-73*832,1544)
        self.assertEqual(9*2768+(72*832-9*2312)-73*832,3272)

    def test_scope_does_not_rule_out_direct_source_shear(self):
        # Original v=y+A x is corrected directly, without starting at the new exit.
        # Its existence separates the adapter floor from a universal P104 floor.
        for i in range(104):
            r={104+i:F(1),**{j:a for j,a in enumerate(self.A[i]) if a}}
            for j in range(104):r=v.row_add(r,{j:F(1)},F(i==j)-self.A[i][j])
            self.assertEqual(r,{i:F(1),104+i:F(1)})

    def test_cli_and_corruption_controls(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'research'/'p104-residual-consumer'
            shutil.copytree(HERE,p,ignore=shutil.ignore_patterns('__pycache__'))
            def run(*args):
                return subprocess.run([sys.executable,'-I','-O','-B',str(p/'verify.py'),*args],
                                      capture_output=True,text=True,timeout=30)
            self.assertEqual(run('--algebra-only').returncode,0)
            q=p/'RESULT.json';raw=q.read_bytes();d=json.loads(raw);d['schema_version']=True
            q.write_text(json.dumps(d));r=run('--algebra-only')
            self.assertNotEqual(r.returncode,0);self.assertIn('typed frozen result mismatch',r.stderr)
            q.write_bytes(raw)
            g=p/'inputs'/'PR3882_geometry.json';rawg=g.read_bytes();g.write_bytes(rawg+b' ')
            r=run('--algebra-only');self.assertNotEqual(r.returncode,0);self.assertIn('source hash',r.stderr)
            g.write_bytes(rawg)
            r=run();self.assertNotEqual(r.returncode,0);self.assertIn('FileNotFoundError',r.stderr)
            self.assertNotIn('PASS_P104_RESIDUAL_CONSUMER_SOURCE_BOUND',r.stdout)

    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError,'duplicate JSON'):
            json.loads('{"x":1,"x":2}',object_pairs_hook=v.unique)

if __name__=='__main__':
    unittest.main(verbosity=2)
