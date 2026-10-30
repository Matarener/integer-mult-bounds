"""Check the product recognizer. Ali Romman with OpenAI Codex. Apache-2.0."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
from collections import deque

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def changed(t, u, v, w, f):
    n = len(t)
    ui, vi = r.a.inverse(u, f), r.a.inverse(v, f)
    return [[r.a.mv(w, r.a.tensor_value(t, r.a.column(ui, i), r.a.column(vi, j), f), f)
             for j in range(n)] for i in range(n)]


def random_gl(n, f, rng, special=False):
    m = r.a.identity(n)
    for _ in range(4*n):
        if n > 1:
            i, j = rng.sample(range(n), 2)
            c = rng.randrange(f.q)
            m[i] = [f.add[x][f.mul[c][y]] for x, y in zip(m[i], m[j])]
    if not special:
        for i in range(n):
            c = rng.randrange(1, f.q)
            m[i] = [f.mul[c][x] for x in m[i]]
    return m


def orbit(f, seeds):
    """Apply GL2 generators directly to the three coefficient indices."""
    generators = [[[0,1],[1,0]]]
    generators.extend([[[1,c],[0,1]] for c in range(1,f.q)])
    generators.extend([[[c,0],[0,1]] for c in range(2,f.q)])

    def pack(vals):
        return sum(c*f.q**i for i,c in enumerate(vals))

    seen = {pack(sum(sum(t, []), [])) for t in seeds}
    queue = deque(seen)
    while queue:
        code = queue.popleft()
        vals = [(code//f.q**i)%f.q for i in range(8)]
        for axis in (1,2,4):
            for m in generators:
                out = vals[:]
                for i in range(8):
                    if not i & axis:
                        x,y = vals[i],vals[i+axis]
                        out[i] = f.add[f.mul[m[0][0]][x]][f.mul[m[0][1]][y]]
                        out[i+axis] = f.add[f.mul[m[1][0]][x]][f.mul[m[1][1]][y]]
                value = pack(out)
                if value not in seen:
                    seen.add(value)
                    queue.append(value)
    return seen


def exhaustive(f):
    seeds = [r.product_model([[],[]],f)]
    if f.p == 2:
        seeds.append(r.product_model([[1]],f))
    expected = orbit(f,seeds)
    accepted = 0
    digest = hashlib.sha256()
    for code in range(f.q**8):
        vals = [(code//f.q**i)%f.q for i in range(8)]
        t = [[vals[4*i+2*j:4*i+2*j+2] for j in range(2)] for i in range(2)]
        cert, why = r.recognize(t,f)
        require((cert is not None) == (code in expected), str((f.q,code,why)))
        if cert is not None:
            require(r.check_certificate(t,cert,f),'literal exhaustive certificate')
            accepted += 1
            digest.update(code.to_bytes(4,'big'))
    return {'q':f.q,'tensors':f.q**8,'accepted':accepted,'sha256':digest.hexdigest()}


def main():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for item in sources['external_inputs']:
        require(hashlib.sha256((HERE/item['local_path']).read_bytes()).hexdigest() == item['sha256'], 'retained source changed')
    global r
    import recognize as r
    fields = [r.a.Field(2,[0,1]),r.a.Field(3,[0,1]),r.a.Field(2,[1,1,1]),
              r.a.Field(2,[1,1,0,1]),r.a.Field(3,[1,0,1])]
    rng = random.Random(56565637)
    fixtures = products = transports = controls = 0
    for f in fields:
        for types in [[[]],[[],[]],[[],[],[]],[[],[1]],[[1],[1]],[[],[2]],[[],[1,1]]]:
            types = sorted(types)
            mu = r.product_model(types,f)
            n = len(mu)
            if n > 9:
                continue
            for _ in range(2):
                u,v,w = (random_gl(n,f,rng) for _ in range(3))
                t = changed(mu,u,v,w,f)
                cert,why = r.recognize(t,f)
                require(cert is not None, str((f.q,types,why)))
                require(cert['types'] == types and r.check_certificate(t,cert,f),'factor types or products')
                delta = f.mul[r.a.determinant(w,f)][f.inv[f.mul[r.a.determinant(u,f)][r.a.determinant(v,f)]]]
                require(cert['sl_orbit_label'] == f.power(delta,(f.q-1)//cert['sl_orbit_count']),'label independent of recovered basis')
                other = changed(t,*(random_gl(n,f,rng,True) for _ in range(3)),f)
                maps,why = r.sl_transporter(t,other,f)
                require(maps is not None, str(why))
                require(all(r.a.determinant(m,f)==1 for m in maps.values()),'SL determinant')
                for i,j in itertools.product(range(n),repeat=2):
                    require(r.a.tensor_value(other,r.a.column(maps['F'],i),r.a.column(maps['G'],j),f)
                            == r.a.mv(maps['H'],t[i][j],f),'SL literal coefficient')
                fixtures += 1
                products += n*n
                transports += 1
                for key in ('U','V','W'):
                    bad = copy.deepcopy(cert)
                    bad[key][0][0] = f.add[bad[key][0][0]][1]
                    require(not r.check_certificate(t,bad,f),'changed factor accepted')
                    controls += 1
                for key in ('sl_orbit_count','sl_orbit_label'):
                    bad = copy.deepcopy(cert); bad[key] = 0
                    require(not r.check_certificate(t,bad,f),'changed character accepted')
                    controls += 1
        # A nonsplit quadratic field is outside the declared product class.
        if f.q in (2,3):
            c = 1 if f.q == 2 else 2
            d = 1 if f.q == 2 else 0
            ext = [[[1,0],[0,1]],[[0,1],[c,d]]]
            require(r.recognize(ext,f)[1] == 'nonsplit residue field','nonsplit field accepted')
            controls += 1
        # The square-zero local algebra has two tangent generators and dimension 3.
        square = [[[0]*3 for _ in range(3)] for _ in range(3)]
        for i in range(3):
            square[0][i][i] = square[i][0][i] = 1
        require(r.recognize(square,f)[0] is None,'extra local relation accepted')
        dual = [[[square[i][k][j] for k in range(3)] for j in range(3)] for i in range(3)]
        require(r.recognize(dual,f)[1] == 'nonregular nucleus module','nonregular dual accepted')
        controls += 2
    # Over F4 the repeated field factors have three SL classes.
    f = fields[2]
    mu = r.product_model([[],[]],f)
    labels = set()
    for c in range(1,f.q):
        w = [[c,0],[0,1]]
        t = changed(mu,r.a.identity(2),r.a.identity(2),w,f)
        labels.add(r.recognize(t,f)[0]['sl_orbit_label'])
        if c != 1:
            require(r.sl_transporter(mu,t,f)[0] is None,'unequal SL labels accepted')
            controls += 1
    require(labels == {1,2,3},'missing split-product SL class')
    # The component permutation sign must be applied to the actual factor maps.
    f = fields[1]
    mu = r.product_model([[],[2]],f)
    permutation = r.a.identity(10)[9:]+r.a.identity(10)[:9]
    t = changed(mu,permutation,permutation,permutation,f)
    cert,_ = r.recognize(t,f)
    require(cert['sl_orbit_count'] == 2 and cert['sl_orbit_label'] == 2,'component-order sign')
    controls += 1
    out = {'presentations':fixtures,'basis_products':products,'SL_transporters':transports,
           'rejection_controls':controls,'exhaustive':[exhaustive(f) for f in fields[:3]]}
    print(json.dumps(out,sort_keys=True))
    print('PASS_SPLIT_PRODUCT_TENSOR_RECOGNITION')


if __name__ == '__main__':
    main()
