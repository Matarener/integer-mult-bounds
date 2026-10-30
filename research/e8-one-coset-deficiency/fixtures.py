"""Exact factorization, normalization and sharp-family controls.

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
These finite controls exercise the universal written argument; they do not
enumerate arbitrary characteristic-zero coefficient choices.
"""

from fractions import Fraction as F


def add(left, right, scale=1):
    return tuple(x + scale * y for x, y in zip(left, right))


def multiple(left, right):
    """Return c for left=c*right, or None, for two nonzero factors."""
    index = next(i for i, x in enumerate(right) if x)
    value = F(left[index]) / right[index]
    return value if all(x == value * y for x, y in zip(left, right)) else None


def cost(g, model, terms):
    return sum(g.copy_rank(model, p, q) for p, q in terms)


def ranks(g, terms):
    if not terms:
        return [0, 0]
    return [g.rational_rank([list(row) for row in zip(*(term[side] for term in terms))])
            for side in (0, 1)]


def exact(g, model, terms):
    for i, root in enumerate(model["roots"]):
        for j, other in enumerate(model["roots"]):
            value = sum(p[i] * q[j] for p, q in terms)
            g.require(value == F(g.dot(root, other), 18), "exact N0 factorization fails")


def normalized(terms):
    if any(not any(p) or not any(q) for p, q in terms):
        return False
    for side in (0, 1):
        for i in range(len(terms)):
            for j in range(i):
                if multiple(terms[i][side], terms[j][side]) is not None:
                    return False
    return True


def normalize(g, model, terms):
    """Literal alternating proportional merges; cost-zero nonzero terms stay."""
    terms = list(terms)
    costs = [cost(g, model, terms)]
    while True:
        live = [(p, q) for p, q in terms if any(p) and any(q)]
        if len(live) != len(terms):
            terms = live
            costs.append(cost(g, model, terms))
        merged = False
        for side in (0, 1):
            for i in range(len(terms)):
                for j in range(i):
                    value = multiple(terms[i][side], terms[j][side])
                    if value is None:
                        continue
                    p, q = terms[j]
                    if side == 0:
                        new = (p, add(q, terms[i][1], value))
                    else:
                        new = (add(p, terms[i][0], value), q)
                    terms = [term for k, term in enumerate(terms) if k not in (i, j)] + [new]
                    costs.append(cost(g, model, terms))
                    merged = True
                    break
                if merged:
                    break
            if merged:
                break
        if not merged:
            g.require(normalized(terms), "normalizer did not terminate in normal form")
            g.require(all(a >= b for a, b in zip(costs, costs[1:])), "merge increased COPY cost")
            return terms, costs


def make_decoders(g, model):
    roots = tuple(tuple(F(x, 2) for x in row) for row in g.standard_binding(model))

    def code(normal):
        return tuple(g.dot(root, normal) for root in roots)

    def unit(index, value=1):
        return tuple(F(value) if i == index else F(0) for i in range(120))

    frame = []
    for a in range(0, 8, 2):
        for sign in (1, -1):
            vector = [0] * 8
            vector[a], vector[a + 1] = 1, sign
            column = tuple(x / 2 for x in code(vector))
            frame.append((column, column))

    # A code basis with first normal v and remaining normals in w-perp.
    # Its first dual normal is w because v.w=1. This permits an exact,
    # normalized two-sided cost72 control after adding a column correction.
    v = (1, 1, 0, 0, 0, 0, 0, 0)
    w = (1, 0, 1, 0, 0, 0, 0, 0)
    h = [v, (0, 1, 0, 0, 0, 0, 0, 0), (1, 0, -1, 0, 0, 0, 0, 0)]
    dual = [w, (-1, 1, -1, 0, 0, 0, 0, 0), (0, 0, -1, 0, 0, 0, 0, 0)]
    for i in range(3, 8):
        axis = tuple(int(j == i) for j in range(8))
        h.append(axis)
        dual.append(axis)
    g.require(all(g.dot(a, b) == int(i == j)
                  for i, a in enumerate(h) for j, b in enumerate(dual)), "dual basis fixture")
    vi = next(i for i, root in enumerate(roots) if root == v or root == tuple(-x for x in v))
    wi = next(i for i, root in enumerate(roots) if root == w or root == tuple(-x for x in w))
    lam = unit(vi, code(v)[vi])
    p = [lam] + [add(lam, code(normal), -1) for normal in h]
    q = [tuple(-x / 2 for x in code(normal)) for normal in dual]
    q = [tuple(-sum(column[i] for column in q) for i in range(120))] + q
    one_sided = list(zip(p, q))

    # Add the exact N0 column and subtract the corresponding unit column
    # from every existing reader. Product preservation is checked entrywise.
    mu = unit(wi)
    column = tuple(g.dot(root, roots[wi]) / 2 for root in roots)
    two_sided = [(a, add(b, mu, -b[wi])) for a, b in one_sided] + [(column, mu)]

    # Split a genuinely nonzero cost-zero atom out of the root-swap term.
    # It must survive until a proportional merge restores the one-sided leaf.
    free = unit(vi, q[1][vi])
    g.require(any(free) and g.copy_rank(model, p[1], free) == 0, "free-atom fixture")
    split = [(a, b) for i, (a, b) in enumerate(one_sided) if i != 1]
    split += [(p[1], add(q[1], free, -1)),
              (tuple(2 * x for x in p[1]), tuple(x / 2 for x in free))]
    zero = tuple(F(0) for _ in range(120))
    return {
        "inside": frame,
        "row_extension": one_sided,
        "column_extension": [(b, a) for a, b in one_sided],
        "two_extensions": two_sided,
        "free_atom_split": split,
        "free_atom_split_transposed": [(b, a) for a, b in split],
        "zero_factor": frame + [(unit(vi), zero)],
        "canceling_free_atoms": frame + [(unit(vi), unit(wi)),
                                          (unit(vi, -1), unit(wi))],
    }


