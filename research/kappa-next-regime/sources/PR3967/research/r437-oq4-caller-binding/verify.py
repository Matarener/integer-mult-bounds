"""Read-only source-bound replay, including Git-free export controls."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def require(ok,message):
    if not ok:raise ValueError(message)


def regular(path):
    require(path.is_file(),'missing regular input: '+str(path))
    for part in (path,*path.parents):
        require(not part.is_symlink(),'symlinked input: '+str(part))


def authenticate():
    sources=json.loads((HERE/'SOURCES.json').read_bytes())
    require(sources['base_commit']=='20ecf2891d80b5acf18d980b2164fb44ea7faa90','canonical scientific base')
    for row in sources['files']:
        if row['usage']!='input':continue
        path=ROOT/row['path'];regular(path);data=path.read_bytes()
        require(hashlib.sha256(data).hexdigest()==row['sha256'],'canonical input hash: '+row['path'])
        require(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
                'canonical input Git blob: '+row['path'])
    inventory=set()
    for row in sources['retained']:
        path=HERE/row['path'];regular(path);data=path.read_bytes();inventory.add(row['path'])
        require(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'] and
                hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['git_blob'],
                'retained source identity: '+row['path'])
    observed={str(f.relative_to(HERE)) for f in (HERE/'inputs').rglob('*') if f.is_file()}
    require(inventory==observed,'complete retained input inventory')
    physical=json.loads((HERE/'PHYSICAL.json').read_bytes())
    require(physical['complete_GL64_payload_executed'] is False and physical['stock_is_controlled_fixture'] is True,
            'controlled physical probe is not a production cohort')
    require(physical['widths']==[2048,832,91] and physical['ancestor_request']==27776 and physical['copy_request']==1603,
            'actual current source records and nonterminal extents')
    return sources


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--suite',choices=['catalogue','physical','export'],required=True)
    args=parser.parse_args();authenticate()
    sys.path.insert(0,str(HERE))
    if args.suite=='export':
        from test_export import run
        result=run()
    else:
        if args.suite=='catalogue':
            from catalogue_audit import run
            receipt='CATALOGUE.json'
        else:
            from physical_probe import run
            receipt='PHYSICAL.json'
        result=run()
        require(json.loads(json.dumps(result))==json.loads((HERE/receipt).read_bytes()),
                'complete scoped receipt mismatch: '+receipt)
    print(json.dumps({'status':'PASS_OQ4_CALLER_BINDING_'+args.suite.upper(),
                      'source_bound_result':result['status'],
                      'conclusion':'Partial: real source/protocol binding; no completed GL64 production cohort'},sort_keys=True))


if __name__=='__main__':main()
