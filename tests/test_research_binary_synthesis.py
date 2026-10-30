"""Truth-table shortest paths and full-group certificate checks."""
import copy
import heapq
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import synthesize_binary_linear as tool


def problem(n,target=None):
    return {'schema':'binary-linear-synthesis/v1','width':n,'target':target or [1<<i for i in range(n)],
            'gates':[{'op':'xor','src':i,'dst':j,'cost':1+(i>j)} for i in range(n) for j in range(n) if i!=j]}


def truth_oracle(v):
    start=tuple(range(1<<v['width']));dist={start:0};queue=[(0,start)]
    while queue:
        cost,state=heapq.heappop(queue)
        if dist[state]!=cost:continue
        for gate in v['gates']:
            a,b=gate['src'],gate['dst'];out=[]
            for x in state:
                regs=[(x>>i)&1 for i in range(v['width'])]
                if gate['op']=='xor':regs[b]=(regs[b]+regs[a])%2
                else:regs[a],regs[b]=regs[b],regs[a]
                out.append(sum(bit<<i for i,bit in enumerate(regs)))
            after=tuple(out);new=cost+gate['cost']
            if after not in dist or new<dist[after]:dist[after]=new;heapq.heappush(queue,(new,after))
    return dist


class SynthesisTests(unittest.TestCase):
    def test_every_three_role_endpoint_against_truth_tables(self):
        v=problem(3);dist=truth_oracle(v);self.assertEqual(len(dist),168)
        for truth,cost in dist.items():
            v['target']=[sum(((truth[1<<j]>>i)&1)<<j for j in range(3)) for i in range(3)]
            r=tool.synthesize(v);self.assertEqual(r['cost'],cost);self.assertTrue(tool.verify(v,r))

    def test_weighted_swap_and_restricted_unreachability(self):
        v=problem(2,[2,1]);v['gates'][1]['cost']=1
        v['gates'].append({'op':'swap','src':0,'dst':1,'cost':7})
        self.assertEqual(tool.synthesize(v)['cost'],3)
        v['gates']=v['gates'][:1];r=tool.synthesize(v)
        self.assertEqual(r['status'],'unreachable');self.assertEqual(len(r['potential']),2)
        self.assertTrue(tool.verify(v,r))

    def test_full_four_role_group(self):
        v=problem(4,[8,4,2,1])
        for gate in v['gates']:gate['cost']=1
        r=tool.synthesize(v);self.assertEqual(len(r['potential']),20160);self.assertEqual(r['cost'],6)
        self.assertTrue(tool.verify(v,r))

    def test_false_proofs_reject(self):
        v=problem(2,[2,1]);good=tool.synthesize(v)
        for kind in ('closure','potential','word','cost','status'):
            bad=copy.deepcopy(good)
            if kind=='closure':bad['potential'].pop(next(k for k in bad['potential'] if k!='9'))
            if kind=='potential':bad['potential']['9']=1
            if kind=='word':bad['word']=[]
            if kind=='cost':bad['cost']+=1
            if kind=='status':bad.update(status='unreachable',cost=None,word=[])
            with self.assertRaises(ValueError):tool.verify(v,bad)

    def test_singular_targets_empty_alphabet_and_invalid_gates(self):
        v=problem(2);v['target']=[1,1];self.assertEqual(tool.synthesize(v)['status'],'unreachable')
        v=problem(1);self.assertEqual(tool.synthesize(v)['cost'],0)
        v=problem(2);v['gates'][0]['dst']=0
        with self.assertRaises(ValueError):tool.synthesize(v)
        v=problem(2);v['gates'][0]['cost']=0
        with self.assertRaises(ValueError):tool.synthesize(v)
        with self.assertRaises(ValueError):tool.synthesize(problem(5))

    def test_portable_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            p,c=Path(tmp)/'problem.json',Path(tmp)/'certificate.json';p.write_text(json.dumps(problem(2,[2,1])))
            cmd=[sys.executable,'-O','-B',str(ROOT/'scripts/synthesize_binary_linear.py'),str(p)]
            out=subprocess.run(cmd,cwd=tmp,capture_output=True,text=True);self.assertEqual(out.returncode,0,out.stderr)
            c.write_text(out.stdout);self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,0)
            p.write_text(p.read_text()+'\n');self.assertEqual(subprocess.run(cmd+['--check',str(c)],capture_output=True).returncode,2)


if __name__=='__main__':unittest.main()
