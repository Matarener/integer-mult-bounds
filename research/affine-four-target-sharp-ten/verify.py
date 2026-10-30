#!/usr/bin/env python3
"""Exact corroboration of the separated linear/translation lower bound."""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

IDENTITY = (0, 1, 2, 3)
LABELS = {"a": (0, 1, 3, 2), "b": (0, 3, 2, 1),
          "tx": (1, 0, 3, 2), "ty": (2, 3, 0, 1)}
MAX_ROLES = 8


def need(condition, message):
    if not condition:
        raise ValueError(message)


def compose(left, right):
    return tuple(left[right[i]] for i in range(4))


def linear_part(g):
    return tuple(x ^ g[0] for x in g)


def rank(rows, columns):
    need(0 <= columns <= 256 and len(rows) <= 256, "rank domain")
    need(all(type(x) is int and 0 <= x < 1 << columns for x in rows), "rank rows")
    basis = [0] * columns
    answer = 0
    for original in rows:
        row = original
        for bit in range(columns - 1, -1, -1):
            if row >> bit & 1:
                if basis[bit]:
                    row ^= basis[bit]
                else:
                    basis[bit] = row
                    answer += 1
                    break
    return answer


def parity(value):
    return value.bit_count() & 1


def validate_gate(roles, name, u, v):
    need(type(roles) is int and 1 <= roles <= MAX_ROLES, "role domain")
    need(name in LABELS, "paid alphabet")
    need(type(u) is int and type(v) is int, "coupling type")
    need(0 < u < 1 << roles and 0 < v < 1 << roles, "coupling range")
    need(parity(u & v) == 1, "idempotent coupling")


def group_data():
    group = tuple(itertools.permutations(range(4)))
    need(len(group) == 24 and all(linear_part(g) in group for g in group), "affine group")
    linear = tuple(g for g in group if g[0] == 0)
    a, b = LABELS["a"], LABELS["b"]
    swap = compose(compose(a, b), a)
    half = frozenset((IDENTITY, a, b))
    need(len(linear) == 6 and len(half) == 3, "regular cut")
    need({compose(swap, x) for x in half} == set(linear) - half, "swap crosses all")
    for g, h in itertools.product(group, repeat=2):
        need(linear_part(compose(g, h)) == compose(linear_part(g), linear_part(h)),
             "quotient homomorphism")
    return group, linear, half, swap


def homogeneous(g):
    origin = g[0]
    col0, col1 = g[1] ^ origin, g[2] ^ origin
    return (sum(((x >> 0) & 1) << j for j, x in enumerate((col0, col1, origin))),
            sum(((x >> 1) & 1) << j for j, x in enumerate((col0, col1, origin))), 4)


def represented_factor(roles, g, u, v):
    block = homogeneous(g)
    rows = [1 << i for i in range(3 * roles)]
    for i, j, d in itertools.product(range(roles), range(roles), range(3)):
        if u >> i & v >> j & 1:
            rows[3 * i + d] ^= (block[d] ^ (1 << d)) << (3 * j)
    return tuple(rows)


def translation_block(rows, roles):
    return tuple(sum(((rows[3 * i + d] >> (3 * j + 2)) & 1) << j
                     for j in range(roles)) for i in range(roles) for d in range(2))


def crossing_factor(roles, g, u, v, linear, half):
    inside = tuple(x for x in linear if x in half)
    outside = tuple(x for x in linear if x not in half)
    rows = []
    for i, destination in itertools.product(range(roles), outside):
        row = 0
        for j, source in itertools.product(range(roles), inside):
            if u >> i & v >> j & 1 and compose(g, source) == destination:
                row |= 1 << (3 * j + inside.index(source))
        rows.append(row)
    return tuple(rows)


