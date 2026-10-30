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
    with tempfile.TemporaryDirectory(prefix='smith-python-') as cache:
        commands = [('derive', ['--out', str(out/'DERIVED.json')]),
                    ('independent', ['--producer', str(out/'DERIVED.json'), '--out', str(out/'INDEPENDENT.json')])]
        for name, extra in commands:
            command = [sys.executable,'-I','-O','-B','-Werror','-X','pycache_prefix='+cache+'/'+name,str(HERE/(name+'.py'))]+extra
            run = subprocess.run(command,cwd=REPO,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=55)
            (out/(name+'.log')).write_text(run.stdout)
            need(run.returncode == 0, name+' failed:\n'+run.stdout[-8000:])
    a = json.loads((out/'DERIVED.json').read_bytes())
    b = json.loads((out/'INDEPENDENT.json').read_bytes())
    need(a['localized_Smith_factors'] == [{'factor':1,'count':30400},{'factor':11,'count':336},{'factor':209,'count':208},{'factor':4807,'count':16}], 'complete Smith factors')
    need(b['localized_smith'] == [[1,30400],[11,336],[209,208],[4807,16]], 'independent Smith factors')
    need(a['physical_row_certificate']['physical_rows'] == b['physical_rows'] and len(set(b['physical_rows'])) == 560, 'literal physical rows')
    need((b['all_harmonic_polynomial_actions'],b['all_mixed_polynomial_actions'],b['all_radial_polynomial_actions']) == (240,560,32), 'all polynomial action coverage')
    need(len(a['negative_controls']) == 2 and len(b['negative_controls']) == 3 and len(a['arithmetic_counterchecks']) == 2, 'matrix and arithmetic controls')
    need(before == authenticate(), 'inputs changed during replay')
    result = {'status':'PASS_H6_DYADIC_SMITH_PHYSICAL_ROW_EXISTENCE','no_new_kappa':True,
              'localized_smith':b['localized_smith'],'physical_rows':560,'stable_auxiliary_dimension':560,
              'independent_actions':{'harmonic':240,'mixed':560,'radial':32},
              'producer_matrix_controls':a['negative_controls'],'independent_controls':b['negative_controls'],
              'producer_arithmetic_controls':a['arithmetic_counterchecks'],
              'seconds':time.monotonic()-start,'python':sys.version,
              'cost_scope':'Algebraic completion of C=I-K only; not the native K response, completion coefficients or a paid physical/restored source circuit.',
              'inherited':'Full characteristic spectrum and degree-six shell moment theorem remain explicit source premises.'}
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
        with tempfile.TemporaryDirectory(prefix='smith-replay-') as work:
            replay(Path(work)/'result')

if __name__ == '__main__':
    main()
