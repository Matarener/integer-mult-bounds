#!/usr/bin/env python3
"""Real source mutants; receipt comparison deliberately bypassed.
SHIN09-git, substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE=Path(__file__).resolve().parent

MUTANTS=(
    ("reorder_closed_formula_inverse","verify.py",
     "(J@A.inverse()@F).rank()","(A.inverse()@J@F).rank()","PR6053 ordered closed rho0"),
    ("omit_H_rank_closed_formula","verify.py",
     "+2*H.rank()-2*A.r","+0*H.rank()-2*A.r","PR6053 ordered closed rho0"),
    ("omit_efficient_row_phase","construct.py",
     "if i not in core_i:","if False and i not in core_i:","maximal rank minor"),
    ("use_principal_minors_only","construct.py",
     "if C.take(ni,nj).rank()==size-1:","if i == j and C.take(ni,nj).rank()==size-1:","nonzero cofactor exists"),
    ("reverse_H_Binverse_order","construct.py",
     "Gp=block([[ai,-bi,ai-bi],[O,H@bi,H@bi-eye(d,p)]])",
     "Gp=block([[ai,-bi,ai-bi],[O,bi@H,bi@H-eye(d,p)]])","left lift identity"),
    ("lose_odd_characteristic_sign","construct.py",
     "tuple(-x for x in z)+(0,)*d if j==1",
     "tuple(z)+(0,)*d if j==1","right lift identity"),
    ("mix_sector_annihilators","construct.py",
     "if emeta[i][0]==j]","if emeta[i][0]!=j]","sector factor"),
    ("wrong_slope_two_bound","construct.py",
     "nmax-2*(2*d-rho)","nmax-(2*d-rho)","sharp dimension law"),
    ("omit_independent_rank_check","check_witnesses.py",
     'require(actual==rho,"literal Schur commutator rank")',
     'require(True,"literal Schur commutator rank")',"independent checker accepted wrong_rank"),
)

def run():
    results=[]
    with tempfile.TemporaryDirectory(prefix="schur-rank-mutants-") as tmp:
        root=Path(tmp)
        pristine=root/"positive"
        pristine.mkdir()
        for src in HERE.iterdir():
            if src.is_file():
                shutil.copyfile(src,pristine/src.name)
        command=[sys.executable,"-I","-O","-B","verify.py","--quick","--emit-receipt"]
        t=time.perf_counter()
        positive=subprocess.run(command,cwd=pristine,capture_output=True,text=True,encoding="utf-8",timeout=90)
        if positive.returncode:
            raise ValueError("optimized source-only positive control failed: "+positive.stderr)
        payload=json.loads(positive.stdout)
        if payload["unique_triples"]!=219 or payload["literal_witnesses"]!=1093:
            raise ValueError("positive coverage changed")
        results.append({"name":"optimized_positive","status":"PASS","seconds":time.perf_counter()-t})
        for name,filename,old,new,message in MUTANTS:
            dest=root/name
            shutil.copytree(pristine,dest)
            target=dest/filename
            source=target.read_text(encoding="utf-8")
            if source.count(old)!=1:
                raise ValueError("mutant target must match exactly once: "+name)
            mutated=source.replace(old,new,1)
            compile(mutated,str(target),"exec")
            target.write_text(mutated,encoding="utf-8",newline="\n")
            t=time.perf_counter()
            run=subprocess.run(command,cwd=dest,capture_output=True,text=True,encoding="utf-8",timeout=90)
            if run.returncode==0 or message not in run.stderr or "SyntaxError" in run.stderr:
                raise ValueError("mutant not rejected by intended scientific check "+name+"\n"+run.stderr[-1800:])
            results.append({"name":name,"status":"REJECTED","seconds":time.perf_counter()-t,
                            "expected_check":message,"stderr_sha256":sha256(run.stderr.encode()).hexdigest(),
                            "last_error":run.stderr.strip().splitlines()[-1]})
    return {"mode":"optimized fresh source-only subprocesses; exact receipt comparison disabled",
            "positive_controls":1,"code_mutants_rejected":len(MUTANTS),"results":results}

if __name__=="__main__":
    print(json.dumps(run(),indent=2))
