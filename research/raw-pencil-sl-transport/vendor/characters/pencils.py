"""Exact determinant maps for bounded supplied finite-field pencil models.

Credit the retained Kronecker lifts and field arithmetic. The regular block
normalization and mixed character assembly are new in this package.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha256
from itertools import product
from pathlib import Path
import importlib.util
import json

ROOT = Path(__file__).resolve().parent
for item in json.loads((ROOT / 'INPUTS.json').read_text()):
    if sha256((ROOT / item['local']).read_bytes()).hexdigest() != item['sha256']:
        raise ValueError('Frozen source differs: ' + item['local'])
spec = importlib.util.spec_from_file_location('credited_pencil', ROOT / 'source/pencil.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
Field = old.Field
need = old.require


def poly_mul(a, b, f):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] = f.add(out[i+j], f.mul(x, y))
    return out


def poly_power(a, n, f):
    out = [1]
    for _ in range(n):
        out = poly_mul(out, a, f)
    return out


def remainder(a, b, f):
    a = list(a)
    while len(a) >= len(b):
        x = f.mul(a[-1], f.inv(b[-1])); offset = len(a)-len(b)
        for j, y in enumerate(b):
            a[offset+j] = f.sub(a[offset+j], f.mul(x, y))
        a.pop()
    return a


def irreducible(a, f):
    for degree in range(1, (len(a)-1)//2+1):
        for low in product(range(f.q), repeat=degree):
            if not any(remainder(a, list(low)+[1], f)):
                return False
    return True


def companion(poly, f):
    n = len(poly)-1
    out = [[0]*n for _ in range(n)]
    for i in range(1, n):
        out[i][i-1] = 1
    for i in range(n):
        out[i][-1] = f.neg(poly[i])
    return out


def matrix_sum(a, b, x, y, f):
    return [[f.add(f.mul(x, u), f.mul(y, v)) for u, v in zip(row, other)]
            for row, other in zip(a, b)]


def evaluate(poly, matrix, f):
    n = len(matrix); out = [[0]*n for _ in range(n)]; power = old.identity(n)
    for coefficient in poly:
        out = matrix_sum(out, power, 1, coefficient, f)
        power = old.multiply(power, matrix, f)
    return out


def normalized(model, f):
    need(isinstance(model, (list, tuple)) and model, 'Nonempty supplied model')
    out = []; total_m = total_n = 0; keys = set()
    for block in model:
        need(isinstance(block, (list, tuple)) and block, 'Block record')
        side = block[0]
        if side in ('R', 'L'):
            need(len(block) == 3, 'Singular record arity')
            _, e, r = block
            need(type(e) is int and 0 <= e <= 5 and type(r) is int and 1 <= r <= 3, 'Singular bounds')
            key = (side, e); m = (e+(side == 'L'))*r; n = (e+(side == 'R'))*r
            out.append(dict(side=side, e=e, r=r, m=m, n=n, row=total_m, col=total_n, key=key))
        else:
            need(side in ('F', 'I'), 'Known block type')
            need(len(block) == (4 if side == 'F' else 3), 'Regular record arity')
            if side == 'F':
                _, poly, length, r = block
                need(isinstance(poly, (tuple, list)) and 2 <= len(poly) <= 4 and poly[-1] == 1 and
                     all(type(x) is int and 0 <= x < f.q for x in poly), 'Monic bounded polynomial')
                need(irreducible(poly, f), 'Irreducible regular primary')
                poly = tuple(poly)
            else:
                _, length, r = block; poly = (0, 1)
            need(type(length) is int and 1 <= length <= 3 and type(r) is int and 1 <= r <= 3, 'Regular bounds')
            key = (side, poly, length); degree = (len(poly)-1)*length
            m = n = degree*r
            out.append(dict(side=side, poly=poly, length=length, r=r, degree=degree,
                            m=m, n=n, row=total_m, col=total_n, key=key))
        need(key not in keys, 'Combine identical block types in the supplied model')
        keys.add(key); total_m += m; total_n += n
    need(0 < total_m <= 16 and 0 < total_n <= 16, 'Positive total dimensions at most sixteen')
    return out, total_m, total_n


def regular_instances(parts, f):
    out = []
    for part in parts:
        if part['side'] in ('F', 'I'):
            poly = poly_power(part['poly'], part['length'], f)
            j = companion(poly, f); identity = old.identity(len(j))
            a, b = (identity, j) if part['side'] == 'F' else (j, identity)
            key = (part['side'], tuple(poly))
            for i in range(part['r']):
                out.append(dict(a=a, b=b, key=key, part=part, row=part['row']+i*len(j), col=part['col']+i*len(j)))
    return out


def put(matrix, block, row, col):
    for i, values in enumerate(block):
        matrix[row+i][col:col+len(values)] = values


def slices(parts, m, n, f):
    a = [[0]*n for _ in range(m)]; b = [[0]*n for _ in range(m)]
    for part in parts:
        if part['side'] in ('R', 'L'):
            for i in range(part['e']):
                for j in range(part['r']):
                    x = part['row']+i*part['r']+j; y = part['col']+i*part['r']+j
                    a[x][y] = 1
                    if part['side'] == 'R': b[x][y+part['r']] = 1
                    else: b[x+part['r']][y] = 1
    for item in regular_instances(parts, f):
        put(a, item['a'], item['row'], item['col']); put(b, item['b'], item['row'], item['col'])
    return a, b


def singular_lift(part, action, determinant, f):
    d = old.identity(part['r']); d[0][0] = determinant
    if part['e']: p, q, _ = old.lift(part['e'], part['r'], action, d, f)
    else: p, q = [], old.transpose(old.inverse(d, f))
    return (q, p) if part['side'] == 'L' else (p, q)


def cyclic_normalize(a, b, action, f):
    """Use one primary block's affine chart and its cyclic vector."""
    first = matrix_sum(a, b, *action[0], f); second = matrix_sum(a, b, *action[1], f)
    finite = old.determinant(first, f) != 0
    base, other = (first, second) if finite else (second, first)
    need(old.determinant(base, f) != 0, 'A regular primary block has an invertible chart')
    inverse = old.inverse(base, f); h = old.multiply(inverse, other, f); n = len(h)
    v = [[int(i == 0)] for i in range(n)]; columns = []
    for _ in range(n):
        columns.append([row[0] for row in v]); v = old.multiply(h, v, f)
    krylov = old.transpose(columns); need(old.determinant(krylov, f) != 0, 'The fractional transform keeps the cyclic vector')
    ki = old.inverse(krylov, f); canonical = old.multiply(old.multiply(ki, h, f), krylov, f)
    poly = tuple(f.neg(row[-1]) for row in canonical)+(1,)
    need(canonical == companion(poly, f), 'Literal companion normalization')
    if not finite: need(poly == (0,)*n+(1,), 'The infinity chart is nilpotent')
    return ('F' if finite else 'I', poly), old.multiply(ki, inverse, f), old.transpose(krylov)


