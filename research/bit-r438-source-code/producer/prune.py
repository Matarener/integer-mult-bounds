#!/usr/bin/env python3
"""Delete nine literally unread physical families from the source-coded word.

All removed indices are arbitrary dirty inputs, never read in either direction.
No global controller or conditional kappa is certified here.
"""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE  # bound to fresh support-code output
sys.dont_write_bytecode = True
import bit_transvection as base
import bit_scalar_invoice as scalar


def need(ok, text):
    if not ok:
        raise ValueError(text)


def project(records, dead):
    used = set()
    for op, dst, src, coefficient, frame, phase in records:
        if op == 1:
            used.add(src)
        elif op in (2, 3):
            used.add(dst)
    need(not (used & dead), 'Deleted family is read')
    keep = [i for i in range(661) if i not in dead]
    renumber = {old: new for new, old in enumerate(keep)}
    result = []
    removed = []
    for rec in records:
        op, dst, src, coefficient, frame, phase = rec
        if dst in dead:
            need(op in (0, 1), 'Unexpected deleted-family operation')
            removed.append(rec[:])
            continue
        new = rec[:]
        new[1] = renumber[dst]
        if op in (1, 2, 3):
            new[2] = renumber[src]
        result.append(new)
    return keep, renumber, result, removed


def authenticate_predecessor(packed):
    raise ValueError('Use reconstruct.py to authenticate the regenerated support word')


def main():
    blob = (SOURCE / 'BIT-SUPPORT-WORD.json.gz').read_bytes()
    authenticate_predecessor(blob)
    word = json.loads(gzip.decompress(blob))
    meta = json.loads((SOURCE / 'BIT-SUPPORT.json').read_text())
    dead = set(range(471, 480))
    original, builder, baseline, _ = base.load()
    keep, renumber, records, removed = project(word['records'], dead)
    need(renumber[660] == 651, 'Wrong private remap')
    negative = word['records'] + [[1, 0, 471, 1, 1, 99]]
    try:
        project(negative, dead)
    except ValueError:
        pass
    else:
        raise ValueError('Read-dead-family negative control escaped')
    new_original = dict(original, R=429,
                        start=[f for i, f in enumerate(word['start']) if i not in dead],
                        final=[f for i, f in enumerate(word['final']) if i not in dead])
    ff = base.replay(new_original, builder, records, meta['matrices'])
    bf = base.replay(new_original, builder, records, meta['matrices'], reverse=True)
    removed_profile = Counter(r[4] for r in removed if r[0] == 0)
    need(removed_profile == {1: 27, 5: 9}, 'Removed profile differs')
    need(sum(r[0] == 1 for r in removed) == 72, 'Removed scalar count differs')
    need(ff['rank_mass'] == bf['rank_mass'] == 4989, 'Wrong complete bill')
    scalar.N = 660
    old_f, old_fs = scalar.execute(word['records'], scalar.eye(660))
    old_b, old_bs = scalar.execute(word['records'], scalar.eye(660), reverse=True)
    scalar.N = 651
    f, fs = scalar.execute(records, scalar.eye(651))
    b, bs = scalar.execute(records, scalar.eye(651), reverse=True)
    rt, rts = scalar.execute(records, f, reverse=True)
    need(rt == scalar.eye(651), 'Integer literal inverse failed')
    for actual, ancestor in ((f, old_f), (b, old_b)):
        need(actual == [[row[j] for j in keep[:-1]] for i, row in enumerate(ancestor) if i not in dead], 'Projected integer endpoint differs')
    need(fs['maximum_exact_prefix_row_l1'] == old_fs['maximum_exact_prefix_row_l1'] and
         bs['maximum_exact_prefix_row_l1'] == old_bs['maximum_exact_prefix_row_l1'], 'Prefix maximum differs')
    container = dict(word, format='coded-r429-pruned-three-source-copy-v1',
                     public_registers=651, private_register=651,
                     start=new_original['start'], final=new_original['final'], records=records,
                     copy_schema='[2,physical_source,651,sourceframe,privateframe,rank]',
                     erase_schema='[3,physical_source,651,sourceframe,privateframe,0]')
    container['parent_word_gzip_sha256'] = hashlib.sha256(blob).hexdigest()
    container['deleted_public_families'] = sorted(dead)
    payload = base.canonical(container)
    packed = gzip.compress(payload, mtime=0)
    (HERE / 'BIT-PRUNED-WORD.json.gz').write_bytes(packed)
    out = dict(status='PASS_LITERAL_DEAD_FAMILY_PROJECTION_NO_GLOBAL_KAPPA',
               parent_gzip_sha256=hashlib.sha256(blob).hexdigest(),
               word_gzip_sha256=hashlib.sha256(packed).hexdigest(),
               word_canonical_sha256=hashlib.sha256(payload).hexdigest(),
               deleted_public_families=sorted(dead), old_public_indices=keep[:-1],
               removed_MOVE_profile=dict(removed_profile), removed_ADDs=72,
               source_code_unchanged=True, target_integer_map_projected_exactly=True,
               original_rank_mass=5121, final_rank_mass=4989, saving_per_local_call=132,
               scalar_ADDs=sum(r[0] == 1 for r in records),
               forward_frames=ff, reverse_frames=bf,
               integer_forward=fs, integer_reverse=bs, integer_roundtrip=rts,
               controls={'read_deleted_family_rejected': True},
               scope='All651 independent integer and F2 inputs; original public paths restricted to retained families; arbitrary429 dirty helpers restored. No global terminal, stock, precision, complex supplier or conditional kappa admission.')
    (HERE / 'BIT-PRUNED.json').write_text(json.dumps(out, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: out[k] for k in ('status','word_gzip_sha256','word_canonical_sha256','scalar_ADDs','saving_per_local_call')}))


if __name__ == '__main__':
    main()
