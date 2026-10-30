"""Exact framed P112 co-delivery kernel; no supplier or kappa admission."""
from __future__ import annotations
import argparse
from collections import Counter
import copy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/community-frontier1094-audit/selected-replay.tar.gz'
MEMBER = 'candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz'
LABELS = [319,289,274,268,140,146,161,191]
E = [[-1,1,1,-1],[-1,1,-1,1],[1,1,-1,-1],[1,1,1,1],
     [-1,1,-1,-1],[-1,1,1,1],[1,1,1,-1],[1,1,-1,1]]
U = [[-1,0,0,1,1,0,0,-1],[-1,0,1,0,0,1,0,-1],[-1,1,0,0,0,0,1,-1],
     [1,-1,-1,-1,0,0,0,2],[1,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0],
     [0,0,0,0,0,0,1,0],[0,0,0,0,0,0,0,1]]


def need(ok, label):
    if not ok:
        raise ValueError(label)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def transpose(a):
    return list(map(list, zip(*a)))


def multiply(a,b):
    return [[sum(x*y for x,y in zip(row,col)) for col in transpose(b)] for row in a]


def difference(a,b):
    return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]


def determinant(a):
    work = [[Q(x) for x in row] for row in a]
    out = Q(1)
    for j in range(len(work)):
        pivot = next((i for i in range(j,len(work)) if work[i][j]),None)
        if pivot is None:
            return Q(0)
        if pivot != j:
            work[j],work[pivot] = work[pivot],work[j]
            out = -out
        out *= work[j][j]
        for i in range(j+1,len(work)):
            scale = work[i][j]/work[j][j]
            work[i] = [x-scale*y for x,y in zip(work[i],work[j])]
    return out


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length()-1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def basis(rows):
    out = []
    for row in rows:
        if rank(out+[row]) > len(out):
            out.append(row)
    return out


def span(rows):
    out = [0]
    for row in rows:
        out += [x^row for x in out]
    return sorted(out)


