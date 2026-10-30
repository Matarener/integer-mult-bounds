"""Semantic rejecting controls; explicit exceptions survive python -O."""
import copy
import json
import tempfile
from pathlib import Path
import verify
from frames import compile_frames


def rejected(fn, label):
    try:
        fn()
    except (ValueError, verify.audit.AuditFailure):
        return
    raise RuntimeError('control accepted: ' + label)


def main():
    source, recipe, target = verify.load_inputs()
    bad = copy.deepcopy(recipe)
    bad['warp_edits'][0]['old'][0] = []
    rejected(lambda: compile_frames(source, bad), 'old frame guard')
    bad = copy.deepcopy(recipe)
    bad['warp_edits'][0]['new'][1] = []
    rejected(lambda: compile_frames(source, bad), 'wrong transported image')
    bad = copy.deepcopy(target)
    i = next(i for i, g in enumerate(bad['B']) if g[:1] == ['scale'] and g[2:4] == [1, 1])
    del bad['B'][i]
    for rec in bad['warps']:
        if rec[0] > i:
            rec[0] -= 1
    rejected(lambda: verify.check(bad, full=False), 'omitted paid climb')
    bad = copy.deepcopy(target)
    bad['report']['local_profile']['1'] += 1
    rejected(lambda: verify.check(bad, full=False), 'false profile')
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / 'INPUTS.json').write_text(json.dumps({'x': '0' * 64}))
        (root / 'x').write_bytes(b'changed')
        rejected(lambda: verify.load_inputs(root), 'changed source')
    print('PASS_5_SEMANTIC_REJECTION_CONTROLS')


if __name__ == '__main__':
    main()
