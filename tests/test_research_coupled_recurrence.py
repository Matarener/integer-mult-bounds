"""Exact analytic classification, source fixture and rejection controls."""
import copy
from fractions import Fraction as Q
import itertools
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import certify_coupled_recurrence as tool


def problem(a,b=None):
    return {'schema':'coupled-recurrence/v1','matrix':[[str(x) for x in row] for row in a],
            'forcing':[str(x) for x in (b if b is not None else [1]*len(a))]}


class RecurrenceTests(unittest.TestCase):
    def test_complete_two_type_grid(self):
        for a,b,c,d in itertools.product((Q(0),Q(1,2),Q(1),Q(3,2)),repeat=4):
            v=problem([[a,b],[c,d]]);r=tool.certify(v)
            stable=a<1 and d<1 and (1-a)*(1-d)>b*c
            self.assertEqual(r['status'],'contracting' if stable else 'noncontracting')
            self.assertTrue(tool.verify(v,r))

    def test_source_barrier_and_joint_failure(self):
        v=json.loads((ROOT/'tests/fixtures/coupled-recurrence/barrier.json').read_text())
        r=tool.certify(v);self.assertEqual(r['total'],['49/156','10/39','83/234'])
        # The retained coupled update s=8,t=2 fails although each alone is safe.
        for pos,new in (((0,1),'9/4'),((1,0),'7/15')):
            one=copy.deepcopy(v);one['matrix'][pos[0]][pos[1]]=new
            self.assertEqual(tool.certify(one)['status'],'contracting')
        v['matrix'][0][1]='9/4';v['matrix'][1][0]='7/15'
        r=tool.certify(v);self.assertEqual(r['status'],'noncontracting')
        self.assertEqual(r['witness'],['9/4','1','0'])

    def test_singular_and_reducible_cases(self):
        for a in ([[0,1],[1,0]], [[0,0,0],[0,1,0],[0,0,0]], [[0,5],[0,0]]):
            v=problem(a,[0]*len(a));r=tool.certify(v);self.assertTrue(tool.verify(v,r))
        r=tool.certify(problem([[0,5],[0,0]]));self.assertEqual(r['total'],['6','1'])
        self.assertEqual(tool.certify(problem([[1]],[0]))['status'],'noncontracting')

    def test_near_boundary_and_full_size(self):
        v=problem([[Q(999999999999,10**12)]]);r=tool.certify(v)
        self.assertEqual(r['total'],['1000000000000'])
        a=[[Q(i+1==j,2) for j in range(64)] for i in range(64)]
        r=tool.certify(problem(a));self.assertTrue(tool.verify(problem(a),r))
        self.assertEqual(Q(r['total'][0]),2-Q(1,2**63))
        with self.assertRaises(ValueError):tool.certify(problem([[0]*65 for _ in range(65)]))

        with self.assertRaisesRegex(ValueError,'6000-bit'):
            tool.encode_rational(Q(1<<6001))

    def test_false_certificates_reject(self):
        v=problem([[0,'1/2'],['1/2',0]]);good=tool.certify(v)
        for kind in ('weights','ratio','total'):
            bad=copy.deepcopy(good)
            if kind=='ratio':bad['ratio']='0'
            else:bad[kind][0]='0'
            with self.assertRaises(ValueError):tool.verify(v,bad)
        bad={'schema':'coupled-recurrence-certificate/v1','status':'noncontracting','witness':['1','1']}
        with self.assertRaises(ValueError):tool.verify(v,bad)
        for a in ([[True]],[[-1]],[[0.5]]):
            with self.assertRaises(ValueError):tool.certify({'schema':'coupled-recurrence/v1','matrix':a,'forcing':[1]})

    def test_portable_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,c=Path(tmp)/'problem.json',Path(tmp)/'certificate.json';p.write_text(json.dumps(problem([[0,2],['1/4',0]])))
            cmd=[sys.executable,'-O','-B',str(ROOT/'scripts/certify_coupled_recurrence.py'),str(p)]
            out=subprocess.run(cmd,cwd=tmp,capture_output=True,text=True);self.assertEqual(out.returncode,0,out.stderr)
            c.write_text(out.stdout);self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,0)
            p.write_text(p.read_text()+'\n');self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,2)


if __name__=='__main__':unittest.main()
