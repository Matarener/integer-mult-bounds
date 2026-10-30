"""Exact staged-entry word review (helpers 608, 609, 600 on PR3945's terminal-width5 words) with constructive
rejection controls.  Retained independent interpreter: Sagar Thakrar, PR3687/3693 (audit_verify.semantics).
Mirrors dataisfire's PR3734 review_staged544.py.  Prepared by Rohan Arun with Anthropic Claude assistance. Apache-2.0.
"""
from pathlib import Path
from copy import deepcopy
import gzip, json
import audit_core as C
from audit_verify import semantics
import staged_entries_applier as S
P = Path(__file__).resolve().parent
PROFILE = {1: 2488, 2: 714, 3: 223, 4: 102, 5: 20, 8: 8}
WIDTHS = {5: 28, 6: 18, 7: 56, 8: 93, 9: 213}


def need(ok, why):
    if not ok: raise ValueError(why)
def load(p): return json.loads(gzip.decompress(p.read_bytes()))
def rejects(name, fn):
    try: fn()
    except (ValueError, C.AuditFailure): return name
    raise ValueError('control accepted ' + name)
def inspect(w):
    C.hygiene(w); bill, widths, _, _, _ = C.frame_bill(w)
    need(bill == PROFILE, 'actual profile'); need(widths == WIDTHS, 'actual widths')
    need(w['cleanup'] == C.derive_cleanup(w), 'literal cleanup')
    return semantics(C, w)


rows = []
for tag in ('base', 'extra'):
    old = load(P / 'staged3' / f'PRE-{tag}.json.gz'); actual = load(P / 'receiver-share-parent' / f'BORROW-WORD-43{tag}.json.gz')
    rec = json.loads((P / 'staged3' / f'RECORD-{tag}.json').read_text())
    w = S.apply(old, rec); need(w == actual, 'declared staged-entry recipe reconstructs the actual word')
    semantic = inspect(w); controls = []
    for entry in rec['entries']:
        h = entry['helper']
        for rel in entry['releases']:
            k = next(i for i, g in enumerate(w['B']) if g[0] == 'add' and g[1:3] == [rel['register'], h])
            for defect in ('omit_release', 'flip_release'):
                bad = deepcopy(w)
                if defect == 'omit_release':
                    bad['B'].pop(k)
                    for r in bad['warps']:
                        if r[0] > k: r[0] -= 1
                else: bad['B'][k][3] *= -1
                bad['cleanup'] = C.derive_cleanup(bad)          # rejection cannot come from a stale inverse
                controls.append(rejects(f'{defect}_{h}_{rel["register"]}', lambda: semantics(C, bad)))
        bad = deepcopy(w); bad['start_extra'][str(h)] = old['start_extra'][str(h)]
        controls.append(rejects(f'old_entrance_{h}', lambda: inspect(bad)))
    bad = deepcopy(w); bad['report']['local_profile']['1'] += 1
    controls.append(rejects('wrong_bill', lambda: need(C.frame_bill(bad)[0] == {int(r): n for r, n in bad['report']['local_profile'].items()}, 'changed report')))
    badrec = deepcopy(rec); badrec['sections']['B'][0]['old'][0][3] += 1
    controls.append(rejects('wrong_literal_preimage', lambda: S.apply(old, badrec)))
    rows.append(dict(provider=tag, semantics=semantic, controls=controls, canonical_sha256=S.canonical(w)))
print(json.dumps(dict(status='PASS_STAGED_ENTRIES_608_609_600_DIRTY_WORD_AND_CONTROLS', providers=rows), sort_keys=True), flush=True)
