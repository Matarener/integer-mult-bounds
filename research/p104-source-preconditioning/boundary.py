# SPDX-License-Identifier: Apache-2.0
"""A reversible source shear and its exact conditional correction identity."""
from fractions import Fraction as Q
from itertools import combinations, product

from bindings import need

TARGET, SOURCE = 71, 102


def root_lines():
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    roots.update((1, *signs) for signs in product((-1, 1), repeat=7) if signs.count(-1) % 2 == 0)
    need(len(roots) == 120, "complete doubled E8 root lines")
    return tuple(sorted(roots))


def correction(fixture):
    selected = fixture["section4_explicit_P104"]
    removed = {tuple(row) for row in selected["F0"] + selected["C"]}
    ports = tuple(row for row in root_lines() if row not in removed)
    need(len(ports) == 104, "complete P104 ports")
    gram_half = tuple(tuple(Q(sum(a * b for a, b in zip(x, y)), 8) for y in ports) for x in ports)
    result = tuple(tuple(Q(i == j) - value for j, value in enumerate(row)) for i, row in enumerate(gram_half))
    need(result[TARGET][SOURCE] == Q(-1, 2), "specific obstructed correction")
    return ports, gram_half, result


def apply_source_shear(rows, coefficient):
    """Left multiplication by I+coefficient*e71*e102^T."""
    result = [list(row) for row in rows]
    result[TARGET] = [a + coefficient * b for a, b in zip(rows[TARGET], rows[SOURCE])]
    return tuple(tuple(row) for row in result)


def conditional_completion(gram_half, corrected, coefficient=Q(-1, 2), restore=True):
    """Check algebra under an explicitly assumed complete correction oracle.

    This function supplies no chronological or dirty-restored corrector.
    """
    identity = tuple(tuple(Q(i == j) for j in range(104)) for i in range(104))
    U = apply_source_shear(identity, coefficient)
    VU = apply_source_shear(U, -coefficient) if restore else U
    need(VU == identity, "source restoration after its last read")
    # Right multiplication by U changes only column102.
    total = tuple(tuple(a + b for a, b in zip(x, y)) for x, y in zip(gram_half, corrected))
    composed = tuple(tuple(value + (coefficient * row[TARGET] if j == SOURCE else 0)
                           for j, value in enumerate(row)) for row in total)
    need(composed == identity, "conditional complete target identity")
    return U


def physical_sources(native, word, fixture, N):
    """Replay the credited Gram-isometry binding before using physical masks."""
    roots = root_lines()
    inner = lambda a, b: sum(x * y for x, y in zip(a, b)) // 4
    binary = [sum(((inner(a, b) + 1) & 1) << j for j, b in enumerate(roots)) for a in roots]
    iso = native["label_isometry"]
    indices = iso["pivot_root_indices"]
    need(len(indices) == len(set(indices)) == 9, "nine isometry coordinate pivots")
    compressed = [sum(((row >> j) & 1) << k for k, j in enumerate(indices)) for row in binary]
    gram = tuple(compressed[i] for i in indices)
    need(list(gram) == iso["compressed_gram"], "compressed Gram binding")
    dual = N.inverse(gram)
    need(list(dual) == iso["compressed_dual_gram"], "compressed dual binding")
    dot = lambda a, b: (a & N.mul(dual, b)).bit_count() & 1
    orthogonal = iso["orthonormal_basis_compressed"]
    need(len(orthogonal) == 9 and all(dot(a, b) == (i == j)
         for i, a in enumerate(orthogonal) for j, b in enumerate(orthogonal)), "native Gram isometry")
    convert = lambda value: sum(dot(value, basis) << i for i, basis in enumerate(orthogonal))
    physical = tuple(convert(value) for value in compressed)
    need(list(physical) == iso["physical_root_labels"] and len(set(physical)) == 120, "physical label image")
    need(all(((a & b).bit_count() & 1) == ((binary[i] >> j) & 1)
             for i, a in enumerate(physical) for j, b in enumerate(physical)), "complete physical pairings")
    ports, _, _ = correction(fixture)
    labels = dict(zip(roots, physical))
    masks, records = [], []
    for port in (TARGET, SOURCE):
        record = next(row for row in native["endpoint_adapters"]
                      if row["position"] == "entry" and row["register"] == "X" + str(port))
        normal = labels[ports[port]]
        need(record["normal"] == normal and record["frame"] == [normal] and
             [convert(value) for value in word["initial_frames"]["X" + str(port)]] == [normal],
             "actual physical source frame")
        expected = N.adjoint((("C", normal, 1),)) + N.frame((normal,), 9)
        N.equal(N.recipe(record["recipe"]), expected, "intrinsic source entry adapter")
        masks.append(normal)
        records.append(record)
    need(tuple(masks) == (121, 296), "bound source masks")
    return tuple(masks), tuple(records)


