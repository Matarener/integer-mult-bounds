"""Exact finite model for the confined two-clique relay theorem.

This contribution was produced by Nick Petalas. Apache-2.0.
"""

from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(generators):
    require(len(generators) <= 9, "at most nine binary generators")
    result = frozenset({0})
    for vector in generators:
        require(type(vector) is int and 0 <= vector < 512, "binary vector")
        result |= frozenset(value ^ vector for value in result)
    return result


def dimension(frame):
    require(0 in frame and len(frame) <= 512, "nonempty bounded frame")
    dim = len(frame).bit_length() - 1
    require(len(frame) == 1 << dim, "frame cardinality")
    return dim


def row_basis(rows, width):
    require(0 <= width <= 16 and len(rows) <= 64, "rational matrix capacity")
    matrix = []
    for row in rows:
        require(len(row) == width, "rational row width")
        converted = [Fraction(value) for value in row]
        require(all(max(abs(x.numerator).bit_length(), x.denominator.bit_length())
                    <= 2048 for x in converted), "rational input capacity")
        matrix.append(converted)
    pivot_row = 0
    for column in range(width):
        pivot = next((i for i in range(pivot_row, len(matrix))
                      if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
        divisor = matrix[pivot_row][column]
        matrix[pivot_row] = [x / divisor for x in matrix[pivot_row]]
        for i in range(len(matrix)):
            if i != pivot_row:
                factor = matrix[i][column]
                matrix[i] = [x - factor * y
                             for x, y in zip(matrix[i], matrix[pivot_row])]
        pivot_row += 1
    return tuple(tuple(row) for row in matrix[:pivot_row])


def in_rows(row, basis):
    return len(row_basis([*basis, row], len(row))) == len(basis)


def tags_for(ports):
    require(len(ports) == 8 and len(set(ports)) == 8, "eight distinct ports")
    first = ports[0]
    tags = tuple(1 if (first & p).bit_count() % 2 else 2 for p in ports)
    require(tags.count(1) == tags.count(2) == 4, "two four-port classes")
    for i, p in enumerate(ports):
        for j, q in enumerate(ports):
            require((p & q).bit_count() % 2 == (tags[i] == tags[j]),
                    "two-clique Gram contract")
    return tags


def image(frame, ports, tags):
    first = ports[tags.index(1)]
    second = ports[tags.index(2)]
    return frozenset(((x & first).bit_count() % 2)
                     | (((x & second).bit_count() % 2) << 1) for x in frame)


def annihilator(binary_image):
    table = {
        frozenset({0}): ((1, 0), (0, 1)),
        frozenset({0, 1}): ((0, 1),),
        frozenset({0, 2}): ((1, 0),),
        frozenset({0, 3}): ((1, -1),),
        frozenset({0, 1, 2, 3}): (),
    }
    require(binary_image in table, "binary quotient subspace")
    return table[binary_image]


def packet(vector, tags, functional):
    return tuple(Fraction(value) * functional[tag - 1]
                 for value, tag in zip(vector, tags))


def check_network(ports, moves, output):
    """Check REL and return the invoice, shadow rank and debt dimension."""
    tags = tags_for(ports)
    universe = span(list(ports))
    require(len(moves) <= 16 and len(output) == 8, "network capacity")
    require(all(len(row) == len(moves) for row in output), "output shape")
    vectors, landings, debt = [], [], ()
    paid = effective = 0
    for move in moves:
        gather, landing, local, parents = move
        require(gather <= universe and landing < gather, "confined strict descent")
        require(span(list(row_basis_binary(gather))) == gather, "gather subspace")
        require(span(list(row_basis_binary(landing))) == landing, "landing subspace")
        require(len(local) == 8 and len(parents) == len(vectors), "source shape")
        require(all(not x or ports[i] in gather for i, x in enumerate(local)),
                "local source availability")
        require(all(not x or landings[i] <= gather for i, x in enumerate(parents)),
                "ancestor arrival availability")
        vector = tuple(Fraction(local[i]) + sum(
            Fraction(a) * old[i] for a, old in zip(parents, vectors))
            for i in range(8))
        before = annihilator(image(gather, ports, tags))
        after = annihilator(image(landing, ports, tags))
        require(all(in_rows(packet(vector, tags, z), debt) for z in before),
                "incoming debt invariant")
        extended = row_basis(list(before), 2)
        added = []
        for z in after:
            if not in_rows(z, extended):
                added.append(packet(vector, tags, z))
                extended = row_basis([*extended, z], 2)
        drop = len(after) - len(before)
        require(len(added) == drop, "quotient extension dimension")
        require(drop <= dimension(gather) - dimension(landing), "drop bill")
        debt = row_basis([*debt, *added], 8)
        require(all(in_rows(packet(vector, tags, z), debt) for z in after),
                "outgoing debt invariant")
        vectors.append(vector)
        landings.append(landing)
        paid += dimension(gather) - dimension(landing)
        effective += drop
    shadow = []
    for j, row in enumerate(output):
        functional = (1, 0) if tags[j] == 1 else (0, 1)
        for coefficient, landing in zip(row, landings):
            require(not coefficient or functional in
                    row_basis(list(annihilator(image(landing, ports, tags))), 2),
                    "receiver availability")
        shadow.append(tuple(sum(Fraction(a) * v[i] for a, v in zip(row, vectors))
                            if tags[i] == tags[j] else Fraction(0)
                            for i in range(8)))
    rank = len(row_basis(shadow, 8))
    require(all(in_rows(row, debt) for row in shadow), "output debt containment")
    require(rank <= len(debt) <= effective <= paid, "complete rank invoice")
    return {"paid": paid, "effective_paid": effective, "shadow_rank": rank,
            "debt_dimension": len(debt), "shadow": shadow}


def row_basis_binary(frame):
    require(len(frame) <= 512 and all(type(x) is int and 0 <= x < 512 for x in frame),
            "bounded binary frame")
    basis = []
    generated = frozenset({0})
    for x in sorted(frame):
        if x not in generated:
            basis.append(x)
            require(len(basis) <= 9, "binary dimension capacity")
            generated = span(basis)
    require(generated == frame, "binary subspace closure")
    return tuple(basis)
