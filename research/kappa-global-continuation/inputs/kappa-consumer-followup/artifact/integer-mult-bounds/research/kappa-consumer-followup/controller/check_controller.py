#!/usr/bin/env python3
"""Exact bank factors and a source-bound dirty-helper retention component.

Apache-2.0. Prepared with substantial OpenAI Codex assistance. The pinned
controller, local native supplier and source-code predecessors retain credit.
This is a local/interface certificate, not a complete supplier admission.
"""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import ast
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HOSTS = (224, 225, 227, 229, 231, 232, 233, 234)


def need(value, message):
    if not value:
        raise ValueError(message)


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def plus(a, b):
    return [[x+y for x, y in zip(row, other)] for row, other in zip(a, b)]


def outer(a, b):
    return [[x*y for y in b] for x in a]


def inverse(a):
    n = len(a)
    block = [row[:] + identity(n)[i] for i, row in enumerate(a)]
    for j in range(n):
        p = next((i for i in range(j, n) if block[i][j]), None)
        need(p is not None, 'matrix is singular')
        block[j], block[p] = block[p], block[j]
        c = block[j][j]
        block[j] = [x/c for x in block[j]]
        for i in range(n):
            if i != j:
                c = block[i][j]
                block[i] = [x-c*y for x, y in zip(block[i], block[j])]
    return [row[n:] for row in block]


def mv(a, x):
    return [sum(v*w for v, w in zip(row, x)) for row in a]


def kron(a, b):
    return [[x*y for x in ar for y in br] for ar in a for br in b]


def ints(a):
    return [int(x) if Q(x).denominator == 1 else str(x) for x in a]


def determinant(a):
    a = [row[:] for row in a]
    value = Q(1)
    for j in range(len(a)):
        p = next((i for i in range(j, len(a)) if a[i][j]), None)
        if p is None:
            return Q(0)
        if p != j:
            a[j], a[p] = a[p], a[j]
            value = -value
        v = a[j][j]
        value *= v
        for i in range(j+1, len(a)):
            c = a[i][j]/v
            a[i] = [x-c*y for x, y in zip(a[i], a[j])]
    return value


def recipe():
    out = []
    for stage, pair in enumerate((0, 0, 0, 1, 1, 2, 2, 3, 3)):
        out.append(dict(kind='local', stage=stage, pair=pair, reverse=bool(stage % 2)))
        if stage in (1, 3, 5):
            out.append(dict(kind='bridge', dst=pair, src=pair+1, coefficient=1))
        if stage in (2, 4, 6):
            out.append(dict(kind='bridge', dst=pair, src=pair+1, coefficient=-1))
    for pair in (2, 1, 0):
        out.append(dict(kind='bridge', dst=pair+1, src=pair, coefficient=1))
    out.append(dict(kind='exchange'))
    return out


