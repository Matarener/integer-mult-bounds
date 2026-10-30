"""Authenticated exact producer audit and rational proof controls."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(ok,why):
    if not ok:raise ValueError(why)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def sources():
    rows=json.loads((HERE/'SOURCES.json').read_text())['files']
    for row in rows:
        if row['usage']=='input':
            p=ROOT/row['path']
            need(p.is_file() and not p.is_symlink(),'regular source '+row['path'])
            need(hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'],'source hash '+row['path'])


def run(physical=True):
    sources()
    with tempfile.TemporaryDirectory(prefix='lu-growth-pycache-') as cache:
        old=sys.pycache_prefix;sys.pycache_prefix=cache
        try:
            sys.path.insert(0,str(HERE));import algebra
            answer={'algebra':algebra.checks()}
            if physical:
                sys.path.insert(0,str(ROOT/'research/physical-gaussian-core'))
                spec=importlib.util.spec_from_file_location('retained_lu_snapshot',ROOT/'research/schur-boundary-residual/fixture.py')
                helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
                from gaussian_sources import opened
                import producer
                with opened():answer['producer']=producer.run(helper)
            return answer
        finally:sys.pycache_prefix=old


def main():
    p=argparse.ArgumentParser();p.add_argument('--algebra-only',action='store_true');p.add_argument('--record',type=Path)
    args=p.parse_args()
    if args.record:need(not args.record.exists(),'record refuses overwrite')
    else:expected=json.loads((HERE/'RESULT.json').read_text())
    result=run(not args.algebra_only)
    if args.record:
        need(not args.record.exists(),'record refuses overwrite')
        args.record.write_text(json.dumps(result,indent=2)+'\n')
    else:
        if args.algebra_only:expected={'algebra':expected['algebra']}
        need(canonical(result)==canonical(expected),'complete typed receipt mismatch')
    print('PASS_OLD_H_ROUNDED_SCHUR_LU_GROWTH'+('_ALGEBRA' if args.algebra_only else ''))
    print(hashlib.sha256(canonical(result).encode()).hexdigest())


if __name__=='__main__':main()
