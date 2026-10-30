#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Find and certify a minimum-cost reversible pebble schedule.

Classical reversible pebbling and Dijkstra shortest paths. Prepared for
Ali Romman with substantial OpenAI Codex assistance.
"""
import argparse
from hashlib import sha256
import heapq
import json
from pathlib import Path
import sys
from compare_recursive_invoices import _pairs, _integer, _not_integer, require


def read_json(path, limit):
    with Path(path).open('rb') as stream:
        raw = stream.read(limit + 1)
    require(len(raw) <= limit, 'JSON byte limit exceeded')
    return json.loads(raw, object_pairs_hook=_pairs, parse_int=_integer,
                      parse_float=_not_integer, parse_constant=_not_integer), sha256(raw).hexdigest()


def problem(value):
    require(type(value) is dict and value.keys() == {'schema', 'nodes', 'targets', 'space'}
            and value['schema'] == 'reversible-pebble-problem/v1', 'Invalid pebble problem')
    nodes, targets, space = value['nodes'], value['targets'], value['space']
    require(type(nodes) is list and 1 <= len(nodes) <= 16, 'Use 1..16 nodes')
    require(type(space) is int and 0 <= space <= 10**12, 'Invalid scratch budget')
    for i, node in enumerate(nodes):
        require(type(node) is dict and node.keys() == {'parents', 'width', 'compute', 'erase'}, 'Invalid node')
        parents = node['parents']
        require(type(parents) is list and all(type(p) is int and 0 <= p < i for p in parents)
                and len(parents) == len(set(parents)), 'Parents must be distinct earlier nodes')
        for key in ('width', 'compute', 'erase'):
            require(type(node[key]) is int and 1 <= node[key] <= 10**12, 'Invalid node ' + key)
    require(type(targets) is list and all(type(t) is int and 0 <= t < len(nodes) for t in targets)
            and len(targets) == len(set(targets)), 'Invalid targets')
    weights = [0] * (1 << len(nodes))
    for mask in range(1, len(weights)):
        bit = mask & -mask
        weights[mask] = weights[mask ^ bit] + nodes[bit.bit_length() - 1]['width']
    parents = [sum(1 << p for p in node['parents']) for node in nodes]
    target = sum(1 << t for t in targets)
    return nodes, space, weights, parents, target


def transitions(mask, nodes, space, weights, parents):
    for i, node in enumerate(nodes):
        if mask & parents[i] != parents[i]:
            continue
        after = mask ^ (1 << i)
        if weights[after] <= space:
            yield after, i, node['erase' if mask & (1 << i) else 'compute']


def plan(value):
    nodes, space, weights, parents, target = problem(value)
    distances, previous, queue = {0: 0}, {}, [(0, 0)]
    while queue:
        cost, state = heapq.heappop(queue)
        if distances[state] != cost:
            continue
        for after, node, charge in transitions(state, nodes, space, weights, parents):
            candidate = cost + charge
            if after not in distances or candidate < distances[after]:
                distances[after] = candidate
                previous[after] = (state, node)
                heapq.heappush(queue, (candidate, after))
    schedule, state = [], target
    if target in distances:
        while state:
            before, node = previous[state]
            schedule.append(node); state = before
        schedule.reverse()
    result = {'schema': 'reversible-pebble-certificate/v1',
              'status': 'optimal' if target in distances else 'infeasible',
              'cost': distances.get(target), 'schedule': schedule,
              'potential': {str(k): distances[k] for k in sorted(distances)}}
    verify(value, result)
    return result


def verify(value, certificate):
    """Check a closed state set and edge potentials, without shortest-path search."""
    nodes, space, weights, parents, target = problem(value)
    require(type(certificate) is dict and certificate.get('schema') == 'reversible-pebble-certificate/v1',
            'Invalid certificate')
    raw = certificate.get('potential')
    require(type(raw) is dict and 1 <= len(raw) <= len(weights), 'Invalid potential table')
    distances = {}
    for key, cost in raw.items():
        require(type(key) is str and key.isascii() and key.isdecimal() and len(key) <= 5
                and str(int(key)) == key and int(key) < len(weights), 'Invalid state key')
        require(type(cost) is int and cost >= 0 and weights[int(key)] <= space, 'Invalid state potential')
        distances[int(key)] = cost
    require(distances.get(0) == 0, 'Initial potential must be zero')
    # All edges of every claimed reachable state must stay in the certificate.
    for state, cost in distances.items():
        for after, _, charge in transitions(state, nodes, space, weights, parents):
            require(after in distances and distances[after] <= cost + charge, 'Missing state or false lower bound')
    if certificate.get('status') == 'infeasible':
        require(target not in distances and certificate.get('cost') is None
                and certificate.get('schedule') == [], 'False infeasibility claim')
        return True
    require(certificate.get('status') == 'optimal' and target in distances, 'Invalid status')
    schedule = certificate.get('schedule')
    require(type(schedule) is list and len(schedule) < len(weights), 'Invalid schedule')
    state, cost = 0, 0
    # Literal replay uses parent sets and widths, separate from transitions().
    live = set()
    for i in schedule:
        require(type(i) is int and 0 <= i < len(nodes), 'Invalid move')
        node = nodes[i]
        require(set(node['parents']) <= live, 'Missing parent in schedule')
        if i in live:
            live.remove(i); cost += node['erase']
        else:
            live.add(i); cost += node['compute']
        require(sum(nodes[j]['width'] for j in live) <= space, 'Schedule exceeds space')
        state ^= 1 << i
    require(state == target and type(certificate.get('cost')) is int
            and cost == certificate['cost'] == distances[target], 'Wrong endpoint or nonoptimal cost')
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem')
    parser.add_argument('--check', help='Check an existing certificate instead of searching')
    args = parser.parse_args(argv)
    try:
        value, digest = read_json(args.problem, 1024**2)
        if args.check:
            result, _ = read_json(args.check, 16 * 1024**2)
            require(type(result) is dict and result.get('input_sha256') == digest, 'Problem bytes changed')
            verify(value, result)
            print('PASS_REVERSIBLE_PEBBLE_CERTIFICATE')
        else:
            result = plan(value); result['input_sha256'] = digest
            print(json.dumps(result, sort_keys=True, indent=2))
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print(str(exc), file=sys.stderr); return 2
    return 0


if __name__ == '__main__': raise SystemExit(main())
