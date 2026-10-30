"""Independent finite controls for the invoice edit selector."""
import copy
from fractions import Fraction as Q
from hashlib import sha256
import itertools
import json
from pathlib import Path
import random
import runpy
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'scripts/select_recursive_edits.py'
M=runpy.run_path(str(TOOL))

def invoice(paid=None,targets=None):
    return {'schema':'integer-mult-recursive-invoice/v1',
            'contract':{'model':'test','rank_semantics':'test','ambient_rank':100,'boundary':'test'},
            'paid':paid or {},'targets':targets or {}}

def plan(edits,capacities=None):
    return {'schema':'integer-mult-recursive-edit-plan/v1','capacities':capacities or {},'edits':edits}

def edit(name,bill,uses=None):return {'id':name,'invoice':bill,'uses':uses or {}}

class SelectionTests(unittest.TestCase):
    def test_joint_gain_beats_largest_single_edit(self):
        base=invoice({'100':1,'25':2})
        p=plan([edit('A',invoice({'9':1,'25':2}),{'helper':2}),
                edit('B',invoice({'100':1,'25':1,'1':1}),{'helper':1}),
                edit('C',invoice({'100':1,'25':1,'1':1}),{'helper':1})],{'helper':2})
        frozen=copy.deepcopy((base,p))
        r=M['select'](base,p,Q(1,2))
        self.assertTrue(r['certified_optimal'])
        self.assertEqual(r['best']['ids'],['B','C'])
        self.assertEqual(r['best']['new_minus_baseline'],{'lower':'-8','upper':'-8'})
        self.assertEqual(r['best']['invoice']['paid'],{'1':2,'100':1})
        self.assertEqual(r['feasible_subsets']+r['infeasible_subsets'],8)
        self.assertEqual((base,p),frozen)

    def test_independent_brute_force(self):
        rng=random.Random(1729)
        for case in range(25):
            base=invoice({'36':8}, {'100':1})
            edits=[];oracle=[]
            for i in range(8):
                count=rng.randrange(1,4);rank=rng.choice((1,4,9,16,25))
                use=rng.randrange(1,4)
                edits.append(edit(str(i),invoice({'36':8-count,str(rank):count},{'100':1}),{'h':use}))
                oracle.append((count,rank,use))
            p=plan(edits,{'h':7})
            values=[]
            for choices in itertools.product((0,1),repeat=8):
                if sum(c*n for c,(n,r,u) in zip(choices,oracle))>8:continue
                if sum(c*u for c,(n,r,u) in zip(choices,oracle))>7:continue
                values.append(sum(c*n*(int(r**0.5)-6) for c,(n,r,u) in zip(choices,oracle)))
            report=M['select'](base,p,Q(1,2))
            self.assertTrue(report['certified_optimal'],case)
            self.assertEqual(Q(report['global_optimum']['lower']),min(values))
            self.assertEqual(Q(report['global_optimum']['upper']),min(values))
            self.assertEqual(report['feasible_subsets'],len(values))

    def test_gross_inventory_cannot_reuse_additions(self):
        base=invoice({'4':1},{'9':1})
        p=plan([edit('add',invoice({'4':2},{'9':2})),
                edit('take1',invoice()),edit('take2',invoice())])
        r=M['select'](base,p,Q(1,2),report_limit=256)
        self.assertEqual(r['feasible_subsets'],6)
        self.assertEqual(r['infeasible_subsets'],2)
        self.assertFalse(any({'take1','take2'}<=set(x['ids']) for x in r['possible_optima']))

    def test_unresolved_precision_is_not_optimality(self):
        r=M['select'](invoice(),plan([edit('near',invoice({'2':1000000},{'1':1414214}))]),Q(1,2),16)
        self.assertFalse(r['certified_optimal'])
        self.assertEqual(r['possible_optima_count'],2)
        exact=M['select'](invoice(),plan([edit('near',invoice({'2':1000000},{'1':1414214}))]),Q(1,2),128)
        self.assertTrue(exact['certified_optimal'])
        self.assertEqual(exact['best']['ids'],['near'])

    def test_maximum_subset_count_and_exact_ties(self):
        p=plan([edit(str(i),invoice({'1':1})) for i in range(16)])
        r=M['select'](invoice(),p,Q(1,2),16)
        self.assertEqual(r['feasible_subsets'],65536)
        self.assertTrue(r['certified_optimal'])
        self.assertEqual(r['best']['ids'],[])
        tied=M['select'](invoice(),plan([edit('a',invoice({'2':1},{'2':1}))]),Q(1,3))
        self.assertTrue(tied['certified_optimal'])
        self.assertEqual(tied['possible_optima_count'],2)

    def test_invalid_inputs(self):
        good=plan([edit('a',invoice({'1':1}))])
        cases=[]
        p=copy.deepcopy(good);p['edits']*=2;cases.append(p)
        p=copy.deepcopy(good);p['edits'][0]['uses']={'missing':1};cases.append(p)
        p=copy.deepcopy(good);p['capacities']={'h':True};cases.append(p)
        p=copy.deepcopy(good);p['edits'][0]['invoice']['contract']['boundary']='other';cases.append(p)
        p=plan([edit('a',invoice({'1':10**60})),edit('b',invoice({'1':1}))]);cases.append(p)
        for p in cases:
            with self.assertRaises(ValueError):M['select'](invoice(),p,Q(1,2))
        for exponent,bits,limit in ((Q(0),128,16),(Q(1,2),15,16),(Q(1,2),128,0)):
            with self.assertRaises(ValueError):M['select'](invoice(),good,exponent,bits,limit)

    def test_isolated_optimized_cli_receipts_and_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            a=Path(directory)/'base.json';b=Path(directory)/'plan.json'
            a.write_text(json.dumps(invoice({'4':1})))
            b.write_text(json.dumps(plan([edit('save',invoice({'1':1}))])))
            command=[sys.executable,'-I','-O',str(TOOL),str(a),str(b),'--exponent','1/2']
            run=subprocess.run(command,capture_output=True,text=True,cwd=directory)
            self.assertEqual(run.returncode,0,run.stderr)
            report=json.loads(run.stdout)
            for name,path in (('baseline',a),('plan',b)):
                self.assertEqual(report['inputs'][name]['sha256'],sha256(path.read_bytes()).hexdigest())
            b.write_text('{"schema":1,"schema":2}')
            run=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(run.returncode,2);self.assertEqual(run.stdout,'')

if __name__=='__main__':unittest.main()