def bridge(N, masks, columns=1):
    """One C^(tensor 2f) call between fixed affine permutations at tensor depth f."""
    need(type(columns) is int and 1 <= columns <= 3, "bounded native tensor fixture")
    a, b = masks
    dimension = 9 * columns
    first = tuple(a << (9 * j) for j in range(columns))
    second = tuple(b << (9 * j) for j in range(columns))
    matrix = N.transpose(N.extend(first + second, dimension))
    flip = sum(second)
    circuit = (("X", flip), ("P", N.inverse(matrix))) + N.fourier(2 * columns) + (("P", matrix),)
    expected = tuple(("C", vector, -1) for vector in second) + tuple(("C", vector, 1) for vector in first)
    need(N.tableau(circuit, dimension) == N.tableau(expected, dimension), "full tensor signed Pauli action")
    need(N.state(circuit) == N.state(expected), "exact tensor global phase")
    return circuit, expected


def channel_rows(word, precondition=True):
    """Execute the literal affine word on all280 independent logical inputs.

    Native frame refinement stays with the authenticated source theorem.
    The side-correction oracle is deliberately absent from this replay.
    """
    names = tuple(word["initial_frames"])
    need(len(names) == 280, "all persistent independent input columns")
    state = {name: {name: Q(1)} for name in names}
    frames = {name: frozenset(_span(basis)) for name, basis in word["initial_frames"].items()}
    if precondition:
        state["X71"]["X102"] = Q(-1, 2)
    for event in word["program"]:
        kind, target = event[:2]
        if kind == "transport":
            need(frames[target] == frozenset(_span(event[2])), "literal frame entry")
            frames[target] = frozenset(_span(event[3]))
        elif kind == "zero":
            need(target == "C" and target not in state, "owned zero private entry")
            state[target] = {}
            frames[target] = frozenset(_span(event[2]))
        elif kind == "erase":
            need(target == "C" and frames[target] == frozenset(_span(event[2])), "owned private disposal")
            del state[target]
            del frames[target]
        elif kind == "copy":
            source, basis = event[2:]
            need(not state[target] and frames[target] == frames[source] == frozenset(_span(basis)), "equal-frame copy")
            state[target] = dict(state[source])
        else:
            need(kind == "add", "literal scalar opcode")
            source, coefficient, basis = event[2:]
            need(frames[target] == frames[source] == frozenset(_span(basis)), "equal-frame addition")
            for name, value in state[source].items():
                updated = state[target].get(name, Q(0)) + Q(coefficient) * value
                if updated:
                    state[target][name] = updated
                else:
                    state[target].pop(name, None)
    need(set(state) == set(frames) == set(names), "complete private lifetimes")
    need(all(frames[name] == frozenset(_span(word["final_frames"][name])) for name in names), "complete frame return")
    return state


def _span(basis):
    result = {0}
    for vector in basis:
        result |= {x ^ vector for x in tuple(result)}
    return result
