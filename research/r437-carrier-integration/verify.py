#!/usr/bin/env python3
"""Immutable integrated replay. New source/receipt errors reject before execution.
Chris R / Clear1nsight; substantial OpenAI Codex assistance. Apache-2.0.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha1, sha256
from pathlib import Path, PurePosixPath
import argparse
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
COMPONENTS={
    'compiler':('compiler_checks','COMPILER-CHECKS.json'),
    'independent':('independent','INDEPENDENT-RESULT.json'),
    'numerical':('numerical','NUMERICAL-RESULT.json'),
    'residual':('residual_algebra','RESIDUAL-ALGEBRA.json'),
    'physical':('physical','PHYSICAL-RESULT.json'),
    'admission':('admission','ADMISSION-RESULT.json'),
}

def need(ok,message):
    if not ok:raise ValueError(message)

def normalize(x):return json.loads(json.dumps(x))
def encoded(x):return json.dumps(normalize(x),sort_keys=True,separators=(',',':'))

def safe_file(root,name):
    p=PurePosixPath(name)
    need(not p.is_absolute() and str(p)==name and all(x not in ('..','.') for x in p.parts),'canonical source path')
    path=root.joinpath(*p.parts)
    need(path.is_file() and not path.is_symlink(),'regular declared source: '+name)
    need(not any(a.is_symlink() for a in path.parents),'symlinked source parent: '+name)
    return path

def authenticate():
    sources=json.loads((HERE/'SOURCES.json').read_bytes())
    all_rows=sources['files'];need(len(all_rows)==len({x['path'] for x in all_rows}),'unique source inventory')
    # Provenance pins are checked by the registered Git metadata validator.
    # A Git-free source export authenticates exactly the declared live inputs.
    rows=[x for x in all_rows if x['usage']=='input']
    for row in rows:
        b=safe_file(ROOT,row['path']).read_bytes()
        need(sha256(b).hexdigest()==row['sha256'],'source SHA256: '+row['path'])
        need(sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'source Git blob: '+row['path'])
    integrity=json.loads((HERE/'INTEGRITY.json').read_bytes())
    actual={p.relative_to(HERE).as_posix() for p in HERE.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.name!='INTEGRITY.json'}
    need(set(integrity)==actual,'exact package inventory')
    for name,digest in integrity.items():
        need(sha256(safe_file(HERE,name).read_bytes()).hexdigest()==digest,'package hash: '+name)
    return len(rows),len(integrity)+1

def component(name):
    sys.path.insert(0,str(HERE))
    if name=='numerical':
        import numerical
        result=numerical.run(json.loads((HERE/'COMPILER-CHECKS.json').read_bytes()))
    else:
        module=__import__(COMPONENTS[name][0])
        result=module.audit() if name=='physical' else module.run()
    expected=json.loads((HERE/COMPONENTS[name][1]).read_bytes())
    need(encoded(result)==encoded(expected),'immutable '+name+' receipt')
    return {'component':name,'status':result['status'],'receipt_sha256':sha256((HERE/COMPONENTS[name][1]).read_bytes()).hexdigest()}

def child(name):
    argv=[sys.executable,'-I','-B']
    if sys.flags.optimize:argv.append('-O')
    argv += [str(HERE/'verify.py'),'--component',name]
    p=subprocess.run(argv,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=590,check=False)
    need(p.returncode==0,'component '+name+' failed:\n'+p.stdout[-3000:]+'\n'+p.stderr[-5000:])
    marker='COMPONENT_JSON='
    records=[x[len(marker):] for x in p.stdout.splitlines() if x.startswith(marker)]
    need(len(records)==1,'single component receipt: '+name)
    return json.loads(records[0])

def run_all():
    sources,files=authenticate()
    results=[]
    with ThreadPoolExecutor(max_workers=3) as executor:
        pending={executor.submit(child,name):name for name in COMPONENTS}
        for future in as_completed(pending):
            result=future.result();results.append(result)
            print('PASS_CARRIER_COMPONENT '+result['component'],flush=True)
    checks={r['component']:r for r in results}
    need(set(checks)==set(COMPONENTS),'all integrated components complete')
    # Bind independently authored request digests/profile to the primary fresh
    # builder, rather than accept two unrelated PASS lines.
    primary=json.loads((HERE/'COMPILER-CHECKS.json').read_bytes())
    independent=json.loads((HERE/'INDEPENDENT-RESULT.json').read_bytes())
    for variant in ('C','D'):
        actual=independent['native_requests'][variant]
        need(actual['ordered_request_sha256']==primary[variant]['request_sha256'],'independent literal '+variant+' request digest')
        need(independent['four_way'][variant]['profile']==primary[variant]['profile'],'independent literal '+variant+' profile')
    print('PASS_R437_CARRIER_INTEGRATION '+json.dumps({'components':sorted(checks),'source_files':sources,'package_files':files,'optimized':bool(sys.flags.optimize),'significance':'scoped enabling integration; no full physical supplier or selected kappa admission'},sort_keys=True))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--component',choices=tuple(COMPONENTS));ap.add_argument('--authenticate-only',action='store_true');a=ap.parse_args()
    if a.component:
        print('COMPONENT_JSON='+json.dumps(component(a.component),sort_keys=True))
    elif a.authenticate_only:
        print('PASS_CARRIER_AUTHENTICATION '+str(authenticate()))
    else:run_all()
