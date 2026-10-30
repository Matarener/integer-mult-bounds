"""Check every released sparse G20 route and its fused q-adic carries."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import gzip
import json
from pathlib import Path
import random
import sys

import importlib.util
_spec = importlib.util.spec_from_file_location("g20_carries", Path(__file__).with_name("carries.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def authenticate():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            C.need(sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'], 'source hash: '+row['path'])


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def reject(label, fn):
    try:
        fn()
    except ValueError:
        return label
    raise ValueError('accepted control: '+label)


def run():
    authenticate()
    source = json.loads((P/'inputs/source-RESULT.json').read_text())
    ports = json.loads((P/'inputs/PORTS.json').read_text())
    calls = json.loads((P/'inputs/CALLS.json').read_text())
    stream = gzip.decompress((P/'inputs/GLOBAL.jsonl.gz').read_bytes())
    C.need(sha256(stream).hexdigest() == ports['stream_sha256'], 'source stream digest')
    events = [json.loads(line) for line in stream.splitlines()]
    markers = {i: e for i, e in enumerate(events) if e[0] == 'PAID_PORT_ROUTE'}
    expected = {}
    for call in calls:
        if call['stage'] == 0:
            continue
        for phase, start in [('ENTRY', call['core_begin']-222), ('RETURN', call['core_end'])]:
            for k, bank in enumerate((call['source_bank'], call['target_bank'])):
                for port in range(111):
                    i = start+111*k+port
                    C.need(i not in expected, 'unique marker position')
                    expected[i] = ['PAID_PORT_ROUTE', call['stage'], 111*bank+port, port, phase]
    C.need(markers == expected and len(markers) == 7548, 'full actual marker binding')
    incidence = Counter((e[3], 'inverse' if e[4] == 'ENTRY' else 'forward') for e in markers.values())
    C.need(set(incidence.values()) == {34} and len(incidence) == 222, 'both direction counts')
    rng = random.Random(5820); receipts = []; cases = 0; cocycles = 0; stream_hash = sha256()
    moduli = [(5,1), (5,2), (7,3), (25,4), (2**89-1,8)]
    for name, key in [('tree','ports'), ('shear','scale_free_ports')]:
        catalogue = source[key]
        C.need([r['port'] for r in catalogue] == list(range(111)), 'complete port domain')
        elementary_total = fused_total = 0
        for record in catalogue:
            matrices = {direction: C.matrix(record[direction]) for direction in ['forward','inverse']}
            s, inverse = matrices['forward'], matrices['inverse']
            C.need(C.multiply(s,inverse) == C.multiply(inverse,s) == C.identity(8), 'both exact products')
            original = ports['port_interfaces']['ports'][record['port']]
            w = [[F(x) for x in row] for row in original['normalizer']]
            v = [[F(x) for x in row] for row in original['inverse']]
            projector = [[w[i][0]*v[0][j] for j in range(8)] for i in range(8)]
            diagonal = [[F(i == j == 0) for j in range(8)] for i in range(8)]
            C.need(C.multiply(projector,s) == C.multiply(s,diagonal), 'same line and complement interface')
            for direction in ['forward','inverse']:
                word = record[direction]; s = matrices[direction]
                back = 'inverse' if direction == 'forward' else 'forward'
                count = incidence[record['port'],direction]
                columns = C.potential_carry_columns(s)
                elementary_total += len(word)*count; fused_total += len(columns)*count
                for q,width in moduli:
                    modulus = q**width; high_mod = q**(width-1)
                    fixtures = [[rng.randrange(modulus) for _ in range(8)], [modulus-1]*8]
                    fixtures += [[int(i == j) for i in range(8)] for j in range(8)]
                    for values in fixtures:
                        low = [x%q for x in values]; high = [x//q for x in values]
                        a,b = C.fused(low,high,word,s,q,width)
                        direct = C.dense_oracle(values,s,modulus)
                        C.need([x+q*y for x,y in zip(a,b)] == direct, 'independent full-width oracle')
                        C.need((a,b) == C.elementary(low,high,word,q,width), 'complete elementary carry comparison')
                        C.need(C.fused(a,b,record[back],matrices[back],q,width) == (low,high), 'committed-low inverse restoration')
                        _,shift = C.carry(low,s,q)
                        C.need(all(not shift[j] for j in range(8) if j not in columns), 'omitted positive-unit columns')
                        stream_hash.update(canonical([name,record['port'],direction,q,width,direct]));cases += 1
                    # A separate noncommuting next matrix tests the general cocycle.
                    t = C.matrix([['ADD',0,1,'1/2'],['ADD',1,2,'-1']])
                    low = [rng.randrange(q) for _ in range(8)]
                    mid,cs = C.carry(low,s,q); end,ct = C.carry(mid,t,q)
                    both,combined = C.carry(low,C.multiply(s,t),q)
                    transported = [sum(x*y for x,y in zip(cs,col)) for col in zip(*t)]
                    C.need(end == both and [x+y for x,y in zip(transported,ct)] == combined, 'exact rational carry cocycle')
                    cocycles += 1
                receipts.append(dict(basis=name,port=record['port'],direction=direction,word_length=len(word),
                    carry_columns=columns,denominator=max(x.denominator for row in s for x in row),
                    column_norms=[str(sum(map(abs,col),F(0))) for col in zip(*s)]))
        C.need(fused_total < elementary_total, 'strict complete carry-site reduction')
        receipts.append(dict(basis=name,elementary_carry_sites=elementary_total,fused_carry_sites=fused_total,
            saved_carry_sites=elementary_total-fused_total,cover_saved_times_f_squared=127*(elementary_total-fused_total)))
    # Exhaust every input pair of two noncommuting factors over complete rings.
    exhaustive = 0
    tiny = [['ADD',0,1,'-3/4'],['SCALE',0,'1/2'],['ADD',1,0,'1']]
    s = C.matrix(tiny,2)
    for q,width in [(5,1),(5,2),(7,1),(7,2)]:
        modulus = q**width
        for values in product(range(modulus),repeat=2):
            a,b = C.fused([x%q for x in values],[x//q for x in values],tiny,s,q,width)
            C.need([x+q*y for x,y in zip(a,b)] == C.dense_oracle(values,s,modulus),'exhaustive rational route')
            exhaustive += 1
    # Full row/column/lane address fixtures, with all spectators retained.
    embedded_cases = 0; addresses = 0
    record = source['ports'][8]; s = C.matrix(record['inverse']); back = C.matrix(record['forward'])
    layouts = [dict(stage=c['stage'],ordinal=k,active_axes=[0,*range(1+7*k,8+7*k)]) for k,c in enumerate(calls)]
    C.need(len(layouts) == 18 and len({r['stage'] for r in layouts}) == 18, 'source stage ordinals')
    for f,ordinal in [(1,0),(1,1),(2,17)]:
        n = 127*f; q = 5; width = 3; active = layouts[ordinal]['active_axes']
        low = [rng.randrange(q) for _ in range(n*n)]; high = [rng.randrange(q**(width-1)) for _ in range(n*n)]
        a,b = C.embedded(low,high,record['inverse'],s,active,f,q,width)
        active_set = {row*n+axis*f+lane for row in range(n) for axis in active for lane in range(f)}
        C.need(all((a[i],b[i]) == (low[i],high[i]) for i in range(n*n) if i not in active_set), 'spectator matrix columns')
        for row in range(n):
            for lane in range(f):
                idx = [row*n+axis*f+lane for axis in active]
                C.need([a[i]+q*b[i] for i in idx] == C.dense_oracle([low[i]+q*high[i] for i in idx],s,q**width),'embedded dense row oracle')
        C.need(C.embedded(a,b,record['forward'],back,active,f,q,width) == (low,high),'entire cover restoration')
        addresses += len(active_set); embedded_cases += 1
    # Full-width errors can survive a successful low map and inverse round trip.
    low = [1,0]; high = [0,0]; word = [['ADD',0,1,'1/2']]; s = C.matrix(word,2)
    a,b = C.fused(low,high,word,s,5,2); wrong = C.high_word(high,word,5)
    controls = [reject('omit high carry',lambda:C.need(wrong == b,'full-width mismatch')),
        reject('use stale low type for return',lambda:C.need(C.fused(low,b,[['ADD',0,1,'-1/2']],C.matrix([['ADD',0,1,'-1/2']],2),5,2) == (low,high),'stale low cache')),
        reject('even source modulus',lambda:C.carry(low,s,4)),
        reject('omit a nonzero carry column',lambda:C.need(not C.carry(low,s,5)[1][1],'nonzero carry')),
        reject('reverse RIGHT word order',lambda:C.need(C.matrix(tiny,2) == C.matrix(tiny[::-1],2),'noncommuting order'))]
    altered = deepcopy(markers); first = min(altered); altered[first][2] += 1
    controls.append(reject('wrong marker owner with same operation count',lambda:C.need(altered == expected,'exact owner binding')))
    return dict(source_pr=5820,source_head='04b5db84b4b02bdc17e1c6287dfcf8b9c04199d4',
        routes=444,markers=len(markers),oracle_cases=cases,cocycle_cases=cocycles,exhaustive_cases=exhaustive,
        embedded_cases=embedded_cases,active_flat_addresses=addresses,layouts=layouts,oracle_sha256=stream_hash.hexdigest(),
        routes_and_invoices=receipts,rejected_controls=controls,
        limits=['Named carry corrections have positive tariffs; no free physical operation is assumed.',
                'Literal heads, cache erasure, ROW/tape tariffs, borrowing and full supplier admission remain open.'])


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write']:
        (P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        C.need(not sys.argv[1:] and result == json.loads((P/'RESULT.json').read_text()),'recorded exact result')
    print('PASS_G20_FUSED_QADIC_CARRIES')
    print(json.dumps({k:result[k] for k in ['routes','markers','oracle_cases','cocycle_cases','exhaustive_cases','active_flat_addresses']},sort_keys=True))
