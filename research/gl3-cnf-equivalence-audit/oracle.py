"""Independent B4 session-4 Boolean and full F2[GL3(F2)] oracle.

Original argument: Brian Ross. Independent construction: Toik Y with substantial
OpenAI Codex assistance. No predecessor code, proof, query, or receipt was read.
The module does not solve SAT, write files, or claim a minimum word length.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from typing import Hashable, Iterable, Mapping, Sequence

Polynomial = frozenset[frozenset[Hashable]]
ZERO: Polynomial = frozenset()
ONE: Polynomial = frozenset((frozenset(),))
IDENTITY = (1, 2, 4)
A = (1, 4, 3)
B = (2, 4, 3)
REGISTER_COUNT = 3
PUBLISHED_LENGTHS = tuple(range(1, 10))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def anf_const(value: bool | int) -> Polynomial:
    require(value in (False, True, 0, 1), "Boolean constant required")
    return ONE if value else ZERO


def anf_var(key: Hashable) -> Polynomial:
    return frozenset((frozenset((key,)),))


def anf_xor(*polys: Polynomial) -> Polynomial:
    result: set[frozenset[Hashable]] = set()
    for poly in polys:
        result.symmetric_difference_update(poly)
    return frozenset(result)


def anf_and(p: Polynomial, q: Polynomial,
            exclusive_groups: Iterable[Iterable[Hashable]] = ()) -> Polynomial:
    groups = tuple(frozenset(group) for group in exclusive_groups)
    result: set[frozenset[Hashable]] = set()
    for left in p:
        for right in q:
            term = left | right
            if any(len(term & group) > 1 for group in groups):
                continue
            if term in result:
                result.remove(term)
            else:
                result.add(term)
    return frozenset(result)


def anf_not(p: Polynomial) -> Polynomial:
    return anf_xor(ONE, p)


def anf_or(p: Polynomial, q: Polynomial,
           exclusive_groups: Iterable[Iterable[Hashable]] = ()) -> Polynomial:
    return anf_xor(p, q, anf_and(p, q, exclusive_groups))


def literal_anf(lit: int) -> Polynomial:
    require(isinstance(lit, int) and lit != 0, "nonzero literal required")
    if abs(lit) == 1:
        return ONE if lit > 0 else ZERO
    value = anf_var(abs(lit))
    return value if lit > 0 else anf_not(value)


def anf_evaluate(poly: Polynomial, values: Mapping[Hashable, bool | int]) -> int:
    total = 0
    for term in poly:
        product = 1
        for key in term:
            product &= int(bool(values[key]))
        total ^= product
    return total


def anf_serializable(poly: Polynomial) -> list[list[str]]:
    # repr is used only for stable receipts; polynomial keys themselves stay typed.
    return sorted((sorted(repr(key) for key in term) for term in poly),
                  key=lambda term: (len(term), term))


def and_clauses(a: int, b: int, z: int) -> tuple[tuple[int, ...], ...]:
    return ((-a, -b, z), (a, -z), (b, -z))


def xor_clauses(a: int, b: int, z: int) -> tuple[tuple[int, ...], ...]:
    return ((-a, -b, -z), (a, b, -z), (-a, b, z), (a, -b, z))


def equality_clauses(a: int, b: int) -> tuple[tuple[int, ...], ...]:
    return ((-a, b), (a, -b))


def normalize_clauses(clauses: Iterable[Iterable[int]]) -> tuple[tuple[int, ...], ...]:
    # Preserve multiplicities of non-tautological clauses for source Counter audits.
    result = []
    for raw in clauses:
        clause = set(raw)
        require(0 not in clause, "literal zero is invalid")
        if 1 in clause or any(-lit in clause for lit in clause):
            continue
        clause.discard(-1)
        result.append(tuple(sorted(clause)))
    return tuple(sorted(result))


def literal_value(lit: int, values: Mapping[int, int | bool]) -> int:
    value = int(bool(values[abs(lit)]))
    return value if lit > 0 else 1 ^ value


def clauses_hold(clauses: Iterable[Iterable[int]], values: Mapping[int, int | bool]) -> bool:
    return all(any(literal_value(lit, values) for lit in clause) for clause in clauses)


class CNF:
    """Small complete Tseitin encoder; independent semantics, not a source adapter."""

    def __init__(self) -> None:
        self.nvars = 1
        self.clauses: list[tuple[int, ...]] = [(1,)]
        self.gates: list[tuple[int, str, int, int]] = []
        self.and_cache: dict[tuple[int, int], int] = {}
        self.xor_cache: dict[tuple[int, int], int] = {}

    def new_var(self) -> int:
        self.nvars += 1
        return self.nvars

    def _check(self, *lits: int) -> None:
        require(all(isinstance(lit, int) and 0 < abs(lit) <= self.nvars
                    for lit in lits), "unallocated or zero literal")

    def and_gate(self, a: int, b: int) -> int:
        self._check(a, b)
        if a == -1 or b == -1 or a == -b:
            return -1
        if a == 1:
            return b
        if b == 1 or a == b:
            return a
        key = tuple(sorted((a, b)))
        if key in self.and_cache:
            return self.and_cache[key]
        z = self.new_var()
        self.and_cache[key] = z
        self.gates.append((z, "and", key[0], key[1]))
        self.clauses.extend(and_clauses(*key, z))
        return z

    def xor_gate(self, a: int, b: int) -> int:
        self._check(a, b)
        if a == -1:
            return b
        if b == -1:
            return a
        if a == 1:
            return -b
        if b == 1:
            return -a
        if a == b:
            return -1
        if a == -b:
            return 1
        # Complementing exactly one operand complements XOR's output.
        sign = -1 if (a < 0) != (b < 0) else 1
        key = tuple(sorted((abs(a), abs(b))))
        if key not in self.xor_cache:
            z = self.new_var()
            self.xor_cache[key] = z
            self.gates.append((z, "xor", key[0], key[1]))
            self.clauses.extend(xor_clauses(*key, z))
        return sign * self.xor_cache[key]

    def or_gate(self, a: int, b: int) -> int:
        return -self.and_gate(-a, -b)

    def equal(self, a: int, b: int) -> None:
        self._check(a, b)
        self.clauses.extend(equality_clauses(a, b))

    def exactly_one(self, lits: Sequence[int]) -> None:
        require(len(lits) > 0, "nonempty onehot group required")
        self._check(*lits)
        self.clauses.append(tuple(lits))
        self.clauses.extend((-a, -b) for a, b in itertools.combinations(lits, 2))

    def extend(self, primary_values: Mapping[int, int | bool]) -> dict[int, int]:
        values = {1: 1, **{key: int(bool(value)) for key, value in primary_values.items()}}
        require(values[1] == 1, "variable 1 is forced true")
        for z, op, a, b in self.gates:
            av, bv = literal_value(a, values), literal_value(b, values)
            values[z] = av & bv if op == "and" else av ^ bv
        return values


def matmul(left: Sequence[int], right: Sequence[int]) -> tuple[int, int, int]:
    rows = []
    for mask in left:
        row = 0
        for k in range(3):
            if mask & (1 << k):
                row ^= right[k]
        rows.append(row)
    return tuple(rows)  # type: ignore[return-value]


def rank3(rows: Sequence[int]) -> int:
    basis = [0, 0, 0]
    rank = 0
    for row in rows:
        residue = row
        for bit in range(2, -1, -1):
            if residue & (1 << bit):
                if basis[bit]:
                    residue ^= basis[bit]
                else:
                    basis[bit] = residue
                    rank += 1
                    break
    return rank


GROUP = tuple(rows for rows in itertools.product(range(8), repeat=3) if rank3(rows) == 3)
GROUP_INDEX = {rows: index for index, rows in enumerate(GROUP)}
GROUP_ORDER = len(GROUP)
E_INDEX = GROUP_INDEX[IDENTITY]
LABEL_COORDINATES = tuple((i, j) for i in range(3) for j in range(3) if i != j)


def row_cnot(i: int, j: int) -> tuple[int, int, int]:
    rows = list(IDENTITY)
    rows[i] ^= rows[j]
    return tuple(rows)  # type: ignore[return-value]


LABELS = tuple(row_cnot(i, j) for i, j in LABEL_COORDINATES)
INVERSES = tuple(next(other for other in GROUP if matmul(element, other) == IDENTITY)
                 for element in GROUP)
PULLBACKS = tuple(tuple(GROUP_INDEX[matmul(INVERSES[GROUP_INDEX[label]], h)] for h in GROUP)
                  for label in LABELS)
LEGAL_UV = tuple((u, v) for u in itertools.product((0, 1), repeat=3)
                 for v in itertools.product((0, 1), repeat=3)
                 if sum(a * b for a, b in zip(u, v)) % 2 == 1)


def validate_state(state: Sequence[Sequence[Sequence[int]]]) -> None:
    require(len(state) == 3 and all(len(row) == 3 for row in state), "3 by 3 state required")
    require(all(len(entry) == GROUP_ORDER and all(bit in (0, 1) for bit in entry)
                for row in state for entry in row), "all 168 Boolean coefficients required")


def identity_state() -> list[list[list[int]]]:
    return [[[int(r == c and h == E_INDEX) for h in range(GROUP_ORDER)]
             for c in range(3)] for r in range(3)]


def endpoint_state() -> list[list[list[int]]]:
    targets = (A, B, IDENTITY)
    return [[[int(r == c and h == GROUP_INDEX[targets[c]]) for h in range(GROUP_ORDER)]
             for c in range(3)] for r in range(3)]


def check_factor(u: Sequence[int], v: Sequence[int], label: int) -> None:
    require(len(u) == len(v) == 3 and all(x in (0, 1) for x in (*u, *v)), "binary u,v required")
    require(sum(a * b for a, b in zip(u, v)) % 2 == 1, "v^T u must be one")
    require(isinstance(label, int) and 0 <= label < 6, "one of six labels required")


def transition_dense(state: Sequence[Sequence[Sequence[int]]], u: Sequence[int],
                     v: Sequence[int], label: int) -> list[list[list[int]]]:
    """One call, all nine entries and all 168 group coefficients."""
    validate_state(state)
    check_factor(u, v, label)
    result = [[[0] * GROUP_ORDER for _ in range(3)] for _ in range(3)]
    for c in range(3):
        q = [sum(v[k] * state[k][c][h] for k in range(3)) % 2
             for h in range(GROUP_ORDER)]
        for r in range(3):
            for h in range(GROUP_ORDER):
                result[r][c][h] = state[r][c][h] ^ (u[r] & (q[h] ^ q[PULLBACKS[label][h]]))
    return result


def factor_ring(u: Sequence[int], v: Sequence[int], label: int) -> list[list[set[int]]]:
    check_factor(u, v, label)
    label_index = GROUP_INDEX[LABELS[label]]
    result = [[set() for _ in range(3)] for _ in range(3)]
    for r in range(3):
        for k in range(3):
            if r == k:
                result[r][k].add(E_INDEX)
            if u[r] & v[k]:
                result[r][k].symmetric_difference_update((E_INDEX, label_index))
    return result


def transition_ring(state: Sequence[Sequence[Sequence[int]]], u: Sequence[int],
                    v: Sequence[int], label: int) -> list[list[list[int]]]:
    """Separate convolution implementation: explicitly multiply F*S in F2[G]."""
    validate_state(state)
    factor = factor_ring(u, v, label)
    result = [[[0] * GROUP_ORDER for _ in range(3)] for _ in range(3)]
    nonzero = [[tuple(h for h, bit in enumerate(entry) if bit) for entry in row] for row in state]
    for r in range(3):
        for c in range(3):
            for k in range(3):
                for left in factor[r][k]:
                    for right in nonzero[k][c]:
                        product = GROUP_INDEX[matmul(GROUP[left], GROUP[right])]
                        result[r][c][product] ^= 1
    return result


def expected_column(state_rows: Sequence[Sequence[Polynomial]], u: Sequence[Polynomial],
                    v: Sequence[Polynomial], labels: Sequence[Polynomial],
                    pullbacks: Sequence[Sequence[int]] = PULLBACKS,
                    exclusive_groups: Iterable[Iterable[Hashable]] = ()) -> list[list[Polynomial]]:
    require(len(state_rows) == len(u) == len(v) == 3, "three register roles required")
    require(all(len(row) == GROUP_ORDER for row in state_rows), "all coefficients required")
    require(len(labels) == len(pullbacks) == 6 and
            all(len(row) == GROUP_ORDER for row in pullbacks), "six full group pullbacks required")
    groups = tuple(frozenset(group) for group in exclusive_groups)
    q = [anf_xor(*(anf_and(v[k], state_rows[k][h], groups) for k in range(3)))
         for h in range(GROUP_ORDER)]
    shifted = [anf_xor(*(anf_and(labels[l], q[pullbacks[l][h]], groups) for l in range(6)))
               for h in range(GROUP_ORDER)]
    return [[anf_xor(state_rows[r][h], anf_and(u[r], anf_xor(q[h], shifted[h]), groups))
             for h in range(GROUP_ORDER)] for r in range(3)]


def expected_transition(state: Sequence[Sequence[Sequence[Polynomial]]], u: Sequence[Polynomial],
                        v: Sequence[Polynomial], labels: Sequence[Polynomial],
                        pullbacks: Sequence[Sequence[int]] = PULLBACKS,
                        exclusive_groups: Iterable[Iterable[Hashable]] = ()) -> list[list[list[Polynomial]]]:
    require(len(state) == 3 and all(len(row) == 3 for row in state), "3 by 3 state required")
    groups = tuple(frozenset(group) for group in exclusive_groups)
    columns = [expected_column([state[r][c] for r in range(3)], u, v, labels, pullbacks, groups)
               for c in range(3)]
    return [[columns[c][r] for c in range(3)] for r in range(3)]


def support_balls(n: int) -> tuple[frozenset[int], ...]:
    require(isinstance(n, int) and n >= 0, "nonnegative ball radius required")
    balls = [frozenset((E_INDEX,))]
    label_indices = tuple(GROUP_INDEX[label] for label in LABELS)
    for _ in range(n):
        previous = balls[-1]
        grown = set(previous)
        grown.update(GROUP_INDEX[matmul(GROUP[label], GROUP[h])]
                     for label in label_indices for h in previous)
        balls.append(frozenset(grown))
    return tuple(balls)


def support_masks(n: int) -> tuple[tuple[frozenset[int], ...], ...]:
    require(n in PUBLISHED_LENGTHS, "published domain is exactly 1 through 9; zero calls excluded")
    balls = support_balls(n)
    targets = (A, B, IDENTITY)
    return tuple(tuple(balls[t] & frozenset(GROUP_INDEX[matmul(GROUP[h], targets[c])]
                                           for h in balls[n - t]) for c in range(3))
                 for t in range(n + 1))


def state_bitstrings(state: Sequence[Sequence[Sequence[int]]]) -> list[list[str]]:
    return [["".join(str(bit) for bit in entry) for entry in row] for row in state]


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _brute_extensions(cnf: CNF, primaries: Mapping[int, int]) -> list[dict[int, int]]:
    free = [var for var in range(2, cnf.nvars + 1) if var not in primaries]
    result = []
    for bits in itertools.product((0, 1), repeat=len(free)):
        values = {1: 1, **primaries, **dict(zip(free, bits))}
        if clauses_hold(cnf.clauses, values):
            result.append(values)
    return result


def primitive_tables() -> tuple[list[dict], list[dict]]:
    rows, controls = [], []
    for op in ("and", "xor", "or"):
        for a, b in itertools.product((2, -2, 3, -3, 1, -1), repeat=2):
            cnf = CNF()
            cnf.new_var()
            cnf.new_var()
            out = getattr(cnf, op + "_gate")(a, b)
            before = (cnf.nvars, len(cnf.clauses))
            require(getattr(cnf, op + "_gate")(b, a) == out, "commutative cache result mismatch")
            require(before == (cnf.nvars, len(cnf.clauses)), "cache changed allocation or clauses")
            for x, y in itertools.product((0, 1), repeat=2):
                inputs = {2: x, 3: y}
                av, bv = literal_value(a, {1: 1, **inputs}), literal_value(b, {1: 1, **inputs})
                expected = av & bv if op == "and" else av ^ bv if op == "xor" else av | bv
                extensions = _brute_extensions(cnf, inputs)
                require(len(extensions) == 1, "primitive lacks unique auxiliary extension")
                actual = literal_value(out, extensions[0])
                require(actual == expected, "primitive semantics mismatch")
                rows.append(dict(op=op, a=a, b=b, x=x, y=y, output=out,
                                 value=actual, unique_extensions=1, clauses=cnf.clauses))
    for op, clauses in (("and", and_clauses(2, 3, 4)), ("xor", xor_clauses(2, 3, 4))):
        for omitted in range(len(clauses)):
            reduced = clauses[:omitted] + clauses[omitted + 1:]
            witnesses = []
            for a, b, z in itertools.product((0, 1), repeat=3):
                values = {1: 1, 2: a, 3: b, 4: z}
                expected = a & b if op == "and" else a ^ b
                if clauses_hold(reduced, values) and z != expected:
                    witnesses.append([a, b, z])
            require(witnesses, "omitted gate direction was not detected")
            controls.append(dict(kind="omitted_gate_clause", op=op, omitted=omitted,
                                 witness=witnesses[0], rejected_by_complete=True))
    require(not clauses_hold(((1,),), {1: 0}) and clauses_hold((), {1: 0}),
            "forced true clause control failed")
    controls.append(dict(kind="omitted_true_unit", witness={"1": 0}))
    # Equality must work in both directions for signed literals and constants.
    for a, b in itertools.product((2, -2, 3, -3, 1, -1), repeat=2):
        for x, y in itertools.product((0, 1), repeat=2):
            values = {1: 1, 2: x, 3: y}
            require(clauses_hold(equality_clauses(a, b), values) ==
                    (literal_value(a, values) == literal_value(b, values)), "equality semantics mismatch")
    for omitted in (0, 1):
        raw = equality_clauses(2, 3)
        reduced = raw[:omitted] + raw[omitted + 1:]
        witness = next([x, y] for x, y in itertools.product((0, 1), repeat=2)
                       if x != y and clauses_hold(reduced, {1: 1, 2: x, 3: y}))
        controls.append(dict(kind="omitted_equality_direction", omitted=omitted, witness=witness))
    signed_cache = CNF()
    x, y = signed_cache.new_var(), signed_cache.new_var()
    base = signed_cache.xor_gate(x, y)
    allocation = (signed_cache.nvars, len(signed_cache.clauses))
    require(signed_cache.xor_gate(-x, -y) == base and
            signed_cache.xor_gate(-x, y) == signed_cache.xor_gate(x, -y) == -base,
            "signed XOR cache identity mismatch")
    require(allocation == (signed_cache.nvars, len(signed_cache.clauses)),
            "signed XOR cache unnecessarily allocated")
    return rows, controls


def raw_clause_tables() -> tuple[list[dict], list[dict]]:
    relations, normalization = [], []
    choices = (2, -2, 3, -3, 1, -1)
    for op, factory in (("and", and_clauses), ("xor", xor_clauses)):
        for a, b in itertools.product(choices, repeat=2):
            raw = factory(a, b, 4)
            for x, y, z in itertools.product((0, 1), repeat=3):
                values = {1: 1, 2: x, 3: y, 4: z}
                av, bv = literal_value(a, values), literal_value(b, values)
                expected = av & bv if op == "and" else av ^ bv
                accepted = clauses_hold(raw, values)
                require(accepted == (z == expected), "raw signed gate-clause semantics mismatch")
                relations.append(dict(op=op, a=a, b=b, x=x, y=y, z=z, accepted=accepted))
    for mask in range(1 << len(choices)):
        raw = tuple(lit for index, lit in enumerate(choices) if mask & (1 << index))
        normalized = normalize_clauses((raw,))
        for x, y in itertools.product((0, 1), repeat=2):
            values = {1: 1, 2: x, 3: y}
            accepted = clauses_hold((raw,), values)
            require(accepted == clauses_hold(normalized, values), "clause normalization changed meaning")
            normalization.append(dict(raw=raw, normalized=normalized, x=x, y=y, accepted=accepted))
    return relations, normalization


def choice_tables() -> tuple[list[dict], list[dict], list[dict], list[dict]]:
    onehot, dot, selector, controls = [], [], [], []
    cnf = CNF()
    labels = [cnf.new_var() for _ in range(6)]
    cnf.exactly_one(labels)
    for bits in itertools.product((0, 1), repeat=6):
        accepted = clauses_hold(cnf.clauses, {1: 1, **dict(zip(labels, bits))})
        require(accepted == (sum(bits) == 1), "exactly-one semantics mismatch")
        onehot.append(dict(labels=bits, accepted=accepted))
    for omitted in range(1, len(cnf.clauses)):
        reduced = cnf.clauses[:omitted] + cnf.clauses[omitted + 1:]
        witness = next(bits for bits in itertools.product((0, 1), repeat=6)
                       if sum(bits) != 1 and clauses_hold(reduced, {1: 1, **dict(zip(labels, bits))}))
        controls.append(dict(kind="omitted_onehot_clause", omitted=omitted, witness=witness))
    cnf = CNF()
    uv = [cnf.new_var() for _ in range(6)]
    terms = [cnf.and_gate(uv[k], uv[k + 3]) for k in range(3)]
    out = cnf.xor_gate(cnf.xor_gate(terms[0], terms[1]), terms[2])
    cnf.clauses.append((out,))
    for bits in itertools.product((0, 1), repeat=6):
        values = cnf.extend(dict(zip(uv, bits)))
        expected = sum(bits[k] * bits[k + 3] for k in range(3)) % 2
        accepted = clauses_hold(cnf.clauses, values)
        require(accepted == bool(expected), "vTu legal factor mismatch")
        require(len(_brute_extensions(cnf, dict(zip(uv, bits)))) == expected,
                "vTu auxiliary uniqueness mismatch")
        dot.append(dict(u=bits[:3], v=bits[3:], dot=expected, accepted=accepted))
    zero_values = cnf.extend(dict.fromkeys(uv, 0))
    require(not clauses_hold(cnf.clauses, zero_values) and clauses_hold(cnf.clauses[:-1], zero_values),
            "omitted vTu assertion control failed")
    controls.append(dict(kind="omitted_vTu_one_unit", u=[0, 0, 0], v=[0, 0, 0],
                         accepted_without_unit=True, rejected_by_complete=True))
    cnf = CNF()
    labels = [cnf.new_var() for _ in range(6)]
    qs = [cnf.new_var() for _ in range(6)]
    terms = [cnf.and_gate(a, b) for a, b in zip(labels, qs)]
    or_out, xor_out = -1, -1
    for term in terms:
        or_out = cnf.or_gate(or_out, term)
        xor_out = cnf.xor_gate(xor_out, term)
    for lb in itertools.product((0, 1), repeat=6):
        for qb in itertools.product((0, 1), repeat=6):
            values = cnf.extend(dict(zip(labels + qs, lb + qb)))
            require(clauses_hold(cnf.clauses, values), "selector gate extension failed")
            or_expected = int(any(a & b for a, b in zip(lb, qb)))
            xor_expected = sum(a * b for a, b in zip(lb, qb)) % 2
            ov, xv = literal_value(or_out, values), literal_value(xor_out, values)
            require((ov, xv) == (or_expected, xor_expected), "selector formula mismatch")
            if sum(lb) == 1:
                require(ov == xv == qb[lb.index(1)], "onehot selector mismatch")
            selector.append(dict(labels=lb, q=qb, onehot=sum(lb) == 1, or_value=ov, xor_value=xv))
    controls.append(dict(kind="missing_exactly_one_selector", labels=[1, 1, 0, 0, 0, 0],
                         q=[1, 1, 0, 0, 0, 0], or_value=1, xor_value=0))
    return onehot, dot, selector, controls


def full_coefficient_tests() -> tuple[dict, list[dict], list[dict]]:
    require(GROUP_ORDER == 168 and len(set(LABELS)) == 6 and len(LEGAL_UV) == 28,
            "group or legal-factor count mismatch")
    for index, element in enumerate(GROUP):
        inverse = INVERSES[index]
        require(matmul(element, inverse) == matmul(inverse, element) == IDENTITY, "group inverse mismatch")
    for label, pullback in zip(LABELS, PULLBACKS):
        require(matmul(label, label) == IDENTITY and len(set(pullback)) == 168, "label permutation mismatch")
    rng = random.Random(0xB40004)
    dirty = [[[rng.randrange(2) for _ in GROUP] for _ in range(3)] for _ in range(3)]
    factors, controls = [], []
    for label in range(6):
        for u, v in LEGAL_UV:
            dense = transition_dense(dirty, u, v, label)
            ring = transition_ring(dirty, u, v, label)
            require(dense == ring, "dense recurrence and independent ring convolution disagree")
            require(transition_dense(dense, u, v, label) == dirty, "factor is not involutive")
            factors.append(dict(label=label, u=u, v=v, output_sha256=digest(state_bitstrings(dense))))
    variables = [[[anf_var(("S", r, c, h)) for h in range(168)] for c in range(3)] for r in range(3)]
    ups = [anf_var(("u", r)) for r in range(3)]
    vps = [anf_var(("v", r)) for r in range(3)]
    lps = [anf_var(("label", l)) for l in range(6)]
    label_keys = frozenset(("label", l) for l in range(6))
    expected = expected_transition(variables, ups, vps, lps, exclusive_groups=(label_keys,))
    expression_table = [dict(r=r, c=c, h=h, terms=anf_serializable(expected[r][c][h]))
                        for r in range(3) for c in range(3) for h in range(168)]
    evaluations = 0
    for label, u, v in ((0, (1, 0, 0), (1, 0, 0)),
                         (5, (1, 1, 1), (1, 1, 1)),
                         (2, (0, 1, 1), (1, 1, 0))):
        values = {("S", r, c, h): dirty[r][c][h]
                  for r in range(3) for c in range(3) for h in range(168)}
        values.update({("u", r): u[r] for r in range(3)})
        values.update({("v", r): v[r] for r in range(3)})
        values.update({("label", l): int(l == label) for l in range(6)})
        actual = transition_dense(dirty, u, v, label)
        for r in range(3):
            for c in range(3):
                for h in range(168):
                    require(anf_evaluate(expected[r][c][h], values) == actual[r][c][h],
                            "generic coefficient ANF evaluation mismatch")
                    evaluations += 1
    # Check OR construction versus XOR modulo onehot orthogonality for every h.
    q = [anf_xor(*(anf_and(vps[k], variables[k][0][h]) for k in range(3))) for h in range(168)]
    for h in range(168):
        terms = [anf_and(lps[l], q[PULLBACKS[l][h]]) for l in range(6)]
        or_poly = ZERO
        for term in terms:
            or_poly = anf_or(or_poly, term, (label_keys,))
        require(or_poly == anf_xor(*terms), "onehot OR and XOR polynomial mismatch")
    # Every coefficient equation is needed as a relation, including constants.
    # Fixing the primary dirty state and choices reduces each next-state equality
    # to a literal unit. Actually evaluate the complete and single-omission CNFs.
    correct = transition_dense(dirty, (1, 0, 0), (1, 0, 0), 0)
    coefficient_controls = []
    endpoint = endpoint_state()
    endpoint_controls = []
    output_keys = [(r, c, h) for r in range(3) for c in range(3) for h in range(168)]
    output_vars = {key: index + 2 for index, key in enumerate(output_keys)}
    correct_values = {1: 1, **{output_vars[r, c, h]: correct[r][c][h] for r, c, h in output_keys}}
    endpoint_values = {1: 1, **{output_vars[r, c, h]: endpoint[r][c][h] for r, c, h in output_keys}}
    coefficient_units = [(var if correct_values[var] else -var,) for var in output_vars.values()]
    endpoint_units = [(var if endpoint_values[var] else -var,) for var in output_vars.values()]
    require(clauses_hold(coefficient_units, correct_values) and clauses_hold(endpoint_units, endpoint_values),
            "positive complete output relation rejected")
    for r in range(3):
        for c in range(3):
            for h in range(168):
                var = output_vars[r, c, h]
                index = var - 2
                flipped = correct_values[var] ^ 1
                candidate = {**correct_values, var: flipped}
                require(not clauses_hold(coefficient_units, candidate) and
                        clauses_hold(coefficient_units[:index] + coefficient_units[index + 1:], candidate),
                        "coefficient omission control failed")
                coefficient_controls.append([r, c, h, correct[r][c][h], flipped])
                wrong_endpoint = endpoint_values[var] ^ 1
                candidate = {**endpoint_values, var: wrong_endpoint}
                require(not clauses_hold(endpoint_units, candidate) and
                        clauses_hold(endpoint_units[:index] + endpoint_units[index + 1:], candidate),
                        "endpoint omission control failed")
                endpoint_controls.append([r, c, h, endpoint[r][c][h], wrong_endpoint])
    controls.extend((dict(kind="all_coefficient_equation_omissions", count=1512,
                          witnesses_sha256=digest(coefficient_controls)),
                     dict(kind="all_endpoint_unit_omissions", count=1512,
                          witnesses_sha256=digest(endpoint_controls))))
    # Noncommutative dirty-state witness detects left/right coefficient translation.
    mismatch = None
    for label in range(6):
        for h in range(168):
            right_pullback = GROUP_INDEX[matmul(GROUP[h], LABELS[label])]
            left_pullback = PULLBACKS[label][h]
            if right_pullback != left_pullback:
                mismatch = dict(label=label, output_h=h, correct_input_h=left_pullback,
                                wrong_right_translate_input_h=right_pullback)
                break
        if mismatch is not None:
            break
    require(mismatch is not None, "left/right translation order control missing")
    # Put one coefficient at the left pullback, so the incorrect side produces
    # an actually different output, rather than merely a different index string.
    side_state = [[[0] * 168 for _ in range(3)] for _ in range(3)]
    side_state[0][0][mismatch["correct_input_h"]] = 1
    side_output = transition_dense(side_state, (1, 0, 0), (1, 0, 0), mismatch["label"])
    h = mismatch["output_h"]
    incorrect_value = side_state[0][0][h] ^ side_state[0][0][h] ^ side_state[0][0][mismatch["wrong_right_translate_input_h"]]
    require(side_output[0][0][h] != incorrect_value, "wrong-side translation did not change actual coefficient")
    controls.append(dict(kind="wrong_coefficient_translation_side", **mismatch,
                         correct_output=side_output[0][0][h], wrong_output=incorrect_value))
    first, second = 0, 3
    chronological = matmul(LABELS[second], LABELS[first])
    reversed_product = matmul(LABELS[first], LABELS[second])
    require(chronological != reversed_product, "chronological order control missing")
    ordered_state = identity_state()
    for label in (first, second):
        ordered_state = transition_dense(ordered_state, (1, 0, 0), (1, 0, 0), label)
    require(ordered_state[0][0][GROUP_INDEX[chronological]] == 1 and
            ordered_state[0][0][GROUP_INDEX[reversed_product]] == 0,
            "chronological order actual state control failed")
    controls.append(dict(kind="wrong_chronological_order", factors=[first, second],
                         correct=chronological, wrong=reversed_product))
    # Right translation in support masks can differ from left translation.
    balls = support_balls(2)
    support_side_witness = None
    for radius in (1, 2):
        for target in (A, B):
            right = frozenset(matmul(GROUP[h], target) for h in balls[radius])
            left = frozenset(matmul(target, GROUP[h]) for h in balls[radius])
            if right != left:
                support_side_witness = dict(radius=radius, target=target,
                                            right_only=sorted(right - left), left_only=sorted(left - right))
                break
        if support_side_witness:
            break
    require(support_side_witness is not None, "support right-translation control missing")
    controls.append(dict(kind="wrong_support_translation_side", **support_side_witness))
    require(support_masks(7) and support_masks(8), "focus support masks missing")
    # Specialize the full expression family at an actual support cut, retaining
    # every output equation, including outputs that the next mask sets to zero.
    masks = support_masks(7)
    zero_keys = frozenset(("S", r, c, h) for r in range(3) for c in range(3)
                          for h in range(168) if h not in masks[3][c])
    specialized_inputs = [[[ZERO if ("S", r, c, h) in zero_keys else variables[r][c][h]
                           for h in range(168)] for c in range(3)] for r in range(3)]
    specialized = expected_transition(specialized_inputs, ups, vps, lps,
                                      exclusive_groups=(label_keys,))
    for r, c, h in output_keys:
        direct = frozenset(term for term in expected[r][c][h] if not (term & zero_keys))
        require(specialized[r][c][h] == direct, "support-zero ANF specialization mismatch")
    forbidden_witness = None
    for c in range(3):
        for input_h in masks[3][c]:
            for label in range(6):
                output_h = GROUP_INDEX[matmul(LABELS[label], GROUP[input_h])]
                if output_h not in masks[4][c]:
                    restricted_input = [[[0] * 168 for _ in range(3)] for _ in range(3)]
                    restricted_input[0][c][input_h] = 1
                    local_next = transition_dense(restricted_input, (1, 0, 0), (1, 0, 0), label)
                    nonzero = [(r, cc, hh) for r, cc, hh in output_keys if local_next[r][cc][hh]]
                    require(nonzero == [(0, c, output_h)], "forbidden output witness is not isolated")
                    candidate = {1: 1, **dict.fromkeys(output_vars.values(), 0)}
                    full_units = [(output_vars[r, cc, hh] if local_next[r][cc][hh]
                                   else -output_vars[r, cc, hh],) for r, cc, hh in output_keys]
                    index = output_vars[0, c, output_h] - 2
                    require(not clauses_hold(full_units, candidate) and
                            clauses_hold(full_units[:index] + full_units[index + 1:], candidate),
                            "omitted forbidden-output equation control failed")
                    forbidden_witness = dict(n=7, cut=3, c=c, input_h=input_h, label=label,
                                             forbidden_output_r=0, forbidden_output_h=output_h,
                                             complete_rejects=True, omission_accepts=True,
                                             scope="local transition, not an attaining-word counterexample")
                    break
            if forbidden_witness:
                break
        if forbidden_witness:
            break
    require(forbidden_witness is not None, "no support-forbidden output omission control found")
    controls.append(dict(kind="omitted_support_forbidden_output_equation", **forbidden_witness))
    try:
        support_masks(0)
    except ValueError:
        controls.append(dict(kind="zero_call_outside_published_domain", rejected=True))
    else:
        raise ValueError("zero-call domain guard failed")
    vectors = []
    for name, initial, word in (
            ("identity_onecall", identity_state(), [(0, (1, 0, 0), (1, 0, 0))]),
            ("dirty_onecall", dirty, [(5, (1, 1, 1), (1, 1, 1))]),
            ("dirty_twocall", dirty, [(0, (1, 1, 0), (1, 0, 1)), (3, (0, 1, 1), (1, 1, 0))]),
            ("dirty_fourcall", dirty, [(1, (1, 0, 1), (1, 1, 0)), (4, (1, 1, 1), (1, 1, 1)),
                                       (2, (0, 1, 0), (1, 1, 1)), (5, (1, 0, 0), (1, 0, 1))])):
        current = initial
        states = [state_bitstrings(current)]
        for label, u, v in word:
            nxt = transition_dense(current, u, v, label)
            require(nxt == transition_ring(current, u, v, label), "multistep positive vector mismatch")
            current = nxt
            states.append(state_bitstrings(current))
        vectors.append(dict(name=name, initial=states[0], word=[dict(label=l, u=u, v=v) for l, u, v in word],
                            states=states, target=states[-1]))
    summary = dict(group_order=168, coordinate_labels=[dict(i=i, j=j, rows=g)
                                                      for (i, j), g in zip(LABEL_COORDINATES, LABELS)],
                   legal_uv_count=28, legal_factor_count=168, independently_crosschecked_factors=factors,
                   dirty_state=state_bitstrings(dirty), coefficient_expressions=expression_table,
                   coefficient_expression_count=1512, coefficient_evaluations=evaluations,
                   support_zero_specialization=dict(n=7, cut=3, zeroed_primary_count=len(zero_keys),
                       expressions_sha256=digest([anf_serializable(specialized[r][c][h])
                                                  for r, c, h in output_keys]),
                       verified_output_equations=1512),
                   support_masks={str(n): [[sorted(mask) for mask in cut] for cut in support_masks(n)]
                                  for n in (7, 8)},
                   coefficient_omission_witnesses=coefficient_controls,
                   endpoint_omission_witnesses=endpoint_controls)
    return summary, vectors, controls


def selftest() -> dict:
    primitive, controls = primitive_tables()
    raw_gates, normalization = raw_clause_tables()
    onehot, dot, selector, choice_controls = choice_tables()
    coefficients, vectors, coefficient_controls = full_coefficient_tests()
    controls += choice_controls + coefficient_controls
    # Boolean algebra and quotient checks are independent of gate allocation.
    x, y = anf_var("x"), anf_var("y")
    require(anf_and(x, x) == x and anf_xor(x, x) == ZERO, "Boolean polynomial reduction mismatch")
    require(anf_and(x, y, ({"x", "y"},)) == ZERO, "onehot orthogonality quotient mismatch")
    require(anf_or(x, y) == anf_xor(x, y, anf_and(x, y)), "OR polynomial identity mismatch")
    report = dict(schema="b4-independent-cnf-oracle-v1", status="PASS",
                  provenance="Independent construction by Toik Y with substantial OpenAI Codex assistance; original argument Brian Ross",
                  source_access_before_freeze=False, sat_solver_calls=0, minimum_claim=None,
                  published_length_domain=list(PUBLISHED_LENGTHS),
                  group=[list(g) for g in GROUP], inverse=[list(g) for g in INVERSES],
                  pullbacks=PULLBACKS, primitive_truth_table=primitive, exactly_one_table=onehot,
                  raw_signed_gate_relation_table=raw_gates, clause_normalization_table=normalization,
                  vTu_table=dot, selector_table=selector, coefficients=coefficients,
                  positive_vectors=vectors, negative_controls=controls,
                  counts=dict(primitive_truth_rows=len(primitive), onehot_rows=len(onehot),
                              raw_signed_gate_relation_rows=len(raw_gates),
                              clause_normalization_rows=len(normalization),
                              vTu_rows=len(dot), vTu_legal=sum(row["accepted"] for row in dot),
                              selector_rows=len(selector), negative_controls=len(controls),
                              coefficient_expressions=1512, coefficient_omission_controls=1512,
                              endpoint_omission_controls=1512))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fulltable", action="store_true", help="emit complete deterministic selftest table to stdout")
    parser.add_argument("--summary", action="store_true", help="emit compact deterministic selftest summary (default)")
    args = parser.parse_args()
    report = selftest()
    if args.fulltable:
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    else:
        print(json.dumps(dict(schema=report["schema"], status=report["status"], counts=report["counts"],
                              fulltable_sha256=digest(report), sat_solver_calls=0, minimum_claim=None,
                              source_access_before_freeze=False), sort_keys=True))


if __name__ == "__main__":
    main()
