#!/usr/bin/env python3
"""Literal agreeing-consumer capture with a paid rollback before production.

This addresses PR4061's named 600/601 partial-capture interface on the actual
valid adaptive base word. It does not remove either helper. Substantial
OpenAI assistance; Apache-2.0; inherited supplier/checker credits preserved.
"""
from argparse import ArgumentParser
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import json
from pathlib import Path
from matched_basis import ROOT, OLD, PREVIOUS, F, O, coalesce, canonical, replay, expected, trace


def main():
    p = ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if not args.output.is_absolute():
        p.error('--output must be absolute and fresh')
    args.output.mkdir(parents=True, exist_ok=False)
    source = OLD/'candidate/BORROW-WORD-43base.json.gz'
    word = F.read(source)
    assert replay(word)[0] == expected(word)
    group, frame = (600, 601), [45]
    assert all(word['start_extra'][str(r)] == frame for r in group)
    events = F.expand(word)['B']
    first_write = min(i for i,e in enumerate(events) if e[1] in group)
    early = [i for i,e in enumerate(events[:first_write]) if e[0] == 'add' and e[2] in group]
    assert len(early) == 8 and early == list(range(early[0], early[-1]+1))
    assert all(events[i][-1] == frame and 112 <= events[i][1] < 224 for i in early)
    changed = deepcopy(word)
    changed['A'].append(['add', 600, 601, 1, 1, frame])
    reads = []
    for i in early:
        e = events[i]
        reads.append(deepcopy(e))
        if e[2] == 600:
            reads.append(['add', e[1], 601, -e[3], e[4], frame])
    reads = coalesce(reads)
    assert len(reads) == 6
    replacements = events[:early[0]] + reads + [['add',600,601,-1,1,frame]] + events[early[-1]+1:]
    changed['B'] = []
    for e in replacements:
        if e[0] == 'warp':
            changed['warps'][e[2]-1][0] = len(changed['B'])
        else:
            changed['B'].append(e)
    F.derive_cleanup(changed)
    assert replay(changed)[0] == expected(changed)
    optimized, info = O.optimize(changed)
    assert replay(optimized)[0] == expected(optimized)
    before, _ = trace(word)
    after, _ = trace(optimized)
    assert before == after and abs(info['saving']) < 1e-9
    def additions(w):
        return sum(e[0] == 'add' for sec in ('precondition','compensation','A','cut','B','restore','cleanup') for e in w.get(sec,[]))
    delta = additions(optimized)-additions(word)
    assert delta == 2
    payload = canonical(optimized)
    (args.output/'WORD.json.gz').write_bytes(gzip.compress(payload, mtime=0))
    paths = [source, Path(__file__), Path(__file__).with_name('matched_basis.py'), OLD/'fanout_search.py',
             OLD/'opt_frames.py', PREVIOUS/'exact_rows.py', PREVIOUS/'commute_birth.py']
    result = {'status': 'EXACT_PARTIAL_CAPTURE_WITH_ROLLBACK_PROFILE_TIE', 'group': group, 'frame': frame,
              'original_read_events': [events[i] for i in early], 'captured_read_events': reads,
              'entrance': ['add',600,601,1,1,frame], 'rollback': ['add',600,601,-1,1,frame],
              'operator': {'all_independent_inputs': 632, 'all_private_zero_buffers': 91,
                           'exact_free_warp_signed_rows': True, 'before_and_after_joint_frames': True},
              'joint_frames': info, 'local_profile': dict(sorted(after.items())),
              'helper_inventory_change': 0, 'scalar_ADD_delta_including_cleanup': delta,
              'paid_child_profile_change': {}, 'native_caller_build': False,
              'native_build_reason': 'Exact legal-frame candidate has no child saving and two extra scalar ADDs.',
              'payload_sha256': sha256(payload).hexdigest(), 'new_kappa': False,
              'source_sha256': {str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest() for path in paths},
              'scope': 'An explicit partial agreeing-consumer capture with rollback before production; not a universal partial-interface obstruction.'}
    (args.output/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
