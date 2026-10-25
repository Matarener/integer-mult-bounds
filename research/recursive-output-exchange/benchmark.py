"""Three alternating fresh-process pairs on one complete unchanged route."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
from time import perf_counter

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--worker',action='store_true')
    parser.add_argument('--optimized',action='store_true')
    args=parser.parse_args()
    if args.worker:
        import route_checks
        result,elapsed=route_checks.one(route_checks.cases()[0],args.optimized)
        print(json.dumps(dict(result=result,seconds=elapsed)));return
    rows=[]
    for repeat in range(3):
        for optimized in ((False,True) if repeat%2==0 else (True,False)):
            cmd=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker']
            if optimized:cmd.append('--optimized')
            start=perf_counter();row=json.loads(subprocess.check_output(cmd,text=True))
            row.update(repeat=repeat,optimized=optimized,process_seconds=perf_counter()-start);rows.append(row)
    summary={}
    for field in ('seconds','process_seconds'):
        a,b=[statistics.median(r[field] for r in rows if r['optimized']==opt) for opt in (False,True)]
        summary[field]=dict(before=a,after=b,speedup=a/b)
    print(json.dumps(dict(python=sys.version,rows=rows,summary=summary),indent=2))


if __name__=='__main__':main()
