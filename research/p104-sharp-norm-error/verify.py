#!/usr/bin/env python3
"""Check the frozen word, exact transfer bounds and attaining executions."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import sys
from fractions import Fraction as F

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import analysis as A


def authenticate(data, item):
    A.need(hashlib.sha256(data).hexdigest() == item['sha256'], 'Source SHA256')
    blob = b'blob '+str(len(data)).encode()+b'\0'+data
    A.need(hashlib.sha1(blob).hexdigest() == item['git_blob'], 'Source Git blob')


def guard(value):
    g = 0
    while F(2**g) <= value:
        g += 1
    return g


def check_model(word, weights, rounded):
    report, witness = A.error_trace(word, weights, rounded)
    scores, hashes = A.reverse_all(word, weights, rounded)
    A.need(scores == report['final_scores'], 'Every final score: forward and transpose')
    A.need(hashes == report['final_coefficient_hashes'], 'Every final error coefficient: forward and transpose')
    for key, peak in list(enumerate(report['peaks'])) + [('final'+str(k),v) for k,v in enumerate(report['final_peaks'])]:
        _, errors = A.reverse_cut(word, rounded, peak['cut'], peak['role'])
        A.need(errors == witness[key], 'Attaining row: forward and reverse')
        k = key if isinstance(key,int) else int(key[-1])
        defects = {j:(1 if c>0 else -1)*(weights[j][k] if k<2 else F(1)) for j,c in errors.items()}
        values = A.execute(word, {}, defects, peak['cut'])
        A.need(values[peak['role']] == peak['value'], 'Literal independent-defect attainment')
    J,K,absolute = [v['value'] for v in report['peaks']]
    g = guard(J+K)
    A.need(J >= 2**(g-1), 'One fewer prefix guard fails this formula')
    gf = 0
    while True:
        z = F(2**gf)
        if z > K:
            value, role = max((a+b*J/(z-K),r) for r,(a,b,_) in enumerate(scores[:word['public']]))
            if value < z:
                break
        gf += 1
    report['guards'] = dict(relative_prefix=g, relative_final=gf, absolute_prefix=guard(absolute),
                            absolute_final=guard(report['final_peaks'][2]['value']))
    report['final_relative_at_guard'] = dict(value=value, role=role, denominator=2**gf)
    report['coefficient_checks'] = dict(final_rows=len(scores), attaining_rows=6)
    return report


def run():
    origins = json.loads((ROOT/'ORIGINS.json').read_text())
    for item in origins:
        data = (ROOT/item['local']).read_bytes()
        authenticate(data,item)
        try:
            authenticate(data+b'!',item)
        except ValueError:
            pass
        else:
            raise ValueError('Corrupt source accepted')
    word = json.loads(gzip.decompress((ROOT/'source/WORD.json.gz').read_bytes()))
    ideal, weights = A.ideal(word)
    peak = ideal['input_peak']
    row,_ = A.reverse_cut(word,set(),peak['cut'],peak['role'])
    A.need(row == peak['row'], 'Peak input row: forward and reverse')
    values = A.execute(word,{r:F(1 if c>0 else -1) for r,c in row.items()},{},peak['cut'])
    A.need(values[peak['role']] == peak['value'] == 131072, 'Sharp input norm and attaining execution')
    A.need(peak['value'] > 2**16, 'Insufficient input guard rejected')
    erasures = ideal['erasures']
    A.need(sum(e['ideal_zero'] for e in erasures) == 1 and len(erasures) == 30, 'Erasure premise is not known-zero recovery')
    for erase in erasures:
        row,_ = A.reverse_cut(word,set(),erase['event'],erase['role'])
        A.need(sum(map(abs,row.values()),F(0)) == erase['ideal_norm'], 'Every pre-erasure ideal norm')
    models = {name:check_model(word,weights,rounded) for name,rounded in (
        ('all_completed',{'MOVE','ADD','SCALE'}), ('native_only',{'MOVE'}))}
    # A reset removes its own error, but cannot remove an error already copied out.
    fixture = dict(public=1,owned_fields=1,program=[['INIT',1,0],['MOVE',1,0,1,True],
        ['ADD',0,1,'1',1],['CLEAR',1,1]])
    A.need(A.execute(fixture,{}, {1:F(1)},4) == [F(1),F(0)], 'Exported error survives owned CLEAR')
    # COPY propagates the source error once; it does not preserve destination dirt.
    fixture['program'] = [['COPY',1,0,'1',0]]
    A.need(A.execute(fixture,{0:F(2),1:F(7)}, {},1) == [F(2),F(2)], 'COPY overwrites destination')
    return A.encode(dict(schema_version=1,source_head='9bab1ca917ec4d1a4e60f4eb8c81d7ef92908a62',
        ideal=ideal, models=models, source_corruption_controls=len(origins),
        controls=['input guard 16 fails','absolute defect maxima attained','prefix relative guard minus one fails formula',
                  'final relative guard is minimal for formula','29 erasures have nonzero ideal data',
                  'exported error survives reset','COPY overwrites destination'],
        scope='Conditional unitary-chart completed-operation precision lemma; no new kappa or rounded child.'))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--write-receipt', action='store_true')
    args = p.parse_args()
    result = run()
    path = ROOT/'RESULT.json'
    if args.write_receipt:
        with path.open('x') as f:
            json.dump(result,f,indent=2,sort_keys=True)
            f.write('\n')
    else:
        A.need(json.loads(path.read_text()) == result, 'Stored exact receipt')
    for name, model in result['models'].items():
        print(name, 'peaks',model['peaks'], 'guards',model['guards'])
    print('PASS_P104_SHARP_NORM_ERROR',A.digest(result))
