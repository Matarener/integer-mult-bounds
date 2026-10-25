#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bind the submitted complex moves to the existing exact operator obstruction.

Credit Nick Petalas/PR3187 for the operator, Matarener/PR3296 for the
remainder replay, and Erwan's PR4046 for binding it to the PR3955 chain.
This is a new source binding, not an independent operator implementation.
Substantial OpenAI assistance.
"""
from pathlib import Path
from hashlib import sha256
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT/'research/pr3190-remainder-stream-obstruction'))
import obstruction as O


def main():
    pins = json.loads((HERE/'WITNESS-SOURCES.json').read_text())
    for name, expected in pins.items():
        O.S.require(sha256((ROOT/name).read_bytes()).hexdigest() == expected, 'review source pin: '+name)
    path = ROOT/'research/kappa-next-regime/sources/PR3959/research/rank7-idle-frame-select/MOVES.json.gz'
    raw = path.read_bytes()
    O.S.require(sha256(raw).hexdigest() == '01e8417b90783f707cd18871be7c615eb9162f356460f07963b5198522aa692b', 'exact PR3955 MOVES')
    data = json.loads(gzip.decompress(raw))
    moves = [(d, r, int(a)) for owner, port, d, r, a in data['moves'] if owner == port == 0]
    O.S.require((14, 8, O.AXIS72) in moves and (15, 10, O.AXIS72) in moves, 'retained witness')
    # load_context authenticates and hashes the full fill, then projects owner 0/port 0.
    ctx = O.S.load_context()
    residual, hosts = O.residual_and_hosts(ctx)
    blocks = O.A.stage_blocks(ctx['template'])
    before = O.replay(ctx, blocks, hosts, residual, O.AXIS72)
    O.S.require(before == O.scalar(O.AXIS72), 'baseline scalar operator')
    # Use EVERY move in this port, not an isolated subset of the submission.
    final = O.apply_moves(ctx['recipe'], residual, moves)
    after = O.replay(ctx, blocks, hosts, final, O.AXIS72)
    changes = O.diff(before, after)
    O.S.require(len(changes) == 10, 'ten changed exact matrix entries')
    empty = O.apply_moves(ctx['recipe'], residual, [])
    O.S.require(O.replay(ctx, blocks, hosts, empty, O.AXIS72) == before, 'empty overlay control')
    rejected = []
    for name, bad in [('self-move', [(14, 14, O.AXIS72)]), ('absent-axis', [(14, 8, 1 << 200)])]:
        try:
            O.apply_moves(ctx['recipe'], residual, bad)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('control accepted: '+name)
    print(json.dumps(dict(status='CONFIRMED_COMPLEX_OPERATOR_OBSTRUCTION', owner=0, port=0,
        character=str(O.AXIS72), complete_port_move_count=len(moves), changed_entries=changes,
        empty_overlay_preserves_operator=True, rejecting_controls=rejected,
        scope='Exact submitted PR3955 moves at owner 0/port 0 under the retained literal frame and unchanged invocation contract; does not exclude repaired schedules or new hosted maps.'), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
