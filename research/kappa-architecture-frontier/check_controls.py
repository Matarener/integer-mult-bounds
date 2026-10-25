#!/usr/bin/env python3
"""Acceptance mutations in disposable copies; no predecessor workloads."""
from pathlib import Path
import base64
import json
import shutil
import subprocess
import sys
import tempfile
import zlib

ROOT = Path(__file__).resolve().parent


def require(c,m):
    if not c:
        raise ValueError(m)


def run(p,ok,needle='',optimized=False,semantic_only=False):
    argv = [sys.executable,'-I','-B'] + (['-O'] if optimized else [])
    if semantic_only:
        # Deliberately isolate arithmetic/accounting rejection from the stronger
        # Merkle source gate. This is a test harness, never an acceptance mode.
        code = ('import importlib.util,sys; '
                's=importlib.util.spec_from_file_location("frontier",sys.argv[1]); '
                'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
                'm.authenticate=lambda:None; m.calculate()')
        argv += ['-c',code,str(p/'verify.py')]
    else:
        argv += [str(p/'verify.py')]
    r = subprocess.run(argv,text=True,capture_output=True,timeout=15)
    require((r.returncode == 0) == ok,'unexpected verifier status: '+r.stdout+r.stderr)
    require(needle in r.stdout+r.stderr,'missing expected rejection: '+r.stdout+r.stderr)


def main():
    count = 0
    for optimized in (False,True):
        with tempfile.TemporaryDirectory(prefix='kappa-frontier-control-') as temp:
            p = Path(temp)/'package'
            shutil.copytree(ROOT,p)
            run(p,True,optimized=optimized)
            path = p/'inputs/p104-5551.json'
            original = path.read_bytes()
            origins = (p/'ORIGINS.json').read_bytes()
            # Authentication failure.
            path.write_bytes(original+b' ')
            run(p,False,'retained source hash',optimized)
            count += 1
            path.write_bytes(original)
            d = json.loads(origins)
            record = next(r for r in d['objects'].values() if r['type'] == 'tree')
            raw = zlib.decompress(base64.b64decode(record['zlib_base64']))
            record['zlib_base64'] = base64.b64encode(zlib.compress(raw+b' ')).decode()
            (p/'ORIGINS.json').write_text(json.dumps(d))
            run(p,False,'origin object hash',optimized)
            count += 1
            (p/'ORIGINS.json').write_bytes(origins)
            # Isolated semantic gates must reject omitted or invented work.
            for kind in ('query','idle','helper'):
                d = json.loads(original)
                if kind == 'query':
                    d['complete_cost']['paid']['1'] -= 104*15
                elif kind == 'idle':
                    d['complete_cost']['paid']['72'] -= 208
                else:
                    d['local']['helpers']['9'] += 1
                path.write_text(json.dumps(d))
                run(p,False,'P104 source path invoice',optimized,semantic_only=True)
                count += 1
            # Change both local and global cost consistently. This gets past
            # invoice equality but must invalidate the old ceiling.
            d = json.loads(original)
            d['local']['paid']['1'] -= 1
            d['complete_cost']['paid']['1'] -= 18
            path.write_text(json.dumps(d))
            run(p,False,'all-n exclusion gate failed',optimized,semantic_only=True)
            count += 1
            path.write_bytes(original)
            expected = p/'RESULT.json'
            d = json.loads(expected.read_text())
            d['native_or_outer_admission'] = True
            expected.write_text(json.dumps(d))
            run(p,False,'fresh scientific result differs',optimized)
            count += 1
    print('PASS_FRONTIER_ACCEPTANCE_CONTROLS:',count,'disposable normal/optimized rejections')


if __name__ == '__main__':
    main()
