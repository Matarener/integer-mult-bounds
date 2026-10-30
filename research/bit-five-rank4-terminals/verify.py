#!/usr/bin/env python3
"""Replay the pinned local word, chart supplement and complete moment screen."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)

def main():
    for name,digest in json.loads((HERE/'CONTENT-SHA256.json').read_text()).items():
        need(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,'content hash: '+name)
    flags=['-I','-B']+(['-O'] if sys.flags.optimize else [])
    for name in ['verify_word.py','admission/verify.py','moment/verify.py','moment/independent/validate_window_independent.py']:
        subprocess.run([sys.executable,*flags,str(HERE/name)],cwd=HERE,check=True)
    print('PASS_FIVE_RANK4_TERMINALS exact_stream finite_charts scoped_cost_obstruction no_new_kappa')

if __name__=='__main__':main()
