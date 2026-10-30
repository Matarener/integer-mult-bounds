#!/usr/bin/env python3
"""Replay raw pencils against separate strict-equivalence orbits."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import decompose as d


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    sources = json.loads((ROOT/'SOURCES.json').read_text())
    count = 0
    for row in sources['files']:
        if row['usage'] == 'input':
            path = ROOT.parents[1]/row['path']
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], 'source hash')
            count += 1
    return count


def flat_matrices(t, m, n):
    return [list(t[i*n:(i+1)*n]) for i in range(m)], [list(t[m*n+i*n:m*n+(i+1)*n]) for i in range(m)]


def neighbors(t, m, n, f):
    for axis, size in ((0, m), (1, n)):
        for i in range(size):
            for j in range(size):
                if i == j:
                    continue
                for c in range(1, f.q):
                    out = list(t)
                    for k in range(2):
                        for z in range(n if axis == 0 else m):
                            dst = k*m*n + (i*n+z if axis == 0 else z*n+i)
                            src = k*m*n + (j*n+z if axis == 0 else z*n+j)
                            out[dst] = f.add[out[dst]][f.mul[c][t[src]]]
                    yield tuple(out)
            for c in range(2, f.q):
                out = list(t)
                for k in range(2):
                    for z in range(n if axis == 0 else m):
                        dst = k*m*n + (i*n+z if axis == 0 else z*n+i)
                        out[dst] = f.mul[c][out[dst]]
                yield tuple(out)


def literal(A, B, m, n, cert, f):
    bs, R, Q = cert
    X, Y, h, w = d.model(bs, f)
    need((h, w) == (m, n), 'output shape')
    need(d.a.determinant(R, f) != 0 and d.a.determinant(Q, f) != 0, 'basis rank')
    for orig, canonical in ((A, X), (B, Y)):
        for i, j in itertools.product(range(m), range(n)):
            left = f.total(f.mul[orig[i][k]][Q[k][j]] for k in range(n))
            right = f.total(f.mul[R[i][k]][canonical[k][j]] for k in range(m))
            need(left == right, 'literal coefficient equation')


def exhaustive(f, m, n):
    seen, signatures = set(), set()
    components = count = 0
    for initial in itertools.product(range(f.q), repeat=2*m*n):
        if initial in seen:
            continue
        todo = [initial]
        seen.add(initial)
        signature = None
        while todo:
            t = todo.pop()
            A, B = flat_matrices(t, m, n)
            cert = d.decompose(A, B, m, n, f)
            literal(A, B, m, n, cert, f)
            key = tuple(sorted(cert[0]))
            if signature is None:
                signature = key
            need(key == signature, 'type changes inside independent GL orbit')
            count += 1
            for x in neighbors(t, m, n, f):
                if x not in seen:
                    seen.add(x)
                    todo.append(x)
        need(signature not in signatures, 'different GL orbits share extracted type')
        signatures.add(signature)
        components += 1
    need(count == f.q**(2*m*n), 'complete raw domain')
    row = {'q': f.q, 'shape': [m, n], 'pencils': count, 'strict_orbits': components}
    print(json.dumps(row), flush=True)
    return row


def factor_oracle(f, degree):
    cases = 0
    for n in range(1, degree+1):
        for coeff in itertools.product(range(f.q), repeat=n):
            p = list(coeff) + [1]
            factors = d.factor(p, f)
            result = [1]
            for g in factors:
                result = d.pmul(result, g, f)
                for k in range(1, (len(g)-1)//2+1):
                    for cs in itertools.product(range(f.q), repeat=k):
                        need(d.pdiv(g, list(cs)+[1], f)[1] != [0], 'factor reducible')
            need(result == p, 'factor product')
            cases += 1
    return cases


def random_basis(n, f, rng):
    Q = d.a.identity(n)
    for _ in range(5*n+1):
        if n < 2:
            break
        i, j = rng.sample(range(n), 2)
        c = rng.randrange(1, f.q)
        Q[i] = [f.add[x][f.mul[c][y]] for x, y in zip(Q[i], Q[j])]
    return Q


def constructed():
    rng = random.Random(7107)
    count = equations = controls = no_slice = 0
    for f in (d.a.Field(2, [0,1]), d.a.Field(3, [0,1]), d.a.Field(2, [1,1,1]), d.a.Field(3, [1,0,1])):
        irreducibles = []
        for k in (2, 3):
            irreducibles.append(next(tuple(cs)+(1,) for cs in itertools.product(range(f.q), repeat=k)
                                     if len(d.factor(list(cs)+[1], f)) == 1))
        fixtures = [[], [('right',(),0)], [('left',(),0)],
                    [('right',(),j) for j in range(5)], [('left',(),j) for j in range(5)],
                    [('finite',irreducibles[0],3), ('finite',irreducibles[0],1),
                     ('finite',irreducibles[1],2), ('infinity',(),3)],
                    [('right',(),2),('right',(),2),('left',(),1),('left',(),3),
                     ('finite',irreducibles[0],2),('finite',(0,1),2),('infinity',(),2)],
                    [('finite',(f.neg[c],1),1) for c in range(f.q)] + [('infinity',(),1)]]
        for bs in fixtures:
            A, B, m, n = d.model(bs, f)
            for _ in range(3):
                R, Q = random_basis(m,f,rng), random_basis(n,f,rng)
                X, Y = (d.mm(R,d.mm(Z,Q,n,f),n,f) for Z in (A,B))
                cert = d.decompose(X,Y,m,n,f)
                literal(X,Y,m,n,cert,f)
                need(sorted(cert[0]) == sorted(bs), 'constructed block multiset')
                count += 1
                equations += 2*m*n
                if bs == fixtures[-1]:
                    for a, b in itertools.product(range(f.q), repeat=2):
                        if a or b:
                            Z = [[f.add[f.mul[a][x]][f.mul[b][y]] for x,y in zip(r,s)] for r,s in zip(X,Y)]
                            need(d.a.determinant(Z,f) == 0, 'no invertible base-field slice')
                    no_slice += 1
                if m and n:
                    bad = copy.deepcopy(cert)
                    bad[1][0] = [0]*m
                    need(not d.check(X,Y,m,n,bad,f), 'singular row-map control')
                    bad = copy.deepcopy(cert)
                    bad[2][0] = [0]*n
                    need(not d.check(X,Y,m,n,bad,f), 'singular column-map control')
                    changed = copy.deepcopy(X)
                    changed[0][0] = f.add[changed[0][0]][1]
                    need(not d.check(changed,Y,m,n,cert,f), 'coefficient corruption control')
                    controls += 3
    for A,B,m,n in [([[2]],[[0]],1,1), ([[0]],[[0,0]],1,1), ([[0]],[[0]],-1,1)]:
        try:
            d.decompose(A,B,m,n,d.a.Field(2,[0,1]))
        except ValueError:
            controls += 1
        else:
            raise ValueError('invalid-input control')
    return {'constructed':count,'coefficient_equations':equations,'no_invertible_slice':no_slice,'failure_controls':controls}


def main():
    source_count = authenticate()
    stats = [exhaustive(d.a.Field(p,mod),m,n) for p,mod,m,n in
             [(2,[0,1],2,2),(3,[0,1],2,2),(2,[1,1,1],2,2),(2,[0,1],2,3),(2,[0,1],3,2)]]
    factors = sum(factor_oracle(d.a.Field(p,mod),degree) for p,mod,degree in
                  [(2,[0,1],7),(3,[0,1],5),(2,[1,1,1],4),(3,[1,0,1],3)])
    result = {'status':'PASS_RAW_PENCIL_DECOMPOSITION','source_inputs':source_count,
              'complete_domains':stats,'factor_polynomials':factors,**constructed()}
    need(result == json.loads((ROOT/'RESULT.json').read_text()), 'committed result differs')
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
