"""Alternating fresh-process comparisons; exact results remain checked."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
from time import perf_counter
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))


def worker(kind,optimized):
    if kind=='kernel':
        from check_kernel import one_case
        result,elapsed=one_case(81,2,3,-4,optimized)
    else:
        # Explicit loading avoids the predecessor's equally named check_routes.
        import importlib.util
        spec=importlib.util.spec_from_file_location('carry_benchmark_routes',HERE/'check_routes.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        result,elapsed=module.run_case(module.cases()[0],optimized)
    print(json.dumps(dict(result=result,seconds=elapsed)))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--worker',choices=('kernel','route'))
    parser.add_argument('--optimized',action='store_true')
    parser.add_argument('--repeats',type=int,default=3)
    args=parser.parse_args()
    if args.worker:return worker(args.worker,args.optimized)
    rows=[]
    for kind in ('kernel','route'):
        for repeat in range(args.repeats):
            for opt in ((False,True) if repeat%2==0 else (True,False)):
                command=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'--worker',kind]
                if opt:command.append('--optimized')
                start=perf_counter()
                output=subprocess.check_output(command,text=True)
                row=json.loads(output);row.update(kind=kind,optimized=opt,repeat=repeat,process_seconds=perf_counter()-start)
                rows.append(row)
    summary={}
    for kind in ('kernel','route'):
        summary[kind]={}
        for field in ('seconds','process_seconds'):
            medians=[statistics.median(row[field] for row in rows if row['kind']==kind and row['optimized']==opt)
                     for opt in (False,True)]
            summary[kind][field]=dict(before=medians[0],after=medians[1],speedup=medians[0]/medians[1])
    print(json.dumps(dict(python=sys.version,rows=rows,summary=summary),indent=2,sort_keys=True))


if __name__=='__main__':main()
