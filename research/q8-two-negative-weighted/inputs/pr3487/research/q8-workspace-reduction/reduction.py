"""Construct the image restriction or common-kernel quotient in the proof."""

from model import diagonal, dot, evaluate, require, validate


def solver(vectors):
    pivots = {}
    for position, vector in enumerate(vectors):
        value, coefficient = vector, 1 << position
        for pivot in sorted(pivots, reverse=True):
            if value >> pivot & 1:
                row, tag = pivots[pivot]
                value ^= row
                coefficient ^= tag
        require(value != 0, "dependent basis")
        pivots[value.bit_length() - 1] = value, coefficient
    return pivots


def coordinates(vector, pivots):
    result = 0
    for pivot in sorted(pivots, reverse=True):
        if vector >> pivot & 1:
            row, tag = pivots[pivot]
            vector ^= row
            result ^= tag
    require(vector == 0, "vector outside span")
    return result


def basis(vectors):
    result = []
    for vector in vectors:
        try:
            coordinates(vector, solver(result))
        except ValueError:
            result.append(vector)
    return tuple(result)


def signature(vector, rows):
    return sum(dot(vector, row) << a for a, row in enumerate(rows))


def first_order(word, target):
    for a, g in enumerate(target):
        column = 0
        for u, v, _ in word:
            if v >> a & 1:
                column ^= u
        require(column == (1 << a if g in (2, 3, 4, 5) else 0), "first-order identity")
    odd = sum(g in (2, 3, 4, 5) for g in target)
    require(len(word) % 2 == odd % 2, "idempotent trace parity")
    return odd


def adapted_basis(word, target, route):
    active = tuple(1 << a for a, g in enumerate(target) if g != 0)
    images = basis(tuple(u for u, _, _ in word))
    rows = basis(tuple(v for _, v, _ in word))
    if route == "image":
        active_mask = sum(active)
        vectors = (*active, *(u & ~active_mask for u in images))
        representatives = basis(vectors)
        return representatives, representatives, images, rows
    representatives, signatures = [], []
    candidates = (*active, *(1 << a for a, g in enumerate(target) if g == 0))
    for vector in candidates:
        value = signature(vector, rows)
        if len(basis((*signatures, value))) > len(signatures):
            representatives.append(vector)
            signatures.append(value)
    require(len(signatures) == len(rows), "quotient basis incomplete")
    return tuple(representatives), tuple(signatures), images, rows


def compress(word, target, route="auto"):
    validate(word, target)
    odd = first_order(word, target)
    require(route in ("auto", "image", "quotient"), "reduction route")
    dx = len(basis(tuple(u for u, _, _ in word)))
    dy = len(basis(tuple(v for _, v, _ in word)))
    if route == "auto":
        route = "image" if dx <= dy else "quotient"
    representatives, encoded, images, rows = adapted_basis(word, target, route)
    pivots = solver(encoded)
    reduced = []
    for u, v, g in word:
        value = u if route == "image" else signature(u, rows)
        new_u = coordinates(value, pivots)
        new_v = signature(v, representatives)
        require(dot(new_u, new_v) == 1, "restricted idempotence")
        reduced.append((new_u, new_v, g))
    active = tuple(g for g in target if g != 0)
    new_target = active + (0,) * (len(representatives) - len(active))
    require(
        evaluate(reduced, len(new_target)) == diagonal(new_target), "reduced endpoint"
    )
    require(dx + dy <= len(word) + odd, "Sylvester bound")
    if (route == "image" and dx <= dy) or (route == "quotient" and dy <= dx):
        require(len(new_target) <= (len(word) + odd) // 2, "two-sided role bound")
    return {
        "route": route,
        "word": tuple(reduced),
        "target": new_target,
        "representatives": representatives,
        "encoded": encoded,
        "image_basis": images,
        "row_basis": rows,
        "odd": odd,
        "image_rank": dx,
        "row_rank": dy,
    }


def check_intertwining(word, target, result):
    """Check every original scalar column, not only the final diagonal output."""
    route = result["route"]
    representatives = result["representatives"]
    pivots = solver(result["encoded"])
    for original, reduced in zip(word, result["word"], strict=True):
        u, v, g = original
        new_u, new_v, new_g = reduced
        require(g == new_g, "paid label/order changed")
        if route == "image":
            for a, vector in enumerate(representatives):
                left = u if dot(v, vector) else 0
                right = 0
                for b, representative in enumerate(representatives):
                    if new_u >> b & new_v >> a & 1:
                        right ^= representative
                require(left == right, "image intertwining")
        else:
            for a in range(len(target)):
                column = coordinates(signature(1 << a, result["row_basis"]), pivots)
                left = new_u if dot(new_v, column) else 0
                value = u if v >> a & 1 else 0
                right = coordinates(signature(value, result["row_basis"]), pivots)
                require(left == right, "quotient intertwining")