def family_controls(g, model):
    lam = tuple(0 if i < 36 else -2 for i in range(120))
    nine = [tuple(lam[i] + row[j] for i, row in enumerate(model["roots"])) for j in range(9)]
    first = model["roots"][0]
    small = tuple(18 if i == 0 else 0 for i in range(120))
    other = tuple(small[i] - g.dot(row, first) for i, row in enumerate(model["roots"]))
    weights = [g.support_weight(model, column) for column in nine]
    pair = [g.support_weight(model, column) for column in (small, other)]
    g.require(weights == [8] * 9 and pair == [1, 8], "sharp family weights")
    g.require(g.rational_rank([list(row) for row in zip(*nine)]) == 9, "sharp family scalar rank")
    # Two outside directions permit an unbounded number of low-weight rays.
    # This is a failure control for the tempting unrestricted extension.
    many = [tuple(1 if i == 0 else t if i == 1 else 0 for i in range(120))
            for t in range(1, 7)]
    deficits = sum(9 - g.support_weight(model, column) for column in many)
    g.require(deficits == 42 and deficits > 18, "two-direction scope control")
    repeated = sum(9 - g.support_weight(model, small) for _ in range(6))
    g.require(repeated == 48, "proportional-family hypothesis control")
    return {"nine_weight_eight_vectors": weights, "nine_family_scalar_rank": 9,
            "annihilator_dimensions_eight_and_one": [9 - x for x in pair],
            "sharp_total_deficiency": 9,
            "two_outside_direction_counterexample": {"vectors": 6, "total_deficiency": deficits},
            "proportional_family_counterexample": {"copies": 6, "total_deficiency": repeated}}


