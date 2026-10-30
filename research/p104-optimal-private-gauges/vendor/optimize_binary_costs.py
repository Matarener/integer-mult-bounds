#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Certify a global optimum of a declared submodular binary cost table.

Classical graph-cut reduction and Dinic flow. Project precedent: restricted
Gaussian coframe min-cut research, with its retained source attribution.
Prepared for Ali Romman with substantial OpenAI Codex assistance.
"""
import argparse
from collections import deque
from hashlib import sha256
import json
from pathlib import Path
import sys
from compare_recursive_invoices import _pairs, _integer, _not_integer, require


def read(path):
    with Path(path).open('rb') as f: raw = f.read(2*1024**2+1)
    require(len(raw) <= 2*1024**2, 'Input exceeds 2 MiB')
    return json.loads(raw, object_pairs_hook=_pairs, parse_int=_integer,
                      parse_float=_not_integer, parse_constant=_not_integer), sha256(raw).hexdigest()


def compile_costs(value):
    require(type(value) is dict and value.keys() == {'schema', 'unary', 'pairs', 'fixed'}
            and value['schema'] == 'submodular-binary-costs/v1', 'Invalid binary problem')
    unary, pairs, fixed = value['unary'], value['pairs'], value['fixed']
    require(type(unary) is list and 1 <= len(unary) <= 512, 'Use 1..512 choices')
    n = len(unary); source, sink = n, n+1
    require(type(fixed) is list and len(fixed) == n
            and all(x is None or type(x) is int and x in (0, 1) for x in fixed), 'Invalid fixed choices')
    require(type(pairs) is list and len(pairs) <= 8192, 'At most 8192 pair terms')
    def costs(row, length):
        require(type(row) is list and len(row) == length
                and all(type(c) is int and abs(c) <= 10**12 for c in row), 'Invalid integer costs')
        return row
    constant, linear, edges = 0, [], []
    for row in unary:
        a, b = costs(row, 2); constant += a; linear.append(b-a)
    for pair in pairs:
        require(type(pair) is dict and pair.keys() == {'i', 'j', 'costs'}, 'Invalid pair')
        i, j = pair['i'], pair['j']
        require(type(i) is int and type(j) is int and 0 <= i < n and 0 <= j < n and i != j, 'Invalid pair indices')
        a, b, c, d = costs(pair['costs'], 4)
        w = b+c-a-d
        require(w >= 0, 'Pair is not submodular')
        constant += a; linear[i] += c-a; linear[j] += d-c
        if w: edges.append((i, j, w))
    for i, d in enumerate(linear):
        if d >= 0:
            if d: edges.append((source, i, d))
        else:
            constant += d; edges.append((i, sink, -d))
    # This bound exceeds the cost of every cut in the finite graph.
    forbidden = 1+sum(cap for _, _, cap in edges)
    for i, x in enumerate(fixed):
        if x is not None: edges.append((source, i, forbidden) if x == 0 else (i, sink, forbidden))
    return n, edges, constant


def minimum_cut(n, edges):
    source, sink = n, n+1; graph = [[] for _ in range(n+2)]; originals = []
    for a, b, cap in edges:
        forward = [b, cap, len(graph[b])]; reverse = [a, 0, len(graph[a])]
        graph[a].append(forward); graph[b].append(reverse); originals.append(forward)
    while True:
        level = [-1]*(n+2); level[source] = 0; queue = deque([source])
        while queue:
            a = queue.popleft()
            for b, cap, _ in graph[a]:
                if cap and level[b] < 0: level[b] = level[a]+1; queue.append(b)
        if level[sink] < 0: break
        at = [0]*(n+2)
        def send(a, limit):
            if a == sink: return limit
            while at[a] < len(graph[a]):
                edge = graph[a][at[a]]; b, cap, reverse = edge
                if cap and level[b] == level[a]+1:
                    sent = send(b, min(limit, cap))
                    if sent:
                        edge[1] -= sent; graph[b][reverse][1] += sent; return sent
                at[a] += 1
            return 0
        bound = 1+sum(cap for _, _, cap in edges)
        while send(source, bound): pass
    return [i for i, depth in enumerate(level) if depth >= 0], [cap-row[1] for (_, _, cap), row in zip(edges, originals)]


def energy(value, bits):
    return sum(row[x] for row, x in zip(value['unary'], bits)) + sum(
        p['costs'][2*bits[p['i']]+bits[p['j']]] for p in value['pairs'])


def optimize(value):
    n, edges, constant = compile_costs(value)
    cut, flow = minimum_cut(n, edges); bits = [int(i not in cut) for i in range(n)]
    result = {'schema': 'binary-cut-certificate/v1', 'assignment': bits, 'energy': energy(value, bits),
              'constant': constant, 'source_side': cut, 'flow': flow}
    verify(value, result)
    return result


def verify(value, result):
    """Check flow feasibility and cut equality; do not run flow search."""
    n, edges, constant = compile_costs(value); source, sink = n, n+1
    require(type(result) is dict and result.get('schema') == 'binary-cut-certificate/v1', 'Invalid certificate')
    cut, flow, bits = result.get('source_side'), result.get('flow'), result.get('assignment')
    require(type(cut) is list and all(type(i) is int and 0 <= i < n+2 for i in cut)
            and len(cut) == len(set(cut)) and source in cut and sink not in cut, 'Invalid cut')
    require(type(bits) is list and len(bits) == n and all(type(x) is int and x in (0, 1) for x in bits)
            and bits == [int(i not in cut) for i in range(n)], 'Assignment differs from cut')
    require(all(x is None or bits[i] == x for i, x in enumerate(value['fixed'])), 'Fixed choice changed')
    require(type(flow) is list and len(flow) == len(edges), 'Incomplete flow')
    balance, cut_cost = [0]*(n+2), 0
    side = set(cut)
    for (a, b, cap), amount in zip(edges, flow):
        require(type(amount) is int and 0 <= amount <= cap, 'Flow exceeds capacity')
        balance[a] -= amount; balance[b] += amount
        if a in side and b not in side: cut_cost += cap
    require(all(x == 0 for x in balance[:n]) and balance[sink] == -balance[source] == cut_cost,
            'Flow is not a matching lower bound')
    require(type(result.get('constant')) is int and result['constant'] == constant
            and type(result.get('energy')) is int and result['energy'] == energy(value, bits) == constant+cut_cost,
            'Original cost differs from certificate')
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('problem'); parser.add_argument('--check')
    args = parser.parse_args(argv)
    try:
        value, digest = read(args.problem)
        if args.check:
            result, _ = read(args.check)
            require(type(result) is dict and result.get('input_sha256') == digest, 'Problem bytes changed')
            verify(value, result); print('PASS_BINARY_COST_OPTIMUM')
        else:
            result = optimize(value); result['input_sha256'] = digest
            print(json.dumps(result, indent=2, sort_keys=True))
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print(str(exc), file=sys.stderr); return 2
    return 0


if __name__ == '__main__': raise SystemExit(main())
