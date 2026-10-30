"""Check identity conservation independently of aggregate invoice equality."""
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
TOOL=ROOT/'scripts/assemble_recursive_inventory.py'
M=runpy.run_path(str(TOOL))
FIXTURE=ROOT/'tests/fixtures/invoice-ledger-selected5599'

def inventory(rows):
    return {'schema':'integer-mult-invoice-inventory/v1',
            'contract':{'model':'test','rank_semantics':'rank','ambient_rank':100,'boundary':'same'},
            'sources':{'word':sha256(b'source').hexdigest()} if rows else {},
            'items':[{'id':name,'source':'word','side':side,'rank':rank,'count':count} for name,side,rank,count in rows]}

def assignment(components):return {'schema':'integer-mult-invoice-assignment/v1','components':components}
def claim(name,count):return {'id':name,'count':count}

class AssemblyTests(unittest.TestCase):
    def test_all_splits_preserve_independent_totals(self):
        inv=inventory([('a','paid',4,3),('b','paid',4,2),('c','targets',9,4)])
        before=copy.deepcopy(inv)
        for splits in itertools.product(range(4),range(3),range(5)):
            groups={'A':[],'B':[]}
            for item,n in zip(inv['items'],splits):
                if n:groups['A'].append(claim(item['id'],n))
                if item['count']-n:groups['B'].append(claim(item['id'],item['count']-n))
            bill,receipt=M['assemble'](inv,assignment(groups))
            self.assertEqual(bill['paid'],{'4':5});self.assertEqual(bill['targets'],{'9':4})
            self.assertEqual(sum(c['paid'].get('4',0) for c in receipt['components'].values()),5)
        self.assertEqual(inv,before)

    def test_same_histogram_does_not_hide_duplicate_origin(self):
        inv=inventory([('target-a','targets',4,1),('target-b','targets',4,1)])
        # The aggregate target histogram is still {4:2}, but one identity is reused.
        plan=assignment({'A':[claim('target-a',1)],'B':[claim('target-a',1)]})
        with self.assertRaisesRegex(ValueError,'over-assigned'):M['assemble'](inv,plan)
        with self.assertRaisesRegex(ValueError,'unassigned'):M['assemble'](inv,assignment({'A':[claim('target-a',1)]}))

    def test_frozen_selected_receipt_components(self):
        inv=json.loads((FIXTURE/'inventory.json').read_text());plan=json.loads((FIXTURE/'assignment.json').read_text())
        result=json.loads((FIXTURE/'RESULT.json').read_text())
        pins=M['source_receipts'](inv,[('result',FIXTURE/'RESULT.json')])
        bill,receipt=M['assemble'](inv,plan)
        self.assertEqual(pins['result']['sha256'],'1d92e587915052110dfb3aca8890df5afdaf496164efa5a4a52e69ceeb3c70f3')
        for side in ('paid','targets'):self.assertEqual(bill[side],result['complete_cost'][side])
        self.assertEqual(receipt['covered_paid_count'],66726);self.assertEqual(receipt['covered_target_count'],13048)
        self.assertEqual(receipt['components']['query-paid']['paid'],{'1':1560})

    def test_source_mutation_missing_and_duplicate_bindings(self):
        inv=inventory([('a','paid',1,1)])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'word';p.write_bytes(b'source')
            self.assertEqual(M['source_receipts'](inv,[('word',p)])['word']['bytes'],6)
            for bindings in ([],[('wrong',p)],[('word',p),('word',p)]):
                with self.assertRaises(ValueError):M['source_receipts'](inv,bindings)
            p.write_bytes(b'sourcf')
            with self.assertRaisesRegex(ValueError,'hash differs'):M['source_receipts'](inv,[('word',p)])

    def test_shape_identity_and_count_controls(self):
        inv=inventory([('a','paid',1,1)]);plan=assignment({'A':[claim('a',1)]})
        for claims in ([claim('unknown',1)],[claim('a',True)],[claim('a',1),claim('a',1)]):
            with self.assertRaises(ValueError):M['assemble'](inv,assignment({'A':claims}))
        for updates in ({'side':'credit'},{'source':'missing'},{'rank':0},{'count':False}):
            bad=copy.deepcopy(inv);bad['items'][0].update(updates)
            with self.assertRaises(ValueError):M['assemble'](bad,plan)
        bad=copy.deepcopy(inv);bad['items']*=2
        with self.assertRaises(ValueError):M['assemble'](bad,plan)
        bad=inventory([('a','paid',1,10**60),('b','paid',1,1)])
        with self.assertRaises(ValueError):M['assemble'](bad,assignment({'A':[claim('a',10**60),claim('b',1)]}))

    def test_empty_inventory_and_component_limits(self):
        bill,receipt=M['assemble'](inventory([]),assignment({'zero':[]}))
        self.assertEqual(bill['paid'],{});self.assertEqual(receipt['covered_items'],0)
        with self.assertRaises(ValueError):M['assemble'](inventory([]),assignment({str(i):[] for i in range(129)}))

    def test_isolated_cli_output_and_receipt_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'word';source.write_bytes(b'source')
            paths=[Path(tmp)/n for n in ('inventory.json','assignment.json')]
            for p,v in zip(paths,(inventory([('a','paid',4,2),('b','targets',9,1)]),assignment({'caller':[claim('a',2),claim('b',1)]}))):p.write_text(json.dumps(v))
            command=[sys.executable,'-I','-O',str(TOOL),*map(str,paths),'--source','word',str(source)]
            run=subprocess.run(command,capture_output=True,check=True,cwd=tmp)
            receipt=json.loads(run.stderr);bill=json.loads(run.stdout)
            self.assertEqual(bill['paid'],{'4':2});self.assertEqual(receipt['output']['sha256'],sha256(run.stdout).hexdigest())
            self.assertEqual(receipt['output']['bytes'],len(run.stdout))
            for key,p in zip(('inventory','assignment'),paths):self.assertEqual(receipt['inputs'][key]['sha256'],sha256(p.read_bytes()).hexdigest())
            source.write_bytes(b'changed');run=subprocess.run(command,capture_output=True)
            self.assertEqual(run.returncode,2);self.assertEqual(run.stdout,b'')

if __name__=='__main__':unittest.main()
