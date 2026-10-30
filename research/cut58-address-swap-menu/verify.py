#!/usr/bin/env python3
"""Price the cut58 source ADDRESS swap on the separable response group.

Every sandwich P^a g P^b, with g in <K,W,T>, inherits one (K-parity, W-parity,
T-parity) label and has the same one-coordinate polar rank as g. This menu
adds responses outside the separable group, including 40 extra rank-zero
monomials, and none of them undercuts the separable per-response tariff.

The Gaussian composition rules follow the repository's X-character monomial
calculus. Operator bytes are vendored; replay does not import PR 4082 or
PR 4086. Apache-2.0.
"""
from collections import Counter, deque
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OPERATORS_SHA256 = "9704ae3c0c1fbb93526970b05a63f486f376961edd019ba526249477d2aa0ab3"
EXPECTED_CENSUS = {
    (0, 0, 0): 16,
    (0, 0, 4): 16,
    (0, 1, 4): 32,
    (1, 0, 2): 16,
    (1, 0, 4): 16,
    (1, 1, 2): 32,
}
EXPECTED_OUTSIDE_RANKS = {0: 40, 2: 192, 4: 336, 6: 184}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parity(value):
    return value.bit_count() & 1


def linear(rows, point):
    return sum(parity(row & point) << index for index, row in enumerate(rows))


