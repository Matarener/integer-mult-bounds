"""Authenticate before importing source; compare the full typed receipt."""
import argparse,hashlib,importlib.util,json,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,why):
    if not ok:raise ValueError(why)
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)
def sources():
    for row in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if row['usage']=='input':
            p=ROOT/row['path'];need(p.is_file() and not p.is_symlink() and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'source hash '+row['path'])
    frozen=json.loads((HERE/'ORACLE-FREEZE.json').read_text())
    need(hashlib.sha256((HERE/'oracle.py').read_bytes()).hexdigest()==frozen['oracle_sha256'],'frozen independent oracle')
def run(physical=True):
    sources()
    with tempfile.TemporaryDirectory(prefix='coefficient-pycache-') as temp:
        old=sys.pycache_prefix;sys.pycache_prefix=temp
        try:
            sys.path.insert(0,str(HERE));import oracle
            out={'oracle_self_tests':oracle.self_tests()}
            if physical:
                sys.path.insert(0,str(ROOT/'research/physical-gaussian-core'))
                spec=importlib.util.spec_from_file_location('raw_snapshot_helper',ROOT/'research/schur-boundary-residual/fixture.py')
                helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
                from gaussian_sources import opened
                import producer
                with opened():out['producer']=producer.run(helper)
            return out
        finally:sys.pycache_prefix=old

def main():
    p=argparse.ArgumentParser();p.add_argument('--record',type=Path);p.add_argument('--oracle-only',action='store_true');a=p.parse_args()
    if a.record:need(not a.record.exists(),'record refuses overwrite')
    else:expected=json.loads((HERE/'RESULT.json').read_text())
    result=run(not a.oracle_only)
    if a.record:a.record.write_text(json.dumps(result,indent=2)+'\n')
    else:
        if a.oracle_only:expected={'oracle_self_tests':expected['oracle_self_tests']}
        need(canonical(result)==canonical(expected),'complete typed receipt mismatch')
    print('PASS_ENCODED_GAUSSIAN_COEFFICIENT_AUDIT'+('_ORACLE'if a.oracle_only else''))
    print(hashlib.sha256(canonical(result).encode()).hexdigest())
if __name__=='__main__':main()
