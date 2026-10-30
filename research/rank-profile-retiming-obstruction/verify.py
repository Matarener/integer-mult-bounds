#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only source binding, exact census, and retained dirty-word controls."""
import gzip
import hashlib
import json
from pathlib import Path
import sys
import types
from copy import deepcopy
from fractions import Fraction as Q

P = Path(__file__).resolve().parent
# Execute this package's actual source, not any adjacent bytecode cache.
R = types.ModuleType('retiming_source')
exec(compile((P / 'retiming.py').read_bytes(), str(P / 'retiming.py'), 'exec'), R.__dict__)
need = R.need


def json_normal(value):
    return json.loads(json.dumps(value, sort_keys=True))


def rejects(fn, name):
    try:
        fn()
    except (ValueError, C.AuditFailure):
        return name
    raise ValueError('control accepted: ' + name)


def authenticate(raw, row):
    need(len(raw) == row['bytes'], 'source length: ' + row['local'])
    need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: ' + row['local'])
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    need(blob == row['git_blob'], 'source Git blob: ' + row['local'])


def module(name, path):
    value = types.ModuleType(name)
    value.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
    return value


sources = json.loads((P / 'SOURCES.json').read_text())
for row in sources['snapshots']:
    authenticate((P / row['local']).read_bytes(), row)
C = module('retained_audit_core', P / 'vendor/audit_core.py')
A = module('retained_audit_adapter', P / 'vendor/audit_verify.py')
expected = json.loads((P / 'CENSUS.json').read_text())
controls = []
first = sources['snapshots'][0]
controls.append(rejects(lambda: authenticate((P / first['local']).read_bytes() + b'x', first), 'source drift'))
need(not R.all_power_nonnegative((0, 1, -2, 1, 0, 0, 0, 0, 0, 0)), 'profitable exchange must not be excluded')
controls.append('profitable 2+2 to 1+3 rejected by non-improvement certificate')
results = {}
for tag in ('base', 'extra'):
    word = json.loads(gzip.decompress((P / 'inputs' / ('BORROW-WORD-43' + tag + '.json.gz')).read_bytes()))
    profile, inventory, *_ = C.frame_bill(word)
    need(profile == {1:2440, 2:725, 3:224, 4:102, 5:20, 8:8}, 'source profile')
    need(word['cleanup'] == C.derive_cleanup(word), 'source literal cleanup')
    need(R.tracing(word)[2] == profile, 'independent chronological bill')
    result = R.census(word)
    need(json_normal(result) == expected[tag], 'complete census differs')
    need(all(row['certificate'] for row in result['deltas']), 'uncertified retiming delta')
    need(sum(row['count'] for row in result['deltas']) == result['candidates'], 'census partition')
    # Counterfactual rollback of one already-retained Jeremy Kothe PR2957 swap.
    # This is not asserted to be the complete historical PR2957 parent word.
    old = deepcopy(word)
    g, h = old['A'][4043:4045]
    need(g[:5] == ['add',81,40,1,1] and h[:5] == ['add',81,17,1,1], 'control preimages')
    old['A'][4043:4045] = [h[:-1] + [g[-1]], g]
    old['cleanup'] = C.derive_cleanup(old)
    before, widths, *_ = C.frame_bill(old)
    old['report']['local_profile'] = {str(r): n for r, n in before.items()}
    need(before == {1:2439, 2:726, 3:225, 4:101, 5:20, 8:8}, 'rollback bill')
    need(widths == inventory and R.tracing(old)[2] == before, 'rollback boundary ledger')
    new = R.apply_move(old, 'A', 4043, 4045, h[-1])
    need(R.span(tuple(new['A'][4044][-1])) == R.span(tuple(h[-1])), 'recovered frame')
    new['A'][4044][-1] = deepcopy(h[-1])  # Restore the source basis spelling.
    new['cleanup'] = C.derive_cleanup(new)
    after, new_widths, *_ = C.frame_bill(new)
    new['report']['local_profile'] = {str(r): n for r, n in after.items()}
    need(new == word, 'literal source word recovered')
    need(new_widths == widths, 'no inventory changes')
    delta = [0] + [after.get(r,0) - before.get(r,0) for r in range(1,10)]
    need(delta == [0,1,-1,-1,1,0,0,0,0,0], 'actual 2+3 to 1+4 circuit delta')
    need(not R.all_power_nonnegative(tuple(delta)), 'known gain must escape obstruction')
    semantics = {'rollback': A.semantics(C, old), 'retained': A.semantics(C, new)}
    bad = deepcopy(new)
    bad['A'][4044][3] *= -1
    bad['cleanup'] = C.derive_cleanup(bad)
    controls.append(rejects(lambda: A.semantics(C, bad), tag + ' wrong scalar with refreshed cleanup'))
    bad = deepcopy(new)
    bad['A'][4044][-1] = []
    controls.append(rejects(lambda: C.frame_bill(bad), tag + ' invalid gate frame'))
    barrier = next(i for i in range(word['prelude_events'], len(word['A'])-1)
                   if word['A'][i][0] == 'add' and not R.crosses(word['A'][i], word['A'][i+1]))
    controls.append(rejects(lambda: R.apply_move(word, 'A', barrier, barrier+2, word['A'][barrier][-1]),
                            tag + ' noncommuting barrier'))
    result['positive_control'] = {'before_profile': before, 'after_profile': after,
                                  'delta': {r:n for r,n in enumerate(delta) if n},
                                  'semantics': semantics}
    results[tag] = result
# PR3863's sufficient credit, now attached to this actual credited rewrite.
lower, upper = Q(17,10000), Q(18,10000)
credit = sum(lower*(1-upper)/((k+1)*(1+upper*k)) for k in (2,3))
need(credit == Q(1491695107,1513529160000), 'exact local credit')
need(3240 * credit - 3 == Q(2437538889,12612743000), 'strict three-child reserve')
report = {'status': 'PASS_SOURCE_BOUND_RETIMING_SCOPE', 'providers': results,
          'controls': controls, 'local_credit': str(credit), 'replications': 3240,
          'three_rank1_margin': str(3240*credit-3), 'new_current_supplier': False}
if '--summary' in sys.argv:
    print(json.dumps({k:v for k,v in report.items() if k != 'providers'}, sort_keys=True))
else:
    print(json.dumps(report, sort_keys=True))
