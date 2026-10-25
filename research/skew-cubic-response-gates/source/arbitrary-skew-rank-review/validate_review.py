#!/usr/bin/env python3
"""Fail-closed read-only review/source hash validator.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
import hashlib,json,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def need(c,m):
    if not c:raise ValueError(m)
def check(p,x):
    raw=p.read_bytes();need(len(raw)==x['bytes'] and hashlib.sha256(raw).hexdigest()==x['sha256'],'hash/size '+str(p))
def main():
    m=json.loads((HERE/'MANIFEST.json').read_text());pins=json.loads((HERE/'SOURCE-PINS.json').read_text())
    for x in m['files']:check(HERE/x['path'],x)
    for x in pins['files']:check(Path(x['path']),x)
    need(m['no_new_kappa'] is True,'claim scope')
    print('PASS_FROZEN_ANY_SUPPORT_SKEW_REVIEW',len(m['files']),'owned files',len(pins['files']),'read-only source pins')
if __name__=='__main__':main()
