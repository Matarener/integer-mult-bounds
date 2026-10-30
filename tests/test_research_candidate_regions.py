"""Independent extrema and known-root tests for candidate power regions."""
from fractions import Fraction as Q
from hashlib import sha256
import itertools
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'scripts/compare_invoice_candidates.py'
M=runpy.run_path(str(TOOL))

def invoice(poly):
    return {'schema':'integer-mult-recursive-invoice/v1',
            'contract':{'model':'test','rank_semantics':'rank','ambient_rank':10**9,'boundary':'same'},
            'paid':{str(2**i):c for i,c in enumerate(poly) if c>0},
            'targets':{str(2**i):-c for i,c in enumerate(poly) if c<0}}

def product(a,b):
    c=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c

class CandidateTests(unittest.TestCase):
    def check_cover(self,r):
        self.assertEqual(Q(r['cells'][0]['left']),1);self.assertEqual(Q(r['cells'][-1]['right']),r['base'])
        for a,b in zip(r['cells'],r['cells'][1:]):self.assertEqual(a['right'],b['left'])

    def test_three_exact_winner_regions(self):
        r=M['compare']([('zero',invoice([])),('left',invoice([-5,4])),('right',invoice([7,-4]))])
        self.check_cover(r);self.assertEqual(r['unresolved_cells'],0)
        for row in r['cells']:
            x=(Q(row['left'])+Q(row['right']))/2
            expected='left' if x<Q(5,4) else 'right' if x>Q(7,4) else 'zero'
            self.assertEqual(row['uniform_minimizers'],[expected])
        ties={Q(v['x']):set(v['minimizers']) for v in r['boundaries']}
        self.assertEqual(ties[Q(5,4)],{'zero','left'});self.assertEqual(ties[Q(7,4)],{'zero','right'})

    def test_tangency_is_counted_without_false_unique_claim(self):
        r=M['compare']([('zero',invoice([])),('touch',invoice([9,-12,4])),('same',invoice([]))])
        self.assertEqual(len(r['cells']),1)
        row=r['cells'][0];self.assertEqual(row['uniform_minimizers'],['zero','same'])
        self.assertEqual(row['comparisons']['zero'][0]['distinct_equalities'],1)

    def test_irrational_transition_keeps_an_unresolved_box(self):
        r=M['compare']([('zero',invoice([])),('curve',invoice([-2,0,1]))],255,12)
        # The primitive rank base is 2, even when rank 4 is the only nonunit rank.
        self.check_cover(r);self.assertEqual(r['base'],2);self.assertEqual(r['unresolved_cells'],1)
        box=next(c for c in r['cells'] if c['classification']=='unresolved')
        self.assertLess(Q(box['left'])**2,2);self.assertGreater(Q(box['right'])**2,2)
        self.assertEqual(Q(box['right'])-Q(box['left']),Q(1,4096))

    def test_all_125_quadratics_against_exact_extrema(self):
        for c,b,a in itertools.product(range(-2,3),repeat=3):
            r=M['compare']([('zero',invoice([])),('curve',invoice([c,b,a]))],31,4)
            self.check_cover(r)
            for cell in r['cells']:
                if cell['classification']!='certified':continue
                lo,hi=Q(cell['left']),Q(cell['right']);points=[lo,hi]
                if a and lo<Q(-b,2*a)<hi:points.append(Q(-b,2*a))
                values=[a*x*x+b*x+c for x in points]
                for winner in cell['uniform_minimizers']:
                    self.assertTrue(min(values)>=0 if winner=='zero' else max(values)<=0,(c,b,a,cell))

    def test_open_root_counts_at_endpoints_and_multiplicities(self):
        for left,middle,right in itertools.product(range(4),repeat=3):
            poly=[1]
            for count,factor in ((left,[-1,1]),(middle,[-3,2]),(right,[-2,1])):
                for _ in range(count):poly=product(poly,factor)
            tower=M['root_tower'](poly)
            self.assertEqual(M['roots'](tower,Q(1),Q(2)),(int(middle>0),middle%2))
            self.assertEqual(M['roots'](tower,Q(1),Q(3,2)),(0,0))
            self.assertEqual(M['roots'](tower,Q(3,2),Q(2)),(0,0))

    def test_limits_cancellation_and_eight_candidates(self):
        cases=[(str(i),invoice([i])) for i in range(8)]
        r=M['compare'](cases,1,0);self.assertEqual(r['cells'][0]['uniform_minimizers'],['0'])
        r=M['compare']([('a',invoice([])),('b',invoice([-3,2]))],1,0)
        self.assertEqual(r['unresolved_cells'],1)
        bad=invoice([]);bad['paid']={'3':1}
        with self.assertRaises(ValueError):M['compare']([('a',invoice([0,1])),('b',bad)])
        a,b=invoice([]),invoice([1]);a['paid']['3']=4;b['paid']['3']=4
        self.assertEqual(M['compare']([('a',a),('b',b)])['unresolved_cells'],0)
        for candidates in (cases+[('extra',invoice([]))],[('a',invoice([])),('a',invoice([]))]):
            with self.assertRaises(ValueError):M['compare'](candidates)

    def test_degree_29_and_large_coefficients(self):
        p=[-10**60]+[0]*28+[10**60]
        r=M['compare']([('zero',invoice([])),('high',invoice(p))],1,0)
        self.assertEqual(r['cells'][0]['uniform_minimizers'],['zero'])
        self.assertEqual(r['relative_polynomials']['high'],p)

    def test_isolated_optimized_cli_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/f'{i}.json' for i in range(2)]
            for path,v in zip(paths,(invoice([]),invoice([-3,2]))):path.write_text(json.dumps(v))
            command=[sys.executable,'-I','-O',str(TOOL),'--candidate','a',str(paths[0]),'--candidate','b',str(paths[1])]
            r=subprocess.run(command,capture_output=True,text=True,check=True,cwd=tmp);report=json.loads(r.stdout)
            for pin,path in zip(report['inputs'],paths):self.assertEqual(pin['sha256'],sha256(path.read_bytes()).hexdigest())
            paths[1].write_text('{}');r=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'')

if __name__=='__main__':unittest.main()
