"""Semantic failure controls, export CLI and source/receipt tamper controls.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from dataclasses import replace
from fractions import Fraction as F
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
import sys
import unittest

from expansion import cap,line,prepare,prepare_row,tensor,window

ROOT=Path(__file__).resolve().parent


class Controls(unittest.TestCase):
    def test_parameters(self):
        for args in [(2,4,0,40),(2,0,1,40),(2,4,True,40),(2,4,1,0)]:
            with self.assertRaises(ValueError): prepare(*args)
        prepare(2,4,1,48)
        with self.assertRaises(ValueError): prepare(2,4,True,48)
        for q in range(1,8):
            with self.assertRaises(ValueError): prepare(2,4,1,q)
        with self.assertRaises(ValueError): prepare_row(2,4,4,1,40)
        with self.assertRaises(ValueError): tensor([],(),20,60)
        with self.assertRaises(ValueError): tensor([(0,0)],((2,4,1),),20,60)

    def test_domain(self):
        rows=prepare(2,4,1,48)
        with self.assertRaises(ValueError): line([(17,0),(0,0)],rows,4)
        with self.assertRaises(ValueError): line([(True,0),(0,0)],rows,4)
        with self.assertRaises(ValueError): line([(0,0)],rows,4)

    def test_coefficient_and_model_tampering(self):
        row=prepare(3,4,2,56)[0]
        for bad in [replace(row,weights=tuple(2*w for w in row.weights)),
                    replace(row,weights=(row.weights[0]+1,*row.weights[1:])),
                    replace(row,deficit=F(0)),replace(row,index=1)]:
            with self.assertRaises(ValueError): line([(16,0)]*3,(bad,),4)

    def test_nearest_grid_is_not_hard_contraction(self):
        # A small-grid semantic control, not a production-precision claim.
        row=prepare(1,2,1,80)[0]
        self.assertGreater(row.mass,F(1,2))
        raw=F(row.weights[0],1 << row.bits)  # p=1 input (1+i)/2: output numerator = mass.
        nearest=(int(raw+F(1,2)),int(raw+F(1,2)))
        self.assertGreater(F(sum(c*c for c in nearest),4),F(3,5)**2)
        safe=line([(1,1)],(row,),1)[0]
        self.assertLessEqual(F(sum(c*c for c in safe),4),cap(1)**2)

    def test_frame_ownership(self):
        rows=prepare(2,4,1,48)
        data={0:(16,0),1:(0,-16),20:'dirty'}
        for src,dst in [((0,0),(4,5,6,7)),((0,1),(4,5,6,6)),((0,1),(1,5,6,7)),((0,1),(4,5,6))]:
            with self.assertRaises(ValueError): window(data,src,dst,rows,4)
        out=window(data,(0,1),(4,5,6,7),rows,4)
        self.assertEqual({k:out[k] for k in data},data)

    def test_missing_periodic_windings(self):
        # With s=1, all unwrapped terms belong to one residue. Keeping only
        # the j=0 term loses substantial positive mass at u=4.
        row=prepare(1,2,4,80)[0]
        single_term=F(1,4)
        self.assertGreater(row.mass-single_term,F(1,5))
        self.assertLess(row.deficit,F(1,1 << 60))

    def test_git_free_cli_and_corruptions(self):
        with TemporaryDirectory(prefix='gaussian-headroom-') as temp:
            copy=Path(temp)/'package'
            shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('__pycache__'))
            command=[sys.executable,'-B',str(copy/'verify.py')]
            passed=subprocess.run(command,cwd=temp,capture_output=True,text=True,timeout=60)
            self.assertEqual(passed.returncode,0,passed.stderr)
            self.assertIn('RECEIPT_MATCH',passed.stdout)
            receipt=copy/'RESULT.json';original=receipt.read_bytes()
            receipt.write_text('{}',encoding='utf-8')
            broken=subprocess.run(command,cwd=temp,capture_output=True,text=True,timeout=60)
            self.assertNotEqual(broken.returncode,0)
            self.assertIn('receipt changed',broken.stderr)
            receipt.write_bytes(original)
            vendor=copy/'vendor/intervals.py'
            vendor.write_bytes(vendor.read_bytes()+b'\n# tamper\n')
            broken=subprocess.run(command,cwd=temp,capture_output=True,text=True,timeout=60)
            self.assertNotEqual(broken.returncode,0)
            self.assertIn('source hash',broken.stderr)


if __name__=='__main__':
    unittest.main()
