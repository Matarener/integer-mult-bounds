"""Finite basis enumeration, coordinate witnesses and rejection controls."""
import copy
from functools import reduce
import itertools
import json
from operator import xor
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import select_binary_query_basis as tool


def problem(vectors,costs,width):
    return {'schema':'binary-query-basis/v1','width':width,
            'vectors':[{'bits':format(v,'x'),'cost':c} for v,c in zip(vectors,costs)]}


def independent(vectors):
    return len({reduce(xor,(v for i,v in enumerate(vectors) if mask>>i&1),0)
                for mask in range(1<<len(vectors))})==1<<len(vectors)


class BinaryBasisTests(unittest.TestCase):
    def test_all_fano_plane_costs(self):
        vectors=list(range(1,8));bases=[b for b in itertools.combinations(range(7),3)
                                       if independent([vectors[i] for i in b])]
        self.assertEqual(len(bases),28)
        for costs in itertools.product(range(3),repeat=7):
            value=problem(vectors,costs,3);r=tool.select(value)
            self.assertEqual(r['cost'],min(sum(costs[i] for i in b) for b in bases))
            self.assertTrue(tool.verify(value,r))

    def test_zero_and_duplicate_queries(self):
        value=problem([0,3,3,1,2],[0,5,1,9,2],2);r=tool.select(value)
        self.assertEqual(r['selected'],[2,4]);self.assertEqual(r['cost'],3)
        self.assertEqual(r['representations'][0],'0')
        zero=tool.select(problem([0,0],[2,1],1));self.assertEqual(zero['selected'],[])
        self.assertTrue(tool.verify(problem([0,0],[2,1],1),zero))

    def test_nonoptimal_independent_basis_rejects(self):
        value=problem([1,1],[5,1],1)
        bad={'schema':'binary-query-basis-certificate/v1','selected':[0],'cost':5,
             'representations':['1','1'],'dual':['1']}
        with self.assertRaisesRegex(ValueError,'cheaper basis exchange'):tool.verify(value,bad)

    def test_certificate_corruption(self):
        value=problem([1,2,3],[1,2,4],2);good=tool.select(value)
        for kind in ('dual','coverage','expression','cost','index'):
            bad=copy.deepcopy(good)
            if kind=='dual':bad['dual'][0]='0'
            if kind=='coverage':bad['representations'].pop()
            if kind=='expression':bad['representations'][2]='0'
            if kind=='cost':bad['cost']+=1
            if kind=='index':bad['selected'][0]=True
            with self.assertRaises(ValueError):tool.verify(value,bad)

    def test_full_input_width_and_count(self):
        value=problem([1<<(i%256) for i in range(4096)],[i//256 for i in range(4096)],256)
        r=tool.select(value);self.assertEqual(r['cost'],0);self.assertEqual(len(r['selected']),256)
        for bad in (problem([1],[True],1),problem([2],[1],1),problem([0]*4097,[0]*4097,1)):
            with self.assertRaises(ValueError):tool.select(bad)
        value=problem([1],[1],1);value['vectors'][0]['bits']='01'
        with self.assertRaises(ValueError):tool.select(value)

    def test_portable_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,c=Path(tmp)/'problem.json',Path(tmp)/'certificate.json';p.write_text(json.dumps(problem([1,2,3],[5,2,1],2)))
            cmd=[sys.executable,'-O','-B',str(ROOT/'scripts/select_binary_query_basis.py'),str(p)]
            out=subprocess.run(cmd,cwd=tmp,capture_output=True,text=True);self.assertEqual(out.returncode,0,out.stderr)
            c.write_text(out.stdout);self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,0)
            p.write_text(p.read_text()+'\n');self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,2)


if __name__=='__main__':unittest.main()