def bank_check():
    source = ROOT/'research/nine-stage-prefix-audit-seed70/verify.py'
    raw = source.read_bytes()
    tree = ast.parse(raw)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'recipe')
    ns = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), ns)
    need(recipe() == ns['recipe'](), 'actual nine-stage recipe differs')
    eye = identity(8)
    prefix = eye
    factors = []
    operations = []
    for event in recipe():
        if event['kind'] == 'exchange':
            break
        op = [row[:] for row in eye]
        if event['kind'] == 'bridge':
            a, b, c = event['dst'], event['src'], event['coefficient']
            op[2*a][2*b] = Q(c)
            op[2*b+1][2*a+1] = Q(-c)
            operations.append(('bridge', op))
        else:
            p, back = event['pair'], event['reverse']
            ex, ey = eye[2*p], eye[2*p+1]
            if back:
                op = plus(eye, outer([-x for x in ex], ey))
                right_a, right_b = [x+y for x, y in zip(ex, ey)], ey
            else:
                op = plus(eye, outer(ey, ex))
                right_a, right_b = ex, ex
            a = mv(inverse(prefix), right_a)
            b = mm([right_b], prefix)[0]
            need(sum(x*y for x, y in zip(a, b)) == 1, 'bank factor not a projection')
            factors.append((a, b))
            operations.append(('local', op, right_a, right_b, event['stage']))
        prefix = mm(op, prefix)
    want = [row[:] for row in eye]
    for p in range(4):
        want[2*p][2*p] = want[2*p+1][2*p+1] = Q(0)
        want[2*p][2*p+1] = Q(-1)
        want[2*p+1][2*p] = Q(1)
    need(prefix == want, 'ordinary controller is not the signed exchange')

    # Nine different exact 2x2 involutions. Distinct conjugating shears make
    # them noncommuting; an ordered replay therefore tests more than G^2=I.
    codes = []
    for j in range(9):
        shear = [[Q(1), Q(j+1)], [Q(0), Q(1)]]
        codes.append(mm(mm(shear, [[Q(-1), Q(0)], [Q(0), Q(1)]]), inverse(shear)))
    need(any(mm(g, h) != mm(h, g) for g in codes for h in codes), 'commuting fixture')
    i2, i16 = identity(2), identity(16)
    actual, residual = i16, i16
    for op in operations:
        if op[0] == 'bridge':
            step = kron(op[1], i2)
        else:
            _, ordinary, a, b, j = op
            difference = [[x-y for x, y in zip(row, other)] for row, other in zip(codes[j], i2)]
            step = mm(kron(ordinary, i2), plus(i16, kron(outer(a, b), difference)))
        actual = mm(step, actual)
    es = []
    for j, (a, b) in enumerate(factors):
        difference = [[x-y for x, y in zip(row, other)] for row, other in zip(codes[j], i2)]
        e = plus(i16, kron(outer(a, b), difference))
        need(mm(e, e) == i16, 'factor involution')
        es.append(e)
        residual = mm(e, residual)
    need(actual == mm(kron(prefix, i2), residual), 'noncommuting factorization')
    undo = i16
    for e in reversed(es):
        undo = mm(e, undo)
    need(mm(undo, residual) == i16, 'ordered inverse')
    wrong = i16
    for e in es:
        wrong = mm(e, wrong)
    need(mm(wrong, residual) != i16, 'reversed-order control was ineffective')

    rows = []
    for j, (a, b) in enumerate(factors):
        # Before the final signed exchange, physical X is FULL and physical
        # Y is FULL C_q^-1. The ordinary S maps normalized X to physical Y.
        aa, bb = mv(prefix, a), mm([b], inverse(prefix))[0]
        image_hole = any(aa[i] for i in (1, 3, 5, 7))
        query_hole = any(bb[i] for i in (1, 3, 5, 7))
        need(image_hole or query_hole, 'unexpected entirely FULL bank factor')
        rows.append(dict(stage=j, a=ints(a), b=ints(b), physical_a=ints(aa),
                         physical_b=ints(bb), image_touches_Y_hole=image_hole,
                         query_touches_Y_hole=query_hole))
    return dict(status='PASS_NONCOMMUTING_NINE_STAGE_BANK_FACTORS',
                source=str(source.relative_to(ROOT)), source_sha256=sha256(raw).hexdigest(),
                bank_order=['X0', 'Y0', 'X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3'],
                factors=rows, completely_common_FULL_factors=[],
                scope='Exact scalar bank factorization; physical cross-cover and payload operators are not assigned zero cost.')


def load_module(path):
    # Execute the exact supplied source bytes, avoiding stale bytecode.
    ns = {'__name__':'retained_component', '__file__':str(path)}
    exec(compile(path.read_bytes(), str(path), 'exec'), ns)
    return type('Module', (), ns)


def retained_code(m, R, A, bank, frame):
    events = []
    for k, query in enumerate(R):
        events.append(m.clear(frame))
        for p, value in sorted(query.items()):
            events.append(m.scalar(('C', 0), ('L', bank+p), value, frame))
        events.append(m.scalar(('L', HOSTS[k]), ('C', 0), Q(1), frame))
        for p, row in enumerate(A):
            if k in row:
                events.append(m.scalar(('L', bank+p), ('C', 0), row[k], frame))
        events.append(m.clear(0))
    return events