def slice_lift(parts, m, n, action, f):
    ps = [[0]*m for _ in range(m)]; qs = [[0]*n for _ in range(n)]
    for part in parts:
        if part['side'] in ('R', 'L'):
            p, q = singular_lift(part, action, 1, f)
            put(ps, p, part['row'], part['row']); put(qs, q, part['col'], part['col'])
    instances = regular_instances(parts, f); unused = set(range(len(instances)))
    for source in instances:
        key, p, q = cyclic_normalize(source['a'], source['b'], action, f)
        target = next((i for i in sorted(unused) if instances[i]['key'] == key), None)
        if target is None: return None
        unused.remove(target); dest = instances[target]
        put(ps, p, dest['row'], source['row']); put(qs, q, dest['col'], source['col'])
    return ps, qs, action


def norm_unit(poly, target, f):
    """Bounded exhaustive residue search; no general fast norm solver is claimed."""
    small = companion(poly, f)
    for coefficients in product(range(f.q), repeat=len(poly)-1):
        if old.determinant(evaluate(coefficients, small, f), f) == target:
            return coefficients
    raise ValueError('Finite field norm must be onto')


def fixed_generators(parts, m, n, f):
    out = []
    for part in parts:
        for u in range(1, f.q):
            p, q = old.identity(m), old.identity(n)
            if part['side'] in ('R', 'L'):
                bp, bq = singular_lift(part, old.identity(2), u, f)
            else:
                poly = poly_power(part['poly'], part['length'], f); j = companion(poly, f)
                coefficients = norm_unit(part['poly'], u, f) if part['side'] == 'F' else [u]
                bp = evaluate(coefficients, j, f); bq = old.transpose(old.inverse(bp, f))
                need(old.determinant(bp, f) == f.power(u, part['length']), 'Norm and length determinant')
            put(p, bp, part['row'], part['row']); put(q, bq, part['col'], part['col'])
            out.append((p, q))
    return out


