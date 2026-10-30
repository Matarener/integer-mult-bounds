"""Exact finite certificate for the new descendant circuit; no new kappa.

Produced by Nick Petalas. Apache-2.0. Standard library only.
"""
import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import platform
import sys
import time

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_hashes():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    hashes = {}
    require(len(sources['files']) <= 16, 'source inventory bound')
    for row in sources['files']:
        if row['usage'] == 'input':
            digest = hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
            require(digest == row['sha256'], 'changed source: ' + row['path'])
            hashes[row['path']] = digest
    for path in sorted(PACKAGE.iterdir()):
        if path.is_file():
            hashes[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def triple_masks():
    return tuple(sum(1 << point for point in triple)
                 for triple in combinations(range(22), 3))


def check_dag(circuit):
    inputs = triple_masks()
    require(tuple(circuit.inputs) == inputs, 'input order changed')
    require(set(circuit.outputs) == set(inputs), 'output index set changed')
    require(len(circuit.support) == len(circuit.args) <= 41441, 'node bound')
    nodes = sorted(circuit.active)
    require(len(nodes) == 32216, 'active node count changed')
    actual, additions = {}, 0
    for node in nodes:
        require(1 <= node < len(circuit.args), 'invalid active node')
        pair = circuit.args[node]
        if node <= len(inputs):
            require(pair is None, 'source has an addition')
            value = 1 << (node - 1)
        else:
            require(isinstance(pair, tuple) and len(pair) == 2, 'invalid addition')
            left, right = pair
            require(left in actual and right in actual, 'acyclic ancestor missing')
            require(not actual[left] & actual[right], 'overlapping integer coefficients')
            value = actual[left] | actual[right]
            additions += 1
        require(value == circuit.support[node], 'cached support disagrees with literal DAG')
        actual[node] = value
    require(additions == circuit.additions == 30676, 'addition count changed')
    for target in inputs:
        expected = sum(1 << index for index, source in enumerate(inputs)
                       if source & target == 0)
        require(actual[circuit.outputs[target]] == expected, 'wrong integer output coefficient')
    return {'additions': additions, 'inputs': len(inputs), 'outputs': len(inputs),
            'coefficient_positions': len(inputs) ** 2,
            'nonzero_coefficients': len(inputs) * comb(19, 3)}


def check_embedding(circuit, code):
    require(code['roles'] == 32216, 'compiled role count changed')
    values = [0] * code['roles']
    inputs = triple_masks()
    positions = {source: index for index, source in enumerate(inputs)}
    require(set(code['sources']) == set(inputs), 'compiled sources missing')
    require(set(code['outputs']) == set(inputs), 'compiled outputs missing')
    for source, slot in code['sources'].items():
        require(0 <= slot < len(values) and values[slot] == 0, 'source slot collision')
        values[slot] = 1 << positions[source]
    require(len(code['gates']) == 32216, 'compiled gate bound')
    for node, ins, outs in code['gates']:
        require(ins and outs and ins[0] == outs[0], 'missing shared pivot')
        require(len(set(ins)) == len(ins) and len(set(outs)) == len(outs), 'slot alias')
        require(set(ins) & set(outs) == {ins[0]}, 'extra input/output alias')
        require(all(0 <= slot < len(values) for slot in ins + outs), 'slot bound')
        for slot in ins[1:]:
            require(not values[ins[0]] & values[slot], 'embedded coefficients overlap')
            values[ins[0]] |= values[slot]
        require(values[ins[0]] == circuit.support[node], 'embedded node differs')
        for slot in outs[1:]:
            require(values[slot] == 0, 'fanout target is not fresh')
            values[slot] = values[ins[0]]
    for target, slot in code['outputs'].items():
        require(values[slot] == circuit.support[circuit.outputs[target]], 'embedded output differs')
    additions = sum(len(ins) + len(outs) - 2 for _, ins, outs in code['gates'])
    require(additions == 61352, 'literal disjoint mixer charge changed')
    return {'roles': code['roles'], 'gates': len(code['gates']),
            'physical_scalar_additions': additions,
            'all_integer_coefficient_positions_checked': True}


def dirty_inverse(code):
    original = [(index * 37 % 101) - 50 for index in range(code['roles'])]
    values = original.copy()
    for _, ins, outs in code['gates']:
        values[ins[0]] += sum(values[slot] for slot in ins[1:])
        for slot in outs[1:]:
            values[slot] += values[ins[0]]
    for _, ins, outs in reversed(code['gates']):
        for slot in outs[1:]:
            values[slot] -= values[ins[0]]
        values[ins[0]] -= sum(values[slot] for slot in ins[1:])
    require(values == original, 'literal integer inverse failed on dirty roles')
    return {'dirty_integer_roundtrips': 1, 'dirty_roles': len(values)}


def invoice(additions):
    h, v, m = 22, comb(22, 3), 22 ** 3
    side = additions + v + comb(h, 2) * (4 * (h - 2) - 6)
    mixer = 2 * additions + 2 * comb(h, 2) * (3 * (h - 2) - 6)
    accesses = injections = 4 * v
    invocation = 4 * mixer + 2 * accesses + 4 * injections + 18 * v
    steps = 3 * v * v * invocation
    width = 2 * v ** 3 + 2 * v * v * (side + h + 1)
    lost = 3 * v * v * h * (h + 1)
    rank = width * m - 2 * v ** 3 + 2 * lost
    error_budget = 64 * (width + m + 1) ** 3
    require(2 <= rank < m ** 5, 'stopped recurrence rank guard')
    require(4 * steps + 8 * rank + 8 * width + 8 * m < error_budget, 'node charge guard')
    return {'side_roles': side, 'centres': h + 1, 'mixer_additions': mixer,
            'source_accesses': accesses, 'weighted_injections': injections,
            'signed_invocation_steps': invocation, 'three_stage_steps': steps,
            'W': width, 'm': m, 'L': lost, 's': rank, 'E': error_budget,
            'fixed_deficit': width * m - rank}


def rejected(action, message):
    try:
        action()
    except (ValueError, KeyError, IndexError):
        return
    raise ValueError('control survived: ' + message)


def controls(circuit, code):
    target = next(iter(circuit.outputs))
    saved = circuit.outputs[target]
    try:
        circuit.outputs[target] = 1
        rejected(lambda: check_dag(circuit), 'wrong final coefficient')
    finally:
        circuit.outputs[target] = saved
    node = next(node for node in sorted(circuit.active) if circuit.args[node])
    saved_pair, saved_support = circuit.args[node], circuit.support[node]
    try:
        circuit.args[node] = (saved_pair[0], saved_pair[0])
        rejected(lambda: check_dag(circuit), 'duplicated summand')
        circuit.args[node] = (node, saved_pair[1])
        rejected(lambda: check_dag(circuit), 'cycle')
        circuit.args[node] = saved_pair
        circuit.support[node] ^= 1
        rejected(lambda: check_dag(circuit), 'cached support corruption')
    finally:
        circuit.args[node], circuit.support[node] = saved_pair, saved_support
    saved_roles = code['roles']
    try:
        code['roles'] -= 1
        rejected(lambda: check_embedding(circuit, code), 'missing paid role')
    finally:
        code['roles'] = saved_roles
    gate = next(index for index, (_, ins, _) in enumerate(code['gates']) if len(ins) == 2)
    saved_gate = code['gates'][gate]
    try:
        n, ins, outs = saved_gate
        code['gates'][gate] = (n, ins, (outs[0], outs[0]))
        rejected(lambda: check_embedding(circuit, code), 'fanout alias')
    finally:
        code['gates'][gate] = saved_gate
    return 6


def main():
    started = time.monotonic()
    hashes = source_hashes()
    sys.path.insert(0, str(PACKAGE))
    from construction import DescendantCircuit
    circuit = DescendantCircuit()
    dag = check_dag(circuit)
    code = circuit.compile()
    embedded = check_embedding(circuit, code)
    inverse = dirty_inverse(code)
    frames = circuit.verify_frames()
    require(frames['orientations'] == 2 and frames['all_physical_transitions_checked'],
            'both physical frame orientations required')
    count = controls(circuit, code)
    # A control restores every mutation before the final successful replay.
    check_dag(circuit)
    check_embedding(circuit, code)
    bill = invoice(dag['additions'])
    require(bill['signed_invocation_steps'] == 409880, 'complete scalar bill changed')
    require(bill['three_stage_steps'] == 2916214224000, 'complete tensor bill changed')
    report = {'claim_type': 'finite certificate', 'no_new_kappa': True,
              'python': platform.python_version(), 'platform': platform.platform(),
              'dag': dag, 'embedding': embedded, 'inverse': inverse, 'frames': frames,
              'invoice': bill, 'rejecting_controls': count,
              'source_sha256': hashes, 'elapsed_seconds': time.monotonic() - started}
    print(json.dumps(report, sort_keys=True))
    print('PASS_DISJOINT_DESCENDANT_TRAVERSAL additions=30676 roles=32216 no_new_kappa')


if __name__ == '__main__':
    main()
