"""Positive control: nreplay reproduces the official literal_replay on the #4610 round-three word
(both orientations): identical rows for all 632 registers + C0 and identical paid profile."""
import gzip, json, importlib.util, sys
from pathlib import Path
from nreplay import replay, v, ROOT
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m; spec.loader.exec_module(m); return m
X = load(ROOT/'research/kappa-rebuild/complex/native_extensions.py', 'r18_literal')
w = json.loads(gzip.decompress((ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()))
c = w['canonical']
for side in ('forward', 'backward'):
    back = side == 'backward'
    rows0, rec = X.literal_replay(v, c, w['programs'][side], back)
    rows1, prof, _ = replay(632, c['frames'], c['start'], c['final'], w['programs'][side], back)
    same = rows0 == rows1 and {int(k): x for k, x in rec['paid_profile'].items()} == prof
    ident = all(rows1['L', r] == v.expected(('L', r), [], back, False) for r in range(632))
    print(side, 'nreplay == literal_replay:', same, '| all 632 endpoints expected:', ident, '| profile', prof)
    assert same and ident
print('PASS_NREPLAY_CONTROL_4610')
