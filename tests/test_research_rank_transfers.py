"""Replay majorization plans against independent prefix and hinge tests."""
import copy
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
TOOL=ROOT/'scripts/plan_recursive_transfers.py'
M=runpy.run_path(str(TOOL))

def invoice(paid=(),targets=()):
    def hist(ranks):return {str(r):ranks.count(r) for r in ranks if r}
    return {'schema':'integer-mult-recursive-invoice/v1',
            'contract':{'model':'test','rank_semantics':'rank','ambient_rank':10,'boundary':'same'},
            'paid':hist(paid),'targets':hist(targets)}

class TransferTests(unittest.TestCase):
    def test_exhaustive_vectors(self):
        vectors=list(itertools.combinations_with_replacement(range(5),4))
        checked=0
        for u,v in itertools.product(vectors,repeat=2):
            if sum(u)!=sum(v):continue
            old,new=invoice(tuple(reversed(v))),invoice(tuple(reversed(u)))
            r=M['plan'](old,new)
            expected=all(sum(u[-k:])>=sum(v[-k:]) for k in range(1,5))
            self.assertEqual(r['supported'],expected,(u,v))
            if not expected:continue
            checked+=1;self.assertTrue(M['verify'](old,new,r['certificate']))
            for cap in range(1,5):
                self.assertLessEqual(sum(min(x,cap) for x in u),sum(min(x,cap) for x in v))
            target=M['plan'](invoice(targets=tuple(reversed(u))),invoice(targets=tuple(reversed(v))))
            self.assertTrue(target['supported'])
        self.assertGreater(checked,200)

    def test_padding_and_both_sides(self):
        old,new=invoice((4,4),(8,)),invoice((8,),(4,4))
        r=M['plan'](old,new)
        self.assertTrue(r['strict_for_strictly_concave_tariffs'])
        self.assertEqual(r['certificate']['paid'],[{'from':0,'to':1,'amount':4}])
        self.assertEqual(r['certificate']['targets'],[{'from':0,'to':1,'amount':4}])
        self.assertTrue(M['verify'](old,new,r['certificate']))
        self.assertFalse(M['plan'](old,old)['strict_for_strictly_concave_tariffs'])

    def test_scope_failures_are_not_global_barriers(self):
        r=M['plan'](invoice((4,4)),invoice((7,)))
        self.assertFalse(r['supported'])
        self.assertEqual(r['obstructions']['paid']['reason'],'unequal_rank_mass')
        r=M['plan'](invoice((7,1)),invoice((4,4)))
        self.assertEqual(r['obstructions']['paid']['margin'],-3)

    def test_replay_rejects_malformed_and_wrong_direction(self):
        old,new=invoice((4,4)),invoice((8,))
        good=M['plan'](old,new)['certificate']
        variants=[]
        for fields in ({'amount':5},{'amount':True},{'from':-1},{'to':0},{'from':1,'to':0}):
            c=copy.deepcopy(good);c['paid'][0].update(fields);variants.append(c)
        c=copy.deepcopy(good);c['paid']=[];variants.append(c)
        c=copy.deepcopy(good);c['extra']=1;variants.append(c)
        for c in variants:
            with self.assertRaises(ValueError):M['verify'](old,new,c)

    def test_slot_limit_before_expansion(self):
        a=invoice((1,));a['paid']['1']=10**60
        with self.assertRaisesRegex(ValueError,'2048'):M['plan'](a,a)
        a['paid']['1']=2048
        self.assertTrue(M['plan'](a,a)['supported'])

    def test_isolated_cli_generation_and_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths=[Path(tmp)/name for name in ('old.json','new.json','cert.json')]
            for p,x in zip(paths,(invoice((4,4)),invoice((8,)))):p.write_text(json.dumps(x))
            command=[sys.executable,'-I','-O',str(TOOL),str(paths[0]),str(paths[1])]
            r=subprocess.run(command,capture_output=True,text=True,check=True,cwd=tmp)
            result=json.loads(r.stdout);paths[2].write_text(json.dumps(result['certificate']))
            r=subprocess.run(command+['--verify',str(paths[2])],capture_output=True,text=True,check=True)
            report=json.loads(r.stdout);self.assertTrue(report['valid'])
            self.assertEqual(report['inputs']['certificate']['sha256'],sha256(paths[2].read_bytes()).hexdigest())
            paths[2].write_text('{}')
            r=subprocess.run(command+['--verify',str(paths[2])],capture_output=True,text=True)
            self.assertEqual(r.returncode,2);self.assertEqual(r.stdout,'')

if __name__=='__main__':unittest.main()
