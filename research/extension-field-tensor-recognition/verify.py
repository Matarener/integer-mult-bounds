"""Check exact certificates and complete small orbits. Apache-2.0."""
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('extension_recognize', HERE / 'recognize.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def fields():
    return [r.Field(p, f) for p, f in [(2, (0, 1)), (3, (0, 1)), (2, (1, 1, 1)),
            (2, (1, 1, 0, 1)), (3, (1, 0, 1)), (2, (1, 1, 0, 0, 1)), (5, (2, 0, 1))]]


def changed(t, u, v, w, f):
    ui, vi = r.inverse(u, f), r.inverse(v, f)
    n = len(t)
    return [[r.mv(w, r.tensor_value(t, r.column(ui, i), r.column(vi, j), f), f)
             for j in range(n)] for i in range(n)]


def random_gl(n, f, rng):
    a = r.identity(n)
    for _ in range(5 * n + 3):
        i = rng.randrange(n)
        c = rng.randrange(1, f.q)
        a[i] = [f.mul[c][x] for x in a[i]]
        if n > 1:
            j = (i + rng.randrange(1, n)) % n
            c = rng.randrange(f.q)
            a[i] = [f.add[x][f.mul[c][y]] for x, y in zip(a[i], a[j])]
    return a


def oracle_orbit(f):
    """Apply literal invertible matrices to each of the three tensor indices."""
    q = f.q
    matrices = [[[0, 1], [1, 0]], [[1, 1], [0, 1]]]
    if q > 2:
        primitive = next(a for a in range(1, q) if len({f.power(a, i) for i in range(q-1)}) == q-1)
        matrices.append([[primitive, 0], [0, 1]])
    powers = [q ** i for i in range(8)]
    def pack(t):
        return sum(x * powers[i] for i, x in enumerate(t))
    # The standard dual-number table has coefficients 000, 011, 101.
    seed = pack([1, 0, 0, 1, 0, 1, 0, 0])
    seen, queue = {seed}, [seed]
    for code in queue:
        values = [(code // a) % q for a in powers]
        for axis in (1, 2, 4):
            for a in matrices:
                out = values[:]
                for i in range(8):
                    if i & axis:
                        continue
                    x, y = values[i], values[i + axis]
                    out[i] = f.add[f.mul[a[0][0]][x]][f.mul[a[0][1]][y]]
                    out[i + axis] = f.add[f.mul[a[1][0]][x]][f.mul[a[1][1]][y]]
                next_code = pack(out)
                if next_code not in seen:
                    seen.add(next_code)
                    queue.append(next_code)
    return seen


def exhaustive(f):
    expected = oracle_orbit(f)
    accepted = set()
    digest = hashlib.sha256()
    for code in range(f.q ** 8):
        vals = [(code // f.q ** i) % f.q for i in range(8)]
        t = [[vals[4*i+2*j:4*i+2*j+2] for j in range(2)] for i in range(2)]
        cert, reason = r.recognize(t, f)
        require((cert is not None) == (code in expected), f'orbit disagreement: q={f.q}, tensor={code}, {reason}')
        if cert is not None:
            accepted.add(code)
            require(r.check_certificate(t, cert, f), 'exhaustive transporter')
            digest.update(code.to_bytes(4, 'big'))
    return {'field': f.q, 'domain': f.q ** 8, 'accepted': len(accepted), 'accepted_sha256': digest.hexdigest()}


def main():
    start = time.monotonic()
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"] == "input":
            data = (HERE.parents[1] / item["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == item["sha256"], "source bytes changed")
    fs = fields()
    for f in fs:
        for a, b, c in itertools.product(range(f.q), repeat=3):
            require(f.add[f.add[a][b]][c] == f.add[a][f.add[b][c]], 'additive associativity')
            require(f.mul[f.mul[a][b]][c] == f.mul[a][f.mul[b][c]], 'multiplicative associativity')
            require(f.mul[a][f.add[b][c]] == f.add[f.mul[a][b]][f.mul[a][c]], 'distributivity')
        for a in range(f.q):
            require(f.add[a][f.neg[a]] == 0 and f.mul[a][1] == a and f.power(a, f.q) == a, 'field laws')
    controls = 0
    for p, poly in [(4, (0,1)), (2, (0,0,1)), (2, (1,0,1)), (3, (2,0,1)), (2, (1,2,1))]:
        try:
            r.Field(p, poly)
        except ValueError:
            controls += 1
        else:
            raise RuntimeError('invalid field accepted')
    rng = random.Random(9405540)
    fixtures = products = labels = 0
    for f in fs:
        for hs in [[], [1], [2], [1,1], [1,2]]:
            if f.p ** sum(hs) > 9:
                continue
            t, _ = r.model(hs, f)
            n = len(t)
            for _ in range(3):
                u, v, w = (random_gl(n, f, rng) for _ in range(3))
                original = changed(t, u, v, w, f)
                cert, reason = r.recognize(original, f)
                require(cert is not None, 'positive fixture rejected: '+str((f.q, hs, reason)))
                require(cert['heights'] == hs and r.check_certificate(original, cert, f), 'wrong transporter')
                index = cert['sl_orbit_count']
                delta = f.mul[r.determinant(w, f)][f.inv[f.mul[r.determinant(u, f)][r.determinant(v, f)]]]
                require(cert['sl_orbit_label'] == f.power(delta, (f.q-1)//index), 'transporter-independent SL label')
                labels += 1
                sl = [random_gl(n, f, rng) for _ in range(3)]
                for matrix in sl:
                    scale = f.inv[r.determinant(matrix,f)]
                    matrix[0] = [f.mul[scale][x] for x in matrix[0]]
                second = changed(original, *sl, f)
                maps, why = r.sl_transporter(original, second, f)
                require(maps is not None, 'equal-label transport failed: '+str(why))
                require(all(r.determinant(maps[k],f) == 1 for k in ('F','G','H')), 'SL determinant')
                for i in range(n):
                    for j in range(n):
                        require(r.tensor_value(second,r.column(maps['F'],i),r.column(maps['G'],j),f)
                                == r.mv(maps['H'],original[i][j],f), 'SL transported product')
                bad = dict(cert)
                bad['W'] = [row[:] for row in cert['W']]
                bad['W'][0][0] = f.add[bad['W'][0][0]][1]
                require(not r.check_certificate(original, bad, f), 'altered transporter accepted')
                controls += 1
                fixtures += 1
                products += n*n
        n = 3
        square = [[[0]*n for _ in range(n)] for _ in range(n)]
        for i in range(n):
            square[0][i][i] = square[i][0][i] = 1
        require(r.recognize(square, f)[1] == 'height dimension', 'extra relation accepted')
        controls += 1
        # The dual action has an output module with a two-dimensional top.
        dual = [[[square[i][k][j] for k in range(n)] for j in range(n)] for i in range(n)]
        require(r.recognize(dual, f)[1] == 'nonregular nucleus module', 'nonregular module accepted')
        controls += 1
        split = [[[int(i == j == k) for k in range(2)] for j in range(2)] for i in range(2)]
        require(r.recognize(split, f)[1] == 'residue field or number of components', 'split algebra accepted')
        controls += 1
    f = fs[2]
    mu, _ = r.model([1], f)
    c = [[1, 2], [0, 1]]
    table = changed(mu, r.inverse(c,f), r.inverse(c,f), r.inverse(c,f), f)
    unit = [1,0]
    powers = r.columns([r.algebra_power(table, e, 2, unit, f) for e in r.identity(2)], 2)
    wrong_kernel = r.kernel(powers, 2, f)
    right_kernel = r.semilinear_kernel(table, unit, 1, f)
    require(wrong_kernel == [[3,1]] and right_kernel == [[2,1]], 'explicit semilinear fixture changed')
    require(r.algebra_power(table, wrong_kernel[0], 2, unit, f) == [1,0], 'untwisted kernel control')
    require(r.algebra_power(table, right_kernel[0], 2, unit, f) == [0,0], 'twisted kernel')
    direct_second = r.columns([r.algebra_power(table, e, 4, unit, f) for e in r.identity(2)],2)
    require(r.mm(powers,powers,f) != direct_second, 'untwisted matrix iterate control')
    controls += 2
    mu, _ = r.model([2], f)
    unit = [1,0,0,0]
    require(len(r.semilinear_kernel(mu, unit, 1, f)) == 2, 'p-kernel dimension')
    require(len(r.semilinear_kernel(mu, unit, 2, f)) == 3, 'q-kernel dimension')
    require(r.recognize(mu, f)[0]['heights'] == [2], 'q-power used as height one')
    controls += 1
    a = r.recognize(mu,f)[0]
    b = r.recognize(r.model([1,1],f)[0],f)[0]
    require((a['sl_orbit_count'],b['sl_orbit_count']) == (3,1), 'dimension-only character control')
    realized = set()
    for scalar in range(1,4):
        w = r.identity(4);w[0][0] = scalar
        cert,_ = r.recognize(changed(mu,r.identity(4),r.identity(4),w,f),f)
        realized.add(cert['sl_orbit_label'])
    require(realized == {1,2,3}, 'missing special-linear orbit')
    w = r.identity(4);w[0][0] = 2
    different = changed(mu,r.identity(4),r.identity(4),w,f)
    require(r.sl_transporter(mu,different,f)[1] == 'different special-linear orbits', 'different labels accepted')
    controls += 2
    for bad in [[], [[[4]]], [[[True]]], [[[0,0]]]]:
        try:
            r.recognize(bad,f)
        except ValueError:
            controls += 1
        else:
            raise RuntimeError('invalid tensor accepted')
    out = {'positive_presentations': fixtures, 'transported_basis_products': products,
           'independent_label_comparisons': labels, 'SL_transporters': labels, 'controls': controls,
           'explicit_F4_kernel': {'wrong': wrong_kernel, 'correct': right_kernel},
           'exhaustive': [exhaustive(fs[0]),exhaustive(fs[2])]}
    print(json.dumps(out,sort_keys=True))
    print('PASS_EXTENSION_FIELD_TENSOR_RECOGNITION')
    print(f'elapsed_seconds={time.monotonic()-start:.3f}')


if __name__ == '__main__':
    main()