def retention_check(recovered, out):
    module_path = recovered/'modern_native_component.py'
    m = load_module(module_path)
    inp = recovered/'modern-source/inputs'
    receipt = m.read(inp/'NATIVE-RECEIPT.json')
    need(m.digest(inp/'NATIVE-RECEIPT.json') == m.NATIVE_RECEIPT_SHA, 'native supplier receipt')
    result = dict(status='PASS_LOCAL_DIRTY_HELPER_RETENTION',
                  helper_hosts=list(HOSTS), component_sha256=m.digest(module_path), providers={})
    out.mkdir(parents=True, exist_ok=True)
    for name, item in receipt['providers'].items():
        loc = inp/'native-cache'/item['word_sha256']/'local'
        for file in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz'):
            need(m.digest(loc/file) == item['complete_native_files']['local/'+file], 'source native payload')
        word, programs = [m.read(loc/file) for file in ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz')]
        R, K, P, J, clean, dirty = m.clean_reconstruction(word, programs)
        need(all(word['start'][h] == 0 and word['final'][h] == 1 for h in HOSTS), 'host boundary frame')
        need(word['frames'][0] == [] and sorted(word['frames'][1]) == [1 << j for j in range(9)], 'I/FULL frame semantics')
        need(all(not any(e[0]=='residual_adapter' and e[2]==h for e in programs['forward']) for h in HOSTS), 'nontrivial helper wrapper')
        A = []
        Z = []
        for k, p in zip(K, P):
            a = {j:-v for j, v in k.items()}; m.add(a,p,Q(12)); A.append(a)
            z = k.copy(); m.add(z,p,Q(-13)); Z.append(z)
        need(m.matmul(R, A) == [{i:Q(-2)} for i in range(8)], 'RA=-2I')
        need(m.matmul(R, Z) == [{i:Q(1)} for i in range(8)], 'RZ=I')
        G = m.matmul(A,R)
        for p,row in enumerate(G):m.add(row,{p:Q(1)})
        need(m.matmul(R,G) == [{j:-x for j,x in row.items()}for row in R], 'RG=-R')
        C = [{j:12*x for j,x in row.items()}for row in m.matmul(P,R)]
        changed = {}
        tests = {}
        for orientation in ('forward', 'backward'):
            back = orientation == 'backward'
            bank, frame = (112,0) if back else (0,1)
            code = retained_code(m,R,A,bank,frame)
            # Canonical I/FULL helper labels have no residual wrapper; the
            # capture uses the exact same query accumulator as the G scatter.
            for event in code:
                if event[0] == 'scalar' and event[1][0] == 'add' and event[1][1][0] == 'L':
                    h = event[1][1][1]
                    if h in HOSTS:
                        need(event[1][2] == ['C',0] and event[2] == frame, 'retention ADD chart')
                        need((word['start'] if back else word['final'])[h] == frame, 'retention host chart mismatch')
            patch = m.repair(C,word,back)
            changed[orientation] = patch+code+clean[orientation] if back else clean[orientation]+code+patch
            actual = m.replay(changed[orientation])
            for p in range(632):
                expected = {(p,()):Q(1)}
                if back and p < 112:m.add(expected,{(112+p,()):Q(-1)})
                elif back and p < 224:expected={(112+j,()):v for j,v in G[p-112].items()}
                elif not back and p < 112:expected={(j,()):v for j,v in G[p].items()}
                elif not back and p < 224:m.add(expected,{(j,()):v for j,v in G[p-112].items()})
                elif p in HOSTS:m.add(expected,{(bank+j,()):v for j,v in R[HOSTS.index(p)].items()})
                need(actual['L',p] == expected, f'all-column retained endpoint {name}:{orientation}:{p}')
            need(all(not row for (kind,_),row in actual.items() if kind in 'CZ'), 'retention private cleanup')
            double = m.replay(code+code)
            need(all(double['L',p] == {(p,()):Q(1)} for p in range(632)), 'augmented source code not involutory')
            bill = m.scalar_bill(changed[orientation])
            need(bill['real_primitives'] == 179964, 'retention scalar invoice')
            profile = Counter(m.core_frame_check(word,clean[orientation])) + Counter({1:8})
            need(dict(profile) == {1:2448,2:725,3:224,4:102,5:20}, 'retention native profile')
            tests[orientation] = dict(input_columns=632, scalar_bill=bill,
                                      native_rank_mass=sum(k*v for k,v in profile.items()),
                                      additional_scalar_ADDs=8,
                                      initial_dirty_columns_kept=list(HOSTS),
                                      private_outputs_zero=True,
                                      augmented_code_square='identity on all 632 columns')
        # The clean-query-host variant has an explicit unit 16x16 minor in
        # Tclean-I, on source pivot and host rows/columns. This is a control
        # against treating its eight records as an eight-rank update.
        aa = list(m.PIVOTS)
        minor = []
        for p in aa:
            minor.append([G[p].get(j,Q(0))-Q(p==j) for j in aa] + [Z[p].get(k,Q(0))for k in range(8)])
        for k in range(8):
            minor.append([R[k].get(j,Q(0))for j in aa] + [Q(-int(k==j))for j in range(8)])
        need(abs(determinant(minor)) == 1, 'clean query rank-16 unit minor')
        payload = json.dumps(changed,sort_keys=True,separators=(',',':')).encode()
        (out/f'RETAINED-PROGRAMS-{name}.json.gz').write_bytes(gzip.compress(payload,mtime=0))
        result['providers'][name] = dict(word_sha256=item['word_sha256'],
            source_program_sha256=m.digest(loc/'LOCAL-PROGRAMS.json.gz'),
            changed_payload_sha256=sha256(payload).hexdigest(), checks=tests,
            I_to_FULL_helpers=sum(word['start'][h]==0 and word['final'][h]==1 for h in range(224,632)),
            clean_query_variant_update_rank=16, clean_query_minor_det=str(determinant(minor)))
    result['scope'] = 'New local dirty-state contract on actual PR3734 helper roles. Existing ownership/hosting assumes local restoration and is not admitted unchanged. Captured records contain arbitrary initial helper dirt; no free query-field credit.'
    result['remaining'] = ['Actual helper owner trajectories and their transported query images',
        'Complete dirty-state cancellation and terminal retirement',
        'Complete added native child, memory, precision and tape invoice']
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--recovered',type=Path,default=HERE.parents[3]/'recovered-involutory')
    ap.add_argument('--out',type=Path,default=HERE/'evidence')
    args = ap.parse_args()
    result = dict(bank=bank_check(),retention=retention_check(args.recovered,args.out))
    (args.out/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS_CONTROLLER_AND_DIRTY_RETENTION: nine ordered bank factors, zero factors supported only in physical FULL banks; both PR3734 words, 632 columns, 8 added ADDs, mass5078, scalar179964; no supplier/kappa admission.')


if __name__ == '__main__':
    main()
