"""Independent checks of the UT3(F4) central-triple paid-call model.

Scope: this file checks the group law and the finite facts the open
central-triple results rest on, verifies the two twelve-call witnesses and
their single-deletion controls in an independently written model, validates
the block collapse the lower-bound arguments use, and runs a bounded
falsification search for a realizing word of length at most eleven.  It does
not machine-verify the step from these finite facts to the all-r lower bound.

No new kappa.  Selected kappa is unchanged.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model as M  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
FAILURES: list[str] = []


def need(condition: bool, label: str) -> None:
    if not condition:
        FAILURES.append(label)
        print("FAIL", label)


# ---------------------------------------------------------------- group law


def group_law() -> dict:
    need(len({M.h_mul(i, j) for i in range(64) for j in range(64)}) == 64,
         "closure")
    need(all(M.h_mul(M.h_mul(i, j), k) == M.h_mul(i, M.h_mul(j, k))
             for i in range(64) for j in range(64) for k in range(64)),
         "associativity")
    need(all(M.h_mul(i, M.H_IDENTITY) == i and M.h_mul(M.H_IDENTITY, i) == i
             for i in range(64)), "identity")
    need(all(M.h_mul(i, M.h_inverse(i)) == M.H_IDENTITY for i in range(64)),
         "inverses")
    involutions = sum(1 for _n, element, _t in M.LETTERS
                      if M.h_mul(element, element) == M.H_IDENTITY)
    need(involutions == 6, "six involutions")
    alphabet = (1, 2, 3)
    commutators = {}
    for i, (xname, xel, _xt) in enumerate(M.LETTERS[:3]):
        for j, (yname, yel, _yt) in enumerate(M.LETTERS[3:]):
            commutators[(xname, yname)] = M.commutator(xel, yel)
            expected = M.h_index(0, 0, M.f4_mul(alphabet[i], alphabet[j]))
            need(commutators[(xname, yname)] == expected,
                 f"commutator {xname},{yname}")
    need(len(set(commutators.values())) == 3, "three distinct commutators")
    need(set(commutators.values()) == set(M.Z_LABELS), "commutator Z labels")
    return {"elements": 64, "involutions": involutions,
            "commutator_classes": len(set(commutators.values()))}


# ----------------------------------------------------------- matrix census


def matrix_rank(rows: list[int]) -> int:
    basis: list[int] = []
    for row in rows:
        cur = row
        for b in basis:
            cur = min(cur, cur ^ b)
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    return len(basis)


def matrix_census(r: int) -> dict:
    rank_one = []
    for bits in range(1 << (r * r)):
        rows = M.bit_matrix_rows(bits, r)
        if any(rows) and matrix_rank(rows) == 1:
            rank_one.append(rows)
    idempotent_rank_one = [rows for rows in rank_one if M.is_idempotent(rows)]
    trace_zero = [rows for rows in rank_one
                  if sum((rows[i] >> i) & 1 for i in range(r)) % 2 == 0]
    enumerated = M.rank_one_idempotents(r)
    need(len(rank_one) == ((1 << r) - 1) ** 2, "rank-one count")
    need(len(idempotent_rank_one) == len(enumerated),
         "idempotent rank-one count matches u v^T enumeration")
    need(sorted(tuple(x) for x in idempotent_rank_one)
         == sorted(tuple(x) for x in enumerated), "identical idempotent sets")
    need(len(trace_zero) == len(rank_one) - len(idempotent_rank_one),
         "trace-zero complement")
    if r == 3:
        need(len(rank_one) == 49, "r=3 rank-one count 49")
        need(len(idempotent_rank_one) == 28, "r=3 rank-one idempotents 28")
        need(len(trace_zero) == 21, "r=3 trace-zero rank-one 21")
        need(len({tuple(x) for x in enumerated}) == 28, "28 distinct products")
    return {"r": r, "rank_one": len(rank_one),
            "rank_one_idempotents": len(idempotent_rank_one),
            "rank_one_trace_zero": len(trace_zero)}


# ---------------------------------------------------------------- witnesses


def mixed_word(r: int) -> list[tuple[int, list[int]]]:
    """E_tt: X_a Y_1 X_a Y_1 with a = 1, w, w^2."""
    word = []
    for t in range(3):
        proj = M.projector(r, t)
        for letter in (t, 3, t, 3):
            word.append((letter, proj))
    return word


def both_new_word(r: int) -> list[tuple[int, list[int]]]:
    """E_00: X_1 Y_1 X_1 Y_1; E_11: X_w2 Y_w2 ...; E_22: X_w Y_w ..."""
    word = []
    for t, (xletter, yletter) in enumerate(((0, 3), (2, 5), (1, 4))):
        proj = M.projector(r, t)
        for letter in (xletter, yletter, xletter, yletter):
            word.append((letter, proj))
    return word


def count_types(word) -> tuple[int, int]:
    return (sum(1 for letter, _n in word if M.LETTER_TYPE[letter] == 0),
            sum(1 for letter, _n in word if M.LETTER_TYPE[letter] == 1))


def nilpotent(letter: int) -> list[int]:
    element = M.LETTER_ELEMENT[letter]
    return [row ^ (1 << i) for i, row in enumerate(M.rho(element))]


def witness_checks() -> dict:
    out = {}
    for name, builder in (("mixed", mixed_word), ("both_new", both_new_word)):
        word = builder(3)
        nx, ny = count_types(word)
        need(nx == 6 and ny == 6, f"{name} call counts")
        need(len(word) == 12, f"{name} length")
        for r in (3, 4, 5):
            need(M.realizes(builder(r), r), f"{name} realizes target r={r}")
            prod = M.word_product(builder(r), r)
            identity = M.identity_rows(6 * r)
            extra_fixed = all(prod[6 * t + i] == identity[6 * t + i]
                              for t in range(3, r) for i in range(6))
            need(extra_fixed, f"{name} spectator fixed r={r}")
        deaths = 0
        for drop in range(len(word)):
            truncated = word[:drop] + word[drop + 1:]
            if not M.realizes(truncated, 3):
                deaths += 1
        need(deaths == 12, f"{name} all 12 single deletions fail")
        out[name] = {"length": len(word), "n_x": nx, "n_y": ny,
                     "deletion_failures": deaths}
    return out


# --------------------------------------------- collapse used by the proofs


def collapse_check(trials: int, rng: random.Random) -> dict:
    """Compare the direct product with I + sum_k E(g_k) x N_k plus the
    surviving second-order corners, i.e. with the block expansion the
    lower-bound arguments use.

    Convention.  The word is stored in time order and multiplied as
    D(g_n)...D(g_1); the nilpotents the model uses satisfy
    E(X)E(Y) != 0 and E(X)E(X) = E(Y)E(X) = 0, so the only surviving pair
    terms are E(g_j)E(g_i) x N_j N_i over i < j with g_j of X-type and
    g_i of Y-type.
    """
    idems = M.rank_one_idempotents(3)
    bad = 0
    for _ in range(trials):
        length = rng.randint(2, 9)
        word = [(rng.randrange(6), rng.choice(idems)) for _ in range(length)]
        direct = M.word_product(word, 3)
        rebuilt = M.identity_rows(18)
        for index, (letter, n) in enumerate(word):
            base = nilpotent(letter)
            for i in range(6):
                for j in range(6):
                    if (base[i] >> j) & 1:
                        for p in range(3):
                            for q in range(3):
                                if (n[p] >> q) & 1:
                                    rebuilt[6 * p + i] ^= 1 << (6 * q + j)
            for earlier in range(index):
                letter0, n0 = word[earlier]
                if M.LETTER_TYPE[letter] == 0 and M.LETTER_TYPE[letter0] == 1:
                    corner = M.mat_mul(nilpotent(letter), nilpotent(letter0))
                    product = M.mat_product(n, n0)
                    for i in range(6):
                        for j in range(6):
                            if (corner[i] >> j) & 1:
                                for p in range(3):
                                    for q in range(3):
                                        if (product[p] >> q) & 1:
                                            rebuilt[6 * p + i] ^= \
                                                1 << (6 * q + j)
        if rebuilt != direct:
            bad += 1
    need(bad == 0, "collapse formula matches direct product")
    return {"trials": trials, "mismatches": bad}


def corner_certificate() -> dict:
    """Rank numbers behind the corner argument."""
    blocks = []
    for z in M.Z_LABELS:
        block = M.rho(z)
        blocks.append([row ^ (1 << i) for i, row in enumerate(block)])
    ranks = [matrix_rank(block) for block in blocks]
    need(ranks == [2, 2, 2], "each corner block has rank 2")
    stacked = [0] * 18
    for reg, block in enumerate(blocks):
        for i in range(6):
            for j in range(6):
                if (block[i] >> j) & 1:
                    stacked[6 * reg + i] |= 1 << (6 * reg + j)
    total_rank = matrix_rank(stacked)
    need(total_rank == 6, "stacked corner rank 6")
    return {"corner_block_ranks": ranks, "stacked_rank": total_rank}


# -------------------------------------------------------- bounded search


def search_uniform(trials: int, rng: random.Random) -> dict:
    idems = M.rank_one_idempotents(3)
    target = M.target_matrix(3)
    hits = 0
    for _ in range(trials):
        length = rng.randint(6, 11)
        word = [(rng.randrange(6), rng.choice(idems)) for _ in range(length)]
        if M.word_product(word, 3) == target:
            hits += 1
    need(hits == 0, "uniform search found no shorter word")
    return {"trials": trials, "length_range": [6, 11], "r": 3, "hits": hits}


def side_from_classes(sizes, common, idems, rng):
    """Fill class multisets: cancellation pairs plus, for odd sizes, one copy
    of the common value.  Every class then sums to `common`."""
    filled = []
    for size in sizes:
        group: list[list[int]] = []
        remaining = size
        while remaining >= 2:
            pick = list(rng.choice(idems))
            group.append(pick)
            group.append(list(pick))
            remaining -= 2
        if remaining == 1:
            group.append(list(common))
        filled.append(group)
    return filled


def class_sums(groups):
    sums = []
    for group in groups:
        acc = [0, 0, 0]
        for call in group:
            for i in range(3):
                acc[i] ^= call[i]
        sums.append(acc)
    return sums


def feasible_shapes(n_calls: int, nonzero_common: bool) -> list[tuple[int, int, int]]:
    """Class-size triples summing to n_calls whose sums can all be equal.

    With a nonzero common value every class needs an unpaired idempotent, so
    every size is odd; with common value zero every class cancels in pairs,
    so every size is even.  A nonzero common value therefore forces an odd
    call count on that side.
    """
    shapes = []
    for a in range(n_calls + 1):
        for b in range(n_calls - a + 1):
            c = n_calls - a - b
            parts = (a, b, c)
            if nonzero_common:
                ok = all(p % 2 == 1 for p in parts)
            else:
                ok = all(p % 2 == 0 for p in parts)
            if ok:
                shapes.append(parts)
    return shapes


def search_class_sum_feasible(draws: int, rng: random.Random) -> dict:
    """Sample words whose three per-letter-class idempotent sums are equal.

    The (0,1) and (1,2) blocks of a realizing word force the three sums to
    be equal, so every realizing word lies in this family; the sample is
    drawn shape by shape from that family, not uniformly from the word
    space.  Class multisets are cancellation pairs plus one unpaired
    idempotent where the parity requires it, which realizes every feasible
    shape for four to six calls per side.
    """
    idems = M.rank_one_idempotents(3)
    target = M.target_matrix(3)
    tested = 0
    hits = 0
    shape_counts: dict[str, int] = {}
    for _ in range(draws):
        nonzero_x = rng.random() < 0.5
        nonzero_y = rng.random() < 0.5
        common_x = list(rng.choice(idems)) if nonzero_x else [0, 0, 0]
        common_y = list(rng.choice(idems)) if nonzero_y else [0, 0, 0]
        n_x = 5 if nonzero_x else rng.choice([4, 6])
        n_y = 5 if nonzero_y else rng.choice([4, 6])
        shapes_x = feasible_shapes(n_x, nonzero_x)
        shapes_y = feasible_shapes(n_y, nonzero_y)
        if not shapes_x or not shapes_y:
            continue
        sizes_x = list(rng.choice(shapes_x))
        sizes_y = list(rng.choice(shapes_y))
        rng.shuffle(sizes_x)
        rng.shuffle(sizes_y)
        calls_x = side_from_classes(sizes_x, common_x, idems, rng)
        calls_y = side_from_classes(sizes_y, common_y, idems, rng)
        for groups in (calls_x, calls_y):
            sums = class_sums(groups)
            if not (sums[0] == sums[1] == sums[2]):
                break
        else:
            pairs = []
            for class_index, group in enumerate(calls_x):
                for call in group:
                    pairs.append((class_index, call))
            for class_index, group in enumerate(calls_y):
                for call in group:
                    pairs.append((3 + class_index, call))
            rng.shuffle(pairs)
            word = [(letter, call) for letter, call in pairs]
            if len(word) > 11:
                continue
            tested += 1
            total_x = sum(len(group) for group in calls_x)
            total_y = sum(len(group) for group in calls_y)
            key = "%d+%d" % (total_x, total_y)
            shape_counts[key] = shape_counts.get(key, 0) + 1
            if M.word_product(word, 3) == target:
                hits += 1
    need(hits == 0, "class-sum-feasible search found no shorter word")
    return {"draws": draws, "tested": tested, "hits": hits, "r": 3,
            "tested_by_shape": dict(sorted(shape_counts.items()))}


def block_relation_check() -> dict:
    """The (0,1) block of a realizing word vanishes, so the linear relation
    sum_alpha m_alpha x N_alpha = 0 must hold for the three per-letter-class
    idempotent sums N_alpha.  Its kernel is computed by Gaussian elimination
    on the 27 images of the coordinate matrices; the equal-triples space is
    contained in it and has the same dimension, so the relation is
    equivalent to N_1 = N_w = N_w2."""
    def flat(rows: list[int]) -> int:
        width = len(rows)
        value = 0
        for i, row in enumerate(rows):
            for j in range(width):
                if (row >> j) & 1:
                    value |= 1 << (i * width + j)
        return value

    images = []
    for slot in range(3):
        base = nilpotent(slot)
        for p in range(3):
            for q in range(3):
                projector = [1 << q if i == p else 0 for i in range(3)]
                images.append(flat(M.kron_block_rows(base, projector, 3)))
    basis: list[int] = []
    for vector in images:
        cur = vector
        for b in basis:
            cur = min(cur, cur ^ b)
        if cur:
            basis.append(cur)
            basis.sort(reverse=True)
    rank = len(basis)
    # equal triples must be killed: m_1 + m_w + m_w2 = 0
    equal_image = 0
    for slot in range(3):
        base = nilpotent(slot)
        for p in range(3):
            for q in range(3):
                projector = [1 << q if i == p else 0 for i in range(3)]
                equal_image ^= flat(M.kron_block_rows(base, projector, 3))
    need(equal_image == 0, "equal triple killed by the block relation")
    need(rank == 18 and 27 - rank == 9, "block relation kernel is the equal triples")
    return {"domain_dim": 27, "rank": rank, "kernel_dim": 27 - rank}


def main() -> int:
    rng = random.Random(20261018)
    result = {
        "schema_version": 1,
        "package": "research/ut3-central-triple-independent",
        "base_commit": "20ecf2891d80b5acf18d980b2164fb44ea7faa90",
        "group_law": group_law(),
        "matrix_census_r3": matrix_census(3),
        "witnesses": witness_checks(),
        "collapse": collapse_check(40, rng),
        "block_relation": block_relation_check(),
        "corner": corner_certificate(),
        "search": {
            "uniform": search_uniform(20000, rng),
            "class_sum_feasible": search_class_sum_feasible(20000, rng),
        },
        "not_checked": [
            "all-r step of the lower-bound arguments (inspected, not machine-verified)",
            "the 82160-subset diagonal-lift census of PR 3788",
            "physical realisation, hosting or price of the twelve formal calls",
        ],
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["receipt_sha256"] = hashlib.sha256(payload.encode()).hexdigest()
    with open(os.path.join(HERE, "RESULT.json"), "w", encoding="utf-8") as out:
        json.dump(result, out, indent=1, sort_keys=True)
        out.write("\n")
    if FAILURES:
        print("FAIL_UT3_CENTRAL_TRIPLE_INDEPENDENT failures=%d" % len(FAILURES))
        return 1
    search = result["search"]
    print("PASS_UT3_CENTRAL_TRIPLE_INDEPENDENT order=64 involutions=6 "
          "idempotents=28 trace_zero=21 witnesses=2 deletions=24 "
          "uniform_trials=%d class_sum_tested=%d shorter_words=0"
          % (search["uniform"]["trials"], search["class_sum_feasible"]["tested"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