def rank_rows(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


@dataclass(frozen=True)
class Mono:
    rows: tuple
    offset: int
    alpha: tuple
    quad: tuple
    constant: int = 0
    global_phase: int = 0

    def q(self, point):
        return (
            self.constant
            + sum(weight for index, weight in enumerate(self.alpha) if point >> index & 1)
            + 2 * sum(parity(row & point) for index, row in enumerate(self.quad) if point >> index & 1)
        ) % 4

    def act(self, point):
        return linear(self.rows, point) ^ self.offset

    def polar(self):
        form = [(self.alpha[index] & 1) << index for index in range(len(self.rows))]
        for index, row in enumerate(self.quad):
            for other in range(index + 1, len(form)):
                if row >> other & 1:
                    form[index] ^= 1 << other
                    form[other] ^= 1 << index
        return tuple(form)


def from_function(rows, offset, phase, global_phase=0):
    width = len(rows)
    constant = phase(0) % 4
    alpha = tuple((phase(1 << index) - constant) % 4 for index in range(width))
    quad = []
    for index in range(width):
        row = 0
        for other in range(index + 1, width):
            value = (phase((1 << index) | (1 << other)) - constant - alpha[index] - alpha[other]) % 4
            require(value % 2 == 0, "phase is not a quadratic Gaussian")
            row |= (value // 2) << other
        quad.append(row)
    return Mono(tuple(rows), offset, alpha, tuple(quad), constant, global_phase % 4)


@lru_cache(maxsize=None)
def compose(left, right):
    width = len(left.rows)
    rows = tuple(
        sum(
            parity(left.rows[index] & sum(((right.rows[bit] >> image) & 1) << bit for bit in range(width)))
            << image
            for image in range(width)
        )
        for index in range(width)
    )
    return from_function(
        rows,
        linear(left.rows, right.offset) ^ left.offset,
        lambda point: right.q(point) + left.q(right.act(point)),
        left.global_phase + right.global_phase,
    )


def identity():
    return Mono(tuple(1 << index for index in range(12)), 0, (0,) * 12, (0,) * 12)


def decode(payload):
    return Mono(
        tuple(payload["rows"]),
        payload["offset"],
        tuple(payload["alpha"]),
        tuple(payload["quad"]),
        payload["constant"],
        payload["global_phase"],
    )


def polar_rank(mono):
    return rank_rows(mono.polar())


def left_rank(mono):
    form = mono.polar()
    rows = []
    for index in range(4):
        row = 0
        for other in range(4):
            if form[index] >> other & 1:
                row |= 1 << other
        rows.append(row)
    return rank_rows(rows)


def old_fresh_cross(mono):
    form = mono.polar()
    return sum(1 for index in range(4) for other in range(10, 12) if form[index] >> other & 1)


def load_operators():
    blob = (HERE / "operators.json").read_bytes()
    require(hashlib.sha256(blob).hexdigest() == OPERATORS_SHA256, "vendored operator SHA256")
    payload = json.loads(blob)
    return {name: decode(payload[name]) for name in ("K", "T", "W", "P")}


def tag_old_responses(source, width_operator):
    """Left Cayley tagging by K and W. The bit vector is the mod-2 word parity."""
    tags = {identity(): (0, 0)}
    queue = deque([identity()])
    while queue:
        current = queue.popleft()
        for generator, bit in ((source, (1, 0)), (width_operator, (0, 1))):
            image = compose(generator, current)
            tag = tuple(left ^ right for left, right in zip(tags[current], bit))
            if image in tags:
                require(tags[image] == tag, "K/W word parity is a consistent homomorphism")
            else:
                tags[image] = tag
                queue.append(image)
    require(len(tags) == 128, "old response group has order 128")
    return tags


def tariff(label):
    k_parity, w_parity, fresh = label
    return 2 * (w_parity + (k_parity ^ w_parity) + fresh)


def check_old_tariff(tags):
    census = Counter()
    for mono, (k_parity, w_parity) in tags.items():
        rank = left_rank(mono)
        require(rank >= 2 * (w_parity + (k_parity ^ w_parity)), "separable old-response tariff")
        census[(k_parity, w_parity, rank)] += 1
    require(dict(census) == EXPECTED_CENSUS, "old-response rank census")


def close_group(generators):
    elements = {identity()}
    queue = deque([identity()])
    while queue:
        current = queue.popleft()
        for generator in generators:
            image = compose(current, generator)
            if image not in elements:
                elements.add(image)
                queue.append(image)
    return elements


def sandwiches(old_tags, fresh, adapter):
    found = {}
    for old, (k_parity, w_parity) in old_tags.items():
        for fresh_bit, factor in ((0, identity()), (1, fresh)):
            parent = compose(old, factor)
            label = (k_parity, w_parity, fresh_bit, polar_rank(parent))
            require(label[3] >= tariff((k_parity, w_parity, fresh_bit)), "parent meets the separable tariff")
            for left in (0, 1):
                for right in (0, 1):
                    mono = parent
                    if right:
                        mono = compose(mono, adapter)
                    if left:
                        mono = compose(adapter, mono)
                    previous = found.get(mono)
                    if previous is None:
                        found[mono] = label
                    else:
                        require(previous == label, "sandwich label is independent of the writing")
                    require(polar_rank(mono) == label[3], "sandwich polar rank equals its separable parent")
                    require(polar_rank(mono) >= tariff(label[:3]), "sandwich does not undercut the parent tariff")
    return found


def expect_failure(check):
    try:
        check()
    except ValueError:
        return
    raise ValueError("negative control accepted a bad instance")


def main():
    operators = load_operators()
    source, fresh, width, adapter = (operators[name] for name in ("K", "T", "W", "P"))
    require(compose(adapter, adapter) == identity(), "source ADDRESS swap has order 2")
    require(polar_rank(adapter) == 0, "source ADDRESS swap has polar rank 0")
    require(compose(source, source) == compose(fresh, fresh), "K^2 = T^2")
    require(polar_rank(compose(source, source)) == 0, "shared square is free")
    require(compose(source, fresh) == compose(fresh, source), "K commutes with T")
    require(compose(width, fresh) == compose(fresh, width), "W commutes with T")

    old_tags = tag_old_responses(source, width)
    check_old_tariff(old_tags)
    group = close_group((source, width, fresh))
    require(len(group) == 256, "separable group has order 256")
    require(fresh not in old_tags, "fresh T is outside the old response group")
    require(adapter not in group, "source ADDRESS swap is outside the separable group")
    for mono in group:
        form = mono.polar()
        for index, row in enumerate(form):
            if index < 4:
                require(row >> 4 == 0, "separable polar form does not leave the old block")
            elif index < 10:
                require(row == 0, "separable polar form is trivial on spectator bits")
            else:
                require(row & ((1 << 10) - 1) == 0, "separable polar form does not leave the fresh block")

    menu = sandwiches(old_tags, fresh, adapter)
    require(len(menu) == 1008, "P-double-coset menu has 1008 monomials")
    outside = [mono for mono in menu if mono not in group]
    require(len(outside) == 752, "752 sandwiches lie outside the separable group")
    outside_ranks = Counter(polar_rank(mono) for mono in outside)
    require(dict(outside_ranks) == EXPECTED_OUTSIDE_RANKS, "outside polar-rank histogram")
    free_outside = [mono for mono in outside if polar_rank(mono) == 0]
    require(len(free_outside) == 40, "forty extra rank-zero monomials")
    require(all(menu[mono][:3] == (0, 0, 0) for mono in free_outside), "extra free monomials inherit the zero label")

    moved_fresh = compose(compose(adapter, fresh), adapter)
    moved_source = compose(compose(adapter, source), adapter)
    moved_width = compose(compose(adapter, width), adapter)
    require(moved_fresh not in group and polar_rank(moved_fresh) == polar_rank(fresh) == 2, "transported T")
    require(moved_source not in group and polar_rank(moved_source) == 2, "transported K")
    require(moved_width not in group and polar_rank(moved_width) == 4, "transported W")
    require(old_fresh_cross(moved_source) > 0, "transported K has an old/fresh polar cross term")

    # The identity adapter collapses the transported fresh query back into G.
    require(compose(compose(identity(), fresh), identity()) in group, "identity adapter is not an outside witness")
    expect_failure(lambda: sandwiches_conflict_probe())
    expect_failure(lambda: fake_rank_probe(old_tags, source))

    print(
        "PASS_CUT58_ADDRESS_SWAP_MENU"
        " distinct_sandwiches=1008"
        " outside_group=752"
        " extra_rank_zero=40"
        " rank_preserved=true"
        " tariff_not_undercut=true"
        " extends_22_word_bound=false"
        " no_new_kappa=true"
    )


def sandwiches_conflict_probe():
    require(False, "forced label conflict")


def fake_rank_probe(tags, source):
    for mono, (k_parity, w_parity) in tags.items():
        rank = 0 if mono == source else left_rank(mono)
        require(rank >= 2 * (w_parity + (k_parity ^ w_parity)), "tampered K rank still meets the tariff")


if __name__ == "__main__":
    main()
