"""Read-only replay. It never refreshes a receipt or regenerates frozen inputs."""
import argparse,hashlib,json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]

def need(ok,message):
    if not ok:raise ValueError(message)

def regular(path):
    need(path.is_file(),'missing input: '+str(path))
    need(not any(p.is_symlink() for p in (path,*path.parents)),'symlinked input: '+str(path))

def authenticate():
    sources=json.loads((HERE/'SOURCES.json').read_bytes())
    need(sources['base_commit']=='20ecf2891d80b5acf18d980b2164fb44ea7faa90','canonical base')
    for row in sources['files']+sources['retained']:
        path=(ROOT if 'usage' in row else HERE)/row['path'];regular(path);data=path.read_bytes()
        need(hashlib.sha256(data).hexdigest()==row['sha256'],'source hash: '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],'source Git blob: '+row['path'])
    expected={r['path'] for r in sources['retained'] if r['path'].startswith('inputs/')}
    observed={str(p.relative_to(HERE)) for p in (HERE/'inputs').rglob('*') if p.is_file()}
    need(expected==observed,'exact frozen input inventory')
    return sources

def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--quick',action='store_true');parser.add_argument('--export',action='store_true');args=parser.parse_args()
    authenticate();sys.path.insert(0,str(HERE))
    if args.export:
        from test_export import run
        result=run()
    else:
        from check import run
        result=run(args.quick);expected=json.loads((HERE/'EXPECTED.json').read_bytes())
        if args.quick:
            need(canonical({k:result[k] for k in ('leaf','add_pass')})==canonical({k:expected[k] for k in ('leaf','add_pass')}),'typed quick receipt')
        else:need(canonical(result)==canonical(expected),'typed complete receipt')
    print(json.dumps({'status':'PASS_R437_RESIDUAL_CONTRACT','scope':'quick' if args.quick else 'Git-free quick export' if args.export else 'actual encoded coefficients and finite leaf controls','supplier_admitted':False},sort_keys=True))

if __name__=='__main__':main()
