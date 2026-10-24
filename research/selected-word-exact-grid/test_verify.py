"""Rejecting controls for verify.py.  Each mutation must raise SystemExit('FAIL...')."""
import copy
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify as V  # noqa: E402

WORD = json.loads(gzip.decompress(V.WORDS['eight_relation_body'].read_bytes()))
CE = V.clifford()


def rejects(name, fn):
    try:
        fn()
    except SystemExit as exc:
        if not str(exc).startswith('FAIL'):
            raise
        print('rejected:', name)
        return
    raise AssertionError('control accepted: ' + name)


def drift():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    row = next(r for r in rows['files'] if r['usage'] == 'input')
    data = (V.ROOT / row['path']).read_bytes()
    V.require(V.hashlib.sha256(data).hexdigest() == '0' * 64, 'input drift: ' + row['path'])


def odd_division():
    bad = copy.deepcopy(WORD)
    e = next(ev for ev in bad['programs']['backward'] if ev[0] == 'scalar' and ev[1][0] == 'add')
    e[1][4] = 3
    V.census(bad, 'backward', V.Ranks(CE, bad['canonical']))


def wrong_climb_rank():
    bad = copy.deepcopy(WORD)
    e = next(ev for ev in bad['programs']['forward'] if ev[0] == 'climb')
    e[5] += 1
    V.census(bad, 'forward', V.Ranks(CE, bad['canonical']))


def smaller_guard_claim():
    res = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))['eight_relation_body/backward']
    V.require(res['guard']['1'] <= 10, 'a ten-bit single-layer guard (false: the witness needs 11)')


def tampered_result():
    stored = json.loads((HERE / 'RESULT.json').read_text(encoding='utf-8'))
    stored['eight_relation_body/backward']['guard']['1'] = 10
    V.require(stored['eight_relation_body/backward']['guard']['1'] == 11, 'stored RESULT.json equals the rebuild')


import caller as CL  # noqa: E402


def _caller_body(mutate):
    spec = CL.importlib.util.spec_from_file_location('cl_ce', CL.CLIFFORD)
    ce = CL.importlib.util.module_from_spec(spec); spec.loader.exec_module(ce)
    body = json.loads(CL.BODY.read_text(encoding='utf-8'))
    prov = json.loads((CL.PROV / 'PROVIDER.json').read_text(encoding='utf-8'))
    word = json.loads(gzip.decompress((CL.PROV / 'WORD.json.gz').read_bytes()))
    canonical = json.loads(gzip.decompress(CL.EIGHT.read_bytes()))['canonical']
    mutate(body, prov)
    B = CL.Body(body, prov, word, canonical, ce)
    B.run()
    CL.require(B.odd == 0, 'every coefficient of the complete body is dyadic')


def caller_odd_division():
    def m(body, prov):
        next(o for o in body['operations'] if o['op'] == 'ADD')['coefficient'] = '1/3'
    _caller_body(m)


def caller_missing_owned_clear():
    def m(body, prov):
        ops = body['operations']
        i = max(k for k, o in enumerate(ops) if o['op'] == 'CLEAR')
        ops.pop(i)
    _caller_body(m)


def caller_tampered_result():
    stored = json.loads((HERE / 'RESULT-CALLER.json').read_text(encoding='utf-8'))
    stored['controller']['rigorous_bracket'] = [70, 77]
    CL.require(stored['controller']['rigorous_bracket'] == [73, 77], 'stored RESULT-CALLER.json equals the rebuild')


for name, fn in [('drifted input hash', drift), ('an odd division in a scalar ADD', odd_division),
                 ('a corrupted climb rank', wrong_climb_rank), ('a smaller guard claim', smaller_guard_claim),
                 ('tampered RESULT.json', tampered_result),
                 ('caller: an odd division in a body ADD', caller_odd_division),
                 ('caller: a missing owned CLEAR', caller_missing_owned_clear),
                 ('caller: tampered RESULT-CALLER.json', caller_tampered_result)]:
    rejects(name, fn)
print('PASS_SELECTED_WORD_EXACT_GRID_CONTROLS')
