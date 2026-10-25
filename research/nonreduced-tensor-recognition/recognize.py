"""Recover commutative multiplication from a square prime-field tensor.

The new step checks local module tops before constructing cyclic vectors.
The pinned sources supply matrix routines and the final algebra classifier.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import hashlib
import importlib.util
import json
from math import isqrt
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_source(name):
    row = next(r for r in json.loads((HERE / 'INPUTS.json').read_text())
               if r['local'] == 'source/' + name + '.py')
    path = HERE / row['local']
    data = path.read_bytes()
    blob = b'blob ' + str(len(data)).encode() + b'\0' + data
    if hashlib.sha256(data).hexdigest() != row['sha256'] or hashlib.sha1(blob).hexdigest() != row['git_blob']:
        raise ValueError('source authentication failed: ' + name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


N = load_source('nucleus_source')
TABLE = load_source('table_source')


def cyclic_vector(action, Y, parts, radical, p):
    """Check each simple top and lift one generator from each component."""
    n = len(Y)
    result = [0] * n
    dimensions = []
    for e in parts:
        ec = N.coordinates(Y, e, p)
        projection = N.combine(action, ec, p)
        component = [N.coordinates(Y, N.multiply(e, a, p), p) for a in Y]
        residue_degree = N.rank(radical + component, p) - len(radical)
        j_columns = []
        for r in radical:
            matrix = N.multiply(projection, N.combine(action, r, p), p)
            j_columns.extend(map(list, zip(*matrix)))
        j_rank = N.rank(j_columns, p)
        top = N.rank(projection, p) - j_rank
        dimensions.append((residue_degree, top))
        if top != residue_degree:
            return None, dimensions
        vector = next((list(v) for v in zip(*projection)
                       if N.rank(j_columns + [list(v)], p) > j_rank), None)
        N.require(vector is not None, 'nonzero simple top')
        result = [(x + y) % p for x, y in zip(result, vector)]
    return result, dimensions


def recognize_commutative(t, p):
    """Return a complete transporter or a mathematical rejection reason.

    Inputs use canonical residues. Malformed inputs raise ValueError.
    """
    N.require(type(p) is int and p >= 2 and
              not any(p % d == 0 for d in range(2, isqrt(p)+1)), 'prime field required')
    N.require(isinstance(t, (list, tuple)) and len(t) > 0, 'nonempty tensor')
    n = len(t)
    N.require(all(isinstance(row, (list, tuple)) and len(row) == n and
                  all(isinstance(v, (list, tuple)) and len(v) == n for v in row)
                  for row in t), 'tensor shape')
    N.require(all(type(a) is int and 0 <= a < p for row in t for v in row for a in v),
              'canonical prime-field entries')
    X, Y = N.nucleus(t, p)
    if len(Y) != n:
        return None, 'nucleus dimension'
    if any(N.rank([N.flat(a) for a in basis], p) != n for basis in [X,Y]):
        return None, 'nucleus projection'
    if any(N.multiply(a,b,p) != N.multiply(b,a,p) for a in Y for b in Y):
        return None, 'noncommutative nucleus'
    right = N.transpose([[t[i][j][k] for i in range(n) for k in range(n)] for j in range(n)])
    if N.rank(right,p) != n:
        return None, 'right kernel'
    frobenius = N.transpose([N.coordinates(Y,N.power(a,p,p),p) for a in Y])
    exponent, bound = 0, 1
    while bound < n:
        exponent += 1
        bound *= p
    radical = N.nullspace(N.power(frobenius,exponent,p),p)
    parts = N.primitive_parts(Y,frobenius,p)
    u0, u_top = cyclic_vector(X,Y,parts,radical,p)
    if u0 is None:
        return None, 'input top multiplicity'
    w0, w_top = cyclic_vector(Y,Y,parts,radical,p)
    if w0 is None:
        return None, 'output top multiplicity'
    U = N.transpose([N.matvec(a,u0,p) for a in X])
    W = N.transpose([N.matvec(a,w0,p) for a in Y])
    phi = N.transpose([N.evaluate(t,u0,v,p) for v in N.identity(n)])
    N.require(all(N.rank(a,p)==n for a in [U,W,phi]), 'regularity construction failed')
    V = N.multiply(N.inverse(phi,p),W,p)
    table = [[N.coordinates(Y,N.multiply(a,b,p),p) for b in Y] for a in Y]
    return dict(table=table,U=U,V=V,W=W,radical_dimension=len(radical),
                residue_degrees=sorted(x[0] for x in w_top),
                input_tops=u_top,output_tops=w_top), None


def recognize_frobenius(t, p):
    """Compose the recovered table with apoursh's pinned class recognizer."""
    certificate, reason = recognize_commutative(t,p)
    if certificate is None:
        return None, reason
    algebra = TABLE.recognize(p,certificate['table'])
    if algebra['status'] != 'accepted':
        return None, 'algebra class: ' + algebra['reason']
    C = N.transpose(algebra['transporter'])
    return dict(heights=algebra['heights'],
                **{key:N.multiply(certificate[key],C,p) for key in ['U','V','W']}), None