def proof_factors(linear, half):
    counts = {}
    for roles in range(1, 6):
        projectors = [(u, v) for u in range(1, 1 << roles)
                      for v in range(1, 1 << roles) if parity(u & v)]
        counts[str(roles)] = len(projectors)
        for (u, v), (name, g) in itertools.product(projectors, LABELS.items()):
            validate_gate(roles, name, u, v)
            t = rank(translation_block(represented_factor(roles, g, u, v), roles), roles)
            q = rank(crossing_factor(roles, linear_part(g), u, v, linear, half), 3 * roles)
            need((q, t) == ((1, 0) if name in ("a", "b") else (0, 1)),
                 "separated paid charges")
    return counts


def targets(swap):
    return (compose(swap, LABELS["tx"]), compose(LABELS["tx"], swap),
            LABELS["tx"], LABELS["ty"])


def endpoint_bounds(linear, half, wanted):
    result = []
    for roles in range(4, MAX_ROLES + 1):
        rows = tuple(homogeneous(g)[d] << (3 * i)
                     for i, g in enumerate(wanted + (IDENTITY,) * (roles - 4))
                     for d in range(3))
        t = rank(translation_block(rows, roles), roles)
        q = sum(rank(crossing_factor(1, linear_part(g), 1, 1, linear, half), 3)
                for g in wanted)
        need((q, t) == (6, 4), "endpoint lower bounds")
        result.append({"roles": roles, "linear_floor": q, "translation_floor": t})
    return result


def direct_word(roles):
    need(4 <= roles <= MAX_ROLES, "witness roles")
    word = []
    # Chronological order is the reverse of each displayed group product.
    for i, names in enumerate((("tx", "a", "b", "a"),
                               ("a", "b", "a", "tx"), ("tx",), ("ty",))):
        word.extend(("paid", name, 1 << i, 1 << i) for name in names)
    return word


def formal_apply(roles, word, group):
    index = {g: i for i, g in enumerate(group)}
    one = 1 << index[IDENTITY]
    matrix = [[one if i == j else 0 for j in range(roles)] for i in range(roles)]
    for kind, name, u, v in word:
        if kind == "scalar":
            need(name == "add" and 0 <= u < roles and 0 <= v < roles and u != v,
                 "scalar instruction")
            matrix[u] = [x ^ y for x, y in zip(matrix[u], matrix[v])]
            continue
        need(kind == "paid", "instruction kind")
        validate_gate(roles, name, u, v)
        source = [0] * roles
        for i in range(roles):
            if v >> i & 1:
                source = [x ^ y for x, y in zip(source, matrix[i])]
        delta = []
        for entry in source:
            translated = 0
            for k, element in enumerate(group):
                if entry >> k & 1:
                    translated ^= 1 << index[compose(LABELS[name], element)]
            delta.append(entry ^ translated)
        for i in range(roles):
            if u >> i & 1:
                matrix[i] = [x ^ y for x, y in zip(matrix[i], delta)]
    return tuple(tuple(row) for row in matrix)


def literal_columns(roles, word, group, wanted):
    """Separate set-valued regular-action execution on every dirty input column."""
    for original_role, address in itertools.product(range(roles), group):
        state = [set() for _ in range(roles)]
        state[original_role] = {address}
        for kind, name, u, v in word:
            if kind == "scalar":
                state[u] ^= state[v]
                continue
            validate_gate(roles, name, u, v)
            source = set()
            for i in range(roles):
                if v >> i & 1:
                    source ^= state[i]
            perm = LABELS[name]
            delta = source ^ {tuple(perm[x] for x in element) for element in source}
            for i in range(roles):
                if u >> i & 1:
                    state[i] ^= delta
        expected = [set() for _ in range(roles)]
        g = wanted[original_role] if original_role < 4 else IDENTITY
        expected[original_role] = {tuple(g[x] for x in address)}
        need(state == expected, "literal dirty endpoint")
    return roles * 24


