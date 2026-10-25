#!/usr/bin/env python3
"""Separate direct-displacement execution, without the full-row engine.

Chronological words are stored in the opposite order to verify.py; no parser,
row operation or result is imported from that engine. Both implement the
source's normalized native chart semantics, which remain an inherited premise.
JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json

P = Path(__file__).resolve().parent


def demand(ok, why):
    if not ok:
        raise RuntimeError(why)


def load():
    result = {}
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            content = (P.parent.parent/row['path']).read_bytes()
            demand(sha256(content).hexdigest() == row['sha256'], 'source hash')
            if row['path'].endswith('.gz'):
                content = gzip.decompress(content)
            result[Path(row['path']).name] = json.loads(content)
    return result


def run(canonical, word, coefficients):
    values = {('L', i): ({(): coefficients[i]} if coefficients.get(i) else {}) for i in range(632)}
    charts = {('L', i): frame for i, frame in enumerate(canonical['start'])}
    for i in range(9):
        values['C', i] = {}
        charts['C', i] = None
    full_events, failures = 0, []
    for at, record in enumerate(word):
        tag = record[0]
        changed = None
        if tag == 'scalar':
            op, chart = record[1:]
            kind, changed = op[0], tuple(op[1])
            if kind == 'clear':
                demand(changed[0] == 'C', 'persistent clear')
                values[changed] = {}
            elif kind == 'copy':
                demand(not values[changed] and charts[tuple(op[2])] == chart, 'owned copy')
                values[changed] = dict(values[tuple(op[2])])
            elif kind == 'scale':
                demand(charts[changed] == chart, 'scale chart')
                coefficient = Fraction(op[2], op[3])
                values[changed] = {w: x*coefficient for w, x in values[changed].items() if x*coefficient}
            else:
                demand(kind == 'add' and charts[changed] == charts[tuple(op[2])] == chart, 'ADD chart')
                accum = defaultdict(Fraction, values[changed])
                for w, x in values[tuple(op[2])].items():
                    accum[w] += x*Fraction(op[3], op[4])
                values[changed] = {w:x for w,x in accum.items() if x}
            charts[changed] = chart
        elif tag == 'warp':
            _, role, symbol, old, new = record
            changed = tuple(role)
            demand(charts[changed] == old, 'warp chart')
            accum = defaultdict(Fraction)
            for chronological, x in values[changed].items():
                next_word = chronological[:-1] if chronological and chronological[-1] == -symbol else chronological+(symbol,)
                accum[next_word] += x
            values[changed] = {w:x for w,x in accum.items() if x}
            charts[changed] = new
        elif tag == 'climb':
            _, _, owner, old, new, rank = record
            changed = ('L', owner)
            demand(charts[changed] == old and rank == len(canonical['frames'][new])-len(canonical['frames'][old]), 'climb chart')
            charts[changed] = new
        elif tag == 'center':
            _, owner, old, new, rank = record
            changed = ('C', owner)
            demand(charts[changed] == old and rank == abs(len(canonical['frames'][new])-len(canonical['frames'][old])), 'center chart')
            charts[changed] = new
        elif tag == 'zero_retag':
            _, owner, old, new = record
            changed = ('L', owner)
            demand(charts[changed] == old and not values[changed], 'zero retag')
            charts[changed] = new
        else:
            demand(tag in ('phase', 'adapter'), 'unexpected record')
        if changed is not None and len(canonical['frames'][charts[changed]]) == 9:
            full_events += 1
            if values[changed]:
                failures.append(at)
    return values, charts, full_events, failures


def main():
    data = load()
    coefficients = {int(j): Fraction(c) for j,c in json.loads((P/'KERNEL.json').read_text())['original_input_displacement']}
    values, charts, count, failures = run(data['ACTUAL-WORD.json.gz']['canonical'], data['WORD.json.gz']['word'], coefficients)
    demand(not failures and count > 4891, 'all full-frame events invisible, including zero and repeated versions')
    demand(all(not values['C', j] for j in range(9)), 'all nine endpoint owned displacements vanish')
    m = data['NORMALIZERS.json']['mode_columns']
    image = [sum(Fraction(v)*coefficients.get(112+j, Fraction()) for j,v in enumerate(row)) for row in m]
    demand(image == [Fraction(0), Fraction(-4), *([Fraction(0)]*6)], 'actual target image')
    # A basis-free conditional decoder needs ORIGINAL E h, not its zero endpoint.
    identity_checks = 0
    for rec in data['PROVIDER.json']['mode_boundaries']:
        k, slot = rec['mode'], rec['cache_slot']-632
        demand(charts['C', slot] == rec['frame'], 'endpoint cache chart')
        original = sum(Fraction(c)*coefficients.get(224+j, Fraction())
                       for j,c in data['PROVIDER.json']['canonical_retraction_E'][k])
        demand(original-image[k] == 0, 'cache cancellation by original helper change')
        identity_checks += 1
    print(json.dumps({'status':'PASS_DIRECT_PARTIAL_CACHE_DISPLACEMENT',
                      'full_frame_events':count, 'endpoint_owned_zero_displacements':9,
                      'original_helper_cache_checks':identity_checks,
                      'target_image':[str(x) for x in image],
                      'execution':'single displacement, chronological free words, independent implementation'},
                     sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
