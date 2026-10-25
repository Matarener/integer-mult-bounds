"""Semantic controls for modular lifting, charged packing and source binding.
Dugongue, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from pathlib import Path
from copy import deepcopy
import json
import shutil
import subprocess
import sys
import tempfile
from hybrid import ROOT,need,lift,residue_lane,certificate,precision_view,seed_lines,least_precision


def rejected(call,label):
    try:call()
    except (ValueError,TypeError):return
    raise ValueError('accepted mutant: '+label)


def main():
    groups=[]
    for modulus in (1,2,4,16,256):
        for c in range(-100,101):
            radius=F(modulus,3)
            for offset in (-radius,0,radius):
                need(lift(F(c)+offset,radius,c%modulus,modulus)==c,'translated integer lift')
    for center,radius,residue,modulus in [(0,1,0,2),(0,-1,0,2),(0,0,1,2),(0,0,2,2),(0,0,0,0)]:
        rejected(lambda a=(center,radius,residue,modulus):lift(*a),'strict spacing/domain')
    # A residue genuinely supplies information absent from ordinary rounding.
    need(lift(F(101,2),F(3,4),50%16,16)==50,'wider valid interval')
    need(lift(F(101,2),F(3,4),51%16,16)==51,'untrusted residue can select a different integer')
    # The numerical interval is not authentication for the exact lane.
    groups.append('universal spacing translation strictness and residue trust boundary')

    for args in [([], [1], 2),([1],[],2),([1],[-1],2),([1],[1],0),([1],[1],True)]:
        rejected(lambda args=args:residue_lane(*args),'packing domain')
    a=[15,15,15];b=[15,15,15];residues,bill=residue_lane(a,b,4)
    need(residues==[1,2,3,2,1] and bill['slot_bits']==10,'guarded exact packing')
    wrong_width=2*4-1
    pa=sum(x << (j*wrong_width) for j,x in enumerate(a));pb=sum(x << (j*wrong_width) for j,x in enumerate(b))
    bad=[((pa*pb >> (j*wrong_width))&((1 << wrong_width)-1))%16 for j in range(5)]
    need(bad!=residues,'under-guarded slots really corrupt residues')
    groups.append('paid carry-free packing and actual spill mutant')

    seeds=seed_lines();lines,cert=least_precision(seeds,64,16)
    need(cert['precision']==192,'hybrid p')
    rejected(lambda:certificate(lines,64,0),'same-p ordinary certificate')
    rejected(lambda:certificate(precision_view(seeds,191),64,16),'one-bit-lower certificate')
    rejected(lambda:precision_view(seeds,25),'alpha square domain')
    rejected(lambda:precision_view(seeds,100),'original p greater than 100 domain')
    rejected(lambda:precision_view(seeds,257),'unproved precision extrapolation')
    rejected(lambda:certificate([lines[0],lines[0]],64,16),'noncoprime CRT axes')
    need(cert['source_scale']==455**2*(1 << 132),'both source normalization factors')
    groups.append('precision domains ordinary comparison CRT and both source factors')

    # Real Git-free command runs; corrupt the authenticated source before import.
    with tempfile.TemporaryDirectory(prefix='modular-recovery-') as temp:
        dst=Path(temp)/'export';shutil.copytree(ROOT,dst,ignore=shutil.ignore_patterns('__pycache__'))
        argv=[sys.executable]+(['-O'] if not __debug__ else [])+['-B',str(dst/'verify.py')]
        def cli(extra=()):return subprocess.run(argv+list(extra),cwd=temp,capture_output=True,text=True,timeout=180)
        p=cli(['--check-inputs']);need(p.returncode==0,'actual clean export input check '+p.stderr)
        source=dst/'vendor/gaussian.py';saved=source.read_bytes();source.write_bytes(saved+b'\n# changed source\n')
        p=cli(['--check-inputs']);need(p.returncode!=0 and 'source hash' in p.stderr,'changed source rejected before import')
        source.write_bytes(saved)
        receipt=dst/'RESULT.json';data=json.loads(receipt.read_text(encoding='utf8'));data['precision_curve'][2]['precision']-=1
        receipt.write_text(json.dumps(data),encoding='utf8')
        p=cli();need(p.returncode!=0 and 'frozen mathematical receipt' in p.stderr,'actual false precision receipt rejected')
    groups.append('actual Git-free CLI source and mathematical receipt corruptions')
    print(json.dumps({'status':'PASS_MODULAR_RECOVERY_CONTROLS','groups':groups,'assertions_enabled':__debug__}))


if __name__=='__main__':main()
