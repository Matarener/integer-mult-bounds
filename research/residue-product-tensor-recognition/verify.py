"""Check residue products. Ali Romman with OpenAI Codex. Apache-2.0."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
from collections import deque
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

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


def polynomial_field(modulus,f):
    d = len(modulus)-1
    table = []
    for i in range(d):
        row = []
        for j in range(d):
            v = [0]*(2*d-1)
            v[i+j] = 1
            for k in range(len(v)-1,d-1,-1):
                for z in range(d):
                    v[k-d+z] = f.add[v[k-d+z]][f.neg[f.mul[v[k]][modulus[z]]]]
            row.append(v[:d])
        table.append(row)
    require(r.field_table_valid(table,f),'fixture field is reducible')
    return table


def quadratic(f):
    for c,d in itertools.product(range(f.q),repeat=2):
        if all(f.total([f.mul[x][x],f.mul[d][x],c]) for x in range(f.q)):
            return polynomial_field([c,d,1],f)
    raise RuntimeError('quadratic fixture absent')


def exhaustive(f):
    field1 = [[[1]]]
    components = [[dict(degree=1,heights=[],field=field1)]*2,
                  [dict(degree=2,heights=[],field=quadratic(f))]]
    if f.p==2:
        components.append([dict(degree=1,heights=[1],field=field1)])
    expected = orbit(f,[r.product_model(cs,f) for cs in components])
    digest = hashlib.sha256()
    accepted = 0
    for code in range(f.q**8):
        vals = [(code//f.q**i)%f.q for i in range(8)]
        t = [[vals[4*i+2*j:4*i+2*j+2] for j in range(2)] for i in range(2)]
        cert,why = r.recognize(t,f)
        require((cert is not None)==(code in expected),str((f.q,code,why)))
        if cert is not None:
            require(r.check_certificate(t,cert,f),'exhaustive literal map')
            accepted += 1
            digest.update(code.to_bytes(4,'big'))
    return dict(q=f.q,tensors=f.q**8,accepted=accepted,sha256=digest.hexdigest())


def main():
    source = json.loads((HERE/'SOURCES.json').read_text())
    for item in source['external_inputs']:
        require(hashlib.sha256((HERE/item['local_path']).read_bytes()).hexdigest()==item['sha256'],'retained source changed')
    global r
    import recognize as r
    fs = [r.a.Field(2,[0,1]),r.a.Field(3,[0,1]),r.a.Field(2,[1,1,1]),r.a.Field(3,[1,0,1])]
    rng = random.Random(56615656)
    fixtures = products = controls = 0
    for f in fs:
        field1 = [[[1]]]
        field2 = quadratic(f)
        unit = dict(degree=1,heights=[],field=field1)
        ext = dict(degree=2,heights=[],field=field2)
        nil = dict(degree=2,heights=[1],field=field2)
        field3 = polynomial_field([1,1,0,1] if f.p==2 else [1,2,0,1],f)
        ext3 = dict(degree=3,heights=[],field=field3)
        nil3 = dict(degree=3,heights=[1],field=field3)
        cases = [[ext],[nil],[unit,nil],[ext,ext],[nil,nil],[ext3],[nil3]]
        if f.p==2:
            cases.append([dict(degree=2,heights=[2],field=field2)])
        for cs in cases:
            mu = r.product_model(cs,f)
            n = len(mu)
            if n>8:
                continue
            target_types = sorted((c['degree'],c['heights']) for c in cs)
            for _ in range(2):
                u,v,w = (random_gl(n,f,rng) for _ in range(3))
                t = changed(mu,u,v,w,f)
                cert,why = r.recognize(t,f)
                require(cert is not None,str((f.q,target_types,why)))
                require(sorted((c['degree'],c['heights']) for c in cert['components'])==target_types,'residue or height type')
                require(r.check_certificate(t,cert,f),'literal product')
                fixtures += 1
                products += n*n
                for key in ('U','V','W'):
                    bad = copy.deepcopy(cert);bad[key][0][0]=f.add[bad[key][0][0]][1]
                    require(not r.check_certificate(t,bad,f),'changed factor accepted')
                    controls += 1
                bad = copy.deepcopy(cert);bad['components'][0]['field'][0][0][0]=0
                require(not r.check_certificate(t,bad,f),'false coefficient field accepted')
                bad = copy.deepcopy(cert);bad['components'][0]['degree']+=1
                require(not r.check_certificate(t,bad,f),'false residue degree accepted')
                controls += 2
        # A local square-zero algebra of rank three over the extension has an extra relation.
        d = 2
        square = [[[0]*(3*d) for _ in range(3*d)] for _ in range(3*d)]
        for i,j in itertools.product(range(3),repeat=2):
            if i and j:
                continue
            for x,y in itertools.product(range(d),repeat=2):
                square[d*i+x][d*j+y][d*(i+j):d*(i+j+1)] = field2[x][y]
        require(r.recognize(square,f)[0] is None,'extra residue-local relation accepted')
        n = len(square)
        dual = [[[square[i][k][j] for k in range(n)] for j in range(n)] for i in range(n)]
        require(r.recognize(dual,f)[1]=='nonregular nucleus module','nonregular nonsplit module accepted')
        controls += 2
        # A reduced product of two fields is not a coefficient field.
        split = r.product_model([unit,unit],f)
        require(not r.field_table_valid(split,f),'reduced product called a field')
        controls += 1
    report = dict(presentations=fixtures,basis_products=products,controls=controls,
                  exhaustive=[exhaustive(f) for f in fs[:3]])
    print(json.dumps(report,sort_keys=True))
    print('PASS_RESIDUE_PRODUCT_TENSOR_RECOGNITION')


if __name__=='__main__':
    main()


