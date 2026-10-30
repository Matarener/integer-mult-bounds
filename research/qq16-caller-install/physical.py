#!/usr/bin/env python3
"""Isolated physical evidence after complete source authentication."""
from pathlib import Path
import sys,json
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import runtime
runtime.cold()
try:
    if len(sys.argv)!=2:raise ValueError('literal physical suite required')
    mode=sys.argv[1]
    if mode=='packet':
        p=runtime.module('qq16_packet',HERE/'packet.py')
        out={'group':p.fixture(),'global':p.global_fixture()}
    elif mode=='lifecycle':
        p=runtime.module('qq16_lifecycle',HERE/'lifecycle.py')
        out={'full224':p.fixture(adopt=True),'adoption':p.adoption_fixture()}
    else:raise ValueError('unknown physical suite')
    print(json.dumps(out,sort_keys=True))
finally:runtime.cleanup()
