"""Reconstruct SOURCE77 from five prior values at its actual native frame.

The G20 word and native verifier are ai-nanachi's PR5512. The snapshot
identity follows Dugongue's PR5639. The new input is a sum of five prior
SOURCE versions. Ali Romman, with substantial OpenAI Codex assistance.
Apache-2.0.
"""
from collections import Counter
from pathlib import Path
from hashlib import sha256
import gzip
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'bit-g20-nine-owned-relations'
_spec = importlib.util.spec_from_file_location(
    'g20_affine_source_local', SOURCE/'local_relations.py')
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)

GATHERS = ((13187, 22), (14523, 33), (14587, 17),
           (14631, 77), (14647, 87))
FIRST, SOURCE_ADD, LAST = 16153, 19366, 19367


def need(ok, message):
    if not ok:
        raise ValueError(message)


def put(folder, name, value):
    raw = (json.dumps(value, indent=2) + '\n').encode()
    path = folder / name
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def construct():
    old = L.read(SOURCE / 'WORD.json.gz')
    word = old['records']
    need(word[FIRST] == ['Q', 444, 509, 79, 3], 'Pinned first return')
    need(word[SOURCE_ADD] == ['ADD', 444, 77, 79], 'Pinned late source add')
    need(word[LAST] == ['Q', 444, 79, 0, 1], 'Pinned final return')
    rows = [1 << i for i in range(660)]
    frames = list(old['start'])
    gathered, evidence = 0, []
    gathers = dict(GATHERS)
    for ix, event in enumerate(word):
        op, dst = event[:2]
        if op == 'ADD':
            src, frame = event[2:]
            need(frames[dst] == frames[src] == frame, 'Actual source frame')
            need(dst != 658, 'The old centre has no incoming data')
            if src == 658:
                need(rows[658] == 0, 'Every removed centre read is zero')
            rows[dst] ^= rows[src]
        elif op in ('ERASE', 'INIT'):
            rows[dst] = 0
            frames[dst] = event[2]
        else:
            need(op in ('Q', 'ZERO_Q'), 'Known source operation')
            if op == 'ZERO_Q':
                need(rows[dst] == 0, 'Old zero query is valid')
            frames[dst] = event[3]
        if ix in gathers:
            src = gathers[ix]
            need(frames[src] == 509, 'Gather has the declared current frame')
            gathered ^= rows[src]
            evidence.append({'event': ix, 'source': src,
                             'raw_terms': L.bitids(rows[src])})
        if FIRST < ix < LAST:
            need(not (op == 'ADD' and event[2] == 444), 'No intervening helper read')
            if dst == 444:
                need(ix == SOURCE_ADD, 'The only intervening helper update')
    need(gathered == 1 << 77, 'Five historical functions sum to SOURCE77')
    out = [['ERASE', 658, 509]]
    removed = Counter()
    for ix, event in enumerate(word):
        if event[1] == 658 or (event[0] == 'ADD' and event[2] == 658):
            removed[event[0]] += 1
            continue
        if ix == FIRST:
            out.extend((['ADD', 444, 658, 509], ['ERASE', 658, None],
                        ['Q', 444, 509, 0, 4]))
        elif ix in (SOURCE_ADD, LAST):
            removed[event[0]] += 1
        else:
            out.append(event)
        if ix in gathers:
            out.append(['ADD', 658, gathers[ix], 509])
    return dict(old, records=out), {'gathers': evidence,
                                  'removed_operations': dict(removed)}


def run(folder):
    word, evidence = construct()
    base, frames, _ = L.source()
    checks = [L.replay(base, frames, word['records'], set(word['owned']), m)
              for m in (None, 101, 101**2)]
    paid = {1: 1308, 2: 1342, 3: 76, 4: 41, 5: 102, 6: 10, 7: 9}
    need(all(x['paid'] == paid for x in checks), 'Derived new local invoice')
    need(checks[0]['owned_allocated'] == 11, 'No new owned bank')
    controls = {}
    bad = [e[:] for e in word['records']]
    bad.pop(next(i for i, e in enumerate(bad) if e == ['ADD', 658, 87, 509]))
    try:
        L.replay(base, frames, bad, set(word['owned']))
    except ValueError:
        controls['missing_gather'] = 'rejected'
    else:
        raise ValueError('An incomplete reconstruction passed')
    bad = [e[:] for e in word['records']]
    bad.pop(0)
    try:
        L.replay(base, frames, bad, set(word['owned']))
    except ValueError:
        controls['missing_dirty_clear'] = 'rejected'
    else:
        raise ValueError('An arbitrary dirty centre was accepted')
    bad = [e[:] for e in word['records']]
    event = next(e for e in bad if e == ['Q', 444, 509, 0, 4])
    event[-1] = 3
    try:
        L.replay(base, frames, bad, set(word['owned']))
    except ValueError:
        controls['underpriced_native_move'] = 'rejected'
    else:
        raise ValueError('An underpriced native move passed')
    result = {'status': 'PASS_G20_AFFINE_HISTORY_ALL660_NATIVE_COLUMNS',
              'stats': checks[0], 'native_controls': checks[1:],
              'semantic_controls': controls, 'evidence': evidence,
              'canonical_word_sha256': sha256(json.dumps(word['records'],
                  separators=(',', ':')).encode()).hexdigest()}
    put(folder, 'WORD.json.gz', word)
    put(folder, 'LOCAL-RESULT.json', result)
    return result
