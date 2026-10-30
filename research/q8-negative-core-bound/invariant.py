"""Degree-two Q8 quotient and chronological binary coefficient. Apache-2.0."""

MAX_CALLS = 12


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(rows, labels):
    n = len(rows)
    require(1 <= n <= MAX_CALLS, "call count must be in 1..12")
    require(len(labels) == n and all(type(g) is int and g in (1, 2) for g in labels),
            "labels must be i=1 or j=2")
    require(all(type(r) is int and 0 <= r < 1 << n for r in rows), "binary rows")
    require(all(r >> k & 1 for k, r in enumerate(rows)), "diagonal must be one")


def multiply(a, b):
    out = []
    for row in a:
        value = 0
        for k in range(len(b)):
            if row >> k & 1:
                value ^= b[k]
        out.append(value)
    return tuple(out)


def rank(rows):
    basis = [0] * MAX_CALLS
    for row in rows:
        for k in range(MAX_CALLS - 1, -1, -1):
            if row >> k & 1:
                if basis[k]:
                    row ^= basis[k]
                else:
                    basis[k] = row
                    break
    return sum(x != 0 for x in basis)


def chronological(rows, labels):
    """H[b,a] is A[b,a] times the t coefficient of x_b*x_a, b>a."""
    validate(rows, labels)
    return tuple(sum(((rows[b] >> a) & 1) << a for a in range(b)
                     if (labels[b], labels[a]) != (1, 2))
                 for b in range(len(rows)))


def obstruction(rows, labels):
    h = chronological(rows, labels)
    unit = tuple(row ^ (1 << k) for k, row in enumerate(h))
    return multiply(multiply(rows, unit), rows)


def quotient_product(u, v):
    """Basis bits 1,x,y,t,xy. All degree-three monomials vanish."""
    require(type(u) is int and type(v) is int and 0 <= u < 32 and 0 <= v < 32,
            "quotient elements must be five-bit integers")
    out = 0
    quadratic = {(1, 1): 8, (2, 2): 8, (1, 2): 16, (2, 1): 24}
    for a in range(5):
        for b in range(5):
            if (u >> a & 1) and (v >> b & 1):
                out ^= (1 << b) if a == 0 else (1 << a) if b == 0 else quadratic.get((a, b), 0)
    return out


def group_images():
    """Q8 order 1,i,j,k,z,zi,zj,zk, with k=ij."""
    i, j, z = 3, 5, 9
    k = quotient_product(i, j)
    return (1, i, j, k, z, quotient_product(z, i),
            quotient_product(z, j), quotient_product(z, k))
