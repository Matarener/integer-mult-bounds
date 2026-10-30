"""One fixed synthetic batch per process; root controls ordering and budgets.

No actual-word speed projection follows from this batch. The candidate command
includes cold compilation/loading and finite qualification before batch timing;
outer guarded wall/CPU is authoritative for the complete command bill.
This source was not executed by its author.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import json
import time

from finite_probe import literal_row, literal_coefficient_bytes, run as finite_run


def batch(native):
    # Fixed inputs, generated afresh inside each batch invocation. No result or
    # answer sharing across baseline/candidate processes or separate invocations.
    weights = [(i + 1, 2 * i + 3) for i in range(64)]
    rows = [{i: ((-1) ** i) * ((1 << 192) + i * 64) for i in range(32)}
            for _ in range(4)]
    scores = [[0, 0, 0] for _ in rows]
    scale = 64
    units = (128, 256, 64)
    stream = sha256()
    for step in range(1024):
        destination = step % 4
        source = {i: (-1 if (step + i) % 3 == 0 else 1) *
                     ((1 << 192) + (i + 1) * 64)
                  for i in range(step % 32, step % 32 + 32)}
        numerator = -3 if step % 2 else 3
        if native is None:
            row, score = literal_row(rows[destination], source, numerator, 3,
                                     scores[destination], weights)
            score_bytes = (str(step) + ':' + ','.join(
                str(Fraction(v, u)) for v, u in zip(score, units)) + ';').encode()
            coefficient_bytes = literal_coefficient_bytes(row, scale)
        else:
            row, score = native.error_row(rows[destination], source, numerator, 3,
                                          scores[destination], weights)
            score_bytes = native.score_bytes(step, score, units)
            coefficient_bytes = native.coefficient_bytes(row, scale)
        rows[destination], scores[destination] = row, list(score)
        stream.update(score_bytes)
        stream.update(coefficient_bytes)
    return dict(batch='fixed-1024-synthetic-sparse-score-format-v1',
                steps=1024, final_rows=rows, final_scores=scores,
                complete_byte_stream_sha256=stream.hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['baseline', 'candidate'], required=True)
    parser.add_argument('--source-sha256')
    args = parser.parse_args()
    native = None
    finite = None
    build = None
    if args.mode == 'candidate':
        if args.source_sha256 is None:
            parser.error('candidate requires --source-sha256')
        import native_loader
        native = native_loader.load(args.source_sha256)
        finite = finite_run(native)
        build = native_loader.receipt()
    started_wall, started_cpu = time.perf_counter(), time.process_time()
    result = batch(native)
    batch_wall = time.perf_counter() - started_wall
    batch_cpu = time.process_time() - started_cpu
    result_digest = sha256(json.dumps(result, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    print(json.dumps(dict(mode=args.mode, result_sha256=result_digest,
                         complete_byte_stream_sha256=result['complete_byte_stream_sha256'],
                         synthetic_batch_wall_seconds=batch_wall,
                         synthetic_batch_cpu_seconds=batch_cpu,
                         finite=finite, build=build,
                         complete_speed_claim=False), sort_keys=True))
