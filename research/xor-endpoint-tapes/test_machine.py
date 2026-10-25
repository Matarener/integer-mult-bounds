"""Endpoint composition, finite-machine failure and export controls.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import shutil
import subprocess
import sys
import unittest

from machine import SEP,compile_machine,compile_inplace,decode,encode,exact_cost,need,run
from verify import check_table,execute

ROOT=Path(__file__).resolve().parent


def raw_phase(values,q):
    # Numerators of ((1+i)I+(1-i)X_q)/2, with the denominator charged separately.
    return [(values[j][0]-values[j][1]+values[j^q][0]+values[j^q][1],
             values[j][0]+values[j][1]+values[j^q][1]-values[j^q][0])
            for j in range(len(values))]


def bits(pair,width=6):
    return tuple(((component%(1 << width))>>k)&1
                 for component in pair for k in reversed(range(width)))


class Controls(unittest.TestCase):
    def test_domains(self):
        for args in [(-1,0),(3,8),(3,-1),(True,0),(2,True)]:
            with self.assertRaises(ValueError):compile_machine(*args)
        with self.assertRaises(ValueError):encode([(0,2)])

    def test_unit_moves_and_borrowed_source(self):
        machine=compile_machine(2,1)
        key=next(iter(machine.table));action=machine.table[key]
        machine.table[key]=(action[0],0,*action[2:])
        with self.assertRaisesRegex(ValueError,'borrowed input'):check_table(machine)
        machine.table[key]=(*action[:3],2,action[4])
        with self.assertRaisesRegex(ValueError,'unit physical'):check_table(machine)

    def test_wrong_mask_and_missing_restoration(self):
        records=[tuple((j>>k)&1 for k in range(3)) for j in range(8)]
        machine=compile_machine(3,2);source,end=encode(records)
        answer=run(machine,source,{})
        got,_=decode(answer['tapes'][1],8)
        with self.assertRaises(ValueError):need(got==[records[j^1] for j in range(8)],'wrong mask')
        # Halt at the first output-return macro, before restoring its head.
        machine.halt=2*machine.operations.index('L1')
        answer=run(machine,source,{})
        with self.assertRaises(ValueError):need(answer['heads']==(0,0),'head restoration')

    def test_missing_delimiter_and_budget(self):
        records=[(0,1),(1,0)]
        machine=compile_machine(1,1);source,end=encode(records)
        count,_=exact_cost(machine,records)
        with self.assertRaisesRegex(ValueError,'budget'):run(machine,source,{},limit=count-1)
        del source[end]
        with self.assertRaisesRegex(ValueError,'blocked'):run(machine,source,{},limit=count+10)

    def test_separate_complex_block_endpoints(self):
        # Three independent streams have shifts 3, 6, 5 with xor zero.
        # Their uncorrected product is not identity on the separate streams.
        before=[];uncorrected=[];after=[]
        for block,labels in enumerate([(1,2),(2,4),(1,4)]):
            values=[(j-4+block,2-j) for j in range(8)]
            numerators=values
            for q in labels+labels:numerators=raw_phase(numerators,q)
            denom=1 << (2*len(labels))
            need(all(a%denom==b%denom==0 for a,b in numerators),'exact block denominator')
            returned=[(a//denom,b//denom) for a,b in numerators]
            delta=labels[0]^labels[1]
            need(returned==[values[j^delta] for j in range(8)],'universal C_E squared identity')
            words=[bits(z) for z in returned]
            _,result,_=execute(3,delta,words)
            corrected,_=decode(result['tapes'][1],8,21)
            self.assertEqual(corrected,[bits(z) for z in values])
            before.append(values);uncorrected.append(returned);after.append(corrected)
        self.assertNotEqual(before,uncorrected)

    def test_involution_and_dirty_windows(self):
        records=[tuple((j+2*k)%2 for k in range(j%4)) for j in range(16)]
        _,first,_=execute(4,11,records,-20,40)
        intermediate,_=decode(first['tapes'][1],16,40)
        _,second,_=execute(4,11,intermediate,7,-100)
        final,_=decode(second['tapes'][1],16,-100)
        self.assertEqual(final,records)

    def test_dirty_scratch_swap_requires_third_pass(self):
        machine=compile_inplace(1,1)
        swaps=[i for i,op in enumerate(machine.operations) if op=='W']
        third=swaps[2]
        machine.halt=sum(3 if op=='W' else 2 for op in machine.operations[:third])
        data,_=encode([(1,0),(0,0)])
        scratch,_=encode([(1,1)])
        result=run(machine,data,scratch)
        with self.assertRaises(ValueError):need(result['tapes'][1]==scratch,'dirty scratch not restored')

    def test_export_cli_and_source_receipt_mutants(self):
        with TemporaryDirectory(prefix='xor-endpoint-') as temp:
            copy=Path(temp)/'package'
            shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('__pycache__'))
            command=[sys.executable,'-B',str(copy/'verify.py')]
            good=subprocess.run(command,cwd=temp,capture_output=True,text=True,timeout=60)
            self.assertEqual(good.returncode,0,good.stderr);self.assertIn('RECEIPT_MATCH',good.stdout)
            receipt=copy/'RESULT.json';original=receipt.read_bytes()
            receipt.write_text('{}',encoding='utf-8')
            bad=subprocess.run(command,cwd=temp,capture_output=True,text=True,timeout=60)
            self.assertNotEqual(bad.returncode,0);self.assertIn('receipt changed',bad.stderr)
            receipt.write_bytes(original)
            predecessor=copy/'inputs/PR3480-verify.py'
            predecessor.write_bytes(predecessor.read_bytes()+b'\n# mutation\n')
            bad=subprocess.run(command,cwd=temp,capture_output=True,text=True,timeout=60)
            self.assertNotEqual(bad.returncode,0);self.assertIn('source hash',bad.stderr)


if __name__=='__main__':unittest.main()
