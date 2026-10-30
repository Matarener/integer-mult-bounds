"""Independent regular action using integer Hamilton multiplication.

Nick Petalas, Apache-2.0.
"""

from linear import MAX_DIM, require

ELEMENTS = (
    (1, 0, 0, 0), (-1, 0, 0, 0), (0, 1, 0, 0), (0, -1, 0, 0),
    (0, 0, 1, 0), (0, 0, -1, 0), (0, 0, 0, 1), (0, 0, 0, -1),
)


def product(a, b):
    w, x, y, z = ELEMENTS[a]
    p, q, r, s = ELEMENTS[b]
    return ELEMENTS.index((w*p-x*q-y*r-z*s, w*q+x*p+y*s-z*r,
                           w*r-x*s+y*p+z*q, w*s+x*r-y*q+z*p))


def action(gates, roles, input_column):
    require(0 <= roles <= MAX_DIM and 0 <= input_column < 8 * roles, "input column")
    state = [0] * roles
    state[input_column // 8] = 1 << (input_column % 8)
    for gate in gates:
        read = 0
        for j in range(roles):
            if gate.v & (1 << j):
                read ^= state[j]
        moved = 0
        for g in range(8):
            if read & (1 << g):
                moved ^= 1 << product(gate.label, g)
        for j in range(roles):
            if gate.u & (1 << j):
                state[j] ^= moved ^ read
    return tuple(state)


def endpoint(gates, roles):
    columns = tuple(action(gates, roles, 8*j) for j in range(roles))
    return tuple(tuple(columns[b][a] for b in range(roles)) for a in range(roles))


def eigen_counts(formal):
    """Enumerate binary eigenvectors at 1,zi,zj without first-order projectors."""
    roles = len(formal)
    require(roles <= 4, "bounded eigenvector oracle")
    spaces = []
    for g in (0, 3, 5):
        vectors = []
        for vector in range(1 << roles):
            output = []
            for row in formal:
                value = 0
                for j in range(roles):
                    if vector & (1 << j):
                        value ^= row[j]
                output.append(value)
            if all(value == ((1 << g) if vector & (1 << j) else 0)
                   for j, value in enumerate(output)):
                vectors.append(vector)
        require(len(vectors).bit_count() == 1, "eigenspace size")
        spaces.append(len(vectors).bit_length() - 1)
    if sum(spaces) != roles:
        return None
    return spaces[1], spaces[2]