def rank_mod(rows, prime):
    work = [[x % prime for x in row] for row in rows]
    rank = 0
    for column in range(len(work[0])):
        pivot = next((i for i in range(rank, len(work)) if work[i][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, prime)
        for i in range(rank + 1, len(work)):
            factor = work[i][column] * inverse % prime
            for j in range(column, len(work[0])):
                work[i][j] = (work[i][j] - factor * work[rank][j]) % prime
        rank += 1
        if rank == len(work):
            break
    return rank


def equality_conditions(g, model, terms, excesses):
    """Necessary rigidity of sharp normalized decoders, not a classification."""
    sides = []
    for side, excess in enumerate(excesses):
        spaces = []
        for term in terms:
            labels = [label for label, value in zip(model["labels"], term[side]) if value]
            basis = []
            for z in range(1, 512):
                if all(not g.parity(z & label) for label in labels):
                    if g.binary_rank(basis + [z]) > len(basis):
                        basis.append(z)
            g.require(len(basis) == 9 - g.support_weight(model, term[side]), "annihilator dimension")
            if excess:
                gram = [sum(g.parity(a & b) << j for j, b in enumerate(basis)) for a in basis]
                g.require(g.binary_rank(gram) == len(basis), "equality annihilator is degenerate")
            spaces.append(basis)
        g.require(sum(map(len, spaces)) == 9 * excess, "unsaturated equality budget")
        for i, left in enumerate(spaces):
            for right in spaces[i + 1:]:
                g.require(all(not g.parity(a & b) for a in left for b in right),
                          "same-side annihilators are not orthogonal")
        all_normals = [z for basis in spaces for z in basis]
        g.require(g.binary_rank(all_normals) == 9 * excess, "equality annihilator sum is not direct")
        sides.append(spaces)
    g.require(len(terms) == 8 + sum(excesses), "equality normalized term count")
    for p_space, q_space in zip(*sides):
        g.require(all(not g.parity(a & b) for a in p_space for b in q_space),
                  "matched equality annihilators are not orthogonal")
    return {"normalized_term_count_tight": True,
            "annihilator_dimensions": [[len(space) for space in side] for side in sides],
            "same_side_orthogonal_direct_sums": True,
            "nonzero_excess_summands_nondegenerate": True,
            "matched_cross_side_orthogonality": True}


def finite_field_controls(g, model, decoders):
    """Small actual field controls; the all-odd-field proof uses unit minors."""
    standard = g.standard_binding(model)
    results = {}
    for prime in (3, 5, 7):
        def convert(value):
            value = F(value)
            return value.numerator * pow(value.denominator, -1, prime) % prime

        target = [[g.dot(a, b) * pow(8, -1, prime) % prime for b in standard] for a in standard]
        g.require(rank_mod(target, prime) == 8, "odd-field Gram rank")
        cases = {}
        for name, original in decoders.items():
            terms = [(tuple(convert(x) for x in p), tuple(convert(x) for x in q)) for p, q in original]
            for i in range(120):
                for j in range(120):
                    g.require(sum(p[i] * q[j] for p, q in terms) % prime == target[i][j],
                              "finite-field exact factorization")
            scalar_ranks = [rank_mod([list(row) for row in zip(*(term[side] for term in terms))], prime)
                            for side in (0, 1)]
            g.require(scalar_ranks == ranks(g, original), "finite-field factor ranks")
            value = cost(g, model, terms)
            g.require(value == 72, "finite-field sharp COPY cost")
            if name == "two_extensions":
                for side in (0, 1):
                    columns = [term[side] for term in terms]
                    for i in range(len(columns)):
                        g.require(any(columns[i]), "finite-field zero normalized factor")
                        for j in range(i):
                            k = next(k for k, x in enumerate(columns[j]) if x)
                            ratio = columns[i][k] * pow(columns[j][k], -1, prime) % prime
                            g.require(any((x - ratio * y) % prime for x, y in zip(columns[i], columns[j])),
                                      "finite-field proportional normalized factors")
            cases[name] = {"ranks": scalar_ranks, "copy_cost": value}
        results[str(prime)] = {"target_rank": 8, "exact_factorizations": cases}
    # At characteristic five R^T R=30I vanishes. The rank-eight product
    # argument must use injectivity/surjectivity rather than invert that matrix.
    g.require(all(sum(row[i] * row[j] for row in standard) % 5 == 0
                  for i in range(8) for j in range(8)), "characteristic-five degeneracy control")
    return {"primes": results, "char5_R_transpose_R_zero_but_Gram_rank_eight": True}


def run(g, model):
    decoders = make_decoders(g, model)
    expected = {"inside": (8, [8, 8]), "row_extension": (9, [9, 8]),
                "column_extension": (9, [8, 9]), "two_extensions": (10, [9, 9]),
                "free_atom_split": (10, [9, 9]),
                "free_atom_split_transposed": (10, [9, 9]), "zero_factor": (9, [9, 8]),
                "canceling_free_atoms": (10, [9, 9])}
    results = {}
    for name, terms in decoders.items():
        exact(g, model, terms)
        scalar_ranks = ranks(g, terms)
        g.require((len(terms), scalar_ranks) == expected[name], "fixture scalar ranks: " + name)
        value = cost(g, model, terms)
        g.require(value == 72, "sharp exact decoder cost: " + name)
        clean, trace = normalize(g, model, terms)
        exact(g, model, clean)
        final_ranks = ranks(g, clean)
        s, t = final_ranks[0] - 8, final_ranks[1] - 8
        g.require(s in (0, 1) and t in (0, 1), "normalization rank admission")
        g.require(len(clean) >= 8 + s + t, "Sylvester fixture bound")
        row_def = sum(9 - g.support_weight(model, p) for p, _ in clean)
        col_def = sum(9 - g.support_weight(model, q) for _, q in clean)
        g.require(row_def <= 9 * s and col_def <= 9 * t, "family budget on actual decoder")
        g.require(all(g.copy_rank(model, p, q) >=
                      g.support_weight(model, p) + g.support_weight(model, q) - 9 for p, q in clean),
                  "binary pairing rank inequality")
        if name in ("inside", "row_extension", "column_extension", "two_extensions"):
            g.require(normalized(terms), "advertised normalized fixture")
        results[name] = {"terms": len(terms), "ranks": scalar_ranks, "copy_cost": value,
                         "normalized_terms": len(clean), "normalized_ranks": final_ranks,
                         "normalized_deficiencies": [row_def, col_def], "merge_cost_trace": trace,
                         "equality_conditions": equality_conditions(g, model, clean, (s, t))}

    # Semantic failures change actual factor matrices, not test bookkeeping.
    baseline = decoders["two_extensions"]
    mutations = {"omit_term": baseline[:-1],
                 "wrong_N0_scale": [(add(p, p), q) for p, q in baseline],
                 "one_factor_sign": [(tuple(-x for x in p) if i == 1 else p, q)
                                     for i, (p, q) in enumerate(baseline)],
                 "drop_nonzero_cost_zero_atom": decoders["free_atom_split"][:-1]}
    rejected = []
    for name, terms in mutations.items():
        try:
            exact(g, model, terms)
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("accepted changed factorization: " + name)
    return {"exact_factorizations": results, "semantic_mutations_rejected": rejected,
            "sharp_families": family_controls(g, model),
            "odd_characteristic_actual_controls": finite_field_controls(g, model, decoders)}
