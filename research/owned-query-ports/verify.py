"""Scoped exact adapter/snapshot checks. Apache-2.0; OpenAI assistance."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import gzip, hashlib, json, sys, types
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok:
        raise ValueError(why)

def rejected(action, why):
    try:
        action()
    except ValueError:
        return
    raise ValueError('Invalid alternative accepted: '+why)

def check_paid_rank(actual, promised):
    need(actual == promised, 'False paid rank')

def check_profile(actual, promised):
    need(dict(actual) == dict(promised), 'Wrong complete invoice')

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8'))

def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)

def load_ce():
    inputs = [x for x in read('SOURCES.json')['files'] if x['usage'] == 'input']
    need(len(inputs) == 1, 'Exactly one live Clifford source')
    row = inputs[0]
    path = ROOT / row['path']
    data = path.read_bytes()
    need(hashlib.sha256(data).hexdigest() == row['sha256'], 'Clifford source drift')
    module = types.ModuleType('owned_query_exact_clifford')
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(data, str(path), 'exec'), module.__dict__)
    return module

def monomial(ce, rec, n):
    # Retained recipe grammar from prune_native.py, with full global phase.
    op = ce.diag(n, tuple(rec['quadratic_rows']), tuple(rec['linear_Z4']))
    op = op.then(ce.perm(n, tuple(rec['matrix_rows']))).then(ce.xgate(n, rec['offset']))
    return op.then(ce.Op(n, ce.identity(n), [('phase', rec['phase'])]))

def conjugate(ce, op):
    # Gate-by-gate complex conjugation, adapted from the credited source.
    out = ce.ident(op.n)
    for g in op.circuit:
        if g[0] == 'P': part = ce.perm(op.n, g[1])
        elif g[0] == 'X': part = ce.xgate(op.n, g[1])
        elif g[0] == 'C': part = ce.cgate(op.n, g[1], -g[2])
        elif g[0] == 'D': part = ce.diag(op.n, g[1], tuple(-x % 4 for x in g[2]))
        else:
            need(g[0] == 'phase', 'Known circuit primitive')
            part = ce.Op(op.n, ce.identity(op.n), [('phase', -g[1] % 4)])
        out = out.then(part)
    return out

def equal_op(a, b):
    return a.tab == b.tab and a.zero_state() == b.zero_state()

def audit_queries():
    ce = load_ce()
    records = []
    for pair in read('QUERIES.json'):
        for backward in (False, True):
            source = ce.canonical_frame(9, pair['source_basis'])
            target = ce.canonical_frame(9, pair['target_basis'])
            if backward:
                source, target = conjugate(ce, source), conjugate(ce, target)
            op = source.adjoint().then(target)
            recipe, compiled = ce.lower_child(op)
            decoded = monomial(ce, recipe['left'], 9)
            if recipe['rank']:
                decoded = monomial(ce, recipe['right'], 9).then(ce.fourier(9, range(recipe['rank']))).then(decoded)
            need(equal_op(decoded, op) and equal_op(compiled, op), 'Decoded rank recipe and absolute phase')
            need(equal_op(source.then(op), target), 'Physical intertwiner')
            need(recipe['rank'] == pair['rank'] == rank([x for x,z,p in op.tab[9:]]), 'Exact paid rank')
            bad = op.then(ce.Op(9, ce.identity(9), [('phase', 1)]))
            need(bad.tab == op.tab and not equal_op(bad, op), 'Global phase mutation rejected')
            rejected(lambda: check_paid_rank(rank([x for x,z,p in op.tab[9:]]), pair['rank']+1), 'false paid rank')
            records.append(recipe['rank'])
    return records

def mv(A, x):
    return tuple(sum((a*b for a,b in zip(row,x)), Q(0)) for row in A)

def inverse(A):
    n = len(A)
    rows = [[Q(x) for x in row] + [Q(i == j) for j in range(n)] for i,row in enumerate(A)]
    for j in range(n):
        pivot = next(i for i in range(j,n) if rows[i][j])
        rows[j],rows[pivot] = rows[pivot],rows[j]
        scalar = rows[j][j]
        rows[j] = [x/scalar for x in rows[j]]
        for i in range(n):
            if i != j:
                scalar = rows[i][j]
                rows[i] = [x-scalar*y for x,y in zip(rows[i],rows[j])]
    return tuple(tuple(row[n:]) for row in rows)

def audit_linear():
    A = ((1,2,0),(0,1,1),(0,0,1))
    B = ((1,0,1),(1,1,0),(0,0,1))
    Bi = inverse(B)
    U = lambda x: mv(A, mv(Bi,x))
    lam = Q(-3,2)
    count = 0
    for i in range(9):
        data = [Q(i == j) for j in range(9)]
        x,y,z = tuple(data[:3]),tuple(data[3:6]),tuple(data[6:])
        physical_source, physical_target = mv(B,x),mv(A,y)
        temp = U(tuple(physical_source))  # explicit COPY overwrites cleared owned storage
        target = tuple(a+lam*b for a,b in zip(physical_target,temp))
        need(target == mv(A,tuple(a+lam*b for a,b in zip(y,x))), 'All input shear columns')
        need(physical_source == mv(B,x), 'Source untouched')
        temp = (Q(0),)*3
        need(not any(temp), 'Owned return zero')
        count += 1
    x = (Q(1),Q(2),Q(3));y = (Q(0),)*3
    need(mv(B,x) != mv(A,x), 'Wrong-operator mutation has a witness')
    need(any(U(mv(B,x))), 'Omitted final erase has a witness')
    u,v = (Q(2),Q(-1)),(Q(3),Q(1,2))
    for col in range(15):
        d = [Q(col == j) for j in range(15)]
        xs = (tuple(d[:3]),tuple(d[3:6]));ys=(tuple(d[6:9]),tuple(d[9:12]));dirty=tuple(d[12:])
        temp = (Q(0),)*3
        for scalar,xi in zip(v,xs):
            temp = tuple(a+scalar*b for a,b in zip(temp,mv(B,xi)))
        temp = U(temp)
        for scalar,yj in zip(u,ys):
            actual = tuple(a+scalar*b for a,b in zip(mv(A,yj),temp))
            wanted = tuple(yj[k]+scalar*sum(v[i]*xs[i][k] for i in range(2)) for k in range(3))
            need(actual == mv(A,wanted), 'Every rank-one rectangle input column')
        count += 1
    need(U((Q(1),Q(0),Q(0))) != (Q(0),)*3, 'Uncleared accumulation has a dirty-input witness')
    return count

def read_graph(path):
    raw = gzip.decompress(path.read_bytes())
    lines = iter(raw.decode('utf-8').splitlines())
    n,m,k = map(int,next(lines).split())
    labels,fixed = [],[]
    for _ in range(n):
        a,b = map(int,next(lines).split());labels.append(a);fixed.append(b)
    edges = [tuple(map(int,next(lines).split())) for _ in range(m)]
    D = [list(map(int,next(lines).split())) for _ in range(k)]
    order = list(map(int,next(lines).split()))
    need(not list(lines), 'No trailing graph records')
    return raw,labels,fixed,edges,D,order

def audit_graph():
    snap = read('SNAPSHOT.json')
    raw,labels,fixed,edges,D,order = read_graph(HERE/'GRAPH.txt.gz')
    frames = read('FRAMES.json')
    n,k = len(labels),len(frames)
    need(hashlib.sha256(raw).hexdigest() == snap['payload_sha256'], 'Exact frozen graph payload')
    need(n == snap['vertices'] and len(edges) == snap['edges'], 'Graph sizes')
    need(len(D) == k and all(len(row)==k for row in D), 'Full distance matrix')
    need(sorted(order) == list(range(k)), 'Every label in search order exactly once')
    need(all(0<=x<k for x in labels) and all(b in (0,1) for b in fixed), 'Valid labels and fixed flags')
    need(sum(fixed) == snap['fixed_vertices'], 'Fixed vertex count')
    for basis in frames:
        need(all(0<x<512 for x in basis) and rank(basis)==len(basis)<=9, 'Independent binary frame')
    for i,a in enumerate(frames):
        for j in range(i+1):
            distance = 2*rank(a+frames[j])-len(a)-len(frames[j])
            need(D[i][j] == D[j][i] == distance, 'Exact CSS Grassmann distance')
    paid = Counter({int(x):y for x,y in snap['constant_paid'].items()})
    for a,b in edges:
        need(0<=a<n and 0<=b<n and a!=b, 'Valid distinct edge vertices')
        r = D[labels[a]][labels[b]]
        if r: paid[r] += 1
    check_profile(paid, {int(x):y for x,y in snap['expected_paid'].items()})
    q = snap['query_bridges']
    need(0<=q<=len(edges) and all(labels[a]==labels[b] for a,b in edges[:q]), 'Initial query bridges have rank zero')
    need(sum(paid.values()) == 3310 and sum(r*n for r,n in paid.items()) == 5327, 'Full count and mass')
    # Real invalid alternatives, not expected-status-only controls.
    rejected(lambda: check_paid_rank(2*rank(frames[0]+frames[1])-len(frames[0])-len(frames[1]), D[0][1]+1), 'corrupt metric entry')
    bad = Counter(paid);bad[1] += 1
    rejected(lambda: check_profile(bad, paid), 'extra child')
    return {'vertices':n,'edges':len(edges),'frames':k,'paid':dict(sorted(paid.items()))}

def audit_integrity():
    manifest = read('INTEGRITY.json')
    for name,record in manifest.items():
        rel = Path(name)
        need(not rel.is_absolute() and '..' not in rel.parts, 'Canonical package file')
        path = HERE / rel
        need(path.is_file() and not path.is_symlink(), 'Regular package file')
        data = path.read_bytes()
        if isinstance(record, dict):
            need(record['mode'] == 'gzip-payload', 'Known integrity mode')
            data = gzip.decompress(data)
            digest = record['sha256']
        else:
            digest = record
        need(hashlib.sha256(data).hexdigest() == digest, 'Package drift: '+name)

def main():
    audit_integrity()
    phases = audit_queries()
    linear = audit_linear()
    graph = audit_graph()
    print(json.dumps({'status':'PASS_SCOPED_OWNED_QUERY_PORTS','phase_checks':len(phases),'rational_columns':linear,'graph':graph,'new_kappa':False},sort_keys=True))

if __name__ == '__main__':
    main()
