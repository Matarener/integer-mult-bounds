#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent two-queue reconstruction of PR3815's stage-1 supply throttle.

The published implementation scans a pending list. This checker keeps only
each replica's next call and orders admissible calls by original list position.
It does not import clock.py or the published verifier.
"""
import argparse
import hashlib
import heapq
import json
from pathlib import Path

P = Path(__file__).resolve().parent
S = P / 'sources/PR3815/research'


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct(original):
    positions = {tuple(call): i for i, call in enumerate(original)}
    replicas = 1 + max(r for _, r in original)
    stages = 1 + max(s for s, _ in original)
    assert len(positions) == len(original) == replicas * stages
    assert set(positions) == {(s, r) for s in range(stages) for r in range(replicas)}
    ordinary = [(positions[(0, r)], 0, r) for r in range(replicas)]
    heapq.heapify(ordinary)
    throttled = []
    closed = 0
    result = []
    for tick in range(len(original)):
        allow_stage1 = 224 * (closed + 1) <= 53 * (tick + 1)
        use_throttled = (allow_stage1 and throttled and
                         (not ordinary or throttled[0] < ordinary[0]))
        queue = throttled if use_throttled else ordinary
        assert queue, ('no admissible call', tick)
        _, stage, replica = heapq.heappop(queue)
        result.append([stage, replica])
        closed += stage == 1
        if stage + 1 < stages:
            next_stage = stage + 1
            destination = throttled if next_stage == 1 else ordinary
            heapq.heappush(destination,
                           (positions[(next_stage, replica)], next_stage, replica))
    assert not ordinary and not throttled
    return result


def prefix_shortage(order):
    closed = 0
    maximum = (0, -1)
    for tick, (stage, _) in enumerate(order):
        closed += stage == 1
        shortage = 224 * closed - 53 * (tick + 1)
        maximum = max(maximum, (shortage, tick))
    return {'width7_deficit': maximum[0], 'last_tick_attaining_maximum': maximum[1]}


def check():
    original_path = S / 'staged544-producer-return/inputs/ORDER.json'
    changed_path = S / 'staged544-clock-ceiling/inputs/ORDER.json'
    original, changed = read(original_path), read(changed_path)
    rebuilt = reconstruct(original)
    assert rebuilt == changed, 'published order differs from independent reconstruction'
    positions = {tuple(call): i for i, call in enumerate(original)}
    differences = [i - positions[tuple(call)] for i, call in enumerate(changed)]
    assert sum(d != 0 for d in differences) == 727
    assert max(differences) == 114 and min(differences) == -36
    for replica in range(360):
        assert [s for s, r in changed if r == replica] == list(range(9))
    assert prefix_shortage(changed)['width7_deficit'] == 0
    assert prefix_shortage(original)['width7_deficit'] > 0
    assert reconstruct(changed) == changed, 'throttle must be idempotent'
    # Concrete controls: the predecessor fails equality and a stage inversion
    # fails the independent per-replica projection check.
    assert original != rebuilt
    mutant = [x[:] for x in changed]
    i, j = next(i for i, x in enumerate(mutant) if x == [0, 0]), next(
        i for i, x in enumerate(mutant) if x == [1, 0])
    mutant[i], mutant[j] = mutant[j], mutant[i]
    assert [s for s, r in mutant if r == 0] != list(range(9))
    return dict(
        status='PASS_INDEPENDENT_STAGE1_CLOCK_RECONSTRUCTION',
        source_commit='77ffbf287b6ca198b4a31e3835db3bae60718b93',
        original_sha256=digest(original_path), changed_sha256=digest(changed_path),
        calls=len(changed), replicas=360, moved_calls=sum(d != 0 for d in differences),
        maximum_delay=max(differences), maximum_advance=-min(differences),
        original_prefix_shortage=prefix_shortage(original),
        changed_prefix_shortage=prefix_shortage(changed),
        controls=['predecessor_is_not_rebuilt_clock', 'same_replica_stage_inversion'],
        clock_source='PR3815 by Erwan Secousses; value priority PR3802 by hexapode',
        scope='Schedule only; physical ownership and complete price checked separately.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    assert __debug__, 'assertions required'
    result = check()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'])
