"""Compare graph-cut optimization with complete binary enumeration."""
import copy
import itertools
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import optimize_binary_costs as tool


def problem(n, pairs=None):
    return {'schema': 'submodular-binary-costs/v1', 'unary': [[0, 0] for _ in range(n)],
            'pairs': pairs or [], 'fixed': [None]*n}


def oracle(v):
    return min(tool.energy(v, bits) for bits in itertools.product((0,1), repeat=len(v['unary']))
               if all(x is None or bits[i] == x for i,x in enumerate(v['fixed'])))


class BinaryCostTests(unittest.TestCase):
    def test_all_small_pair_tables(self):
        for table in itertools.product(range(3), repeat=4):
            v = problem(2, [{'i': 0, 'j': 1, 'costs': list(table)}])
            if table[0]+table[3] > table[1]+table[2]:
                with self.assertRaises(ValueError): tool.optimize(v)
            else:
                self.assertEqual(tool.optimize(v)['energy'], min(table))
                n, edges, constant = tool.compile_costs(v)
                for bits in itertools.product((0,1), repeat=2):
                    side = {n} | {i for i,x in enumerate(bits) if not x}
                    cut = sum(c for a,b,c in edges if a in side and b not in side)
                    self.assertEqual(constant+cut, table[2*bits[0]+bits[1]])

    def test_signed_random_graphs_with_fixed_choices(self):
        rng = random.Random(913)
        for _ in range(100):
            v = problem(6); v['unary'] = [[rng.randrange(-8,9),rng.randrange(-8,9)] for _ in range(6)]
            v['fixed'] = [rng.choice([None,None,0,1]) for _ in range(6)]
            for _ in range(14):
                i,j = rng.sample(range(6),2); a,b,c = [rng.randrange(-10,11) for _ in range(3)]
                v['pairs'].append({'i':i,'j':j,'costs':[a,b,c,b+c-a-rng.randrange(8)]})
            r = tool.optimize(v); self.assertEqual(r['energy'], oracle(v)); self.assertTrue(tool.verify(v,r))

    def test_corruption_controls(self):
        v = problem(2,[{'i':0,'j':1,'costs':[0,8,0,0]}]); v['unary'] = [[0,5],[5,0]]
        good = tool.optimize(v)
        for kind in ('flow','assignment','constant','energy','cut'):
            bad = copy.deepcopy(good)
            if kind == 'flow': bad['flow'][0] += 20
            if kind == 'assignment': bad['assignment'][0] ^= 1
            if kind == 'constant': bad['constant'] += 1
            if kind == 'energy': bad['energy'] -= 1
            if kind == 'cut': bad['source_side'].append(3)
            with self.assertRaises(ValueError): tool.verify(v,bad)

    def test_long_flow_path_and_limits(self):
        v = problem(512,[{'i':i,'j':i+1,'costs':[0,1,0,0]} for i in range(511)])
        v['fixed'][0]=0; v['fixed'][-1]=1
        r = tool.optimize(v); self.assertEqual(r['energy'],1); self.assertTrue(tool.verify(v,r))
        v['unary'].append([0,0]); v['fixed'].append(None)
        with self.assertRaises(ValueError): tool.optimize(v)
        v = problem(1);v['unary']=[[True,0]]
        with self.assertRaises(ValueError): tool.optimize(v)

    def test_all_pair_slots_and_fixed_penalty(self):
        v = problem(2,[{'i':0,'j':1,'costs':[0,1,0,0]} for _ in range(8192)])
        v['fixed']=[0,1]; r=tool.optimize(v);self.assertEqual(r['energy'],8192)
        v['pairs'].append(v['pairs'][0])
        with self.assertRaises(ValueError):tool.optimize(v)

    def test_portable_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,c=Path(tmp)/'problem.json',Path(tmp)/'certificate.json';p.write_text(json.dumps(problem(3)))
            cmd=[sys.executable,'-O','-B',str(ROOT/'scripts/optimize_binary_costs.py'),str(p)]
            out=subprocess.run(cmd,cwd=tmp,capture_output=True,text=True);self.assertEqual(out.returncode,0,out.stderr)
            c.write_text(out.stdout);self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,0)
            p.write_text(p.read_text()+'\n');self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,2)


if __name__ == '__main__':unittest.main()
