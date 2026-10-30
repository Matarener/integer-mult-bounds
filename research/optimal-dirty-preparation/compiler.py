"""Overlap-aware scalar preparation and dirty Q8 action. Apache-2.0.

Nick Petalas. The Q8 action and conjugation contract credit Arham Tahir/PR3137.
"""

MAX_ROLES = 256
MAX_PAYLOAD = 7
MAX_PACKET_BITS = 8 * MAX_ROLES * MAX_PAYLOAD


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_pair(roles, u, v):
    require(type(roles) is int and 1 <= roles <= MAX_ROLES, "invalid roles")
    limit = 1 << roles
    require(type(u) is int and type(v) is int, "vectors must be integers")
    require(0 < u < limit and 0 < v < limit, "vectors outside role space")
    require((u & v).bit_count() % 2 == 1, "coupling is not idempotent")


def distance(roles, u, v):
    validate_pair(roles, u, v)
    return u.bit_count() + v.bit_count() - ((u & v).bit_count() + 3) // 2


def preparation(roles, u, v):
    """Return pivot and chronological row-XOR pairs, destination first."""
    validate_pair(roles, u, v)
    shared = [k for k in range(roles) if (u & v) >> k & 1]
    pivot = shared[0]
    program = []
    for offset in range(1, len(shared), 2):
        a, b = shared[offset : offset + 2]
        program.extend(((a, b), (b, pivot), (pivot, a)))
    for k in range(roles):
        if (u & ~v) >> k & 1:
            program.append((k, pivot))
        if (v & ~u) >> k & 1:
            program.append((pivot, k))
    require(len(program) == distance(roles, u, v), "preparation invoice")
    return pivot, tuple(program)


def move_pair(u, v, destination, source):
    """E u and v E^-1 for E=I+e_destination e_source^T."""
    return (
        u ^ (((u >> source) & 1) << destination),
        v ^ (((v >> destination) & 1) << source),
    )


def affine_action(label, point):
    """PR3137's z^c i^a j^b regular encoding, z=-1."""
    a, b, c = label & 1, (label >> 1) & 1, label >> 2
    x, y, s = point & 1, (point >> 1) & 1, point >> 2
    return (x ^ a) | ((y ^ b) << 1) | ((s ^ c ^ ((a ^ b) & x) ^ (b & y)) << 2)


def permutation_swaps(label):
    require(type(label) is int and 0 <= label < 8, "invalid Q8 label")
    seen = set()
    swaps = []
    for start in range(8):
        if start in seen:
            continue
        point = start
        for _ in range(8):
            seen.add(point)
            point = affine_action(label, point)
            if point == start:
                break
            swaps.append((start, point))
        require(point == start, "Q8 cycle failed to close")
    require(len(swaps) in (0, 4, 6), "Q8 swap count")
    return tuple(swaps)


def row_xors(data, program, payload):
    for destination, source in program:
        for cell in range(8 * payload):
            data[destination][cell] ^= data[source][cell]


def execute(data, pivot, program, swaps, payload):
    """Internal trusted schedule; exactly three XORs implement each swap."""
    row_xors(data, program, payload)
    row = data[pivot]
    for a, b in swaps:
        for cell in range(payload):
            left, right = a * payload + cell, b * payload + cell
            row[left] ^= row[right]
            row[right] ^= row[left]
            row[left] ^= row[right]
    row_xors(data, reversed(program), payload)
    return data


def apply_coupling(data, u, v, label, payload=1):
    """In-place I+uv^T(P_label-I), with distinct arbitrary dirty role arrays."""
    require(type(data) is list, "data must be a list")
    roles = len(data)
    validate_pair(roles, u, v)
    require(type(payload) is int and 1 <= payload <= MAX_PAYLOAD, "invalid payload")
    require(
        all(type(row) is list and len(row) == 8 * payload for row in data),
        "invalid array shape",
    )
    require(len({id(row) for row in data}) == roles, "aliased role arrays")
    require(
        all(
            type(cell) is int and cell >= 0 and cell.bit_length() <= MAX_PACKET_BITS
            for row in data
            for cell in row
        ),
        "invalid integer bit packet",
    )
    swaps = permutation_swaps(label)
    if not swaps:
        return data
    pivot, program = preparation(roles, u, v)
    return execute(data, pivot, program, swaps, payload)