def witness_checks(group, wanted):
    index = {g: i for i, g in enumerate(group)}
    columns = 0
    omitted = 0
    witnesses = 0
    for roles in range(4, MAX_ROLES + 1):
        word = direct_word(roles)
        for mixed in range(2 if roles > 4 else 1):
            actual = word
            if mixed:
                changed = []
                for kind, name, u, v in word:
                    up = u ^ ((u >> (roles - 1) & 1) << 0)
                    vp = v ^ ((v & 1) << (roles - 1))
                    changed.append((kind, name, up, vp))
                actual = [("scalar", "add", 0, roles - 1)] + changed
                actual += [("scalar", "add", 0, roles - 1)]
            endpoint = formal_apply(roles, actual, group)
            expected = tuple(tuple((1 << index[wanted[i] if i < 4 else IDENTITY])
                                   if i == j else 0 for j in range(roles))
                             for i in range(roles))
            need(endpoint == expected, "full formal witness")
            columns += literal_columns(roles, actual, group, wanted)
            witnesses += 1
            for position, instruction in enumerate(actual):
                if instruction[0] == "paid":
                    need(formal_apply(roles, actual[:position] + actual[position + 1:], group)
                         != expected, "omitted paid call accepted")
                    omitted += 1
    return {"witnesses": witnesses, "regular_basis_columns": columns,
            "single_paid_call_omissions_rejected": omitted}


def rejects(function, message):
    try:
        function()
    except ValueError:
        return
    raise ValueError(message)


def controls(group, linear, half, wanted):
    rejects(lambda: validate_gate(4, "h", 1, 1), "new label accepted")
    rejects(lambda: validate_gate(4, "a", 1, 2), "nilpotent accepted")
    rejects(lambda: validate_gate(4, "a", 0, 1), "zero coupling accepted")
    rejects(lambda: validate_gate(4, "a", 16, 1), "oversized coupling accepted")
    rejects(lambda: validate_gate(True, "a", 1, 1), "boolean role count accepted")
    word = direct_word(5) + [("paid", "tx", 16, 16)]
    rejects(lambda: literal_columns(5, word, group, wanted), "dirty spectator leakage")
    reversed_target = (wanted[1], wanted[0], wanted[2], wanted[3])
    rejects(lambda: literal_columns(4, direct_word(4), group, reversed_target), "phase order")
    # The necessary representations are deliberately not endpoint certificates.
    omega_h = tuple(0 for _ in range(3))
    for g in group:
        omega_h = tuple(x ^ y for x, y in zip(omega_h, homogeneous(g)))
    need(omega_h == (0, 0, 0), "homogeneous alias control")
    need(all(sum(linear_part(g) == h for g in group) == 4 for h in linear),
         "quotient alias control")
    need(len(group) > 0 and len(set(group)) == 24, "formal Omega is nonzero")
    # An extra affine h label has charges (3,1), rather than a unit charge.
    q = rank(crossing_factor(1, linear_part(wanted[0]), 1, 1, linear, half), 3)
    t = rank(translation_block(represented_factor(1, wanted[0], 1, 1), 1), 1)
    need((q, t) == (3, 1), "enlarged-alphabet distinction")
    return 10


def rank_controls():
    checked = 0
    for nrows, ncols in ((1, 1), (2, 2), (2, 3), (3, 2)):
        for rows in itertools.product(range(1 << ncols), repeat=nrows):
            span = {0}
            for row in rows:
                span |= {x ^ row for x in span}
            need(len(span) == 1 << rank(rows, ncols), "independent rank oracle")
            checked += 1
    return checked


def main():
    group, linear, half, swap = group_data()
    wanted = targets(swap)
    need(wanted[0] == (2, 0, 3, 1) and wanted[1] == (1, 3, 0, 2), "target convention")
    receipt = {
        "claim_type": "scoped written proof with finite exact corroboration",
        "minimum": 10,
        "projectors_by_roles": proof_factors(linear, half),
        "endpoint_bounds": endpoint_bounds(linear, half, wanted),
        "witness_checks": witness_checks(group, wanted),
        "boundary_controls": controls(group, linear, half, wanted),
        "rank_oracle_matrices": rank_controls(),
    }
    root = Path(__file__).resolve().parent
    receipt["source_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(root.iterdir()) if p.is_file()}
    print("PASS_AFFINE_FOUR_TARGET_SHARP_TEN minimum=10 linear_floor=6 translation_floor=4")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
