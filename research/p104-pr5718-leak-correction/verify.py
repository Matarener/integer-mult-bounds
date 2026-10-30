#!/usr/bin/env python3
"""Verify the mid-word leak-correction census on the PR6030 and PR5907 P104 words.  Apache-2.0.

Python 3.12, standard library only.  Checks:
 (0) pinned input bytes (the PR6040 census module and the three words);
 (1) the re-run class census equals PR6040's own census counts on both words;
 (2) every leak class has a nonzero retired value row_p(i); carrier mode: on both words no leak class has a single carrier source (a field whose original value is zero
     while carrying the pivot's cut content), so every leak class is 'unreachable' by carrier corrections;
 (3) the z-part-only screen (PR6040's r += q*new) on the PR6030 leak-1 classes: it reports z-part witnesses, and
     the direct simulator confirms for the first three single corrections that the z-leak is cleared while a non-z
     defect remains on an O output (the exact lemma in README.md);
 (4) planted positive control on the PR5713 word: a carrier and a leak planted after PR5718's own split cut; carrier
     mode finds the single correction and the direct simulator accepts it with no defect outside V; a perturbed
     coefficient is rejected;
 (5) RESULT.json equals the recomputed receipt.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip, io, json, sys, tarfile, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SHAPESPLIT_SHA256 = '11e8ef691b28fb4f401a8c2e97b6d462e7a004f0e215a28579d6a654b4ca3304'   # PR6040 head 1889253f, git blob 6eedc849
if sha256((HERE/'inputs'/'shapesplit.py').read_bytes()).hexdigest() != SHAPESPLIT_SHA256:
    raise SystemExit('pinned PR6040 shapesplit.py does not match')   # checked before any imported code runs
sys.path.insert(0, str(HERE))
import leakfix as L      # noqa: E402
import check as K        # noqa: E402

W6030 = 'research/p104-helper470-twin-rung-removal/WORD.json.gz'
W5907 = 'research/p104-helper468-rung-removal/WORD.json.gz'
TAR5713 = 'research/p104-two-boundary-helper-split/inputs/pr5713-source.tar'
MEMBER5713 = 'research/p104-temporal-updates/WORD.json.gz'
need = L.need


def pins():
    src = json.loads((HERE/'SOURCES.json').read_text())
    for row in src['files']:
        need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'pin ' + row['path'])
    with tarfile.open(ROOT/TAR5713) as tar:
        w5713 = json.loads(gzip.decompress(tar.extractfile(MEMBER5713).read()))
    return L.SS.read(ROOT/W6030), L.SS.read(ROOT/W5907), w5713


def carrier_summary(w):
    classes, _ = L.leak_classes(w)
    need(all(c['row_p'] for c in classes if c['kind'] == 'leak'), 'retired value row_p(i) nonzero in every leak class')
    counts, res, iv = L.run(w, mode='carrier')
    ref = L.SS.census(w, 'empty')[0]
    need(counts == ref, 'class census equals PR6040 census')
    need(all(r['sources'] == 0 for r in res), 'no carrier source in any leak class')
    need(all(r['kind'] == 'unreachable' for r in res), 'every leak class unreachable by carrier corrections')
    return {'pr6040_counts': counts, 'leak_classes': len(res),
            'leak_classes_by_leak_count': {str(k): v for k, v in sorted(Counter(r['leak'] for r in res).items())},
            'carrier_sources': sum(r['sources'] for r in res), 'kinds': dict(Counter(r['kind'] for r in res))}


def purez_screen(w):
    counts, res, iv = L.run(w, mode='purez', select=lambda c: c['leak'] == 1)
    kinds = dict(sorted(Counter(r['kind'] for r in res).items()))
    singles = [r for r in res if r['single'] and r['kind'] == 'witness']
    demos = []
    for r in singles[:3]:
        corr = [r['single']]
        z_only = K.check(w, r['cut_after'], r['pivot'], corr, full=False, pure_sources=True)
        need(z_only['O_nonz_defect_after'], 'pure-z correction leaves a non-z defect on O')
        try:
            K.check(w, r['cut_after'], r['pivot'], corr, full=True, pure_sources=True)
            raise AssertionError('full check unexpectedly passed')
        except ValueError as exc:
            need(str(exc) == 'no non-z defect on O outputs', 'full check fails on the non-z defect')
        demos.append({'cut_after': r['cut_after'], 'pivot': r['pivot'], 'correction': r['single'],
                      'z_leak_before': z_only['z_leak_before'], 'O_nonz_defect_after': z_only['O_nonz_defect_after']})
    need(len(demos) == 3, 'three pure-z demonstrations')
    return {'classes': len(res), 'kinds': kinds, 'single_corrections': sum(1 for r in res if r['single']),
            'single_and_pairing_witness': len(singles), 'demonstrations': demos}


def planted(w):
    """PR5713 word with, after PR5718's cut (event 14330, chart 602, helper 708): INIT s; s += p; [cut]; s -= p;
    o += p for the O role o = 128 at chart 602.  s is a carrier (original 0, carries -p) and o leaks."""
    w = json.loads(json.dumps(w))
    n, m = w['public'], w['owned_fields']; s, p, o, F = n + m, 708, 128, 602
    plant_pre = [['INIT', s, F], ['ADD', s, p, '1', F]]
    plant_post = [['ADD', s, p, '-1', F], ['ADD', o, p, '1', F], ['CLEAR', s, F]]
    prog = w['program']
    w['program'] = prog[:14331] + plant_pre + plant_post + prog[14331:]
    w['owned_fields'] = m + 1
    return w, 14332, p, o


def control(w5713):
    base = L.SS.census(w5713, 'empty')[0]
    need(base['witnesses'] == 7, 'PR6040 calibration on PR5713 (7 witnesses)')
    w, cut, p, o = planted(w5713)
    counts, res, iv = L.run(w, mode='carrier', select=lambda c: (c['cut_after'], c['pivot']) == (cut, p))
    need(len(res) == 1 and res[0]['leak'] >= 1, 'planted class leaks')
    r = res[0]
    need(r['kind'] == 'witness' and r['single'] and r['single']['target'] == o, 'carrier mode finds the planted fix')
    full = K.check(w, cut, p, [r['single']], full=True)
    need(not full['O_nonz_defect_after'] and full['z_leak_before'], 'planted fix: leak before, no defect after')
    bad = dict(r['single']); bad['mu'] = str(L.Q(bad['mu']) * 2)
    try:
        K.check(w, cut, p, [bad], full=True)
        raise AssertionError('perturbed correction accepted')
    except ValueError:
        pass
    return {'class': {'cut_after': cut, 'frame': r['frame'], 'pivot': p, 'leak': r['leak'], 'kind': r['kind']},
            'correction': r['single'], 'z_leak_before': full['z_leak_before'], 'perturbed_rejected': True}


def main():
    t0 = time.time()
    w6030, w5907, w5713 = pins()
    need(len(w6030['program']) == 22803 and len(w5907['program']) == 25998, 'word sizes')
    print('pins ok', flush=True)
    out = {'schema': 'p104-pr5718-leak-correction/v1'}
    out['pr6030_carrier'] = carrier_summary(w6030); print('PR6030 carrier', out['pr6030_carrier']['kinds'], flush=True)
    out['pr5907_carrier'] = carrier_summary(w5907); print('PR5907 carrier', out['pr5907_carrier']['kinds'], flush=True)
    out['pr6030_purez_leak1'] = purez_screen(w6030); print('PR6030 pure-z leak-1', out['pr6030_purez_leak1']['kinds'], flush=True)
    out['planted_control'] = control(w5713); print('planted control', out['planted_control']['correction'], flush=True)
    text = json.dumps(out, indent=1, sort_keys=True) + '\n'
    if '--write' in sys.argv:
        (HERE/'RESULT.json').write_text(text)
    need((HERE/'RESULT.json').read_text() == text, 'RESULT.json equals the recomputed receipt')
    print('PASS_P104_PR5718_LEAK_CORRECTION (%.0f s)' % (time.time() - t0))


if __name__ == '__main__':
    main()
