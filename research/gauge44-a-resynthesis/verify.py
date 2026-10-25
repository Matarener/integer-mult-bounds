#!/usr/bin/env python3
"""Verify the frozen resynthesis artifact and its global admission.

The exact X4 source word is the input pinned by PR #799; this package freezes
both the resulting word and all independent local/global receipts.
"""
import argparse, gzip, hashlib, json, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUTPUT_SHA='9094660307632862c3b09027a736fe93d397e88fa74806755a2e83198c060844'
def content(path):return hashlib.sha256(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args();root=HERE.parents[1];a.work.mkdir(parents=True,exist_ok=False)
 word=HERE/'artifacts/FULL-WORD.json.gz';assert content(word)==OUTPUT_SHA
 print('PASS_FROZEN_WORD',OUTPUT_SHA)
 cmd=[sys.executable,'-B',str(HERE/'verify_global.py'),'--main',str(root),'--local',str(HERE/'artifacts'),'--work',str(a.work/'global')]
 subprocess.run(cmd,check=True)
 result=json.loads((a.work/'global/ASSEMBLY.json').read_text());assert result['kappa_decimal']=='0.001661634653669567';print('PASS_GLOBAL_ADMISSION',result['kappa_decimal'])
if __name__=='__main__':main()
