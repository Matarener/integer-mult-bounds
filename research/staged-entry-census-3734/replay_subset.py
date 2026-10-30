# SPDX-License-Identifier: Apache-2.0
"""Optional replay of a census subset (numpy 2.5.4, scipy 1.18.1), compared with the recorded evidence.

Reruns, in a temporary directory: the fixed-frame census on the two parent words (544 on PR3682's,
644/660 on PR3133's: the published staged entries must be rediscovered), the fixed-frame census on
PR3734's base word for helpers 457, 472 and 640, the re-solved B-window pass for 472 and the
A-window pass for 461. For each, the rows of those helpers must equal the recorded rows
(status per helper, raise and cut). Not registered in VERIFY.json: float decisions are not
guaranteed identical across BLAS builds. About four minutes on one machine.
"""
import gzip
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

P = Path(__file__).resolve().parent
S = P.parent / 'staged544-producer-return'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def evidence(name):
    return json.loads(gzip.decompress((P / 'evidence' / name).read_bytes()))['results']


def key(r):
    return (r['h'], tuple(r['P']), r['pos'] if 'pos' in r else r['cut'], r.get('kind', ''), r['status'])


def run(tmp, script, *args):
    out = subprocess.run([sys.executable, '-B', str(P / 'code' / script), *args], cwd=tmp,
                         capture_output=True, text=True, timeout=1200)
    need(out.returncode == 0, script + ' failed: ' + out.stderr[-2000:])
    tag = args[0].replace('/', '_')
    stem = {'pass5.py': 'pass5', 'pass7.py': 'pass7', 'pass8.py': 'pass8'}[script]
    return json.loads((Path(tmp) / f'{stem}-{tag}.json').read_text())['results']


def compare(name, rows, helpers):
    want = sorted(key(r) for r in evidence(name) if r['h'] in helpers)
    got = sorted(key(r) for r in rows if r['h'] in helpers)
    need(got == want, f'{name}: replayed rows differ for helpers {sorted(helpers)}')
    return len(got)


def main():
    report = {}
    with tempfile.TemporaryDirectory() as tmp:
        arch = json.loads((S / 'REPLAY-INPUTS.json').read_text())
        with tarfile.open(fileobj=io.BytesIO((S / 'REPLAY-INPUTS.tar.gz').read_bytes())) as t:
            raw = t.extractfile('source/new/borrow/inputs/PRE3605-base.json.gz').read()
        import hashlib
        need(hashlib.sha256(raw).hexdigest() == arch['files']['source/new/borrow/inputs/PRE3605-base.json.gz'],
             'PR3605 parent word digest')
        pre3605 = str(Path(tmp) / 'PRE3605-base.json.gz')
        Path(pre3605).write_bytes(raw)
        pre544 = str(S / 'staged544' / 'PRE-base.json.gz')
        rows = run(tmp, 'pass5.py', pre544, '24', '544')
        need(sorted({r['h'] for r in rows if r['status'] == 'ok'}) == [544], '544 rediscovered')
        report['control_544'] = compare('CONTROL-PRE544-base.json.gz', rows, {544})
        rows = run(tmp, 'pass5.py', pre3605, '24', '644,660')
        need(sorted({r['h'] for r in rows if r['status'] == 'ok'}) == [644, 660], '644/660 rediscovered')
        report['control_644_660'] = compare('CONTROL-PRE3605-base.json.gz', rows, {644, 660})
        rows = run(tmp, 'pass5.py', 'base', '24', '457,472,640')
        report['fixed_frames_457_472_640'] = compare('FIXED-FRAMES-base.json.gz', rows, {457, 472, 640})
        rows = run(tmp, 'pass7.py', 'base', '6', '4', '472')
        report['resolved_B_472'] = compare('RESOLVED-B-WINDOWS-base.json.gz', rows, {472})
        rows = run(tmp, 'pass8.py', 'base', '5', '4', '461')
        report['resolved_A_461'] = compare('RESOLVED-A-WINDOWS-base.json.gz', rows, {461})
    print(json.dumps(report, sort_keys=True))
    print('PASS_STAGED_ENTRY_CENSUS_SUBSET_REPLAY', flush=True)


if __name__ == '__main__':
    main()
