"""One paired workload per fresh process; timing is separate from scientific receipts."""
import argparse
import json
from pathlib import Path
import sys
from time import perf_counter
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fused_sources


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=('kernel', 'route'), required=True)
    parser.add_argument('--optimized', type=int, choices=(0, 1), required=True)
    args = parser.parse_args()
    start = perf_counter()
    if args.kind == 'kernel':
        check = fused_sources.load('affine_benchmark_kernel', 'research/dyadic-affine-streams/check_affine.py')
        result, seconds = check.one_case(81, 2, 3, 4, -4, False, bool(args.optimized))
    else:
        check = fused_sources.load('affine_benchmark_route', 'research/dyadic-affine-streams/check_routes.py')
        result, seconds = check.run_case(check.cases()[0], bool(args.optimized))
    print(json.dumps(dict(kind=args.kind, optimized=bool(args.optimized), total=result['total'],
                         instrumented_seconds=seconds, loaded_seconds=perf_counter()-start), sort_keys=True))


if __name__ == '__main__':
    main()
