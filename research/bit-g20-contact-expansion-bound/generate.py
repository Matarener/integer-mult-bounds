"""Optionally generate the flow certificate with OR-Tools 9.14.6206.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
This program does not change the checked-in certificate.
"""
import argparse
import gzip
import importlib.util
from pathlib import Path
import struct


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('The output file already exists')
    from ortools.graph.python import max_flow
    spec = importlib.util.spec_from_file_location('contact_bound', Path(__file__).with_name('verify.py'))
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    codes, _, vertices, mutable, edges, distances, _, _ = checker.model()
    payload = bytearray(b'G20FLOW1')
    for alpha in codes:
        arcs, source, sink, constant = checker.network(alpha, vertices, mutable, edges, distances)
        solver = max_flow.SimpleMaxFlow()
        for u, v, capacity in arcs:
            solver.add_arc_with_capacity(u, v, capacity)
        checker.need(solver.solve(source, sink) == solver.OPTIMAL, 'Solver completion')
        pairs = [(i, solver.flow(i)) for i in range(len(arcs)) if solver.flow(i) > 0]
        checker.flow_check(arcs, source, sink, constant, pairs)
        payload.extend(struct.pack('<II', alpha, len(pairs)))
        for index, value in pairs:
            checker.need(value < 2**32, 'Certificate flow field')
            payload.extend(struct.pack('<II', index, value))
    with args.output.open('xb') as stream:
        stream.write(gzip.compress(payload, mtime=0))
    print('PASS_GENERATED_INTEGER_FLOW_CERTIFICATE', args.output)

if __name__ == '__main__':
    main()