def pair_mul(a, b, f):
    return tuple(f.mul(x, y) for x, y in zip(a, b))


def compile_model(model, f):
    parts, m, n = normalized(model, f); a, b = slices(parts, m, n, f)
    fixed = {(1, 1): (old.identity(m), old.identity(n))}; queue = [(1, 1)]
    generators = [(tuple(old.determinant(x, f) for x in pair), pair) for pair in fixed_generators(parts, m, n, f)]
    for key in queue:
        for char, pair in generators:
            target = pair_mul(key, char, f)
            if target not in fixed:
                fixed[target] = tuple(old.multiply(x, y, f) for x, y in zip(fixed[key], pair)); queue.append(target)
    image = {}; lifts = []; actions = 0
    for action in old.general_linear_two(f):
        actions += 1; lift = slice_lift(parts, m, n, action, f)
        if lift is None: continue
        need(old.fixes(a, b, lift, f), 'Literal regular and singular slice lift')
        char = tuple(old.determinant(x, f) for x in lift); lifts.append((char, lift))
        for key, pair in fixed.items():
            triple = pair_mul(char, key+(1,), f)
            image.setdefault(triple, (pair, lift))
    return dict(model=model, parts=parts, dimensions=(m, n), slices=(a, b), fixed=fixed, lifts=lifts,
                image=image, slice_actions=actions, field=f)


def witness(compiled, triple, action=None):
    f = compiled['field']; triple = tuple(triple)
    need(len(triple) == 3 and all(type(x) is int and 0 < x < f.q for x in triple), 'Nonzero determinant triple')
    need(triple in compiled['image'], 'Excluded determinant triple')
    pair, lift = compiled['image'][triple]
    if action is not None:
        choices = [(char, candidate) for char, candidate in compiled['lifts'] if candidate[2] == action]
        need(choices, 'Excluded prescribed slice action')
        char, lift = choices[0]
        need(char[2] == triple[2], 'Prescribed slice determinant')
        key = tuple(f.mul(x, f.inv(y)) for x, y in zip(triple[:2], char[:2]))
        need(key in compiled['fixed'], 'Excluded prescribed slice coset')
        pair = compiled['fixed'][key]
    result = tuple(old.multiply(x, y, f) for x, y in zip(pair, lift[:2]))+(lift[2],)
    need(old.fixes(*compiled['slices'], result, f), 'Literal determinant witness')
    need(tuple(old.determinant(x, f) for x in result) == triple, 'Requested determinant witness')
    return result


def tensor_image(slices, maps, f):
    a, b = slices; p, q, action = maps
    return tuple(old.multiply(old.multiply(p, matrix_sum(a, b, x, y, f), f), old.transpose(q), f) for x, y in action)


def correct_map(compiled, maps):
    f = compiled['field']; triple = tuple(old.determinant(x, f) for x in maps)
    h = witness(compiled, triple)
    result = tuple(old.multiply(g, old.inverse(x, f), f) for g, x in zip(maps, h))
    need(all(old.determinant(x, f) == 1 for x in result), 'Three determinant-one factors')
    need(tensor_image(compiled['slices'], maps, f) == tensor_image(compiled['slices'], result, f), 'Unchanged tensor image')
    return result


def orbit_labels(compiled):
    f = compiled['field']; labels = {}
    for triple in product(range(1, f.q), repeat=3):
        if triple not in labels:
            for delta in compiled['image']:
                labels[pair_mul(triple, delta, f)] = triple
    need(len(labels) == (f.q-1)**3 and len(set(labels.values()))*len(compiled['image']) == len(labels), 'Finite quotient cardinality')
    return labels