def selected_data():
    with tarfile.open(ROOT / ARCHIVE) as archive:
        payload = gzip.decompress(archive.extractfile(MEMBER).read())
    need(hashlib.sha256(payload).hexdigest() ==
         '4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c', 'word pin')
    w = json.loads(payload)
    ports = [w['ports'].index(q) for q in LABELS]
    centres = {role:i for i,role in enumerate(w['centers'])}
    S = [[Q(0)]*8 for _ in range(8)]
    for op,dst,src,a,b,*_ in w['cut']:
        need(op == 'add' and 112 <= dst < 224 and src in centres, 'destination-first cut form')
        if dst-112 in ports:
            S[ports.index(dst-112)][centres[src]] += Q(a,b)
    centre_labels = []
    for f in w['center_frames']:
        candidates = [q for q in range(1,512)
                      if all((q&r).bit_count()%2 == 0 for r in w['frames'][f])]
        need(len(candidates) == 1, 'centre normal')
        centre_labels += candidates
    K, M = multiply(E,transpose(E)), multiply(U,E)
    need(determinant(U) == -1,'unimodular integer output basis')
    need(multiply(transpose(E),E) == [[8*int(i==j) for j in range(4)] for i in range(4)],
         'four independent query payloads')
    need(M[:4] == [[0]*4 for _ in range(4)], 'four kernel rows')
    need(all((K[i][j]//2+1)%2 == (LABELS[i]&LABELS[j]).bit_count()%2
             for i in range(8) for j in range(8)), 'root/port parity')
    D = multiply(transpose(S),difference(M,E))
    need(sum(x != 0 for row in D for x in row) == 2, 'centre support')
    need(D[6][2] == Q(1,2) and D[7][2] == -Q(1,2), 'centre coefficients')
    A = basis(LABELS)
    B = basis(q for q in span(A) if all((q&r).bit_count()%2 == 0 for r in LABELS[4:]))
    need((len(A),len(B)) == (4,3), 'nested frame dimensions')
    need(all((q&centre_labels[j]).bit_count()%2 == 0 for q in B for j in (6,7)),
         'centre output compatibility')
    return dict(ports=ports,centres=centre_labels,S=S,K=K,M=M,D=D,A=A,B=B)


class Native:
    def __init__(self, compiler, oracle):
        self.c, self.o = compiler, oracle
        self.cache = {}

    def lower(self, op):
        key = json.dumps(op.circuit,sort_keys=True)
        if key not in self.cache:
            record,_ = self.c.lower_child(op)
            self.o.equal(self.o.recipe(record),op.circuit,'exact native phase and Pauli action')
            self.cache[key] = record
        return self.cache[key]


def execute(data, native, mode, wrong_centre=False):
    c = native.c
    frames = {'0':c.ident(9),'A':c.canonical_frame(9,data['A']),
              'B':c.canonical_frame(9,data['B']),'FULL':c.fourier(9)}
    normals = LABELS + data['centres']
    for i,q in enumerate(normals):
        frames['T'+str(i)] = frames['FULL'].then(c.cgate(9,q).adjoint())
    for i,q in enumerate(LABELS):
        frames['X'+str(i)] = c.cgate(9,q)
    current = ['X'+str(i) for i in range(8)] + ['0']*17
    values = [[Q(i==j) for j in range(25)] for i in range(25)]
    hist, scalars = Counter(), Counter()

    def move(r,f):
        if current[r] != f:
            op = frames[current[r]].adjoint().then(frames[f])
            record = native.lower(op)
            if record['rank']:
                hist[record['rank']] += 1
            current[r] = f

    def add(dst,src,coef):
        need(current[dst] == current[src], 'cross-frame scalar ADD')
        values[dst] = [x+coef*y for x,y in zip(values[dst],values[src])]
        scalars[str(coef)] += 1

    zero_ports = mode in ('zero_cut','actual_zero_scatter')
    if mode == 'actual_zero_scatter':
        for i in range(8):
            for j in range(8):
                if data['S'][i][j]:
                    if wrong_centre:
                        add(16+j,8+i,data['S'][i][j])
                    else:
                        add(8+i,16+j,data['S'][i][j])
    for i in range(8):
        move(i,'A')
    if not zero_ports:
        for i in range(4,8):
            move(8+i,'B')
    if mode == 'framed_centres':
        for j in (6,7):
            move(16+j,'B')
    for k in range(4):
        # The owned private array may start dirty. Clearing is explicit.
        values[24] = [Q(0)]*25
        scalars['CLEAR'] += 1
        current[24] = 'A'  # a zero array can be initialized in this representation
        for i in range(8):
            add(24,i,Q(E[i][k]))
        move(24,'0' if zero_ports else 'B')
        for i in range(8):
            coefficient = E[i][k] if mode == 'actual_zero_scatter' else data['M'][i][k]
            if coefficient:
                add(8+i,24,Q(coefficient))
        if mode == 'zero_centres' and any(row[k] for row in data['D']):
            move(24,'0')
        for j in range(8):
            if mode != 'actual_zero_scatter' and data['D'][j][k]:
                factor = 1 if wrong_centre else -1
                add(16+j,24,factor*data['D'][j][k])
    values[24] = [Q(0)]*25
    scalars['CLEAR'] += 1
    current[24] = '0'
    for i in range(8):
        move(i,'FULL')
    if not zero_ports:
        for i in range(8):
            move(8+i,'T'+str(i))
    if mode == 'framed_centres':
        for j in (6,7):
            move(16+j,'T'+str(8+j))
    if mode == 'zero_cut':
        for i in range(8):
            for j in range(8):
                if data['S'][i][j]:
                    add(16+j,8+i,data['S'][i][j])
    expected = [[Q(i==j) for j in range(25)] for i in range(25)]
    updated = data['K'] if mode == 'actual_zero_scatter' else multiply(data['M'],transpose(E))
    centre = multiply(data['D'],transpose(E))
    for i in range(8):
        expected[8+i][:8] = updated[i]
    for j in range(8):
        for i in range(8):
            expected[16+j][i] = Q(0) if mode == 'actual_zero_scatter' else -centre[j][i]
    if mode == 'actual_zero_scatter':
        for i in range(8):
            for j in range(8):
                expected[8+i][16+j] = data['S'][i][j]
    if mode == 'zero_cut':
        product = multiply(transpose(data['S']),data['K'])
        for j in range(8):
            expected[16+j][:8] = product[j]
            for i in range(8):
                expected[16+j][8+i] = data['S'][i][j]
    expected[24] = [Q(0)]*25
    need(values == expected,'exact arbitrary-data endpoint')
    end_frames = ['FULL']*8 + [('0' if zero_ports else 'T'+str(i)) for i in range(8)] + ['0']*9
    if mode == 'framed_centres':
        for j in (6,7):
            end_frames[16+j] = 'T'+str(8+j)
    need(current == end_frames,'physical endpoint representations')
    wanted = {'framed_centres':148,'zero_centres':135,'zero_cut':80,'actual_zero_scatter':80}[mode]
    need(sum(r*n for r,n in hist.items()) == wanted,'complete module rank mass')
    if not zero_ports:
        need(hist[1] == 4,'four distinct query-copy lifetimes')
    scalar_allowance = 2*scalars['CLEAR']
    for coefficient,count in scalars.items():
        if coefficient != 'CLEAR':
            value = Q(coefficient)
            need(abs(value.numerator) == 1 and value.denominator in (1,2,4),'dyadic scalar alphabet')
            scalar_allowance += count*{1:8,2:10,4:12}[value.denominator]
    return dict(profile=dict(sorted(hist.items())),rank_mass=wanted,scalar_adds=dict(scalars),
                scalar_real_primitive_allowance=scalar_allowance,
                final_frames=current,independent_scalar_columns=25,owned_private_arrays=1)


def calculate():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],row['path'])
    c = load('p112_kernel_clifford','research/p104-native-channel/vendor/clifford_exact.py')
    o = load('p112_kernel_gaussian','research/p104-native-channel/vendor/native_verify.py')
    data = selected_data()
    native = Native(c,o)
    modes = {m:execute(data,native,m) for m in
             ('framed_centres','zero_centres','zero_cut','actual_zero_scatter')}
    try:
        execute(data,native,'zero_cut',wrong_centre=True)
    except ValueError as error:
        need(str(error) == 'exact arbitrary-data endpoint','wrong mutation failure')
    else:
        raise ValueError('wrong centre sign accepted')
    try:
        execute(data,native,'actual_zero_scatter',wrong_centre=True)
    except ValueError as error:
        need(str(error) == 'exact arbitrary-data endpoint','wrong orientation-control failure')
    else:
        raise ValueError('reversed selected scatter accepted')
    A,B = c.canonical_frame(9,data['A']),c.canonical_frame(9,data['B'])
    record = native.lower(A.adjoint().then(B))
    need(record['rank'] == 1,'rank-one transfer')
    literal = A.adjoint().then(B).circuit
    for column in range(512):
        need(o.state(o.recipe(record),column) == o.state(literal,column),'dense native copy column')
    bad = copy.deepcopy(record)
    bad['left']['phase'] = (bad['left']['phase']+1)%4
    try:
        o.equal(o.recipe(bad),literal,'phase mutation')
    except ValueError:
        pass
    else:
        raise ValueError('wrong global phase accepted')
    zero_drop = native.lower(A.adjoint())
    need(zero_drop['rank'] == 4,'fixed-zero cut requires rank-four drop')
    digest = hashlib.sha256(json.dumps(list(native.cache.values()),sort_keys=True).encode()).hexdigest()
    return dict(status='PASS_P112_NATIVE_CO_DELIVERY_BLOCK',selected_kappa_unchanged='0.001672660197076918',
                source_labels=LABELS,source_ports=data['ports'],gather_basis=data['A'],reader_basis=data['B'],
                source_to_gather_rank=3,gather_to_full_rank=5,reader_to_target_rank=5,
                framed_transfer_rank=1,fixed_zero_drop_rank=4,dense_copy_columns=512,
                framed_transfer_recipe=record,fixed_zero_drop_recipe=zero_drop,
                exact_native_recipes=len(native.cache),native_recipes_sha256=digest,modes=modes,
                selected_scatter_direction='ports <- ports + S centres; centres unchanged',
                abstract_reader_direction='centres <- centres + S^T ports; not the selected scatter',
                controls=['wrong centre sign rejected','reversed actual scatter rejected',
                          'wrong global phase rejected','fixed-zero copy costs four'],
                missing=['selected chronological producer and matched consumer','whole-owner hosting and precision invoice',
                         'complete bit-side improvement and kappa above 0.002'])


def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');args=p.parse_args()
    result=json.dumps(calculate(),indent=2,sort_keys=True)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(result)
    else:
        need((HERE/'RESULT.json').read_text() == result,'receipt differs')
    print('PASS_P112_NATIVE_CO_DELIVERY_BLOCK copy=1 fixed_zero=4 modes=4 no_new_kappa')


if __name__ == '__main__':
    main()
