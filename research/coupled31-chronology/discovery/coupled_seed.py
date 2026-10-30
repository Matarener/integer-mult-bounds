"""Search a coupled three-leaf seed with all call orders free.

This search uses necessary coefficients. Each candidate needs full replay.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import time
import z3

ROOT = Path(__file__).resolve().parents[1]


def build(pattern, timeout, seed):
    d, g, n = 4, 3, 16
    solver = z3.Solver()
    solver.set(timeout=timeout, random_seed=seed)
    def zero(size):
        return [z3.BitVecVal(0, size) for _ in range(size)]
    def eye(size):
        return [z3.BitVecVal(1 << i, size) for i in range(size)]
    def add(a, b):
        return [x ^ y for x, y in zip(a, b)]
    def mul(a, b):
        size = len(a)
        out = []
        for row in a:
            value = z3.BitVecVal(0, size)
            for k in range(size):
                value ^= z3.If(z3.Extract(k, k, row) == 1, b[k], 0)
            out.append(z3.simplify(value))
        return out
    def embed(a, b, stage):
        p, r = zero(n), zero(n)
        for i in range(d):
            aa = z3.ZeroExt(n-d, a[i])
            bb = z3.ZeroExt(n-d, b[i])
            p[i] = (aa ^ bb) | (bb << (d*(stage+1)))
            p[d*(stage+1)+i] = bb | ((aa ^ bb) << (d*(stage+1)))
            r[i] = aa | (aa << (d*(stage+1)))
            r[d*(stage+1)+i] = r[i]
        return p, r
    calls = []
    for j in range(g):
        a = [z3.BitVec(f'a{j}_{i}', d) for i in range(d)]
        b = [z3.BitVec(f'b{j}_{i}', d) for i in range(d)]
        for x, y in zip(mul(a, a), a):
            solver.add(x == y)
        for x, y in zip(add(mul(a, b), mul(b, a)), b):
            solver.add(x == y)
        trace = z3.BitVecVal(0, 1)
        for i in range(d):
            trace ^= z3.Extract(i, i, a[i])
        solver.add(trace == 0, z3.Or(*[x != 0 for x in a]),
                   z3.Or(*[x != (1 << i) for i, x in enumerate(a)]))
        for half in range(2):
            p, r = embed(a if not half else add(a, eye(d)), b, j)
            calls.append((j, p, r))
    signatures = (0, 1, 1) if pattern == 'pair' else (1, 2, 3)
    u = sum(v << (d*(j+1)) for j, v in enumerate(signatures))
    e = [u if (u >> i) & 1 else 0 for i in range(n)]
    fs, gs = [], []
    for i in range(d):
        f, h = [0]*n, [0]*n
        for j in range(g):
            f[i] |= 1 << (d*(j+1)+i)
            h[d*(j+1)+i] = 1 << i
        fs.append(f)
        gs.append(h)
    qs = [[x ^ y for x, y in zip(fs[0], e)],
          [x ^ y for x, y in zip(gs[1], e)]]
    qs += [[x ^ y for x, y in zip(fs[i], gs[(i+1) % d])]
           for i in range(1, d)]
    for query in qs:
        calls.append((g, zero(n), [z3.BitVecVal(x, n) for x in query]))
    positions = [z3.Int(f'pos{i}') for i in range(len(calls))]
    solver.add(z3.Distinct(positions), *[z3.And(p >= 0, p < len(calls))
                                       for p in positions])
    for j in range(g):
        solver.add(positions[2*j] < positions[2*j+1])
    for j in range(g):
        equation = zero(n)
        for i in (2*j, 2*j+1):
            tail = zero(n)
            for k, (_, _, r) in enumerate(calls):
                if k != i:
                    tail = add(tail, [z3.If(positions[k] > positions[i], x, 0)
                                     for x in r])
            p = calls[i][1]
            equation = add(equation, add(mul(p, tail), mul(tail, p)))
        solver.add(*[x == 0 for x in equation])
    # Every pair of pure stage coefficients must agree.
    for j in range(g):
        for k in range(j):
            eq = zero(n)
            for i in (2*j, 2*j+1):
                for h in (2*k, 2*k+1):
                    before = mul(calls[h][1], calls[i][1])
                    after = mul(calls[i][1], calls[h][1])
                    eq = add(eq, [z3.If(positions[i] < positions[h], x, y)
                                  for x, y in zip(before, after)])
            ej = add(calls[2*j][1], calls[2*j+1][1])
            ek = add(calls[2*k][1], calls[2*k+1][1])
            solver.add(*[x == y for x, y in zip(eq, mul(ej, ek))])
    return solver, calls, positions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pattern', choices=('pair', 'triangle'), required=True)
    parser.add_argument('--timeout', type=int, default=60000)
    parser.add_argument('--seed', type=int, default=20261026)
    parser.add_argument('--models', type=int, default=8)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start = time.monotonic()
    solver, calls, positions = build(args.pattern, args.timeout, args.seed)
    spec = importlib.util.spec_from_file_location('old_word', ROOT/'sources/old-word-replay.py')
    replay = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(replay)
    records = []
    for iteration in range(args.models):
        status = solver.check()
        row = {'iteration': iteration, 'status': str(status),
               'seconds': round(time.monotonic()-start, 3)}
        if status == z3.sat:
            model = solver.model()
            order = sorted(range(len(calls)), key=lambda i: model.eval(positions[i], model_completion=True).as_long())
            numeric = [{'stage': j, 'p': [model.eval(x, model_completion=True).as_long() for x in p],
                        'r': [model.eval(x, model_completion=True).as_long() for x in r]}
                       for j, p, r in calls]
            row.update(order=order, calls=numeric, endpoint=replay.replay(numeric, order))
            # Do not repeat a necessary-condition false positive.
            expressions = [x for _, p, r in calls for x in p+r] + positions
            solver.add(z3.Or(*[x != model.eval(x, model_completion=True) for x in expressions]))
        elif status == z3.unknown:
            row['reason'] = solver.reason_unknown()
        records.append(row)
        result = {'pattern': args.pattern, 'timeout_ms': args.timeout,
                  'seed': args.seed, 'z3': z3.get_version_string(), 'records': records}
        args.output.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps({k: v for k, v in row.items() if k != 'calls'}), flush=True)
        if status != z3.sat or row['endpoint']['passed']:
            break


if __name__ == '__main__':
    main()
