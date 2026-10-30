"""Protect matched-target cancellation, side credits and explicit fees."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('substitution',ROOT/'scripts/substitute_recursive_invoice.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)


def bill(rank,paid=None,targets=None):
    return {'schema':'integer-mult-recursive-invoice/v1','contract':{'model':'fixture',
            'rank_semantics':'dimension','ambient_rank':rank,'boundary':'fixed'},
            'paid':paid or {},'targets':targets or {}}


class SubstitutionTests(unittest.TestCase):
    def test_literal_coproduct_accounting_and_fees(self):
        outer=bill(40,{'12':3,'20':1},{'40':1})
        inner=bill(4,{'1':3,'2':1},{'4':2,'1':1})
        fees=bill(40,{'1':7})
        new,steps=M.substitute(outer,inner,fees,[(12,2)])
        self.assertEqual(new['paid'],{'1':7,'3':6,'6':2,'12':1,'20':1})
        self.assertEqual(new['targets'],{'3':2,'12':2,'40':1})
        self.assertEqual(steps,[{'outer_rank':12,'copies':2,'rank_scale':3,'consumed_inner_target_rank':4}])

    def test_complete_moment_identity_in_144_small_models(self):
        def cost(x,t):return sum(int(r)**t*n for r,n in x['paid'].items())-sum(int(r)**t*n for r,n in x['targets'].items())
        for scale in range(1,5):
            for count in range(1,4):
                for paid in range(1,5):
                    for targets in range(1,4):
                        outer=bill(40,{str(4*scale):count+1},{'40':1})
                        inner=bill(4,{'1':paid,'3':1},{'4':targets,'2':2})
                        fees=bill(40,{'1':3})
                        new,_=M.substitute(outer,inner,fees,[(4*scale,count)])
                        for t in (0,1,2):self.assertEqual(cost(new,t),cost(outer,t)+count*scale**t*cost(inner,t)+cost(fees,t))

    def test_repeated_demand_is_aggregated_and_inputs_stay_unchanged(self):
        inputs=[bill(12,{'12':3}),bill(4,{'1':2},{'4':1}),bill(12)]
        saved=copy.deepcopy(inputs)
        a=M.substitute(*inputs,[(12,1),(12,2)])
        b=M.substitute(*inputs,[(12,3)])
        self.assertEqual(a,b);self.assertEqual(inputs,saved)
        with self.assertRaises(ValueError):M.substitute(*inputs,[(12,2),(12,2)])
        self.assertEqual(inputs,saved)

    def test_no_missing_target_fractional_scale_or_circular_children(self):
        outer=bill(20,{'12':2,'10':1});fees=bill(20)
        for inner,demand in [(bill(4,{'1':2}),[(12,1)]),
                             (bill(4,{'4':1},{'4':1}),[(12,1)]),
                             (bill(4,{'1':2},{'4':1}),[(10,1)])]:
            with self.assertRaises(ValueError):M.substitute(outer,inner,fees,demand)

    def test_contracts_fees_counts_and_overflow_reject(self):
        outer=bill(8,{'8':2});inner=bill(4,{'1':2},{'4':1});fees=bill(8)
        for demand in ([],[(8,True)],[(True,1)],[(8,3)],[(8,1)]*129):
            with self.assertRaises(ValueError):M.substitute(outer,inner,fees,demand)
        bad=copy.deepcopy(inner);bad['contract']['boundary']='other'
        with self.assertRaises(ValueError):M.substitute(outer,bad,fees,[(8,1)])
        with self.assertRaises(ValueError):M.substitute(outer,inner,bill(8,targets={'1':1}),[(8,1)])
        huge=bill(4,{'1':10**60},{'4':1})
        with self.assertRaises(ValueError):M.substitute(outer,huge,fees,[(8,2)])

    def test_cli_receipt_and_late_failure_do_not_emit_partial_invoice(self):
        with tempfile.TemporaryDirectory() as d:
            paths=[]
            for name,x in zip(('outer','inner','fees'),(bill(12,{'12':2}),bill(4,{'1':2},{'4':1}),bill(12,{'1':1}))):
                p=Path(d)/(name+'.json');p.write_text(json.dumps(x));paths.append(str(p))
            command=[sys.executable,'-I','-O','-B',str(ROOT/'scripts/substitute_recursive_invoice.py'),*paths]
            p=subprocess.run(command+['--replace','1','12'],capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr)
            r=json.loads(p.stderr);self.assertEqual(r['output_sha256'],hashlib.sha256(p.stdout).hexdigest())
            for name,path in zip(('outer','inner','fees'),paths):self.assertEqual(r['inputs'][name]['sha256'],hashlib.sha256(Path(path).read_bytes()).hexdigest())
            p=subprocess.run(command+['--replace','1','12','--replace','1','8'],capture_output=True)
            self.assertEqual(p.returncode,2);self.assertEqual(p.stdout,b'')


if __name__=='__main__':unittest.main()
