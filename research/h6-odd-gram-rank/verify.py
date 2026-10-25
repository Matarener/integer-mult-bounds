#!/usr/bin/env python3
"""Read-only exact replay; Apache-2.0, substantial OpenAI Codex assistance."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

def need(ok, message):
    if not ok:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def authenticate():
    files = json.loads((HERE/'ARTIFACTS.json').read_bytes())['files']
    for name, digest in files.items():
        path = HERE/name
        need(not path.is_symlink() and sha(path) == digest, 'package changed: '+name)
    for row in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
        if row['usage'] == 'input':
            path = REPO/row['path']
            need(not path.is_symlink() and sha(path) == row['sha256'], 'source changed: '+row['path'])
    return files

def replay(out):
    before = authenticate()
    need(not out.exists() and not out.resolve().is_relative_to(HERE), 'fresh external output required')
    out.mkdir(parents=True)
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='odd-gram-python-') as cache:
        commands = [('derive', ['--out', str(out/'DERIVED.json')]),
                    ('independent', ['--producer', str(out/'DERIVED.json'), '--out', str(out/'INDEPENDENT.json')])]
        for name, extra in commands:
            command = [sys.executable,'-I','-O','-B','-Werror','-X','pycache_prefix='+cache+'/'+name,str(HERE/(name+'.py'))]+extra
            run = subprocess.run(command,cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=55)
            (out/(name+'.log')).write_text(run.stdout)
            need(run.returncode == 0, name+' failed:\n'+run.stdout[-8000:])
    a = json.loads((out/'DERIVED.json').read_bytes())
    b = json.loads((out/'INDEPENDENT.json').read_bytes())
    need(a['rank_minima'] == {'cubic':800,'genuine_quintic':9424,'septic':20400}, 'derived minima')
    need(b['rank_minima'] == [800,9424,20400], 'independent minima')
    need(a['direct_actions'] == b['direct_actions'] == 18, 'complete action coverage')
    need(b['association_square_entries'] == 57600 and b['canonical_input_columns_per_action'] == 28800, 'finite coverage')
    need(len(a['rejected_coefficient_controls']) == 4 and b['canonical_quotient_negative_control'], 'five defect controls')
    need(before == authenticate(), 'inputs changed during replay')
    result = {'status':'PASS_H6_ODD_GRAM_SHARP_RANKS','no_new_kappa':True,'rank_minima':[800,9424,20400],
              'association_entries_per_checker':57600,'actions_per_checker':18,'columns_per_action':28800,
              'producer_controls':4,'independent_controls':1,'seconds':time.monotonic()-start,'python':sys.version,
              'all_parameter_scope':'Written characteristic-zero interpolation and exhaustive affine-case proof; finite exact evidence supports its coefficients.',
              'cost_scope':'Full-width17 scalar rank-one return episodes only; not a universal physical-helper or arbitrary-decoder bound.'}
    (out/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    need(sys.version_info[:2] == (3,12), 'Python3.12 required')
    if args.out:
        replay(args.out.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix='odd-gram-replay-') as work:
            replay(Path(work)/'result')

if __name__ == '__main__':
    main()
