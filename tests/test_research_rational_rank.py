"""Independent minor enumeration and complete-kernel rejection tests."""
import copy
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import certify_rational_rank as tool


def problem(a):return {'schema':'rational-rank-problem/v1','matrix':a}


def determinant(a):
    n=len(a);out=Q(0)
    for p in itertools.permutations(range(n)):
        term=Q((-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n)))
        for i,j in enumerate(p):term*=Q(a[i][j])
        out+=term
    return out


def oracle(a):
    m,n=len(a),len(a[0])
    for r in reversed(range(1,min(m,n)+1)):
        if any(determinant([[a[i][j] for j in js] for i in inds])
               for inds in itertools.combinations(range(m),r) for js in itertools.combinations(range(n),r)):return r
    return 0


class RankTests(unittest.TestCase):
    def test_all_binary_three_by_three_matrices(self):
        for values in itertools.product(range(2),repeat=9):
            a=[list(values[i:i+3]) for i in (0,3,6)];r=tool.certify(problem(a))
            self.assertEqual(r['rank'],oracle(a));self.assertTrue(tool.verify(problem(a),r))

    def test_rectangular_rational_oracles(self):
        rng=random.Random(607)
        for _ in range(60):
            a=[[str(Q(rng.randrange(-3,4),rng.randrange(1,5))) for _ in range(4)] for _ in range(3)]
            r=tool.certify(problem(a));self.assertEqual(r['rank'],oracle(a))
        r=tool.certify(problem([[1,0,1],[0,1,1],[1,1,2]]))
        self.assertEqual(r['right_kernel'],[['-1','-1','1']]);self.assertEqual(r['left_kernel'],[['-1','-1','1']])

    def test_each_certificate_component_is_checked(self):
        value=problem([[1,0,1],[0,1,1],[1,1,2]]);good=tool.certify(value)
        for key in ('minor_inverse','coefficients','right_kernel','left_kernel'):
            bad=copy.deepcopy(good);bad[key][0][0]=str(Q(bad[key][0][0])+1)
            with self.assertRaises(ValueError):tool.verify(value,bad)
        bad=copy.deepcopy(good);bad['right_kernel'][0]=['0','0','0']
        with self.assertRaises(ValueError):tool.verify(value,bad)
        bad=copy.deepcopy(good);bad['rows']=[0,0]
        with self.assertRaises(ValueError):tool.verify(value,bad)

    def test_zero_full_rank_and_limits(self):
        self.assertEqual(tool.certify(problem([[0,0,0],[0,0,0]]))['rank'],0)
        a=[[int(i==j) for j in range(64)] for i in range(64)]
        r=tool.certify(problem(a));self.assertEqual(r['rank'],64);self.assertEqual(r['left_kernel'],[])
        for a in ([],[[]],[[0]*65],[[True]],[[0.1]],[['1/1000000001']]):
            with self.assertRaises(ValueError):tool.certify(problem(a))

        with self.assertRaisesRegex(ValueError,'6000-bit'):
            tool.encode_rational(Q(1<<6001))

    def test_nonleading_pivot_minor(self):
        a=[[0,0,0,0],[0,0,2,1],[0,3,0,2],[0,6,4,6]]
        r=tool.certify(problem(a));self.assertEqual(r['rank'],2)
        self.assertEqual(r['rows'],[2,1]);self.assertEqual(r['columns'],[1,2])
        self.assertTrue(tool.verify(problem(a),r))

    def test_portable_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,c=Path(tmp)/'problem.json',Path(tmp)/'certificate.json';p.write_text(json.dumps(problem([[1,2],[2,4]])))
            cmd=[sys.executable,'-O','-B',str(ROOT/'scripts/certify_rational_rank.py'),str(p)]
            out=subprocess.run(cmd,cwd=tmp,capture_output=True,text=True);self.assertEqual(out.returncode,0,out.stderr)
            c.write_text(out.stdout);self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,0)
            p.write_text(p.read_text()+'\n');self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,2)


if __name__=='__main__':unittest.main()
