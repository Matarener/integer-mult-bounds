"""Full operator, boundary, phase and small exhaustive metric controls."""
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import audit_scalar_gate_fusion as fusion


class ScalarGateFusion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=fusion.audit()

    def test_actual_region_and_boundaries(self):
        r=self.report['region']
        self.assertEqual(r['operation_ids'],[16579,16580])
        self.assertEqual(r['transition_rank'],3)
        self.assertEqual(r['input_frames'].count('U')+r['output_frames'].count('U'),3)
        self.assertEqual(r['input_frames'].count('V')+r['output_frames'].count('V'),3)
        self.assertEqual(len(fusion.basis(tuple(r['U'])+tuple(r['V']))),8)

    def test_literal_operator_and_dirty_restoration(self):
        operator=self.report['operator']
        self.assertEqual(operator['full_operator'],[
            [{'0':'1'},{'0':'1'},{}],
            [{},{'1':'1'},{'0':'1'}],
            [{},{},{'0':'1'}]])
        self.assertTrue(operator['every_input_and_inverse_checked_symbolically'])
        self.assertTrue(operator['copied_control_schedule_checked'])
        with self.assertRaisesRegex(ValueError,'independent reversible role'):
            fusion.inverse([('copy',3,2)])
        self.assertEqual(len(operator['rejected_controls']),4)
        self.assertTrue(self.report['small_complex_check']['complex_C_not_an_involution'])

    def test_gate_order_is_not_free(self):
        bad=fusion.compose([('shear',1,2,1),('frames',(0,1,0)),('shear',0,1,1)])
        self.assertNotEqual(bad[0][2],{})

    def test_all_lagrangians_in_small_symplectic_space(self):
        h=3;mask=(1<<h)-1
        def pairing(x,y):
            return (((x&mask)&(y>>h)).bit_count()+((y&mask)&(x>>h)).bit_count())%2
        spaces={()}
        for dimension in range(h):
            new=set()
            for K in spaces:
                for v in range(1,1<<(2*h)):
                    if all(pairing(v,u)==0 for u in K):
                        L=fusion.basis(K+(v,))
                        if len(L)==dimension+1:new.add(L)
            spaces=new
        self.assertEqual(len(spaces),135)
        U=tuple(1<<(h+i) for i in range(h))
        V=tuple((1<<i)|(1<<(h+i)) for i in range(h))
        charges=[]
        for K in spaces:
            A=len(fusion.basis(U+K))-h
            B=len(fusion.basis(V+K))-h
            self.assertGreaterEqual(A+B,3)
            charges.append(3*A+2*B)
        self.assertEqual(min(charges),6)

    def test_even_unproved_pooling_is_worse(self):
        cost=self.report['paid_comparison']
        self.assertEqual(cost['baseline_positive_children'],[3])
        self.assertEqual(cost['best_common_frame_positive_children'],[3,3])
        self.assertGreater(Q(cost['pooling_to_baseline_ratio_lower']),1)
        self.assertLessEqual(Q(cost['pooling_to_baseline_ratio_lower'])**40,Q(2)**37)
        self.assertGreaterEqual(Q(cost['pooling_to_baseline_ratio_upper'])**40,Q(2)**37)

    def test_receipt_and_published_control(self):
        saved=json.loads((ROOT/'docs/research/scalar-gate-fusion.json').read_text())
        self.assertEqual(saved,self.report)
        self.assertEqual(self.report['published_control']['strict_constraint_count'],47)


if __name__=='__main__':unittest.main()
