#!/usr/bin/env python3
"""Independent review replay for the G20 BIT chain PR5679 / PR5708.

Authenticates every live input, runs four from-scratch checkers (none imports package code)
on both packages, runs negative controls on PR5708 and compares every result with RESULT.json.
`--write` regenerates RESULT.json. Matarener, with substantial Anthropic Claude assistance. Apache-2.0.
"""
from hashlib import sha256
from pathlib import Path
import json, subprocess, sys

H = Path(__file__).resolve().parent
ROOT = H.parent.parent
PKGS = {'PR5679': 'research/g20-helper-split', 'PR5708': 'research/g20-conjugation-admission'}
FRAMES = 'research/g20-conjugation-admission/prior/prior/prior/source/vendor/g20/inputs/FRAMES.json'


def need(ok, msg):
    if not ok:
        raise SystemExit('FAIL: ' + msg)


def run(script, *args, timeout=300):
    r = subprocess.run([sys.executable, '-I', '-B', str(H / script), *map(str, args)],
                       cwd=ROOT, capture_output=True, text=True, timeout=timeout)
    need(r.returncode == 0, '%s %s\n%s%s' % (script, args, r.stdout[-1500:], r.stderr[-1500:]))
    return r.stdout


def last_json(out, token):
    line = [l for l in out.splitlines() if token in l][-1]
    return json.loads(line[line.index('{'):])


def main():
    for row in json.load(open(H / 'SOURCES.json'))['files']:
        if row['usage'] == 'input':
            need(sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'], 'input ' + row['path'])
    print('PASS_INPUTS_AUTHENTICATED', flush=True)
    res = {}
    for label, pkg in PKGS.items():
        r = {}
        r['local'] = last_json(run('audit_local.py', ROOT / FRAMES, ROOT / pkg / 'WORD.json.gz', label), 'PASS {')
        print('PASS_LOCAL', label, flush=True)
        g = last_json(run('audit_global.py', ROOT / pkg, ROOT / FRAMES, label), 'PASS {')
        r['global'] = g
        print('PASS_GLOBAL', label, flush=True)
        r['admission'] = last_json(run('audit_admission.py', ROOT / pkg), 'PASS_ADMISSION')
        r['chain_levels'] = last_json(run('chain_levels.py', ROOT / pkg), 'PASS_CHAIN_LEVELS')
        print('PASS_ADMISSION_AND_LEVELS', label, flush=True)
        res[label] = r
    a, b = res['PR5679']['global'], res['PR5708']['global']
    delta = {k: b['paid'].get(k, 0) - a['paid'].get(k, 0) for k in set(a['paid']) | set(b['paid'])}
    delta = {k: v for k, v in sorted(delta.items(), key=lambda x: int(x[0])) if v}
    need(delta == {'1': 36, '2': -72, '3': 36} and a['targets'] == b['targets'], 'PR5679 -> PR5708 delta')
    res['delta_PR5679_to_PR5708'] = dict(paid=delta, targets_equal=True)
    out = run('controls.py', ROOT / PKGS['PR5708'], ROOT / FRAMES, timeout=500)
    need('ALL_CONTROLS_REJECTED' in out, 'negative controls')
    res['controls_PR5708'] = [l.split(' ')[0] + ' ' + l.split(' ')[1] for l in out.splitlines() if l.startswith(('local', 'global'))]
    print('PASS_CONTROLS', len(res['controls_PR5708']), flush=True)
    path = H / 'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(res, indent=1, sort_keys=True) + '\n')
    need(json.loads(path.read_text()) == json.loads(json.dumps(res)), 'results equal RESULT.json')
    print('PASS_G20_INDEPENDENT_REVIEW_5679_5708', flush=True)


if __name__ == '__main__':
    main()
